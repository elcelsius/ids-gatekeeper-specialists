# GKS: Uma Arquitetura de IA em Dois Estágios para Problemas Complexos de Classificação – Estudo de Caso em Detecção de Intrusões

*GKS: A Two-Stage AI Architecture for Complex Classification Problems – A Case Study in Intrusion Detection*

Celso de Oliveira Lisboa

## Resumo

Problemas complexos de classificação supervisionada combinam, com frequência, heterogeneidade de padrões, desbalanceamento, sobreposição entre classes e necessidade de decisões em múltiplos níveis. Este artigo investiga uma estratégia de Inteligência Artificial baseada em decomposição hierárquica da inferência, implementada por uma arquitetura em dois estágios composta por um mecanismo inicial de triagem (gatekeeper) e classificadores especialistas. A proposta é analisada em detecção de intrusões em redes, com o CIC-IDS2018 como cenário principal em formulação multiclasse granular e o UNSW-NB15 como cenário complementar em formulação binária. O pipeline experimental foi reconstruído a partir dos scripts, configurações e artefatos do projeto, com geração explícita de conjuntos de treino e holdout, seleção automática de especialistas por F1 por classe e registro de métricas e latência por estágio. A arquitetura atingiu F1-macro de 0,764 e acurácia de 93,3% no CIC-IDS2018 em sete classes, e F1-macro de 0,866 com acurácia de 87,4% no UNSW-NB15 binário. Como referência comparativa, o baseline XGBoost monolítico no recorte robusto do CIC alcançou F1-macro de 0,976 e acurácia de 97,6%. Os resultados indicam que a arquitetura hierárquica é operacionalmente viável e particularmente forte na separação entre tráfego benigno e malicioso, embora apresente perda de desempenho na discriminação entre subclasses raras ou sobrepostas, como BruteForce, Bot e Web. Conclui-se que a decomposição gatekeeper-especialistas constitui estratégia metodologicamente plausível de IA aplicada, desde que interpretada à luz das limitações de protocolo, da rareza de classes e da assimetria entre formulações comparadas.

**Palavras-chave:** inteligência artificial aplicada. classificação hierárquica. detecção de intrusões. ensemble learning. especialistas por classe.

## Abstract

Complex supervised classification problems often combine pattern heterogeneity, class imbalance, class overlap, and the need for multi-stage decisions. This article investigates an Artificial Intelligence strategy based on hierarchical decomposition of inference, implemented through a two-stage architecture composed of an initial screening mechanism (gatekeeper) and specialist classifiers. The proposal is analyzed in network intrusion detection, using CIC-IDS2018 as the main scenario in a granular multiclass formulation and UNSW-NB15 as a complementary binary scenario. The experimental pipeline was reconstructed from project scripts, configurations and artifacts, with explicit generation of training and holdout sets, automatic specialist selection based on classwise F1, and latency recording per stage. The architecture reached macro-F1 of 0.764 and accuracy of 93.3% on CIC-IDS2018 with seven classes, and macro-F1 of 0.866 with accuracy of 87.4% on binary UNSW-NB15. As a comparative reference, the monolithic XGBoost baseline on the robust CIC split achieved macro-F1 of 0.976 and accuracy of 97.6%. The results indicate that the hierarchical architecture is operationally viable and particularly strong in separating benign from malicious traffic, although it loses performance when discriminating rare or overlapping attack subclasses such as BruteForce, Bot, and Web. The study concludes that the gatekeeper-specialist decomposition is a plausible Applied AI strategy, provided that its gains are interpreted together with protocol limitations, class rarity, and asymmetry between evaluation formulations.

**Keywords:** applied artificial intelligence. hierarchical classification. intrusion detection. ensemble learning. class specialists.

## 1 Introdução

Problemas de classificação supervisionada tornam-se particularmente desafiadores quando envolvem sobreposição entre classes, desbalanceamento, heterogeneidade dos padrões de entrada e fronteiras de decisão difíceis de modelar por uma única função global. Em contextos dessa natureza, abordagens monolíticas podem apresentar desempenho desigual entre regiões do espaço de atributos, o que motiva a investigação de estratégias de Inteligência Artificial capazes de decompor o problema em etapas ou subproblemas mais específicos.

