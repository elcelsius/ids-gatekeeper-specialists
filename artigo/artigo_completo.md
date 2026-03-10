# Decomposição Hierárquica e Especialização de Modelos em Inteligência Artificial: um Estudo de Caso em Detecção de Intrusões

## Resumo

Problemas complexos de classificação supervisionada frequentemente envolvem heterogeneidade de padrões, sobreposição entre classes, desbalanceamento e fronteiras de decisão difíceis de capturar por modelos monolíticos. Nesse contexto, este artigo investiga uma estratégia de Inteligência Artificial baseada em decomposição hierárquica da decisão, implementada por meio de uma arquitetura em dois estágios composta por um mecanismo inicial de triagem (*gatekeeper*) e classificadores especialistas. A proposta é analisada em um estudo de caso de detecção de intrusões em redes, adotado como domínio aplicado para avaliar a adequação metodológica da arquitetura. O trabalho foi desenvolvido a partir do ecossistema técnico do projeto 2D-AEF e considerou, de forma conservadora e reprodutível, um pipeline versionado de preparação de dados, seleção de atributos, treinamento, inferência e avaliação, com ênfase no recorte binário e uso principal do dataset CIC-IDS2018, complementado pelo UNSW-NB15 quando sustentado pelos artefatos disponíveis. Os resultados agregados, as matrizes de confusão, os registros de custo inferencial e os artefatos complementares de interpretabilidade indicam que a estratégia hierárquica é operacionalmente viável no escopo estudado e oferece base analítica para discutir desempenho, erro, custo e rastreabilidade. Entretanto, as conclusões permanecem condicionadas por limitações do material versionado, incluindo lacunas em artefatos estruturados por classe e coexistência de snapshots distintos em parte das execuções. Conclui-se que a arquitetura em dois estágios constitui uma estratégia metodologicamente plausível de IA aplicada para problemas complexos de classificação, tendo a detecção de intrusões como estudo de caso relevante, desde que acompanhada por governança experimental rigorosa e consolidação consistente de métricas e relatórios.

## 1 Introdução

Problemas de classificação supervisionada tornam-se particularmente desafiadores quando envolvem sobreposição entre classes, desbalanceamento, heterogeneidade dos padrões de entrada e fronteiras de decisão difíceis de modelar por uma única função global. Em contextos dessa natureza, abordagens monolíticas podem apresentar desempenho desigual entre regiões do espaço de atributos, o que motiva a investigação de estratégias de Inteligência Artificial capazes de decompor o problema em etapas ou subproblemas mais específicos.

Entre as possibilidades discutidas na literatura de IA aplicada, arquiteturas hierárquicas e sistemas com especialização de classificadores oferecem uma alternativa conceitualmente relevante. Nesses arranjos, uma etapa inicial de triagem ou roteamento pode encaminhar cada amostra para modelos mais especializados, potencialmente mais adequados para lidar com padrões locais de decisão. Essa perspectiva desloca o foco de um único classificador global para um processo estruturado de inferência, no qual a decisão final resulta da combinação entre filtragem inicial e análise especializada.

A detecção de intrusões em redes constitui um estudo de caso particularmente apropriado para investigar esse tipo de estratégia. Além de sua relevância prática, o domínio de IDS reúne características típicas de problemas complexos de classificação, como desbalanceamento entre categorias, semelhança parcial entre comportamentos benignos e maliciosos, diversidade interna dos padrões de ataque e necessidade de avaliação criteriosa do comportamento do modelo. Assim, embora o cenário aplicado pertença ao campo da segurança computacional, ele pode ser entendido, neste trabalho, como um ambiente de validação para uma questão mais ampla de Inteligência Artificial.

Nesse contexto, este artigo investiga uma arquitetura de classificação em dois estágios, derivada do ecossistema técnico do projeto 2D-AEF e aqui reposicionada como objeto de análise em IA aplicada. Em termos gerais, a arquitetura combina um classificador inicial de triagem, denominado gatekeeper, com classificadores especialistas responsáveis por subproblemas ou regiões mais específicas da decisão. O interesse central do estudo não está em assumir superioridade universal da abordagem, mas em examinar se a decomposição hierárquica da inferência constitui uma estratégia metodologicamente plausível para tratar problemas classificatórios complexos em um cenário aplicado realista.

O objetivo do artigo é investigar, de forma conservadora e reprodutível, a adequação dessa arquitetura em dois estágios para problemas complexos de classificação, utilizando a detecção de intrusões em formulação binária como estudo de caso principal. Para isso, o trabalho considera métricas clássicas de desempenho, análise de matriz de confusão, custo de inferência e, quando sustentado pelos artefatos disponíveis, evidências complementares de interpretabilidade. O recorte experimental foi definido de modo a preservar coerência com os relatórios e artefatos efetivamente existentes no projeto, evitando extrapolações indevidas.

Além desta introdução, o artigo está organizado da seguinte forma. A Seção 2 discute os trabalhos relacionados, com ênfase em classificação complexa, arquiteturas hierárquicas, especialização de modelos e aplicações em IDS. A Seção 3 apresenta a metodologia e descreve a arquitetura em dois estágios como estratégia de IA. A Seção 4 detalha o desenho experimental adotado no estudo de caso. A Seção 5 reúne os resultados efetivamente disponíveis. A Seção 6 discute implicações, trade-offs e limitações da abordagem. Por fim, a Seção 7 apresenta as conclusões e indica possibilidades de continuidade.

## 2 Trabalhos Relacionados

## 2.1 Classificação complexa e arquiteturas hierárquicas em IA aplicada

