from src import (
    etl_data_collection,
    etl_data_labeling,
    etl_data_model
)

if __name__ == "__main__":
    etl_data_collection.execute()
    etl_data_labeling.execute()
    etl_data_model.execute()
