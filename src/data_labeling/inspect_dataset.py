from pathlib import Path

import pandas as pd


# Localização dos arquivos
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / 'data' / 'raw'

PERIOD_A_PATH = RAW_DIR / 'period_a.csv'
PERIOD_B_PATH = RAW_DIR / 'period_b.csv'


def load_dataset(csv_path):
    """Carrega um dataset CSV e retorna seu conteúdo em um DataFrame."""
    return pd.read_csv(csv_path)


def inspect_dataset(df, name):
    """Exibe informações gerais, duplicatas e valores ausentes do dataset."""
    print(f'\n{"=" * 50}')
    print(f'Dataset: {name}')
    print(f'{"=" * 50}')

    print(f'Quantidade de linhas: {len(df)}')
    print(f'Quantidade de colunas: {len(df.columns)}')

    print('\nColunas:')
    print(df.columns.tolist())

    print('\nTipos de dados:')
    print(df.dtypes)

    print(f'\nLinhas duplicadas completas: {df.duplicated().sum()}')

    print('\nValores ausentes por coluna:')
    print(df.isna().sum().to_string())


def inspect_flows(df, name):
    """Conta os fluxos distintos e verifica a quantidade de RTTs válidos."""
    flow_columns = ['msm_id', 'probe_id']

    print(f'\n--- Fluxos: {name} ---')

    flow_counts = (
        df.groupby(flow_columns, dropna=False)
        .agg(
            total_medicoes=('timestamp', 'size'),
            rtts_validos=('avg', lambda values: values.gt(0).sum())
        )
        .reset_index()
    )

    print(f'Quantidade de fluxos: {len(flow_counts)}')
    print(f'Fluxos com pelo menos 1500 RTTs válidos: '
          f'{flow_counts["rtts_validos"].ge(1500).sum()}')
    print(f'Fluxos com menos de 1500 RTTs válidos: '
          f'{flow_counts["rtts_validos"].lt(1500).sum()}')

    print('\nResumo das medições por fluxo:')
    print(flow_counts['total_medicoes'].describe())

    print('\nResumo dos RTTs válidos por fluxo:')
    print(flow_counts['rtts_validos'].describe())

    return flow_counts


def inspect_results(df, name):
    """Resume RTTs inválidos, perdas de pacotes e intervalos temporais."""
    print(f'\n--- Qualidade dos dados: {name} ---')

    print(f'RTTs ausentes: {df["avg"].isna().sum()}')
    print(f'RTTs iguais a -1: {df["avg"].eq(-1).sum()}')
    print(f'RTTs positivos: {df["avg"].gt(0).sum()}')

    print(f'Medições com perda de pacotes: '
          f'{df["rcvd"].lt(df["sent"]).sum()}')

    print(f'Medições sem nenhuma resposta: '
          f'{df["rcvd"].eq(0).sum()}')

    timestamps = pd.to_numeric(df['timestamp'], errors='coerce')

    if timestamps.notna().any():
        start = pd.to_datetime(
            timestamps.min(), unit='s', utc=True
        )
        end = pd.to_datetime(
            timestamps.max(), unit='s', utc=True
        )

        print(f'Primeiro timestamp: {start}')
        print(f'Último timestamp: {end}')


def main():
    """Inspeciona os dois períodos sem modificar os arquivos originais."""
    period_a = load_dataset(PERIOD_A_PATH)
    period_b = load_dataset(PERIOD_B_PATH)

    inspect_dataset(period_a, 'Período A')
    inspect_dataset(period_b, 'Período B')

    flow_counts_a = inspect_flows(period_a, 'Período A')
    inspect_flows(period_b, 'Período B')

    inspect_results(period_a, 'Período A')
    inspect_results(period_b, 'Período B')

    print('\n--- Verificação dos fluxos entre períodos ---')

    flows_a = set(
        zip(flow_counts_a['msm_id'], flow_counts_a['probe_id'])
    )

    flows_b = set(
        zip(period_b['msm_id'], period_b['probe_id'])
    )

    print(f'Fluxos presentes nos dois períodos: {len(flows_a & flows_b)}')
    print(f'Fluxos exclusivos do Período A: {len(flows_a - flows_b)}')
    print(f'Fluxos exclusivos do Período B: {len(flows_b - flows_a)}')


if __name__ == '__main__':
    main()