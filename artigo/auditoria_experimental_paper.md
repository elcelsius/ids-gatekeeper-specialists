# Auditoria Experimental do Paper

**Projeto:** `artigo-ia` (derivado de 2D-AEF)  
**Data da auditoria:** 2026-03-09  
**Posicionamento do paper:** IA aplicada como eixo central, com IDS como estudo de caso  
**Escopo inspecionado:** `scripts/`, `src/`, `configs/`, `artifacts/`, `reports/`, `docs/`, `README.md`

## 1. Visão geral da pipeline experimental

A pipeline experimental implementada no projeto está conceitualmente completa para o desenho two-stage:

1. preparação de dados (CIC e variações UNSW);
2. geração/seleção de conjuntos de atributos;
3. treino do gatekeeper;
4. treino de especialistas por classe;
5. inferência em dois estágios;
6. avaliação e geração de gráficos;
7. agregação de métricas e XAI.

No entanto, a consolidação final para publicação ainda não está fechada, por quatro razões principais:

- coexistência de snapshots e caminhos legados (especialmente UNSW);
- ausência de artefatos estruturados essenciais no material versionado (predições, matriz absoluta em formato tabular único por cenário);
- baseline comparável existente em código, mas sem consolidação final no pacote de relatórios;
- divergência entre parte da documentação e a organização atual de caminhos (`configs/` vs `artifacts/`, `reports/unsw_bin` vs `reports/UNSW` legado).

## 2. Scripts centrais para o paper

### 2.1 CLIs e módulos centrais (`src/twodaef/`)

| Arquivo | Finalidade | Dataset/cenário | Entradas principais | Saídas principais | Diagnóstico para o paper |
|---|---|---|---|---|---|
| `src/twodaef/cli_train_gatekeeper.py` | Treino do gatekeeper (árvore podada) | CIC binário, UNSW binário/multiclasse | `--train_csv`, `--target_col`, `--features`, `--model_out` | modelo `.joblib` | **Utilizável**; etapa central de treino |
| `src/twodaef/cli_train_specialists.py` | Orquestra treino dos especialistas por classe | CIC/UNSW | `--train_csv`, `--target_col`, `--feature_pool_json`, `--out_dir`, `--map_path`, `--models` | diretório de especialistas + `specialist_map*.json` | **Utilizável**; inclui `dry_run` e validações |
| `src/twodaef/specialists/train_specialists.py` | Busca melhor par modelo+feature set por classe (F1_k + latência) | CIC/UNSW | `TrainConfig` (CSV, target, pool, seed etc.) | modelos por classe + mapa com metadados | **Utilizável** e metodologicamente alinhado ao paper |
| `src/twodaef/cli_infer_twostage.py` | Inferência Gatekeeper -> Especialista | CIC/UNSW | `--gatekeeper_model`, `--gatekeeper_features`, `--specialist_map`, `--input_csv`, `--output_csv` | `preds.csv` com predições e latência por estágio | **Utilizável**; essencial para campanha final |
| `src/twodaef/infer/two_stage.py` | Implementação de inferência two-stage com benchmark de latência | CIC/UNSW | config + mapa de especialistas + CSV de entrada | `preds.csv` com `pred_final`, `latency_ms_stage1/2/total` | **Utilizável**; fornece custo inferencial diretamente |
| `src/twodaef/cli_eval_twostage.py` | Avalia `preds.csv` já gerado | CIC/UNSW | `--output_dir` (assume `preds.csv` dentro), `--label_col`, `--specialist_map` | `metrics_eval.json`, `classification_report_eval.csv`, `confusion_matrix_eval.csv` | **Utilizável**, porém depende de `preds.csv` prévio |
| `src/twodaef/eval/evaluate.py` | Cálculo de métricas e matriz em formato tabular | CIC/UNSW | caminho de `preds.csv` e `label_col` | métricas e matriz absoluta em CSV | **Utilizável** e importante para fechar lacuna de matriz absoluta |
| `src/twodaef/cli_plot_eval.py` | Gera matriz de confusão (PNG), F1 por classe (PNG) e `metrics_again.json` | CIC/UNSW | `--preds_csv` ou `--dataset_tag`, `--label_col`, `--out_dir` | `confusion_matrix*.png`, `f1_per_class*.png`, `metrics_again.json` | **Utilizável**; atualmente base dos artefatos em `reports/` |
| `src/twodaef/reports/plots_eval.py` | Lógica de plots e recomputação de métricas | CIC/UNSW | DataFrame de predições | PNG + `metrics_again.json` | **Utilizável**, mas não gera matriz absoluta em JSON (apenas figura + métricas agregadas) |
| `src/twodaef/cli_make_feature_pool.py` | Geração programática de pool de features | Geral | `--csv`, `--target_col`, `--max_features_per_set`, `--total_sets`, `--out_json` | JSON de pool (`pool`) | **Utilizável**; formato diferente de alguns scripts legados |
| `src/twodaef/cli_explain_specialist.py` | XAI por especialista (SHAP/LIME fallback) | CIC/UNSW | `--specialist_map`, `--class_key`, `--input_csv`, `--output_dir` | artefatos por classe em `class_*` | **Utilizável**; componente complementar |
| `src/twodaef/cli_xai_aggregate.py` | Consolida XAI por classe em CSV/MD | CIC/UNSW | `--xai_root`, `--out_dir` | `xai_shap_consolidado.csv/.md` | **Utilizável**; já há evidência no CIC |
| `src/twodaef/cli_xai_report.py` | Agregador alternativo de XAI (API ligeiramente distinta) | Geral | `--base_dir`, `--out_dir`, `--top_k` | consolidado XAI | **Ambíguo/duplicado**; existe com papel semelhante ao `cli_xai_aggregate` |

