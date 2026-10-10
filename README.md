# NetPulse — Sistema de Monitoramento e Predição de Falhas em Redes
Sistema para monitoramento de métricas de rede com análise em tempo real e predição de falhas fazendo uso de árvore de decisão e usando como base de dados a RIPE Atlas API.

## 👨‍💻 Equipe:

- Eduardo Gabriel de Souza Cardozo
- Gabriel Alves de Farias
- Gisele Franco de Lima
- Luigi Santos Caires
- Rodrigo de Souza Galvão

## 🔗 Projeto Interdisciplinar
Esse projeto possui conexão com as seguintes disciplinas:

- Redes de Computadores
- Análise e Projeto de Sistemas
- Estrutura de Dados II

## 📑 Metodologia:

A metodologia adotada para esse projeto será a SCRUM

## Estrutura do Projeto

``` bash
netpulse-sistema-monitor-de-redes/
├── archive/
├── cache/
├── docs/
├── notebooks/
├── raw/
├── src/
│   └── data_collection/
│       ├── dataset/
│       │   ├── builder.py
│       │   └── pairs_metadata.py
│       ├── extraction/
│       │   ├── anchors.py
│       │   ├── cache.py
│       │   ├── config.py
│       │   ├── measurements.py
│       │   ├── probes.py
│       │   └── results.py
│       ├── build_dataset.py
│       └── create_cache.py
├── .gitignore
├── LICENSE
├── main.py
└── README.md
```