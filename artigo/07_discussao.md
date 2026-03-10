# 07 Discussão

## 7.1 Interpretação dos resultados à luz da hipótese de IA

O ponto central desta discussão não é apenas verificar se o pipeline produziu classificações úteis em um cenário de detecção de intrusões, mas examinar em que medida os resultados observados são compatíveis com a hipótese metodológica do artigo: a de que uma arquitetura em dois estágios, baseada em triagem inicial e especialização posterior, pode constituir uma estratégia plausível de Inteligência Artificial para problemas complexos de classificação.

Sob essa perspectiva, os resultados disponíveis sugerem que a arquitetura é operacionalmente viável no recorte binário adotado e que sua efetividade depende do contexto de dados em que é aplicada. O desempenho agregado mais elevado no cenário CIC e o comportamento mais contido no cenário UNSW indicam, de forma coerente com a literatura de classificação complexa, que a adequação de uma arquitetura hierárquica não pode ser dissociada das características do espaço de atributos, da dificuldade intrínseca do dataset e da configuração concreta dos modelos selecionados. Assim, mais do que indicar uma superioridade uniforme da abordagem, os artefatos disponíveis reforçam a leitura de que a decomposição da decisão deve ser analisada como estratégia dependente do cenário de aplicação.

## 7.2 Métricas como instrumentos de análise da arquitetura

As métricas utilizadas neste estudo devem ser interpretadas não apenas como indicadores de desempenho final, mas como instrumentos para compreender o comportamento da arquitetura em dois estágios. Recall, precision, F1-score, acurácia e matriz de confusão fornecem visões complementares sobre como a decisão distribuída entre gatekeeper e especialistas se manifesta no estudo de caso escolhido.

No domínio de IDS, a ênfase em recall e precision permanece importante, sobretudo porque diferentes tipos de erro possuem custos distintos. Entretanto, no enquadramento do presente artigo, essas métricas interessam também por permitirem avaliar a adequação da estratégia de decomposição hierárquica. Uma arquitetura dessa natureza não deve ser julgada apenas por um valor agregado único, mas por sua capacidade de organizar a inferência, reduzir ambiguidades locais e produzir comportamento previsível frente a diferentes bases de dados. Nesse sentido, as figuras de matriz de confusão e F1 por classe disponíveis em `reports/` ampliam a leitura do problema, ainda que a ausência de tabelas estruturadas com TP, FP, TN e FN imponha limites à análise quantitativa mais fina.

## 7.3 Especialização e decomposição do problema de classificação

Do ponto de vista conceitual, os resultados são compatíveis com a hipótese de que a especialização pode funcionar como mecanismo de organização da inferência em problemas classificatórios difíceis. O gatekeeper atua como etapa inicial de triagem, enquanto os especialistas assumem a decisão refinada com base em configurações próprias de modelo e subconjuntos de atributos. Essa separação de papéis não elimina a complexidade do problema, mas a redistribui em etapas com funções distintas.

A relevância metodológica dessa escolha está no fato de que diferentes regiões do espaço de decisão podem exigir tratamentos distintos. Em vez de impor um único indutor para toda a variabilidade presente nos dados, a arquitetura permite associar subproblemas a combinações específicas entre modelo e representação de entrada. No caso deste trabalho, essa ideia é reforçada pelo uso explícito de *feature pools*, mapeamentos e artefatos de configuração no repositório, o que torna observável a ligação entre especialização classificatória e organização diferenciada da informação de entrada.

Ao mesmo tempo, os resultados não autorizam a concluir que a especialização será sempre vantajosa. O que eles permitem sustentar, de forma mais prudente, é que a decomposição hierárquica constitui uma estratégia plausível de IA aplicada, cujo valor analítico se torna particularmente visível em cenários nos quais o problema global apresenta heterogeneidade interna e demanda leitura mais granular do comportamento do sistema.

## 7.4 Trade-offs entre desempenho, custo e complexidade estrutural

