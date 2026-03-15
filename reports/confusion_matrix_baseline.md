# Confusion Matrix Baseline

Matriz de confusao tabular do baseline XGBoost robusto no CIC, consolidada a partir de `outputs/cic_robust_xgb_baseline/confusion_matrix_cic_robust_xgb_baseline.csv`.

| true_label | pred_Benign | pred_Attack | row_total |
| --- | --- | --- | --- |
| Benign | 46738 | 245 | 46983 |
| Attack | 2127 | 50890 | 53017 |
| col_total | 48865 | 51135 | 100000 |

Notas:
- Esta matriz corresponde ao baseline binario robusto sem `dst_port`.
- Ela nao e estritamente comparavel a classe-a-classe com o GKS principal, porque o GKS oficial permanece multiclasse.
