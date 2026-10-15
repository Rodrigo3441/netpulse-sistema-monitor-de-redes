from pathlib import Path
import numpy as np
import pandas as pd
import ast
import math


# Caminhos
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / 'data' / 'raw'
INTERIM_DIR = PROJECT_ROOT / 'data' / 'interim'

PERIOD_B_PATH = RAW_DIR / 'period_b.csv'
BASELINE_PATH = INTERIM_DIR / 'baseline_por_fluxo.csv'
OUTPUT_PATH = INTERIM_DIR / 'period_b_metrics.csv'

FLOW_COLUMNS = ['msm_id', 'probe_id']


def calculate_measurement_jitter(result_value):
    """Calcula a média das diferenças absolutas entre RTTs consecutivos."""
    if not isinstance(result_value, str):
        return float('nan')

    try:
        results = ast.literal_eval(result_value)
    except (ValueError, SyntaxError):
        return float('nan')

    if not isinstance(results, list):
        return float('nan')

    differences = []
    previous_rtt = None

    for item in results:
        rtt = item.get('rtt') if isinstance(item, dict) else None

        if (
            not isinstance(rtt, (int, float))
            or isinstance(rtt, bool)
            or not math.isfinite(rtt)
            or rtt <= 0
        ):
            previous_rtt = None
            continue

        if previous_rtt is not None:
            differences.append(abs(rtt - previous_rtt))

        previous_rtt = rtt

    if not differences:
        return float('nan')

    return sum(differences) / len(differences)


def calculate_jitter_metrics(df):
    """Calcula jitter atual e compara com o baseline histórico."""
    df = df.copy()

    df['jitter_atual'] = df['result'].apply(
        calculate_measurement_jitter
    )

    df['jitter_relativo'] = np.nan

    valid_jitter = df['jitter_atual'].notna()
    positive_baseline = df['jitter_tipico'] > 0

    normal_case = valid_jitter & positive_baseline

    df.loc[normal_case, 'jitter_relativo'] = (
        df.loc[normal_case, 'jitter_atual']
        / df.loc[normal_case, 'jitter_tipico']
    )

    zero_baseline = valid_jitter & (df['jitter_tipico'] == 0)

    both_zero = zero_baseline & (df['jitter_atual'] == 0)
    current_positive = zero_baseline & (df['jitter_atual'] > 0)

    df.loc[both_zero, 'jitter_relativo'] = 1.0
    df.loc[current_positive, 'jitter_relativo'] = 3.0

    return df


def load_data():
    """Carrega o Período B e o baseline calculado no Período A."""
    period_b = pd.read_csv(PERIOD_B_PATH)
    baseline = pd.read_csv(BASELINE_PATH)

    period_b['timestamp'] = pd.to_numeric(
        period_b['timestamp'], errors='raise'
    )
    period_b['avg'] = pd.to_numeric(period_b['avg'], errors='raise')
    period_b['sent'] = pd.to_numeric(period_b['sent'], errors='raise')
    period_b['rcvd'] = pd.to_numeric(period_b['rcvd'], errors='raise')

    return period_b, baseline


def validate_baseline(period_b, baseline):
    """Confirma que cada fluxo do Período B possui baseline."""
    if baseline.duplicated(FLOW_COLUMNS).any():
        raise ValueError('O baseline contém fluxos duplicados.')

    period_b_flows = period_b[FLOW_COLUMNS].drop_duplicates()
    baseline_flows = baseline[FLOW_COLUMNS].drop_duplicates()

    missing = period_b_flows.merge(
        baseline_flows,
        on=FLOW_COLUMNS,
        how='left',
        indicator=True
    )

    missing = missing.loc[missing['_merge'] == 'left_only', FLOW_COLUMNS]

    if not missing.empty:
        raise ValueError(
            'Existem fluxos sem baseline: '
            f'{missing.to_dict(orient="records")}'
        )


