
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

FLOW_COLUMNS = ["msm_id", "probe_id"]
TIME_COLUMN = "timestamp"

TRAIN_RATIO = 0.50
VALIDATION_RATIO = 0.20


def assign_split(flow):
    """Divide um fluxo ordenado em treino, validação e teste."""
    flow = flow.sort_values(TIME_COLUMN).copy()

    total = len(flow)

    train_end = int(total * TRAIN_RATIO)
    validation_end = int(
        total * (TRAIN_RATIO + VALIDATION_RATIO)
    )

    flow["split"] = "test"

    flow.iloc[
        :train_end,
        flow.columns.get_loc("split"),
    ] = "train"

    flow.iloc[
        train_end:validation_end,
        flow.columns.get_loc("split"),
    ] = "validation"

    return flow


def main():
    df = pd.read_csv(INPUT_PATH)

    required_columns = set(
        FLOW_COLUMNS + [TIME_COLUMN, "classe"]
    )

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Colunas ausentes no CSV: {sorted(missing_columns)}"
        )

    # Verifica se a identificação do fluxo e o timestamp
    # estão preenchidos.
    if df[FLOW_COLUMNS + [TIME_COLUMN]].isna().any().any():
        raise ValueError(
            "Existem valores ausentes em msm_id, probe_id "
            "ou timestamp."
        )

    # Cada fluxo deve ter no máximo uma medição por timestamp.
    duplicate_mask = df.duplicated(
        subset=FLOW_COLUMNS + [TIME_COLUMN],
        keep=False,
    )

    if duplicate_mask.any():
        raise ValueError(
            "Existem timestamps repetidos dentro de um fluxo. "
            "Inspecione os dados antes de dividir."
        )

    original_count = len(df)

    # Processa cada fluxo separadamente para preservar
    # a estrutura das colunas.
    parts = []

    for _, flow in df.groupby(FLOW_COLUMNS, sort=False):
        parts.append(assign_split(flow))

    if not parts:
        raise ValueError("O CSV não contém registros.")

    split_df = pd.concat(parts, ignore_index=True)

    # Verificações de integridade.
    if len(split_df) != original_count:
        raise RuntimeError(
            "A quantidade de registros mudou durante a divisão."
        )

    if split_df["split"].isna().any():
        raise RuntimeError(
            "Existem registros sem conjunto atribuído."
        )

    expected_splits = {"train", "validation", "test"}

    if set(split_df["split"].unique()) != expected_splits:
        raise RuntimeError(
            "A divisão não gerou os três conjuntos esperados."
        )

    # Confirma que os conjuntos seguem a ordem cronológica
    # dentro de cada fluxo.
    split_order = {
        "train": 0,
        "validation": 1,
        "test": 2,
    }

    for _, flow in split_df.groupby(FLOW_COLUMNS):
        flow = flow.sort_values(TIME_COLUMN)
        order = flow["split"].map(split_order)

        if not order.is_monotonic_increasing:
            raise RuntimeError(
                "A ordem temporal dos conjuntos está inconsistente."
            )

    # Salva o resultado sem modificar o arquivo original.
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    split_df.to_csv(OUTPUT_PATH, index=False)

    # Relatório da divisão.
    print(f"Arquivo de entrada: {INPUT_PATH}")
    print(f"Arquivo de saída: {OUTPUT_PATH}")
    print(f"Total de registros: {len(split_df)}")
    print(
        "Total de fluxos:",
        split_df.groupby(FLOW_COLUMNS).ngroups,
    )

    print("\n=== Quantidade por conjunto ===")
    print(
        split_df["split"]
        .value_counts()
        .reindex(["train", "validation", "test"], fill_value=0)
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

    print("\n=== Verificação dos percentuais ===")
    print(
        (
            split_df["split"].value_counts(normalize=True)
            .mul(100)
            .reindex(["train", "validation", "test"], fill_value=0)
        ).round(2).to_string()
    )

    print("\nDivisão concluída e verificações aprovadas.")


if __name__ == "__main__":
    main()
