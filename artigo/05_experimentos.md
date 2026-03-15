# 05 Experimentos

### 4.1 Delineamento experimental

O delineamento experimental foi estruturado para avaliar, de forma reprodutível, a arquitetura GKS em três leituras complementares: um cenário principal multiclasse no CIC-IDS2018, um cenário secundário binário no UNSW-NB15 e um baseline XGBoost monolítico binário no recorte robusto do CIC. Os scripts e configurações do pipeline são versionados no repositório; os valores reportados foram verificados diretamente nos artefatos atuais de data/, outputs/ e reports/.

### 4.2 Datasets e preparação

**CIC-IDS2018.** O dataset CIC-IDS2018 é composto por dez arquivos CSV diários, totalizando aproximadamente 6,5 GB de tráfego de rede capturado em condições controladas, cobrindo datas entre fevereiro e março de 2018. A preparação adotou uma estratégia de coleta proporcional por arquivo, coletando até 30.000 linhas de cada CSV bruto para o conjunto de treino e as 10.000 linhas subsequentes (offset disjunto) para o holdout de avaliação. Foram aplicados: normalização de nomes de colunas para snake_case; descarte de colunas de metadados de identificação; conversão forçada para tipo numérico com substituição de Infinity por 0; remoção de colunas 100% nulas; e alinhamento de colunas por interseção entre arquivos antes da concatenação. O arquivo 03-01-2018.csv foi descartado automaticamente por não apresentar colunas numéricas válidas.

Tabela 1 – Conjuntos de dados preparados para o CIC-IDS2018

|  |  |  |  |
|:---|:--:|:--:|:---|
| **Arquivo** | **Linhas** | **Features** | **Classes presentes** |
| train_cic.csv | 300.000 | 78 | Benign, Bot, BruteForce, DDoS, DoS, Others, Web |
| cic_eval.csv | 100.000 | 78 | Benign, Bot, BruteForce, DDoS, DoS, Others |
| train_cic_robust.csv | 300.000 | 77 | Idem (sem dst_port) |
| cic_eval_robust.csv | 100.000 | 77 | Idem (sem dst_port) |

*Fonte: elaborado pelo autor (2026).*

**UNSW-NB15.** O UNSW-NB15 foi obtido via Kaggle, utilizando diretamente os arquivos oficiais de treino e teste gerados pelos criadores do dataset. Os rótulos originais 0/1 foram mapeados para Normal/Attack. A coluna id (índice sequencial) foi descartada explicitamente como metadado. O holdout (175.341 amostras) é maior que o treino (82.332 amostras), o que reflete o split oficial dos criadores, amplamente adotado na literatura comparável, incluindo Mohale e Obagbuwa (2025).

### 4.3 Configuração da arquitetura GKS

**Gatekeeper:** classificador de árvore de decisão podada, treinado com 12 atributos selecionados automaticamente por importância a partir do CSV de treino.

**Especialistas:** para cada classe presente no treino, o pipeline busca o melhor par (modelo, conjunto de features) entre cinco famílias — LightGBM, XGBoost, CatBoost, Histogram Gradient Boosting e Random Forest — e dois conjuntos de 20 features candidatas. O critério de seleção é o F1 por classe (F1_k) no conjunto de validação interno (20% do treino, TRAIN_SEED=42), com desempate por latência de inferência.

Seeds: treino com TRAIN_SEED=42, holdout com EVAL_SEED=123.

Tabela 2 – Especialistas selecionados por classe, CIC-IDS2018

|            |                        |                              |
|:-----------|:-----------------------|:----------------------------:|
| **Classe** | **Modelo selecionado** | **F1_k (validação interna)** |
| Benign     | Random Forest          |            0,999             |
| Bot        | XGBoost                |            1,000             |
| BruteForce | XGBoost                |            0,738             |
| DDoS       | XGBoost                |            1,000             |
| DoS        | Histogram GBT          |            0,875             |
| Others     | CatBoost               |            1,000             |
| Web        | Random Forest          |            0,901             |

*Fonte: elaborado pelo autor (2026).*

Para o UNSW, XGBoost foi selecionado para ambas as classes (F1_k: Attack=0,968, Normal=0,960).

### 4.4 Baseline

O baseline monolítico adota um classificador XGBoost global treinado sobre train_cic_robust.csv (sem dst_port) e avaliado em cic_eval_robust.csv. A formulação é binária estrita — Benign vs. Attack — sem distinção entre tipos de ataque. A comparação entre o GKS e o baseline é deliberadamente assimétrica em formulação: o GKS avalia 7 classes granulares enquanto o baseline avalia 2. Essa assimetria é intencional e metodologicamente relevante — ela expressa exatamente o trade-off central do artigo: granularidade de decisão versus desempenho agregado.

### 4.5 Métricas e protocolo de avaliação

As métricas reportadas são: F1-macro, acurácia global, precision e recall por classe, matriz de confusão absoluta e latência média por estágio. O F1-macro é a métrica principal de comparação por ser invariante ao desbalanceamento de classes. A latência é medida em milissegundos por amostra, com separação entre o tempo do gatekeeper (estágio 1) e o tempo do especialista (estágio 2).
