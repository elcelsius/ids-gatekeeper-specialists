# 03 Related Works

## 3.1 IDS baseados em aprendizado de máquina

A literatura recente de detecção de intrusões com aprendizado de máquina mostra uma migração progressiva de abordagens estritamente assinadas para modelos orientados a dados, com ênfase em classificação supervisionada de tráfego de rede. No estudo *Evaluating machine learning-based intrusion detection systems with explainable AI: enhancing transparency and interpretability*, diferentes modelos de classificação são avaliados no UNSW-NB15, evidenciando a relevância de comparar algoritmos sob múltiplas métricas e não apenas por acurácia agregada. De modo complementar, o trabalho *Enhancing intrusion detection in wireless sensor networks using a Tabu search based optimized random forest* explora otimização de hiperparâmetros em Random Forest para cenários de WSN, reforçando que o desempenho de IDS depende de escolhas metodológicas de modelagem e ajuste, além da seleção do algoritmo base.

Em conjunto, esses estudos sustentam duas premissas importantes para este artigo: (i) IDS com ML devem ser avaliados com protocolo explícito e comparável; e (ii) desempenho preditivo e viabilidade operacional precisam ser tratados de forma integrada.

## 3.2 Ensembles, decisão em múltiplos estágios e estruturas hierárquicas

No eixo de ensembles, o artigo *A Novel Ensemble Framework for an Intelligent Intrusion Detection System* argumenta que um único classificador tende a ser insuficiente para capturar, com uniformidade, a diversidade de categorias de ataque. A estratégia proposta no trabalho combina classificadores a partir de sua capacidade de detecção por classe, aproximando-se da ideia de decisão especializada.

Na mesma direção, *LCCDE: A Decision-Based Ensemble Framework for Intrusion Detection in The Internet of Vehicles* formaliza um ensemble orientado por classe e por confiança de predição, no qual modelos líderes contribuem de maneira diferenciada para a decisão final. Embora aplicado ao contexto de Internet of Vehicles, esse desenho é conceitualmente relevante para arquiteturas hierárquicas em IDS, pois explicita a decomposição do problema em decisões parciais guiadas por especialização.

Essas contribuições dialogam com o recorte deste artigo ao indicar que estratégias de combinação e roteamento podem ser alternativas metodológicas plausíveis quando há heterogeneidade entre classes de intrusão.

## 3.3 Especialização por classe e seleção de atributos

A especialização por classe é frequentemente acompanhada por mecanismos de seleção de atributos, dado que diferentes ataques podem depender de subconjuntos distintos de variáveis. O trabalho *Bio-inspired Hybrid Feature Selection Model for Intrusion Detection* propõe uma estrutura em camadas para seleção de atributos com metaheurísticas (PSO, GWO e FFA), seguida por otimização adicional. Mesmo sem tratar diretamente de um gatekeeper de classificação, o estudo reforça a hipótese de que a etapa de seleção de atributos pode alterar de forma substantiva o comportamento de detectores de intrusão.

No contexto do presente projeto, essa discussão é particularmente pertinente, pois o pipeline utiliza pools de atributos e seleção por especialista, com artefatos explícitos de configuração. Assim, a literatura oferece suporte conceitual para a combinação entre especialização e engenharia de atributos, sem implicar que exista uma configuração universalmente ótima.

## 3.4 Interpretabilidade e XAI em IDS

A incorporação de técnicas de explicabilidade em IDS tem sido tratada como requisito para uso prático de modelos mais complexos. O estudo sobre avaliação de IDS com XAI citado anteriormente destaca o papel de métodos como SHAP e LIME na interpretação das decisões de modelos supervisionados. Em ambientes de segurança, esse aspecto é relevante não apenas para auditoria técnica, mas também para confiança operacional de analistas humanos.

Para este artigo, a literatura de XAI funciona como base para tratar interpretabilidade como dimensão complementar ao desempenho, evitando que avaliação de IDS se restrinja a métricas agregadas de classificação.

## 3.5 Síntese crítica e espaço de pesquisa

As referências disponíveis convergem para três pontos: (i) a utilidade de ML em IDS depende de desenho experimental rigoroso; (ii) ensembles e estratégias orientadas por classe são abordagens recorrentes para lidar com diversidade de ataques; e (iii) interpretabilidade tem papel crescente na validação de sistemas de detecção. Ao mesmo tempo, observa-se que os trabalhos analisados concentram-se em contextos específicos (por exemplo, IoV e WSN) ou em propostas de otimização pontual de modelos e atributos.

Nesse cenário, há espaço para uma investigação acadêmica que articule, de forma reprodutível, arquitetura em dois estágios (gatekeeper + especialistas), comparação com baselines coerentes e avaliação conjunta de desempenho e custo de inferência em IDS binário. É nesse espaço que o presente artigo se posiciona, sem pressupor superioridade a priori da abordagem proposta.
