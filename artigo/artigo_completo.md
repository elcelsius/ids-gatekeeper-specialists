# Detecção de Intrusões com Arquitetura em Dois Estágios: Gatekeeper e Especialistas por Classe em Cenário Binário

## Resumo

A detecção de intrusões em redes permanece como desafio relevante para a segurança cibernética, especialmente em cenários com heterogeneidade de tráfego, sobreposição entre padrões benignos e maliciosos e custo elevado de erros de detecção. Neste contexto, este artigo, desenvolvido no âmbito da disciplina de Inteligência Artificial e derivado do ecossistema técnico do 2D-AEF, teve como objetivo avaliar, de forma conservadora e reprodutível, a adequação de uma arquitetura de classificação em dois estágios, composta por um gatekeeper de triagem inicial e especialistas por classe. A abordagem foi descrita e analisada com base em pipeline versionado de preparação de dados, seleção de atributos, treinamento, inferência e avaliação, com foco no recorte binário de IDS. O contexto experimental considerou principalmente o CIC-IDS2018, com cenário complementar no UNSW-NB15, utilizando artefatos e relatórios disponíveis em `reports/` e `docs/`. Os resultados agregados e os materiais gráficos existentes indicam viabilidade operacional da estratégia hierárquica no escopo estudado, além de evidências complementares de interpretabilidade por meio de artefatos XAI no cenário CIC. Entretanto, a leitura dos achados é condicionada por limitações do material versionado, como ausência de parte dos artefatos estruturados por classe e coexistência de snapshots distintos em algumas execuções. Conclui-se que a arquitetura em dois estágios constitui uma alternativa metodologicamente plausível para IDS binário, desde que acompanhada por governança rigorosa de experimentos, padronização de relatórios e consolidação consistente de métricas.

## 1 Introdução

A segurança de redes permanece como um tema central para a operação de sistemas computacionais em organizações públicas e privadas. O aumento do volume de tráfego, a heterogeneidade de aplicações e a sofisticação de ameaças tornam a identificação de comportamentos maliciosos uma tarefa progressivamente mais complexa. Nesse contexto, Sistemas de Detecção de Intrusões (Intrusion Detection Systems, IDS) são amplamente utilizados como mecanismos de apoio à detecção precoce de ataques e ao processo de resposta a incidentes.

O uso de técnicas de Inteligência Artificial em IDS é motivado pela capacidade de modelar padrões em dados de tráfego e apoiar decisões em cenários com alta variabilidade. Em comparação com abordagens estritamente baseadas em assinaturas, métodos de aprendizado de máquina tendem a ampliar a cobertura de detecção para comportamentos não triviais e para variações de ataques já conhecidos. Entretanto, essa adoção exige cuidado metodológico, principalmente quanto à reprodutibilidade experimental, à interpretação dos modelos e à avaliação sob métricas adequadas ao domínio de segurança.

Do ponto de vista do problema de pesquisa, a literatura e a prática experimental em IDS indicam dificuldades recorrentes: desbalanceamento entre classes, sobreposição de padrões entre tráfego benigno e malicioso e custo operacional elevado de falsos negativos. Em cenários reais, deixar de detectar tráfego de ataque pode produzir impacto significativamente maior do que o aumento moderado de falsos positivos. Além disso, modelos globais únicos podem apresentar desempenho desigual entre classes, dificultando o equilíbrio entre qualidade preditiva e custo computacional.

Este artigo, derivado do ecossistema técnico do 2D-AEF e desenvolvido como trabalho próprio da disciplina de Inteligência Artificial, investiga uma alternativa arquitetural para esse problema: uma classificação em dois estágios, composta por um gatekeeper inicial e por classificadores especialistas por classe ou grupo de classes. Em alto nível, o gatekeeper realiza uma triagem inicial de baixo custo e encaminha cada amostra para o especialista correspondente, que opera com combinação específica de modelo e conjunto de atributos. A proposta busca organizar o processo de decisão de forma hierárquica, sem assumir, a priori, superioridade universal sobre abordagens mais simples.

O objetivo deste artigo é avaliar, com escopo conservador e protocolo reprodutível, a adequação dessa arquitetura de dois estágios para detecção de intrusões em formulação binária, com ênfase em métricas relevantes para IDS e em análise de custo de inferência. O estudo também considera comparações com baselines factíveis no projeto e inclui interpretação complementar por técnicas de explicabilidade, quando aplicável.

