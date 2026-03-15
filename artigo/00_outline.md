# Outline do Artigo 2 (Disciplina de IA)

## 1. Título provisório
**Decomposição Hierárquica e Especialização de Modelos em Inteligência Artificial: um Estudo de Caso em Detecção de Intrusões**

## 2. Tema
Investigação de uma estratégia de Inteligência Artificial para problemas complexos de classificação, baseada em uma arquitetura hierárquica em dois estágios, composta por um classificador inicial de triagem (gatekeeper) e classificadores especialistas, avaliada em detecção de intrusões em redes como estudo de caso aplicado.

## 3. Problema de pesquisa
Em problemas de classificação complexos, modelos monolíticos podem apresentar dificuldades diante de sobreposição entre classes, desbalanceamento, heterogeneidade dos padrões de entrada e necessidade de decisões mais granulares. Nesse contexto, surge a questão de se arquiteturas hierárquicas com especialização por subproblema podem constituir uma alternativa metodologicamente adequada para organizar o processo decisório.

Pergunta central: **uma arquitetura de classificação em dois estágios, com gatekeeper e especialistas, é uma estratégia adequada de Inteligência Artificial para lidar com problemas complexos de classificação, tomando a detecção de intrusões como estudo de caso?**

## 4. Hipótese
Uma estratégia de IA baseada em decomposição hierárquica da decisão, com triagem inicial e posterior especialização por subproblema, pode oferecer uma forma mais estruturada de tratar problemas complexos de classificação do que abordagens monolíticas, permitindo análise mais rica de desempenho, erro, custo computacional e interpretabilidade em um cenário aplicado como IDS.

## 5. Objetivo geral
Investigar, de forma metodologicamente conservadora e reprodutível, uma arquitetura de Inteligência Artificial em dois estágios, baseada em gatekeeper e especialistas, avaliando sua aplicação à detecção de intrusões como estudo de caso.

## 6. Objetivos específicos
- Caracterizar o problema de classificação complexa sob a perspectiva de IA aplicada.
- Descrever formalmente a arquitetura em dois estágios implementada no projeto, incluindo gatekeeper, especialistas e fluxo de decisão.
- Analisar o papel da decomposição hierárquica e da especialização de classificadores no processo de inferência.
- Avaliar a proposta em um cenário aplicado de detecção de intrusões, com base nos artefatos e relatórios efetivamente disponíveis no repositório.
- Comparar a arquitetura com baselines factíveis e coerentes com o projeto.
- Discutir métricas de desempenho, custo computacional e interpretabilidade de forma integrada e sem extrapolações indevidas.
- Explicitar limitações metodológicas, ameaças à validade e escopo de generalização do estudo.

## 7. Estudo de caso e recorte experimental
**Detecção de intrusões em redes, utilizando o CIC-IDS2018 em formulação multiclasse granular como estudo de caso principal.**

Justificativa do recorte:
- o domínio de IDS oferece um cenário realista de classificação complexa;
- o projeto já possui pipeline implementado, artefatos e relatórios compatíveis com esse cenário;
- o cenário multiclasse do CIC permite observar não apenas detecção de intrusão, mas também o custo analítico de discriminar subclasses de ataque com especialistas dedicados.

Estudo complementar já materializado:
- **UNSW-NB15 binário**, como apoio à análise de consistência externa, já sustentado pelos artefatos atuais em `reports/unsw_bin/` e `outputs/eval_unsw/`.

## 8. Possíveis baselines
- Modelo global/monolítico de referência, quando implementado de forma comparável no projeto.
- Baseline global XGBoost no recorte robusto do CIC, já sustentado pelos artefatos atuais e tratado como comparação oficial.
- Variações ablatórias da própria arquitetura, como uso de conjunto ampliado de atributos versus conjunto reduzido.
- Gatekeeper isolado, quando houver material experimental suficiente para essa comparação.

## 9. Métricas principais
- Recall.
- Precision.
- F1-score por classe e F1-macro.
- Acurácia global.
- Matriz de confusão absoluta.
- Latência média por amostra, quando efetivamente reportada.
- Evidências complementares de interpretabilidade, quando sustentadas pelos relatórios e artefatos existentes.

## 10. Diferencial do artigo
- Reposicionar a arquitetura em dois estágios como estratégia de IA para classificação complexa, e não apenas como solução aplicada de segurança.
- Discutir decomposição hierárquica da decisão e especialização de classificadores em um cenário aplicado real.
- Integrar desempenho, custo computacional e interpretabilidade em uma análise metodologicamente conservadora.
- Utilizar a detecção de intrusões como estudo de caso para avaliar a proposta, preservando IA como eixo principal do artigo.

## 11. Estrutura prevista das seções
1. Introdução  
Problemas complexos de classificação em IA, motivação para decomposição hierárquica e apresentação da detecção de intrusões como estudo de caso.

2. Trabalhos Relacionados  
Classificação com aprendizado de máquina, arquiteturas hierárquicas, ensembles, especialização de modelos e interpretabilidade, com referência ao domínio de IDS como aplicação.

3. Metodologia  
Descrição da arquitetura em dois estágios, do papel do gatekeeper, dos especialistas e do fluxo de decisão como estratégia de IA.

4. Desenho Experimental  
Caracterização do estudo de caso, datasets, recortes, baselines, protocolo de avaliação e critérios de reprodutibilidade.

5. Resultados  
Apresentação dos artefatos experimentais disponíveis, incluindo métricas, matrizes de confusão, custos e demais evidências efetivamente registradas.

6. Discussão  
Interpretação dos resultados à luz da hipótese de IA, discussão sobre especialização, trade-offs, limites e implicações para IA aplicada no estudo de caso.

7. Conclusão e Trabalhos Futuros  
Síntese da contribuição do estudo, limitações e possibilidades de aprofundamento metodológico e experimental.