def calculate_current_metrics(df):
    """Calcula perda, aumento de RTT, z robusto e timeout."""
    df = df.copy()

    # RTT válido: valor positivo em avg.
    # -1 representa ausência de resposta e não será tratado como RTT.
    df['rtt_valido'] = df['avg'].where(df['avg'] > 0)

    # Perda de pacotes (%).
    df['perda_pct'] = np.nan
    valid_sent = df['sent'] > 0

    df.loc[valid_sent, 'perda_pct'] = (
        (df.loc[valid_sent, 'sent'] - df.loc[valid_sent, 'rcvd'])
        / df.loc[valid_sent, 'sent']
        * 100
    )

    # Aumento percentual em relação à mediana histórica.
    df['aumento_pct'] = (
        (df['rtt_valido'] - df['mediana'])
        / df['mediana']
        * 100
    )

    # Z robusto, respeitando os casos especiais de MAD = 0.
    df['z_robusto'] = np.nan

    valid_rtt = df['rtt_valido'].notna()
    mad_positive = valid_rtt & (df['MAD'] > 0)

    df.loc[mad_positive, 'z_robusto'] = (
        (df.loc[mad_positive, 'rtt_valido']
         - df.loc[mad_positive, 'mediana'])
        / (1.4826 * df.loc[mad_positive, 'MAD'])
    )

    mad_zero_equal = (
        valid_rtt
        & (df['MAD'] == 0)
        & (df['rtt_valido'] == df['mediana'])
    )

    df.loc[mad_zero_equal, 'z_robusto'] = 0.0

    mad_zero_different = (
        valid_rtt
        & (df['MAD'] == 0)
        & (df['rtt_valido'] != df['mediana'])
    )

    fallback_denominator = (
        df['IQR'] / 1.349
    ).clip(lower=1.0)

    df.loc[mad_zero_different, 'z_robusto'] = (
        (
            df.loc[mad_zero_different, 'rtt_valido']
            - df.loc[mad_zero_different, 'mediana']
        )
        / fallback_denominator.loc[mad_zero_different]
    )

    # Timeout: RTT ausente ou perda total de pacotes.
    df['timeout_atual'] = (
        df['rtt_valido'].isna()
        | df['perda_pct'].eq(100)
    ).astype(int)

    return df



def calculate_recent_counts(df):
    """Conta eventos nas cinco medições mais recentes de cada fluxo."""
    df = df.sort_values(
        FLOW_COLUMNS + ['timestamp']
    ).reset_index(drop=True)

    # Aumento de RTT estritamente superior a 80%.
    df['aumento80_atual'] = (
        df['aumento_pct'] > 80
    ).astype(int)

    # Critério individual que pode contribuir para RISCO.
    df['risco_criterio_atual'] = (
        (
            (df['z_robusto'] >= 2)
            & (df['z_robusto'] < 3.5)
        )
        | (
            (df['aumento_pct'] >= 30)
            & (df['aumento_pct'] <= 80)
        )
        | (df['jitter_relativo'] >= 3)
    ).astype(int)

    grouped = df.groupby(FLOW_COLUMNS, sort=False)

    df['n5_timeout'] = grouped['timeout_atual'].transform(
        lambda series: series.rolling(5, min_periods=1).sum()
    ).astype(int)

    df['n5_aumento80'] = grouped['aumento80_atual'].transform(
        lambda series: series.rolling(5, min_periods=1).sum()
    ).astype(int)

    df['n5_risco'] = grouped['risco_criterio_atual'].transform(
        lambda series: series.rolling(5, min_periods=1).sum()
    ).astype(int)

    return df



def main():
    """Calcula as métricas do Período B sem alterar o baseline."""
    period_b, baseline = load_data()

    validate_baseline(period_b, baseline)

    # Incorpora somente as estatísticas históricas necessárias.
    baseline_columns = FLOW_COLUMNS + [
        'mediana', 'MAD', 'IQR', 'jitter_tipico'
    ]

    df = period_b.merge(
        baseline[baseline_columns],
        on=FLOW_COLUMNS,
        how='left',
        validate='many_to_one'
    )

    df = calculate_current_metrics(df)
    df = calculate_jitter_metrics(df)
    df = calculate_recent_counts(df)

    # Remove coluna auxiliar: o RTT original continua preservado em avg.
    df = df.drop(
    columns=[
        'rtt_valido',
        'aumento80_atual',
        'risco_criterio_atual'
    ]
)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8')

    print(f'Medições processadas: {len(df)}')
    print(f'Fluxos processados: {df[FLOW_COLUMNS].drop_duplicates().shape[0]}')
    print(f'Timeouts: {df["timeout_atual"].sum()}')
    print(f'Arquivo salvo em: {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