A literatura de Inteligência Artificial aplicada tem discutido, de forma recorrente, as limitações de modelos monolíticos em problemas de classificação que apresentam heterogeneidade interna, sobreposição entre classes, fronteiras de decisão difíceis e necessidade de tratamento diferenciado para subconjuntos do espaço de entrada. Nesse contexto, arquiteturas hierárquicas e estratégias de decomposição da decisão surgem como alternativas metodológicas relevantes, pois permitem organizar o processo inferencial em múltiplos estágios, com diferentes níveis de granularidade.

No domínio de detecção de intrusões, essa discussão aparece de maneira explícita em trabalhos recentes sobre classificação hierárquica. Uddin et al. investigam uma abordagem em três níveis para IDS, distinguindo inicialmente tráfego benigno e malicioso, depois categorias amplas de ataque e, por fim, subtipos mais específicos. Embora o estudo não reporte superioridade global inequívoca da hierarquia sobre a classificação plana em todos os cenários, ele mostra que a organização hierárquica pode reduzir um erro particularmente crítico no domínio, que é a classificação de tráfego malicioso como benigno. Esse resultado é importante para o presente artigo não apenas pelo contexto de segurança, mas sobretudo por reforçar a pertinência metodológica de estruturas de decisão em múltiplos níveis para problemas classificatórios complexos. :contentReference[oaicite:2]{index=2}

Além disso, propostas multicamadas recentes, como o sistema MIDES, reforçam que arquiteturas compostas podem ser concebidas como mecanismos adaptativos de organização do processo decisório. Nesse tipo de desenho, uma etapa inicial de filtragem rápida é combinada com camadas posteriores de análise mais especializada, com o objetivo de equilibrar desempenho e eficiência. Ainda que tais trabalhos estejam ancorados no domínio de IDS, eles dialogam com uma questão mais ampla de IA aplicada: como estruturar a decisão classificatória quando um único modelo global pode não ser suficiente para capturar adequadamente toda a complexidade do problema. :contentReference[oaicite:3]{index=3}

## 2.2 IDS com aprendizado de máquina como estudo de caso de classificação complexa

A detecção de intrusões baseada em aprendizado de máquina consolidou-se como uma área aplicada importante, em parte pela dificuldade de sistemas puramente baseados em assinatura acompanharem a diversidade e a evolução dos ataques. Ao mesmo tempo, a literatura recente mostra que o desempenho de IDS com ML não depende apenas da escolha do algoritmo, mas também da qualidade do desenho experimental, da seleção de datasets, do tratamento de desbalanceamento, da escolha de métricas e da clareza das comparações realizadas.

A revisão sistemática de Rehman et al. é particularmente útil nesse ponto, pois mostra que a pesquisa recente em IDS com aprendizado de máquina se apoia fortemente em escolhas metodológicas relacionadas a bases de dados, protocolos de avaliação e métricas, além de registrar limitações recorrentes como desbalanceamento, obsolescência parcial de alguns datasets e dificuldade de comparação entre estudos. Para o presente trabalho, essa literatura é importante porque justifica o uso de IDS não como fim em si mesmo, mas como estudo de caso exigente para investigar uma estratégia de IA aplicada à classificação complexa. Em outras palavras, o domínio de IDS oferece um cenário adequado para avaliar arquiteturas hierárquicas porque concentra, de forma realista, muitos dos desafios que essas arquiteturas pretendem enfrentar. :contentReference[oaicite:4]{index=4}

Nesse sentido, alguns trabalhos herdados da linha do projeto 2D-AEF continuam conceitualmente relevantes. Propostas como *A Novel Ensemble Framework for an Intelligent Intrusion Detection System* e *LCCDE: A Decision-Based Ensemble Framework for Intrusion Detection in the Internet of Vehicles* ajudam a mostrar que a combinação de modelos, a decisão orientada por classe e o uso de múltiplos classificadores já constituem uma direção consolidada em IDS. O presente artigo, contudo, reposiciona essa discussão ao enfatizar menos a ideia de ensemble como simples mecanismo de aumento de desempenho e mais a noção de decomposição hierárquica da decisão como estratégia de IA. :contentReference[oaicite:5]{index=5}

## 2.3 Especialização de modelos, roteamento e subproblemas de decisão

Um dos pontos centrais do presente artigo é a hipótese de que a especialização de classificadores pode ser útil quando o problema global contém subestruturas com padrões distintos. Essa ideia aparece, de formas variadas, em arquiteturas orientadas por classe, em mecanismos de roteamento entre modelos e em sistemas que combinam triagem inicial com análise especializada posterior. Ainda que os trabalhos da literatura nem sempre utilizem a mesma terminologia de gatekeeper e especialistas, muitos deles compartilham a intuição de que diferentes regiões do espaço de decisão podem se beneficiar de tratamentos específicos.

No contexto de IDS, o uso de ensembles orientados por classe e de estruturas multicamadas sugere precisamente esse movimento de especialização. Em vez de confiar toda a inferência a um único classificador global, parte-se do princípio de que decisões iniciais mais amplas podem encaminhar a amostra para etapas subsequentes mais adequadas ao seu perfil. O interesse acadêmico dessa abordagem, no âmbito da IA aplicada, está menos em defender uma arquitetura única como solução universal e mais em investigar se a decomposição do problema favorece decisões mais organizadas, análise mais fina de erro e melhor entendimento dos trade-offs entre capacidade preditiva, custo e complexidade estrutural. :contentReference[oaicite:6]{index=6}

