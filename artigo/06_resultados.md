# 06 Resultados

Esta seção apresenta os resultados obtidos na campanha experimental. Os valores reportados derivam exclusivamente dos artefatos gerados durante a execução, sem interpolação manual posterior. Valores tabulados por classe foram arredondados a três casas decimais.

### 5.1 Cenário principal — CIC-IDS2018 (GKS, 7 classes)

Tabela 3 – Métricas agregadas, CIC-IDS2018 (GKS)

|                         |                     |
|:------------------------|:-------------------:|
| **Métrica**             |      **Valor**      |
| **F1-macro**            |      **0,764**      |
| **Acurácia**            |      **93,3%**      |
| Latência – Gatekeeper   | 0,000056 ms/amostra |
| Latência – Especialista |  21,789 ms/amostra  |
| Latência – Total        |  21,789 ms/amostra  |

*Fonte: elaborado pelo autor (2026).*

Tabela 4 – Métricas por classe, CIC-IDS2018 (GKS)

|                  |               |            |           |             |
|:-----------------|:-------------:|:----------:|:---------:|:-----------:|
| **Classe**       | **Precision** | **Recall** |  **F1**   | **Suporte** |
| Benign           |     0,973     |   1,000    |   0,986   |   46.983    |
| Bot              |     1,000     |   0,736    |   0,848   |    3.907    |
| BruteForce       |     0,939     |   0,495    |   0,649   |    9.998    |
| DDoS             |     1,000     |   1,000    |   1,000   |   19.999    |
| DoS              |     0,786     |   0,968    |   0,868   |   19.112    |
| Others           |     1,000     |   1,000    |   1,000   |      1      |
| Web              |     0,000     |   0,000    |   0,000   |      0      |
| **Macro avg**    |   **0,814**   | **0,743**  | **0,764** |    **—**    |
| **Weighted avg** |   **0,940**   | **0,933**  | **0,927** |    **—**    |

*Fonte: elaborado pelo autor (2026).*

A figura 1 e a figura 2 consolidam visualmente esses resultados.

![Figura 1 – Matriz de confusão do GKS no CIC-IDS2018.](../reports/cic/confusion_matrix_cic.png){ width=14cm }

Figura 1 – Matriz de confusão do GKS no CIC-IDS2018.

*Fonte: elaborado pelo autor (2026).*

![Figura 2 – F1 por classe do GKS no CIC-IDS2018.](../reports/cic/f1_per_class_cic.png){ width=14cm }

Figura 2 – F1 por classe do GKS no CIC-IDS2018.

*Fonte: elaborado pelo autor (2026).*

Os principais padrões observados na matriz de confusão são: Benign com classificação quase perfeita (46.978 corretos, 5 erros); DDoS com F1=1,000 e apenas 3 confusões com Benign; DoS com desempenho sólido (18.506 corretos), com 323 confusões com BruteForce e 269 com Benign; Bot com precision perfeita, mas recall reduzido (1.033 amostras classificadas como Benign); BruteForce como ponto mais fraco — recall de 0,495, com 5.044 amostras classificadas como DoS; Web com F1=0,000, ausente no holdout; e Others com F1=1,000, mas suporte de apenas 1 amostra, o que torna o resultado estatisticamente irrelevante.

### 5.2 Cenário secundário — UNSW-NB15 (GKS, binário)

Tabela 5 – Métricas por classe, UNSW-NB15 (GKS)

|               |               |            |           |             |
|:--------------|:-------------:|:----------:|:---------:|:-----------:|
| **Classe**    | **Precision** | **Recall** |  **F1**   | **Suporte** |
| Attack        |     0,984     |   0,829    |   0,900   |   119.341   |
| Normal        |     0,727     |   0,971    |   0,831   |   56.000    |
| **Macro avg** |   **0,855**   | **0,900**  | **0,866** |    **—**    |

*Fonte: elaborado pelo autor (2026).*