Além desta introdução, o texto está organizado da seguinte forma: a Seção 2 apresenta os trabalhos relacionados; a Seção 3 descreve a metodologia; a Seção 4 detalha o desenho experimental; a Seção 5 reúne os resultados; a Seção 6 discute implicações e limitações; e a Seção 7 apresenta as conclusões e possibilidades de continuidade do estudo.

## 2 Trabalhos Relacionados

### 2.1 IDS baseados em aprendizado de máquina

A literatura recente de detecção de intrusões com aprendizado de máquina mostra uma migração progressiva de abordagens estritamente assinadas para modelos orientados a dados, com ênfase em classificação supervisionada de tráfego de rede. No estudo *Evaluating machine learning-based intrusion detection systems with explainable AI: enhancing transparency and interpretability*, diferentes modelos de classificação são avaliados no UNSW-NB15, evidenciando a relevância de comparar algoritmos sob múltiplas métricas e não apenas por acurácia agregada. De modo complementar, o trabalho *Enhancing intrusion detection in wireless sensor networks using a Tabu search based optimized random forest* explora otimização de hiperparâmetros em Random Forest para cenários de WSN, reforçando que o desempenho de IDS depende de escolhas metodológicas de modelagem e ajuste, além da seleção do algoritmo base.

Em conjunto, esses estudos sustentam duas premissas importantes para este artigo: (i) IDS com ML devem ser avaliados com protocolo explícito e comparável; e (ii) desempenho preditivo e viabilidade operacional precisam ser tratados de forma integrada.

### 2.2 Ensembles, decisão em múltiplos estágios e estruturas hierárquicas

No eixo de ensembles, o artigo *A Novel Ensemble Framework for an Intelligent Intrusion Detection System* argumenta que um único classificador tende a ser insuficiente para capturar, com uniformidade, a diversidade de categorias de ataque. A estratégia proposta no trabalho combina classificadores a partir de sua capacidade de detecção por classe, aproximando-se da ideia de decisão especializada.

Na mesma direção, *LCCDE: A Decision-Based Ensemble Framework for Intrusion Detection in The Internet of Vehicles* formaliza um ensemble orientado por classe e por confiança de predição, no qual modelos líderes contribuem de maneira diferenciada para a decisão final. Embora aplicado ao contexto de Internet of Vehicles, esse desenho é conceitualmente relevante para arquiteturas hierárquicas em IDS, pois explicita a decomposição do problema em decisões parciais guiadas por especialização.

Essas contribuições dialogam com o recorte deste artigo ao indicar que estratégias de combinação e roteamento podem ser alternativas metodológicas plausíveis quando há heterogeneidade entre classes de intrusão.

### 2.3 Especialização por classe e seleção de atributos

A especialização por classe é frequentemente acompanhada por mecanismos de seleção de atributos, dado que diferentes ataques podem depender de subconjuntos distintos de variáveis. O trabalho *Bio-inspired Hybrid Feature Selection Model for Intrusion Detection* propõe uma estrutura em camadas para seleção de atributos com metaheurísticas (PSO, GWO e FFA), seguida por otimização adicional. Mesmo sem tratar diretamente de um gatekeeper de classificação, o estudo reforça a hipótese de que a etapa de seleção de atributos pode alterar de forma substantiva o comportamento de detectores de intrusão.

No contexto do presente projeto, essa discussão é particularmente pertinente, pois o pipeline utiliza pools de atributos e seleção por especialista, com artefatos explícitos de configuração. Assim, a literatura oferece suporte conceitual para a combinação entre especialização e engenharia de atributos, sem implicar que exista uma configuração universalmente ótima.

### 2.4 Interpretabilidade e XAI em IDS

A incorporação de técnicas de explicabilidade em IDS tem sido tratada como requisito para uso prático de modelos mais complexos. O estudo sobre avaliação de IDS com XAI citado anteriormente destaca o papel de métodos como SHAP e LIME na interpretação das decisões de modelos supervisionados. Em ambientes de segurança, esse aspecto é relevante não apenas para auditoria técnica, mas também para confiança operacional de analistas humanos.

Para este artigo, a literatura de XAI funciona como base para tratar interpretabilidade como dimensão complementar ao desempenho, evitando que avaliação de IDS se restrinja a métricas agregadas de classificação.

### 2.5 Síntese crítica e espaço de pesquisa

