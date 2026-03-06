# 04 Methodology

## 4.1 Visão geral da abordagem

Este trabalho adota uma abordagem de classificação hierárquica para detecção de intrusões, implementada no projeto `twodaef` e organizada em dois estágios complementares: um classificador inicial de triagem (gatekeeper) e um conjunto de classificadores especialistas. A proposta é avaliada no contexto de IDS com formulação binária, mantendo aderência ao escopo do repositório e separando claramente a camada técnica (pipeline de dados, treino e inferência) da camada acadêmica de análise.

Do ponto de vista metodológico, a abordagem não pressupõe superioridade universal em relação a modelos globais únicos. O objetivo é investigar, sob protocolo reprodutível, se a decomposição da decisão em etapas sucessivas constitui uma alternativa plausível para lidar com dificuldades típicas de IDS, como heterogeneidade de padrões, sobreposição entre classes e sensibilidade a falsos negativos.

## 4.2 Arquitetura em dois estágios

A arquitetura empregada segue a lógica Gatekeeper -> Especialista, conforme implementação em `src/twodaef/`. No primeiro estágio, uma decisão de roteamento é produzida a partir de um conjunto reduzido de atributos. No segundo estágio, a amostra é encaminhada para um especialista associado à classe (ou ao grupo de classes) indicado pelo roteamento inicial.

Em termos conceituais, o primeiro estágio realiza uma filtragem de baixa complexidade; o segundo estágio concentra a discriminação mais fina. No recorte binário adotado neste artigo, a especialização pode ocorrer por classes diretamente (por exemplo, `Benign` e `Others`) ou por grupos funcionais equivalentes, preservando a mesma ideia de roteamento hierárquico.

## 4.3 Papel do gatekeeper

O gatekeeper é implementado como um classificador de árvore de decisão podada (`DecisionTreeClassifier`) no módulo `src/twodaef/gatekeeper.py`, com hiperparâmetros controláveis para profundidade e tamanho mínimo de folha. Sua função principal é produzir uma decisão inicial rápida e, com isso, definir qual especialista deverá ser acionado na etapa seguinte.

As variáveis de entrada do gatekeeper são explicitadas por arquivos de colunas em `configs/cols/`, o que mantém a seleção de atributos rastreável e separada do código-fonte. Essa decisão de projeto favorece reprodutibilidade e facilita a manutenção de versões por dataset/recorte sem alteração da lógica central do classificador.

## 4.4 Papel dos especialistas

Os especialistas são treinados por classe a partir do módulo `src/twodaef/specialists/train_specialists.py`. Para cada classe alvo, o pipeline avalia combinações entre famílias de modelos disponíveis (por exemplo, LightGBM, XGBoost, CatBoost e alternativas do scikit-learn) e conjuntos de atributos candidatos oriundos de um feature pool. A seleção do especialista segue critério de desempenho por classe (F1 da classe correspondente), com desempate por latência de inferência.

Esse desenho permite heterogeneidade entre especialistas: classes distintas podem ser atendidas por modelos e subconjuntos de atributos diferentes. Em vez de impor um único indutor para todo o espaço de dados, o método busca adequar a capacidade discriminativa ao comportamento específico de cada classe.

## 4.5 Fluxo geral do pipeline

O fluxo metodológico completo pode ser resumido em cinco etapas:

1. Preparação dos dados por scripts em `scripts/`, com geração de conjuntos de treino e avaliação/inferência e normalização de rótulos conforme o recorte.
2. Definição dos conjuntos de atributos do gatekeeper (`configs/cols/*.txt`) e dos feature pools dos especialistas (`artifacts/feature_pools/*.json`).
3. Treino dos componentes: gatekeeper e especialistas, com persistência dos modelos em `artifacts/trained_models/`.
4. Construção/uso do mapeamento de especialistas (`configs/mappings/*.json`), que associa classes a modelo, feature set e caminhos dos artefatos.
5. Inferência em dois estágios (`src/twodaef/infer/two_stage.py`), na qual cada amostra recebe predição final após roteamento inicial e decisão do especialista correspondente.

Na inferência, o sistema também registra informações auxiliares para auditoria metodológica, como predição do gatekeeper, especialista acionado e estimativas de latência por estágio. Esses elementos não constituem resultado em si, mas viabilizam rastreabilidade e análise posterior.

## 4.6 Conjuntos de atributos, mapeamentos e artefatos

O repositório adota separação explícita entre configuração e execução. Em particular:

- `configs/cols/` contém as listas de atributos do gatekeeper;
- `artifacts/feature_pools/` contém os conjuntos de atributos candidatos para especialistas;
- `configs/mappings/` contém mapeamentos de especialistas e, quando necessário, mapas de alinhamento de rótulos do gatekeeper;
- `artifacts/trained_models/` contém os modelos persistidos para gatekeeper e especialistas.

Essa organização favorece reprodutibilidade porque torna observáveis as decisões de modelagem (quais atributos, quais especialistas e quais mapeamentos) sem exigir alteração direta dos módulos principais do pipeline.

## 4.7 Justificativa metodológica da decomposição hierárquica

A escolha por decomposição hierárquica e especialização é justificada por três argumentos metodológicos no contexto de IDS. Primeiro, a triagem inicial reduz o espaço de decisão imediato e pode tornar o processo de inferência mais controlável em termos computacionais. Segundo, a especialização por classe permite que diferentes regiões do problema sejam tratadas por modelos e atributos potencialmente mais adequados às suas características. Terceiro, a estrutura em estágios facilita análise interpretável por componente, uma vez que decisões de roteamento e decisões finais podem ser examinadas separadamente.

Assim, a metodologia proposta busca equilibrar desempenho discriminativo, custo operacional e transparência analítica, sem antecipar conclusões empíricas antes da apresentação dos experimentos e resultados.
