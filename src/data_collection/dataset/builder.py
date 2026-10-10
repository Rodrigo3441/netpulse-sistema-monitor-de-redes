import json
import pandas as pd
from pathlib import Path
from src.data_collection.extraction.config import ANCHORS


# Define as colunas e a ordem do dataset final.
DATASET_COLUMNS = [
    'anchor_id',
    'anchor_ip',
    'probe_id',
    'probe_ip',
    'msm_id',
    'ttl',
    'result',
    'dup',
    'rcvd',
    'sent',
    'min',
    'max',
    'avg',
    'timestamp',
    'type',
    'packets',
    'interval'
]


# =========================
# Carregamento dos dados
# =========================

def load_json(json_path):
    """Carrega e retorna o conteúdo de um arquivo JSON."""
    json_path = Path(json_path)

    with json_path.open('r', encoding='utf-8') as file:
        return json.load(file)


def load_measurements(measurements_dir):
    """Carrega os parâmetros packets e interval de cada measurement."""
    measurements_dir = Path(measurements_dir)
    measurements = {}

    for measurement_file in measurements_dir.glob('*.json'):
        measurement = load_json(measurement_file)
        msm_id = measurement['id']

        measurements[msm_id] = {
            'packets': measurement['packets'],
            'interval': measurement['interval']
        }

    return measurements


def load_entity_metadata(metadata_dir, id_field, fields):
    """Carrega metadados de anchors ou probes, indexados pelo ID."""
    metadata_dir = Path(metadata_dir)
    metadata = {}

    for metadata_file in metadata_dir.glob('*.json'):
        entity = load_json(metadata_file)
        entity_id = entity[id_field]

        metadata[entity_id] = {
            field: entity.get(field)
            for field in fields
        }

    return metadata


def load_results(results_path):
    """Carrega um arquivo de resultados e o converte em DataFrame."""
    results = load_json(results_path)
    return pd.DataFrame(results)


def load_all_results(results_dir):
    """Carrega e combina os resultados de todos os JSONs do diretório."""
    results_dir = Path(results_dir)
    all_results = []

    for result_file in results_dir.glob('*.json'):
        results = load_results(result_file)
        all_results.append(results)

    return pd.concat(all_results, ignore_index=True)


# =========================
# Inspeção dos dados
# =========================

def inspect_results(df):
    """Exibe informações gerais e verifica métricas básicas dos resultados."""
    print('=== Inspeção dos dados ===')

    print(f'\nTotal de registros: {len(df)}')
    print(f'Total de colunas: {len(df.columns)}')

    print('\nValores ausentes por coluna:')
    print(df.isna().sum())

    print('\nTipos de dados:')
    print(df.dtypes)

    print('\nEstatísticas das métricas:')
    print(df[['min', 'max', 'avg', 'sent', 'rcvd']].describe())

    invalid_latency = (
        (df['min'] < 0)
        | (df['max'] < 0)
        | (df['avg'] < 0)
    )

    print('\n=== Validação das métricas ===')
    print(f'Registros com latência negativa: {invalid_latency.sum()}')
    print(f'Registros sem respostas: {(df["rcvd"] == 0).sum()}')
    print(
        'Registros com perda de pacotes: '
        f'{(df["rcvd"] < df["sent"]).sum()}'
    )


# =========================
# Construção dos datasets
# =========================

def build_dataset(results_df, measurements, anchors, probes):
    """Combina resultados e metadados e seleciona as colunas finais."""
    records = []

    # Cria uma relação direta entre measurement e anchor.
    measurement_anchors = {
        measurement_id: anchor_id
        for anchor_id, measurement_id in ANCHORS.items()
    }

    for result in results_df.to_dict('records'):
        msm_id = result['msm_id']
        probe_id = result['prb_id']
        anchor_id = measurement_anchors[msm_id]

        record = {
            'anchor_id': anchor_id,
            'anchor_ip': anchors[anchor_id]['ip_v4'],
            'probe_id': probe_id,
            'probe_ip': probes[probe_id]['address_v4'],
            **result,
            **measurements[msm_id]
        }

        records.append(record)

    dataset_df = pd.DataFrame(records)
    return dataset_df[DATASET_COLUMNS]


def build_dataset_from_dir(
    results_dir,
    measurements,
    anchors,
    probes
):
    """Constrói um dataset a partir de todos os resultados de um diretório."""
    results_df = load_all_results(results_dir)

    return build_dataset(
        results_df,
        measurements,
        anchors,
        probes
    )


# =========================
# Exportação dos datasets
# =========================

def export_dataset(df, output_path):
    """Exporta o DataFrame para CSV, criando o diretório se necessário."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        output_path,
        index=False,
        encoding='utf-8'
    )

    print(f'Dataset exportado: {output_path}')
    print(f'Total de registros: {len(df)}')