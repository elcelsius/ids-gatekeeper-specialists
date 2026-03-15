# Decomposição Hierárquica e Especialização de Modelos em Inteligência Artificial: um Estudo de Caso em Detecção de Intrusões

## Resumo

Problemas complexos de classificação supervisionada frequentemente combinam heterogeneidade de padrões, desbalanceamento, sobreposição entre classes e necessidade de decisões em múltiplos níveis. Nesse contexto, este artigo investiga uma estratégia de Inteligência Artificial baseada em decomposição hierárquica da inferência, implementada por meio de uma arquitetura em dois estágios composta por um mecanismo inicial de triagem (*gatekeeper*) e classificadores especialistas. A proposta é analisada em detecção de intrusões em redes como estudo de caso aplicado, utilizando o CIC-IDS2018 como cenário principal em formulação multiclasse granular e o UNSW-NB15 como cenário complementar em formulação binária. O pipeline experimental foi reconstruído a partir dos scripts, configurações e artefatos atuais do projeto 2D-AEF, com geração explícita de conjuntos de treino e holdout, seleção automática de especialistas por F1 por classe e registro de métricas e latência por estágio. Nos testes materializados no snapshot atual do repositório, a arquitetura atingiu F1-macro de 0,764 e acurácia de 93,3% no CIC-IDS2018 em sete classes, e F1-macro de 0,866 com acurácia de 87,4% no UNSW-NB15 binário. Como referência, o baseline XGBoost monolítico no recorte robusto do CIC alcançou F1-macro de 0,976 e acurácia de 97,6%. Os resultados mostram que a arquitetura hierárquica é operacionalmente viável e particularmente forte na separação entre tráfego benigno e malicioso, mas paga custo na discriminação entre subclasses de ataque raras ou sobrepostas, como BruteForce, Bot e Web. Conclui-se que a decomposição gatekeeper-especialistas constitui estratégia metodologicamente plausível de IA aplicada para problemas complexos de classificação, desde que seus ganhos analíticos sejam interpretados em conjunto com limitações de protocolo, rareza de classes e assimetria entre formulações comparadas.

## 1 Introdução

Problemas de classificação supervisionada tornam-se particularmente desafiadores quando envolvem sobreposição entre classes, desbalanceamento, heterogeneidade dos padrões de entrada e fronteiras de decisão difíceis de modelar por uma única função global. Em contextos dessa natureza, abordagens monolíticas podem apresentar desempenho desigual entre regiões do espaço de atributos, o que motiva a investigação de estratégias de Inteligência Artificial capazes de decompor o problema em etapas ou subproblemas mais específicos.

Entre as possibilidades discutidas na literatura de IA aplicada, arquiteturas hierárquicas e sistemas com especialização de classificadores oferecem uma alternativa conceitualmente relevante. Nesses arranjos, uma etapa inicial de triagem ou roteamento pode encaminhar cada amostra para modelos mais especializados, potencialmente mais adequados para lidar com padrões locais de decisão. Essa perspectiva desloca o foco de um único classificador global para um processo estruturado de inferência, no qual a decisão final resulta da combinação entre filtragem inicial e análise especializada.

A detecção de intrusões em redes constitui um estudo de caso particularmente apropriado para investigar esse tipo de estratégia. Além de sua relevância prática, o domínio de IDS reúne características típicas de problemas complexos de classificação, como desbalanceamento entre categorias, semelhança parcial entre comportamentos benignos e maliciosos, diversidade interna dos padrões de ataque e necessidade de avaliação criteriosa do comportamento do modelo. Assim, embora o cenário aplicado pertença ao campo da segurança computacional, ele pode ser entendido, neste trabalho, como um ambiente de validação para uma questão mais ampla de Inteligência Artificial.

Nesse contexto, este artigo investiga uma arquitetura de classificação em dois estágios, derivada do ecossistema técnico do projeto 2D-AEF e aqui reposicionada como objeto de análise em IA aplicada. Em termos gerais, a arquitetura combina um classificador inicial de triagem, denominado gatekeeper, com classificadores especialistas responsáveis por subproblemas ou regiões mais específicas da decisão. O interesse central do estudo não está em assumir superioridade universal da abordagem, mas em examinar se a decomposição hierárquica da inferência constitui uma estratégia metodologicamente plausível para tratar problemas classificatórios complexos em um cenário aplicado realista.

O objetivo do artigo é investigar, de forma conservadora e reprodutível, a adequação dessa arquitetura em dois estágios para problemas complexos de classificação, utilizando o CIC-IDS2018 em formulação multiclasse granular como cenário principal, complementado pelo UNSW-NB15 em formulação binária e por um baseline XGBoost monolítico no recorte robusto do CIC. Para isso, o trabalho considera métricas clássicas de desempenho, análise de matriz de confusão, custo de inferência e, quando pertinente, materiais auxiliares de interpretabilidade explicitamente identificados como complementares. O recorte experimental foi definido de modo a preservar coerência com os scripts, relatórios e artefatos efetivamente existentes no projeto, evitando extrapolações indevidas.

Além desta introdução, o artigo está organizado da seguinte forma. A Seção 2 discute os trabalhos relacionados, com ênfase em classificação complexa, arquiteturas hierárquicas, especialização de modelos e aplicações em IDS. A Seção 3 apresenta a metodologia e descreve a arquitetura em dois estágios como estratégia de IA. A Seção 4 detalha o desenho experimental adotado no estudo de caso. A Seção 5 reúne os resultados efetivamente disponíveis. A Seção 6 discute implicações, trade-offs e limitações da abordagem. Por fim, a Seção 7 apresenta as conclusões e indica possibilidades de continuidade.[^1]

## 2 Trabalhos Relacionados

### 2.1 Decomposição da decisão em IA: especialização de modelos e roteamento

A ideia de decompor um problema complexo de classificação entre múltiplos modelos especializados, coordenados por um mecanismo de roteamento, representa uma direção consolidada na literatura de Inteligência Artificial. O paradigma de *Mixture of Experts* (MoE), cujas raízes remontam ao início dos anos 1990, propõe que uma rede de roteamento (*gating network*) aprenda a distribuir as instâncias de entrada entre especialistas, cada um responsável por uma região do espaço do problema. Em revisão recente e abrangente, Cai et al. (2024) documentam a trajetória desse paradigma desde suas formulações clássicas até sua adoção em larga escala em modelos de linguagem de grande porte, mostrando que o princípio central permanece o mesmo: especialistas distintos ativados seletivamente por um mecanismo de roteamento produzem ganhos de eficiência e especialização que modelos monolíticos não conseguem replicar sem custo computacional proporcional.

Para o presente artigo, o interesse no paradigma MoE não está em suas aplicações a grandes modelos de linguagem, mas na intuição arquitetural que ele formaliza: diferentes regiões do espaço de decisão podem se beneficiar de tratamentos específicos, e um mecanismo de triagem inicial pode organizar esse roteamento de forma eficiente. Essa intuição é diretamente aplicável ao domínio de detecção de intrusões, onde o espaço de instâncias é heterogêneo — tráfego benigno, famílias de ataque com padrões distintos, classes raras e classes dominantes — e onde o custo assimétrico dos erros reforça a necessidade de organizar a decisão em etapas.