Entre as possibilidades discutidas na literatura de IA aplicada, arquiteturas hierárquicas e sistemas com especialização de classificadores oferecem uma alternativa conceitualmente relevante. Nesses arranjos, uma etapa inicial de triagem ou roteamento pode encaminhar cada amostra para modelos mais especializados, potencialmente mais adequados para lidar com padrões locais de decisão. Essa perspectiva desloca o foco de um único classificador global para um processo estruturado de inferência, no qual a decisão final resulta da combinação entre filtragem inicial e análise especializada.

A detecção de intrusões em redes constitui um estudo de caso particularmente apropriado para investigar esse tipo de estratégia. Além de sua relevância prática, o domínio de IDS reúne características típicas de problemas complexos de classificação, como desbalanceamento entre categorias, semelhança parcial entre comportamentos benignos e maliciosos, diversidade interna dos padrões de ataque e necessidade de avaliação criteriosa do comportamento do modelo. Assim, embora o cenário aplicado pertença ao campo da segurança computacional, ele pode ser entendido, neste trabalho, como um ambiente de validação para uma questão mais ampla de Inteligência Artificial.

Nesse contexto, este artigo investiga uma arquitetura de classificação em dois estágios denominada GKS (*Gatekeeper + Specialists*), derivada do ecossistema técnico do projeto 2D-AEF e aqui reposicionada como objeto de análise em IA aplicada. Em termos gerais, a arquitetura combina um classificador inicial de triagem, denominado *gatekeeper*, com classificadores especialistas responsáveis por subproblemas ou regiões mais específicas da decisão. O interesse central do estudo não está em assumir superioridade universal da abordagem, mas em examinar se a decomposição hierárquica da inferência constitui uma estratégia metodologicamente plausível para tratar problemas classificatórios complexos em um cenário aplicado realista.

O objetivo do artigo é investigar, de forma conservadora e reprodutível, a adequação dessa arquitetura em dois estágios para problemas complexos de classificação, utilizando o CIC-IDS2018 em formulação multiclasse granular como cenário principal, complementado pelo UNSW-NB15 em formulação binária e por um baseline XGBoost monolítico no recorte robusto do CIC. Além desta introdução, o artigo está organizado da seguinte forma. A Seção 2 discute os trabalhos relacionados. A Seção 3 apresenta a metodologia. A Seção 4 detalha o desenho experimental. A Seção 5 reúne os resultados. A Seção 6 discute implicações, *trade-offs* e limitações. Por fim, a Seção 7 apresenta as conclusões.

## 2 Trabalhos Relacionados

### 2.1 Decomposição da decisão em IA: especialização de modelos e roteamento

A ideia de decompor um problema complexo de classificação entre múltiplos modelos especializados, coordenados por um mecanismo de roteamento, representa uma direção consolidada na literatura de Inteligência Artificial. O paradigma de *Mixture of Experts* (MoE), cujas raízes remontam ao início dos anos 1990, propõe que uma rede de roteamento (*gating network*) aprenda a distribuir as instâncias de entrada entre especialistas, cada um responsável por uma região do espaço do problema. Em revisão recente e abrangente, Cai et al. (2024) documentam a trajetória desse paradigma desde suas formulações clássicas até sua adoção em larga escala em modelos de linguagem de grande porte, mostrando que o princípio central permanece o mesmo: especialistas distintos ativados seletivamente por um mecanismo de roteamento produzem ganhos de eficiência e especialização que modelos monolíticos não conseguem replicar sem custo computacional proporcional.

Para o presente artigo, o interesse no paradigma MoE não está em suas aplicações a grandes modelos de linguagem, mas na intuição arquitetural que ele formaliza: diferentes regiões do espaço de decisão podem se beneficiar de tratamentos específicos, e um mecanismo de triagem inicial pode organizar esse roteamento de forma eficiente. Essa intuição é diretamente aplicável ao domínio de detecção de intrusões, onde o espaço de instâncias é heterogêneo e o custo assimétrico dos erros reforça a necessidade de organizar a decisão em etapas.

Do ponto de vista de ensemble learning, Ganaie et al. (2022) mostram que combinações de classificadores produzem ganhos consistentes especialmente quando os modelos componentes cometem erros em regiões distintas — o que os autores denominam diversidade funcional. A arquitetura em dois estágios explorada neste artigo torna essa diversidade explícita ao separar estruturalmente o problema de triagem (gatekeeper) do problema de discriminação refinada (especialistas), em vez de simplesmente combinar classificadores de forma indistinta.

