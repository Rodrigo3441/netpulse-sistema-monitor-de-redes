# Estrutura do diretório src

O diretório `src/` contém os módulos responsáveis pelas principais etapas do NetPulse, organizados de acordo com suas respectivas responsabilidades.

### 📁 data_collection/
Responsável pela coleta de dados da API RIPE Atlas, incluindo medições de rede, probes e informações dos anchors.

### 📁 data_labeling/
Responsável pelo processamento dos dados coletados, construção do baseline, cálculo de métricas, extração de features e classificação dos fluxos em OK, RISCO ou FALHA.

### 📁 data_model/
Contém a implementação dos modelos de Machine Learning, treinamento, avaliação e exportação dos modelos treinados.

### 📁 data_visualization/
Responsável pela criação e apresentação dos resultados em uma página html, permitindo comparar o desempenho dos modelos e consultar suas métricas.

---

## Scripts ETL

Os scripts ETL funcionam como orquestradores das principais etapas do pipeline, organizando a execução dos módulos.

| Script | Responsabilidade |
|---|---|
| `etl_data_colletion.py` | Orquestra a coleta e extração dos dados da RIPE Atlas. |
| `etl_data_labeling.py` | Orquestra o processamento, construção do baseline, cálculo das métricas e rotulagem dos dados. |
| `etl_data_model.py` | Orquestra o treinamento, avaliação e exportação dos modelos de Machine Learning. |

**Fluxo geral:**

`Coleta → Processamento e Rotulagem → Treinamento e Avaliação → Visualização`

Cada diretório mantém suas responsabilidades separadas, facilitando a organização, manutenção e evolução do projeto.