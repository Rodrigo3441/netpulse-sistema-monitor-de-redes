from pathlib import Path
from src.data_collection.dataset.builder import build_dataset_from_dir, export_dataset, load_entity_metadata, load_measurements
from src.data_collection.dataset.pairs_metadata import (
    build_pairs_metadata,
    export_pairs_metadata
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CACHE_DIR = PROJECT_ROOT / 'cache'
OUTPUT_DIR = PROJECT_ROOT / 'raw'


def execute_dataset_creation():
    """Executa a criação dos datasets de treinamento e validação, bem como a exportação dos metadados dos pares."""
    pairs_metadata_df = build_pairs_metadata(
        probes_dir=CACHE_DIR / 'probes',
        anchors_dir=CACHE_DIR / 'anchors'
    )

    output_path = OUTPUT_DIR / 'pairs_metadata.csv'

    export_pairs_metadata(
        pairs_metadata_df,
        output_path
    )

    print(f'Metadados exportados: {output_path}')
    print(f'Total de pares: {len(pairs_metadata_df)}')

    # Carregar metadados das measurements
    measurements = load_measurements('cache/measurements')

    # Carregar metadados dos anchors
    anchors = load_entity_metadata(
        'cache/anchors',
        id_field='id',
        fields=['ip_v4']
    )

    # Carregar metadados dos probes
    probes = load_entity_metadata(
        'cache/probes',
        id_field='id',
        fields=['address_v4']
    )

    # Dataset de treinamento
    training_df = build_dataset_from_dir(
        CACHE_DIR / 'training' / 'results',
        measurements,
        anchors,
        probes
    )

    export_dataset(
        training_df,
        OUTPUT_DIR / 'training.csv'
    )

    # Dataset de validação
    validation_df = build_dataset_from_dir(
        CACHE_DIR / 'validation' / 'results',
        measurements,
        anchors,
        probes
    )

    export_dataset(
        validation_df,
        OUTPUT_DIR / 'validation.csv'
    )