### 2.2 Scripts utilitários (`scripts/`)

| Arquivo | Finalidade | Dataset/cenário | Entradas principais | Saídas principais | Diagnóstico para o paper |
|---|---|---|---|---|---|
| `scripts/prep_cic_train.py` | Prepara CIC a partir de `data/raw/cicids2018`, agrega rótulos e cria treino/infer | CIC binário (agregado multi -> `Benign`/`Others`) | caminhos fixos no código (`RAW_DIR`) | `data/train_cic.csv`, `data/cic_infer.csv` | **Utilizável** para cenário principal |
| `scripts/make_cic_eval.py` | Gera conjunto de avaliação amostrado | CIC binário | `data/train_cic.csv` (fixo) | `data/cic_eval.csv` | **Utilizável**; simples e objetivo |
| `scripts/prep_cic_robust.py` | Remove `dst_port` para recorte robusto | CIC robusto | `data/train_cic.csv`, `data/cic_eval.csv` | `data/train_cic_robust.csv`, `data/cic_eval_robust.csv` | **Utilizável** para baseline e ablação |
| `scripts/download_cicids2018.py` | Download de dataset via Kaggle | CIC | credencial Kaggle local | CSVs em `data/raw/cicids2018` | **Utilizável** como etapa de aquisição |
| `scripts/prep_unsw_multiclass.py` | Prepara UNSW multiclasses com `attack_cat` | UNSW multiclasses | arquivos brutos UNSW | `data/UNSW_train_mc.csv`, `data/UNSW_test_mc.csv` | **Parcialmente útil**; não resolve binarização oficial do paper |
| `scripts/make_gatekeeper_cols_from_csv.py` | Gera lista de colunas numéricas para gatekeeper | CIC/UNSW | `--csv`, `--out`, `--max_cols` | TXT de colunas | **Utilizável**; recomendado para rastreabilidade |
| `scripts/make_feature_pool_min.py` | Gera pool mínimo por variância (formato `feature_sets`) | CIC/UNSW | `--in`, `--out`, `--target`, `--max_per_set` | JSON de pool | **Utilizável**; alinhado a execução prática recente |
| `scripts/make_feature_pool_cic.py` | Pool específico CIC (heurística fixa) | CIC | caminho fixo `data/train_cic.csv` | `artifacts/feature_pool_cic.json` | **Utilizável com ressalva**; caminho legado (fora de `artifacts/feature_pools/`) |
| `scripts/make_feature_pool_cic_robust.py` | Pool CIC robusto (2 sets de 20) | CIC robusto | caminho fixo | `artifacts/feature_pool_cic_robust.json` | **Utilizável** para comparações robustas |
| `scripts/make_feature_pool_cic_robust_all.py` | Pool CIC robusto com todas as features | CIC robusto | caminho fixo | `artifacts/feature_pool_cic_robust_all.json` | **Utilizável** para ablação FS<=20 vs ALL |
| `scripts/make_feature_pool_unsw.py` | Pool UNSW binário (heurística simples) | UNSW binário | caminho fixo | `artifacts/feature_pool_unsw.json` | **Utilizável**, mas depende de convenção de dados não formalizada no repositório |
| `scripts/make_feature_pool_unsw_mc.py` | Pool UNSW multiclasses | UNSW multiclasses | `data/UNSW_train_mc.csv` | `artifacts/feature_pool_unsw_mc.json` | **Secundário/legado** para paper atual |
| `scripts/baseline_xgb_cic_robust.py` | Baseline monolítico XGBoost (binário robusto) | CIC robusto | caminhos fixos de treino/eval robustos | métricas e matriz CSV em `outputs/cic_robust_xgb_baseline/` | **Utilizável e central**, mas ainda sem consolidação versionada no pacote final |
| `scripts/aggregate_metrics.py` | Consolida `metrics_again.json` em CSV/MD comparativo | CIC + UNSW | `--unsw`, `--cic`, `--out_csv`, `--out_md` | `reports/metrics_comparados.csv/.md` | **Utilizável**; hoje mistura snapshot legado no UNSW |
| `scripts/make_xai_brief.py` | Gera resumo textual do CSV consolidado de SHAP | CIC/UNSW | `--in`, `--out`, `--topk` | `XAI_BRIEF.md` | **Utilizável** como apoio analítico |
| `scripts/plot_latency_cic_robust.py` | Plota latência a partir de `preds.csv` robusto | CIC robusto | `outputs/cic_robust/preds.csv` | figura em `figs/` | **Ambíguo/auxiliar**; fora da trilha principal de `reports/` |
| `scripts/plot_ablation_cic_robust.py` | Gráfico de ablação (FS<=20, ALL, XGB) | CIC robusto | CSVs de métricas em `outputs/` | figura em `figs/` | **Ambíguo/auxiliar**; útil após consolidar baseline |
| `scripts/plot_confusion_cic_robust.py` | Gera figura de matriz a partir de CSV de confusão | CIC robusto | `outputs/cic_robust/...csv` | figura em `figs/` | **Legado**; sobreposição com `plot-eval` |
| `scripts/plot_confusion_unsw_mc.py` | Matriz para UNSW multiclasses | UNSW multiclasses | `outputs/unsw_mc/...csv` | figura em `figs/` | **Fora do escopo principal do paper** |
| `scripts/plot_shap_cic_robust.py` | SHAP para baseline XGB robusto | CIC robusto | dados robustos + XGBoost/SHAP | figura em `figs/` | **Auxiliar**; não é a trilha XAI principal já adotada |
| `scripts/smoke_test.ps1` | Teste rápido de geração de plots com dados sintéticos | Sanidade pipeline | sem dados reais | `reports/cic/*` sintético | **Útil para CI/sanidade**, não para evidência do paper |
| `scripts/smoke_test_multiclass.py` | Smoke end-to-end multiclasses sintético | teste interno | dados toy | `outputs/tmp_mc/` | **Fora do escopo do paper** |
| `scripts/agrupar_arquivos.ps1` | Empacotamento legado de outro caminho local (`D:\\Workspace\\2D-AEF`) | operação manual | caminho hardcoded externo | pasta/zip local | **Obsoleto para este repositório** |

