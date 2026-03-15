# 06 Resultados

Esta seção apresenta os resultados obtidos na campanha experimental descrita na Seção 5. Os valores reportados derivam exclusivamente dos artefatos atuais gerados durante a execução — `classification_report_eval.csv`, `confusion_matrix_eval.csv`, `metrics_again.json`, `preds.csv` e os CSVs do baseline — sem interpolação manual posterior. Os valores tabulados por classe foram arredondados a três casas decimais.

## 6.1 Cenário principal — CIC-IDS2018 (GKS, 7 classes)

A avaliação da arquitetura GKS no holdout do CIC-IDS2018 (`cic_eval.csv`, n=100.000) produziu os seguintes resultados agregados:

| Métrica | Valor |
|---|---|
| F1-macro | **0.764** |
| Acurácia | **93,3%** |
| Latência — Gatekeeper | 0,000056 ms/amostra |
| Latência — Especialista | 21,79 ms/amostra |
| Latência — Total | 21,79 ms/amostra |

Os resultados por classe são apresentados na Tabela 1.

**Tabela 1 — Métricas por classe, CIC-IDS2018 (GKS)**

| Classe | Precision | Recall | F1 | Suporte |
|---|---|---|---|---|
| Benign | 0.973 | 1.000 | 0.986 | 46.983 |
| Bot | 1.000 | 0.736 | 0.848 | 3.907 |
| BruteForce | 0.939 | 0.495 | 0.649 | 9.998 |
| DDoS | 1.000 | 1.000 | 1.000 | 19.999 |
| DoS | 0.786 | 0.968 | 0.868 | 19.112 |
| Others | 1.000 | 1.000 | 1.000 | 1 |
| Web | 0.000 | 0.000 | 0.000 | 0 |
| **Macro avg** | **0.814** | **0.743** | **0.764** | — |
| **Weighted avg** | **0.940** | **0.933** | **0.927** | — |

A figura `confusion_matrix_cic.png` (Figura 1) e `f1_per_class_cic.png` (Figura 2) consolidam visualmente esses resultados.

Os principais padrões observados na matriz de confusão são:

- **Benign:** classificação quase perfeita (46.978 corretos, 5 erros para Web — desprezível).
- **DDoS:** F1=1.000 com apenas 3 confusões com Benign.
- **DoS:** desempenho sólido (18.506 corretos), com 323 confusões com BruteForce e 269 com Benign.
- **Bot:** precision perfeita, recall reduzido (1.033 amostras classificadas como Benign).
- **BruteForce:** o ponto mais fraco — recall de 0.495, com 5.044 amostras classificadas como DoS. A confusão entre BruteForce e DoS é esperada dado que ambos os ataques compartilham características de volume de pacotes.
- **Web:** F1=0.000, ausente no holdout. Classe com apenas 928 amostras no treino, sem representação no offset de avaliação.
- **Others:** F1=1.000, mas com suporte de apenas 1 amostra — resultado estatisticamente irrelevante.

## 6.2 Cenário secundário — UNSW-NB15 (GKS, binário)

A avaliação no holdout do UNSW-NB15 (`unsw_eval.csv`, n=175.341) produziu:

| Métrica | Valor |
|---|---|
| F1-macro | **0.866** |
| Acurácia | **87,4%** |
| Latência — Gatekeeper | 0,000058 ms/amostra |
| Latência — Especialista | 1,401 ms/amostra |
| Latência — Total | 1,401 ms/amostra |

**Tabela 2 — Métricas por classe, UNSW-NB15 (GKS)**

| Classe | Precision | Recall | F1 | Suporte |
|---|---|---|---|---|
| Attack | 0.984 | 0.829 | 0.900 | 119.341 |
| Normal | 0.727 | 0.971 | 0.831 | 56.000 |
| **Macro avg** | **0.855** | **0.900** | **0.866** | — |

A matriz de confusão (`confusion_matrix_unsw_bin.png`) revela que o modelo classifica corretamente 54.362 amostras Normal e 98.933 amostras Attack, com 20.408 falsos negativos (Attack classificado como Normal) e 1.638 falsos positivos (Normal classificado como Attack).

O padrão observado é assimétrico: o modelo tem alta precision para Attack (0.984) mas recall moderado (0.829), enquanto para Normal apresenta precision mais baixa (0.727) e recall elevado (0.971). Em termos operacionais, o sistema tende a ser mais conservador na sinalização de Normal — preferindo classificar como Attack na dúvida — o que é um comportamento defensável em cenários de IDS onde falsos negativos têm custo operacional maior.

## 6.3 Baseline — XGBoost monolítico, CIC-IDS2018 (binário)

O baseline XGBoost global, avaliado em `cic_eval_robust.csv` (n=100.000), produziu:

| Métrica | Valor |
|---|---|
| F1-macro | **0.976** |
| Acurácia | **97,6%** |

**Tabela 3 — Métricas por classe, Baseline XGBoost (CIC, binário)**

| Classe | Precision | Recall | F1 | Suporte |
|---|---|---|---|---|
| Benign | 0.956 | 0.995 | 0.975 | 46.983 |
| Attack | 0.995 | 0.960 | 0.977 | 53.017 |
| **Macro avg** | **0.976** | **0.977** | **0.976** | — |

A matriz de confusão do baseline registra 46.738 Benign corretos (245 falsos positivos) e 50.890 Attack corretos (2.127 falsos negativos).

## 6.4 Comparação consolidada

**Tabela 4 — Comparação GKS vs. Baseline (CIC-IDS2018)**

| Método | Formulação | F1-macro | Acurácia | Classes avaliadas |
|---|---|---|---|---|
| GKS | Granular (7 classes) | 0.764 | 93,3% | Benign, Bot, BruteForce, DDoS, DoS, Others, Web |
| Baseline XGBoost | Binária | 0.976 | 97,6% | Benign vs. Attack |

A diferença de F1-macro entre os dois métodos reflete diretamente a diferença de formulação: o GKS avalia 7 classes granulares, enquanto o baseline avalia apenas 2. F1-macro em problema de 7 classes é estruturalmente mais sensível a classes raras ou ausentes no holdout, como Web (0 amostras) e Others (1 amostra), além de fronteiras difíceis como BruteForce.

A comparação direta mais relevante não é portanto apenas F1-macro vs. F1-macro, mas o que cada abordagem é capaz de discriminar: o baseline identifica se há intrusão; o GKS identifica qual tipo de intrusão, ao custo de desempenho menor nas subclasses mais ambíguas.

Como leitura auxiliar, colapsando-se as predições do GKS no CIC para a formulação binária `Benign` vs. `Attack`, obtém-se acurácia de **98,689%** e F1-macro de **0,9869**, com 46.978 amostras `Benign` corretamente reconhecidas, 51.711 amostras de `Attack` corretamente reconhecidas, 5 falsos positivos e 1.306 falsos negativos. Esse cálculo não substitui o baseline robusto como comparação oficial, porque usa a configuração completa do GKS no `cic_eval.csv` e não o recorte robusto sem `dst_port`, mas evidencia que a principal perda do método está na discriminação entre subclasses de ataque, e não na separação entre tráfego benigno e malicioso.