Além disso, a especialização frequentemente se articula com seleção de atributos ou com subconjuntos de informação mais adequados a cada subproblema. Trabalhos anteriores da literatura de IDS já indicavam que escolhas de atributos podem alterar significativamente o comportamento dos detectores. No presente projeto, essa discussão ganha relevância adicional porque a arquitetura avaliada incorpora pools de atributos e artefatos explícitos de configuração, o que reforça a afinidade entre especialização classificatória e organização diferenciada da representação de entrada. :contentReference[oaicite:7]{index=7}

## 2.4 Interpretabilidade e XAI em sistemas classificatórios aplicados a IDS

A crescente complexidade de modelos de aprendizado de máquina tem ampliado o interesse por técnicas de interpretabilidade e Explainable AI, especialmente em domínios nos quais a decisão automatizada precisa ser auditável. Em IDS, esse movimento é particularmente relevante porque classificações incorretas podem ter implicações operacionais importantes, ao mesmo tempo em que analistas humanos frequentemente precisam compreender, ao menos em nível aproximado, por que determinada decisão foi produzida.

Estudos recentes tratam essa questão de maneira mais sistemática. Samed e Sagiroglu discutem a incorporação de modelos de XAI em IDS como resposta à opacidade de sistemas de detecção mais complexos. Khan et al., por sua vez, mostram que a literatura recente sobre XAI em IDS já é suficientemente extensa para demandar revisões sistemáticas próprias, incluindo não apenas benefícios de transparência, mas também limitações e superfícies adicionais de ataque. Em paralelo, Mohale et al. reforçam que interpretabilidade e desempenho não devem ser tratados como dimensões incompatíveis, mas também não podem ser confundidos: explicações ajudam a compreender o comportamento do modelo, sem substituir validação experimental rigorosa. :contentReference[oaicite:8]{index=8}

Para o presente artigo, a literatura de XAI cumpre um papel complementar. O objetivo não é deslocar o foco do trabalho para explicabilidade, mas reconhecer que, em uma arquitetura hierárquica com múltiplas etapas de decisão, mecanismos interpretáveis podem contribuir para inspecionar a coerência do fluxo inferencial e apoiar a análise dos artefatos experimentais disponíveis. Assim, interpretabilidade entra como dimensão analítica adicional dentro de um estudo mais amplo sobre estratégias de IA aplicada. :contentReference[oaicite:9]{index=9}

## 2.5 Síntese crítica e posicionamento do artigo

A literatura recente converge para três constatações relevantes. Primeiro, problemas de detecção de intrusões continuam sendo um campo fértil para investigação de classificadores avançados, mas a comparação entre propostas depende fortemente de desenho experimental rigoroso e de métricas apropriadas. Segundo, arquiteturas hierárquicas, multicamadas e orientadas por especialização constituem uma direção metodológica plausível quando o problema apresenta heterogeneidade, diferentes níveis de granularidade e custo assimétrico dos erros. Terceiro, interpretabilidade vem ganhando espaço como complemento importante à avaliação tradicional de desempenho, ainda que não substitua análise quantitativa consistente. :contentReference[oaicite:10]{index=10}

É nesse espaço que o presente artigo se insere. Diferentemente de estudos estritamente orientados ao domínio de segurança, este trabalho toma a detecção de intrusões como estudo de caso para investigar uma questão mais ampla de IA aplicada: a adequação de uma arquitetura em dois estágios, com gatekeeper e especialistas, para problemas complexos de classificação. Com isso, o artigo busca articular arquitetura hierárquica, avaliação empírica, custo computacional e interpretabilidade em uma análise metodologicamente conservadora, sem pressupor superioridade universal da proposta e preservando o domínio de IDS como cenário de validação, e não como único centro conceitual do estudo. :contentReference[oaicite:11]{index=11} :contentReference[oaicite:12]{index=12}

## 3 Metodologia

## 3.1 Visão geral da abordagem

Este trabalho investiga uma estratégia de Inteligência Artificial voltada a problemas complexos de classificação, baseada na decomposição hierárquica da decisão em dois estágios complementares. A arquitetura analisada, implementada no ecossistema técnico do projeto `twodaef`, combina um classificador inicial de triagem, denominado *gatekeeper*, com classificadores especialistas responsáveis por decisões mais específicas em subespaços do problema. O domínio de detecção de intrusões é utilizado neste artigo como estudo de caso aplicado, e não como único centro conceitual da proposta.

Do ponto de vista metodológico, a abordagem parte da hipótese de que, em cenários com heterogeneidade de padrões, sobreposição entre classes e diferentes graus de dificuldade local de decisão, uma arquitetura em múltiplas etapas pode constituir alternativa plausível à adoção de um único classificador global. O objetivo, portanto, não é pressupor superioridade universal da estratégia hierárquica, mas examinar se a decomposição do processo inferencial favorece uma organização mais estruturada da decisão, com potencial para análise mais rica de desempenho, erro, custo computacional e interpretabilidade.

## 3.2 Arquitetura em dois estágios

A arquitetura empregada segue a lógica **Gatekeeper → Especialistas**, conforme implementada em `src/twodaef/`. No primeiro estágio, uma decisão inicial de triagem é produzida a partir de um conjunto mais enxuto de atributos, com o propósito de identificar a região do problema ou o grupo funcional ao qual a amostra parece pertencer. No segundo estágio, a amostra é encaminhada para um especialista associado ao encaminhamento definido na etapa anterior, onde ocorre a decisão mais refinada.

Em termos conceituais, o primeiro estágio atua como mecanismo de organização do espaço de decisão, enquanto o segundo concentra a discriminação mais específica. No recorte binário adotado neste artigo, essa especialização permanece metodologicamente relevante, pois mesmo uma formulação com duas classes pode se beneficiar de etapas distintas de triagem e refinamento, sobretudo quando o objetivo é observar o comportamento da arquitetura em um cenário controlado e coerente com os artefatos efetivamente disponíveis no projeto.