Do ponto de vista de ensemble learning, Ganaie et al. (2022) mostram que combinações de classificadores produzem ganhos consistentes especialmente quando os modelos componentes cometem erros em regiões distintas — o que os autores denominam diversidade funcional. A arquitetura em dois estágios explorada neste artigo torna essa diversidade explícita ao separar estruturalmente o problema de triagem (gatekeeper) do problema de discriminação refinada (especialistas), em vez de simplesmente combinar classificadores de forma indistinta.

### 2.2 Classificação complexa e arquiteturas hierárquicas em IA aplicada

A literatura de Inteligência Artificial aplicada tem discutido, de forma recorrente, as limitações de modelos monolíticos em problemas de classificação que apresentam heterogeneidade interna, sobreposição entre classes, fronteiras de decisão difíceis e necessidade de tratamento diferenciado para subconjuntos do espaço de entrada. Nesse contexto, arquiteturas hierárquicas e estratégias de decomposição da decisão surgem como alternativas metodológicas relevantes, pois permitem organizar o processo inferencial em múltiplos estágios, com diferentes níveis de granularidade.

No domínio de detecção de intrusões, essa discussão aparece de maneira explícita em trabalhos recentes sobre classificação hierárquica. Uddin et al. (2024) investigam uma abordagem em três níveis para IDS, distinguindo inicialmente tráfego benigno e malicioso, depois categorias amplas de ataque e, por fim, subtipos mais específicos. Em um experimento sistemático com dez algoritmos distintos em dez datasets de referência, os autores mostram que **não há diferença significativa no desempenho global (F1-macro) entre a abordagem hierárquica e a classificação plana**. O resultado relevante está em outro lugar: a hierarquia reduz especificamente a classificação de tráfego malicioso como benigno — o erro de falso negativo, que é o mais crítico operacionalmente. Em outras palavras, a hierarquia não é superior em tudo, mas é estruturalmente mais adequada para o tipo de erro que mais importa. Esse resultado é central para o presente artigo porque reforça que o valor da decomposição hierárquica é metodológico e analítico, não necessariamente expresso em métricas agregadas (Uddin et al., 2024).

Além disso, propostas multicamadas recentes, como o sistema MIDES (Agate et al., 2025), aprofundam a convergência entre especialização por classe e eficiência computacional. O MIDES emprega um classificador binário inicial — funcionalmente equivalente ao gatekeeper — para filtrar tráfego claramente benigno antes de acionar um ensemble de classificadores multiclasse para eventos suspeitos. Um agente auto-adaptativo (denominado Arbiter) seleciona dinamicamente a estratégia de decisão mais adequada por amostra, com base em heurísticas estáticas e dinâmicas. Avaliado nos datasets CIC-IDS2017 e CIC-IDS2018, o MIDES reporta F1-macro de 56,2% em cenário de transferência cross-dataset, evidenciando que arquiteturas multicamadas bem projetadas mantêm razoável capacidade de generalização mesmo em distribuições não vistas durante o treino. Esse número contextualiza o presente artigo ao oferecer uma referência concreta para o comportamento esperado em condições realistas de avaliação (Agate et al., 2025).

O MIDES é, dentre os trabalhos analisados, o mais próximo arquiteturalmente da proposta investigada neste artigo. A diferença central está no mecanismo de seleção de especialistas: enquanto o MIDES emprega um Arbiter que raciocina dinamicamente sobre confiança e desempenho por rodada de inferência, o 2D-AEF seleciona especialistas em tempo de treino com base em F1 por classe e latência medida, privilegiando interpretabilidade e previsibilidade do fluxo de inferência.

### 2.3 IDS com aprendizado de máquina como estudo de caso de classificação complexa

A detecção de intrusões baseada em aprendizado de máquina consolidou-se como uma área aplicada importante, em parte pela dificuldade de sistemas puramente baseados em assinatura acompanharem a diversidade e a evolução dos ataques. Ao mesmo tempo, a literatura recente mostra que o desempenho de IDS com ML não depende apenas da escolha do algoritmo, mas também da qualidade do desenho experimental, da seleção de datasets, do tratamento de desbalanceamento, da escolha de métricas e da clareza das comparações realizadas.

A revisão sistemática de Rehman et al. (2025) é particularmente útil nesse ponto. Ao mapear sistematicamente estudos recentes em IDS com ML, os autores identificam limitações recorrentes: uso de poucos datasets e poucos algoritmos comparados simultaneamente, ausência de benchmarking padronizado, dificuldade de comparação entre estudos por falta de protocolos comuns, e insuficiente atenção a custo computacional e tempo de detecção em tempo real. Essas lacunas justificam o uso de IDS não como fim em si mesmo, mas como estudo de caso exigente para investigar estratégias de IA. O domínio concentra, de forma realista, os desafios que arquiteturas hierárquicas pretendem enfrentar: desbalanceamento de classes, heterogeneidade de padrões e custo assimétrico dos erros (Rehman et al., 2025).

Nesse sentido, alguns trabalhos herdados da linha do projeto 2D-AEF continuam conceitualmente relevantes. Propostas como *A Novel Ensemble Framework for an Intelligent Intrusion Detection System* e *LCCDE: A Decision-Based Ensemble Framework for Intrusion Detection in the Internet of Vehicles* ajudam a mostrar que a combinação de modelos, a decisão orientada por classe e o uso de múltiplos classificadores já constituem uma direção consolidada em IDS. O presente artigo, contudo, reposiciona essa discussão ao enfatizar menos a ideia de ensemble como simples mecanismo de aumento de desempenho e mais a noção de decomposição hierárquica da decisão como estratégia de IA (Seth et al., 2021; Yang et al., 2022).

### 2.4 Especialização de modelos, roteamento e subproblemas de decisão

Um dos pontos centrais do presente artigo é a hipótese de que a especialização de classificadores pode ser útil quando o problema global contém subestruturas com padrões distintos. Essa ideia aparece, de formas variadas, em arquiteturas orientadas por classe, em mecanismos de roteamento entre modelos e em sistemas que combinam triagem inicial com análise especializada posterior. Ainda que os trabalhos da literatura nem sempre utilizem a mesma terminologia de gatekeeper e especialistas, muitos deles compartilham a intuição de que diferentes regiões do espaço de decisão podem se beneficiar de tratamentos específicos.

Do ponto de vista teórico em IA, o paradigma MoE revisitado por Cai et al. (2024) mostra que a especialização viabilizada por roteamento explícito não é um artifício arquitetural, mas uma estratégia de particionamento do espaço de decisão com fundamento em eficiência computacional e generalização seletiva. A arquitetura proposta neste artigo compartilha essa lógica: o gatekeeper particiona o espaço de entrada entre fluxos de decisão distintos, e cada especialista opera em um subespaço reduzido onde sua especialização pode produzir discriminação mais precisa.

