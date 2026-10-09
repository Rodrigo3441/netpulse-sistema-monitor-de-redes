# Documentação dos Dados Brutos

Esta pasta contém os arquivos CSV gerados a partir dos dados coletados pela API do RIPE Atlas.

## Arquivos disponíveis

| Arquivo | Descrição |
|---|---|
| `pairs_metadata.csv` | Contém os metadados dos pares probe de origem → anchor de destino, incluindo IDs, países e coordenadas geográficas. |
| `training.csv` | Contém os resultados de ping destinados ao treinamento, enriquecidos com os metadados dos anchors, probes e medições. |
| `validation.csv` | Contém os resultados de ping destinados à validação, utilizando a mesma estrutura de colunas do conjunto de treinamento. |

## Períodos dos datasets

Os datasets de treinamento e validação possuem janelas temporais consecutivas, sem sobreposição.

| Dataset | Período de coleta | Duração |
|---|---|---|
| `training.csv` | De `currentTime - 14 dias` até `currentTime - 7 dias` | 7 dias |
| `validation.csv` | De `currentTime - 7 dias` até `currentTime` | 7 dias |

`currentTime` representa o instante de referência utilizado pelo processo de coleta. O início de cada intervalo é inclusivo e o fim é exclusivo.

## Colunas dos datasets

Os arquivos `training.csv` e `validation.csv` possuem as mesmas 17 colunas.

| Coluna | Descrição |
|---|---|
| `anchor_id` | Identificador do anchor de destino. |
| `anchor_ip` | Endereço IPv4 do anchor de destino. |
| `probe_id` | Identificador do probe de origem. |
| `probe_ip` | Endereço IPv4 do probe de origem. |
| `msm_id` | Identificador da medição no RIPE Atlas. |
| `ttl` | Valor de Time to Live informado no resultado. |
| `result` | Informações do resultado de ping retornadas pela API. |
| `dup` | Quantidade de respostas duplicadas, quando informada. |
| `rcvd` | Quantidade de respostas recebidas. |
| `sent` | Quantidade de pacotes enviados. |
| `min` | Menor latência medida. |
| `max` | Maior latência medida. |
| `avg` | Latência média medida. |
| `timestamp` | Instante do resultado, representado por um timestamp Unix. |
| `type` | Tipo de medição, como `ping`. |
| `packets` | Quantidade de pacotes configurados por medição. |
| `interval` | Intervalo configurado entre as medições, em segundos. |