## 3.3 Papel do gatekeeper

O *gatekeeper* é implementado como um classificador de árvore de decisão podada (`DecisionTreeClassifier`), no módulo `src/twodaef/gatekeeper.py`, com hiperparâmetros configuráveis para profundidade máxima e tamanho mínimo de folha. Sua função metodológica central é realizar uma triagem inicial de baixa complexidade computacional, produzindo a decisão de roteamento que define qual especialista será acionado na etapa seguinte.

As variáveis de entrada utilizadas pelo *gatekeeper* são mantidas em arquivos de configuração localizados em `configs/cols/`, o que separa explicitamente a seleção de atributos da lógica principal do código-fonte. Essa escolha favorece rastreabilidade, reprodutibilidade e flexibilidade experimental, ao permitir que diferentes recortes de atributos sejam avaliados sem necessidade de alteração estrutural da implementação.

## 3.4 Papel dos especialistas

Os especialistas são treinados por meio do módulo `src/twodaef/specialists/train_specialists.py`. Para cada classe ou grupo alvo, o pipeline considera combinações entre famílias de modelos disponíveis no projeto e subconjuntos candidatos de atributos definidos em *feature pools*. A seleção do especialista é feita com base no desempenho da classe correspondente, adotando F1 como critério principal e latência de inferência como critério de desempate quando necessário.

Esse desenho permite heterogeneidade entre especialistas, isto é, diferentes regiões do problema podem ser atendidas por modelos e representações de entrada distintas. Em vez de impor um único indutor para todo o espaço de dados, a metodologia procura adequar o mecanismo discriminativo às características particulares de cada subproblema. Essa é precisamente a dimensão de IA aplicada que interessa ao presente artigo: investigar se a especialização pode funcionar como estratégia de organização da inferência em cenários classificatórios complexos.

## 3.5 Fluxo geral do pipeline

O fluxo metodológico adotado no estudo pode ser resumido em cinco etapas principais:

1. preparação dos dados por meio dos scripts disponíveis em `scripts/`, com geração dos conjuntos de treino e avaliação/inferência e padronização dos rótulos de acordo com o recorte experimental;
2. definição dos atributos utilizados pelo *gatekeeper* (`configs/cols/*.txt`) e dos *feature pools* dos especialistas (`artifacts/feature_pools/*.json`);
3. treinamento dos componentes da arquitetura, com persistência dos modelos em `artifacts/trained_models/`;
4. construção e utilização dos mapeamentos de especialistas (`configs/mappings/*.json`), associando classes, modelos, conjuntos de atributos e caminhos dos artefatos;
5. execução da inferência em dois estágios (`src/twodaef/infer/two_stage.py`), em que cada amostra recebe uma decisão final após o roteamento inicial e a avaliação do especialista correspondente.

Durante a inferência, o sistema também pode registrar informações auxiliares, como a predição do *gatekeeper*, o especialista acionado e estimativas de latência por estágio. Esses elementos não constituem, por si só, resultado experimental conclusivo, mas ampliam a rastreabilidade do processo inferencial e fornecem subsídios para análise posterior da arquitetura.

## 3.6 Conjuntos de atributos, mapeamentos e artefatos

O repositório adota uma separação explícita entre configuração, treinamento e execução. Em particular:

- `configs/cols/` contém as listas de atributos utilizadas pelo *gatekeeper*;
- `artifacts/feature_pools/` reúne os conjuntos de atributos candidatos para os especialistas;
- `configs/mappings/` armazena os mapeamentos de especialistas e, quando aplicável, os alinhamentos de rótulos necessários ao processo de roteamento;
- `artifacts/trained_models/` concentra os modelos persistidos do *gatekeeper* e dos especialistas.

Essa organização é metodologicamente importante porque torna observáveis as decisões de modelagem adotadas ao longo do pipeline. Assim, escolhas relativas a atributos, roteamento e especialização não ficam implícitas apenas no código, mas passam a existir também como artefatos auditáveis, o que reforça a reprodutibilidade do estudo.

## 3.7 Justificativa metodológica da decomposição hierárquica

A adoção de decomposição hierárquica e especialização é justificada, neste trabalho, por três argumentos principais. Primeiro, a triagem inicial permite reduzir a complexidade imediata da decisão, organizando o problema em etapas sucessivas e potencialmente mais controláveis. Segundo, a especialização por classe ou grupo funcional cria a possibilidade de empregar modelos e subconjuntos de atributos mais adequados a regiões específicas do espaço de dados. Terceiro, a estrutura em estágios favorece uma leitura analítica mais detalhada do comportamento do sistema, pois separa a decisão de roteamento da decisão final.

No estudo de caso em IDS, esses argumentos se tornam particularmente relevantes porque o domínio concentra características típicas de problemas complexos de classificação, como heterogeneidade de padrões, assimetria entre tipos de erro e necessidade de análise cuidadosa da decisão automatizada. Ainda assim, o interesse central do artigo permanece mais amplo: discutir a adequação de uma arquitetura hierárquica como estratégia de IA aplicada, utilizando a detecção de intrusões como ambiente de validação metodológica.

## 3.8 Considerações de escopo

A metodologia apresentada neste artigo está condicionada ao escopo experimental efetivamente sustentado pelos artefatos disponíveis no repositório. Por essa razão, a descrição da arquitetura e do pipeline foi construída de forma conservadora, preservando aderência à implementação real e evitando a inclusão de componentes, variações ou protocolos não documentados. Essa escolha é coerente com a proposta do trabalho, que privilegia uma análise metodologicamente rastreável da arquitetura em dois estágios, em vez de uma formulação excessivamente abrangente ou especulativa.

