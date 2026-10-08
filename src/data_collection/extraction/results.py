from datetime import datetime, timedelta, timezone
from src.data_collection.extraction.config import ANCHORS, MEASUREMENT_PROBES, MEASUREMENTS_URL
from src.data_collection.extraction.cache import get_or_fetch


def collect_results():
    current_time = datetime.now(timezone.utc)

    training_start = current_time - timedelta(days=14)
    training_stop = current_time - timedelta(days=7)

    validation_start = current_time - timedelta(days=7)
    validation_stop = current_time

    windows = {
        'training': (training_start, training_stop),
        'validation': (validation_start, validation_stop)
    }

    measurement_ids = set(ANCHORS.values())

    for measurement_id in measurement_ids:
        for probe_id in MEASUREMENT_PROBES[measurement_id]:

            for dataset, (start, stop) in windows.items():
                url = f'{MEASUREMENTS_URL}/{measurement_id}/results/'

                params = {
                    'start': start.strftime('%Y-%m-%dT%H:%M:%S'),
                    'stop': stop.strftime('%Y-%m-%dT%H:%M:%S'),
                    'probe_ids': probe_id
                }

                cache_path = (
                    f'cache/{dataset}/results/'
                    f'{measurement_id}_{probe_id}.json'
                )

                get_or_fetch(url, cache_path, params=params)