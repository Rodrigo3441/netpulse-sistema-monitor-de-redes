# Exemplos Auditáveis de Rotulagem — NetPulse

## 1. Objetivo

Apresentar três medições reais do Período B para demonstrar como as regras de rotulagem são aplicadas. A classificação respeita a prioridade das regras: FALHA, RISCO e OK.

## 2. Exemplo OK

- `timestamp`: 1790954730
- `msm_id`: 18399117
- `probe_id`: 6358
- `avg`: 430,622 ms
- `mediana`: 404,403 ms
- `z_robusto`: 1,763
- `aumento_pct`: 6,48%
- `jitter_relativo`: 2,900
- `n5_risco`: 4
- **Classe:** OK
- **Regra:** nenhuma regra anterior satisfeita.

**Justificativa:** embora o RTT seja elevado, o desvio robusto é inferior a 2, o aumento percentual é inferior a 30% e o jitter relativo é inferior a 3. A medição atual não satisfaz nenhum critério de RISCO ou FALHA.

**Observação:** a classificação demonstra que RTT absoluto elevado não determina a classe. A caracterização desse exemplo como caminho longo depende da confirmação da distância entre os endpoints.

## 3. Exemplo RISCO

- `timestamp`: 1790828391
- `msm_id`: 11863561
- `probe_id`: 6251
- `avg`: 65,603 ms
- `z_robusto`: 1,601
- `aumento_pct`: 0,59%
- `jitter_relativo`: 3,603
- `n5_risco`: 2
- **Classe:** RISCO
- **Regra:** critério atual de risco e `n5_risco >= 2`.

**Justificativa:** o jitter relativo é maior ou igual a 3 e pelo menos duas das últimas cinco medições satisfazem algum critério de risco. Como nenhuma regra anterior de FALHA é satisfeita, a medição recebe RISCO.

## 4. Exemplo FALHA por timeout/perda

- `timestamp`: 1790905289
- `msm_id`: 18399117
- `probe_id`: 6349
- `avg`: -1
- `perda_pct`: 100%
- `timeout_atual`: 1
- **Classe:** FALHA
- **Regra:** `perda_pct >= 10`.

**Justificativa:** a medição não possui RTT válido e apresenta perda total de pacotes. A primeira regra de FALHA é satisfeita, encerrando a avaliação das regras seguintes.

## 5. Conclusão

Os exemplos ilustram três comportamentos distintos: uma medição que não satisfaz os critérios de alerta, uma medição com jitter relativo elevado e uma medição com perda total de pacotes. As classes são atribuídas pelas métricas e regras especificadas, não por um limite absoluto de RTT.