## 4 Experimentos

## 4.1 Delineamento experimental

O delineamento experimental deste artigo foi estruturado para avaliar, de forma reprodutível, uma arquitetura de detecção de intrusões em dois estágios (gatekeeper + especialistas) no contexto de classificação binária. Em coerência com o escopo do repositório, a seção experimental descreve cenários, insumos e critérios de avaliação com base nos artefatos e documentos técnicos versionados, sem introduzir componentes externos ao projeto.

## 4.2 Dataset principal e enquadramento do problema

O dataset principal adotado no artigo é o **CIC-IDS2018**, na formulação binária com rótulos agregados para tráfego benigno e tráfego de ataque (ou classe equivalente). Esse recorte está alinhado ao material em `reports/cic/`, aos scripts de preparação disponíveis e ao objetivo do trabalho de discutir a viabilidade metodológica da arquitetura hierárquica em IDS.

Como cenário complementar de validade externa, o projeto também mantém avaliação binária com **UNSW-NB15**, documentada em `reports/unsw_bin/`. Entretanto, o foco analítico desta seção permanece no desenho experimental principal baseado no CIC.

Do ponto de vista de aprendizado supervisionado, o problema é modelado como classificação binária em dados tabulares de tráfego de rede, com atenção explícita a desafios usuais de IDS, como desbalanceamento de classes, sobreposição parcial de padrões entre tráfego benigno e malicioso e impacto operacional de erros do tipo falso negativo.

## 4.3 Preparação e pré-processamento dos dados

A preparação de dados é conduzida por scripts versionados em `scripts/`, com separação entre dados brutos (não versionados) e artefatos experimentais. Para o CIC, os procedimentos de preparação incluem construção de arquivos de treino e avaliação a partir dos dados brutos (`scripts/prep_cic_train.py` e `scripts/make_cic_eval.py`). O projeto também inclui um recorte robusto sem a variável de porta de destino (`scripts/prep_cic_robust.py`), utilizado em comparações específicas previstas no desenho experimental.

No nível de modelagem, o pipeline privilegia atributos numéricos e aplica rotinas de sanitização para valores ausentes ou infinitos, conforme implementado nos módulos de treino e inferência em `src/twodaef/`. A seleção efetiva de atributos não é fixa para todo o sistema: ela é definida por listas de colunas para o gatekeeper (`configs/cols/`) e por pools de atributos candidatos para especialistas (`artifacts/feature_pools/`).

## 4.4 Configuração experimental

A configuração experimental segue a organização do repositório:

1. O **gatekeeper** é treinado com conjunto de atributos explícito em arquivos de configuração.
2. Os **especialistas** são treinados por classe com busca entre combinações de famílias de modelos e conjuntos de atributos candidatos.
3. O mapeamento classe -> especialista é persistido em `configs/mappings/`, garantindo rastreabilidade do especialista selecionado em cada classe.
4. A inferência em dois estágios produz predições finais e registra informações auxiliares de decisão e latência por estágio.
5. A avaliação consolida métricas e figuras em `reports/`, de acordo com o plano experimental descrito em `docs/experiment_plan.md` e `docs/paper_experimental_plan.md`.

Para reprodutibilidade, o projeto adota parâmetros controlados nos scripts (por exemplo, sementes fixas quando aplicável) e mantém separação entre código, configuração e artefatos gerados.

## 4.5 Baselines e comparações coerentes com o projeto

As comparações consideradas nesta pesquisa são restritas ao que está explicitamente suportado no repositório:

- **Baseline global XGBoost** para o cenário robusto do CIC (`scripts/baseline_xgb_cic_robust.py`), sem decomposição em dois estágios.
- **Comparação por seleção de atributos** no CIC robusto, contrapondo configuração com pool reduzido e configuração com conjunto amplo de atributos (`scripts/make_feature_pool_cic_robust.py` e `scripts/make_feature_pool_cic_robust_all.py`).
- **Comparação entre famílias de modelos dos especialistas** (LGBM, XGB e CatBoost), conforme plano documentado em `reports/cic/EXPERIMENTOS_BOOSTERS.md`.

Essas comparações são tratadas como parte do desenho experimental e não implicam, por si, conclusão de superioridade de qualquer abordagem antes da análise de resultados.

## 4.6 Métricas de avaliação

As métricas adotadas refletem critérios tradicionais de avaliação em IDS e os artefatos efetivamente gerados pelo projeto:

- **Recall** da classe de ataque;
- **Precision** da classe de ataque;
- **F1-score** por classe e **F1-macro**;
- **Acurácia** global;
- **Matriz de confusão** em valores absolutos (TP, FP, TN, FN);
- **Latência média de inferência** por estágio (gatekeeper e especialista) e latência total estimada por amostra.

## 4.7 Justificativa para a escolha das métricas

Em IDS, a ênfase em **recall da classe maliciosa** é metodologicamente justificada pelo maior custo operacional associado a falsos negativos, que correspondem a ataques não detectados. A **precision** é incluída para controlar o impacto de alarmes indevidos, importante para a operação prática de centros de monitoramento. O **F1-score** (por classe e macro) é utilizado como medida de equilíbrio entre recall e precision, especialmente útil em cenários com desbalanceamento.

A **matriz de confusão absoluta** complementa as métricas agregadas por permitir inspeção direta da distribuição de erros. Por fim, métricas de **latência de inferência** são incorporadas porque a viabilidade de um IDS não depende apenas de qualidade preditiva, mas também de custo computacional compatível com uso operacional.

## 5 Resultados