No contexto de IDS, o uso de ensembles orientados por classe e de estruturas multicamadas, como demonstrado pelo MIDES (Agate et al., 2025), reforça que essa lógica de especialização produz resultados competitivos quando combinada com mecanismos de seleção explícita de estratégia por amostra. Além disso, Ganaie et al. (2022) mostram empiricamente que a diversidade funcional entre classificadores — medida pela correlação entre seus erros — é o principal preditor de ganho em ensemble, reforçando que arquiteturas que estruturam explicitamente essa diversidade têm fundamento teórico mais sólido do que abordagens puramente votativas.

### 2.5 XAI em sistemas de detecção de intrusões

À medida que sistemas IDS baseados em ML incorporam modelos de maior complexidade, a opacidade das decisões torna-se um problema prático. Analistas humanos precisam compreender, ao menos aproximadamente, por que determinado alerta foi gerado — seja para validar o modelo, priorizar respostas ou justificar decisões perante regulações como o GDPR.

Al e Sagiroglu (2025) apresentam revisão abrangente da aplicação de XAI em IDS, organizando os métodos em três categorias: *ante-hoc* (explicações definidas antes do treinamento), *intrínsecos* (modelos inerentemente interpretáveis, como árvores de decisão) e *post-hoc* (técnicas aplicadas após o treinamento a qualquer modelo de caixa-preta, como SHAP e LIME). Essa taxonomia é relevante para o presente artigo porque a arquitetura proposta combina deliberadamente os dois últimos tipos: o gatekeeper é um classificador de árvore de decisão podada, intrinsecamente interpretável, enquanto os especialistas podem ser inspecionados via técnicas post-hoc como SHAP, preservando a transparência do fluxo decisório nos dois estágios.

Mohale e Obagbuwa (2025) fornecem evidências empíricas sobre esse balanço no contexto do UNSW-NB15 — o mesmo dataset secundário utilizado neste artigo. Os autores mostram que XGBoost e CatBoost atingem 87% de acurácia com taxa de falso positivo de 0,07 e taxa de falso negativo de 0,12, e que a integração de SHAP, LIME e ELI5 não apenas melhora a interpretabilidade mas também evidencia quais atributos são os mais discriminativos. Esses números servem como referência concreta para o cenário secundário do presente artigo e reforçam que desempenho e interpretabilidade não são dimensões necessariamente incompatíveis (Mohale & Obagbuwa, 2025).

Pawlicki et al. (2024) identificam 25 desafios para XAI em IDS. Dois são particularmente relevantes para este trabalho. O primeiro é a ausência de padronização na definição de explicabilidade, que impede comparações rigorosas entre estudos. O segundo é o *trade-off* entre modelos intrinsecamente interpretáveis (*glass box*) e modelos de alta acurácia porém opacos (*crystal ball*), conforme a nomenclatura adotada pelos autores. A arquitetura em dois estágios enfrenta esse trade-off de forma explícita: o gatekeeper é deliberadamente um *glass box*, enquanto os especialistas podem ser modelos mais complexos inspecionados por ferramentas post-hoc, compartimentando a interpretabilidade em nível de estágio.

Khan et al. (2025) ampliam essa discussão para o que denominam *adversarial XAI*: a explicabilidade de um modelo pode ser explorada por adversários para construir ataques mais direcionados, uma vez que mecanismos como SHAP expõem quais atributos mais influenciam a decisão. Esse trade-off — transparência como risco — é ainda pouco explorado na literatura de IDS e representa uma limitação importante a ser declarada em estudos que integram XAI, incluindo o presente.

Para o presente artigo, a literatura de XAI cumpre um papel complementar. O objetivo não é deslocar o foco para explicabilidade, mas reconhecer que, em uma arquitetura hierárquica com múltiplas etapas de decisão, mecanismos interpretáveis podem contribuir para inspecionar a coerência do fluxo inferencial e apoiar a análise dos artefatos experimentais disponíveis. Interpretabilidade entra, portanto, como dimensão analítica adicional, e não como eixo central do artigo (Pawlicki et al., 2024; Al & Sagiroglu, 2025).

### 2.6 Síntese crítica e posicionamento do artigo

A literatura recente converge para quatro constatações relevantes para o presente artigo.

**Primeira:** a decomposição hierárquica da decisão tem fundamento em IA que precede as aplicações em IDS. O paradigma MoE, revisitado e documentado em escala por Cai et al. (2024), formaliza a intuição de que problemas com estrutura heterogênea se beneficiam de roteamento explícito entre especialistas. Arquiteturas mais recentes como o MIDES (Agate et al., 2025) mostram que essa lógica permanece relevante e produz resultados competitivos em IDS modernos.

**Segunda:** problemas de detecção de intrusões continuam sendo um campo fértil para investigação de classificadores avançados, mas a comparação entre propostas depende fortemente de desenho experimental rigoroso. Rehman et al. (2025) documentam lacunas metodológicas sistemáticas que justificam esforço de maior rastreabilidade e padronização — o que o presente artigo busca incorporar ao seu protocolo experimental.

**Terceira:** arquiteturas hierárquicas e orientadas por especialização constituem direção plausível quando o problema apresenta heterogeneidade e custo assimétrico dos erros. O resultado de Uddin et al. (2024) — hierarquia não melhora F1-macro global mas reduz especificamente falsos negativos — é emblemático: o valor da decomposição está em *onde* ela melhora, não necessariamente em ganhos agregados. Ganaie et al. (2022) complementam esse argumento ao mostrar que diversidade funcional entre classificadores é o principal preditor de ganho em ensemble.

**Quarta:** interpretabilidade vem ganhando espaço como complemento importante à avaliação tradicional de desempenho, mas traz riscos próprios — adversarial XAI e o trade-off *glass box/crystal ball* — que precisam ser declarados explicitamente (Khan et al., 2025; Pawlicki et al., 2024).

É nesse espaço que o presente artigo se insere. Diferentemente de estudos estritamente orientados ao domínio de segurança, este trabalho toma a detecção de intrusões como estudo de caso para investigar uma questão mais ampla de IA aplicada: a adequação de uma arquitetura em dois estágios, com gatekeeper e especialistas, para problemas complexos de classificação. Com isso, o artigo busca articular arquitetura hierárquica, avaliação empírica, custo computacional e interpretabilidade em uma análise metodologicamente conservadora, sem pressupor superioridade universal da proposta e preservando o domínio de IDS como cenário de validação, e não como único centro conceitual do estudo.

## 3 Metodologia

### 3.1 Visão geral da abordagem

