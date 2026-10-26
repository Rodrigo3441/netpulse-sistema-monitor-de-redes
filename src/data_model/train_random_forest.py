from sklearn.ensemble import RandomForestClassifier

from src.data_model.config import (
    GRADE_RF,
    RF_GRID_NAME,
    RF_JOBLIB_NAME,
    RF_METADATA_NAME,
    SEED,
)
from src.data_model.evaluate import evaluate_predictions, print_evaluation
from src.data_model.load_dataset import prepare_dataset
from src.data_model.persist import save_artifacts
from src.data_model.search import fit_grid_search


def main(dataset=None):
    if dataset is None:
        dataset = prepare_dataset()

    print("\nTreinando random forest...")

    estimator = RandomForestClassifier(random_state=SEED, n_jobs=1)
    search, n_combinacoes = fit_grid_search(
        estimator,
        GRADE_RF,
        dataset,
    )

    predictions = search.best_estimator_.predict(dataset["X_test"])
    metrics = evaluate_predictions(dataset["y_test"], predictions)
    print_evaluation("Random forest — teste", metrics)

    return save_artifacts(
        familia="random_forest",
        busca=search,
        metrics=metrics,
        n_combinacoes=n_combinacoes,
        joblib_name=RF_JOBLIB_NAME,
        metadata_name=RF_METADATA_NAME,
        grid_name=RF_GRID_NAME,
    )

