from src.data_collection.create_cache import execute_data_collection
from src.data_collection.build_dataset import execute_dataset_creation

if __name__ == "__main__":
    execute_data_collection()
    execute_dataset_creation()