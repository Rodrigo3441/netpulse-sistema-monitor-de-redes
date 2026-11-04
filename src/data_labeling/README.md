# Rotulação

Esta pasta contém os scripts responsáveis pela preparação, cálculo de métricas e rotulagem dos dados do projeto NetPulse.

## Scripts

| Script | Responsabilidade |
|---|---|
| `inspect_dataset.py` | Inspeciona os datasets e ajuda a entender sua estrutura e qualidade antes do processamento. |
| `build_baseline.py` | Constrói uma linha de base para cada fluxo utilizando exclusivamente os dados do Período A. Calcula estatísticas de referência, como mediana, MAD, IQR, jitter típico e perda típica. Exige pelo menos 1.500 RTTs válidos por fluxo e gera indicadores de validade e recomendação de uso do baseline, separando os fluxos com quantidade insuficiente de dados. |
| `calculate_metrics.py` | Calcula as métricas do Período B em relação à linha de base congelada, incluindo aumento percentual, z-score robusto, perda, jitter relativo e indicadores temporais. |
| `label_period_b.py` | Realiza a rotulagem das medições do Período B, atribuindo as classes OK, RISCO e FALHA por meio de regras hierárquicas que consideram perda de pacotes, timeouts, desvios de RTT, jitter e recorrência temporal. Também incorpora a distância geográfica dos fluxos a partir dos metadados e registra a regra responsável por cada classificação em regra_rotulagem, permitindo auditar os resultados. |
| `split_dataset.py` | Cria a variável-alvo classe_futura utilizando um horizonte mínimo de 12 minutos, associando cada medição à classe da primeira medição futura elegível do mesmo par. Remove registros sem uma medição futura correspondente e divide os pares em conjuntos de treino (train), validação (validation) e teste (test), utilizando uma distribuição aleatória e estratificada por categoria de distância, com seed 42. Garante que cada par pertença exclusivamente a um conjunto e adiciona a coluna split ao dataset. |

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