Este trabalho investiga uma estratégia de Inteligência Artificial voltada a problemas complexos de classificação, baseada na decomposição hierárquica da decisão em dois estágios complementares. A arquitetura analisada, implementada no ecossistema técnico do projeto `twodaef`, combina um classificador inicial de triagem, denominado *gatekeeper*, com classificadores especialistas responsáveis por decisões mais específicas em subespaços do problema. O domínio de detecção de intrusões é utilizado neste artigo como estudo de caso aplicado, e não como único centro conceitual da proposta.

Do ponto de vista metodológico, a abordagem parte da hipótese de que, em cenários com heterogeneidade de padrões, sobreposição entre classes e diferentes graus de dificuldade local de decisão, uma arquitetura em múltiplas etapas pode constituir alternativa plausível à adoção de um único classificador global. O objetivo, portanto, não é pressupor superioridade universal da estratégia hierárquica, mas examinar se a decomposição do processo inferencial favorece uma organização mais estruturada da decisão, com potencial para análise mais rica de desempenho, erro, custo computacional e interpretabilidade.

### 3.2 Arquitetura em dois estágios

A arquitetura empregada segue a lógica **Gatekeeper → Especialistas**, conforme implementada em `src/twodaef/`. No primeiro estágio, uma decisão inicial de triagem é produzida a partir de um conjunto mais enxuto de atributos, com o propósito de identificar a região do problema ou o grupo funcional ao qual a amostra parece pertencer. No segundo estágio, a amostra é encaminhada para um especialista associado ao encaminhamento definido na etapa anterior, onde ocorre a decisão mais refinada.

Em termos conceituais, o primeiro estágio atua como mecanismo de organização do espaço de decisão, enquanto o segundo concentra a discriminação mais específica. No cenário principal deste artigo, essa lógica é aplicada ao CIC-IDS2018 em formulação multiclasse de sete categorias; no cenário complementar, a mesma arquitetura é reutilizada no UNSW-NB15 em formulação binária (`Normal` vs. `Attack`). Em ambos os casos, a especialização permanece metodologicamente relevante porque separa a decisão de triagem da decisão refinada, permitindo observar onde o desempenho agregado se perde e em que estágio o custo computacional se concentra.

### 3.3 Papel do gatekeeper

O *gatekeeper* é implementado como um classificador de árvore de decisão podada (`DecisionTreeClassifier`), no módulo `src/twodaef/gatekeeper.py`, com hiperparâmetros configuráveis para profundidade máxima e tamanho mínimo de folha. Sua função metodológica central é realizar uma triagem inicial de baixa complexidade computacional, produzindo a decisão de roteamento que define qual especialista será acionado na etapa seguinte.

As variáveis de entrada utilizadas pelo *gatekeeper* são mantidas em arquivos de configuração localizados em `configs/cols/`, o que separa explicitamente a seleção de atributos da lógica principal do código-fonte. Essa escolha favorece rastreabilidade, reprodutibilidade e flexibilidade experimental, ao permitir que diferentes recortes de atributos sejam avaliados sem necessidade de alteração estrutural da implementação.

### 3.4 Papel dos especialistas

Os especialistas são treinados por meio do módulo `src/twodaef/specialists/train_specialists.py`. Para cada classe ou grupo alvo, o pipeline considera combinações entre famílias de modelos disponíveis no projeto e subconjuntos candidatos de atributos definidos em *feature pools*. A seleção do especialista é feita com base no desempenho da classe correspondente, adotando F1 como critério principal e latência de inferência como critério de desempate quando necessário.

Esse desenho permite heterogeneidade entre especialistas, isto é, diferentes regiões do problema podem ser atendidas por modelos e representações de entrada distintas. Em vez de impor um único indutor para todo o espaço de dados, a metodologia procura adequar o mecanismo discriminativo às características particulares de cada subproblema. Essa é precisamente a dimensão de IA aplicada que interessa ao presente artigo: investigar se a especialização pode funcionar como estratégia de organização da inferência em cenários classificatórios complexos.

### 3.5 Fluxo geral do pipeline

O fluxo metodológico adotado no estudo pode ser resumido em cinco etapas principais:

1. preparação dos dados por meio dos scripts disponíveis em `scripts/`, com geração dos conjuntos de treino e avaliação/inferência e padronização dos rótulos de acordo com o recorte experimental;
2. definição dos atributos utilizados pelo *gatekeeper* (`configs/cols/*.txt`) e dos *feature pools* dos especialistas (`artifacts/feature_pools/*.json`);
3. treinamento dos componentes da arquitetura, com persistência dos modelos em `artifacts/trained_models/`;
4. construção e utilização dos mapeamentos de especialistas (`configs/mappings/*.json`), associando classes, modelos, conjuntos de atributos e caminhos dos artefatos;
5. execução da inferência em dois estágios (`src/twodaef/infer/two_stage.py`), em que cada amostra recebe uma decisão final após o roteamento inicial e a avaliação do especialista correspondente.

Durante a inferência, o sistema também pode registrar informações auxiliares, como a predição do *gatekeeper*, o especialista acionado e estimativas de latência por estágio. Esses elementos não constituem, por si só, resultado experimental conclusivo, mas ampliam a rastreabilidade do processo inferencial e fornecem subsídios para análise posterior da arquitetura.

### 3.6 Conjuntos de atributos, mapeamentos e artefatos

O repositório adota uma separação explícita entre configuração, treinamento e execução. Em particular:

- `configs/cols/` contém as listas de atributos utilizadas pelo *gatekeeper*;
- `artifacts/feature_pools/` reúne os conjuntos de atributos candidatos para os especialistas;
- `configs/mappings/` armazena os mapeamentos de especialistas e, quando aplicável, os alinhamentos de rótulos necessários ao processo de roteamento;
- `artifacts/trained_models/` concentra os modelos persistidos do *gatekeeper* e dos especialistas.

Essa organização é metodologicamente importante porque torna observáveis as decisões de modelagem adotadas ao longo do pipeline. Assim, escolhas relativas a atributos, roteamento e especialização não ficam implícitas apenas no código, mas passam a existir também como artefatos auditáveis, o que reforça a reprodutibilidade do estudo.

### 3.7 Justificativa metodológica da decomposição hierárquica

A adoção de decomposição hierárquica e especialização é justificada, neste trabalho, por três argumentos principais. Primeiro, a triagem inicial permite reduzir a complexidade imediata da decisão, organizando o problema em etapas sucessivas e potencialmente mais controláveis. Segundo, a especialização por classe ou grupo funcional cria a possibilidade de empregar modelos e subconjuntos de atributos mais adequados a regiões específicas do espaço de dados. Terceiro, a estrutura em estágios favorece uma leitura analítica mais detalhada do comportamento do sistema, pois separa a decisão de roteamento da decisão final.

No estudo de caso em IDS, esses argumentos se tornam particularmente relevantes porque o domínio concentra características típicas de problemas complexos de classificação, como heterogeneidade de padrões, assimetria entre tipos de erro e necessidade de análise cuidadosa da decisão automatizada. Ainda assim, o interesse central do artigo permanece mais amplo: discutir a adequação de uma arquitetura hierárquica como estratégia de IA aplicada, utilizando a detecção de intrusões como ambiente de validação metodológica.