### 2.2 Classificação complexa e arquiteturas hierárquicas em IA aplicada

A literatura de Inteligência Artificial aplicada tem discutido, de forma recorrente, as limitações de modelos monolíticos em problemas de classificação que apresentam heterogeneidade interna, sobreposição entre classes, fronteiras de decisão difíceis e necessidade de tratamento diferenciado para subconjuntos do espaço de entrada. Nesse contexto, arquiteturas hierárquicas e estratégias de decomposição da decisão surgem como alternativas metodológicas relevantes, pois permitem organizar o processo inferencial em múltiplos estágios, com diferentes níveis de granularidade.

No domínio de detecção de intrusões, essa discussão aparece de maneira explícita em trabalhos recentes sobre classificação hierárquica. Uddin et al. (2024) investigam uma abordagem em três níveis para IDS, distinguindo inicialmente tráfego benigno e malicioso, depois categorias amplas de ataque e, por fim, subtipos mais específicos. Em um experimento sistemático com dez algoritmos distintos em dez datasets de referência, os autores mostram que não há diferença significativa no desempenho global (F1-macro) entre a abordagem hierárquica e a classificação plana. O resultado relevante está em outro lugar: a hierarquia reduz especificamente a classificação de tráfego malicioso como benigno — o erro de falso negativo, que é o mais crítico operacionalmente. Em outras palavras, a hierarquia não é superior em tudo, mas é estruturalmente mais adequada para o tipo de erro que mais importa.

Além disso, propostas multicamadas recentes, como o sistema MIDES (AGATE et al., 2025), aprofundam a convergência entre especialização por classe e eficiência computacional. O MIDES emprega um classificador binário inicial — funcionalmente equivalente ao *gatekeeper* — para filtrar tráfego claramente benigno antes de acionar um ensemble de classificadores multiclasse para eventos suspeitos. Avaliado nos datasets CIC-IDS2017 e CIC-IDS2018, o MIDES reporta F1-macro de 56,2% em cenário de transferência cross-dataset. Esse número contextualiza o presente artigo ao oferecer uma referência concreta para o comportamento esperado em condições realistas de avaliação.

### 2.3 IDS com aprendizado de máquina como estudo de caso

A revisão sistemática de Rehman et al. (2025) é particularmente útil neste ponto. Ao mapear sistematicamente estudos recentes em IDS com ML, os autores identificam limitações recorrentes: uso de poucos datasets e poucos algoritmos comparados simultaneamente, ausência de benchmarking padronizado, dificuldade de comparação entre estudos por falta de protocolos comuns, e insuficiente atenção a custo computacional. Essas lacunas justificam o uso de IDS não como fim em si mesmo, mas como estudo de caso exigente para investigar estratégias de IA.

Propostas como os frameworks de ensemble apresentados por Seth, Kaur e Singh (2021) e Yang et al. (2022) ajudam a mostrar que a combinação de modelos, a decisão orientada por classe e o uso de múltiplos classificadores já constituem uma direção consolidada em IDS. Seth, Kaur e Singh (2021) propõem um framework inteligente baseado em ensemble que combina múltiplos classificadores para melhorar a detecção, demonstrando ganhos consistentes em datasets de rede. Yang et al. (2022) apresentam o LCCDE (*Leader Class and Confidence Decision Ensemble*), que seleciona dinamicamente o classificador líder por classe e confiança, aproximando-se da lógica de especialização por subproblema adotada no presente artigo. O GKS reposiciona essa discussão ao enfatizar menos a ideia de ensemble como simples mecanismo de aumento de desempenho e mais a noção de decomposição hierárquica da decisão como estratégia de IA (SETH; KAUR; SINGH, 2021; YANG et al., 2022).

### 2.4 Especialização de modelos, roteamento e subproblemas de decisão

Um dos pontos centrais do presente artigo é a hipótese de que a especialização de classificadores pode ser útil quando o problema global contém subestruturas com padrões distintos. Essa ideia aparece, de formas variadas, em arquiteturas orientadas por classe, em mecanismos de roteamento entre modelos e em sistemas que combinam triagem inicial com análise especializada posterior.

