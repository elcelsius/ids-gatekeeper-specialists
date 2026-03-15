# Roteiro Operacional — Campanha Mínima (CIC + Baseline)

## Escopo desta execução

- Inclui: **CIC multiclasse (7 classes)**, two-stage (gatekeeper + especialistas), avaliação estruturada, métricas/plots e baseline XGBoost robusto.
- Não inclui: **UNSW**.
- Não inclui: **XAI**.
- Objetivo: fechar o núcleo mínimo publicável do paper com cenário principal e baseline comparável.
- Status do snapshot atual: o núcleo CIC + baseline já está materializado em `outputs/eval_cic/`, `reports/cic/` e `outputs/cic_robust_xgb_baseline/`; este roteiro serve agora tanto para reexecução quanto para auditoria.

## Convenções

- Executar na raiz do repositório.
- Onde houver CLI, usar preferencialmente o comando via módulo Python (`python -m ...`), que está **confirmado pelos arquivos em `src/twodaef/`**.
- Os comandos curtos (`gatekeeper-train`, `train-specialists`, etc.) são **prováveis** (dependem de instalação do pacote com entrypoints).

---

## Checklist operacional executável

## Fase 0 — Pré-condições

### [ ] 0.1 Verificar dados brutos CIC
- **Script/CLI:** validação manual
- **Comando:** `Get-ChildItem data\raw\cicids2018\*.csv`
- **Status do comando:** confirmado
- **Entradas esperadas:** CSVs brutos do CIC em `data/raw/cicids2018/`
- **Saídas esperadas:** listagem de arquivos
- **Dependência:** nenhuma
- **Critério de sucesso:** há arquivos `.csv` disponíveis

---

## Fase 1 — Cenário principal (CIC multiclasse)

### [ ] 1.1 Preparação CIC multiclasse (treino + infer)
- **Script/CLI:** `scripts/prep_cic_train.py`
- **Comando (confirmado):**
```powershell
python scripts/prep_cic_train.py
```
- **Entradas esperadas:** `data/raw/cicids2018/*.csv`
- **Saídas esperadas:** `data/train_cic.csv`, `data/cic_infer.csv`
- **Dependência:** Fase 0 concluída
- **Critério de sucesso:** os dois arquivos são gerados e `train_cic.csv` contém coluna `label`

### [ ] 1.2 Preparação CIC multiclasse (avaliação)
- **Script/CLI:** `scripts/make_cic_eval.py`
- **Comando (confirmado):**
```powershell
python scripts/make_cic_eval.py
```
- **Entradas esperadas:** `data/train_cic.csv`
- **Saídas esperadas:** `data/cic_eval.csv`
- **Dependência:** 1.1
- **Critério de sucesso:** `data/cic_eval.csv` existe e contém coluna `label`

### [ ] 1.3 (Re)gerar colunas do gatekeeper CIC
- **Script/CLI:** `scripts/make_gatekeeper_cols_from_csv.py`
- **Comando (confirmado):**
```powershell
python scripts/make_gatekeeper_cols_from_csv.py `
  --csv data/train_cic.csv `
  --out configs/cols/gatekeeper_cic_cols.txt `
  --max_cols 12
```
- **Entradas esperadas:** `data/train_cic.csv`
- **Saídas esperadas:** `configs/cols/gatekeeper_cic_cols.txt`
- **Dependência:** 1.1
- **Critério de sucesso:** arquivo de features existe e não está vazio

### [ ] 1.4 Treinar gatekeeper CIC
- **Script/CLI:** `twodaef.cli_train_gatekeeper`
- **Comando (confirmado):**
```powershell
python -m twodaef.cli_train_gatekeeper `
  --train_csv data/train_cic.csv `
  --target_col label `
  --features configs/cols/gatekeeper_cic_cols.txt `
  --model_out artifacts/trained_models/gatekeeper_cic.joblib
```
- **Comando provável (entrypoint):**
```powershell
gatekeeper-train `
  --train_csv data/train_cic.csv `
  --target_col label `
  --features configs/cols/gatekeeper_cic_cols.txt `
  --model_out artifacts/trained_models/gatekeeper_cic.joblib
```
- **Entradas esperadas:** `data/train_cic.csv`, `configs/cols/gatekeeper_cic_cols.txt`
- **Saídas esperadas:** `artifacts/trained_models/gatekeeper_cic.joblib`
- **Dependência:** 1.3
- **Critério de sucesso:** modelo salvo no caminho definido

### [ ] 1.5 Gerar feature pool CIC (para especialistas)
- **Script/CLI:** `scripts/make_feature_pool_min.py`
- **Comando (confirmado):**
```powershell
python scripts/make_feature_pool_min.py `
  --in data/train_cic.csv `
  --out artifacts/feature_pools/feature_pool_cic.json `
  --target label `
  --max_per_set 20
