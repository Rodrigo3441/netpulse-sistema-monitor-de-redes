from src.data_model import (
    load_dataset,
    train_decision_tree,
    train_random_forest
)


def execute():
    print('Carregando o dataset rotulado e dividido: ')
    dataset = load_dataset.prepare_dataset()

    print('Treinando a árvore de decisão: ')
    train_decision_tree.main(dataset)

    print('Treinando a random forest: ')
    train_random_forest.main(dataset)
