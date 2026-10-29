from pathlib import Path
import pandas as pd
import ast
import math


# Caminhos dos arquivos
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / 'data' /'raw'
INTERIM_DIR = PROJECT_ROOT / 'data' / 'interim'

PERIOD_A_PATH = RAW_DIR / 'period_a.csv'
BASELINE_PATH = INTERIM_DIR / 'baseline_por_fluxo.csv'
EXCLUDED_PATH = INTERIM_DIR / 'fluxos_excluidos.csv'

MIN_VALID_RTT = 1500
FLOW_COLUMNS = ['msm_id', 'probe_id']


def calculate_measurement_jitter(result_value):
    """Calcula a média das diferenças absolutas entre RTTs consecutivos válidos."""
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

        # RTT ausente, inválido ou timeout: interrompe a sequência.
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



def load_period_a(csv_path):
    """Carrega o Período A e ordena as medições por fluxo e timestamp."""
    df = pd.read_csv(csv_path)

    return df.sort_values(
        FLOW_COLUMNS + ['timestamp']
    ).reset_index(drop=True)


def calculate_baseline(flow_df):
    """Calcula as estatísticas históricas de um único fluxo."""
    valid_rtt = flow_df.loc[flow_df['avg'] > 0, 'avg']

    jitter_values = flow_df['result'].apply(
    calculate_measurement_jitter
    ).dropna()

    jitter_tipico = jitter_values.median()

    periodo_inicio = pd.to_datetime(
    flow_df['timestamp'].min(),
    unit='s',
    utc=True
    ).isoformat()

    periodo_fim = pd.to_datetime(
        flow_df['timestamp'].max(),
        unit='s',
        utc=True
    ).isoformat()

    sent = flow_df['sent']
    rcvd = flow_df['rcvd']

    valid_loss = sent > 0
    loss_pct = (
        (sent[valid_loss] - rcvd[valid_loss])
        / sent[valid_loss]
        * 100
    )

    median = valid_rtt.median()
    mad = (valid_rtt - median).abs().median()

    q1 = valid_rtt.quantile(0.25)
    q3 = valid_rtt.quantile(0.75)

    return {
        'periodo_inicio': periodo_inicio,
        'periodo_fim': periodo_fim,
        'total_medicoes': len(flow_df),
        'rtts_validos': len(valid_rtt),
        'mediana': median,
        'MAD': mad,
        'jitter_tipico': jitter_tipico,
        'q1': q1,
        'q3': q3,
        'IQR': q3 - q1,
        'perda_tipica': loss_pct.median(),
        'prop_resposta': len(valid_rtt) / len(flow_df)
    }


def build_baselines(df):
    """Gera um baseline por fluxo e separa os fluxos insuficientes."""
    baselines = []
    excluded = []

    for (msm_id, probe_id), flow_df in df.groupby(FLOW_COLUMNS):
        stats = calculate_baseline(flow_df)

        estatisticas_rtt_validas = all(
            pd.notna(stats[col]) and math.isfinite(stats[col])
            for col in ['mediana', 'MAD', 'q1', 'q3', 'IQR']
        )

        baseline_valido = (
            stats['rtts_validos'] >= MIN_VALID_RTT
            and estatisticas_rtt_validas
        )

        referencias_completas = all(
            pd.notna(stats[col]) and math.isfinite(stats[col])
            for col in ['mediana', 'MAD', 'IQR', 'jitter_tipico']
        )

        recomendado_uso = baseline_valido and referencias_completas

        flow_info = {
            'msm_id': msm_id,
            'probe_id': probe_id,
            **stats,
            'baseline_valido': baseline_valido,
            'recomendado_uso': recomendado_uso
        }

        if stats['rtts_validos'] < MIN_VALID_RTT:
            excluded.append({
                'msm_id': msm_id,
                'probe_id': probe_id,
                'rtts_validos': stats['rtts_validos'],
                'motivo': 'Menos de 1500 RTTs válidos no Período A'
            })
        else:
            baselines.append(flow_info)

    return pd.DataFrame(baselines), pd.DataFrame(excluded)


def export_csv(df, output_path):
    """Cria a pasta de destino e exporta um DataFrame para CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8')


def main():
    """Constrói e exporta os baselines calculados exclusivamente no Período A."""
    period_a = load_period_a(PERIOD_A_PATH)

    baseline_df, excluded_df = build_baselines(period_a)

    export_csv(baseline_df, BASELINE_PATH)
    export_csv(excluded_df, EXCLUDED_PATH)

    print(f'Fluxos com baseline: {len(baseline_df)}')
    print(f'Fluxos excluídos: {len(excluded_df)}')
    print(f'Baseline salvo em: {BASELINE_PATH}')
    print(f'Exclusões salvas em: {EXCLUDED_PATH}')