```
- **Entradas esperadas:** `data/train_cic.csv`
- **Saídas esperadas:** `artifacts/feature_pools/feature_pool_cic.json`
- **Dependência:** 1.1
- **Critério de sucesso:** JSON existe com chave `feature_sets`

### [ ] 1.6 Treinar especialistas CIC
- **Script/CLI:** `twodaef.cli_train_specialists`
- **Comando (confirmado):**
```powershell
python -m twodaef.cli_train_specialists `
  --train_csv data/train_cic.csv `
  --target_col label `
  --feature_pool_json artifacts/feature_pools/feature_pool_cic.json `
  --out_dir artifacts/trained_models/specialists_cic `
  --map_path configs/mappings/specialist_map_cic.json `
  --models auto
```
- **Comando provável (entrypoint):**
```powershell
train-specialists `
  --train_csv data/train_cic.csv `
  --target_col label `
  --feature_pool_json artifacts/feature_pools/feature_pool_cic.json `
  --out_dir artifacts/trained_models/specialists_cic `
  --map_path configs/mappings/specialist_map_cic.json `
  --models auto
```
- **Entradas esperadas:** treino CIC + feature pool
- **Saídas esperadas:** modelos em `artifacts/trained_models/specialists_cic/` e mapa `configs/mappings/specialist_map_cic.json`
- **Dependência:** 1.5
- **Critério de sucesso:** mapa possui `specialists` não vazio e os `model_path` existem

### [ ] 1.7 Inferência two-stage CIC
- **Script/CLI:** `twodaef.cli_infer_twostage`
- **Comando (confirmado):**
```powershell
python -m twodaef.cli_infer_twostage `
  --gatekeeper_model artifacts/trained_models/gatekeeper_cic.joblib `
  --gatekeeper_features configs/cols/gatekeeper_cic_cols.txt `
  --specialist_map configs/mappings/specialist_map_cic.json `
  --input_csv data/cic_eval.csv `
  --output_csv outputs/eval_cic/preds.csv `
  --fill_missing 0.0
```
- **Entradas esperadas:** modelo gatekeeper + mapa especialistas + `data/cic_eval.csv`
- **Saídas esperadas:** `outputs/eval_cic/preds.csv`
- **Dependência:** 1.6
- **Critério de sucesso:** `preds.csv` existe com `pred_final` e colunas de latência (`latency_ms_stage1`, `latency_ms_stage2`, `latency_ms_total_est`)

### [ ] 1.8 Avaliação estruturada CIC
- **Script/CLI:** `twodaef.cli_eval_twostage`
- **Comando (confirmado):**
```powershell
python -m twodaef.cli_eval_twostage `
  --gatekeeper_model artifacts/trained_models/gatekeeper_cic.joblib `
  --gatekeeper_features configs/cols/gatekeeper_cic_cols.txt `
  --specialist_map configs/mappings/specialist_map_cic.json `
  --input_csv data/cic_eval.csv `
  --label_col label `
  --output_dir outputs/eval_cic `
  --fill_missing 0.0
```
- **Entradas esperadas:** `outputs/eval_cic/preds.csv` (pré-requisito implícito da CLI)
- **Saídas esperadas:** `outputs/eval_cic/metrics_eval.json`, `outputs/eval_cic/confusion_matrix_eval.csv`, `outputs/eval_cic/classification_report_eval.csv`
- **Dependência:** 1.7
- **Critério de sucesso:** os três artefatos existem e `metrics_eval.json` contém `f1_macro` e `accuracy`

### [ ] 1.9 Métricas agregadas + gráficos CIC
- **Script/CLI:** `twodaef.cli_plot_eval`
- **Comando (confirmado):**
```powershell
python -m twodaef.cli_plot_eval `
  --preds_csv outputs/eval_cic/preds.csv `
  --label_col label `
  --out_dir reports/cic `
  --dataset_tag cic
```
- **Entradas esperadas:** `outputs/eval_cic/preds.csv`
- **Saídas esperadas:** `reports/cic/metrics_again.json`, `reports/cic/confusion_matrix_cic.png`, `reports/cic/f1_per_class_cic.png`
- **Dependência:** 1.7
- **Critério de sucesso:** os três artefatos são gerados

---

## Fase 2 — Bloco robusto + baseline (comparação auxiliar)

> Justificativa: o baseline disponível no projeto (`baseline_xgb_cic_robust.py`) usa `train_cic_robust`/`cic_eval_robust`.  
> Executar o two-stage no mesmo recorte robusto ajuda a isolar o efeito da remoção de `dst_port`, mas **não** torna a comparação estritamente simétrica, porque o two-stage permanece multiclasse e o baseline continua binário.