As referências disponíveis convergem para três pontos: (i) a utilidade de ML em IDS depende de desenho experimental rigoroso; (ii) ensembles e estratégias orientadas por classe são abordagens recorrentes para lidar com diversidade de ataques; e (iii) interpretabilidade tem papel crescente na validação de sistemas de detecção. Ao mesmo tempo, observa-se que os trabalhos analisados concentram-se em contextos específicos (por exemplo, IoV e WSN) ou em propostas de otimização pontual de modelos e atributos.

Nesse cenário, há espaço para uma investigação acadêmica que articule, de forma reprodutível, arquitetura em dois estágios (gatekeeper + especialistas), comparação com baselines coerentes e avaliação conjunta de desempenho e custo de inferência em IDS binário. É nesse espaço que o presente artigo se posiciona, sem pressupor superioridade a priori da abordagem proposta.

## 3 Metodologia

### 3.1 Visão geral da abordagem

Este trabalho adota uma abordagem de classificação hierárquica para detecção de intrusões, implementada no projeto `twodaef` e organizada em dois estágios complementares: um classificador inicial de triagem (gatekeeper) e um conjunto de classificadores especialistas. A proposta é avaliada no contexto de IDS com formulação binária, mantendo aderência ao escopo do repositório e separando claramente a camada técnica (pipeline de dados, treino e inferência) da camada acadêmica de análise.

Do ponto de vista metodológico, a abordagem não pressupõe superioridade universal em relação a modelos globais únicos. O objetivo é investigar, sob protocolo reprodutível, se a decomposição da decisão em etapas sucessivas constitui uma alternativa plausível para lidar com dificuldades típicas de IDS, como heterogeneidade de padrões, sobreposição entre classes e sensibilidade a falsos negativos.

### 3.2 Arquitetura em dois estágios

A arquitetura empregada segue a lógica Gatekeeper -> Especialista, conforme implementação em `src/twodaef/`. No primeiro estágio, uma decisão de roteamento é produzida a partir de um conjunto reduzido de atributos. No segundo estágio, a amostra é encaminhada para um especialista associado à classe (ou ao grupo de classes) indicado pelo roteamento inicial.

Em termos conceituais, o primeiro estágio realiza uma filtragem de baixa complexidade; o segundo estágio concentra a discriminação mais fina. No recorte binário adotado neste artigo, a especialização pode ocorrer por classes diretamente (por exemplo, `Benign` e `Others`) ou por grupos funcionais equivalentes, preservando a mesma ideia de roteamento hierárquico.

### 3.3 Papel do gatekeeper

O gatekeeper é implementado como um classificador de árvore de decisão podada (`DecisionTreeClassifier`) no módulo `src/twodaef/gatekeeper.py`, com hiperparâmetros controláveis para profundidade e tamanho mínimo de folha. Sua função principal é produzir uma decisão inicial rápida e, com isso, definir qual especialista deverá ser acionado na etapa seguinte.

As variáveis de entrada do gatekeeper são explicitadas por arquivos de colunas em `configs/cols/`, o que mantém a seleção de atributos rastreável e separada do código-fonte. Essa decisão de projeto favorece reprodutibilidade e facilita a manutenção de versões por dataset/recorte sem alteração da lógica central do classificador.

### 3.4 Papel dos especialistas

Os especialistas são treinados por classe a partir do módulo `src/twodaef/specialists/train_specialists.py`. Para cada classe alvo, o pipeline avalia combinações entre famílias de modelos disponíveis (por exemplo, LightGBM, XGBoost, CatBoost e alternativas do scikit-learn) e conjuntos de atributos candidatos oriundos de um feature pool. A seleção do especialista segue critério de desempenho por classe (F1 da classe correspondente), com desempate por latência de inferência.

Esse desenho permite heterogeneidade entre especialistas: classes distintas podem ser atendidas por modelos e subconjuntos de atributos diferentes. Em vez de impor um único indutor para todo o espaço de dados, o método busca adequar a capacidade discriminativa ao comportamento específico de cada classe.

### 3.5 Fluxo geral do pipeline

O fluxo metodológico completo pode ser resumido em cinco etapas:

