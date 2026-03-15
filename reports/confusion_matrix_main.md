# Confusion Matrix Main

Matriz de confusao tabular do cenario principal do paper (GKS no CIC-IDS2018 multiclasse), derivada diretamente de `outputs/eval_cic/preds.csv`.

| true_label | pred_Benign | pred_Bot | pred_BruteForce | pred_DDoS | pred_DoS | pred_Others | pred_Web | row_total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Benign | 46978 | 0 | 0 | 0 | 0 | 0 | 5 | 46983 |
| Bot | 1033 | 2874 | 0 | 0 | 0 | 0 | 0 | 3907 |
| BruteForce | 1 | 0 | 4953 | 0 | 5044 | 0 | 0 | 9998 |
| DDoS | 3 | 0 | 0 | 19996 | 0 | 0 | 0 | 19999 |
| DoS | 269 | 0 | 323 | 0 | 18506 | 0 | 14 | 19112 |
| Others | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| Web | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| col_total | 48284 | 2874 | 5276 | 19996 | 23550 | 1 | 19 | 100000 |

Notas:
- A ordem das classes segue o manuscrito: Benign, Bot, BruteForce, DDoS, DoS, Others, Web.
- A classe Web permanece com suporte zero no holdout atual, por isso sua linha e sua coluna aparecem zeradas.