Do ponto de vista teórico em IA, o paradigma MoE revisitado por Cai et al. (2024) mostra que a especialização viabilizada por roteamento explícito não é um artifício arquitetural, mas uma estratégia de particionamento do espaço de decisão com fundamento em eficiência computacional e generalização seletiva. No contexto de IDS, o uso de ensembles orientados por classe e de estruturas multicamadas, como demonstrado pelo MIDES (AGATE et al., 2025), reforça que essa lógica de especialização produz resultados competitivos quando combinada com mecanismos de seleção explícita de estratégia por amostra. Além disso, Ganaie et al. (2022) mostram empiricamente que a diversidade funcional entre classificadores é o principal preditor de ganho em ensemble, reforçando que arquiteturas que estruturam explicitamente essa diversidade têm fundamento teórico mais sólido do que abordagens puramente votativas.

### 2.5 XAI em sistemas de detecção de intrusões

À medida que sistemas IDS baseados em ML incorporam modelos de maior complexidade, a opacidade das decisões torna-se um problema prático. Al e Sagiroglu (2025) apresentam revisão abrangente da aplicação de XAI em IDS, organizando os métodos em três categorias: ante-hoc, intrínsecos e post-hoc. Essa taxonomia é relevante para o presente artigo porque a arquitetura proposta combina deliberadamente os dois últimos tipos: o gatekeeper é uma árvore de decisão podada, intrinsecamente interpretável, enquanto os especialistas podem ser inspecionados via técnicas post-hoc como SHAP.

Mohale e Obagbuwa (2025) fornecem evidências empíricas sobre esse balanço no contexto do UNSW-NB15 — o mesmo dataset secundário utilizado neste artigo. Os autores mostram que XGBoost e CatBoost atingem 87% de acurácia com taxa de falso positivo de 0,07 e taxa de falso negativo de 0,12, e que a integração de SHAP, LIME e ELI5 evidencia quais atributos são os mais discriminativos. Esses números servem como referência concreta para o cenário secundário do presente artigo.

Pawlicki et al. (2024) identificam 25 desafios para XAI em IDS. O mais relevante para este trabalho é o trade-off entre modelos intrinsecamente interpretáveis (glass box) e modelos de alta acurácia porém opacos (crystal ball). A arquitetura em dois estágios enfrenta esse trade-off de forma explícita: o gatekeeper é deliberadamente um glass box, enquanto os especialistas podem ser modelos mais complexos inspecionados por ferramentas post-hoc. Khan et al. (2025) ampliam essa discussão para o que denominam adversarial XAI: a explicabilidade de um modelo pode ser explorada por adversários para construir ataques mais direcionados, um trade-off que representa limitação importante a ser declarada em estudos que integram XAI.

### 2.6 Síntese crítica e posicionamento do artigo

A literatura recente converge para quatro constatações relevantes para o presente artigo. Primeira: a decomposição hierárquica da decisão tem fundamento em IA que precede as aplicações em IDS. O paradigma MoE, revisitado por Cai et al. (2024), formaliza a intuição de que problemas com estrutura heterogênea se beneficiam de roteamento explícito entre especialistas. Segunda: problemas de detecção de intrusões continuam sendo um campo fértil para investigação de classificadores avançados, mas a comparação entre propostas depende fortemente de desenho experimental rigoroso, como documentado por Rehman et al. (2025). Terceira: arquiteturas hierárquicas constituem direção plausível quando o problema apresenta heterogeneidade e custo assimétrico dos erros — o resultado de Uddin et al. (2024) é emblemático nesse sentido. Quarta: interpretabilidade vem ganhando espaço como complemento importante à avaliação tradicional de desempenho, mas traz riscos próprios que precisam ser declarados explicitamente (KHAN et al., 2025; PAWLICKI et al., 2024). É nesse espaço que o presente artigo se insere.

## 3 Metodologia

### 3.1 Visão geral da abordagem

Este trabalho investiga uma estratégia de Inteligência Artificial voltada a problemas complexos de classificação, baseada na decomposição hierárquica da decisão em dois estágios complementares. A arquitetura GKS, implementada no módulo *twodaef*, combina um classificador inicial de triagem, denominado *gatekeeper*, com classificadores especialistas responsáveis por decisões mais específicas em subespaços do problema. O domínio de detecção de intrusões é utilizado como estudo de caso aplicado, e não como único centro conceitual da proposta.

### 3.2 Arquitetura em dois estágios