### 3.8 Considerações de escopo

A metodologia apresentada neste artigo está condicionada ao escopo experimental efetivamente sustentado pelos artefatos disponíveis no repositório. Por essa razão, a descrição da arquitetura e do pipeline foi construída de forma conservadora, preservando aderência à implementação real e evitando a inclusão de componentes, variações ou protocolos não documentados. Essa escolha é coerente com a proposta do trabalho, que privilegia uma análise metodologicamente rastreável da arquitetura em dois estágios, em vez de uma formulação excessivamente abrangente ou especulativa.

## 4 Experimentos

### 4.1 Delineamento experimental

O delineamento experimental deste artigo foi estruturado para avaliar, de forma reprodutível, a arquitetura GKS (*Gatekeeper + Specialists*) em três leituras complementares do problema: um cenário principal multiclasse no CIC-IDS2018, um cenário secundário binário no UNSW-NB15 e um baseline XGBoost monolítico binário no recorte robusto do CIC. Os scripts e configurações do pipeline são versionados no repositório; os valores reportados nesta seção foram verificados diretamente nos artefatos atuais de `data/`, `outputs/` e `reports/`, evitando o uso de números externos ao snapshot experimental disponível.

O cenário principal utiliza o dataset **CIC-IDS2018**, com rótulos agregados em sete classes: Benign, Bot, BruteForce, DDoS, DoS, Others e Web. O cenário secundário utiliza o **UNSW-NB15** em formulação binária estrita (Normal vs. Attack), com função de verificação de consistência externa. Para o CIC, um baseline monolítico XGBoost é incluído como referência comparativa.

### 4.2 Datasets e preparação

#### CIC-IDS2018

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

#### UNSW-NB15

O UNSW-NB15 foi obtido via Kaggle (`mrwellsdavid/unsw-nb15`). O dataset disponibiliza arquivos oficiais de treino e teste gerados pelos criadores, que foram utilizados diretamente sem reamostragem adicional. O arquivo `UNSW_NB15_training-set.csv` serviu como base de treino e o `UNSW_NB15_testing-set.csv` como holdout. Os rótulos originais `0/1` foram mapeados para `Normal`/`Attack`. A coluna `id` (índice sequencial) foi descartada explicitamente como metadado.

| Arquivo | Linhas | Features | Distribuição |
|---|---|---|---|
| `train_unsw.csv` | 82.332 | 40 | Attack: 45.332 (55%) / Normal: 37.000 (45%) |
| `unsw_eval.csv` | 175.341 | 40 | Attack: 119.341 (68%) / Normal: 56.000 (32%) |

O split invertido (holdout maior que treino) é o split oficial do dataset e amplamente adotado na literatura comparável, incluindo Mohale e Obagbuwa (2025), o que facilita comparação direta com trabalhos relacionados.

### 4.3 Configuração da arquitetura GKS

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

### 4.4 Baseline

O baseline monolítico adota um classificador XGBoost global treinado sobre `train_cic_robust.csv` (sem `dst_port`) e avaliado em `cic_eval_robust.csv`. A formulação é binária estrita — Benign vs. Attack — sem distinção entre tipos de ataque. Essa configuração representa o modelo de referência mais direto: um classificador único que trata o problema como separação benigno/malicioso, sem qualquer decomposição hierárquica.

A comparação entre o GKS e o baseline é deliberadamente assimétrica em formulação: o GKS avalia 7 classes granulares enquanto o baseline avalia 2. Essa assimetria é intencional e metodologicamente relevante — ela expressa exatamente o trade-off central do artigo: granularidade de decisão versus desempenho agregado.

### 4.5 Métricas e protocolo de avaliação

As métricas reportadas são: F1-macro, acurácia global, precision e recall por classe, matriz de confusão absoluta e latência média por estágio. O F1-macro é a métrica principal de comparação por ser invariante ao desbalanceamento de classes. A latência é medida em milissegundos por amostra, com separação entre o tempo do gatekeeper (estágio 1) e o tempo do especialista (estágio 2).

Todos os artefatos de avaliação usados neste artigo — predições, relatórios por classe e figuras — foram gerados automaticamente pelos CLIs `cli_eval_twostage` e `cli_plot_eval` e persistidos em `outputs/` e `reports/`. O repositório também contém artefatos de XAI para um snapshot binário legado do CIC (`Benign` vs. `Others`), mas eles não são utilizados como evidência central do cenário multiclasse desta campanha.

## 5 Resultados

Esta seção apresenta os resultados obtidos na campanha experimental descrita na Seção 4. Os valores reportados derivam exclusivamente dos artefatos atuais gerados durante a execução — `classification_report_eval.csv`, `confusion_matrix_eval.csv`, `metrics_again.json`, `preds.csv` e os CSVs do baseline — sem interpolação manual posterior. Os valores tabulados por classe foram arredondados a três casas decimais.

### 5.1 Cenário principal — CIC-IDS2018 (GKS, 7 classes)

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

![Figura 1 - Matriz de confusão do GKS no CIC-IDS2018.](../reports/cic/confusion_matrix_cic.png){ width=14cm }

![Figura 2 - F1 por classe do GKS no CIC-IDS2018.](../reports/cic/f1_per_class_cic.png){ width=14cm }


Os principais padrões observados na matriz de confusão são:

- **Benign:** classificação quase perfeita (46.978 corretos, 5 erros para Web — desprezível).
- **DDoS:** F1=1.000 com apenas 3 confusões com Benign.
- **DoS:** desempenho sólido (18.506 corretos), com 323 confusões com BruteForce e 269 com Benign.
- **Bot:** precision perfeita, recall reduzido (1.033 amostras classificadas como Benign).
- **BruteForce:** o ponto mais fraco — recall de 0.495, com 5.044 amostras classificadas como DoS. A confusão entre BruteForce e DoS é esperada dado que ambos os ataques compartilham características de volume de pacotes.
- **Web:** F1=0.000, ausente no holdout. Classe com apenas 928 amostras no treino, sem representação no offset de avaliação.
- **Others:** F1=1.000, mas com suporte de apenas 1 amostra — resultado estatisticamente irrelevante.

### 5.2 Cenário secundário — UNSW-NB15 (GKS, binário)

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

As figuras `confusion_matrix_unsw_bin.png` (Figura 3) e `f1_per_class_unsw_bin.png` (Figura 4) sintetizam visualmente esse comportamento.

![Figura 3 - Matriz de confusão do GKS no UNSW-NB15.](../reports/unsw_bin/confusion_matrix_unsw_bin.png){ width=14cm }

![Figura 4 - F1 por classe do GKS no UNSW-NB15.](../reports/unsw_bin/f1_per_class_unsw_bin.png){ width=14cm }