Uma das implicações mais importantes dos artefatos analisados é que a arquitetura em dois estágios introduz trade-offs explícitos. O primeiro deles é o trade-off entre flexibilidade e simplicidade: ao permitir especialistas distintos, a arquitetura amplia a capacidade de adaptação local, mas em contrapartida aumenta o número de componentes, artefatos e relações a serem mantidos. O segundo é o trade-off entre desempenho e custo computacional: os registros de latência sugerem que o custo da inferência não é uniforme entre cenários e que a contribuição relativa do estágio especialista pode variar significativamente conforme a base considerada.

Esses resultados são relevantes porque reforçam que o valor de uma estratégia de IA não se resume ao melhor escore agregado. Em aplicações reais, a adequação de uma arquitetura depende também de sua governança experimental, de sua rastreabilidade e do custo de sua operação inferencial. No presente estudo, esse aspecto é particularmente evidente, já que o pipeline depende de conjuntos de atributos, especialistas persistidos, mapeamentos e relatórios intermediários. Assim, a discussão da abordagem precisa considerar simultaneamente capacidade preditiva, custo e complexidade estrutural.

## 7.5 Interpretabilidade como dimensão complementar

Os artefatos de XAI disponíveis para o cenário CIC sugerem que as decisões dos especialistas podem ser relacionadas a atributos observáveis de tráfego, como portas de destino, tamanhos de segmento e variáveis associadas à temporalidade e à interação de pacotes. Esse tipo de evidência é relevante porque reforça a ideia de que arquiteturas hierárquicas e especializadas podem ser inspecionadas de modo mais detalhado, favorecendo auditoria técnica do fluxo inferencial.

Ainda assim, a interpretabilidade deve ser entendida neste artigo como dimensão complementar. A identificação de atributos mais relevantes não equivale a explicação causal do fenômeno, nem substitui avaliação preditiva rigorosa. Seu valor está em ampliar a inteligibilidade da arquitetura e em oferecer um apoio adicional para examinar coerência e plausibilidade das decisões. Essa leitura é especialmente importante no contexto da IA aplicada, em que desempenho e interpretabilidade não devem ser tratados como sinônimos, mas como dimensões distintas e potencialmente complementares do sistema.

## 7.6 Limitações do estudo e do material experimental

As interpretações propostas nesta seção permanecem condicionadas às limitações objetivas do material disponível no repositório. Entre as principais restrições, destacam-se a ausência de matrizes de confusão absolutas em formato estruturado para todos os cenários, a ausência de arquivos completos de predição no versionamento atual, a coexistência de resultados agregados distintos para execuções relacionadas ao UNSW e a falta de consolidação plena de algumas comparações auxiliares entre famílias de especialistas.

Há ainda limitações associadas à padronização do ambiente experimental, uma vez que informações completas de hardware, configuração de execução e versionamento de certos artefatos não estão concentradas em um único relatório sintético. Essas restrições não anulam a utilidade do estudo, mas delimitam com clareza o alcance das inferências possíveis. Em especial, elas recomendam cautela ao extrapolar conclusões para além do recorte binário adotado e ao tratar os resultados como evidência definitiva de superioridade arquitetural.

## 7.7 Implicações para IA aplicada e para o estudo de caso IDS

No plano acadêmico, o trabalho contribui ao discutir a arquitetura em dois estágios como estratégia de IA aplicada para problemas complexos de classificação, em vez de tratá-la apenas como solução pontual de segurança. Essa mudança de foco permite interpretar o estudo de caso em IDS como ambiente de validação metodológica, no qual se observam desempenho, erro, custo e interpretabilidade sob uma mesma estrutura analítica.

No plano aplicado, os resultados indicam que a detecção de intrusões continua sendo um cenário fértil para investigar arquiteturas de decisão compostas, justamente por concentrar desafios como heterogeneidade de padrões, assimetria entre tipos de erro e necessidade de avaliação cuidadosa da inferência automatizada. Assim, embora o artigo não proponha uma solução universal para IDS, ele sugere que a decomposição hierárquica com especialistas merece consideração como linha legítima de investigação em IA aplicada, especialmente quando acompanhada por governança rigorosa de artefatos, métricas e relatórios.