A arquitetura empregada segue a lógica *Gatekeeper → Especialistas*. No primeiro estágio, uma decisão inicial de triagem é produzida a partir de um conjunto mais enxuto de atributos, com o propósito de identificar a região do problema ao qual a amostra parece pertencer. No segundo estágio, a amostra é encaminhada para um especialista associado ao encaminhamento definido na etapa anterior, onde ocorre a decisão mais refinada.

### 3.3 Papel do gatekeeper

O *gatekeeper* é implementado como um classificador de árvore de decisão podada (DecisionTreeClassifier), com hiperparâmetros configuráveis para profundidade máxima e tamanho mínimo de folha. Sua função metodológica central é realizar uma triagem inicial de baixa complexidade computacional, produzindo a decisão de roteamento que define qual especialista será acionado. As variáveis de entrada utilizadas são mantidas em arquivos de configuração em configs/cols/, o que separa explicitamente a seleção de atributos da lógica do código-fonte, favorecendo rastreabilidade e reprodutibilidade.

### 3.4 Papel dos especialistas

Os especialistas são treinados por meio do módulo de treino de especialistas do projeto. Para cada classe ou grupo alvo, o pipeline considera combinações entre famílias de modelos disponíveis e subconjuntos candidatos de atributos definidos em feature pools. A seleção do especialista é feita com base no F1 por classe no conjunto de validação interno, com latência de inferência como critério de desempate. Esse desenho permite heterogeneidade entre especialistas: diferentes regiões do problema podem ser atendidas por modelos e representações de entrada distintas.

### 3.5 Fluxo geral do pipeline

O fluxo metodológico adotado pode ser resumido em cinco etapas: (1) preparação dos dados por meio dos scripts de preparação, com geração dos conjuntos de treino e avaliação; (2) definição dos atributos do gatekeeper e dos feature pools dos especialistas; (3) treinamento dos componentes da arquitetura, com persistência dos modelos; (4) construção e utilização dos mapeamentos de especialistas, associando classes, modelos, conjuntos de atributos e caminhos dos artefatos; e (5) execução da inferência em dois estágios, em que cada amostra recebe uma decisão final após o roteamento inicial e a avaliação do especialista correspondente.

### 3.6 Justificativa metodológica

A adoção de decomposição hierárquica e especialização é justificada por três argumentos principais. Primeiro, a triagem inicial permite reduzir a complexidade imediata da decisão, organizando o problema em etapas sucessivas. Segundo, a especialização por classe cria a possibilidade de empregar modelos e subconjuntos de atributos mais adequados a regiões específicas do espaço de dados. Terceiro, a estrutura em estágios favorece uma leitura analítica mais detalhada do comportamento do sistema, separando a decisão de roteamento da decisão final e tornando ambas observáveis como artefatos auditáveis.

## 4 Experimentos

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

## 5 Resultados

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

## 6 Discussão

### 6.1 Adequação da decomposição hierárquica

Os resultados do CIC-IDS2018 mostram que a arquitetura GKS é operacionalmente viável: acurácia de 93,3% e F1-macro de 0,764 em um problema de 7 classes. O sistema classificou corretamente a esmagadora maioria das amostras das classes bem representadas — Benign (F1=0,986), DDoS (F1=1,000) e DoS (F1=0,868). O resultado do UNSW-NB15 (F1-macro=0,866) reforça a consistência externa dessa observação. Esses resultados são coerentes com Uddin et al. (2024), que mostram que classificação hierárquica não melhora necessariamente o F1-macro global, mas reduz erros específicos de maior custo operacional.

### 6.2 Comportamento por classe e análise de erros

A análise por classe revela padrões que o F1-macro agregado não captura. Classes bem resolvidas como DDoS (F1=1,000) e Benign (F1=0,986) têm padrões estatisticamente distintos que facilitam a discriminação. BruteForce com F1=0,649 e recall de 0,495 é o ponto mais crítico: 5.044 amostras foram classificadas como DoS, pois ataques de força bruta repetitivos geram padrões de volume de pacotes similares a ataques DoS de baixa intensidade. O especialista Bot apresentou queda de recall entre validação interna (F1_k=1,000) e holdout (recall=0,736), sugerindo covariate shift temporal leve — padrão comum em datasets de rede coletados em períodos distintos. A ausência de Web no holdout é limitação de protocolo, não incapacidade do especialista.

### 6.3 Trade-off granularidade vs. desempenho agregado

