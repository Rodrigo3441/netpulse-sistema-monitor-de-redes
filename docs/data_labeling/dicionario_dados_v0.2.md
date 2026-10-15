# Dicionário de Dados v0.2

## 1. Objetivo

Documentar as principais métricas utilizadas na rotulagem do Período B e identificar as colunas que não podem ser utilizadas como atributos da árvore de decisão.

## 2. Identificação e dados originais

| Coluna | Descrição |
|---|---|
| `msm_id` | Identificador da medição RIPE Atlas. |
| `probe_id` | Identificador da probe de origem. |
| `anchor_id` | Identificador do anchor de destino. |
| `timestamp` | Instante da medição, em Unix timestamp. |
| `avg` | RTT médio informado pela medição; `-1` indica ausência de RTT válido. |
| `sent` | Quantidade de pacotes enviados. |
| `rcvd` | Quantidade de pacotes recebidos. |
| `result` | Resultados individuais dos pacotes da medição. |

## 3. Métricas utilizadas

| Coluna | Descrição |
|---|---|
| `mediana` | Mediana dos RTTs válidos do fluxo no Período A. |
| `MAD` | Mediana dos desvios absolutos dos RTTs em relação à mediana. |
| `IQR` | Intervalo interquartil dos RTTs válidos da linha de base. |
| `z_robusto` | Desvio robusto do RTT atual em relação à linha de base. |
| `aumento_pct` | Aumento percentual do RTT em relação à mediana. |
| `perda_pct` | Percentual de pacotes perdidos na medição atual. |
| `jitter_atual` | Média das diferenças absolutas entre RTTs válidos consecutivos de uma medição. |
| `jitter_tipico` | Mediana dos valores de jitter calculados no Período A. |
| `jitter_relativo` | Relação entre o jitter atual e o jitter típico. |
| `timeout_atual` | Indicador de timeout na medição atual. |
| `n5_timeout` | Quantidade de timeouts nas últimas cinco medições do fluxo. |
| `n5_aumento80` | Quantidade de medições com aumento de RTT superior a 80% nas últimas cinco medições. |
| `n5_risco` | Quantidade de medições que satisfazem ao menos um critério de risco na janela de cinco medições. |

A linha de base é calculada exclusivamente com dados do Período A e permanece congelada durante a análise do Período B.

## 4. Rotulagem

| Coluna | Descrição |
|---|---|
| `classe` | Classe atribuída à medição: `OK`, `RISCO` ou `FALHA`. |
| `regra_rotulagem` | Regra que determinou a classe, respeitando a prioridade definida na especificação. |

## 5. Colunas proibidas como atributos da árvore

Não utilizar como atributos preditivos:

- País e endereços IP.
- `rota_id` e `fluxo_id`, quando presentes.
- Identificadores de fluxo ou medição, como `msm_id`, `probe_id` e `anchor_id`.
- RTT absoluto como substituto das métricas relativas.
- `classe`, pois é a variável-alvo.
- `regra_rotulagem`, pois registra a regra responsável pela classe.

As métricas relativas e temporais serão avaliadas como atributos candidatos, considerando que algumas participam diretamente da definição dos rótulos.