Esta seção apresenta exclusivamente os resultados disponíveis nos artefatos versionados do projeto, com base principal em `reports/` e suporte em relatórios de `docs/` quando necessário para completar informações de execução. Não são introduzidos valores externos aos arquivos do repositório.

## 5.1 Base de evidências utilizada

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

## 5.2 Métricas agregadas por cenário

A Tabela 1 consolida os valores agregados explicitamente presentes nos arquivos JSON de métricas.

**Tabela 1 — Métricas agregadas disponíveis nos artefatos versionados**

| Cenário | Arquivo-fonte | F1-macro | Acurácia | n |
|---|---|---:|---:|---:|
| CIC-IDS2018 (binário) | `reports/cic/metrics_again.json` | 1.000000 | 1.000000 | 100000 |
| UNSW-NB15 (binário, execução `unsw_bin`) | `reports/unsw_bin/metrics_again.json` | 0.890069 | 0.898432 | 175341 |
| UNSW-NB15 (binário, execução `unsw` legado) | `reports/unsw_bin/metrics_again_unsw_legacy.json` | 0.892938 | 0.900987 | 175341 |

Observa-se a coexistência de dois artefatos de métricas para o UNSW-NB15 (`unsw_bin` e `unsw` legado), com pequena variação nos valores agregados e caminhos de saída distintos (`outputs/unsw_bin/preds.csv` e `outputs/eval_unsw/preds.csv`).

## 5.3 Métricas por classe e matrizes de confusão

Para o experimento CIC, estão disponíveis as figuras `reports/cic/f1_per_class_cic.png` e `reports/cic/confusion_matrix_cic.png`. Para o experimento UNSW binário, estão disponíveis `reports/unsw_bin/f1_per_class_unsw.png` e `reports/unsw_bin/confusion_matrix_unsw.png`.

Esses arquivos registram visualmente a distribuição de desempenho por classe e os padrões de erro de classificação em cada cenário. No conjunto versionado atual, entretanto, os valores numéricos detalhados por classe (em formato tabular) e as contagens absolutas da matriz de confusão (TP, FP, TN, FN em arquivo estruturado) não estão disponibilizados diretamente em `reports/`.

## 5.4 Custo de inferência reportado

No relatório UNSW versionado em `reports/unsw_bin/RELATORIO_UNSW.md`, consta latência média de inferência total de aproximadamente **0.8776 ms** por amostra, com decomposição em estágio de gatekeeper (~**0.000038 ms**) e estágio especialista (~**0.877536 ms**).

Para o CIC, a síntese numérica de latência explícita está registrada em `docs/cic_eval_report.md` (execução `v0.1.0-cic-mvp`), com valor total aproximado de **0.0001 ms** por amostra (gatekeeper ~**0.00008 ms**, especialista ~**0.00000 ms**). No relatório `reports/cic/RELATORIO_CIC.md` (versão `v0.2.0-cic`), a ênfase está na descrição do pipeline e dos artefatos, sem tabela agregada específica de latência.

## 5.5 Consolidação inter-datasets

Os arquivos `reports/metrics_comparados.csv` e `reports/metrics_comparados.md` apresentam uma consolidação entre CIC-IDS2018 e UNSW-NB15 com os seguintes valores:

- UNSW-NB15: `f1_macro = 0.8929`, `accuracy = 0.9010`;
- CIC-IDS2018: `f1_macro = 1.0000`, `accuracy = 1.0000`.

Essa consolidação utiliza a execução UNSW identificada como `unsw` (legado), coerente com `metrics_again_unsw_legacy.json`.

## 5.6 Artefatos de interpretabilidade (XAI) disponíveis

No cenário CIC binário, o projeto contém consolidação SHAP em `reports/cic/xai/xai_shap_consolidado.csv` e resumo em `reports/cic/XAI_BRIEF.md`. Entre as variáveis com maior contribuição média absoluta (|SHAP| médio), destacam-se:

- Classe `Benign`: `dst_port` (0.0239138633), `fwd_seg_size_min` (0.0107793954), `bwd_pkts_s` (0.0026201308);
- Classe `Others`: `fwd_seg_size_min` (0.0217095731), `init_fwd_win_byts` (0.0159603954), `flow_iat_max` (0.0062686020).

Esses valores são reportados como evidência descritiva de importância de atributos e não como métrica de desempenho classificatório.

## 5.7 Completude e limitações dos resultados versionados

Com base no estado atual do repositório, os resultados agregados (F1-macro, acurácia e tamanho amostral), as figuras de matriz de confusão/F1 por classe e os artefatos de XAI estão disponíveis e passíveis de rastreamento.

Por outro lado, alguns itens previstos em documentos de planejamento aparecem incompletos ou ausentes no material versionado: (i) não há, em `reports/`, arquivos tabulares de matriz de confusão absoluta por dataset (`TP`, `FP`, `TN`, `FN`) no formato JSON explicitado no plano experimental; (ii) os arquivos `preds.csv` referenciados nas métricas apontam para `outputs/`, pasta não versionada; e (iii) o relatório `reports/cic/EXPERIMENTOS_BOOSTERS.md` mantém a tabela comparativa entre famílias de modelos sem preenchimento de resultados.

## 6 Discussão

## 6.1 Interpretação dos resultados à luz da hipótese de IA

O ponto central desta discussão não é apenas verificar se o pipeline produziu classificações úteis em um cenário de detecção de intrusões, mas examinar em que medida os resultados observados são compatíveis com a hipótese metodológica do artigo: a de que uma arquitetura em dois estágios, baseada em triagem inicial e especialização posterior, pode constituir uma estratégia plausível de Inteligência Artificial para problemas complexos de classificação.