1. Preparação dos dados por scripts em `scripts/`, com geração de conjuntos de treino e avaliação/inferência e normalização de rótulos conforme o recorte.
2. Definição dos conjuntos de atributos do gatekeeper (`configs/cols/*.txt`) e dos feature pools dos especialistas (`artifacts/feature_pools/*.json`).
3. Treino dos componentes: gatekeeper e especialistas, com persistência dos modelos em `artifacts/trained_models/`.
4. Construção/uso do mapeamento de especialistas (`configs/mappings/*.json`), que associa classes a modelo, feature set e caminhos dos artefatos.
5. Inferência em dois estágios (`src/twodaef/infer/two_stage.py`), na qual cada amostra recebe predição final após roteamento inicial e decisão do especialista correspondente.

Na inferência, o sistema também registra informações auxiliares para auditoria metodológica, como predição do gatekeeper, especialista acionado e estimativas de latência por estágio. Esses elementos não constituem resultado em si, mas viabilizam rastreabilidade e análise posterior.

### 3.6 Conjuntos de atributos, mapeamentos e artefatos

O repositório adota separação explícita entre configuração e execução. Em particular:

- `configs/cols/` contém as listas de atributos do gatekeeper;
- `artifacts/feature_pools/` contém os conjuntos de atributos candidatos para especialistas;
- `configs/mappings/` contém mapeamentos de especialistas e, quando necessário, mapas de alinhamento de rótulos do gatekeeper;
- `artifacts/trained_models/` contém os modelos persistidos para gatekeeper e especialistas.

Essa organização favorece reprodutibilidade porque torna observáveis as decisões de modelagem (quais atributos, quais especialistas e quais mapeamentos) sem exigir alteração direta dos módulos principais do pipeline.

### 3.7 Justificativa metodológica da decomposição hierárquica

A escolha por decomposição hierárquica e especialização é justificada por três argumentos metodológicos no contexto de IDS. Primeiro, a triagem inicial reduz o espaço de decisão imediato e pode tornar o processo de inferência mais controlável em termos computacionais. Segundo, a especialização por classe permite que diferentes regiões do problema sejam tratadas por modelos e atributos potencialmente mais adequados às suas características. Terceiro, a estrutura em estágios facilita análise interpretável por componente, uma vez que decisões de roteamento e decisões finais podem ser examinadas separadamente.

Assim, a metodologia proposta busca equilibrar desempenho discriminativo, custo operacional e transparência analítica, sem antecipar conclusões empíricas antes da apresentação dos experimentos e resultados.

## 4 Experimentos

### 4.1 Delineamento experimental

O delineamento experimental deste artigo foi estruturado para avaliar, de forma reprodutível, uma arquitetura de detecção de intrusões em dois estágios (gatekeeper + especialistas) no contexto de classificação binária. Em coerência com o escopo do repositório, a seção experimental descreve cenários, insumos e critérios de avaliação com base nos artefatos e documentos técnicos versionados, sem introduzir componentes externos ao projeto.

### 4.2 Dataset principal e enquadramento do problema

O dataset principal adotado no artigo é o **CIC-IDS2018**, na formulação binária com rótulos agregados para tráfego benigno e tráfego de ataque (ou classe equivalente). Esse recorte está alinhado ao material em `reports/cic/`, aos scripts de preparação disponíveis e ao objetivo do trabalho de discutir a viabilidade metodológica da arquitetura hierárquica em IDS.

Como cenário complementar de validade externa, o projeto também mantém avaliação binária com **UNSW-NB15**, documentada em `reports/unsw_bin/`. Entretanto, o foco analítico desta seção permanece no desenho experimental principal baseado no CIC.

Do ponto de vista de aprendizado supervisionado, o problema é modelado como classificação binária em dados tabulares de tráfego de rede, com atenção explícita a desafios usuais de IDS, como desbalanceamento de classes, sobreposição parcial de padrões entre tráfego benigno e malicioso e impacto operacional de erros do tipo falso negativo.

### 4.3 Preparação e pré-processamento dos dados

A preparação de dados é conduzida por scripts versionados em `scripts/`, com separação entre dados brutos (não versionados) e artefatos experimentais. Para o CIC, os procedimentos de preparação incluem construção de arquivos de treino e avaliação a partir dos dados brutos (`scripts/prep_cic_train.py` e `scripts/make_cic_eval.py`). O projeto também inclui um recorte robusto sem a variável de porta de destino (`scripts/prep_cic_robust.py`), utilizado em comparações específicas previstas no desenho experimental.

