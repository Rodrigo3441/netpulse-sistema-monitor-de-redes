import json
from pathlib import Path

import pandas as pd

from src.data_collection.extraction.config import ANCHORS, MEASUREMENT_PROBES


# Construção do índice de pares
def build_pair_index():
    """Cria a lista de combinações entre probes de origem e anchors de destino."""
    pairs = []

    for anchor_id, msm_id in ANCHORS.items():
        for probe_id in MEASUREMENT_PROBES[msm_id]:
            pairs.append({
                'msm_id': msm_id,
                'src_probe_id': probe_id,
                'dst_anchor_id': anchor_id
            })

    return pd.DataFrame(pairs)


# Carregamento de metadados
def load_metadata(json_path):
    """Carrega e retorna os dados de um arquivo JSON."""
    json_path = Path(json_path)

    with json_path.open('r', encoding='utf-8') as file:
        return json.load(file)


# Extração de metadados das entidades
def extract_probe_metadata(probe):
    """Extrai país e coordenadas geográficas da probe de origem."""
    coordinates = probe.get('geometry', {}).get('coordinates', [])

    longitude = coordinates[0] if len(coordinates) >= 2 else None
    latitude = coordinates[1] if len(coordinates) >= 2 else None

    return {
        'src_country': probe.get('country_code'),
        'src_latitude': latitude,
        'src_longitude': longitude
    }


def extract_anchor_metadata(anchor):
    """Extrai país e coordenadas geográficas do anchor de destino."""
    coordinates = anchor.get('geometry', {}).get('coordinates', [])

    longitude = coordinates[0] if len(coordinates) >= 2 else None
    latitude = coordinates[1] if len(coordinates) >= 2 else None

    return {
        'dst_country': anchor.get('country'),
        'dst_latitude': latitude,
        'dst_longitude': longitude
    }


# Construção dos metadados dos pares
def build_pairs_metadata(probes_dir, anchors_dir):
    """Combina os pares configurados com os metadados de probes e anchors."""
    pairs_df = build_pair_index()
    metadata = []

    probes_dir = Path(probes_dir)
    anchors_dir = Path(anchors_dir)

    for row in pairs_df.to_dict('records'):
        probe_path = probes_dir / f'{row["src_probe_id"]}.json'
        anchor_path = anchors_dir / f'{row["dst_anchor_id"]}.json'

        probe = load_metadata(probe_path)
        anchor = load_metadata(anchor_path)

        pair_metadata = {
            **row,
            **extract_probe_metadata(probe),
            **extract_anchor_metadata(anchor)
        }

        metadata.append(pair_metadata)

    return pd.DataFrame(metadata)


# Exportação dos metadados
def export_pairs_metadata(df, output_path):
    """Exporta os metadados dos pares para um arquivo CSV."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False, encoding='utf-8')