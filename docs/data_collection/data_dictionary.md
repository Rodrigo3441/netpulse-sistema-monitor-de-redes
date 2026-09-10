# Dicionário de dados

Este documento descreve os dados resultantes da etapa de coleta e processamento inicial dos dados obtidos através da API do RIPE Atlas.

| Coluna | Tipo | Descrição |
|---|---|---|
| `timestamp` | timestamp | Data e hora em que a medição foi realizada. |
| `ip` | string | Endereço IP de origem da medição. |
| `latencia_ms` | float | Latência média (RTT) da medição, em milissegundos. O valor `-1` indica que não foi possível obter uma medição válida de latência. |
| `pacotes_enviados` | integer | Quantidade de pacotes enviados durante a medição. |
| `pacotes_recebidos` | integer | Quantidade de pacotes recebidos durante a medição. |