Sob essa perspectiva, os resultados disponíveis sugerem que a arquitetura é operacionalmente viável no recorte binário adotado e que sua efetividade depende do contexto de dados em que é aplicada. O desempenho agregado mais elevado no cenário CIC e o comportamento mais contido no cenário UNSW indicam, de forma coerente com a literatura de classificação complexa, que a adequação de uma arquitetura hierárquica não pode ser dissociada das características do espaço de atributos, da dificuldade intrínseca do dataset e da configuração concreta dos modelos selecionados. Assim, mais do que indicar uma superioridade uniforme da abordagem, os artefatos disponíveis reforçam a leitura de que a decomposição da decisão deve ser analisada como estratégia dependente do cenário de aplicação.

## 6.2 Métricas como instrumentos de análise da arquitetura

As métricas utilizadas neste estudo devem ser interpretadas não apenas como indicadores de desempenho final, mas como instrumentos para compreender o comportamento da arquitetura em dois estágios. Recall, precision, F1-score, acurácia e matriz de confusão fornecem visões complementares sobre como a decisão distribuída entre gatekeeper e especialistas se manifesta no estudo de caso escolhido.

No domínio de IDS, a ênfase em recall e precision permanece importante, sobretudo porque diferentes tipos de erro possuem custos distintos. Entretanto, no enquadramento do presente artigo, essas métricas interessam também por permitirem avaliar a adequação da estratégia de decomposição hierárquica. Uma arquitetura dessa natureza não deve ser julgada apenas por um valor agregado único, mas por sua capacidade de organizar a inferência, reduzir ambiguidades locais e produzir comportamento previsível frente a diferentes bases de dados. Nesse sentido, as figuras de matriz de confusão e F1 por classe disponíveis em `reports/` ampliam a leitura do problema, ainda que a ausência de tabelas estruturadas com TP, FP, TN e FN imponha limites à análise quantitativa mais fina.

## 6.3 Especialização e decomposição do problema de classificação

Do ponto de vista conceitual, os resultados são compatíveis com a hipótese de que a especialização pode funcionar como mecanismo de organização da inferência em problemas classificatórios difíceis. O gatekeeper atua como etapa inicial de triagem, enquanto os especialistas assumem a decisão refinada com base em configurações próprias de modelo e subconjuntos de atributos. Essa separação de papéis não elimina a complexidade do problema, mas a redistribui em etapas com funções distintas.

A relevância metodológica dessa escolha está no fato de que diferentes regiões do espaço de decisão podem exigir tratamentos distintos. Em vez de impor um único indutor para toda a variabilidade presente nos dados, a arquitetura permite associar subproblemas a combinações específicas entre modelo e representação de entrada. No caso deste trabalho, essa ideia é reforçada pelo uso explícito de *feature pools*, mapeamentos e artefatos de configuração no repositório, o que torna observável a ligação entre especialização classificatória e organização diferenciada da informação de entrada.

Ao mesmo tempo, os resultados não autorizam a concluir que a especialização será sempre vantajosa. O que eles permitem sustentar, de forma mais prudente, é que a decomposição hierárquica constitui uma estratégia plausível de IA aplicada, cujo valor analítico se torna particularmente visível em cenários nos quais o problema global apresenta heterogeneidade interna e demanda leitura mais granular do comportamento do sistema.

## 6.4 Trade-offs entre desempenho, custo e complexidade estrutural

Uma das implicações mais importantes dos artefatos analisados é que a arquitetura em dois estágios introduz trade-offs explícitos. O primeiro deles é o trade-off entre flexibilidade e simplicidade: ao permitir especialistas distintos, a arquitetura amplia a capacidade de adaptação local, mas em contrapartida aumenta o número de componentes, artefatos e relações a serem mantidos. O segundo é o trade-off entre desempenho e custo computacional: os registros de latência sugerem que o custo da inferência não é uniforme entre cenários e que a contribuição relativa do estágio especialista pode variar significativamente conforme a base considerada.

Esses resultados são relevantes porque reforçam que o valor de uma estratégia de IA não se resume ao melhor escore agregado. Em aplicações reais, a adequação de uma arquitetura depende também de sua governança experimental, de sua rastreabilidade e do custo de sua operação inferencial. No presente estudo, esse aspecto é particularmente evidente, já que o pipeline depende de conjuntos de atributos, especialistas persistidos, mapeamentos e relatórios intermediários. Assim, a discussão da abordagem precisa considerar simultaneamente capacidade preditiva, custo e complexidade estrutural.

## 6.5 Interpretabilidade como dimensão complementar

Os artefatos de XAI disponíveis para o cenário CIC sugerem que as decisões dos especialistas podem ser relacionadas a atributos observáveis de tráfego, como portas de destino, tamanhos de segmento e variáveis associadas à temporalidade e à interação de pacotes. Esse tipo de evidência é relevante porque reforça a ideia de que arquiteturas hierárquicas e especializadas podem ser inspecionadas de modo mais detalhado, favorecendo auditoria técnica do fluxo inferencial.

Ainda assim, a interpretabilidade deve ser entendida neste artigo como dimensão complementar. A identificação de atributos mais relevantes não equivale a explicação causal do fenômeno, nem substitui avaliação preditiva rigorosa. Seu valor está em ampliar a inteligibilidade da arquitetura e em oferecer um apoio adicional para examinar coerência e plausibilidade das decisões. Essa leitura é especialmente importante no contexto da IA aplicada, em que desempenho e interpretabilidade não devem ser tratados como sinônimos, mas como dimensões distintas e potencialmente complementares do sistema.

## 6.6 Limitações do estudo e do material experimental