### [ ] 2.1 Gerar recorte robusto CIC
- **Script/CLI:** `scripts/prep_cic_robust.py`
- **Comando (confirmado):**
```powershell
python scripts/prep_cic_robust.py
```
- **Entradas esperadas:** `data/train_cic.csv`, `data/cic_eval.csv`
- **Saídas esperadas:** `data/train_cic_robust.csv`, `data/cic_eval_robust.csv`
- **Dependência:** 1.2
- **Critério de sucesso:** arquivos robustos existem

### [ ] 2.2 (Re)gerar colunas do gatekeeper robusto
- **Script/CLI:** `scripts/make_gatekeeper_cols_from_csv.py`
- **Comando (confirmado):**
```powershell
python scripts/make_gatekeeper_cols_from_csv.py `
  --csv data/train_cic_robust.csv `
  --out configs/cols/gatekeeper_cic_robust_cols.txt `
  --max_cols 20
```
- **Entradas esperadas:** `data/train_cic_robust.csv`
- **Saídas esperadas:** `configs/cols/gatekeeper_cic_robust_cols.txt`
- **Dependência:** 2.1
- **Critério de sucesso:** arquivo de features robusto existe e não está vazio

### [ ] 2.3 Gerar feature pool robusto
- **Script/CLI:** `scripts/make_feature_pool_min.py`
- **Comando (confirmado):**
```powershell
python scripts/make_feature_pool_min.py `
  --in data/train_cic_robust.csv `
  --out artifacts/feature_pools/feature_pool_cic_robust.json `
  --target label `
  --max_per_set 20
```
- **Entradas esperadas:** `data/train_cic_robust.csv`
- **Saídas esperadas:** `artifacts/feature_pools/feature_pool_cic_robust.json`
- **Dependência:** 2.1
- **Critério de sucesso:** JSON existe com `feature_sets`

### [ ] 2.4 Treinar gatekeeper robusto
- **Script/CLI:** `twodaef.cli_train_gatekeeper`
- **Comando (confirmado):**
```powershell
python -m twodaef.cli_train_gatekeeper `
  --train_csv data/train_cic_robust.csv `
  --target_col label `
  --features configs/cols/gatekeeper_cic_robust_cols.txt `
  --model_out artifacts/trained_models/gatekeeper_cic_robust.joblib
```
- **Entradas esperadas:** treino robusto + cols robustas
- **Saídas esperadas:** `artifacts/trained_models/gatekeeper_cic_robust.joblib`
- **Dependência:** 2.2
- **Critério de sucesso:** modelo salvo

### [ ] 2.5 Treinar especialistas robustos
- **Script/CLI:** `twodaef.cli_train_specialists`
- **Comando (confirmado):**
```powershell
python -m twodaef.cli_train_specialists `
  --train_csv data/train_cic_robust.csv `
  --target_col label `
  --feature_pool_json artifacts/feature_pools/feature_pool_cic_robust.json `
  --out_dir artifacts/trained_models/specialists_cic_robust `
  --map_path configs/mappings/specialist_map_cic_robust.json `
  --models auto
```
- **Entradas esperadas:** treino robusto + pool robusto
- **Saídas esperadas:** especialistas robustos + `configs/mappings/specialist_map_cic_robust.json`
- **Dependência:** 2.3
- **Critério de sucesso:** mapa robusto preenchido e `model_path` existentes

### [ ] 2.6 Inferência two-stage robusta
- **Script/CLI:** `twodaef.cli_infer_twostage`
- **Comando (confirmado):**
```powershell
python -m twodaef.cli_infer_twostage `
  --gatekeeper_model artifacts/trained_models/gatekeeper_cic_robust.joblib `
  --gatekeeper_features configs/cols/gatekeeper_cic_robust_cols.txt `
  --specialist_map configs/mappings/specialist_map_cic_robust.json `
  --input_csv data/cic_eval_robust.csv `
  --output_csv outputs/cic_robust/preds.csv `
  --fill_missing 0.0
```
- **Entradas esperadas:** modelos robustos + `data/cic_eval_robust.csv`
- **Saídas esperadas:** `outputs/cic_robust/preds.csv`
- **Dependência:** 2.5
- **Critério de sucesso:** `preds.csv` robusto com `pred_final` e latências

### [ ] 2.7 Avaliação estruturada robusta
- **Script/CLI:** `twodaef.cli_eval_twostage`
- **Comando (confirmado):**
```powershell
python -m twodaef.cli_eval_twostage `
  --gatekeeper_model artifacts/trained_models/gatekeeper_cic_robust.joblib `
  --gatekeeper_features configs/cols/gatekeeper_cic_robust_cols.txt `
  --specialist_map configs/mappings/specialist_map_cic_robust.json `
  --input_csv data/cic_eval_robust.csv `
  --label_col label `
  --output_dir outputs/cic_robust `
  --fill_missing 0.0
```
- **Entradas esperadas:** `outputs/cic_robust/preds.csv`
- **Saídas esperadas:** `outputs/cic_robust/metrics_eval.json`, `confusion_matrix_eval.csv`, `classification_report_eval.csv`
- **Dependência:** 2.6
- **Critério de sucesso:** artefatos estruturados robustos gerados

