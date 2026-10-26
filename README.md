# NetPulse — Sistema de Monitoramento e Predição de Falhas em Redes
Sistema para monitoramento de métricas de rede com análise em tempo real e predição de falhas fazendo uso de árvore de decisão e usando como base de dados a RIPE Atlas API.

## 👨‍💻 Equipe e contexto acadêmico:

- Eduardo Gabriel de Souza Cardozo
- Gabriel Alves de Farias
- Gisele Franco de Lima
- Luigi Santos Caires
- Rodrigo de Souza Galvão

Esse projeto possui conexão com as seguintes disciplinas:

- Redes de Computadores
- Análise e Projeto de Sistemas
- Estrutura de Dados II

A metodologia adotada para esse projeto será a SCRUM

## 📑 Problemas e objetivos

O problema é identificar antecipadamente possíveis falhas de rede a partir de métricas de conectividade é um desafio. Busca-se investigar como dados reais de rede podem ser utilizados para identificar condições de risco por meio de aprendizado de máquina.

O objetivo é desenvolver um sistema de monitoramento e predição de falhas em redes utilizando dados da RIPE Atlas API.

- Coletar e processar medições de rede.
- Preparar e rotular datasets para modelagem.
- Treinar e avaliar modelos de Árvore de Decisão e Random Forest.
- Classificar condições futuras dos fluxos em OK, RISCO e FALHA.


## Arquitetura do Sistema

## Tecnologias utilizadas

## Pipeline de dados

## 💾 Modelos e resultados


Foram avaliados dois algoritmos de aprendizado de máquina: **Árvore de Decisão** e **Random Forest**, com ajuste de hiperparâmetros e avaliação em conjunto de teste com 12.518 registros.

| Métrica | Árvore de Decisão | Random Forest |
|---|---:|---:|
| Acurácia | 72,04% | **82,72%** |
| Macro F1-score | 0,555 | **0,630** |
| Recall — FALHA | 48,67% | **75,73%** |
| Recall — RISCO | **40,58%** | 22,51% |

O **Random Forest apresentou o melhor resultado geral**, com maior acurácia, Macro F1-score e capacidade de identificar a classe FALHA. Entretanto, ambos os modelos apresentaram dificuldades na classificação de RISCO, indicando oportunidades para melhorias na metodologia e no desempenho preditivo.

Os resultados e os metadados dos experimentos são utilizados para documentar os parâmetros selecionados e as métricas obtidas.

## Estrutura do Projeto

``` bash
netpulse-sistema-monitor-de-redes/
├── archive/                       # arquivos de dados inutilizados
├── data/                          
│   ├── interim/                   # contem dados referente ao dataset processado
│   ├── models/                    # contem metadados sobre os modelos
│   └── raw/                       # contem os datasets do período A e B, e metadados
├── docs/                          # contem a documentação do projeto
├── notebooks/                     # contem notebooks que foram usados durante a construção do projeto
├── src/                                   
│   ├── data_collection/           # contem os scripts relacionados a coleta e criação do cache
│   ├── data_labeling/             # contem os scripts relacionamos a rotulação dos dados
│   ├── data_model/                # contem os scripts do treinamento dos modelos
│   ├── etl_data_collection.py     # orquestrador da etapa de criação do cache
│   ├── etl_data_labeling.py       # orquestrador da etapa de rotulação
│   └── etl_data_model.py          # orquestrador do treinamento dos modelos
├── .gitignore          
├── LICENSE
├── main.py                        # arquivo de execução principal do projeto
└── README.md
```

## Como executar

## Limitações e próximos passos

### Limitações
- Desempenho limitado na classificação da classe RISCO.
- Necessidade de ampliar e diversificar os dados utilizados nos experimentos.
- Resultados ainda restritos aos dados e às condições avaliadas.

### Próximos passos
- Investigar estratégias para melhorar a classificação de RISCO.
- Explorar novos atributos e técnicas de engenharia de dados.
- Avaliar outros algoritmos e estratégias de ajuste de hiperparâmetros.
- Ampliar os testes com dados de diferentes períodos e fluxos de rede.