As interpretações propostas nesta seção permanecem condicionadas às limitações objetivas do material disponível no repositório. Entre as principais restrições, destacam-se a ausência de matrizes de confusão absolutas em formato estruturado para todos os cenários, a ausência de arquivos completos de predição no versionamento atual, a coexistência de resultados agregados distintos para execuções relacionadas ao UNSW e a falta de consolidação plena de algumas comparações auxiliares entre famílias de especialistas.

Há ainda limitações associadas à padronização do ambiente experimental, uma vez que informações completas de hardware, configuração de execução e versionamento de certos artefatos não estão concentradas em um único relatório sintético. Essas restrições não anulam a utilidade do estudo, mas delimitam com clareza o alcance das inferências possíveis. Em especial, elas recomendam cautela ao extrapolar conclusões para além do recorte binário adotado e ao tratar os resultados como evidência definitiva de superioridade arquitetural.

## 6.7 Implicações para IA aplicada e para o estudo de caso IDS

No plano acadêmico, o trabalho contribui ao discutir a arquitetura em dois estágios como estratégia de IA aplicada para problemas complexos de classificação, em vez de tratá-la apenas como solução pontual de segurança. Essa mudança de foco permite interpretar o estudo de caso em IDS como ambiente de validação metodológica, no qual se observam desempenho, erro, custo e interpretabilidade sob uma mesma estrutura analítica.

No plano aplicado, os resultados indicam que a detecção de intrusões continua sendo um cenário fértil para investigar arquiteturas de decisão compostas, justamente por concentrar desafios como heterogeneidade de padrões, assimetria entre tipos de erro e necessidade de avaliação cuidadosa da inferência automatizada. Assim, embora o artigo não proponha uma solução universal para IDS, ele sugere que a decomposição hierárquica com especialistas merece consideração como linha legítima de investigação em IA aplicada, especialmente quando acompanhada por governança rigorosa de artefatos, métricas e relatórios.

## 7 Conclusão

Este artigo investigou uma estratégia de Inteligência Artificial aplicada a problemas complexos de classificação, baseada em uma arquitetura hierárquica em dois estágios composta por um mecanismo inicial de triagem (*gatekeeper*) e classificadores especialistas. A detecção de intrusões em redes foi adotada como estudo de caso, por oferecer um domínio aplicado no qual heterogeneidade de padrões, sobreposição entre classes, assimetria entre tipos de erro e necessidade de avaliação criteriosa tornam visível a dificuldade do problema classificatório.

Ao longo do trabalho, foram articulados quatro eixos complementares: a discussão conceitual de classificação complexa e arquiteturas hierárquicas na literatura recente; a formalização metodológica da arquitetura implementada no projeto; o delineamento experimental construído a partir dos artefatos efetivamente versionados; e a interpretação conservadora dos resultados disponíveis para os cenários considerados. Nesse sentido, o estudo não foi conduzido para demonstrar superioridade universal da proposta, mas para examinar se a decomposição hierárquica da decisão constitui uma estratégia metodologicamente plausível e analiticamente útil em um cenário aplicado realista.

Os resultados e a discussão sustentam, no escopo do material disponível, a viabilidade operacional da arquitetura em dois estágios e reforçam que seu valor não deve ser reduzido a um único indicador agregado de desempenho. O principal aporte do estudo está em mostrar que a combinação entre triagem inicial, especialização posterior, organização explícita de atributos e artefatos de roteamento permite examinar o comportamento do sistema sob múltiplas dimensões, incluindo desempenho preditivo, custo computacional, rastreabilidade experimental e interpretabilidade complementar. Assim, a contribuição central do artigo situa-se mais no campo da IA aplicada do que no de uma solução fechada de segurança: trata-se de discutir uma forma de organizar a inferência em problemas classificatórios complexos, utilizando IDS como ambiente de validação.

Do ponto de vista metodológico, o trabalho contribui ao reposicionar a arquitetura gatekeeper-especialistas como hipótese de decomposição da decisão, e não apenas como arranjo instrumental para um domínio específico. Do ponto de vista aplicado, contribui ao mostrar que a detecção de intrusões permanece um estudo de caso relevante para avaliar esse tipo de estratégia, justamente por concentrar desafios reais de classificação. Do ponto de vista analítico, o artigo também reforça a importância de tratar desempenho, custo e interpretabilidade como dimensões complementares, sem confundir explicação com validação empírica nem métricas agregadas com compreensão suficiente do comportamento do modelo.

As limitações do estudo permanecem diretamente vinculadas ao material experimental disponível no repositório. Entre elas, destacam-se a ausência de matrizes de confusão absolutas estruturadas para todos os cenários, a indisponibilidade de arquivos completos de predição no versionamento corrente, a coexistência de snapshots distintos para o cenário UNSW e a incompletude de algumas comparações auxiliares planejadas entre famílias de especialistas. Além disso, informações completas de ambiente experimental e configuração computacional ainda não se encontram consolidadas em um único relatório sintético. Essas restrições recomendam cautela ao extrapolar conclusões e delimitam o alcance do artigo como estudo metodológico aplicado, e não como prova definitiva de superioridade arquitetural.

Como trabalhos futuros, recomenda-se: consolidar um protocolo de avaliação mais uniforme entre datasets e execuções; padronizar e versionar artefatos de erro em nível mais fino; completar comparações com baselines e variações ablatórias da própria arquitetura; ampliar a análise para cenários multiclasses quando houver suporte experimental suficiente; e aprofundar o uso de XAI dentro de um protocolo comparável entre especialistas e bases distintas. Esses desdobramentos podem fortalecer tanto a robustez empírica da proposta quanto seu valor como contribuição para a investigação de arquiteturas hierárquicas em Inteligência Artificial aplicada.




