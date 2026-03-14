# 2D-AEF — Fluxo de Desenvolvimento, Treinamento e Avaliação
Versão: v0.2.0

Este documento descreve, ponta-a-ponta, as **etapas do projeto** — desde a
preparação dos dados até a publicação de resultados (métricas, XAI e relatórios).
Todos os comandos são relativos à raiz do repositório.

---

## Visão Geral das Etapas

1. **Baixar datasets** — scripts dedicados por dataset em `scripts/`
2. **Preparar dados** — splits de treino / holdout / infer sem leakage
3. **Feature Pool** — geração de conjuntos candidatos de atributos para especialistas
4. **Treinar Gatekeeper** — classificador de triagem rápida
5. **Treinar Especialistas** — busca do melhor par (modelo + features) por classe
6. **Inferência two-stage** — gatekeeper → especialista → `preds.csv`
7. **Avaliação** — métricas, matriz de confusão, F1 por classe
8. **Plots** — figuras para o paper
9. **XAI** — interpretabilidade por especialista (SHAP/LIME)
10. **Relatórios** — consolidação em `reports/`

> Pastas `data/`, `artifacts/` e `outputs/` **não são versionadas**.
> Cada uma contém um `README.md` com instruções de reprodução.

---

## 1) Download dos Datasets

### CIC-IDS2018

```powershell
python scripts\download_cicids2018.py
```

Salva CSVs brutos em `data\raw\cicids2018\`.
Requer credencial Kaggle em `%USERPROFILE%\.kaggle\kaggle.json`.

### UNSW-NB15

```powershell
python scripts\download_unsw.py
```

Salva CSVs em `data\raw\unsw\`.
Dataset Kaggle: `mrwellsdavid/unsw-nb15`.
Inclui os arquivos oficiais `UNSW_NB15_training-set.csv` e `UNSW_NB15_testing-set.csv`.

---

## 2) Preparação de Dados

> **Importante — anti-leakage:** treino e holdout de avaliação são gerados
> a partir dos **dados brutos**, nunca um a partir do outro.
> Seeds documentadas: treino `TRAIN_SEED=42`, holdout `EVAL_SEED=123`.

### CIC-IDS2018 (cenário principal)

```powershell
# Passo 1 — gera treino + amostra de inferência
python scripts\prep_cic_train.py

# Passo 2 — gera holdout de avaliação (lê brutos, NÃO lê train_cic.csv)
python scripts\make_cic_eval.py
```

Artefatos gerados:

| Arquivo | Linhas aprox. | Uso |
|---|---|---|
| `data\train_cic.csv` | 300 000 | treino do gatekeeper e especialistas |
| `data\cic_eval.csv` | 100 000 | holdout de avaliação (sem sobreposição) |
| `data\cic_infer.csv` | 1 000 | inferência rápida / smoke test |

Recorte robusto (remove `dst_port`, usado no baseline XGBoost):

```powershell
python scripts\prep_cic_robust.py
```

Gera `data\train_cic_robust.csv` e `data\cic_eval_robust.csv`.

### UNSW-NB15 (cenário secundário)

```powershell
python scripts\prep_unsw_binary.py
```

O script detecta automaticamente o modo de operação:

- **Modo preferencial** — usa `UNSW_NB15_training-set.csv` como treino e
  `UNSW_NB15_testing-set.csv` como holdout (split oficial do dataset).
- **Fallback** — se os arquivos oficiais não estiverem presentes, concatena
  os brutos `UNSW-NB15_1.csv` a `UNSW-NB15_4.csv` e aplica split 80/20
  estratificado.

Artefatos gerados:

| Arquivo | Linhas aprox. | Uso |
|---|---|---|
| `data\train_unsw.csv` | ~175 000 | treino do gatekeeper e especialistas |
| `data\unsw_eval.csv` | ~82 000 | holdout de avaliação (sem sobreposição) |
| `data\unsw_infer.csv` | 1 000 | inferência rápida / smoke test |

Rótulos: `Normal` / `Attack`.

---

## 3) Gerar Feature Pool

```powershell
# CIC
python -m twodaef.cli_make_feature_pool `
  --csv data\train_cic.csv `
  --target_col label `
  --max_features_per_set 20 `
  --total_sets 30 `
  --seed 42 `
  --out_json artifacts\feature_pools\feature_pool_cic.json

# UNSW
python -m twodaef.cli_make_feature_pool `
  --csv data\train_unsw.csv `
  --target_col label `
  --max_features_per_set 20 `
  --total_sets 30 `
  --seed 42 `
  --out_json artifacts\feature_pools\feature_pool_unsw.json
```

---

## 4) Treinar Gatekeeper

```powershell
# CIC
python -m twodaef.cli_train_gatekeeper `
  --train_csv data\train_cic.csv `
  --target_col label `
  --features configs\cols\gatekeeper_cic_cols.txt `
  --model_out artifacts\trained_models\gatekeeper_cic.joblib

# UNSW
python -m twodaef.cli_train_gatekeeper `
  --train_csv data\train_unsw.csv `
  --target_col label `
  --features configs\cols\gatekeeper_unsw_cols.txt `
  --model_out artifacts\trained_models\gatekeeper_unsw.joblib
```

Para gerar os arquivos `.txt` de colunas automaticamente:

```powershell
python scripts\make_gatekeeper_cols_from_csv.py `
  --csv data\train_cic.csv `
  --out configs\cols\gatekeeper_cic_cols.txt `
  --max_cols 12
```

---

## 5) Treinar Especialistas

