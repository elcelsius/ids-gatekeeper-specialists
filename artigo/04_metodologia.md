# 04 Metodologia

## 4.1 Visão geral da abordagem

Este trabalho investiga uma estratégia de Inteligência Artificial voltada a problemas complexos de classificação, baseada na decomposição hierárquica da decisão em dois estágios complementares. A arquitetura analisada, implementada no ecossistema técnico do projeto `twodaef`, combina um classificador inicial de triagem, denominado *gatekeeper*, com classificadores especialistas responsáveis por decisões mais específicas em subespaços do problema. O domínio de detecção de intrusões é utilizado neste artigo como estudo de caso aplicado, e não como único centro conceitual da proposta.

Do ponto de vista metodológico, a abordagem parte da hipótese de que, em cenários com heterogeneidade de padrões, sobreposição entre classes e diferentes graus de dificuldade local de decisão, uma arquitetura em múltiplas etapas pode constituir alternativa plausível à adoção de um único classificador global. O objetivo, portanto, não é pressupor superioridade universal da estratégia hierárquica, mas examinar se a decomposição do processo inferencial favorece uma organização mais estruturada da decisão, com potencial para análise mais rica de desempenho, erro, custo computacional e interpretabilidade.

## 4.2 Arquitetura em dois estágios

A arquitetura empregada segue a lógica **Gatekeeper → Especialistas**, conforme implementada em `src/twodaef/`. No primeiro estágio, uma decisão inicial de triagem é produzida a partir de um conjunto mais enxuto de atributos, com o propósito de identificar a região do problema ou o grupo funcional ao qual a amostra parece pertencer. No segundo estágio, a amostra é encaminhada para um especialista associado ao encaminhamento definido na etapa anterior, onde ocorre a decisão mais refinada.

Em termos conceituais, o primeiro estágio atua como mecanismo de organização do espaço de decisão, enquanto o segundo concentra a discriminação mais específica. No recorte binário adotado neste artigo, essa especialização permanece metodologicamente relevante, pois mesmo uma formulação com duas classes pode se beneficiar de etapas distintas de triagem e refinamento, sobretudo quando o objetivo é observar o comportamento da arquitetura em um cenário controlado e coerente com os artefatos efetivamente disponíveis no projeto.

## 4.3 Papel do gatekeeper

O *gatekeeper* é implementado como um classificador de árvore de decisão podada (`DecisionTreeClassifier`), no módulo `src/twodaef/gatekeeper.py`, com hiperparâmetros configuráveis para profundidade máxima e tamanho mínimo de folha. Sua função metodológica central é realizar uma triagem inicial de baixa complexidade computacional, produzindo a decisão de roteamento que define qual especialista será acionado na etapa seguinte.

As variáveis de entrada utilizadas pelo *gatekeeper* são mantidas em arquivos de configuração localizados em `configs/cols/`, o que separa explicitamente a seleção de atributos da lógica principal do código-fonte. Essa escolha favorece rastreabilidade, reprodutibilidade e flexibilidade experimental, ao permitir que diferentes recortes de atributos sejam avaliados sem necessidade de alteração estrutural da implementação.

## 4.4 Papel dos especialistas

Os especialistas são treinados por meio do módulo `src/twodaef/specialists/train_specialists.py`. Para cada classe ou grupo alvo, o pipeline considera combinações entre famílias de modelos disponíveis no projeto e subconjuntos candidatos de atributos definidos em *feature pools*. A seleção do especialista é feita com base no desempenho da classe correspondente, adotando F1 como critério principal e latência de inferência como critério de desempate quando necessário.

Esse desenho permite heterogeneidade entre especialistas, isto é, diferentes regiões do problema podem ser atendidas por modelos e representações de entrada distintas. Em vez de impor um único indutor para todo o espaço de dados, a metodologia procura adequar o mecanismo discriminativo às características particulares de cada subproblema. Essa é precisamente a dimensão de IA aplicada que interessa ao presente artigo: investigar se a especialização pode funcionar como estratégia de organização da inferência em cenários classificatórios complexos.

