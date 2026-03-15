# Confusion Matrix UNSW Bin

Matriz de confusao tabular do cenario complementar (GKS no UNSW-NB15 binario), derivada diretamente de `outputs/eval_unsw/preds.csv`.

| true_label | pred_Normal | pred_Attack | row_total |
| --- | --- | --- | --- |
| Normal | 54362 | 1638 | 56000 |
| Attack | 20408 | 98933 | 119341 |
| col_total | 74770 | 100571 | 175341 |

Notas:
- A ordem das classes foi normalizada para Normal, Attack, alinhada ao manuscrito atual.
