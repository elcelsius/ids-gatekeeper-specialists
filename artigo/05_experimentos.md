# 05 Experimentos

## 5.1 Delineamento experimental

O delineamento experimental deste artigo foi estruturado para avaliar, de forma reprodutível, a arquitetura GKS (*Gatekeeper + Specialists*) em três leituras complementares do problema: um cenário principal multiclasse no CIC-IDS2018, um cenário secundário binário no UNSW-NB15 e um baseline XGBoost monolítico binário no recorte robusto do CIC. Os scripts e configurações do pipeline são versionados no repositório; os valores reportados nesta seção foram verificados diretamente nos artefatos atuais de `data/`, `outputs/` e `reports/`, evitando o uso de números externos ao snapshot experimental disponível.

O cenário principal utiliza o dataset **CIC-IDS2018**, com rótulos agregados em sete classes: Benign, Bot, BruteForce, DDoS, DoS, Others e Web. O cenário secundário utiliza o **UNSW-NB15** em formulação binária estrita (Normal vs. Attack), com função de verificação de consistência externa. Para o CIC, um baseline monolítico XGBoost é incluído como referência comparativa.

## 5.2 Datasets e preparação

### CIC-IDS2018

O dataset CIC-IDS2018 é composto por dez arquivos CSV diários, totalizando aproximadamente 6,5 GB de tráfego de rede capturado em condições controladas. Os arquivos cobrem datas entre fevereiro e março de 2018, com tipos de ataque variados por dia. O download foi realizado via Kaggle (`solarmainframe/ids-intrusion-csv`).

A preparação adotou uma estratégia de coleta proporcional por arquivo, coletando até 30.000 linhas de cada CSV bruto para o conjunto de treino e as 10.000 linhas subsequentes (offset disjunto) para o holdout de avaliação. Essa abordagem garante representação de todas as datas e tipos de ataque, evitando dominância de um único arquivo. Os seguintes tratamentos foram aplicados:

- normalização de nomes de colunas para *snake_case*;
- descarte de colunas de metadados de identificação (`flow_id`, `src_ip`, `dst_ip`, `src_port`);
- conversão forçada para tipo numérico com `pd.to_numeric(errors='coerce')`, substituindo `Infinity` por 0 via `fillna(0)`;
- remoção de colunas 100% nulas (`dropna(axis=1, how='all')`);
- alinhamento de colunas por interseção entre arquivos antes da concatenação.

O arquivo `03-01-2018.csv` foi descartado automaticamente por não apresentar colunas numéricas válidas (cabeçalho duplicado no meio do arquivo). Os conjuntos resultantes são:

| Arquivo | Linhas | Features | Classes presentes |
|---|---|---|---|
| `train_cic.csv` | 300.000 | 78 | Benign, Bot, BruteForce, DDoS, DoS, Others, Web |
| `cic_eval.csv` | 100.000 | 78 | Benign, Bot, BruteForce, DDoS, DoS, Others |
| `train_cic_robust.csv` | 300.000 | 77 | idem (sem `dst_port`) |
| `cic_eval_robust.csv` | 100.000 | 77 | idem (sem `dst_port`) |

A variante *robust* remove a coluna `dst_port`, utilizada exclusivamente no baseline XGBoost para evitar viés de porta de destino na comparação.

No snapshot atual, a distribuição observada em `train_cic.csv` é: 124.000 amostras `Benign`, 59.747 `DoS`, 57.726 `DDoS`, 29.899 `BruteForce`, 27.696 `Bot`, 928 `Web` e 4 `Others`. No holdout `cic_eval.csv`, a distribuição observada é: 46.983 `Benign`, 19.999 `DDoS`, 19.112 `DoS`, 9.998 `BruteForce`, 3.907 `Bot` e 1 `Others`.

A ausência da classe Web no holdout de avaliação é consequência direta da distribuição temporal do dataset: as 928 amostras de Web no treino concentram-se nos dias 22 e 23 de fevereiro, e o offset de 30.000 linhas não capturou amostras adicionais dessa classe. Essa limitação é declarada explicitamente como restrição do protocolo adotado.

### UNSW-NB15