## 4.5 Fluxo geral do pipeline

O fluxo metodológico adotado no estudo pode ser resumido em cinco etapas principais:

1. preparação dos dados por meio dos scripts disponíveis em `scripts/`, com geração dos conjuntos de treino e avaliação/inferência e padronização dos rótulos de acordo com o recorte experimental;
2. definição dos atributos utilizados pelo *gatekeeper* (`configs/cols/*.txt`) e dos *feature pools* dos especialistas (`artifacts/feature_pools/*.json`);
3. treinamento dos componentes da arquitetura, com persistência dos modelos em `artifacts/trained_models/`;
4. construção e utilização dos mapeamentos de especialistas (`configs/mappings/*.json`), associando classes, modelos, conjuntos de atributos e caminhos dos artefatos;
5. execução da inferência em dois estágios (`src/twodaef/infer/two_stage.py`), em que cada amostra recebe uma decisão final após o roteamento inicial e a avaliação do especialista correspondente.

Durante a inferência, o sistema também pode registrar informações auxiliares, como a predição do *gatekeeper*, o especialista acionado e estimativas de latência por estágio. Esses elementos não constituem, por si só, resultado experimental conclusivo, mas ampliam a rastreabilidade do processo inferencial e fornecem subsídios para análise posterior da arquitetura.

## 4.6 Conjuntos de atributos, mapeamentos e artefatos

O repositório adota uma separação explícita entre configuração, treinamento e execução. Em particular:

- `configs/cols/` contém as listas de atributos utilizadas pelo *gatekeeper*;
- `artifacts/feature_pools/` reúne os conjuntos de atributos candidatos para os especialistas;
- `configs/mappings/` armazena os mapeamentos de especialistas e, quando aplicável, os alinhamentos de rótulos necessários ao processo de roteamento;
- `artifacts/trained_models/` concentra os modelos persistidos do *gatekeeper* e dos especialistas.

Essa organização é metodologicamente importante porque torna observáveis as decisões de modelagem adotadas ao longo do pipeline. Assim, escolhas relativas a atributos, roteamento e especialização não ficam implícitas apenas no código, mas passam a existir também como artefatos auditáveis, o que reforça a reprodutibilidade do estudo.

## 4.7 Justificativa metodológica da decomposição hierárquica

A adoção de decomposição hierárquica e especialização é justificada, neste trabalho, por três argumentos principais. Primeiro, a triagem inicial permite reduzir a complexidade imediata da decisão, organizando o problema em etapas sucessivas e potencialmente mais controláveis. Segundo, a especialização por classe ou grupo funcional cria a possibilidade de empregar modelos e subconjuntos de atributos mais adequados a regiões específicas do espaço de dados. Terceiro, a estrutura em estágios favorece uma leitura analítica mais detalhada do comportamento do sistema, pois separa a decisão de roteamento da decisão final.

No estudo de caso em IDS, esses argumentos se tornam particularmente relevantes porque o domínio concentra características típicas de problemas complexos de classificação, como heterogeneidade de padrões, assimetria entre tipos de erro e necessidade de análise cuidadosa da decisão automatizada. Ainda assim, o interesse central do artigo permanece mais amplo: discutir a adequação de uma arquitetura hierárquica como estratégia de IA aplicada, utilizando a detecção de intrusões como ambiente de validação metodológica.

## 4.8 Considerações de escopo

A metodologia apresentada neste artigo está condicionada ao escopo experimental efetivamente sustentado pelos artefatos disponíveis no repositório. Por essa razão, a descrição da arquitetura e do pipeline foi construída de forma conservadora, preservando aderência à implementação real e evitando a inclusão de componentes, variações ou protocolos não documentados. Essa escolha é coerente com a proposta do trabalho, que privilegia uma análise metodologicamente rastreável da arquitetura em dois estágios, em vez de uma formulação excessivamente abrangente ou especulativa.