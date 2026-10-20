
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "period_b_labeled.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "period_b_split.csv"
)

# Identifica o par origem-destino.
PAIR_COLUMNS = ["anchor_id", "probe_id"]

RANDOM_SEED = 42

TRAIN_PAIRS = 20
VALIDATION_PAIRS = 5
TEST_PAIRS = 5


def assign_pairs(pairs):
    """Atribui cada par completo a um único conjunto."""
    shuffled = pairs.sample(
        frac=1,
        random_state=RANDOM_SEED,
    ).reset_index(drop=True)

    shuffled["split"] = "test"

    shuffled.loc[:TRAIN_PAIRS - 1, "split"] = "train"

    shuffled.loc[
        TRAIN_PAIRS:TRAIN_PAIRS + VALIDATION_PAIRS - 1,
        "split",
    ] = "validation"

    return shuffled


def main():
    df = pd.read_csv(INPUT_PATH)

    required_columns = set(
        PAIR_COLUMNS + ["msm_id", "timestamp", "classe"]
    )
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Colunas ausentes no CSV: {sorted(missing_columns)}"
        )

    if df[PAIR_COLUMNS].isna().any().any():
        raise ValueError(
            "Existem pares com anchor_id ou probe_id ausentes."
        )

    if df["timestamp"].isna().any():
        raise ValueError("Existem timestamps ausentes.")

    original_count = len(df)

    # Obtém os pares distintos, não as medições individuais.
    pairs = df[PAIR_COLUMNS].drop_duplicates().reset_index(drop=True)

    expected_pairs = TRAIN_PAIRS + VALIDATION_PAIRS + TEST_PAIRS

    if len(pairs) != expected_pairs:
        raise ValueError(
            f"Esperados {expected_pairs} pares, "
            f"mas foram encontrados {len(pairs)}."
        )

    # Cada par é atribuído a exatamente um conjunto.
    pair_assignments = assign_pairs(pairs)

    # Associa a atribuição a todas as medições do par.
    split_df = df.merge(
        pair_assignments,
        on=PAIR_COLUMNS,
        how="left",
        validate="many_to_one",
    )

    if len(split_df) != original_count:
        raise RuntimeError(
            "A quantidade de medições mudou durante a divisão."
        )

    if split_df["split"].isna().any():
        raise RuntimeError(
            "Existem medições sem conjunto atribuído."
        )

    # Verifica a quantidade de pares em cada conjunto.
    pairs_per_split = (
        pair_assignments.groupby("split")
        .size()
        .to_dict()
    )

    expected_counts = {
        "train": TRAIN_PAIRS,
        "validation": VALIDATION_PAIRS,
        "test": TEST_PAIRS,
    }

    if pairs_per_split != expected_counts:
        raise RuntimeError(
            f"Distribuição inesperada dos pares: {pairs_per_split}"
        )

    # Verifica que nenhum par aparece em mais de um conjunto.
    splits_per_pair = (
        split_df.groupby(PAIR_COLUMNS)["split"]
        .nunique()
    )

    if (splits_per_pair > 1).any():
        raise RuntimeError(
            "Um ou mais pares aparecem em múltiplos conjuntos."
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    split_df.to_csv(OUTPUT_PATH, index=False)

    print(f"Arquivo de entrada: {INPUT_PATH}")
    print(f"Arquivo de saída: {OUTPUT_PATH}")
    print(f"Total de medições: {len(split_df)}")
    print(f"Total de pares: {len(pairs)}")

    print("\n=== Quantidade de pares por conjunto ===")
    print(
        pair_assignments["split"]
        .value_counts()
        .reindex(["train", "validation", "test"])
        .to_string()
    )

    print("\n=== Quantidade de medições por conjunto ===")
    print(
        split_df["split"]
        .value_counts()
        .reindex(["train", "validation", "test"])
        .to_string()
    )

    print("\n=== Classes por conjunto ===")
    print(
        pd.crosstab(
            split_df["split"],
            split_df["classe"],
            margins=True,
        ).to_string()
    )

    print("\n=== Pares atribuídos ===")
    print(
        pair_assignments.sort_values(
            ["split", "anchor_id", "probe_id"]
        ).to_string(index=False)
    )

    print("\nDivisão por pares concluída.")
    print("Verificações de integridade aprovadas.")


if __name__ == "__main__":
    main()
