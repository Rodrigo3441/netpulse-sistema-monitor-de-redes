from src.data_model.load_dataset import prepare_dataset
from src.data_model.train_decision_tree import main as train_tree
from src.data_model.train_random_forest import main as train_forest


def execute():
    print("Carregando dataset rotulado e dividido:")
    dataset = prepare_dataset()

    print("\nIniciando treino da árvore de decisão:")
    train_tree(dataset)

    print("\nIniciando treino da random forest:")
    train_forest(dataset)

    print("\nTreino dos modelos concluído.")

