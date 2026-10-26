import numpy as np
import pandas as pd
from sklearn.model_selection import PredefinedSplit

from src.data_model.config import (
    CLASSES,
    FEATURES,
    INPUT_PATH,
    SPLIT_COLUMN,
    SPLIT_TEST,
    SPLIT_TRAIN,
    SPLIT_VALIDATION,
    TARGET_COLUMN,
)


def count_grid_combinations(param_grid):
    total = 1
    for values in param_grid.values():
        total *= len(values)
    return total


def load_labeled_split():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {INPUT_PATH}\n"
            "Execute a rotulação e o split antes do treino."
        )

    df = pd.read_csv(INPUT_PATH)

    required_columns = set(FEATURES + [TARGET_COLUMN, SPLIT_COLUMN])
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {sorted(missing)}"
        )

    df[FEATURES] = df[FEATURES].replace([np.inf, -np.inf], np.nan)

    invalid_target = ~df[TARGET_COLUMN].isin(CLASSES)
    if invalid_target.any():
        raise ValueError(
            "Existem valores de classe futura fora de "
            f"{CLASSES}."
        )

    expected_splits = {SPLIT_TRAIN, SPLIT_VALIDATION, SPLIT_TEST}
    found_splits = set(df[SPLIT_COLUMN].dropna().unique())
    missing_splits = expected_splits - found_splits

    if missing_splits:
        raise ValueError(
            f"Splits ausentes no dataset: {sorted(missing_splits)}"
        )

    return df


def split_xy(df):
    X = df[FEATURES]
    y = df[TARGET_COLUMN]
    split = df[SPLIT_COLUMN]

    mask_train = split == SPLIT_TRAIN
    mask_val = split == SPLIT_VALIDATION
    mask_test = split == SPLIT_TEST

    X_train, y_train = X.loc[mask_train], y.loc[mask_train]
    X_val, y_val = X.loc[mask_val], y.loc[mask_val]
    X_test, y_test = X.loc[mask_test], y.loc[mask_test]

    X_fit = pd.concat([X_train, X_val], axis=0)
    y_fit = pd.concat([y_train, y_val], axis=0)

    test_fold = np.concatenate(
        [
            np.full(len(X_train), -1, dtype=int),
            np.full(len(X_val), 0, dtype=int),
        ]
    )
    partition = PredefinedSplit(test_fold)

    print(f"Arquivo de entrada: {INPUT_PATH}")
    print(f"Medições: {len(df)}")
    print(f"Features: {len(FEATURES)}")
    print(
        f"Treino: {len(X_train)} | "
        f"Validação: {len(X_val)} | "
        f"Teste: {len(X_test)}"
    )

    print("\n=== Proporção das classes futuras ===")
    table = pd.DataFrame(
        {
            "train": y_train.value_counts(normalize=True),
            "validation": y_val.value_counts(normalize=True),
            "test": y_test.value_counts(normalize=True),
        }
    ).reindex(CLASSES).round(4)
    print(table.to_string())

    return {
        "X_train": X_train,
        "y_train": y_train,
        "X_val": X_val,
        "y_val": y_val,
        "X_test": X_test,
        "y_test": y_test,
        "X_fit": X_fit,
        "y_fit": y_fit,
        "partition": partition,
    }


def prepare_dataset():
    df = load_labeled_split()
    return split_xy(df)
