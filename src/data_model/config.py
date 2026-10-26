from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = PROJECT_ROOT / "data" / "interim" / "period_b_split.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "models"

SEED = 42
CLASSES = ["OK", "RISCO", "FALHA"]

TARGET_COLUMN = "classe_futura"
SPLIT_COLUMN = "split"

SPLIT_TRAIN = "train"
SPLIT_VALIDATION = "validation"
SPLIT_TEST = "test"

# Métricas relativas e temporais candidatas. Identificadores, IPs,
# RTT absoluto, classe atual e regra de rotulagem ficam de fora.
FEATURES = [
    "perda_pct",
    "aumento_pct",
    "z_robusto",
    "jitter_atual",
    "jitter_relativo",
    "timeout_atual",
    "n5_timeout",
    "n5_aumento80",
    "n5_risco",
]

SCORING = "f1_macro"
N_JOBS_SEARCH = -1

# True usa as grades didáticas completas do notebook de referência
# False usa só a combinação vencedora comentada no notebook (busca rápida).
USAR_GRADE_COMPLETA = True

GRADE_ARVORE_COMPLETA = {
    "max_depth": [3, 5, 8, 12, None],
    "min_samples_leaf": [1, 20, 100],
    "class_weight": [None, "balanced"],
}

GRADE_ARVORE_RAPIDA = {
    "max_depth": [None],
    "min_samples_leaf": [100],
    "class_weight": [None],
}

GRADE_RF_COMPLETA = {
    "n_estimators": [100, 200],
    "max_depth": [6, 12, None],
    "min_samples_leaf": [5, 50],
    "max_features": ["sqrt"],
    "class_weight": [None, "balanced_subsample"],
}

GRADE_RF_RAPIDA = {
    "n_estimators": [100],
    "max_depth": [None],
    "min_samples_leaf": [5],
    "max_features": ["sqrt"],
    "class_weight": [None],
}

GRADE_ARVORE = (
    GRADE_ARVORE_COMPLETA if USAR_GRADE_COMPLETA else GRADE_ARVORE_RAPIDA
)
GRADE_RF = GRADE_RF_COMPLETA if USAR_GRADE_COMPLETA else GRADE_RF_RAPIDA

ARVORE_JOBLIB_NAME = "modelo_arvore_decisao.joblib"
ARVORE_METADATA_NAME = "metadados_arvore_decisao.json"
ARVORE_GRID_NAME = "busca_arvore_decisao.csv"

RF_JOBLIB_NAME = "modelo_random_forest.joblib"
RF_METADATA_NAME = "metadados_random_forest.json"
RF_GRID_NAME = "busca_random_forest.csv"
