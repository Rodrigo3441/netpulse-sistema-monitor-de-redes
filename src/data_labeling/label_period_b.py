from pathlib import Path
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"

INPUT_PATH = INTERIM_DIR / "period_b_metrics.csv"
OUTPUT_PATH = INTERIM_DIR / "period_b_labeled.csv"

FLOW_COLUMNS = ["msm_id", "probe_id"]

METADATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "pairs_metadata.csv"
)


def load_data():
    """Carrega as métricas e incorpora a distância geográfica."""
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {INPUT_PATH}\n"
            "Execute calculate_metrics.py primeiro."
        )

    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo de metadados não encontrado: {METADATA_PATH}"
        )

    df = pd.read_csv(INPUT_PATH)
    metadata = pd.read_csv(METADATA_PATH)

    required_columns = {
        "msm_id",
        "probe_id",
        "anchor_id",
        "avg",
        "perda_pct",
        "z_robusto",
        "aumento_pct",
        "jitter_relativo",
        "n5_timeout",
        "n5_aumento80",
        "n5_risco",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Colunas obrigatórias ausentes no dataset: {sorted(missing)}"
        )

    metadata_columns = {
        "msm_id",
        "src_probe_id",
        "dst_anchor_id",
        "distancia",
    }

    missing_metadata = metadata_columns - set(metadata.columns)

    if missing_metadata:
        raise ValueError(
            "Colunas obrigatórias ausentes nos metadados: "
            f"{sorted(missing_metadata)}"
        )

    # Seleciona apenas as colunas necessárias para a junção.
    metadata = metadata[
        ["msm_id", "src_probe_id", "dst_anchor_id", "distancia"]
    ].copy()

    # Renomeia as chaves para corresponder ao dataset de métricas.
    metadata = metadata.rename(
        columns={
            "src_probe_id": "probe_id",
            "dst_anchor_id": "anchor_id",
        }
    )

    join_columns = ["msm_id", "probe_id", "anchor_id"]

    # Cada combinação deve identificar um único registro de metadados.
    if metadata.duplicated(join_columns).any():
        raise ValueError(
            "Existem combinações duplicadas de msm_id, probe_id "
            "e anchor_id nos metadados."
        )

    original_count = len(df)

    # Incorpora a distância sem multiplicar as medições.
    df = df.merge(
        metadata,
        on=join_columns,
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    unmatched = df["_merge"] != "both"

    if unmatched.any():
        examples = (
            df.loc[unmatched, join_columns]
            .drop_duplicates()
            .head(10)
            .to_dict("records")
        )

        raise ValueError(
            f"{unmatched.sum()} medições não possuem metadados "
            f"correspondentes. Exemplos: {examples}"
        )

    df = df.drop(columns="_merge")

    if len(df) != original_count:
        raise RuntimeError(
            "A quantidade de medições mudou durante a junção."
        )

    return df



def label_measurement(row):
    """
    Aplica as regras de rotulagem na ordem definida
    pelo professor. Para na primeira regra verdadeira.
    """
    rtt_presente = pd.notna(row["avg"]) and row["avg"] > 0

    # 1. FALHA: perda de pacotes na medição atual.
    if pd.notna(row["perda_pct"]) and row["perda_pct"] >= 10:
        return "FALHA", "perda_pct >= 10"

    # 2. FALHA: pelo menos 3 timeouts nas últimas 5 medições.
    if row["n5_timeout"] >= 3:
        return "FALHA", "n5_timeout >= 3"

    # 3. FALHA: desvio robusto extremo com RTT presente.
    if (
        rtt_presente
        and pd.notna(row["z_robusto"])
        and row["z_robusto"] >= 3.5
    ):
        return "FALHA", "z_robusto >= 3.5"

    # 4. FALHA: pelo menos 2 aumentos acima de 80%
    # nas últimas 5 medições.
    if row["n5_aumento80"] >= 2:
        return "FALHA", "n5_aumento80 >= 2"

    # 5. RISCO: critério atual presente E recorrência temporal.
    z_risco = (
        pd.notna(row["z_robusto"])
        and 2 <= row["z_robusto"] < 3.5
    )

    aumento_risco = (
        pd.notna(row["aumento_pct"])
        and 30 <= row["aumento_pct"] <= 80
    )

    jitter_risco = (
        pd.notna(row["jitter_relativo"])
        and row["jitter_relativo"] >= 3
    )

    criterio_risco_atual = (
        z_risco or aumento_risco or jitter_risco
    )

    if criterio_risco_atual and row["n5_risco"] >= 2:
        return "RISCO", "critério atual de risco e n5_risco >= 2"

    # 6. Nenhuma regra anterior foi satisfeita.
    return "OK", "nenhuma regra anterior satisfeita"


def main():
    df = load_data()

    # Mantém a ordem original das medições no arquivo.
    resultados = df.apply(label_measurement, axis=1)

    df[["classe", "regra_rotulagem"]] = pd.DataFrame(
        resultados.tolist(),
        index=df.index,
    )


    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Medições rotuladas: {len(df)}")
    print(f"Fluxos: {df[FLOW_COLUMNS].drop_duplicates().shape[0]}")
    print(f"Arquivo salvo em: {OUTPUT_PATH}")

    print("\n=== Contagem de classes ===")
    contagem = (
        df["classe"]
        .value_counts()
        .reindex(["OK", "RISCO", "FALHA"], fill_value=0)
    )

    for classe, quantidade in contagem.items():
        percentual = quantidade / len(df) * 100
        print(f"{classe}: {quantidade} ({percentual:.2f}%)")

    print("\n=== Regras que dispararam ===")
    print(df["regra_rotulagem"].value_counts().to_string())

    # Exemplos para auditoria: um de cada classe.
    colunas_exemplo = [
        "timestamp",
        "msm_id",
        "probe_id",
        "avg",
        "perda_pct",
        "z_robusto",
        "aumento_pct",
        "jitter_relativo",
        "n5_timeout",
        "n5_aumento80",
        "n5_risco",
        "classe",
        "regra_rotulagem",
    ]

    # OK com RTT relativamente alto, mas desvio robusto baixo.
    exemplos_ok = df[
        (df["classe"] == "OK")
        & (df["avg"] > 0)
        & (df["z_robusto"].abs() < 2)
    ].sort_values("avg", ascending=False)

    exemplos_risco = df[df["classe"] == "RISCO"]

    exemplos_falha = df[
        (df["classe"] == "FALHA")
        & (
            (df["timeout_atual"] == 1)
            | (df["n5_timeout"] >= 3)
        )
    ] if "timeout_atual" in df.columns else df[
        df["classe"] == "FALHA"
    ]

    print("\n=== Exemplos para auditoria ===")

    for nome, candidatos in [
        ("OK — RTT alto e z robusto baixo", exemplos_ok),
        ("RISCO", exemplos_risco),
        ("FALHA — timeout", exemplos_falha),
    ]:
        print(f"\n--- {nome} ---")

        if candidatos.empty:
            print("Nenhuma linha encontrada para este exemplo.")
            continue

        linha = candidatos.iloc[0]
        print(linha[colunas_exemplo].to_string())