### [ ] 2.8 Métricas/plots robustos (two-stage)
- **Script/CLI:** `twodaef.cli_plot_eval`
- **Comando (confirmado):**
```powershell
python -m twodaef.cli_plot_eval `
  --preds_csv outputs/cic_robust/preds.csv `
  --label_col label `
  --out_dir reports/cic_robust `
  --dataset_tag cic_robust
```
- **Entradas esperadas:** `outputs/cic_robust/preds.csv`
- **Saídas esperadas:** `reports/cic_robust/metrics_again.json`, `confusion_matrix_cic_robust.png`, `f1_per_class_cic_robust.png`
- **Dependência:** 2.6
- **Critério de sucesso:** métricas agregadas + figuras robustas disponíveis

### [ ] 2.9 Executar baseline XGBoost (robusto)
- **Script/CLI:** `scripts/baseline_xgb_cic_robust.py`
- **Comando (confirmado):**
```powershell
python scripts/baseline_xgb_cic_robust.py
```
- **Entradas esperadas:** `data/train_cic_robust.csv`, `data/cic_eval_robust.csv`
- **Saídas esperadas:** `outputs/cic_robust_xgb_baseline/metrics_cic_robust_xgb_baseline.csv`, `outputs/cic_robust_xgb_baseline/confusion_matrix_cic_robust_xgb_baseline.csv`
- **Dependência:** 2.1
- **Critério de sucesso:** dois arquivos do baseline gerados

---

## Fase 3 — Fechamento mínimo da campanha (sem UNSW/XAI)

### [ ] 3.1 Verificar núcleo principal do paper (CIC)
- **Script/CLI:** validação manual
- **Comando (confirmado):**
```powershell
Get-ChildItem outputs/eval_cic, reports/cic -File
```
- **Entradas esperadas:** artefatos da Fase 1
- **Saídas esperadas:** listagem de arquivos de avaliação e relatório
- **Dependência:** Fase 1 completa
- **Critério de sucesso:** existem `preds.csv`, `metrics_eval.json`, `classification_report_eval.csv`, `confusion_matrix_eval.csv`, `metrics_again.json`, matriz PNG e F1 PNG

### [ ] 3.2 Verificar bloco comparável (two-stage robusto + baseline)
- **Script/CLI:** validação manual
- **Comando (confirmado):**
```powershell
Get-ChildItem outputs/cic_robust, outputs/cic_robust_xgb_baseline, reports/cic_robust -File
```
- **Entradas esperadas:** artefatos da Fase 2
- **Saídas esperadas:** listagem de artefatos comparáveis
- **Dependência:** Fase 2 completa
- **Critério de sucesso:** existem métricas estruturadas do two-stage robusto e métricas/matriz do baseline robusto

### [ ] 3.3 Consolidação comparativa final (tabela)
- **Script/CLI:** **precisa confirmar argumentos**
- **Motivo:** não há, no estado atual auditado, um script único já fechado para consolidar automaticamente `outputs/cic_robust/metrics_eval.json` + `outputs/cic_robust_xgb_baseline/metrics_*.csv` em tabela final pronta do paper.
- **Ação conservadora:** consolidar manualmente em `.md/.csv` a partir dos artefatos da Fase 2, ou criar script específico antes de automatizar.
- **Dependência:** 2.8 e 2.9
- **Critério de sucesso:** tabela comparativa final (two-stage robusto vs baseline XGB robusto) publicada em `reports/` ou `artigo/`.

---

## Resumo de comandos com maior segurança

- **Confirmados (por código):**
  - `python scripts/prep_cic_train.py`
  - `python scripts/make_cic_eval.py`
  - `python scripts/prep_cic_robust.py`
  - `python scripts/make_gatekeeper_cols_from_csv.py ...`
  - `python scripts/make_feature_pool_min.py ...`
  - `python -m twodaef.cli_train_gatekeeper ...`
  - `python -m twodaef.cli_train_specialists ...`
  - `python -m twodaef.cli_infer_twostage ...`
  - `python -m twodaef.cli_eval_twostage ...`
  - `python -m twodaef.cli_plot_eval ...`
  - `python scripts/baseline_xgb_cic_robust.py`

- **Prováveis (dependem de entrypoints instalados):**
  - `gatekeeper-train ...`
  - `train-specialists ...`
  - `infer-twostage ...`
  - `eval-twostage ...`
  - `plot-eval ...`