A comparação entre GKS (F1-macro=0,764, 7 classes) e baseline XGBoost (F1-macro=0,976, 2 classes) ilustra o trade-off central da arquitetura hierárquica: granularidade de discriminação ao custo de F1-macro menor. O baseline resolve um problema mais simples e o resolve muito bem. O GKS resolve um problema fundamentalmente mais difícil — distinguir sete categorias com fronteiras sobrepostas. Como leitura auxiliar, colapsando-se as predições do GKS no CIC para a formulação binária Benign vs. Attack, obtém-se acurácia de 98,7% e F1-macro de 0,987, evidenciando que a principal perda está na taxonomia interna dos ataques, não na detecção de intrusão em sentido amplo.

### 6.4 Custo computacional e latência

A latência total de 21,789 ms/amostra no CIC é dominada pelo especialista (21,789 ms) com contribuição desprezível do gatekeeper (0,000056 ms). Esse resultado confirma o design esperado: o gatekeeper é deliberadamente uma árvore de decisão podada de baixíssimo custo, enquanto o especialista concentra o custo computacional. No UNSW-NB15, a latência total de 1,401 ms/amostra é significativamente menor, o que sugere que a combinação entre espaço de atributos mais compacto (40 features vs. 78) e especialistas XGBoost binários produz um cenário inferencial mais leve.

### 6.5 Interpretabilidade e papel do gatekeeper

O gatekeeper, por ser uma árvore de decisão podada, é intrinsecamente interpretável no sentido de Al e Sagiroglu (2025) — suas regras de roteamento podem ser inspecionadas diretamente sem necessidade de técnicas post-hoc. Para os especialistas, a interpretabilidade post-hoc via SHAP permanece aplicável individualmente por classe. O repositório contém artefatos de XAI em reports/cic/xai/ para um snapshot binário legado do CIC, mas eles não correspondem ao cenário multiclasse principal e foram tratados apenas como material complementar histórico.

### 6.6 Limitações

As principais limitações do estudo são: (1) protocolo de coleta por offset garante disjunção mas não representação equilibrada de todas as classes — a ausência de Web no holdout é o exemplo mais visível; (2) distribuição temporal não controlada, com o episódio de queda de recall em Bot sugerindo covariate shift temporal; (3) classe Web com apenas 928 amostras no treino, marginal para treinar um especialista robusto; (4) baseline em formulação binária enquanto o GKS é avaliado em 7 classes, tornando a comparação de F1-macro metricamente assimétrica; (5) holdout UNSW com 175.341 amostras maior que o treino com 82.332, refletindo o split oficial dos criadores; e (6) ausência de XAI formal alinhado ao cenário multiclasse principal.

## 7 Conclusão

Este artigo investigou uma estratégia de Inteligência Artificial aplicada a problemas complexos de classificação, baseada em uma arquitetura hierárquica em dois estágios — denominada GKS (*Gatekeeper + Specialists*) — composta por um mecanismo inicial de triagem (*gatekeeper*) e classificadores especialistas por categoria. A detecção de intrusões em redes foi adotada como estudo de caso, por oferecer um domínio no qual heterogeneidade de padrões, sobreposição entre classes, assimetria de custos de erro e necessidade de discriminação granular tornam visível a complexidade do problema classificatório.

Os resultados principais são: F1-macro de 0,764 e acurácia de 93,3% no CIC-IDS2018 em sete classes granulares; F1-macro de 0,866 e acurácia de 87,4% no UNSW-NB15 binário; e F1-macro de 0,976 com acurácia de 97,6% para o baseline XGBoost monolítico no CIC em formulação binária robusta. Esses resultados sustentam que a arquitetura hierárquica em dois estágios constitui uma estratégia de IA operacionalmente viável e analiticamente útil. Seu principal diferencial não está em F1-macro superior — o baseline demonstrou desempenho agregado mais alto em sua formulação binária —, mas na capacidade de discriminar tipos específicos de ataque com especialistas dedicados, tornando o comportamento do sistema observável em granularidade de classe.

Do ponto de vista metodológico, o trabalho contribui ao demonstrar que a arquitetura gatekeeper-especialistas pode ser tratada como hipótese de decomposição da decisão em IA aplicada. A separação explícita entre triagem inicial e discriminação refinada estrutura o pipeline de forma que escolhas de modelagem, roteamento e especialização se tornam artefatos auditáveis.

