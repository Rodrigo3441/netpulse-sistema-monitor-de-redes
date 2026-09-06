# Memorando de Decisão — Fonte de Dados do Projeto


| Campo | Informação |
|---|---|
| Curso / Disciplina | `Estrutura de Dados II` |
| Projeto integrador | `Entrutura de Dados II, Redes de Computadores e Análise e Projeto de Sistemas` |
| Orientador(a) | `Professora Andréia` |
| Data de entrega desta etapa | `08/09/2026` |
| Integrantes do grupo | `Eduardo Gabriel de Souza Cardozo, Gabriel Alves de Farias, Gisele Franco de Lima, Luigi Santos Caires, Rodrigo de Souza Galvão` |

---

> Preencha cada seção com o que você encontrou na pesquisa. Não deixe nenhum campo com o texto entre colchetes — substitua pelo seu conteúdo. Toda informação levantada nas Opções A e B precisa indicar a fonte de onde veio.

## 1. Situação

<!-- Em uma frase: qual decisão precisa ser tomada e por quê. 
O pipeline do projeto já está definido: qualquer fonte de dados precisa produzir registros que se transformem em janelas e, por fim, em X = [latência, perda, jitter]. Falta decidir de onde virão esses dados na próxima fase. A equipe do projeto precisa recomendar, com base em pesquisa e não em preferência pessoal, se a próxima etapa deve usar um dataset real já publicado ou a API do RIPE Atlas. O grupo deve produzir um memorando de decisão com a recomendação da tomada de decisão. A recomendação só tem valor se for sustentada por pesquisa real — não existe resposta pronta para copiar; ela precisa ser construída a partir do que vocês encontraram.
-->

A equipe precisa decidir entre utilizar um dataset real de medições ICMP já publicado ou a API do RIPE Atlas como fonte de dados para o treinamento e alimentação do preditor de falhas, considerando seu controle sobre coleta, diversidade geográfica, complexidade de implementação e disponibilidade de dados.

## 2. Opção A — Dataset real

<!-- O que foi encontrado sobre um dataset real de ICMP. Cite a fonte de cada informação. -->

- **Origem / link:** Hats Network — Global Latency Measurements
- **Formato:** CSV, JSON e YAML. O dataset disponibiliza tanto séries de pings individuais quanto estatísticas agregadas.
- **Período coberto:** O dataset possui versões diárias; a versão consultada é de 08/08/2026. Novas versões são publicadas diariamente quando há novas medições.
- **Campos disponíveis:** Nos registros individuais: from, to, round_id, seq, offset_ms e rtt_ms. Também existem estatísticas agregadas como rtt_avg, rtt_min, rtt_max, rtt_stdev, jitter_ms e packet_loss_percent.
- **Licença de uso:** CC BY 4.0 (Creative Commons Attribution 4.0 International). Permite compartilhar e adaptar os dados, desde que seja dado o devido crédito

**Resumo do que foi encontrado:**

O Hats Network Global Latency Measurements é um dataset público produzido a partir de medições reais de ICMP Echo na rede de produção da Hats Network. Cada par de pontos de presença (PoP) é medido com 50 requisições ICMP, enviadas em intervalos de 100 ms. Os resultados são disponibilizados tanto individualmente, com o RTT de cada pacote, quanto de forma agregada. O dataset também fornece estatísticas de latência, jitter e perda de pacotes. A estrutura dos dados é adequada para o projeto porque permite trabalhar com vários registros temporais de uma mesma rodada e posteriormente agrupá-los em janelas.

## 3. Opção B — API do RIPE Atlas

<!-- O que foi encontrado sobre a API: autenticação, criação e consulta de medições. Cite a fonte de cada informação. -->

- **Documentação consultada (link):** https://atlas.ripe.net/docs/getting-started/

- **Autenticação exigida:** 

Para utilizar a API para ver medições não precisa de chave mas para fazer medições precisamos da chave da api e creditos, e para criarmos uma chave precisaremos fazer uma conta no site https://atlas.ripe.net/. **COMO CRIAR UMA CHAVE:** https://atlas.ripe.net/docs/howtos/keys 

**DOC:** https://atlas.ripe.net/docs/apis/rest-api-manual/authentication/

- **Como se cria uma medição:** 

Precisa de creditos e uma chave api para criar uma medição, tendo os dois voce precisa especificar pelo menos um sendo ele, description (Descrição da medida), target (endereço ip alvo), type (tipo de formato de medição, usaremos o ping) e af (Adress family) **DOC:** https://atlas.ripe.net/docs/apis/rest-api-manual/measurements/