No nível de modelagem, o pipeline privilegia atributos numéricos e aplica rotinas de sanitização para valores ausentes ou infinitos, conforme implementado nos módulos de treino e inferência em `src/twodaef/`. A seleção efetiva de atributos não é fixa para todo o sistema: ela é definida por listas de colunas para o gatekeeper (`configs/cols/`) e por pools de atributos candidatos para especialistas (`artifacts/feature_pools/`).

### 4.4 Configuração experimental

A configuração experimental segue a organização do repositório:

1. O **gatekeeper** é treinado com conjunto de atributos explícito em arquivos de configuração.
2. Os **especialistas** são treinados por classe com busca entre combinações de famílias de modelos e conjuntos de atributos candidatos.
3. O mapeamento classe -> especialista é persistido em `configs/mappings/`, garantindo rastreabilidade do especialista selecionado em cada classe.
4. A inferência em dois estágios produz predições finais e registra informações auxiliares de decisão e latência por estágio.
5. A avaliação consolida métricas e figuras em `reports/`, de acordo com o plano experimental descrito em `docs/experiment_plan.md` e `docs/paper_experimental_plan.md`.

Para reprodutibilidade, o projeto adota parâmetros controlados nos scripts (por exemplo, sementes fixas quando aplicável) e mantém separação entre código, configuração e artefatos gerados.

### 4.5 Baselines e comparações coerentes com o projeto

As comparações consideradas nesta pesquisa são restritas ao que está explicitamente suportado no repositório:

- **Baseline global XGBoost** para o cenário robusto do CIC (`scripts/baseline_xgb_cic_robust.py`), sem decomposição em dois estágios.
- **Comparação por seleção de atributos** no CIC robusto, contrapondo configuração com pool reduzido e configuração com conjunto amplo de atributos (`scripts/make_feature_pool_cic_robust.py` e `scripts/make_feature_pool_cic_robust_all.py`).
- **Comparação entre famílias de modelos dos especialistas** (LGBM, XGB e CatBoost), conforme plano documentado em `reports/cic/EXPERIMENTOS_BOOSTERS.md`.

Essas comparações são tratadas como parte do desenho experimental e não implicam, por si, conclusão de superioridade de qualquer abordagem antes da análise de resultados.

### 4.6 Métricas de avaliação

As métricas adotadas refletem critérios tradicionais de avaliação em IDS e os artefatos efetivamente gerados pelo projeto:

- **Recall** da classe de ataque;
- **Precision** da classe de ataque;
- **F1-score** por classe e **F1-macro**;
- **Acurácia** global;
- **Matriz de confusão** em valores absolutos (TP, FP, TN, FN);
- **Latência média de inferência** por estágio (gatekeeper e especialista) e latência total estimada por amostra.

### 4.7 Justificativa para a escolha das métricas

Em IDS, a ênfase em **recall da classe maliciosa** é metodologicamente justificada pelo maior custo operacional associado a falsos negativos, que correspondem a ataques não detectados. A **precision** é incluída para controlar o impacto de alarmes indevidos, importante para a operação prática de centros de monitoramento. O **F1-score** (por classe e macro) é utilizado como medida de equilíbrio entre recall e precision, especialmente útil em cenários com desbalanceamento.

A **matriz de confusão absoluta** complementa as métricas agregadas por permitir inspeção direta da distribuição de erros. Por fim, métricas de **latência de inferência** são incorporadas porque a viabilidade de um IDS não depende apenas de qualidade preditiva, mas também de custo computacional compatível com uso operacional.

## 5 Resultados

Esta seção apresenta exclusivamente os resultados disponíveis nos artefatos versionados do projeto, com base principal em `reports/` e suporte em relatórios de `docs/` quando necessário para completar informações de execução. Não são introduzidos valores externos aos arquivos do repositório.

### 5.1 Base de evidências utilizada

Foram considerados, como fontes primárias de resultado:

- `reports/cic/metrics_again.json`
- `reports/unsw_bin/metrics_again.json`
- `reports/unsw_bin/metrics_again_unsw_legacy.json`
- `reports/metrics_comparados.csv` e `reports/metrics_comparados.md`
- `reports/cic/confusion_matrix_cic.png` e `reports/cic/f1_per_class_cic.png`
- `reports/unsw_bin/confusion_matrix_unsw.png` e `reports/unsw_bin/f1_per_class_unsw.png`
- `reports/cic/xai/xai_shap_consolidado.csv` e `reports/cic/XAI_BRIEF.md`

Como apoio documental, foram utilizados:

- `reports/cic/RELATORIO_CIC.md` (versão `v0.2.0-cic`, data 2025-11-19)
- `reports/unsw_bin/RELATORIO_UNSW.md` (versão `v0.1.0-unsw-mvp`, data 2025-10-31)
- `docs/cic_eval_report.md` e `docs/unsw_eval_report.md`

### 5.2 Métricas agregadas por cenário

A Tabela 1 consolida os valores agregados explicitamente presentes nos arquivos JSON de métricas.

**Tabela 1 — Métricas agregadas disponíveis nos artefatos versionados**

| Cenário | Arquivo-fonte | F1-macro | Acurácia | n |
|---|---|---:|---:|---:|
| CIC-IDS2018 (binário) | `reports/cic/metrics_again.json` | 1.000000 | 1.000000 | 100000 |
| UNSW-NB15 (binário, execução `unsw_bin`) | `reports/unsw_bin/metrics_again.json` | 0.890069 | 0.898432 | 175341 |
| UNSW-NB15 (binário, execução `unsw` legado) | `reports/unsw_bin/metrics_again_unsw_legacy.json` | 0.892938 | 0.900987 | 175341 |

Observa-se a coexistência de dois artefatos de métricas para o UNSW-NB15 (`unsw_bin` e `unsw` legado), com pequena variação nos valores agregados e caminhos de saída distintos (`outputs/unsw_bin/preds.csv` e `outputs/eval_unsw/preds.csv`).

### 5.3 Métricas por classe e matrizes de confusão

Para o experimento CIC, estão disponíveis as figuras `reports/cic/f1_per_class_cic.png` e `reports/cic/confusion_matrix_cic.png`. Para o experimento UNSW binário, estão disponíveis `reports/unsw_bin/f1_per_class_unsw.png` e `reports/unsw_bin/confusion_matrix_unsw.png`.

Esses arquivos registram visualmente a distribuição de desempenho por classe e os padrões de erro de classificação em cada cenário. No conjunto versionado atual, entretanto, os valores numéricos detalhados por classe (em formato tabular) e as contagens absolutas da matriz de confusão (TP, FP, TN, FN em arquivo estruturado) não estão disponibilizados diretamente em `reports/`.

### 5.4 Custo de inferência reportado

No relatório UNSW versionado em `reports/unsw_bin/RELATORIO_UNSW.md`, consta latência média de inferência total de aproximadamente **0.8776 ms** por amostra, com decomposição em estágio de gatekeeper (~**0.000038 ms**) e estágio especialista (~**0.877536 ms**).

Para o CIC, a síntese numérica de latência explícita está registrada em `docs/cic_eval_report.md` (execução `v0.1.0-cic-mvp`), com valor total aproximado de **0.0001 ms** por amostra (gatekeeper ~**0.00008 ms**, especialista ~**0.00000 ms**). No relatório `reports/cic/RELATORIO_CIC.md` (versão `v0.2.0-cic`), a ênfase está na descrição do pipeline e dos artefatos, sem tabela agregada específica de latência.

### 5.5 Consolidação inter-datasets

Os arquivos `reports/metrics_comparados.csv` e `reports/metrics_comparados.md` apresentam uma consolidação entre CIC-IDS2018 e UNSW-NB15 com os seguintes valores:

- UNSW-NB15: `f1_macro = 0.8929`, `accuracy = 0.9010`;
- CIC-IDS2018: `f1_macro = 1.0000`, `accuracy = 1.0000`.

Essa consolidação utiliza a execução UNSW identificada como `unsw` (legado), coerente com `metrics_again_unsw_legacy.json`.

### 5.6 Artefatos de interpretabilidade (XAI) disponíveis

No cenário CIC binário, o projeto contém consolidação SHAP em `reports/cic/xai/xai_shap_consolidado.csv` e resumo em `reports/cic/XAI_BRIEF.md`. Entre as variáveis com maior contribuição média absoluta (|SHAP| médio), destacam-se:

- Classe `Benign`: `dst_port` (0.0239138633), `fwd_seg_size_min` (0.0107793954), `bwd_pkts_s` (0.0026201308);
- Classe `Others`: `fwd_seg_size_min` (0.0217095731), `init_fwd_win_byts` (0.0159603954), `flow_iat_max` (0.0062686020).

Esses valores são reportados como evidência descritiva de importância de atributos e não como métrica de desempenho classificatório.

### 5.7 Completude e limitações dos resultados versionados

