# Outline do Artigo 2 (Disciplina de IA)

## 1. Título provisório
**Detecção de Intrusões com Arquitetura em Dois Estágios: Gatekeeper e Especialistas por Classe em Cenário Binário**

## 2. Tema
Aplicação de Inteligência Artificial à detecção de intrusões em redes, com avaliação de uma arquitetura hierárquica em dois estágios (gatekeeper + especialistas por classe), derivada do pipeline implementado em `src/twodaef/`.

## 3. Problema de pesquisa
Em IDS baseados em aprendizado de máquina, modelos globais únicos podem perder desempenho em classes críticas de ataque e dificultar o equilíbrio entre qualidade preditiva e custo computacional.  
Pergunta central: **uma decomposição em dois estágios, com roteamento por gatekeeper e especialistas por classe, é metodologicamente vantajosa para o contexto binário de IDS sem comprometer reprodutibilidade e interpretabilidade?**

## 4. Hipótese
A arquitetura em dois estágios **pode** oferecer melhor equilíbrio entre detecção de ataques (com ênfase em recall/F1 da classe maliciosa) e custo de inferência, quando comparada a baselines globais, desde que avaliada com protocolo reprodutível e sem extrapolações além dos artefatos disponíveis.

## 5. Objetivo geral
Avaliar, de forma reprodutível e conservadora, a adequação da arquitetura gatekeeper-especialistas para detecção de intrusões em formulação binária.

## 6. Objetivos específicos
- Descrever formalmente o pipeline de treino, inferência e avaliação já existente (`gatekeeper-train`, `train-specialists`, `infer-twostage`, `plot-eval`, `eval-twostage`).
- Definir o recorte experimental binário e documentar preparação de dados conforme scripts do projeto.
- Comparar o modelo em dois estágios com baselines factíveis já suportados por `scripts/` e `configs/`.
- Reportar métricas de classificação e custo computacional (latência por estágio e total) sem inferir ganhos não medidos.
- Incluir análise interpretável com SHAP de forma complementar, conforme fluxo em `reports/cic/xai/`.
- Discutir limitações metodológicas, ameaças à validade e escopo de generalização.

## 7. Dataset principal sugerido
**CIC-IDS2018 (formulação binária Benign vs Others/Attack), com recorte robusto sem porta de destino (`scripts/prep_cic_robust.py`)**.

Justificativa do recorte:
- há pipeline completo já documentado para CIC em `reports/cic/`;
- há suporte explícito a variações robustas e ablação em `scripts/plot_*_cic_robust.py`;
- há baseline global implementado para comparação (`scripts/baseline_xgb_cic_robust.py`).

Dataset secundário recomendado para validade externa:
- **UNSW-NB15 binário**, aproveitando `reports/unsw_bin/`.

## 8. Possíveis baselines
- **Baseline global XGBoost** (modelo único) no recorte robusto do CIC (`scripts/baseline_xgb_cic_robust.py`).
- **2D-AEF sem seleção restrita de atributos** (feature set amplo/ALL) versus versão com pool reduzido (`scripts/make_feature_pool_cic_robust_all.py` e `scripts/make_feature_pool_cic_robust.py`).
- **Especialistas com família única de modelos** (LGBM, XGB ou CatBoost), conforme plano em `reports/cic/EXPERIMENTOS_BOOSTERS.md`.
- **Gatekeeper isolado** como referência inferior de arquitetura (sem segunda etapa), quando o experimento estiver disponível.

## 9. Métricas principais
- Recall da classe de ataque (métrica prioritária para IDS).
- Precision da classe de ataque.
- F1-score por classe e F1-macro.
- Acurácia global.
- Matriz de confusão absoluta (TP, FP, TN, FN).
- Latência média por amostra: estágio 1 (gatekeeper), estágio 2 (especialista) e total.

## 10. Diferencial do artigo
- Aplicação acadêmica de uma arquitetura hierárquica já implementada e reprodutível no projeto (sem criar framework novo ad hoc).
- Comparação explícita entre abordagem em dois estágios e baselines simples/ablatórios já previstos no repositório.
- Integração de desempenho, custo computacional e interpretabilidade (SHAP) no mesmo protocolo experimental.
- Postura metodológica conservadora: foco em evidência disponível em `reports/`, evitando promessas além dos experimentos executados.

## 11. Estrutura prevista das seções
1. Introdução  
Contexto de IDS, motivação em IA aplicada, problema e hipótese.

2. Trabalhos Relacionados  
IDS com ML, arquiteturas em cascata/ensemble, e uso de XAI em segurança.

3. Metodologia  
Arquitetura 2 estágios, definição de gatekeeper e especialistas, seleção de features/modelos, fluxo de inferência.

4. Desenho Experimental  
Datasets e recortes (CIC principal e UNSW secundário), baselines, protocolo de avaliação, critérios de reprodutibilidade.

5. Resultados  
Métricas, matrizes de confusão, latências e tabelas comparativas derivadas de artefatos do projeto.

6. Discussão  
Interpretação dos resultados, implicações para IDS, limites, ameaças à validade.

7. Conclusão e Trabalhos Futuros  
Síntese, contribuição efetiva do estudo e próximos passos sem extrapolação.
