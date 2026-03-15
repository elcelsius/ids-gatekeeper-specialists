# Ficha Mestra do Paper

## 1. Identidade do artigo

- **Título do artigo:** GKS: uma arquitetura de IA em dois estágios para problemas complexos de classificação: estudo de caso em detecção de intrusões.
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
- **Contribuição aplicada:** avaliação da estratégia no estudo de caso de IDS com cenário principal multiclasse no CIC-IDS2018 e cenário complementar binário no UNSW-NB15.
- **Contribuição analítica:** leitura conservadora de métricas agregadas, métricas por classe, matrizes de confusão, custo/latência e materiais complementares de interpretabilidade.

## 4. Recorte experimental

- **Dataset principal:** CIC-IDS2018 em formulação multiclasse agregada (`Benign`, `Bot`, `BruteForce`, `DDoS`, `DoS`, `Others`, `Web`), conforme `reports/cic/` e `outputs/eval_cic/`.
- **Dataset secundário complementar:** UNSW-NB15 binário (`Normal` vs `Attack`), conforme `reports/unsw_bin/` e `outputs/eval_unsw/`.
- **Cenário principal:** arquitetura em dois estágios com gatekeeper para triagem e especialistas por classe/subespaço.
- **Baseline principal:** baseline global XGBoost no recorte CIC robusto (`scripts/baseline_xgb_cic_robust.py`), já incorporado ao manuscrito como comparação oficial binária.
- **Métricas oficiais:** recall, precision, F1 por classe, F1-macro, acurácia, matriz de confusão e latência por estágio/total (quando disponível nos relatórios).

## 5. Evidências obrigatórias do paper

- **Tabela principal:** tabela comparativa de desempenho consolidando, no mínimo, GKS no CIC, GKS no UNSW e baseline XGBoost no CIC robusto; os artefatos sintéticos atuais são `reports/table_main_results.csv` e `reports/table_main_results.md`.
- **Figura da arquitetura:** representação do fluxo em dois estágios (referência atual: `docs/ARCHITECTURE.md` e `diagrama.md`).
- **Matriz de confusão principal:** `reports/cic/confusion_matrix_cic.png`, complementada pelas versões tabulares `reports/confusion_matrix_main.csv` e `reports/confusion_matrix_main.md` (com equivalente binário em `reports/confusion_matrix_unsw_bin.(csv|md)` e baseline em `reports/confusion_matrix_baseline.(csv|md)`).
- **Comparação com baseline:** já incorporada no manuscrito final e agora também empacotada em `reports/table_baseline_comparison.csv` e `reports/table_baseline_comparison.md`.
- **Manifesto e custo computacional:** `reports/run_manifest.md` consolida a rastreabilidade do snapshot atual e `reports/latency_summary.(csv|md)` sintetiza as medições de latência disponíveis.
- **Guia do diretório `reports/`:** `reports/README.md` separa artefatos oficiais do snapshot atual de artefatos legados ou apenas complementares.
- **Papel de XAI:** material complementar eventual de interpretabilidade, hoje restrito a um snapshot binário legado do CIC em `reports/cic/xai/xai_shap_consolidado.csv` e `reports/cic/XAI_BRIEF.md`.

## 6. Papel do IDS no artigo

- **Como o IDS deve aparecer na narrativa:** como estudo de caso aplicado para testar uma estratégia de IA em classificação complexa.
- **O que evitar:** narrativa centrada em operação de SOC, descrição de ferramenta de segurança prática ou foco exclusivo em ataque vs benigno sem discussão metodológica de IA.

## 7. Lacunas atuais

- **O que já existe no projeto:** manuscrito completo consolidado (`artigo/artigo_completo.md`), seções temáticas finalizadas, métricas agregadas e por classe em `outputs/`, figuras de matriz/F1 por classe em `reports/` e baseline oficial calculado no recorte robusto do CIC.
- **O que falta consolidar:** um pacote de XAI alinhado ao cenário multiclasse principal.
- **O que falta gerar ou revisar:** reforço de rastreabilidade externa para artefatos hoje apenas locais em `outputs/`, além da revisão de bibliografia (`references/references.bib`) para citação formal.

## 8. Critério de prontidão

- **Para revisão científica:** manuscrito completo e coerente com IA como eixo central, evidências mínimas explícitas (métricas agregadas, matriz, figura de arquitetura e comparação com baseline), limitações declaradas e hipóteses claramente delimitadas; XAI entra apenas se permanecer no escopo editorial.
- **Para submissão:** baseline principal consolidado no corpo do artigo, versão final das tabelas/figuras com rastreabilidade, pacote experimental reproduzível (métricas, configurações e ambiente), revisão editorial final e adequação ao template do veículo-alvo.
