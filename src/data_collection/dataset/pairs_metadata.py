
import json
import math
from pathlib import Path

import pandas as pd

from src.data_collection.extraction.config import ANCHORS, MEASUREMENT_PROBES


# Construção do índice de pares
def build_pair_index():
    """Cria as combinações entre probes de origem e anchors de destino."""
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


# Cálculo da distância geográfica
def calculate_distance_km(src_lat, src_lon, dst_lat, dst_lon):
    """Calcula a distância aproximada entre dois pontos usando Haversine."""
    try:
        src_lat, src_lon, dst_lat, dst_lon = map(
            float, (src_lat, src_lon, dst_lat, dst_lon)
        )
    except (TypeError, ValueError):
        return None

    coordinates = (src_lat, src_lon, dst_lat, dst_lon)

    if not all(math.isfinite(value) for value in coordinates):
        return None

    if not (
        -90 <= src_lat <= 90
        and -90 <= dst_lat <= 90
        and -180 <= src_lon <= 180
        and -180 <= dst_lon <= 180
    ):
        return None

    # Conversão de graus para radianos
    src_lat, src_lon, dst_lat, dst_lon = map(
        math.radians, coordinates
    )

    # Fórmula de Haversine
    delta_lat = dst_lat - src_lat
    delta_lon = dst_lon - src_lon

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(src_lat)
        * math.cos(dst_lat)
        * math.sin(delta_lon / 2) ** 2
    )

    # Evita pequenas imprecisões numéricas
    a = min(1.0, max(0.0, a))

    earth_radius_km = 6371.0

    return 2 * earth_radius_km * math.asin(math.sqrt(a))


def classify_distance(distance_km):
    """Classifica a rota conforme a distância geográfica em quilômetros."""
    if distance_km is None:
        return None

    if distance_km < 1000:
        return 'curta'
    elif distance_km <= 5000:
        return 'media'
    else:
        return 'longa'


# Construção dos metadados dos pares
def build_pairs_metadata(probes_dir, anchors_dir):
    """Combina pares, metadados geográficos e classificação da distância."""
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

        distance_km = calculate_distance_km(
            pair_metadata['src_latitude'],
            pair_metadata['src_longitude'],
            pair_metadata['dst_latitude'],
            pair_metadata['dst_longitude']
        )

        pair_metadata['distancia_km'] = (
            round(distance_km, 2)
            if distance_km is not None
            else None
        )

        pair_metadata['distancia'] = classify_distance(distance_km)

        metadata.append(pair_metadata)

    return pd.DataFrame(metadata)


# Exportação dos metadados
def export_pairs_metadata(df, output_path):
    """Exporta os metadados dos pares para um arquivo CSV."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False, encoding='utf-8')
