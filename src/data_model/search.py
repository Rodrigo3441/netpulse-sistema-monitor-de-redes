from sklearn.model_selection import GridSearchCV

from src.data_model.config import N_JOBS_SEARCH, SCORING, SEED
from src.data_model.load_dataset import count_grid_combinations


def fit_grid_search(estimator, param_grid, dataset):
    n_combinacoes = count_grid_combinations(param_grid)

    print(f"Combinações na grade: {n_combinacoes}")
    print(f"Métrica de seleção: {SCORING}")
    print(f"Semente: {SEED}")

    search = GridSearchCV(
        estimator=estimator,
        param_grid=param_grid,
        scoring=SCORING,
        cv=dataset["partition"],
        n_jobs=N_JOBS_SEARCH,
        refit=True,
        return_train_score=True,
    )

    search.fit(dataset["X_fit"], dataset["y_fit"])

    print("Busca concluída.")
    print(f"Melhores parâmetros: {search.best_params_}")
    print(f"Macro-F1 validação: {search.best_score_:.6f}")

    return search, n_combinacoes
