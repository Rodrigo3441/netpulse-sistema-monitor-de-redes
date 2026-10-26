
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

PAIR_COLUMNS = ["anchor_id", "probe_id"]

HORIZON_SECONDS = 12 * 60

RANDOM_SEED = 42

TRAIN_PAIRS = 20
VALIDATION_PAIRS = 5
TEST_PAIRS = 5


SPLIT_DISTRIBUTION = {
    "longa": {
        "train": 15,
        "validation": 3,
        "test": 3,
    },
    "media": {
        "train": 2,
        "validation": 1,
        "test": 1,
    },
    "curta": {
        "train": 3,
        "validation": 1,
        "test": 1,
    },
}

def assign_pairs(pairs):
    """Distribui pares por categoria de distância."""
    rng_seed = RANDOM_SEED
    assignments = []

    for distance, distribution in SPLIT_DISTRIBUTION.items():
        category_pairs = pairs[
            pairs["distancia"].str.strip().str.lower() == distance
        ].sample(
            frac=1,
            random_state=rng_seed,
        ).reset_index(drop=True)

        expected = sum(distribution.values())

        if len(category_pairs) != expected:
            raise ValueError(
                f"Categoria '{distance}': esperados {expected} pares, "
                f"mas encontrados {len(category_pairs)}."
            )

        start = 0

        for split_name in ["train", "validation", "test"]:
            count = distribution[split_name]
            selected = category_pairs.iloc[start:start + count].copy()
            selected["split"] = split_name
            assignments.append(selected)
            start += count

        rng_seed += 1

    return pd.concat(assignments, ignore_index=True)



def create_future_class(df):
    """Obtém a classe da primeira medição do mesmo fluxo
    ocorrida pelo menos 12 minutos depois."""
    df = df.copy()
    df["_row_id"] = range(len(df))
    df["classe_futura"] = pd.NA

    horizon = HORIZON_SECONDS

    for _, group in df.groupby(PAIR_COLUMNS, sort=False):
        group = group.sort_values("timestamp")

        timestamps = group["timestamp"].to_numpy()
        classes = group["classe"].to_numpy()
        row_ids = group["_row_id"].to_numpy()

        for i, row_id in enumerate(row_ids):
            target_timestamp = timestamps[i] + horizon

            # Primeira medição no instante-alvo ou depois dele.
            j = timestamps.searchsorted(
                target_timestamp,
                side="left",
            )

            if j < len(timestamps):
                df.loc[row_id, "classe_futura"] = classes[j]

    total_before = len(df)

    df = df.dropna(subset=["classe_futura"]).copy()
    removed = total_before - len(df)

    df = df.drop(columns="_row_id")

    print("\n=== Criação da classe futura ===")
    print(f"Horizonte mínimo: {horizon} segundos")
    print(f"Linhas originais: {total_before}")
    print(f"Linhas removidas: {removed}")
    print(f"Linhas restantes: {len(df)}")

    print("\n=== Distribuição de classe_futura ===")
    print(df["classe_futura"].value_counts().to_string())

    return df



def main():
    df = pd.read_csv(INPUT_PATH)

    required_columns = set(
        PAIR_COLUMNS + ["timestamp", "classe"]
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

    df["timestamp"] = pd.to_numeric(
        df["timestamp"],
        errors="coerce",
    )

    if df["timestamp"].isna().any():
        raise ValueError(
            "Existem timestamps ausentes ou inválidos."
        )

    if df["classe"].isna().any():
        raise ValueError("Existem classes atuais ausentes.")

    # Cria o alvo futuro ANTES do split.
    df = create_future_class(df)

    
    pairs = (
        df[PAIR_COLUMNS + ["distancia"]]
        .drop_duplicates(subset=PAIR_COLUMNS)
        .reset_index(drop=True)
    )


    expected_pairs = (
        TRAIN_PAIRS + VALIDATION_PAIRS + TEST_PAIRS
    )

    if len(pairs) != expected_pairs:
        raise ValueError(
            f"Esperados {expected_pairs} pares após criar "
            f"a classe futura, mas foram encontrados {len(pairs)}. "
            "Verifique se algum fluxo ficou sem medições válidas."
        )

    # Cada par é atribuído a exatamente um conjunto.
    pair_assignments = assign_pairs(pairs)

    split_df = df.merge(
        pair_assignments,
        on=PAIR_COLUMNS,
        how="left",
        validate="many_to_one",
    )

    if len(split_df) != len(df):
        raise RuntimeError(
            "A quantidade de medições mudou durante a divisão."
        )

    if split_df["split"].isna().any():
        raise RuntimeError(
            "Existem medições sem conjunto atribuído."
        )

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

    print(f"\nArquivo de entrada: {INPUT_PATH}")
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

    print("\n=== Classes futuras por conjunto ===")
    print(
        pd.crosstab(
            split_df["split"],
            split_df["classe_futura"],
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