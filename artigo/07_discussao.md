# 07 Discussão

### 6.1 Adequação da decomposição hierárquica

Os resultados do CIC-IDS2018 mostram que a arquitetura GKS é operacionalmente viável: acurácia de 93,3% e F1-macro de 0,764 em um problema de 7 classes. O sistema classificou corretamente a esmagadora maioria das amostras das classes bem representadas — Benign (F1=0,986), DDoS (F1=1,000) e DoS (F1=0,868). O resultado do UNSW-NB15 (F1-macro=0,866) reforça a consistência externa dessa observação. Esses resultados são coerentes com Uddin et al. (2024), que mostram que classificação hierárquica não melhora necessariamente o F1-macro global, mas reduz erros específicos de maior custo operacional.

### 6.2 Comportamento por classe e análise de erros

A análise por classe revela padrões que o F1-macro agregado não captura. Classes bem resolvidas como DDoS (F1=1,000) e Benign (F1=0,986) têm padrões estatisticamente distintos que facilitam a discriminação. BruteForce com F1=0,649 e recall de 0,495 é o ponto mais crítico: 5.044 amostras foram classificadas como DoS, pois ataques de força bruta repetitivos geram padrões de volume de pacotes similares a ataques DoS de baixa intensidade. O especialista Bot apresentou queda de recall entre validação interna (F1_k=1,000) e holdout (recall=0,736), sugerindo covariate shift temporal leve — padrão comum em datasets de rede coletados em períodos distintos. A ausência de Web no holdout é limitação de protocolo, não incapacidade do especialista.

### 6.3 Trade-off granularidade vs. desempenho agregado

A comparação entre GKS (F1-macro=0,764, 7 classes) e baseline XGBoost (F1-macro=0,976, 2 classes) ilustra o trade-off central da arquitetura hierárquica: granularidade de discriminação ao custo de F1-macro menor. O baseline resolve um problema mais simples e o resolve muito bem. O GKS resolve um problema fundamentalmente mais difícil — distinguir sete categorias com fronteiras sobrepostas. Como leitura auxiliar, colapsando-se as predições do GKS no CIC para a formulação binária Benign vs. Attack, obtém-se acurácia de 98,7% e F1-macro de 0,987, evidenciando que a principal perda está na taxonomia interna dos ataques, não na detecção de intrusão em sentido amplo.

### 6.4 Custo computacional e latência

A latência total de 21,789 ms/amostra no CIC é dominada pelo especialista (21,789 ms) com contribuição desprezível do gatekeeper (0,000056 ms). Esse resultado confirma o design esperado: o gatekeeper é deliberadamente uma árvore de decisão podada de baixíssimo custo, enquanto o especialista concentra o custo computacional. No UNSW-NB15, a latência total de 1,401 ms/amostra é significativamente menor, o que sugere que a combinação entre espaço de atributos mais compacto (40 features vs. 78) e especialistas XGBoost binários produz um cenário inferencial mais leve.

### 6.5 Interpretabilidade e papel do gatekeeper

O gatekeeper, por ser uma árvore de decisão podada, é intrinsecamente interpretável no sentido de Al e Sagiroglu (2025) — suas regras de roteamento podem ser inspecionadas diretamente sem necessidade de técnicas post-hoc. Para os especialistas, a interpretabilidade post-hoc via SHAP permanece aplicável individualmente por classe. O repositório contém artefatos de XAI em reports/cic/xai/ para um snapshot binário legado do CIC, mas eles não correspondem ao cenário multiclasse principal e foram tratados apenas como material complementar histórico.

### 6.6 Limitações

As principais limitações do estudo são: (1) protocolo de coleta por offset garante disjunção mas não representação equilibrada de todas as classes — a ausência de Web no holdout é o exemplo mais visível; (2) distribuição temporal não controlada, com o episódio de queda de recall em Bot sugerindo covariate shift temporal; (3) classe Web com apenas 928 amostras no treino, marginal para treinar um especialista robusto; (4) baseline em formulação binária enquanto o GKS é avaliado em 7 classes, tornando a comparação de F1-macro metricamente assimétrica; (5) holdout UNSW com 175.341 amostras maior que o treino com 82.332, refletindo o split oficial dos criadores; e (6) ausência de XAI formal alinhado ao cenário multiclasse principal.
