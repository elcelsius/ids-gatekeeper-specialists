# Auditoria Experimental do Paper

**Projeto:** `ids-gatekeeper-specialists`  
**Data da auditoria:** 2026-03-15  
**Posicionamento do paper:** IA aplicada como eixo central, com IDS como estudo de caso  
**Escopo inspecionado:** `scripts/`, `src/`, `configs/`, `artifacts/`, `outputs/`, `reports/`, `docs/`, `artigo/`

## 1. Síntese executiva

O projeto possui, no snapshot atual, uma pipeline two-stage operacional e coerente com o manuscrito principal. O cenário principal consolidado do paper é o **CIC-IDS2018 em formulação multiclasse agregada** (`Benign`, `Bot`, `BruteForce`, `DDoS`, `DoS`, `Others`, `Web`), complementado por um cenário **UNSW-NB15 binário** (`Normal` vs. `Attack`) e por um **baseline XGBoost binário robusto** no CIC.

Em relação à auditoria anterior, quatro pontos relevantes mudaram:

- o protocolo do paper deixou de tratar o CIC como cenário binário principal;
- o script `scripts/prep_unsw_binary.py` existe e cobre explicitamente a preparação binária do UNSW;
- o snapshot local atual contém `outputs/` com predições, métricas estruturadas e matrizes de confusão em CSV;
- `reports/metrics_comparados.csv` e `reports/metrics_comparados.md` foram regenerados com o snapshot oficial `unsw_bin`.

Persistem, entretanto, algumas lacunas importantes para fechamento publicável externo: os `outputs/` continuam não versionados e o XAI disponível no CIC corresponde a um snapshot binário legado, não ao cenário multiclasse principal. Em contrapartida, a documentação auxiliar principal do paper foi reconciliada com esse estado do snapshot, e o pacote textual de `reports/` agora inclui manifesto de execução, tabelas sintéticas independentes e matrizes tabulares de confusão.

Como regra de leitura do diretório `reports/`, o arquivo `reports/README.md` passa a funcionar como índice editorial do snapshot atual, separando os artefatos oficiais dos materiais legados ou apenas complementares.

## 2. Pipeline experimental atual

A trilha principal do paper está operacional em sete etapas:

1. preparação de dados;
2. geração de colunas do gatekeeper e feature pools;
3. treino do gatekeeper;
4. treino dos especialistas;
5. inferência two-stage;
6. avaliação estruturada;
7. geração de plots e consolidação auxiliar.

## 3. Scripts e módulos centrais

### 3.1 Módulos `src/twodaef/`

| Arquivo | Papel atual no paper | Diagnóstico |
|---|---|---|
| `src/twodaef/cli_train_gatekeeper.py` | treino do gatekeeper | utilizável e central |
| `src/twodaef/cli_train_specialists.py` | treino dos especialistas por classe | utilizável e central |
| `src/twodaef/cli_infer_twostage.py` | geração de `preds.csv` com latência por estágio | utilizável e central |
| `src/twodaef/cli_eval_twostage.py` | geração de `metrics_eval.json`, `classification_report_eval.csv` e `confusion_matrix_eval.csv` | utilizável e central |
| `src/twodaef/cli_plot_eval.py` | geração de `metrics_again.json` e figuras em `reports/` | utilizável e em uso |
| `src/twodaef/infer/two_stage.py` | implementação da inferência e benchmark de latência | utilizável e importante para custo inferencial |
| `src/twodaef/eval/evaluate.py` | cálculo de métricas e matriz tabular | utilizável e importante para fechar lacuna de matriz absoluta |
| `src/twodaef/cli_explain_specialist.py` | XAI por especialista | utilizável, mas não faz parte do núcleo principal atual |
| `src/twodaef/cli_xai_aggregate.py` | consolidação XAI | utilizável, porém hoje alimenta snapshot legado no CIC |

### 3.2 Scripts `scripts/`

| Arquivo | Papel atual no paper | Diagnóstico |
|---|---|---|
| `scripts/prep_cic_train.py` | prepara `train_cic.csv` e `cic_infer.csv` com rótulos agregados multiclasse | utilizável para o cenário principal |
| `scripts/make_cic_eval.py` | gera `cic_eval.csv` com holdout por offset | utilizável para o cenário principal |
| `scripts/prep_cic_robust.py` | gera recorte robusto sem `dst_port` | utilizável para baseline e leitura auxiliar |
| `scripts/prep_unsw_binary.py` | prepara `train_unsw.csv`, `unsw_eval.csv` e `unsw_infer.csv` em modo binário | utilizável e agora cobre explicitamente o cenário secundário |
| `scripts/make_gatekeeper_cols_from_csv.py` | gera TXT de colunas do gatekeeper | utilizável |
| `scripts/make_feature_pool_min.py` | gera pools mínimos de features | utilizável |
| `scripts/baseline_xgb_cic_robust.py` | baseline global binário no CIC robusto | utilizável e central |
| `scripts/aggregate_metrics.py` | consolidação cross-dataset entre `metrics_again.json` | utilizável; já regenerado para o snapshot atual |
| `scripts/make_xai_brief.py` | resumo textual de XAI | utilizável, mas hoje ligado a snapshot legado |

## 4. Artefatos comprováveis no snapshot atual

### 4.1 Artefatos versionados em `reports/`