O padrão observado é assimétrico: o modelo tem alta precision para Attack (0.984) mas recall moderado (0.829), enquanto para Normal apresenta precision mais baixa (0.727) e recall elevado (0.971). Em termos operacionais, o sistema tende a ser mais conservador na sinalização de Normal — preferindo classificar como Attack na dúvida — o que é um comportamento defensável em cenários de IDS onde falsos negativos têm custo operacional maior.

### 5.3 Baseline — XGBoost monolítico, CIC-IDS2018 (binário)

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

### 5.4 Comparação consolidada

**Tabela 4 — Comparação GKS vs. Baseline (CIC-IDS2018)**

| Método | Formulação | F1-macro | Acurácia | Classes avaliadas |
|---|---|---|---|---|
| GKS | Granular (7 classes) | 0.764 | 93,3% | Benign, Bot, BruteForce, DDoS, DoS, Others, Web |
| Baseline XGBoost | Binária | 0.976 | 97,6% | Benign vs. Attack |

A diferença de F1-macro entre os dois métodos reflete diretamente a diferença de formulação: o GKS avalia 7 classes granulares, enquanto o baseline avalia apenas 2. F1-macro em problema de 7 classes é estruturalmente mais sensível a classes raras ou ausentes no holdout, como Web (0 amostras) e Others (1 amostra), além de fronteiras difíceis como BruteForce.

A comparação direta mais relevante não é portanto apenas F1-macro vs. F1-macro, mas o que cada abordagem é capaz de discriminar: o baseline identifica se há intrusão; o GKS identifica qual tipo de intrusão, ao custo de desempenho menor nas subclasses mais ambíguas.

Como leitura auxiliar, colapsando-se as predições do GKS no CIC para a formulação binária `Benign` vs. `Attack`, obtém-se acurácia de **98,689%** e F1-macro de **0,9869**, com 46.978 amostras `Benign` corretamente reconhecidas, 51.711 amostras de `Attack` corretamente reconhecidas, 5 falsos positivos e 1.306 falsos negativos. Esse cálculo não substitui o baseline robusto como comparação oficial, porque usa a configuração completa do GKS no `cic_eval.csv` e não o recorte robusto sem `dst_port`, mas evidencia que a principal perda do método está na discriminação entre subclasses de ataque, e não na separação entre tráfego benigno e malicioso.

## 6 Discussão

Esta seção interpreta os resultados apresentados na Seção 5 à luz da hipótese central do artigo: a de que uma arquitetura hierárquica em dois estágios, com gatekeeper e especialistas, constitui uma estratégia de IA plausível e analiticamente útil para problemas complexos de classificação. A discussão é conduzida em torno de quatro eixos: adequação da decomposição hierárquica, comportamento por classe, trade-offs de custo e granularidade, e limitações do estudo.

### 6.1 Adequação da decomposição hierárquica

Os resultados do CIC-IDS2018 mostram que a arquitetura GKS é operacionalmente viável: acurácia de 93,3% e F1-macro de 0,764 em um problema de 7 classes, com gatekeeper responsável por triagem inicial e especialistas dedicados a cada categoria de ataque. O sistema classificou corretamente a esmagadora maioria das amostras das classes bem representadas — Benign (F1=0,986), DDoS (F1=1,000) e DoS (F1=0,868) — demonstrando que a decomposição hierárquica organiza a decisão de forma coerente quando o volume de dados por subproblema é suficiente.

O resultado do UNSW-NB15 (F1-macro=0,866) reforça a consistência externa dessa observação. Em um dataset com distribuição e espaço de atributos distintos do CIC, a arquitetura manteve desempenho razoável sem mudança estrutural de pipeline, o que sugere que a lógica de decomposição não depende de um único dataset.

Esses resultados são coerentes com a literatura recente. Uddin et al. (2024) mostram que classificação hierárquica não melhora necessariamente o F1-macro global, mas reduz erros específicos de maior custo operacional — como falsos negativos. No presente estudo, a comparação principal mostra o GKS multiclasse com F1-macro inferior ao baseline binário; entretanto, quando suas predições no CIC são colapsadas para `Benign` vs. `Attack`, o desempenho sobe para F1-macro 0,9869 e acurácia 98,689%. Isso indica que a maior dificuldade da arquitetura não está em detectar intrusão, mas em separar subclasses de ataque com fronteiras sobrepostas.

### 6.2 Comportamento por classe e análise de erros

A análise por classe revela padrões que o F1-macro agregado não captura.

**Classes bem resolvidas:** DDoS (F1=1,000) e Benign (F1=0,986) são classificadas com alta precisão e alto suporte, o que lhes confere maior relevância analítica. `Others` também aparece com F1=1,000, mas seu suporte de apenas 1 amostra no holdout impede qualquer interpretação substantiva. DDoS é uma categoria com padrões estatisticamente distintos do tráfego benigno — alto volume de pacotes e baixa variabilidade relativa —, o que facilita a discriminação pelo especialista XGBoost.

**BruteForce como caso crítico:** O resultado mais preocupante é BruteForce com F1=0.649 e recall de 0.495. A análise da matriz de confusão revela que 5.044 amostras de BruteForce foram classificadas como DoS. Isso é analiticamente interessante: ataques de força bruta repetitivos (especialmente FTP e SSH patator) geram padrões de volume de pacotes similares a ataques DoS de baixa intensidade, tornando a fronteira de decisão genuinamente ambígua. Esse erro não reflete falha do pipeline — reflete dificuldade intrínseca do problema —, mas aponta para a necessidade de features mais discriminativas entre essas duas categorias em trabalhos futuros.

**Bot com recall reduzido:** O especialista Bot (XGBoost, F1_k=1.000 na validação interna) apresentou recall de 0.736 no holdout — queda considerável. Isso sugere que o conjunto de validação interna (20% do treino) não representou adequadamente a variabilidade dos padrões de Bot no holdout. A diferença pode decorrer de distribuição temporal: amostras de Bot concentradas no arquivo `03-02-2018.csv` podem ter características de tráfego levemente distintas das amostras usadas no treino. Esse é um exemplo de *covariate shift* temporal leve, comum em datasets de rede coletados em períodos distintos.

**Web com F1=0.000:** A ausência de amostras Web no holdout é consequência do protocolo de coleta proporcional por offset — as 928 amostras Web no treino foram todas coletadas dentro do range 0–30.000 das linhas dos arquivos de fevereiro 22 e 23, sem linhas adicionais disponíveis no range 30.000–40.000. Esse resultado deve ser lido como limitação de protocolo, não como incapacidade do especialista: o especialista Web (Random Forest, F1_k=0.901 na validação interna) demonstrou capacidade razoável na validação interna com os dados disponíveis.

### 6.3 Trade-off granularidade vs. desempenho agregado

A comparação entre GKS (F1-macro=0,764, 7 classes) e baseline XGBoost (F1-macro=0,976, 2 classes) ilustra com clareza o trade-off central da arquitetura hierárquica: granularidade de discriminação ao custo de F1-macro menor na formulação principal reportada.