Com base no estado atual do repositório, os resultados agregados (F1-macro, acurácia e tamanho amostral), as figuras de matriz de confusão/F1 por classe e os artefatos de XAI estão disponíveis e passíveis de rastreamento.

Por outro lado, alguns itens previstos em documentos de planejamento aparecem incompletos ou ausentes no material versionado: (i) não há, em `reports/`, arquivos tabulares de matriz de confusão absoluta por dataset (`TP`, `FP`, `TN`, `FN`) no formato JSON explicitado no plano experimental; (ii) os arquivos `preds.csv` referenciados nas métricas apontam para `outputs/`, pasta não versionada; e (iii) o relatório `reports/cic/EXPERIMENTOS_BOOSTERS.md` mantém a tabela comparativa entre famílias de modelos sem preenchimento de resultados.

## 6 Discussão

### 6.1 Interpretação dos resultados no contexto de IDS

Os resultados disponíveis sugerem que a arquitetura em dois estágios é operacionalmente viável no recorte binário adotado, com desempenho agregado elevado no cenário CIC e desempenho também consistente, porém inferior, no cenário UNSW. Em termos de IDS, esse comportamento é compatível com a expectativa de que diferentes bases imponham níveis distintos de dificuldade de separação entre tráfego benigno e malicioso.

Sem extrapolar além dos artefatos versionados, a leitura mais prudente é que o pipeline se mostrou capaz de produzir classificações com bom nível de acerto agregado nos dois cenários avaliados, mas com sensibilidade ao contexto de dados e à configuração de execução. A presença de duas versões de métricas para o UNSW (`unsw_bin` e `unsw` legado), com variações pequenas porém observáveis, reforça essa interpretação.

### 6.2 Relevância das métricas para a análise

No domínio de detecção de intrusões, métricas agregadas como acurácia e F1-macro são úteis para visão global, mas não esgotam a avaliação de risco. A ênfase em recall e precision da classe maliciosa permanece metodologicamente central: recall baixo implica ataques não detectados; precision baixa implica aumento de alarmes indevidos.

As figuras de F1 por classe e matriz de confusão disponíveis em `reports/` contribuem para avaliar distribuição de erros além da média agregada. Contudo, como os artefatos versionados não incluem, no estado atual, tabelas estruturadas com TP, FP, TN e FN por cenário, a discussão quantitativa fina desses erros precisa ser tratada com cautela e reconhecida como limitação empírica desta etapa.

### 6.3 Papel conceitual da arquitetura em dois estágios

Do ponto de vista conceitual, os resultados são compatíveis com a hipótese metodológica de decomposição hierárquica: o gatekeeper atua como etapa inicial de triagem e os especialistas assumem a decisão final com maior granularidade. Essa organização é coerente com o objetivo de reduzir a rigidez de modelos globais únicos em cenários com heterogeneidade de padrões de ataque.

A estratégia de especialistas por classe também dialoga com o desenho de seleção por pares (modelo, conjunto de atributos), permitindo que cada classe seja tratada com configuração potencialmente distinta. Ainda que essa escolha aumente o número de componentes a gerenciar, ela oferece flexibilidade para ajustar o classificador às características de cada classe no espaço de atributos disponível.

### 6.4 Trade-offs entre detecção, custo computacional e complexidade

Os artefatos de latência indicam que o custo computacional não é uniforme entre cenários: no UNSW, o estágio especialista concentra a maior parcela do tempo de inferência, enquanto no CIC os valores reportados são substancialmente menores. Isso sugere que o custo da arquitetura em dois estágios depende do perfil do dataset e da combinação efetiva de modelos/atributos selecionada.

Em termos práticos, a arquitetura oferece uma troca explícita: maior flexibilidade e potencial de adaptação por classe em contrapartida de maior complexidade de configuração, rastreamento de artefatos e governança experimental (mapeamentos, pools de atributos, versões de execução). Assim, a avaliação da abordagem deve considerar simultaneamente desempenho, latência e custo de manutenção metodológica.

### 6.5 Comentário sobre interpretabilidade (XAI)

Os artefatos de XAI disponíveis para o CIC (`reports/cic/xai/xai_shap_consolidado.csv` e `reports/cic/XAI_BRIEF.md`) mostram que decisões dos especialistas estão associadas a atributos de tráfego identificáveis, como `dst_port`, `fwd_seg_size_min` e variáveis de temporalidade/interação de pacotes. Esse resultado fortalece o uso de interpretabilidade como apoio à auditoria técnica do modelo.

