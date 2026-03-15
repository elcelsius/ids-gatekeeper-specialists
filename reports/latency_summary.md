# Latency Summary

Resumo de latencia derivado dos artefatos atuais de predicao.

| Metodo | Dataset | Formulacao | Lat_stage1_ms | Lat_stage2_ms | Lat_total_ms | Observacao |
| --- | --- | --- | --- | --- | --- | --- |
| GKS | CIC-IDS2018 | multiclasse (7 classes) | 0.000 | 21.789 | 21.789 | Latencia dominada pelo especialista. |
| GKS | UNSW-NB15 | binaria | 0.000 | 1.401 | 1.401 | Latencia dominada pelo especialista. |
| XGBoost global | CIC-IDS2018 robust | binaria robusta | NA | NA | NA | Nao ha medicao de latencia no artefato atual do baseline. |

Notas:
- Os valores do GKS correspondem a medias por amostra registradas em `preds.csv`.
- O baseline XGBoost robusto nao possui campo de latencia no artefato atual.
