# 04 Metodologia

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
