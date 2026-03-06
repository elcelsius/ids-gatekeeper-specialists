# XAI Brief — CIC (binário)

Este resumo foi gerado automaticamente a partir de `reports/cic/xai/xai_shap_consolidado.csv`.
Ele lista as *TOP 12* features globais (|SHAP| médio) por classe.

## Visão rápida
- Classes: Benign, Others
- Arquivo de origem: `reports/cic/xai/xai_shap_consolidado.csv`

---

### Classe: Benign

| Rank | Feature | |SHAP| médio |
|-----:|---------|-------------:|
| 1 | `dst_port` | 0.023914 |
| 2 | `fwd_seg_size_min` | 0.010779 |
| 3 | `bwd_pkts_s` | 0.002620 |
| 4 | `flow_iat_min` | 0.002110 |
| 5 | `flow_iat_mean` | 0.001859 |
| 6 | `init_fwd_win_byts` | 0.001014 |
| 7 | `init_bwd_win_byts` | 0.000702 |
| 8 | `fwd_pkts_s` | 0.000619 |
| 9 | `fwd_header_len` | 0.000395 |
| 10 | `flow_iat_max` | 0.000261 |


### Classe: Others

| Rank | Feature | |SHAP| médio |
|-----:|---------|-------------:|
| 1 | `fwd_seg_size_min` | 0.021710 |
| 2 | `init_fwd_win_byts` | 0.015960 |
| 3 | `flow_iat_max` | 0.006269 |
| 4 | `ack_flag_cnt` | 0.001307 |
| 5 | `fwd_pkt_len_max` | 0.001016 |
| 6 | `pkt_size_avg` | 0.000826 |
| 7 | `fwd_seg_size_avg` | 0.000638 |
| 8 | `fwd_iat_std` | 0.000563 |
| 9 | `fwd_pkt_len_mean` | 0.000554 |
| 10 | `urg_flag_cnt` | 0.000317 |


