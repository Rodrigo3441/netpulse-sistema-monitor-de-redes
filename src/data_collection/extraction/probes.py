from src.data_collection.extraction.config import MEASUREMENT_PROBES, PROBES_URL
from src.data_collection.extraction.cache import get_or_fetch


def collect_probes():
    probe_ids = set()

    for probes in MEASUREMENT_PROBES.values():
        probe_ids.update(probes)

    for probe_id in probe_ids:
        url = f'{PROBES_URL}/{probe_id}/'
        cache_path = f'cache/probes/{probe_id}.json'

        get_or_fetch(url, cache_path)