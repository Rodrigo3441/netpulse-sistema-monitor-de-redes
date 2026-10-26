import json

import joblib
import numpy as np
import pandas as pd

from src.data_model.config import FEATURES, OUTPUT_DIR, SEED


def json_ready(value):
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}

    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]

    if isinstance(value, np.ndarray):
        return json_ready(value.tolist())

    if isinstance(value, (np.floating, np.integer)):
        return value.item()

    if isinstance(value, np.bool_):
        return bool(value)

    if pd.isna(value):
        return None

    return value


def build_metadata(familia, busca, metrics, n_combinacoes):
    importances = getattr(busca.best_estimator_, "feature_importances_", None)

    if importances is None:
        feature_importances = {}
    else:
        feature_importances = {
            feature: float(score)
            for feature, score in zip(FEATURES, importances)
        }

    return {
        "familia": familia,
        "seed": SEED,
        "features": list(FEATURES),
        "n_combinacoes_grade": n_combinacoes,
        "best_params": json_ready(busca.best_params_),
        "macro_f1_validacao": float(busca.best_score_),
        "macro_f1_teste": metrics["macro_f1"],
        "recall_falha_teste": metrics["recall_falha"],
        "classification_report": json_ready(metrics["classification_report"]),
        "confusion_matrix": metrics["confusion_matrix"],
        "confusion_matrix_labels": metrics["confusion_matrix_labels"],
        "feature_importances": feature_importances,
    }


def save_artifacts(familia, busca, metrics, n_combinacoes, joblib_name, metadata_name, grid_name):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    metadata = build_metadata(familia, busca, metrics, n_combinacoes)

    joblib_path = OUTPUT_DIR / joblib_name
    metadata_path = OUTPUT_DIR / metadata_name
    grid_path = OUTPUT_DIR / grid_name

    joblib.dump(
        {
            "familia": familia,
            "modelo": busca.best_estimator_,
            "best_params": busca.best_params_,
            "features": list(FEATURES),
            "macro_f1_validacao": metadata["macro_f1_validacao"],
            "macro_f1_teste": metadata["macro_f1_teste"],
            "recall_falha_teste": metadata["recall_falha_teste"],
            "seed": SEED,
        },
        joblib_path,
    )

    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    pd.DataFrame(busca.cv_results_).to_csv(grid_path, index=False)

    print(f"\nModelo salvo em: {joblib_path}")
    print(f"Metadados salvos em: {metadata_path}")
    print(f"Resultados da busca salvos em: {grid_path}")

    return {
        "joblib_path": joblib_path,
        "metadata_path": metadata_path,
        "grid_path": grid_path,
        "metadata": metadata,
    }