### 2.3 Observação específica sobre preparação UNSW binário

Para o recorte **UNSW binário**, não foi encontrado um script dedicado de preparação equivalente ao `prep_cic_train.py`.  
O que existe é:

- suporte de treino/inferência para alvo `label`;
- script de preparação **multiclasses** (`prep_unsw_multiclass.py`);
- documentação citando `unsw_eval.csv`/`unsw_infer.csv`, mas sem script explícito versionado para geração desses arquivos no fluxo binário.

Diagnóstico: **lacuna operacional real** para campanha final reproduzível do cenário secundário.

## 3. Artefatos atuais do projeto

### 3.1 Artefatos versionados e comprováveis no Git

- `reports/cic/metrics_again.json`
- `reports/unsw_bin/metrics_again.json`
- `reports/unsw_bin/metrics_again_unsw_legacy.json`
- `reports/metrics_comparados.csv` e `reports/metrics_comparados.md`
- `reports/cic/RELATORIO_CIC.md`
- `reports/unsw_bin/RELATORIO_UNSW.md`
- `reports/cic/EXPERIMENTOS_BOOSTERS.md` (template sem preenchimento de resultados)
- `reports/cic/xai/xai_shap_consolidado.csv` e `.md`
- `reports/cic/XAI_BRIEF.md`

### 3.2 Artefatos locais detectados, mas não versionados

Foram encontrados localmente (fora do controle de versão):

- imagens em `reports/` (`confusion_matrix_*.png`, `f1_per_class_*.png`);
- pools de features e modelos em `artifacts/feature_pools/` e `artifacts/trained_models/`;
- ausência de `outputs/` no estado local atual auditado.

Diagnóstico: esses itens podem ajudar em execução local, mas **não são evidência versionada suficiente** para fechamento publicável/reprodutível.

