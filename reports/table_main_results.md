# Table Main Results

Tabela consolidada a partir dos artefatos atuais do snapshot local.

| Metodo | Dataset | Formulacao | Precision_macro | Recall_macro | F1_macro | Acuracia | n | Lat_total_ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GKS | CIC-IDS2018 | Multiclasse (7 classes) | 0.814 | 0.743 | 0.764 | 0.933 | 100000 | 21.789 |
| GKS | UNSW-NB15 | Binaria | 0.855 | 0.900 | 0.866 | 0.874 | 175341 | 1.401 |
| XGBoost global | CIC-IDS2018 robust | Binaria robusta | 0.976 | 0.977 | 0.976 | 0.976 | 100000 | NA |

Fontes principais:
- `reports/cic/metrics_again.json` e `outputs/eval_cic/preds.csv`.
- `reports/unsw_bin/metrics_again.json` e `outputs/eval_unsw/preds.csv`.
- `outputs/cic_robust_xgb_baseline/metrics_cic_robust_xgb_baseline.csv`.

Observacoes:
- O baseline robusto nao possui latencia registrada no snapshot atual.
- A comparacao entre GKS no CIC e baseline XGBoost continua metodologicamente assimetrica porque compara 7 classes contra 2 classes.
