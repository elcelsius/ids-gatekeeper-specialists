# 05 Experiments

## 5.1 Delineamento experimental

O delineamento experimental deste artigo foi estruturado para avaliar, de forma reprodutível, uma arquitetura de detecção de intrusões em dois estágios (gatekeeper + especialistas) no contexto de classificação binária. Em coerência com o escopo do repositório, a seção experimental descreve cenários, insumos e critérios de avaliação com base nos artefatos e documentos técnicos versionados, sem introduzir componentes externos ao projeto.

## 5.2 Dataset principal e enquadramento do problema

O dataset principal adotado no artigo é o **CIC-IDS2018**, na formulação binária com rótulos agregados para tráfego benigno e tráfego de ataque (ou classe equivalente). Esse recorte está alinhado ao material em `reports/cic/`, aos scripts de preparação disponíveis e ao objetivo do trabalho de discutir a viabilidade metodológica da arquitetura hierárquica em IDS.

Como cenário complementar de validade externa, o projeto também mantém avaliação binária com **UNSW-NB15**, documentada em `reports/unsw_bin/`. Entretanto, o foco analítico desta seção permanece no desenho experimental principal baseado no CIC.

Do ponto de vista de aprendizado supervisionado, o problema é modelado como classificação binária em dados tabulares de tráfego de rede, com atenção explícita a desafios usuais de IDS, como desbalanceamento de classes, sobreposição parcial de padrões entre tráfego benigno e malicioso e impacto operacional de erros do tipo falso negativo.

## 5.3 Preparação e pré-processamento dos dados

A preparação de dados é conduzida por scripts versionados em `scripts/`, com separação entre dados brutos (não versionados) e artefatos experimentais. Para o CIC, os procedimentos de preparação incluem construção de arquivos de treino e avaliação a partir dos dados brutos (`scripts/prep_cic_train.py` e `scripts/make_cic_eval.py`). O projeto também inclui um recorte robusto sem a variável de porta de destino (`scripts/prep_cic_robust.py`), utilizado em comparações específicas previstas no desenho experimental.

No nível de modelagem, o pipeline privilegia atributos numéricos e aplica rotinas de sanitização para valores ausentes ou infinitos, conforme implementado nos módulos de treino e inferência em `src/twodaef/`. A seleção efetiva de atributos não é fixa para todo o sistema: ela é definida por listas de colunas para o gatekeeper (`configs/cols/`) e por pools de atributos candidatos para especialistas (`artifacts/feature_pools/`).

## 5.4 Configuração experimental

A configuração experimental segue a organização do repositório:

1. O **gatekeeper** é treinado com conjunto de atributos explícito em arquivos de configuração.
2. Os **especialistas** são treinados por classe com busca entre combinações de famílias de modelos e conjuntos de atributos candidatos.
3. O mapeamento classe -> especialista é persistido em `configs/mappings/`, garantindo rastreabilidade do especialista selecionado em cada classe.
4. A inferência em dois estágios produz predições finais e registra informações auxiliares de decisão e latência por estágio.
5. A avaliação consolida métricas e figuras em `reports/`, de acordo com o plano experimental descrito em `docs/experiment_plan.md` e `docs/paper_experimental_plan.md`.

Para reprodutibilidade, o projeto adota parâmetros controlados nos scripts (por exemplo, sementes fixas quando aplicável) e mantém separação entre código, configuração e artefatos gerados.

## 5.5 Baselines e comparações coerentes com o projeto

As comparações consideradas nesta pesquisa são restritas ao que está explicitamente suportado no repositório:

- **Baseline global XGBoost** para o cenário robusto do CIC (`scripts/baseline_xgb_cic_robust.py`), sem decomposição em dois estágios.
- **Comparação por seleção de atributos** no CIC robusto, contrapondo configuração com pool reduzido e configuração com conjunto amplo de atributos (`scripts/make_feature_pool_cic_robust.py` e `scripts/make_feature_pool_cic_robust_all.py`).
- **Comparação entre famílias de modelos dos especialistas** (LGBM, XGB e CatBoost), conforme plano documentado em `reports/cic/EXPERIMENTOS_BOOSTERS.md`.

Essas comparações são tratadas como parte do desenho experimental e não implicam, por si, conclusão de superioridade de qualquer abordagem antes da análise de resultados.

## 5.6 Métricas de avaliação

As métricas adotadas refletem critérios tradicionais de avaliação em IDS e os artefatos efetivamente gerados pelo projeto:

- **Recall** da classe de ataque;
- **Precision** da classe de ataque;
- **F1-score** por classe e **F1-macro**;
- **Acurácia** global;
- **Matriz de confusão** em valores absolutos (TP, FP, TN, FN);
- **Latência média de inferência** por estágio (gatekeeper e especialista) e latência total estimada por amostra.

## 5.7 Justificativa para a escolha das métricas

Em IDS, a ênfase em **recall da classe maliciosa** é metodologicamente justificada pelo maior custo operacional associado a falsos negativos, que correspondem a ataques não detectados. A **precision** é incluída para controlar o impacto de alarmes indevidos, importante para a operação prática de centros de monitoramento. O **F1-score** (por classe e macro) é utilizado como medida de equilíbrio entre recall e precision, especialmente útil em cenários com desbalanceamento.

A **matriz de confusão absoluta** complementa as métricas agregadas por permitir inspeção direta da distribuição de erros. Por fim, métricas de **latência de inferência** são incorporadas porque a viabilidade de um IDS não depende apenas de qualidade preditiva, mas também de custo computacional compatível com uso operacional.
