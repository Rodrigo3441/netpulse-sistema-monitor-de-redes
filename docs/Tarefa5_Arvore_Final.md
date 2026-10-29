# Diário da Tarefa 5 — Árvore final e teste único

**Período:** 12/10/2026 a 25/10/2026  
**Projeto:** Preditor de degradação de rede com RTT normalizado (independente da rota)

**Equipe:** <br>
`Eduardo Gabriel de Souza Cardozo`<br> `Gabriel Alves de Farias`<br> `Gisele Franco de Lima`<br> `Luigi Santos Caires`<br> `Rodrigo de Souza Galvão`<br>
**Scrum Master da tarefa:**  Rodrigo de Souza Galvão<br>
**Repositório GitHub:** `https://github.com/Rodrigo3441/netpulse-sistema-monitor-de-redes`

> A árvore que entra aqui é a da Tarefa 4. O baseline e o rótulo são os da Tarefa 2. O teste, guardado desde a Tarefa 2, é medido **uma vez**.
>
> Continua sendo uma árvore de decisão. O grupo entrega as regras, a matriz e o que a árvore faz num fluxo que ela não viu — desde que esse fluxo tenha a própria ficha de baseline, calculada só no período inicial dele.

### Contrato desta tarefa

| | Artefato | Origem / destino |
|---|---|---|
| **Entra** | Corte da Tarefa 2 e ficha de baseline | Tarefa 2 |
| **Entra** | Árvore ajustada e regras | Tarefa 4 |
| **Sai** | Teste único: matriz 3×3, F1 por classe, F1 macro | Entrega |
| **Sai** | Checagem de fluxo não visto, com baseline próprio | Entrega |
| **Sai** | Ficha da árvore (abaixo) e dicionário v0.4 igual às colunas usadas | Entrega |

Não há tarefa seguinte.

- [X] A profundidade não foi escolhida de novo olhando o teste
- [X] O baseline do teste não usou medição do próprio teste

---

## 1. Árvore que será medida

- [X] Critério, profundidade, mínimo de amostras na folha, colunas
- [X] Três regras em português, as mesmas da Tarefa 4 ou as revistas **antes** de abrir o teste
- [X] Confirmação de que país, IP, rota e RTT absoluto não estão na árvore

**Parâmetros:**
- Critério: `gini` (padrão do scikit-learn).
- Profundidade máxima: `5`.
- Mínimo de amostras por folha: `100`.
- Peso das classes: `balanced`.
- Métrica de seleção: `f1_macro`.

**Colunas:**
- `perda_pct`
- `aumento_pct`
- `z_robusto`
- `jitter_atual`
- `jitter_relativo`
- `timeout_atual`
- `n5_timeout`
- `n5_aumento80`
- `n5_risco`

**Regras:**

1. Valores elevados de `z_robusto` podem indicar desvios relevantes em relação ao comportamento habitual da latência.
2. Aumentos em `aumento_pct` e `jitter_relativo` podem indicar instabilidade na rede.
3. A recorrência de indicadores como `n5_timeout` e `n5_risco` pode ajudar a identificar situações de degradação persistente.

**Observação:** as regras são interpretações gerais das características utilizadas, não condições exatas extraídas da árvore treinada.


## 2. Teste temporal (uma vez)

Fluxos conhecidos, período mais recente do Período B.

- [X] Matriz 3×3 com contagem, não só porcentagem
- [X] Precisão, recall e F1 de OK, RISCO e FALHA
- [X] F1 macro
- [X] Recall de FALHA e a troca RISCO ↔ FALHA comentados

**Matriz:**

| Classe real \ Predita | OK | RISCO | FALHA |
|---|---:|---:|---:|
| OK | 6946 | 1065 | 141 |
| RISCO | 361 | 265 | 27 |
| FALHA | 282 | 1624 | 1807 |

**Métricas por classe:**

| Classe | Precisão | Recall | F1-score |
|---|---:|---:|---:|
| OK | 0.9153 | 0.8521 | 0.8825 |
| RISCO | 0.0897 | 0.4058 | 0.1469 |
| FALHA | 0.9149 | 0.4867 | 0.6354 |

**F1 macro no teste:** 0.5549


## 3. O que declarar

- [X] Se a árvore só repete a tabela de rótulo, dizer isso: o rótulo foi feito com as mesmas métricas, então a árvore está aprendendo a política, não um ticket de roteador
- [X] Se o alvo for o estado 12 minutos à frente, comparar com a regra “repetir a classe atual”. Sem ganho nessa comparação, o entregável é um **detector** do estado atual, não um preditor
- [X] Limitações: baseline fixo não acompanha troca de rota; rajada curta estima mal o jitter; Anchors não são a rede do campus

## 4. Ficha da árvore

| Campo | Conteúdo |
|---|---|
| Problema | Classe OK, RISCO ou FALHA pelo desvio ao baseline do fluxo |
| Unidade | Uma medição de um `fluxo_id` no Período B |
| Baseline | Período A, mediana e MAD, piso de 1.500 RTT válidos |
| Colunas | `perda_pct`, `aumento_pct`, `z_robusto`, `jitter_atual`, `jitter_relativo`, `timeout_atual`, `n5_timeout`, `n5_aumento80`, `n5_risco` |
| Árvore | Critério Gini, profundidade máxima 5, mínimo de 100 amostras por folha e semente 42 |
| Teste (uma vez) | F1 macro: 0,5549; recall de FALHA: 0,4867 (48,67%) |
| O que ela não faz | Não classifica distância. Não opera em fluxo sem ficha. |
| Como reproduzir | `requirements.txt`, notebook, `config/` |

## 5. Scrum e diário

- [X] Board atualizado

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| @Rodrigo | Preenchi esse documento | A forma como preencher os campos | Alguma seção que não tenha sido preenchida muito bem |

---

## Rubrica — Tarefa 5 (0 a 4,0)

| Critério | Peso | Nota máxima | Nota | Observações |
|---|---|---|---|---|
| Árvore final legível | 1,0 | Regras em português, colunas relativas, parâmetros da Tarefa 4 | | |
| Teste único | 1,5 | Matriz 3×3 em contagem, F1 por classe, F1 macro, casos curto/longo; teste não escolheu a árvore | | |
| Fluxo novo com baseline próprio | 1,0 | Ficha só no período inicial; ou limitação declarada se faltou fluxo | | |
| Ficha + diário | 0,5 | Ficha preenchida e diário de todos | | |
| **Total** | **4,0** | | **___ / 4,0** | |
