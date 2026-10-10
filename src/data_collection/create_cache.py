from src.data_collection.extraction.anchors import collect_anchors
from src.data_collection.extraction.probes import collect_probes
from src.data_collection.extraction.measurements import collect_measurements
from src.data_collection.extraction.results import collect_results

def execute_data_collection():
    """Faz a criação do cache de dados, coletando anchors, probes, measurements e results da API."""
    collect_anchors()
    collect_probes()
    collect_measurements()
    collect_results()