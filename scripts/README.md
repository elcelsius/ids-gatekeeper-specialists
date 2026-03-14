# scripts/

Índice de todos os scripts utilitários do projeto, com finalidade, entradas,
saídas e status atual.

---

## Download de datasets

| Script | Dataset | Saída | Observações |
|---|---|---|---|
| `download_cicids2018.py` | CIC-IDS2018 | `data/raw/cicids2018/*.csv` | Kaggle: `solarmainframe/ids-intrusion-csv` |
| `download_unsw.py` | UNSW-NB15 | `data/raw/unsw/*.csv` | Kaggle: `mrwellsdavid/unsw-nb15` |

---

## Preparação de dados

| Script | Dataset | Entradas | Saídas | Observações |
|---|---|---|---|---|
| `prep_cic_train.py` | CIC-IDS2018 | `data/raw/cicids2018/*.csv` | `data/train_cic.csv`, `data/cic_infer.csv` | Treino principal; `TRAIN_SEED=42` |
| `make_cic_eval.py` | CIC-IDS2018 | `data/raw/cicids2018/*.csv` | `data/cic_eval.csv` | Holdout sem leakage; `EVAL_SEED=123` — **rodar após `prep_cic_train.py`** |
| `prep_cic_robust.py` | CIC-IDS2018 | `data/train_cic.csv`, `data/cic_eval.csv` | `data/train_cic_robust.csv`, `data/cic_eval_robust.csv` | Remove coluna `dst_port` |
| `prep_unsw_binary.py` | UNSW-NB15 | `data/raw/unsw/*.csv` | `data/train_unsw.csv`, `data/unsw_eval.csv`, `data/unsw_infer.csv` | Modo preferencial usa split oficial; fallback 80/20; remove metadados (`id`, IP/porta de identificação quando presentes) |
| `prep_unsw_multiclass.py` | UNSW-NB15 | `data/raw/unsw/*.csv` | `data/UNSW_train_mc.csv`, `data/UNSW_test_mc.csv` | Multiclasse — fora do escopo principal do paper |

---

## Configuração de features

| Script | Finalidade | Entradas | Saídas |
|---|---|---|---|
| `make_gatekeeper_cols_from_csv.py` | Seleciona colunas para o gatekeeper via importância | CSV de treino | `configs/cols/*.txt` |
| `make_feature_pool_min.py` | Gera pool mínimo de features para especialistas | CSV de treino | `artifacts/feature_pools/*.json` |

---

## Baseline

| Script | Finalidade | Entradas | Saídas |
|---|---|---|---|
| `baseline_xgb_cic_robust.py` | XGBoost monolítico no CIC robusto (baseline do paper) | `data/train_cic_robust.csv`, `data/cic_eval_robust.csv` | `outputs/cic_robust_xgb_baseline/` |

---

## Plots e análise

| Script | Finalidade | Entradas | Saídas | Status |
|---|---|---|---|---|
| `aggregate_metrics.py` | Consolida métricas entre datasets | `reports/*/metrics_again.json` | `reports/metrics_comparados.csv` | Ativo — verificar snapshot UNSW |
| `plot_latency_cic_robust.py` | Gráfico de latência | `outputs/cic_robust/preds.csv` | `figs/` | Auxiliar |
| `plot_ablation_cic_robust.py` | Gráfico de ablação de features | `outputs/` CSVs | `figs/` | Auxiliar |
| `plot_confusion_cic_robust.py` | Matriz de confusão CIC robusto | `outputs/cic_robust/*.csv` | `figs/` | Legado — preferir `cli_plot_eval` |
| `plot_confusion_unsw_mc.py` | Matriz UNSW multiclasse | `outputs/unsw_mc/*.csv` | `figs/` | Fora do escopo do paper |
| `plot_shap_cic_robust.py` | SHAP global para baseline XGB | dados robustos | `figs/` | Auxiliar |
| `make_xai_brief.py` | Gera resumo textual do SHAP consolidado | CSV consolidado | `XAI_BRIEF.md` | Ativo |

---

## Testes e sanidade

| Script | Finalidade | Observações |
|---|---|---|
| `smoke_test.ps1` | Teste rápido com dados sintéticos | Útil para CI — não gera evidências reais |
| `smoke_test_multiclass.py` | Smoke end-to-end multiclasse | Dados toy — fora do escopo do paper |

---

## Obsoletos

| Script | Motivo |
|---|---|
| `agrupar_arquivos.ps1` | Caminho hardcoded de outra máquina — não usar |

---

## Ordem de execução recomendada (campanha do paper)

```powershell
# 1. Download
python scripts\download_cicids2018.py
python scripts\download_unsw.py

# 2. Preparação CIC
python scripts\prep_cic_train.py
python scripts\make_cic_eval.py
python scripts\prep_cic_robust.py

# 3. Preparação UNSW
python scripts\prep_unsw_binary.py

# 4. Features (CIC e UNSW)
python scripts\make_gatekeeper_cols_from_csv.py --csv data\train_cic.csv ...
python scripts\make_feature_pool_min.py ...

# 5–10. Pipeline principal via CLIs em src/twodaef/
# Ver docs/WORKFLOW.md para comandos completos
```

---

## Convenções de código

- Todos os scripts usam `from __future__ import annotations` e `pathlib.Path`
- Nomes de colunas são normalizados via `snake_case` antes de qualquer operação
- Seeds documentadas no topo de cada script: `TRAIN_SEED`, `EVAL_SEED`
- Erros de leitura de CSV são tratados com `[WARN]` e o script continua
- Saídas são sempre prefixadas com `[OK]`, `[WARN]` ou `[ERRO]`
