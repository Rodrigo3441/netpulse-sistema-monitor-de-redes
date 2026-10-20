# Dados Intermediários (`interim`)

Esta pasta armazena os arquivos intermediários gerados durante a preparação dos dados. Eles são utilizados nas etapas de cálculo de métricas, rotulagem e divisão temporal dos dados.

## Arquivos

| Arquivo | Descrição |
|---|---|
| `baseline_por_fluxo.csv` | Contém as estatísticas de referência de cada fluxo, calculadas com os dados do Período A. Inclui mediana, MAD, IQR, jitter típico, perda típica e proporção de respostas válidas. |
| `fluxos_excluidos.csv` | Registra os fluxos que não atenderam aos critérios definidos para a construção da linha de base, como a quantidade mínima de RTTs válidos. |
| `period_b_metrics.csv` | Contém as medições do Período B com as métricas calculadas em relação à linha de base, incluindo z-score robusto, aumento percentual, perda, jitter relativo e indicadores temporais. |
| `period_b_labeled.csv` | Contém as medições do Período B com as classes `OK`, `RISCO` e `FALHA`, além da regra que justificou cada classificação. |
| `period_b_split.csv` | Contém os dados rotulados do Período B com a coluna `split`, que identifica cada registro como treino (`train`), validação (`validation`) ou teste (`test`).<br> Fluxos estão definidos na proporção de 20/5/5: `20 fluxos para treinamento`, `5 para validação`, `5 para teste`. |
