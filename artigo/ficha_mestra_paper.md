# Ficha Mestra do Paper

## 1. Identidade do artigo

- **Título provisório:** Detecção de Intrusões com Arquitetura em Dois Estágios: Gatekeeper e Especialistas por Classe em Cenário Binário.
- **Tipo de artigo:** estudo metodológico de Inteligência Artificial aplicada, com validação experimental em estudo de caso.
- **Área principal:** Inteligência Artificial (aprendizado de máquina para problemas de classificação complexa).
- **Domínio de aplicação:** detecção de intrusões em redes (IDS), tratada como ambiente de validação e não como centro conceitual do paper.

## 2. Pergunta de pesquisa

- **Pergunta central:** Uma arquitetura de IA em dois estágios, com gatekeeper e especialistas, é uma estratégia adequada para problemas de classificação complexos?
- **Hipótese principal:** A decomposição hierárquica da decisão, com triagem inicial e especialização por subproblema, pode estruturar a classificação de forma mais adequada do que uma abordagem monolítica única em cenários complexos.
- **Hipótese secundária:** Mesmo sem assumir ganho universal, a organização em estágios favorece análise mais rica de desempenho, erros, custo computacional e interpretabilidade.

## 3. Contribuições

- **Contribuição principal:** análise de uma estratégia de IA baseada em decomposição hierárquica e especialização de classificadores.
- **Contribuição metodológica:** formalização e discussão de arquitetura em dois estágios (gatekeeper + especialistas) com rastreabilidade de artefatos.
- **Contribuição aplicada:** avaliação da estratégia no estudo de caso de IDS com recorte binário.
- **Contribuição analítica:** leitura conservadora de métricas agregadas, matrizes de confusão (figuras), custo/latência e evidências de XAI disponíveis.

## 4. Recorte experimental

- **Dataset principal:** CIC-IDS2018 (formulação binária `Benign` vs `Others`/ataque), conforme `reports/cic/`.
- **Dataset secundário opcional:** UNSW-NB15 binário, conforme `reports/unsw_bin/`.
- **Cenário principal:** arquitetura em dois estágios com gatekeeper para triagem e especialistas por classe/subespaço.
- **Baseline principal:** baseline global XGBoost no recorte CIC robusto (`scripts/baseline_xgb_cic_robust.py`), com consolidação comparativa ainda pendente em artefatos finais versionados.
- **Métricas oficiais:** recall, precision, F1 por classe, F1-macro, acurácia, matriz de confusão e latência por estágio/total (quando disponível nos relatórios).

## 5. Evidências obrigatórias do paper

- **Tabela principal:** tabela comparativa de desempenho consolidando, no mínimo, 2-stage vs baseline no cenário principal; atualmente há consolidação parcial em `reports/metrics_comparados.(csv|md)`.
- **Figura da arquitetura:** representação do fluxo em dois estágios (referência atual: `docs/ARCHITECTURE.md` e `diagrama.md`).
- **Matriz de confusão principal:** `reports/cic/confusion_matrix_cic.png` (com equivalente no cenário secundário em `reports/unsw_bin/`).
- **Comparação com baseline:** necessária no manuscrito final; no estado atual, `reports/cic/EXPERIMENTOS_BOOSTERS.md` permanece sem preenchimento de resultados.
- **Papel de XAI:** evidência complementar de interpretabilidade (CIC) com base em `reports/cic/xai/xai_shap_consolidado.csv` e `reports/cic/XAI_BRIEF.md`.

## 6. Papel do IDS no artigo

- **Como o IDS deve aparecer na narrativa:** como estudo de caso aplicado para testar uma estratégia de IA em classificação complexa.
- **O que evitar:** narrativa centrada em operação de SOC, descrição de ferramenta de segurança prática ou foco exclusivo em ataque vs benigno sem discussão metodológica de IA.

## 7. Lacunas atuais

- **O que já existe no projeto:** manuscrito completo consolidado (`artigo/artigo_completo.md`), seções temáticas finalizadas, métricas agregadas para CIC/UNSW, figuras de matriz/F1 por classe, e artefatos XAI no CIC.
- **O que falta consolidar:** versão única de referência para UNSW (há snapshots `unsw_bin` e `unsw` legado), matriz de confusão em formato estruturado (TP/FP/TN/FN), e pacote de comparação com baseline preenchido.
- **O que falta gerar ou revisar:** tabela principal final do paper com baseline, padronização completa de evidências de custo computacional, revisão final de coerência editorial IA-centrada e atualização de bibliografia (`references/references.bib`) para citação formal.

## 8. Critério de prontidão

- **Para revisão científica:** manuscrito completo e coerente com IA como eixo central, evidências mínimas explícitas (métricas agregadas, matriz, figura de arquitetura, XAI complementar), limitações declaradas e hipóteses claramente delimitadas.
- **Para submissão:** baseline principal consolidado no corpo do artigo, versão final das tabelas/figuras com rastreabilidade, pacote experimental reproduzível (métricas, configurações e ambiente), revisão editorial final e adequação ao template do veículo-alvo.
