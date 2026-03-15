# 07 Discussão

Esta seção interpreta os resultados apresentados na Seção 5 à luz da hipótese central do artigo: a de que uma arquitetura hierárquica em dois estágios, com gatekeeper e especialistas, constitui uma estratégia de IA plausível e analiticamente útil para problemas complexos de classificação. A discussão é conduzida em torno de quatro eixos: adequação da decomposição hierárquica, comportamento por classe, trade-offs de custo e granularidade, e limitações do estudo.

## 7.1 Adequação da decomposição hierárquica

Os resultados do CIC-IDS2018 mostram que a arquitetura GKS é operacionalmente viável: acurácia de 93,3% e F1-macro de 0,764 em um problema de 7 classes, com gatekeeper responsável por triagem inicial e especialistas dedicados a cada categoria de ataque. O sistema classificou corretamente a esmagadora maioria das amostras das classes bem representadas — Benign (F1=0,986), DDoS (F1=1,000) e DoS (F1=0,868) — demonstrando que a decomposição hierárquica organiza a decisão de forma coerente quando o volume de dados por subproblema é suficiente.

O resultado do UNSW-NB15 (F1-macro=0,866) reforça a consistência externa dessa observação. Em um dataset com distribuição e espaço de atributos distintos do CIC, a arquitetura manteve desempenho razoável sem mudança estrutural de pipeline, o que sugere que a lógica de decomposição não depende de um único dataset.

Esses resultados são coerentes com a literatura recente. Uddin et al. (2024) mostram que classificação hierárquica não melhora necessariamente o F1-macro global, mas reduz erros específicos de maior custo operacional — como falsos negativos. No presente estudo, a comparação principal mostra o GKS multiclasse com F1-macro inferior ao baseline binário; entretanto, quando suas predições no CIC são colapsadas para `Benign` vs. `Attack`, o desempenho sobe para F1-macro 0,9869 e acurácia 98,689%. Isso indica que a maior dificuldade da arquitetura não está em detectar intrusão, mas em separar subclasses de ataque com fronteiras sobrepostas.

## 7.2 Comportamento por classe e análise de erros

A análise por classe revela padrões que o F1-macro agregado não captura.

**Classes bem resolvidas:** DDoS (F1=1,000) e Benign (F1=0,986) são classificadas com alta precisão e alto suporte, o que lhes confere maior relevância analítica. `Others` também aparece com F1=1,000, mas seu suporte de apenas 1 amostra no holdout impede qualquer interpretação substantiva. DDoS é uma categoria com padrões estatisticamente distintos do tráfego benigno — alto volume de pacotes e baixa variabilidade relativa —, o que facilita a discriminação pelo especialista XGBoost.

**BruteForce como caso crítico:** O resultado mais preocupante é BruteForce com F1=0.649 e recall de 0.495. A análise da matriz de confusão revela que 5.044 amostras de BruteForce foram classificadas como DoS. Isso é analiticamente interessante: ataques de força bruta repetitivos (especialmente FTP e SSH patator) geram padrões de volume de pacotes similares a ataques DoS de baixa intensidade, tornando a fronteira de decisão genuinamente ambígua. Esse erro não reflete falha do pipeline — reflete dificuldade intrínseca do problema —, mas aponta para a necessidade de features mais discriminativas entre essas duas categorias em trabalhos futuros.

**Bot com recall reduzido:** O especialista Bot (XGBoost, F1_k=1.000 na validação interna) apresentou recall de 0.736 no holdout — queda considerável. Isso sugere que o conjunto de validação interna (20% do treino) não representou adequadamente a variabilidade dos padrões de Bot no holdout. A diferença pode decorrer de distribuição temporal: amostras de Bot concentradas no arquivo `03-02-2018.csv` podem ter características de tráfego levemente distintas das amostras usadas no treino. Esse é um exemplo de *covariate shift* temporal leve, comum em datasets de rede coletados em períodos distintos.

**Web com F1=0.000:** A ausência de amostras Web no holdout é consequência do protocolo de coleta proporcional por offset — as 928 amostras Web no treino foram todas coletadas dentro do range 0–30.000 das linhas dos arquivos de fevereiro 22 e 23, sem linhas adicionais disponíveis no range 30.000–40.000. Esse resultado deve ser lido como limitação de protocolo, não como incapacidade do especialista: o especialista Web (Random Forest, F1_k=0.901 na validação interna) demonstrou capacidade razoável na validação interna com os dados disponíveis.

## 7.3 Trade-off granularidade vs. desempenho agregado

A comparação entre GKS (F1-macro=0,764, 7 classes) e baseline XGBoost (F1-macro=0,976, 2 classes) ilustra com clareza o trade-off central da arquitetura hierárquica: granularidade de discriminação ao custo de F1-macro menor na formulação principal reportada.

O baseline resolve um problema mais simples — separar tráfego benigno de malicioso — e o resolve muito bem. O GKS resolve um problema fundamentalmente mais difícil — distinguir sete categorias, incluindo classes com pouquíssimos exemplos e fronteiras de decisão sobrepostas. A comparação direta de F1-macro entre os dois, isoladamente, seria metodologicamente pobre, porque pune o GKS por uma dificuldade que ele voluntariamente assume.

