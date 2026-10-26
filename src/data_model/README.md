# Modelagem

Scripts de treino da árvore de decisão e da random forest, a partir de `data/interim/period_b_split.csv`.

O notebook `Arvore_e_random_forest_didatico.ipynb` é só a referência didática. O projeto roda pelos arquivos `.py`.

## Arquivos

| Arquivo | O que faz |
|---|---|
| `config.py` | Define caminhos, features, alvo, semente e as grades de hiperparâmetros. |
| `load_dataset.py` | Lê o CSV, valida as colunas e separa treino, validação e teste. |
| `search.py` | Roda o `GridSearchCV` respeitando o split já definido. |
| `evaluate.py` | Calcula as métricas do conjunto de teste. |
| `persist.py` | Grava o modelo (`.joblib`), os metadados (`.json`) e o resultado da busca (`.csv`). |
| `train_decision_tree.py` | Treina a árvore de decisão. |
| `train_random_forest.py` | Treina a random forest. |
| `train_models.py` | Entrada alternativa para treinar os dois modelos juntos. |

Hiperparâmetros e features são ajustados em `config.py`.

## Fluxo de execução

1. `load_dataset.py` carrega e divide os dados.
2. `train_decision_tree.py` busca hiperparâmetros, avalia e salva a árvore.
3. `train_random_forest.py` faz o mesmo para a floresta.

Na prática, isso é disparado pelo orquestrador `src/etl_data_model.py`, no mesmo estilo da coleta e da rotulação.

Os dois scripts de treino também podem ser executados sozinhos. Os arquivos gerados ficam em `data/models/`.