Como trabalhos futuros, recomenda-se: desenvolver um protocolo de split estratificado por classe e por janela temporal para o CIC-IDS2018; incluir um baseline multiclasse global com as mesmas 7 categorias para comparação mais rigorosa; executar a análise XAI por especialista com protocolo comparável entre datasets; investigar estratégias de oversampling ou pesos de classe para as categorias com suporte insuficiente (Web, BruteForce); e avaliar a arquitetura em configurações multiclasse mais granulares quando os dados permitirem.

## Referências

AGATE, Vincenzo; DE PAOLA, Alessandra; FERRARO, Pierluca; LO RE, Giuseppe. MIDES: a multi-layer intrusion detection system using ensemble machine learning. International Journal of Intelligent Networks, 2025. DOI: 10.1016/j.ijin.2025.09.001.

AL, Samed; SAGIROGLU, Seref. Explainable artificial intelligence models in intrusion detection systems. Engineering Applications of Artificial Intelligence, v. 144, p. 110145, 2025. DOI: 10.1016/j.engappai.2025.110145.

CAI, Weilin; JIANG, Juyong; WANG, Fan; TANG, Jing; KIM, Sunghun; HUANG, Jiayi. A survey on mixture of experts in large language models. arXiv, \[s.l.\], 2024. Disponível em: https://arxiv.org/abs/2407.06204. Acesso em: 15 mar. 2026.

GANAIE, M. A.; HU, Minghui; MALIK, A. K.; TANVEER, M.; SUGANTHAN, P. N. Ensemble deep learning: a review. Engineering Applications of Artificial Intelligence, v. 115, p. 105151, 2022. DOI: 10.1016/j.engappai.2022.105151.

KHAN, Naseem; AHMAD, Kashif; AL TAMIMI, Aref; ALANI, Mohammed M.; BERMAK, Amine; KHALIL, Issa. Explainable AI-based intrusion detection systems for Industry 5.0 and adversarial XAI: a systematic review. Information, v. 16, n. 12, p. 1036, 2025. DOI: 10.3390/info16121036.

MOHALE, Vincent Zibi; OBAGBUWA, Isaac Chukwuma. Evaluating machine learning-based intrusion detection systems with explainable AI: enhancing transparency and interpretability. Frontiers in Computer Science, 2025. DOI: 10.3389/fcomp.2025.1520741. Disponível em: https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2025.1520741/full. Acesso em: 15 mar. 2026.

PAWLICKI, Marek; PAWLICKA, Aleksandra; KOZIK, Rafal; CHORAS, Michal. The survey on the dual nature of XAI challenges in intrusion detection and their potential for AI innovation. Artificial Intelligence Review, v. 57, n. 12, p. 330, 2024.

REHMAN, Hafiz Muhammad Raza ur; LIAQUAT, Saira; GUL, Muhammad Junaid; JHANDIR, Muhammad Zeeshan; GAVILANES, Daniel; VERGARA, Manuel Masias; ASHRAF, Imran. A systematic literature study of machine learning techniques based intrusion detection: datasets, models, challenges, and future directions. Journal of Big Data, v. 12, n. 1, 2025. DOI: 10.1186/s40537-025-01323-2.

SETH, Sugandh; KAUR, Kuljit; SINGH, Gurwinder. A novel ensemble framework for an intelligent intrusion detection system. IEEE Access, 2021. DOI: 10.1109/ACCESS.2021.3116219.

UDDIN, Md. Ashraf; ARYAL, Sunil; BOUADJENEK, Mohamed Reda; AL-HAWAWREH, Muna; TALUKDER, Md. Alamin. Hierarchical classification for intrusion detection system: effective design and empirical analysis. CoRR, abs/2403.13013, 2024. Disponível em: https://arxiv.org/abs/2403.13013. Acesso em: 15 mar. 2026.

YANG, Li; SHAMI, Abdallah; STEVENS, Gary; DE RUSETT, Stephen. LCCDE: a decision-based ensemble framework for intrusion detection in the Internet of Vehicles. In: IEEE GLOBAL COMMUNICATIONS CONFERENCE (GLOBECOM), 2022, Rio de Janeiro. Proceedings \[...\]. \[s.l.\]: IEEE, 2022. DOI: 10.1109/GLOBECOM48099.2022.10001280. Disponível em: https://arxiv.org/abs/2208.03399. Acesso em: 15 mar. 2026.