O UNSW-NB15 foi obtido via Kaggle (`mrwellsdavid/unsw-nb15`). O dataset disponibiliza arquivos oficiais de treino e teste gerados pelos criadores, que foram utilizados diretamente sem reamostragem adicional. O arquivo `UNSW_NB15_training-set.csv` serviu como base de treino e o `UNSW_NB15_testing-set.csv` como holdout. Os rótulos originais `0/1` foram mapeados para `Normal`/`Attack`. A coluna `id` (índice sequencial) foi descartada explicitamente como metadado.

| Arquivo | Linhas | Features | Distribuição |
|---|---|---|---|
| `train_unsw.csv` | 82.332 | 40 | Attack: 45.332 (55%) / Normal: 37.000 (45%) |
| `unsw_eval.csv` | 175.341 | 40 | Attack: 119.341 (68%) / Normal: 56.000 (32%) |

O split invertido (holdout maior que treino) é o split oficial do dataset e amplamente adotado na literatura comparável, incluindo Mohale e Obagbuwa (2025), o que facilita comparação direta com trabalhos relacionados.

## 5.3 Configuração da arquitetura GKS

A arquitetura foi configurada de forma idêntica para os dois datasets, respeitando a lógica de seleção automática de especialistas implementada no projeto:

**Gatekeeper:** classificador de árvore de decisão podada (`DecisionTreeClassifier`), treinado com 12 atributos selecionados automaticamente por importância a partir do CSV de treino (`make_gatekeeper_cols_from_csv.py`). O gatekeeper produz a decisão de roteamento que determina qual especialista será acionado para cada amostra.

**Especialistas:** para cada classe presente no treino, o pipeline busca o melhor par (modelo, conjunto de features) entre cinco famílias de classificadores — LightGBM, XGBoost, CatBoost, Histogram Gradient Boosting e Random Forest — e dois conjuntos de 20 features candidatas gerados via `make_feature_pool_min.py`. O critério de seleção é o F1 por classe (F1_k) no conjunto de validação interno (20% do treino, `TRAIN_SEED=42`), com desempate por latência de inferência.

**Seeds:** treino com `TRAIN_SEED=42`, holdout com `EVAL_SEED=123`.

Os especialistas selecionados para o CIC foram:

| Classe | Modelo selecionado | F1_k (validação interna) |
|---|---|---|
| Benign | Random Forest | 0.999 |
| Bot | XGBoost | 1.000 |
| BruteForce | XGBoost | 0.738 |
| DDoS | XGBoost | 1.000 |
| DoS | Histogram GBT | 0.875 |
| Others | CatBoost | 1.000 |
| Web | Random Forest | 0.901 |

Para o UNSW, XGBoost foi selecionado para ambas as classes (F1_k: Attack=0.968, Normal=0.960).

## 5.4 Baseline

O baseline monolítico adota um classificador XGBoost global treinado sobre `train_cic_robust.csv` (sem `dst_port`) e avaliado em `cic_eval_robust.csv`. A formulação é binária estrita — Benign vs. Attack — sem distinção entre tipos de ataque. Essa configuração representa o modelo de referência mais direto: um classificador único que trata o problema como separação benigno/malicioso, sem qualquer decomposição hierárquica.

A comparação entre o GKS e o baseline é deliberadamente assimétrica em formulação: o GKS avalia 7 classes granulares enquanto o baseline avalia 2. Essa assimetria é intencional e metodologicamente relevante — ela expressa exatamente o trade-off central do artigo: granularidade de decisão versus desempenho agregado.

## 5.5 Métricas e protocolo de avaliação

As métricas reportadas são: F1-macro, acurácia global, precision e recall por classe, matriz de confusão absoluta e latência média por estágio. O F1-macro é a métrica principal de comparação por ser invariante ao desbalanceamento de classes. A latência é medida em milissegundos por amostra, com separação entre o tempo do gatekeeper (estágio 1) e o tempo do especialista (estágio 2).

Todos os artefatos de avaliação usados neste artigo — predições, relatórios por classe e figuras — foram gerados automaticamente pelos CLIs `cli_eval_twostage` e `cli_plot_eval` e persistidos em `outputs/` e `reports/`. O repositório também contém artefatos de XAI para um snapshot binário legado do CIC (`Benign` vs. `Others`), mas eles não são utilizados como evidência central do cenário multiclasse desta campanha.
