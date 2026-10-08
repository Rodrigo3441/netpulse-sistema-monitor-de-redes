from src.data_collection.extraction.config import ANCHORS, MEASUREMENTS_URL
from src.data_collection.extraction.cache import get_or_fetch


def collect_measurements():
    measurement_ids = set(ANCHORS.values())

    for measurement_id in measurement_ids:
        url = f'{MEASUREMENTS_URL}/{measurement_id}/'
        cache_path = f'cache/measurements/{measurement_id}.json'

        get_or_fetch(url, cache_path)