```powershell
# CIC
python -m twodaef.cli_train_specialists `
  --train_csv data\train_cic.csv `
  --target_col label `
  --feature_pool_json artifacts\feature_pools\feature_pool_cic.json `
  --out_dir artifacts\trained_models\specialists_cic `
  --map_path configs\mappings\specialist_map_cic.json `
  --test_size 0.2 `
  --seed 42 `
  --models auto

# UNSW
python -m twodaef.cli_train_specialists `
  --train_csv data\train_unsw.csv `
  --target_col label `
  --feature_pool_json artifacts\feature_pools\feature_pool_unsw.json `
  --out_dir artifacts\trained_models\specialists_unsw `
  --map_path configs\mappings\specialist_map_unsw.json `
  --test_size 0.2 `
  --seed 42 `
  --models auto
```

---

## 6) Inferência Two-Stage

```powershell
# CIC
python -m twodaef.cli_infer_twostage `
  --gatekeeper_model artifacts\trained_models\gatekeeper_cic.joblib `
  --gatekeeper_features configs\cols\gatekeeper_cic_cols.txt `
  --specialist_map configs\mappings\specialist_map_cic.json `
  --input_csv data\cic_eval.csv `
  --output_csv outputs\eval_cic\preds.csv `
  --fill_missing 0.0

# UNSW
python -m twodaef.cli_infer_twostage `
  --gatekeeper_model artifacts\trained_models\gatekeeper_unsw.joblib `
  --gatekeeper_features configs\cols\gatekeeper_unsw_cols.txt `
  --specialist_map configs\mappings\specialist_map_unsw.json `
  --input_csv data\unsw_eval.csv `
  --output_csv outputs\eval_unsw\preds.csv `
  --fill_missing 0.0
```

---

## 7) Avaliação

```powershell
# CIC
python -m twodaef.cli_eval_twostage `
  --gatekeeper_model artifacts\trained_models\gatekeeper_cic.joblib `
  --gatekeeper_features configs\cols\gatekeeper_cic_cols.txt `
  --specialist_map configs\mappings\specialist_map_cic.json `
  --input_csv data\cic_eval.csv `
  --label_col label `
  --output_dir outputs\eval_cic `
  --fill_missing 0.0

# UNSW
python -m twodaef.cli_eval_twostage `
  --gatekeeper_model artifacts\trained_models\gatekeeper_unsw.joblib `
  --gatekeeper_features configs\cols\gatekeeper_unsw_cols.txt `
  --specialist_map configs\mappings\specialist_map_unsw.json `
  --input_csv data\unsw_eval.csv `
  --label_col label `
  --output_dir outputs\eval_unsw `
  --fill_missing 0.0
```

Artefatos gerados em `outputs/<exp>/`:
- `preds.csv`
- `metrics_eval.json`
- `confusion_matrix_eval.csv`
- `classification_report_eval.csv`

---

## 8) Plots

```powershell
# CIC
python -m twodaef.cli_plot_eval `
  --preds_csv outputs\eval_cic\preds.csv `
  --label_col label `
  --out_dir reports\cic `
  --dataset_tag cic

# UNSW
python -m twodaef.cli_plot_eval `
  --preds_csv outputs\eval_unsw\preds.csv `
  --label_col label `
  --out_dir reports\unsw_bin `
  --dataset_tag unsw_bin
```

Artefatos gerados em `reports/<dataset>/`:
- `confusion_matrix_<tag>.png`
- `f1_per_class_<tag>.png`
- `metrics_again.json`

---

## 9) XAI

```powershell
# Por classe (exemplo CIC — repetir para cada classe)
python -m twodaef.cli_explain_specialist `
  --specialist_map configs\mappings\specialist_map_cic.json `
  --class_key Benign `
  --input_csv data\cic_eval.csv `
  --output_dir outputs\xai_cic `
  --limit_samples 200 `
  --top_k_global 12 `
  --top_k_local 12

# Consolidação
python -m twodaef.cli_xai_aggregate `
  --xai_root outputs\xai_cic `
  --out_dir reports\cic\xai
```

Artefatos: `xai_shap_consolidado.csv`, `xai_shap_consolidado.md`.

---

## 10) Baseline XGBoost

```powershell
python scripts\baseline_xgb_cic_robust.py
```

Saídas em `outputs\cic_robust_xgb_baseline\`:
- `metrics_cic_robust_xgb_baseline.csv`
- `confusion_matrix_cic_robust_xgb_baseline.csv`

---

## Troubleshooting

| Problema | Solução |
|---|---|
| Rótulos divergentes (`0/1` vs `Normal/Attack`) | `plot-eval` alinha automaticamente; ou normalize antes com `map_label_unsw()` |
| SHAP + XGBoost: erro de `base_score` | Use `algorithm="permutation"` no Explainer |
| Latência aparece como `0.000` | Normal para amostras pequenas — use totais por batch |
| `make_cic_eval.py` gera dados iguais ao treino | **Erro de versão antiga** — certifique-se de usar a versão ≥ v0.2.0 que lê os brutos |

---

## Como Adicionar um Novo Dataset

1. Criar `scripts/download_<novo>.py` para aquisição dos dados brutos
2. Criar `scripts/prep_<novo>_binary.py` com split treino/holdout sem leakage
3. Gerar feature pool, gatekeeper cols e specialist map nos caminhos de `configs/`
4. Seguir etapas 3–10 acima
5. Documentar em `reports/<novo>/RELATORIO_<NOVO>.md`

---

## Referências Internas

- `docs/ARCHITECTURE.md` — diagrama e visão macro da arquitetura
- `README.md` — setup rápido e pré-requisitos
- `data/README.md` — estrutura e política de versionamento dos dados
- `scripts/README.md` — índice e descrição de todos os scripts
- `artigo/checklist_execucao_experimental.md` — checklist da campanha do paper
- `artigo/plano_mestre_execucao_experimental.md` — plano mestre experimental
