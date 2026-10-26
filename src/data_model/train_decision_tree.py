from sklearn.tree import DecisionTreeClassifier

from src.data_model.config import (
    ARVORE_GRID_NAME,
    ARVORE_JOBLIB_NAME,
    ARVORE_METADATA_NAME,
    GRADE_ARVORE,
    SEED,
)
from src.data_model.evaluate import evaluate_predictions, print_evaluation
from src.data_model.load_dataset import prepare_dataset
from src.data_model.persist import save_artifacts
from src.data_model.search import fit_grid_search


def main(dataset=None):
    if dataset is None:
        dataset = prepare_dataset()

    print("\nTreinando árvore de decisão...")

    estimator = DecisionTreeClassifier(random_state=SEED)
    search, n_combinacoes = fit_grid_search(
        estimator,
        GRADE_ARVORE,
        dataset,
    )

    predictions = search.best_estimator_.predict(dataset["X_test"])
    metrics = evaluate_predictions(dataset["y_test"], predictions)
    print_evaluation("Árvore de decisão — teste", metrics)

    return save_artifacts(
        familia="arvore_decisao",
        busca=search,
        metrics=metrics,
        n_combinacoes=n_combinacoes,
        joblib_name=ARVORE_JOBLIB_NAME,
        metadata_name=ARVORE_METADATA_NAME,
        grid_name=ARVORE_GRID_NAME,
    )