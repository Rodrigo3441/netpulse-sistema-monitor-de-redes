# Documentação dos Dados Brutos

Esta pasta contém os arquivos CSV gerados a partir dos dados coletados pela API do RIPE Atlas.

## Arquivos disponíveis

| Arquivo | Descrição |
|---|---|
| `pairs_metadata.csv` | Contém os metadados dos pares probe de origem → anchor de destino, incluindo IDs, países e coordenadas geográficas. |
| `period_a.csv`<br>`period_b.csv` | Contém os resultados de ping, enriquecidos com os metadados dos anchors, probes e medições. |


## Períodos dos datasets

Os datasets possuem janelas temporais consecutivas, sem sobreposição.

| Dataset | Período de coleta | Duração |
|---|---|---|
| `period_a.csv` | De `currentTime - 14 dias` até `currentTime - 7 dias` | 7 dias |
| `period_b.csv` | De `currentTime - 7 dias` até `currentTime` | 7 dias |

`currentTime` representa o instante de referência utilizado pelo processo de coleta. O início de cada intervalo é inclusivo e o fim é exclusivo.

## Colunas dos datasets

Os arquivos `period_a.csv` e `period_b.csv` possuem as mesmas 17 colunas.

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

### Metadados - Classificação de Distância Geográfica 

A distância geográfica entre cada probe de origem e a âncora de destino foi calculada utilizando a fórmula de Haversine, que estima a distância em linha reta entre duas coordenadas geográficas (latitude e longitude), em quilômetros.

As distâncias foram classificadas em três categorias:

- **Curta:** distância inferior a 1.000 km.
- **Média:** distância entre 1.000 km e 5.000 km, incluindo os limites.
- **Longa:** distância superior a 5.000 km.