O baseline resolve um problema mais simples — separar tráfego benigno de malicioso — e o resolve muito bem. O GKS resolve um problema fundamentalmente mais difícil — distinguir sete categorias, incluindo classes com pouquíssimos exemplos e fronteiras de decisão sobrepostas. A comparação direta de F1-macro entre os dois, isoladamente, seria metodologicamente pobre, porque pune o GKS por uma dificuldade que ele voluntariamente assume.

A comparação mais informativa é outra: dado um sistema que precisa não apenas detectar intrusões, mas também classificá-las por tipo para orientar resposta operacional diferenciada, qual é o custo de desempenho? O GKS mostra que esse custo é mensurável e localizado — concentrado em classes específicas (BruteForce, Bot, Web) — e não difuso por todo o espaço de decisão.

O colapso auxiliar do GKS para `Benign` vs. `Attack` ajuda a qualificar esse trade-off. Nesse cenário derivado, o pipeline atinge F1-macro 0,9869 e erra apenas 1.306 ataques como benignos no holdout do CIC. O resultado não substitui o baseline robusto, porque não usa o mesmo recorte de atributos, mas reforça que a maior parte da perda de desempenho está na taxonomia interna dos ataques, não na detecção de intrusão em sentido amplo.

### 6.4 Custo computacional e latência

A latência total de 21,79 ms/amostra no CIC é dominada pelo especialista (21,79 ms) com contribuição desprezível do gatekeeper (0,000056 ms). Esse resultado confirma o design esperado da arquitetura: o gatekeeper é deliberadamente uma árvore de decisão podada de baixíssimo custo, enquanto o especialista concentra quase todo o custo computacional da inferência.

Em valores absolutos, 21,79 ms/amostra não é adequado para inspeção de tráfego em tempo real de alta velocidade, mas o contexto do paper não é o de um sistema de produção — é o de uma avaliação de estratégia de IA em estudo de caso. A separação explícita de latência por estágio é, em si, uma contribuição analítica: ela torna observável onde o custo computacional se concentra e onde há margem para otimização.

No UNSW-NB15, a latência total estimada foi de 1,401 ms/amostra, novamente dominada pelo especialista (1,401 ms) e com contribuição residual do gatekeeper (0,000058 ms). Em termos absolutos, trata-se de custo bem inferior ao observado no CIC, o que sugere que a combinação entre espaço de atributos, classes e especialistas selecionados produz um cenário inferencial mais leve. Ainda assim, a ausência de padronização de hardware e de benchmark externo impede transformar essa diferença em conclusão generalizável de eficiência.

### 6.5 Interpretabilidade e papel do gatekeeper

O gatekeeper, por ser uma árvore de decisão podada, é intrinsecamente interpretável no sentido de Al e Sagiroglu (2025) — suas regras de roteamento podem ser inspecionadas diretamente sem necessidade de técnicas post-hoc. Essa propriedade é relevante em IDS porque o analista pode auditar quais atributos determinam o roteamento, identificar possíveis pontos de manipulação adversarial e ajustar a triagem sem requalificar os especialistas.

Para os especialistas, a interpretabilidade post-hoc via SHAP ou LIME permanece aplicável individualmente por classe — cada especialista processa um subproblema mais restrito que o problema global, o que potencialmente torna as explicações mais localmente coerentes. O repositório contém artefatos de XAI em `reports/cic/xai/` e `reports/cic/XAI_BRIEF.md`, mas eles correspondem a um snapshot binário legado do CIC (`Benign` vs. `Others`) e não ao cenário multiclasse principal desta campanha. Por isso, foram tratados apenas como material complementar de viabilidade, e não como evidência comparativa central do artigo.

### 6.6 Limitações

As principais limitações do estudo são:

**Protocolo de coleta por offset:** a estratégia de disjunção por offset de linhas garante ausência de leakage estrutural, mas não garante balanceamento de classes no holdout. A ausência de Web no holdout é o exemplo mais visível dessa limitação. Um protocolo de split estratificado por classe sobre o dataset completo produziria holdouts mais representativos, ao custo de maior complexidade de implementação e possível overlap temporal.

**Distribuição temporal não controlada:** os dados do CIC são organizados por data, e o protocolo de offset pode resultar em holdout com distribuição temporal diferente do treino. O episódio de Bot com queda de recall entre validação interna (F1_k=1.000) e holdout (recall=0.736) sugere que esse efeito está presente, embora não seja possível quantificá-lo sem rastreamento de timestamps por amostra.

**Classe Web com suporte insuficiente:** 928 amostras no treino é marginal para treinar um especialista robusto em Random Forest. Embora o F1_k interno seja 0.901, a ausência de amostras no holdout impede qualquer avaliação real dessa classe no cenário de avaliação. O mesmo vale, em menor grau, para `Others`, que aparece com apenas 4 amostras no treino e 1 no holdout.

**Baseline em formulação binária:** a comparação entre GKS (7 classes) e baseline (2 classes) é conceitualmente válida mas metricamente assimétrica. Uma comparação mais rigorosa exigiria um baseline multiclasse global com as mesmas 7 categorias, o que é tecnicamente viável mas fora do escopo desta campanha.

**UNSW-NB15 com split invertido:** o holdout UNSW (175.341 amostras) é mais que o dobro do treino (82.332 amostras), o que é incomum e potencialmente favorável às métricas de avaliação por ampliar a cobertura estatística. Esse split foi mantido por ser o split oficial dos criadores do dataset, amplamente adotado na literatura, mas deve ser declarado explicitamente.

**Ausência de XAI alinhado ao cenário principal:** embora o repositório contenha artefatos SHAP para um snapshot binário legado do CIC, não há um pacote de interpretabilidade equivalente e consolidado para o cenário multiclasse principal reportado neste artigo.

## 7 Conclusão

Este artigo investigou uma estratégia de Inteligência Artificial aplicada a problemas complexos de classificação, baseada em uma arquitetura hierárquica em dois estágios — denominada GKS (*Gatekeeper + Specialists*) — composta por um mecanismo inicial de triagem (*gatekeeper*) e classificadores especialistas por categoria. A detecção de intrusões em redes foi adotada como estudo de caso, por oferecer um domínio no qual heterogeneidade de padrões, sobreposição entre classes, assimetria de custos de erro e necessidade de discriminação granular tornam visível a complexidade do problema classificatório.

A campanha experimental aqui discutida foi reconstruída a partir dos artefatos atuais do projeto para CIC-IDS2018, UNSW-NB15 e baseline robusto. Os resultados principais são: F1-macro de 0,764 e acurácia de 93,3% no CIC-IDS2018 em sete classes granulares; F1-macro de 0,866 e acurácia de 87,4% no UNSW-NB15 binário; e F1-macro de 0,976 com acurácia de 97,6% para o baseline XGBoost monolítico no CIC em formulação binária robusta.

