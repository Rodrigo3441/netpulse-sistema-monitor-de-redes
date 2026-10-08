from src.data_collection.extraction.config import ANCHORS, ANCHORS_URL
from src.data_collection.extraction.cache import get_or_fetch


def collect_anchors():
    for anchor_id in ANCHORS:
        url = f'{ANCHORS_URL}/{anchor_id}/'
        cache_path = f'cache/anchors/{anchor_id}.json'

        get_or_fetch(url, cache_path)