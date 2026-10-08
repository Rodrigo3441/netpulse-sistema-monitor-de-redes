from pathlib import Path
import json
import requests


def get_or_fetch(url, cache_path, params=None):
    cache_path = Path(cache_path)

    if cache_path.exists():
        with cache_path.open('r', encoding='utf-8') as file:
            return json.load(file)

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

    cache_path.parent.mkdir(parents=True, exist_ok=True)

    with cache_path.open('w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

    return data