- **Como se consultam os resultados:**

Para fazer uma consulta dos resultados é preciso ter o id da medição feita e fazer um get utilizando a biblioteca requests do python e passar a url dentro dos parametros https://atlas.ripe.net/api/v2/measurements/{ID da medição}/results/.
**DOC:** https://atlas.ripe.net/docs/apis/rest-api-manual/measurements/results-and-latest

**Resumo do que foi encontrado:**

Na documentação do ripe atlas sobre a API rest que utilizaremos encontramos como fazer um request get e post, criar chaves e o mais importante como fazer e pegar medições publicas.

## 4. Comparação

<!-- Preencha a tabela com base no que você levantou nas seções 2 e 3. -->

| Critério | Opção A — Dataset real | Opção B — API RIPE Atlas |
|----------|------------------------|--------------------------|
| Controle sobre a coleta | |Parcial|
| Diversidade geográfica | |Global|
| Custo / complexidade de implementação | |Alto|
| Tempo até os primeiros dados estarem disponíveis | |Depende|

## 5. Recomendação

<!-- Uma frase direta: qual opção você recomenda. -->

[Escreva aqui]

## 6. Justificativa

<!-- Por que essa opção vence a outra, com base nas evidências das seções 2, 3 e 4 — não em preferência pessoal. -->

A **opção A - Dataset real** é mais adequada para esta etapa, pois ela já diponibiliza os dados reais de ICMP, incluindo a latência, o jitter e a perda de pacotes, compatíveis com as variáveis do projeto. Além disso, os dados já ficam estruturados e disponíveis para uso, reduzindo o tempo e a complexidade inicial de implementação.

Enquanto o **RIPE Atlas** oferece maior diversidade geográfica e permite realizar novas medições, mas a criação delas exige configuração da API, autenticação e a utilização de créditos. Portanto, o dataset apresenta melhor relação entre a disponibilidade, a simplicidade e tempo de implementação nesta fase do projeto.

## 7. Riscos e limitações

<!-- O que pode dar errado com a opção escolhida, e como isso poderia ser mitigado. -->

[Escreva aqui]

## 8. Contribuição Individual dos Integrantes

<!-- cada integrante deve descrever, com suas próprias palavras, o que efetivamente fez nesta etapa. Contribuições genéricas como "ajudei em tudo" não serão aceitas. Use verbos de ação e seja específico (ex.: "pesquisei , analisei, testei, ... apresentei prós/contras ao grupo, ...").-->

### Integrante 1 — `[Escreva nome completo do aluno ]`
- **O que fez nesta etapa:** `[]`
- **Tempo dedicado (aprox.):** `[ex.: 3h30]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*:
`[]` 
`[]`

### Integrante 2 — `[Escreva nome completo do aluno ]`
- **O que fez nesta etapa:** `[]`
- **Tempo dedicado (aprox.):** `[ex.: 3h30]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*:
`[]` 
`[]`

### Integrante 3 — `[Escreva nome completo do aluno ]`
- **O que fez nesta etapa:** `[]`
- **Tempo dedicado (aprox.):** `[ex.: 3h30]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*: 
`[]` 
`[]`

### Integrante 4 — `[Escreva nome completo do aluno ]`
- **O que fez nesta etapa:** `[]`
- **Tempo dedicado (aprox.):** `[ex.: 3h30]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*: 
`[]` 
`[]`

### Integrante 5 — `[Escreva nome completo do aluno ]`
- **O que fez nesta etapa:** `[]`
- **Tempo dedicado (aprox.):** `[ex.: 3h30]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*: 
`[]` 
`[]`

---

## Fontes consultadas

<!-- Mínimo de 3 fontes. Liste todas as páginas de documentação, artigos ou repositórios usados. -->

1. HATS NETWORK INC. Hats Network Global Latency Measurements. Disponível em: https://hatsnet.io/opendata/latency/. Acesso em: 6 set. 2026.

2. RIPE NCC. Authentication — RIPE Atlas Documentation. Disponível em: https://atlas.ripe.net/docs/apis/rest-api-manual/authentication/. Acesso em: 6 set. 2026.

3. RIPE NCC. Creating Measurements — RIPE Atlas Documentation. Disponível em: https://atlas.ripe.net/docs/apis/rest-api-manual/measurements/creating-measurements/. Acesso em: 6 set. 2026.