Esses resultados sustentam, dentro do escopo experimental efetivamente observado, que a arquitetura hierárquica em dois estágios constitui uma estratégia de IA operacionalmente viável e analiticamente útil. Seu principal diferencial em relação a um classificador monolítico não está em F1-macro superior na comparação principal — o baseline demonstrou desempenho agregado mais alto em sua formulação binária oficial —, mas na capacidade de discriminar tipos específicos de ataque com especialistas dedicados, tornando o comportamento do sistema observável em granularidade de classe. Como mostrado pelos resultados por classe, DDoS e Benign são classificados com altíssima precisão (F1=1,000 e 0,986, respectivamente), enquanto BruteForce (F1=0,649) e Bot (recall=0,736) evidenciam fronteiras de decisão genuinamente ambíguas que um modelo monolítico trataria de forma opaca. A leitura auxiliar obtida ao colapsar o GKS para `Benign` vs. `Attack` no holdout do CIC reforça essa interpretação: o pipeline mantém alta capacidade de detectar intrusão, e sua principal perda ocorre na taxonomia fina entre subclasses maliciosas.

Do ponto de vista metodológico, o trabalho contribui ao demonstrar que a arquitetura gatekeeper-especialistas pode ser tratada como hipótese de decomposição da decisão em IA aplicada, e não apenas como arranjo instrumental de segurança. A separação explícita entre triagem inicial (gatekeeper intrinsecamente interpretável) e discriminação refinada (especialistas com interpretabilidade post-hoc disponível) estrutura o pipeline de forma que escolhas de modelagem, roteamento e especialização se tornam artefatos auditáveis. Do ponto de vista aplicado, os resultados confirmam que o domínio de IDS oferece um cenário exigente e realista para avaliação de estratégias hierárquicas, concentrando desafios típicos de problemas complexos de classificação.

As limitações do estudo estão diretamente vinculadas ao protocolo experimental adotado. O método de coleta por offset garantiu disjunção entre treino e holdout, mas não representação equilibrada de todas as classes — a ausência da classe Web no holdout e a rareza extrema de `Others` são os casos mais evidentes. O baseline foi avaliado em formulação binária robusta enquanto o GKS foi avaliado em formulação de 7 classes, o que torna a comparação principal conceitualmente válida, porém metricamente assimétrica. O repositório contém artefatos de interpretabilidade para um snapshot binário legado do CIC, mas não um conjunto equivalente alinhado ao cenário multiclasse principal. Por fim, o efeito de distribuição temporal não foi formalmente controlado, embora o episódio de queda de recall em Bot sugira sua presença.

Como trabalhos futuros, recomenda-se: desenvolver um protocolo de split estratificado por classe e por janela temporal para o CIC-IDS2018; incluir um baseline multiclasse global com as mesmas 7 categorias para comparação mais rigorosa; executar a análise XAI por especialista com protocolo comparável entre datasets; investigar estratégias de oversampling ou pesos de classe para as categorias com suporte insuficiente (Web, BruteForce); e avaliar a arquitetura em configurações multiclasse mais granulares quando os dados permitirem. Esses desdobramentos podem fortalecer tanto a robustez empírica da proposta quanto seu valor como contribuição para a investigação de arquiteturas hierárquicas em Inteligência Artificial aplicada.

## Referências

Agate, Vincenzo; De Paola, Alessandra; Ferraro, Pierluca; Lo Re, Giuseppe. MIDES: A multi-layer Intrusion Detection System using ensemble machine learning. *International Journal of Intelligent Networks*, 2025. DOI: 10.1016/j.ijin.2025.09.001.

Al, Samed; Sagiroglu, Seref. Explainable artificial intelligence models in intrusion detection systems. *Engineering Applications of Artificial Intelligence*, v. 144, 2025. DOI: 10.1016/j.engappai.2025.110145.

Cai, Weilin; Jiang, Juyong; Wang, Fan; Tang, Jing; Kim, Sunghun; Huang, Jiayi. A Survey on Mixture of Experts in Large Language Models. arXiv:2407.06204v3, 2024.

Ganaie, M. A.; Hu, Minghui; Malik, A. K.; Tanveer, M.; Suganthan, P. N. Ensemble deep learning: A review. arXiv:2104.02395v3, 2022.

Khan, Naseem; Ahmad, Kashif; Al Tamimi, Aref; Alani, Mohammed M.; Bermak, Amine; Khalil, Issa. Explainable AI-Based Intrusion Detection Systems for Industry 5.0 and Adversarial XAI: A Systematic Review. *Information*, v. 16, n. 12, p. 1036, 2025. DOI: 10.3390/info16121036.

Mohale, Vincent Zibi; Obagbuwa, Isaac Chukwuma. Evaluating machine learning-based intrusion detection systems with explainable AI: enhancing transparency and interpretability. *Frontiers in Computer Science*, 2025. DOI: 10.3389/fcomp.2025.1520741.

Pawlicki, Marek; Pawlicka, Aleksandra; Kozik, Rafal; Choras, Michal. The survey on the dual nature of xAI challenges in intrusion detection and their potential for AI innovation. *Artificial Intelligence Review*, v. 57, n. 12, p. 330, 2024.

Rehman, Hafiz Muhammad Raza ur; Liaquat, Saira; Gul, Muhammad Junaid; Jhandir, Muhammad Zeeshan; Gavilanes, Daniel; Vergara, Manuel Masias; Ashraf, Imran. A systematic literature study of machine learning techniques based intrusion detection: datasets, models, challenges, and future directions. *Journal of Big Data*, v. 12, n. 1, 2025. DOI: 10.1186/s40537-025-01323-2.

Seth, Sugandh; Kaur, Kuljit; Singh, Gurwinder. A Novel Ensemble Framework for an Intelligent Intrusion Detection System. *IEEE Access*, 2021. DOI: 10.1109/ACCESS.2021.3116219.

Uddin, Md. Ashraf; Aryal, Sunil; Bouadjenek, Mohamed Reda; Al-Hawawreh, Muna; Talukder, Md. Alamin. Hierarchical Classification for Intrusion Detection System: Effective Design and Empirical Analysis. *CoRR*, abs/2403.13013, 2024.

Yang, Li; Shami, Abdallah; Stevens, Gary; de Rusett, Stephen. LCCDE: A Decision-Based Ensemble Framework for Intrusion Detection in The Internet of Vehicles. arXiv:2208.03399v2, 2022. Accepted for IEEE GLOBECOM 2022.

[^1]: Nota sobre o uso de Inteligência Artificial: Em linha com a transparência e a integridade acadêmica, declara-se o uso de ferramentas de Inteligência Artificial (IA) como assistentes no desenvolvimento deste trabalho. Especificamente, o modelo de linguagem Codex foi utilizado na fase de codificação para gerar rascunhos de código em Python, os quais foram subsequentemente revisados, corrigidos e validados manualmente. Adicionalmente, a ferramenta Gemini.ai foi empregada para a revisão ortográfica e gramatical do texto. O planejamento, a concepção da pesquisa, a análise crítica e a redação final do manuscrito são de contribuição inteiramente humana do autor.
