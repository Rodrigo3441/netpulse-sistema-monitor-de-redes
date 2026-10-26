from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    recall_score,
)

from src.data_model.config import CLASSES


def evaluate_predictions(y_true, y_pred):
    labels = CLASSES

    return {
        "macro_f1": float(
            f1_score(
                y_true,
                y_pred,
                average="macro",
                labels=labels,
                zero_division=0,
            )
        ),
        "recall_falha": float(
            recall_score(
                y_true,
                y_pred,
                labels=["FALHA"],
                average="macro",
                zero_division=0,
            )
        ),
        "classification_report": classification_report(
            y_true,
            y_pred,
            labels=labels,
            zero_division=0,
            output_dict=True,
        ),
        "confusion_matrix": confusion_matrix(
            y_true,
            y_pred,
            labels=labels,
        ).tolist(),
        "confusion_matrix_labels": labels,
    }


def print_evaluation(title, metrics):
    print(f"\n=== {title} ===")
    print(f"Macro-F1 teste: {metrics['macro_f1']:.6f}")
    print(f"Recall FALHA teste: {metrics['recall_falha']:.6f}")
    print("\nRelatório de classificação (teste):")

    for label in CLASSES + ["macro avg", "weighted avg"]:
        values = metrics["classification_report"].get(label)
        if values is None:
            continue

        print(
            f"{label:>12}  "
            f"precision={values['precision']:.4f}  "
            f"recall={values['recall']:.4f}  "
            f"f1={values['f1-score']:.4f}  "
            f"support={int(values['support'])}"
        )
