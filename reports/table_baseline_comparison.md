# Table Baseline Comparison

Comparacao independente entre o cenario principal do paper, o baseline oficial e uma leitura auxiliar derivada do colapso binario do GKS no CIC.

| Linha | Dataset | Formulacao | Precision_macro | Recall_macro | F1_macro | Acuracia | Lat_total_ms | Observacao |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GKS oficial | CIC-IDS2018 | Multiclasse (7 classes) | 0.814 | 0.743 | 0.764 | 0.933 | 21.789 | Comparacao oficial, mas assimetrica. |
| Baseline XGB oficial | CIC-IDS2018 robust | Binaria robusta | 0.976 | 0.977 | 0.976 | 0.976 | NA | Sem latencia registrada no snapshot. |
| GKS colapsado (auxiliar) | CIC-IDS2018 | Binaria derivada | 0.986 | 0.988 | 0.987 | 0.987 | 21.789 | Auxiliar; nao substitui o baseline robusto. |

Notas metodologicas:
- `GKS oficial` e `Baseline XGB oficial` formam a comparacao principal do paper, mas em formulacoes diferentes.
- `GKS colapsado (auxiliar)` foi calculado diretamente de `outputs/eval_cic/preds.csv` e serve apenas para qualificar onde a perda do GKS ocorre.
- O baseline oficial foi treinado no recorte robusto sem `dst_port`, enquanto o GKS oficial corresponde ao pipeline completo do CIC multiclasse.