A comparação mais informativa é outra: dado um sistema que precisa não apenas detectar intrusões, mas também classificá-las por tipo para orientar resposta operacional diferenciada, qual é o custo de desempenho? O GKS mostra que esse custo é mensurável e localizado — concentrado em classes específicas (BruteForce, Bot, Web) — e não difuso por todo o espaço de decisão.

O colapso auxiliar do GKS para `Benign` vs. `Attack` ajuda a qualificar esse trade-off. Nesse cenário derivado, o pipeline atinge F1-macro 0,9869 e erra apenas 1.306 ataques como benignos no holdout do CIC. O resultado não substitui o baseline robusto, porque não usa o mesmo recorte de atributos, mas reforça que a maior parte da perda de desempenho está na taxonomia interna dos ataques, não na detecção de intrusão em sentido amplo.

## 7.4 Custo computacional e latência

A latência total de 21,79 ms/amostra no CIC é dominada pelo especialista (21,79 ms) com contribuição desprezível do gatekeeper (0,000056 ms). Esse resultado confirma o design esperado da arquitetura: o gatekeeper é deliberadamente uma árvore de decisão podada de baixíssimo custo, enquanto o especialista concentra quase todo o custo computacional da inferência.

Em valores absolutos, 21,79 ms/amostra não é adequado para inspeção de tráfego em tempo real de alta velocidade, mas o contexto do paper não é o de um sistema de produção — é o de uma avaliação de estratégia de IA em estudo de caso. A separação explícita de latência por estágio é, em si, uma contribuição analítica: ela torna observável onde o custo computacional se concentra e onde há margem para otimização.

No UNSW-NB15, a latência total estimada foi de 1,401 ms/amostra, novamente dominada pelo especialista (1,401 ms) e com contribuição residual do gatekeeper (0,000058 ms). Em termos absolutos, trata-se de custo bem inferior ao observado no CIC, o que sugere que a combinação entre espaço de atributos, classes e especialistas selecionados produz um cenário inferencial mais leve. Ainda assim, a ausência de padronização de hardware e de benchmark externo impede transformar essa diferença em conclusão generalizável de eficiência.

## 7.5 Interpretabilidade e papel do gatekeeper

O gatekeeper, por ser uma árvore de decisão podada, é intrinsecamente interpretável no sentido de Al e Sagiroglu (2025) — suas regras de roteamento podem ser inspecionadas diretamente sem necessidade de técnicas post-hoc. Essa propriedade é relevante em IDS porque o analista pode auditar quais atributos determinam o roteamento, identificar possíveis pontos de manipulação adversarial e ajustar a triagem sem requalificar os especialistas.

Para os especialistas, a interpretabilidade post-hoc via SHAP ou LIME permanece aplicável individualmente por classe — cada especialista processa um subproblema mais restrito que o problema global, o que potencialmente torna as explicações mais localmente coerentes. O repositório contém artefatos de XAI em `reports/cic/xai/` e `reports/cic/XAI_BRIEF.md`, mas eles correspondem a um snapshot binário legado do CIC (`Benign` vs. `Others`) e não ao cenário multiclasse principal desta campanha. Por isso, foram tratados apenas como material complementar de viabilidade, e não como evidência comparativa central do artigo.

## 7.6 Limitações

As principais limitações do estudo são:

**Protocolo de coleta por offset:** a estratégia de disjunção por offset de linhas garante ausência de leakage estrutural, mas não garante balanceamento de classes no holdout. A ausência de Web no holdout é o exemplo mais visível dessa limitação. Um protocolo de split estratificado por classe sobre o dataset completo produziria holdouts mais representativos, ao custo de maior complexidade de implementação e possível overlap temporal.

**Distribuição temporal não controlada:** os dados do CIC são organizados por data, e o protocolo de offset pode resultar em holdout com distribuição temporal diferente do treino. O episódio de Bot com queda de recall entre validação interna (F1_k=1.000) e holdout (recall=0.736) sugere que esse efeito está presente, embora não seja possível quantificá-lo sem rastreamento de timestamps por amostra.

**Classe Web com suporte insuficiente:** 928 amostras no treino é marginal para treinar um especialista robusto em Random Forest. Embora o F1_k interno seja 0.901, a ausência de amostras no holdout impede qualquer avaliação real dessa classe no cenário de avaliação. O mesmo vale, em menor grau, para `Others`, que aparece com apenas 4 amostras no treino e 1 no holdout.

**Baseline em formulação binária:** a comparação entre GKS (7 classes) e baseline (2 classes) é conceitualmente válida mas metricamente assimétrica. Uma comparação mais rigorosa exigiria um baseline multiclasse global com as mesmas 7 categorias, o que é tecnicamente viável mas fora do escopo desta campanha.

**UNSW-NB15 com split invertido:** o holdout UNSW (175.341 amostras) é mais que o dobro do treino (82.332 amostras), o que é incomum e potencialmente favorável às métricas de avaliação por ampliar a cobertura estatística. Esse split foi mantido por ser o split oficial dos criadores do dataset, amplamente adotado na literatura, mas deve ser declarado explicitamente.

**Ausência de XAI alinhado ao cenário principal:** embora o repositório contenha artefatos SHAP para um snapshot binário legado do CIC, não há um pacote de interpretabilidade equivalente e consolidado para o cenário multiclasse principal reportado neste artigo.