Ainda assim, a evidência de XAI deve ser tratada como complementar: importância de atributos não equivale a relação causal e não substitui avaliação preditiva por métricas de classificação. Além disso, há sinais de múltiplos snapshots de consolidação no repositório, o que demanda controle rigoroso de versão para interpretações reproduzíveis.

### 6.6 Limitações do estudo e do material experimental

A discussão dos achados é condicionada por limitações objetivas do material disponível:

- ausência, em `reports/`, de matrizes de confusão absolutas em formato estruturado (TP/FP/TN/FN) para todos os cenários;
- ausência dos arquivos `preds.csv` no versionamento (referenciados em `outputs/`, pasta não versionada);
- coexistência de resultados agregados distintos para UNSW em execuções diferentes (`unsw_bin` e `unsw` legado);
- tabela de comparação entre famílias de especialistas em `reports/cic/EXPERIMENTOS_BOOSTERS.md` ainda não preenchida;
- informações de ambiente de execução (hardware e configuração completa) não consolidadas em um único relatório padronizado.

Esses pontos não invalidam os resultados apresentados, mas restringem o nível de inferência comparativa possível nesta versão do estudo.

### 6.7 Implicações acadêmicas e técnicas

No plano acadêmico, o trabalho contribui ao documentar, de forma reprodutível e conservadora, a aplicação de uma arquitetura hierárquica de IA para IDS, articulando desempenho agregado, custo de inferência e evidências de interpretabilidade no mesmo escopo experimental.

No plano técnico, os resultados indicam que o desenho em dois estágios é promissor como estratégia de engenharia para cenários binários de detecção de intrusão, desde que acompanhado por governança de artefatos, padronização de relatórios e consolidação rigorosa de métricas por classe e por tipo de erro. Essa combinação é essencial para transformar desempenho experimental em evidência robusta para uso prático.

## 7 Conclusão

Este artigo investigou a aplicação de Inteligência Artificial à detecção de intrusões em redes por meio de uma arquitetura de classificação em dois estágios, composta por gatekeeper e especialistas por classe. O problema de pesquisa partiu de desafios recorrentes em IDS, como heterogeneidade de padrões, sobreposição entre classes e custo operacional de erros, com ênfase particular na necessidade de avaliação criteriosa em cenários binários.

No desenvolvimento do trabalho, foram articulados: (i) revisão de literatura sobre IDS com aprendizado de máquina, ensembles, especialização e interpretabilidade; (ii) formalização metodológica da arquitetura hierárquica adotada no projeto; (iii) delineamento experimental com base em artefatos versionados; e (iv) análise dos resultados efetivamente disponíveis para CIC-IDS2018 e UNSW-NB15. Em termos de síntese, os achados sustentam a viabilidade operacional do pipeline em dois estágios no escopo estudado, sem permitir, nesta versão do material, inferências definitivas de superioridade geral sobre alternativas.

Como contribuições, o trabalho oferece uma consolidação acadêmica, reprodutível e tecnicamente rastreável de um fluxo de IDS em dois estágios, conectando desempenho agregado, custo de inferência e evidências de interpretabilidade no mesmo quadro analítico. Também contribui ao explicitar critérios de leitura conservadora dos resultados, especialmente quando há diferenças entre execuções e quando parte dos artefatos planejados não está integralmente consolidada no versionamento.

As limitações do estudo decorrem, sobretudo, do material experimental disponível: ausência de matrizes de confusão absolutas estruturadas por cenário (TP, FP, TN, FN), ausência dos arquivos `preds.csv` no repositório versionado, coexistência de snapshots distintos para UNSW e incompletude de comparações planejadas entre famílias de especialistas. Além disso, informações de ambiente de execução não estão padronizadas de forma única, o que restringe análises comparativas mais finas.

Como trabalhos futuros, recomenda-se: (1) padronizar e versionar artefatos de avaliação em nível de classe e de tipo de erro; (2) consolidar, em relatório único, configuração experimental e ambiente computacional; (3) concluir as comparações previstas de baselines e variações de especialistas; (4) ampliar a avaliação para recortes multiclasses e cenários adicionais já previstos no projeto; e (5) aprofundar o uso de XAI com protocolo homogêneo entre datasets. Esses passos tendem a fortalecer a robustez empírica das conclusões e a utilidade acadêmica e técnica da arquitetura proposta.

