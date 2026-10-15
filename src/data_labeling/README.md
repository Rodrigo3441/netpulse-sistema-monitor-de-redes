# Data Labeling

Esta pasta contém os scripts responsáveis pela preparação, cálculo de métricas e rotulagem dos dados do projeto NetPulse.

## Scripts

| Script | Responsabilidade |
|---|---|
| `inspect_dataset.py` | Inspeciona os datasets e ajuda a entender sua estrutura e qualidade antes do processamento. |
| `build_baseline.py` | Constrói a linha de base de cada fluxo usando exclusivamente os dados do Período A. Calcula estatísticas de referência, como mediana, MAD, IQR, jitter típico e perda típica. |
| `calculate_metrics.py` | Calcula as métricas do Período B em relação à linha de base congelada, incluindo aumento percentual, z-score robusto, perda, jitter relativo e indicadores temporais. |
| `label_period_b.py` | Atribui as classes `OK`, `RISCO` e `FALHA` às medições do Período B. |
| `split_dataset.py` | Divide cronologicamente as medições rotuladas de cada fluxo em treino (`train`), validação (`validation`) e teste (`test`), adicionando a coluna `split`. |

## Ordem de execução

Os scripts principais devem ser executados nesta ordem:

1. `build_baseline.py`
2. `calculate_metrics.py`
3. `label_period_b.py`
4. `split_dataset.py`

O `inspect_dataset.py` é um script auxiliar para inspeção dos dados e pode ser executado quando necessário.

## Arquivos gerados

Os principais arquivos intermediários ficam em `data/interim/`:

- `baseline_por_fluxo.csv`: estatísticas de referência por fluxo.
- `fluxos_excluidos.csv`: fluxos que não atendem aos critérios para construção da linha de base.
- `period_b_metrics.csv`: métricas calculadas para o Período B.
- `period_b_labeled.csv`: medições do Período B com suas classes e regras de rotulagem.
- `period_b_split.csv`: dataset rotulado com a coluna `split`.

**Observação:** o Período A é usado para construir a linha de base, enquanto o Período B é usado para calcular métricas, atribuir classes e preparar os conjuntos de treino, validação e teste.