A avaliação no holdout do UNSW-NB15 (n=175.341) produziu F1-macro de 0,866 e acurácia de 87,4%. O modelo classifica corretamente 54.362 amostras Normal e 98.933 amostras Attack, com 20.408 falsos negativos e 1.638 falsos positivos.

![Figura 3 – Matriz de confusão do GKS no UNSW-NB15.](../reports/unsw_bin/confusion_matrix_unsw_bin.png){ width=14cm }

Figura 3 – Matriz de confusão do GKS no UNSW-NB15.

*Fonte: elaborado pelo autor (2026).*

![Figura 4 – F1 por classe do GKS no UNSW-NB15.](../reports/unsw_bin/f1_per_class_unsw_bin.png){ width=14cm }

Figura 4 – F1 por classe do GKS no UNSW-NB15.

*Fonte: elaborado pelo autor (2026).*

O padrão é assimétrico: alta precision para Attack (0,984) e recall moderado (0,829), enquanto para Normal a precision é mais baixa (0,727) e o recall elevado (0,971). Em termos operacionais, o sistema tende a classificar como Attack na dúvida, comportamento defensável em cenários de IDS onde falsos negativos têm custo operacional maior.

### 5.3 Baseline — XGBoost monolítico, CIC-IDS2018 (binário)

Tabela 6 – Métricas por classe, Baseline XGBoost (CIC, binário)

|               |               |            |           |             |
|:--------------|:-------------:|:----------:|:---------:|:-----------:|
| **Classe**    | **Precision** | **Recall** |  **F1**   | **Suporte** |
| Benign        |     0,956     |   0,995    |   0,975   |   46.983    |
| Attack        |     0,995     |   0,960    |   0,977   |   53.017    |
| **Macro avg** |   **0,976**   | **0,977**  | **0,976** |    **—**    |

*Fonte: elaborado pelo autor (2026).*

O baseline XGBoost global (n=100.000) produziu F1-macro de 0,976 e acurácia de 97,6%, com 46.738 Benign corretos (245 falsos positivos) e 50.890 Attack corretos (2.127 falsos negativos).

### 5.4 Comparação consolidada

Tabela 7 – Comparação GKS vs. Baseline (CIC-IDS2018)

|  |  |  |  |  |
|:---|:---|:--:|:--:|:---|
| **Método** | **Formulação** | **F1-macro** | **Acurácia** | **Classes avaliadas** |
| GKS | Granular (7 classes) | 0,764 | 93,3% | Benign, Bot, BruteForce, DDoS, DoS, Others, Web |
| Baseline XGBoost | Binária robusta | 0,976 | 97,6% | Benign vs. Attack |
| GKS colapsado\* | Binária derivada | 0,987 | 98,7% | Benign vs. Attack (derivado) |

*Fonte: elaborado pelo autor (2026).*

*\* Leitura auxiliar derivada do preds.csv multiclasse; não substitui o baseline robusto oficial.*

Tabela 8 – Resumo de latência por estágio

|  |  |  |  |  |
|:---|:---|:--:|:--:|:--:|
| **Método** | **Dataset** | **Lat. Stage 1 (ms)** | **Lat. Stage 2 (ms)** | **Lat. Total (ms)** |
| GKS | CIC-IDS2018 | 0,000056 | 21,789 | 21,789 |
| GKS | UNSW-NB15 | 0,000058 | 1,401 | 1,401 |
| XGBoost global | CIC robusto | N/A | N/A | N/A |

*Fonte: elaborado pelo autor (2026).*

A diferença de F1-macro entre os dois métodos reflete diretamente a diferença de formulação. O GKS avalia 7 classes granulares, o baseline avalia apenas 2. A comparação direta mais relevante não é portanto apenas F1-macro vs. F1-macro, mas o que cada abordagem é capaz de discriminar: o baseline identifica se há intrusão; o GKS identifica qual tipo de intrusão.
