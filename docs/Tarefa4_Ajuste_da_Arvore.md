# Diário da Tarefa 4 — Ajuste da árvore a partir do erro

**Período:** 05/10/2026 a 11/10/2026  
**Projeto:** Preditor de degradação de rede com RTT normalizado (independente da rota)

**Equipe:** <br>
`Eduardo Gabriel de Souza Cardozo`<br> `Gabriel Alves de Farias`<br> `Gisele Franco de Lima`<br> `Luigi Santos Caires`<br> `Rodrigo de Souza Galvão`<br>
**Scrum Master da tarefa:** Eduardo Gabriel de Souza Cardozo  <br>
**Repositório GitHub:** `https://github.com/Rodrigo3441/netpulse-sistema-monitor-de-redes`

> O rótulo e o baseline da Tarefa 2 continuam. O corte temporal continua. Esta tarefa **não troca o algoritmo**: ajusta a mesma árvore de decisão com o que a Tarefa 3 errou.
>
> Ajuste permitido: profundidade, mínimo de amostras na folha, critério (Gini ou entropia) e poda. Se entrar coluna nova, ela tem de ser outra métrica **relativa ao baseline** (tendência do `z_robusto` nas janelas anteriores, por exemplo). País, IP, rota e RTT absoluto continuam fora.

### Contrato desta tarefa

| | Artefato | Origem / destino |
|---|---|---|
| **Entra** | Árvore da Tarefa 3, matriz e erros | Tarefa 3 |
| **Entra** | Mesmo baseline, mesmo rótulo, mesmo corte | Tarefa 2 |
| **Sai** | Árvore ajustada e tabela Tarefa 3 → Tarefa 4 (F1 macro e recall de FALHA na validação) | Tarefa 5 usa **esta** árvore como ponto de partida |
| **Sai** | Regras novas em português | Tarefa 5 |
| **Sai** | Dicionário v0.3, se nasceu coluna relativa nova | Tarefa 5 |

**Não sai daqui:** outro tipo de modelo, mudança do teste, recálculo do baseline com o Período B.

- [X] O corte é o da Tarefa 2
- [X] Nenhuma coluna de rota entrou

---

## 1. O que o erro pediu

- [X] Citar os erros da Tarefa 3 (classe confundida, caminho longo ou curto, pico isolado virando FALHA, RISCO sumindo)
- [X] Cada mudança da árvore responde a um desses erros
- [X] Parâmetros escolhidos na validação

**Erro da Tarefa 3 → mudança na árvore:**

| Erro observado | Mudança (profundidade, folha, critério ou métrica relativa nova) |
|---|---|
| Acurácia de 100% devido à ausência de deslocamento temporal das classes, permitindo que o modelo previsse a classe da própria observação em vez da classe futura. | Implementação do deslocamento temporal de 12 minutos (`HORIZON_SECONDS = 12 * 60`), usando a classe futura como alvo da previsão.  |


## 2. Árvore ajustada

- [X] Mesmas colunas relativas, mais o que a tabela acima acrescentou
- [X] Profundidade, folhas e três regras em português
- [X] Fit só no treino

**Parâmetros finais candidatos (ainda não é o teste):** 

- `max_depth = 5`
- `min_samples_leaf = 100`
- `class_weight = "balanced"`
- `criterion = "gini"` (padrão do scikit-learn)
- `scoring = "f1_macro"`

**Regras:**

1.  Se o desvio relativo da latência (`z_robusto`) for elevado, a árvore pode classificar a situação como risco ou falha.
2.  Se houver aumento relativo da latência (`jitter_relativo` ou `aumento_pct`), a árvore pode usar esses sinais para diferenciar situações normais de instabilidade.
3.  Se os indicadores temporais, como `n5_risco`, apontarem problemas recorrentes, a árvore pode considerar a situação mais crítica.


## 3. Comparação no teste: antes e depois da correção temporal


| Modelo | F1 macro | Acurácia | Recall de FALHA | Recall de RISCO |
|---|---:|---:|---:|---:|
| Árvore antes da correção temporal | 1.0000* | 1.0000* | — | — |
| Árvore após a correção temporal | 0.5549 | 0.7204 | 0.4867 | 0.4058 |

- [X] Se não houve ganho, dizer o que foi tentado e descartado
- [X] Matriz 3×3 da árvore desta tarefa, na validação

**Matriz de confusão da árvore após a correção:**

| Classe real \ Predita | OK | RISCO | FALHA |
|---|---:|---:|---:|
| OK | 6946 | 1065 | 141 |
| RISCO | 361 | 265 | 27 |
| FALHA | 282 | 1624 | 1807 |

**Leitura do ganho (ou da falta de ganho):**

Antes da correção, a árvore apresentava 100% de acurácia devido à ausência do deslocamento temporal do alvo, comprometendo a validade da avaliação. Após a correção, o modelo passou a prever a classe futura, considerando um horizonte de 12 minutos. A acurácia caiu para 72,04% e o F1 macro ficou em 0,5549, resultados mais realistas para avaliar a capacidade de generalização do modelo. O recall de FALHA foi de 48,67%, enquanto o de RISCO foi de 40,58%, mostrando que ainda existem dificuldades para identificar corretamente essas situações.


## 4. Revisão com o docente

**O que foi mostrado:**  
**O que foi pedido para ajustar antes da Tarefa 5:**

## 5. Scrum e diário

- [X] Board atualizado

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| @Eduardo | Preenchi esse documento | A forma como preencher os campos | Alguma seção que não tenha sido preenchida muito bem |

---

## Rubrica — Tarefa 4 (0 a 4,0)

| Critério | Peso | Nota máxima | Nota | Observações |
|---|---|---|---|---|
| Ajuste ligado ao erro | 1,5 | Cada mudança da árvore cita um erro da Tarefa 3; continua árvore de decisão | | |
| Rota fora do modelo | 1,0 | Nenhuma coluna de rota, país, IP ou RTT absoluto; baseline da Tarefa 2 intacto | | |
| Tabela Tarefa 3 → Tarefa 4 | 1,0 | F1 macro e recall de FALHA e de RISCO na validação, com leitura | | |
| Revisão + diário | 0,5 | Incremento mostrado ao docente; diário de todos | | |
| **Total** | **4,0** | | **___ / 4,0** | |
