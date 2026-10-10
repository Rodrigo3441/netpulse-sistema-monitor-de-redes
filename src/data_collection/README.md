# Documentação dos Scripts de Coleta de Dados

Esta pasta contém os scripts responsáveis pela coleta, organização e preparação dos dados utilizados pelo projeto NetPulse.

## Scripts principais

| Arquivo | Função |
|---|---|
| `create_cache.py` | Inicia o processo de coleta e criação dos caches com os dados obtidos da API do RIPE Atlas. |
| `build_dataset.py` | Orquestra a geração dos arquivos CSV de metadados, treinamento e validação. |

## Pasta `extraction/`

Contém os módulos responsáveis pela extração e pelo armazenamento dos dados brutos.

| Arquivo | Função |
|---|---|
| `config.py` | Centraliza as configurações da coleta, incluindo os IDs dos anchors, das measurements e dos probes selecionados. |
| `cache.py` | Gerencia o armazenamento e o acesso aos dados em cache, evitando requisições desnecessárias à API. |
| `anchors.py` | Obtém e armazena os metadados dos anchors utilizados na coleta. |
| `probes.py` | Obtém e armazena os metadados dos probes de origem. |
| `measurements.py` | Obtém e armazena os metadados das medições do RIPE Atlas. |
| `results.py` | Obtém e armazena os resultados das medições para os períodos de treinamento e validação. |

## Pasta `dataset/`

Contém os módulos responsáveis por transformar os dados armazenados em datasets estruturados.

| Arquivo | Função |
|---|---|
| `builder.py` | Carrega os resultados e os metadados, combina as informações correspondentes e prepara os DataFrames com as colunas definidas para os datasets. |
| `pairs_metadata.py` | Constrói e exporta o CSV com os metadados dos pares de probes de origem e anchors de destino. |

## Fluxo geral

1. `create_cache.py` inicia o processo de coleta.
2. Os módulos de `extraction/` obtêm e armazenam os dados da API do RIPE Atlas.
3. `build_dataset.py` inicia a preparação dos arquivos CSV.
4. Os módulos de `dataset/` combinam e organizam os dados.
5. Os arquivos finais são exportados para uso nas próximas etapas do projeto.