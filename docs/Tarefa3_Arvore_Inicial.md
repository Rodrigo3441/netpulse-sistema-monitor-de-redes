# Diário da Tarefa 3 — Primeira árvore de decisão

**Período:** 28/09/2026 a 04/10/2026  
**Projeto:** Preditor de degradação de rede com RTT normalizado (independente da rota)

**Equipe:** <br>
`Eduardo Gabriel de Souza Cardozo`<br> `Gabriel Alves de Farias`<br> `Gisele Franco de Lima`<br> `Luigi Santos Caires`<br> `Rodrigo de Souza Galvão`<br>
**Scrum Master da tarefa:** Gisele Franco de Lima<br>  
**Repositório GitHub:** `https://github.com/Rodrigo3441/netpulse-sistema-monitor-de-redes`

> Tarefa 1 coletou. Tarefa 2 fez o baseline e o rótulo. Esta tarefa **não refaz** a ficha nem a tabela de classes.
>
> O modelo é uma **árvore de decisão**. O entregável é a árvore: atributos de cada divisão, profundidade, folhas e as regras lidas em português. Não é um desfile de algoritmos.
>
> A árvore oficial usa só métricas relativas ao baseline do fluxo. Uma segunda árvore, de contraste, pode ver a rota ou o RTT absoluto — só para mostrar que ela aprende distância. Essa árvore de contraste **não** é o modelo do projeto.

### Contrato desta tarefa

| | Artefato | Origem / destino |
|---|---|---|
| **Entra** | Ficha de baseline, dataset rotulado, corte temporal | Tarefa 2 — **os mesmos** |
| **Sai** | Árvore treinada só no treino, com profundidade e critério registrados | Tarefa 4 mexe nesta árvore, não no rótulo |
| **Sai** | Regras da árvore em texto e matriz 3×3 (OK, RISCO, FALHA) | Tarefa 4, para atacar o erro |
| **Sai** | Árvore de contraste (com rota ou RTT absoluto) e a frase do que ela aprendeu | Prova de que o modelo oficial não segue esse atalho |

**Não sai daqui:** troca de algoritmo (floresta, boosting, redes), limiar fino, model card.

- [X] Treino, validação e teste são os da Tarefa 2
- [X] A ficha de baseline não foi recalculada com o Período B

---

## 1. Colunas que a árvore oficial pode usar

Entram: `z_robusto`, `aumento_pct`, `jitter_relativo`, `perda_pct`, `timeout_atual`, `n5_timeout`, `n5_aumento80`, `n5_risco`.

Não entram: país, IP, `rota_id`, `fluxo_id`, nome do destino, RTT em milissegundos no lugar das métricas relativas.

- [X] Lista de colunas do treino colada no diário
- [X] Conferido que a classe (`OK` / `RISCO` / `FALHA`) é o alvo, não uma feature

**Colunas usadas:**
- `z_robusto`
- `aumento_pct`
- `jitter_relativo`
- `perda_pct`
- `timeout_atual`
- `n5_timeout`
- `n5_aumento80`
- `n5_risco`

## 2. A árvore

- [X] Uma árvore de decisão (CART: Gini ou entropia — declarar qual)
- [X] `max_depth` e `min_samples_leaf` escolhidos olhando **só a validação**, não o teste
- [X] Semente registrada se o treino for estocástico
- [X] Ajuste (`fit`) só no treino
- [X] Profundidade real, número de folhas e as primeiras divisões descritas
- [X] Pelo menos três regras no formato “se métrica ≤ limiar e … então classe”, copiadas da árvore (não inventadas)

**Critério, profundidade máxima pedida, profundidade obtida, folhas:**  
- Critério: Balancear classes
- Profundidade Máxima: 5
- Folhas: 100

**Regras lidas da árvore:**

1.  se (aumento_pct <= 1.311) e (jitter_relativo <= 3.139) e (z_robusto <= 1.921) então OK
2.  se (z_robusto > 2.702) e (jitter_relativo <= 3.182) e (z_robusto <= 4.354) então RISCO
3.  se (z_robusto > 2.702) e (jitter_relativo <= 3.182) e (z_robusto > 4.354) então FALHA

## 3. Leitura do erro

No bloco de **validação** (o teste fica fechado até a Tarefa 5; se o grupo já mediu o teste aqui, registra e **não** escolhe profundidade de novo olhando esse número):

- [X] Matriz 3×3 com contagem
- [X] Precisão, recall e F1 de OK, RISCO e FALHA
- [X] F1 macro
- [X] Acurácia sozinha não decide: com maioria OK, ela fica alta mesmo errando FALHA
- [X] Dois erros concretos: uma medição de caminho longo estável que tenha caído em FALHA, ou uma FALHA de caminho curto que tenha caído em OK. Se não houver, dizer que o caso não apareceu na validação

**Matriz e F1 macro (validação):**  

- [x] Matriz 3×3 com contagem
- [x] Precisão, recall e F1 de OK, RISCO e FALHA
- [x] F1 macro

**Matriz e F1 macro (teste):**

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

**F1 macro:** 0.5549  
**Acurácia:** 0.7204


## 4. Árvore de contraste (não é o modelo)

Treinar outra árvore, no mesmo treino, acrescentando a rota ou o RTT absoluto.

- [X] Dizer qual divisão apareceu perto da raiz (em geral a rota ou um corte fixo de milissegundos)
- [X] Declarar que essa árvore fica fora da entrega final

## 5. Scrum e diário

- [X] Board atualizado

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| @Gisele| Preenchi esse documento | A forma como preencher os campos | Alguma seção que não tenha sido preenchida muito bem |

---

## Rubrica — Tarefa 3 (0 a 4,0)

| Critério | Peso | Nota máxima | Nota | Observações |
|---|---|---|---|---|
| Árvore oficial | 1,5 | Uma árvore, critério e profundidade declarados, regras em português, fit só no treino | | |
| Métricas de três classes | 1,0 | Matriz 3×3, F1 por classe e F1 macro; acurácia não é o critério | | |
| Independência da rota | 1,0 | Colunas relativas apenas; árvore de contraste mostra o atalho da distância e é descartada | | |
| Scrum + diário | 0,5 | Board e diário de todos | | |
| **Total** | **4,0** | | **___ / 4,0** | |