- `reports/cic/metrics_again.json`
- `reports/unsw_bin/metrics_again.json`
- `reports/unsw_bin/metrics_again_unsw_legacy.json` *(legado)*
- `reports/metrics_comparados.csv`
- `reports/metrics_comparados.md`
- `reports/README.md`
- `reports/table_main_results.csv`
- `reports/table_main_results.md`
- `reports/table_baseline_comparison.csv`
- `reports/table_baseline_comparison.md`
- `reports/latency_summary.csv`
- `reports/latency_summary.md`
- `reports/confusion_matrix_main.csv`
- `reports/confusion_matrix_main.md`
- `reports/confusion_matrix_unsw_bin.csv`
- `reports/confusion_matrix_unsw_bin.md`
- `reports/confusion_matrix_baseline.csv`
- `reports/confusion_matrix_baseline.md`
- `reports/run_manifest.md`
- `reports/cic/RELATORIO_CIC.md`
- `reports/unsw_bin/RELATORIO_UNSW.md`
- `reports/cic/xai/xai_shap_consolidado.csv` *(legado/complementar)*
- `reports/cic/xai/xai_shap_consolidado.md` *(legado/complementar)*
- `reports/cic/XAI_BRIEF.md` *(legado/complementar)*

### 4.2 Artefatos locais presentes, porém não versionados

- `outputs/eval_cic/preds.csv`, `metrics_eval.json`, `classification_report_eval.csv`, `confusion_matrix_eval.csv`
- `outputs/eval_unsw/preds.csv`, `metrics_eval.json`, `classification_report_eval.csv`, `confusion_matrix_eval.csv`
- `outputs/cic_robust_xgb_baseline/metrics_cic_robust_xgb_baseline.csv`
- `outputs/cic_robust_xgb_baseline/confusion_matrix_cic_robust_xgb_baseline.csv`
- figuras PNG em `reports/cic/` e `reports/unsw_bin/`
- modelos em `artifacts/trained_models/` e pools em `artifacts/feature_pools/`

Diagnóstico: o projeto está suficientemente sustentado para redação técnica interna, mas ainda depende de artefatos locais não versionados para reprodutibilidade externa completa.

## 5. Métricas consolidadas no snapshot atual

### 5.1 GKS no CIC-IDS2018 (7 classes)

Fontes: `outputs/eval_cic/*` e `reports/cic/metrics_again.json`

- F1-macro: **0.7642775701**
- Acurácia: **0.933080**
- n: **100000**
- Latência média total estimada: **21.788869 ms/amostra**

### 5.2 GKS no UNSW-NB15 (binário)

Fontes: `outputs/eval_unsw/*` e `reports/unsw_bin/metrics_again.json`

- F1-macro: **0.8655823711**
- Acurácia: **0.8742678552**
- n: **175341**
- Latência média total estimada: **1.401404 ms/amostra**

### 5.3 Baseline XGBoost no CIC robusto (binário)

Fonte: `outputs/cic_robust_xgb_baseline/*`

- F1-macro: **0.9762390382**
- Acurácia: **0.976280**
- n: **100000**

## 6. Diagnóstico por eixo do paper

| Eixo | Situação atual | Observação |
|---|---|---|
| Cenário principal CIC multiclasse | consolidado | coerente com manuscrito final |
| Cenário secundário UNSW binário | consolidado localmente | coerente com `reports/unsw_bin/` |
| Baseline principal | consolidado e empacotado | suportado por tabela independente em `reports/` |
| Métricas por classe | disponíveis em `outputs/` | artigo já incorpora os valores principais |
| Matriz de confusão absoluta | consolidada | disponível em `outputs/` e promovida para `reports/` em CSV/MD |
| Latência | disponível em `preds.csv` | suficientemente sustentada para discussão atual |
| XAI | parcial e legada | evidência hoje alinhada a CIC binário legado, não ao cenário multiclasse principal |

## 7. Lacunas remanescentes

1. **Artefatos críticos continuam fora do versionamento**: `outputs/` e modelos treinados permanecem locais.
2. **XAI principal não está alinhado ao cenário multiclasse do CIC**: os arquivos atuais referem-se a um snapshot binário legado.
3. **Parte da rastreabilidade continua dependente de artefatos locais**: embora `run_manifest.md` consolide o snapshot atual, os `outputs/` e modelos treinados seguem fora do versionamento.
4. **Governança documental ainda exige manutenção contínua**: `outline`, `checklist`, `plano`, `ficha` e `roteiro` foram reconciliados nesta revisão, mas futuras reexecuções precisam preservar essa sincronização com o snapshot experimental.

## 8. Conclusão da auditoria

No estado atual, o projeto é **tecnicamente suficiente para sustentar o artigo principal com rigor interno**, porque o manuscrito já está alinhado às métricas e matrizes realmente produzidas pelos testes atuais. A pipeline central roda, os cenários principais estão materializados, a documentação auxiliar crítica foi sincronizada com esse estado e as limitações relevantes podem ser declaradas sem recorrer a inferências frágeis.

O ponto fraco remanescente não é mais a ausência de experimento principal, mas a **governança dos artefatos finais**: o que ainda falta para fechamento mais forte é transformar parte do que hoje está apenas em `outputs/` locais em um pacote reprodutível e mais autoexplicativo em `reports/`.