### 3.3 Classificação dos artefatos de `reports/`

| Artefato | Classificação | Justificativa | Ação recomendada |
|---|---|---|---|
| `reports/cic/metrics_again.json` | Reutilizável com ressalvas | métricas agregadas consistentes, mas dependem de `preds_csv` não versionado | regenerar junto com campanha final para rastreabilidade total |
| `reports/unsw_bin/metrics_again.json` | Reutilizável com ressalvas | métrica agregada presente para `unsw_bin` | manter apenas se protocolo final escolher `unsw_bin` como snapshot oficial |
| `reports/unsw_bin/metrics_again_unsw_legacy.json` | Herdado/ambíguo | representa execução `unsw` legado (`outputs/eval_unsw`) | escolher snapshot único e arquivar o alternativo como legado |
| `reports/metrics_comparados.*` | Deve ser regenerado | consolidado atual usa snapshot UNSW legado (`unsw`) e não o `unsw_bin` | recalcular após congelar protocolo |
| `reports/cic/EXPERIMENTOS_BOOSTERS.md` | Herdado incompleto | tabela sem resultados preenchidos | preencher com execução real ou remover do escopo do paper |
| `reports/cic/xai/xai_shap_consolidado.csv` | Reutilizável | contém dados numéricos estruturados por classe | manter como evidência complementar, com referência ao run que o gerou |
| `reports/cic/xai/xai_shap_consolidado.md` | Herdado com inconsistência | valores diferem do CSV consolidado atual | regenerar para alinhar com CSV |
| `reports/cic/XAI_BRIEF.md` | Reutilizável com ressalvas | coerente com o CSV atual | regenerar automaticamente após consolidar XAI final |
| Figuras PNG em `reports/*` | Deve ser regenerado/versionado de forma controlada | existem localmente, mas não estão versionadas | gerar novamente e decidir política de versionamento para submissão |

## 4. Checagem objetiva dos itens-chave do paper

| Item solicitado | Situação atual | Evidência |
|---|---|---|
| Baseline comparável ao two-stage | **Existe em código, não consolidado no pacote final** | `scripts/baseline_xgb_cic_robust.py`; `reports/cic/EXPERIMENTOS_BOOSTERS.md` sem resultados |
| Relatórios com métricas agregadas | **Sim (parcialmente)** | `reports/cic/metrics_again.json`, `reports/unsw_bin/metrics_again*.json` |
| Métricas por classe (estruturadas) | **Parcial** | há figuras e alguns relatórios textuais; falta padrão estruturado único para paper |
| Matriz de confusão absoluta estruturada | **Não consolidada em `reports/`** | código gera CSV (`evaluate.py`), mas não há artefato final consolidado versionado por cenário no pacote atual |
| Predições salvas (`preds.csv`) | **Não disponíveis no estado versionado** | métricas apontam para `outputs/.../preds.csv`; pasta `outputs/` não está presente |
| Latência/custo | **Parcial** | disponível em relatórios textuais e colunas previstas no `two_stage.py`; faltam arquivos finais padronizados por run |
| XAI reaproveitável | **Sim (CIC)** | `reports/cic/xai/xai_shap_consolidado.csv` e `reports/cic/XAI_BRIEF.md` |

## 5. Documentação útil e aderência

| Documento | Utilidade para execução | Diagnóstico |
|---|---|---|
| `README.md` | Boa visão geral e comandos-base | útil, mas ainda há coexistência de convenções antigas/novas |
| `docs/experiment_plan.md` | roteiro curto de etapas | útil e alinhado ao objetivo |
| `docs/paper_experimental_plan.md` | define artefatos mínimos publicáveis | muito útil; vários itens ainda pendentes no estado atual |
| `docs/WORKFLOW.md` | documentação detalhada da pipeline | útil, porém com exemplos em caminhos legados (`artifacts/specialist_map*.json`, `outputs/eval_unsw`) |
| `docs/ARCHITECTURE.md` | apoio conceitual da arquitetura | útil para seção metodológica/figura |
| `docs/cic_eval_report.md` e `docs/unsw_eval_report.md` | histórico de execuções | úteis como referência histórica; não substituem campanha final consolidada |
| `docs/REPORTS.md` | índice de relatórios | parcialmente desatualizado (referências legadas) |
| `artigo/plano_mestre_execucao_experimental.md` e `artigo/checklist_execucao_experimental.md` | governança de execução focada no paper | muito úteis para fechar lacunas operacionais |

## 6. O que já está pronto

