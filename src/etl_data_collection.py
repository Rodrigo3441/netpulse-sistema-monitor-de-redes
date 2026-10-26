from src.data_collection import (
    build_dataset,
    create_cache
)

def execute():
    print('Criando o cache com dados da API: ')
    create_cache.execute_data_collection()

    print('Fazendo a criação do dataset do período \'A\' e \'B\': ')
    build_dataset.execute_dataset_creation()