- Pipeline two-stage implementada e operacional no código-fonte.
- CLIs principais de treino, inferência, avaliação e XAI disponíveis.
- Métricas agregadas para CIC e UNSW já existem em `reports/`.
- Estrutura de mapeamentos em `configs/mappings/` já organizada por cenário.
- Existe baseline monolítico explícito (XGBoost robusto CIC) no repositório.
- Existe trilha XAI reaproveitável para CIC (consolidado CSV + resumo).

## 7. O que precisa ser regenerado

- campanha final CIC binário do zero, com manifesto de execução;
- baseline CIC robusto com saída comparável ao two-stage (mesmas métricas/tabelas);
- matriz de confusão absoluta estruturada por cenário (além de PNG);
- métricas por classe em formato tabular final (não só figura);
- consolidação final UNSW em snapshot único (eliminar dualidade `unsw_bin` vs legado);
- `reports/metrics_comparados.*` após definir snapshot oficial;
- pacote final de figuras (versionado ou com política explícita) e validação de consistência XAI CSV/MD.

## 8. Lacunas críticas para campanha publicável

1. **Ausência de protocolo único congelado para UNSW binário** (script de preparação binária não está explícito no repositório).
2. **Predições não versionadas** (`preds.csv`) e sem manifesto formal de runs.
3. **Matriz de confusão absoluta não consolidada em artefato oficial de relatório** (embora o código gere CSV).
4. **Comparação com baseline não fechada** no material versionado.
5. **Inconsistências de documentação e caminhos legados** podem induzir execução em trilha errada.
6. **Inconsistência entre artefatos XAI (CSV vs MD)** sugere snapshots diferentes.
7. **Dependência de artefatos locais ignorados** (`artifacts/`, PNG em `reports/`) reduz reprodutibilidade externa.

## 9. Proposta de ordem de execução (operacional)

1. congelar protocolo oficial do paper (CIC principal, UNSW secundário, baseline XGB robusto, seeds, caminhos de saída);
2. limpar convenções de caminho (usar `configs/mappings/*` e layout final único de outputs/reports);
3. executar CIC principal (preparo -> gatekeeper -> especialistas -> inferência -> avaliação -> plots -> XAI);
4. executar baseline XGB robusto com métricas equivalentes e matriz comparável;
5. consolidar tabelas oficiais (agregadas + por classe + matriz absoluta + latência);
6. executar ou reconfirmar UNSW binário em snapshot único para validação complementar;
7. regenerar `reports/metrics_comparados.*` com snapshots finais;
8. atualizar relatórios finais do paper (`05` a `08`) com os novos artefatos rastreáveis.

## 10. Tabela resumo operacional

| etapa experimental | script principal | status | observações |
|---|---|---|---|
| Preparação CIC binário | `scripts/prep_cic_train.py` + `scripts/make_cic_eval.py` | Implementado e utilizável | principal trilha de dados para o paper |
| Preparação UNSW binário | (não há script dedicado único) | Lacuna crítica | existe suporte parcial; falta script oficial de binarização/preparo |
| Treino gatekeeper | `src/twodaef/cli_train_gatekeeper.py` | Implementado e utilizável | depende de TXT de features consistente |
| Treino especialistas | `src/twodaef/cli_train_specialists.py` | Implementado e utilizável | seleção por F1_k e latência |
| Inferência two-stage | `src/twodaef/cli_infer_twostage.py` | Implementado e utilizável | gera latência por estágio em `preds.csv` |
| Avaliação estruturada | `src/twodaef/cli_eval_twostage.py` | Implementado e utilizável | gera `confusion_matrix_eval.csv` e `classification_report_eval.csv` |
| Matriz/F1 em figuras + métricas agregadas | `src/twodaef/cli_plot_eval.py` | Implementado e em uso | base dos `metrics_again.json` em `reports/` |
| Baseline principal | `scripts/baseline_xgb_cic_robust.py` | Implementado, não consolidado | precisa entrar na tabela final comparativa |
| Consolidação cross-dataset | `scripts/aggregate_metrics.py` | Implementado, porém com snapshot ambíguo | atualmente mistura `unsw` legado e `unsw_bin` |
| Latência/custo | `src/twodaef/infer/two_stage.py` (+ opcional `scripts/plot_latency_cic_robust.py`) | Parcialmente consolidado | valores aparecem em relatórios, mas faltam artefatos finais padronizados |
| XAI por especialista | `src/twodaef/cli_explain_specialist.py` + `src/twodaef/cli_xai_aggregate.py` | Implementado e parcialmente consolidado | CIC possui artefatos; necessário alinhar CSV/MD e snapshot final |

