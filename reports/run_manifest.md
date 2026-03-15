# Run Manifest

## Natureza do documento

Este manifesto foi consolidado em 2026-03-15 a partir do snapshot local do repositorio.
Ele descreve apenas o que e comprovavel pelos artefatos hoje presentes em `reports/`, `outputs/`, `scripts/` e `src/`.
Datas originais de execucao, seeds, hardware e duracao nao sao inventados quando nao estao rastreaveis nos artefatos.
Para distinguir o pacote oficial do snapshot atual dos materiais legados, usar `reports/README.md`.

## Blocos experimentais identificados

| Bloco | Dataset | Formulacao | Status no snapshot | Artefatos-chave |
| --- | --- | --- | --- | --- |
| GKS principal | CIC-IDS2018 | Multiclasse (7 classes) | materializado | `outputs/eval_cic/*`, `reports/cic/*` |
| GKS complementar | UNSW-NB15 | Binaria | materializado | `outputs/eval_unsw/*`, `reports/unsw_bin/*` |
| Baseline oficial | CIC-IDS2018 robust | Binaria robusta | materializado | `outputs/cic_robust_xgb_baseline/*` |

## Execucao 1 - GKS no CIC-IDS2018

- Scripts de proveniencia observados: `scripts/prep_cic_train.py`, `scripts/make_cic_eval.py`, `src/twodaef/cli_train_gatekeeper.py`, `src/twodaef/cli_train_specialists.py`, `src/twodaef/cli_infer_twostage.py`, `src/twodaef/cli_eval_twostage.py`, `src/twodaef/cli_plot_eval.py`.
- Entradas rastreaveis: `data/train_cic.csv`, `data/cic_eval.csv`, `configs/cols/gatekeeper_cic_cols.txt`, `configs/mappings/specialist_map_cic.json`.
- Saidas rastreaveis: `outputs/eval_cic/preds.csv`, `outputs/eval_cic/metrics_eval.json`, `outputs/eval_cic/classification_report_eval.csv`, `outputs/eval_cic/confusion_matrix_eval.csv`, `reports/cic/metrics_again.json`, `reports/cic/confusion_matrix_cic.png`, `reports/cic/f1_per_class_cic.png`, `reports/confusion_matrix_main.csv`, `reports/confusion_matrix_main.md`.
- Metricas consolidadas: precision_macro=0.813935, recall_macro=0.742720, f1_macro=0.764278, accuracy=0.933080, n=100000.
- Latencia media: stage1=0.000056 ms, stage2=21.788813 ms, total=21.788869 ms.
- Lacunas de rastreabilidade: seed, data original da execucao, hardware e duracao nao aparecem no snapshot atual.

## Execucao 2 - GKS no UNSW-NB15

- Scripts de proveniencia observados: `scripts/prep_unsw_binary.py`, `src/twodaef/cli_train_gatekeeper.py`, `src/twodaef/cli_train_specialists.py`, `src/twodaef/cli_infer_twostage.py`, `src/twodaef/cli_eval_twostage.py`, `src/twodaef/cli_plot_eval.py`.
- Entradas rastreaveis: `data/train_unsw.csv`, `data/unsw_eval.csv`, `data/unsw_infer.csv`, `configs/mappings/specialist_map_unsw.json`.
- Saidas rastreaveis: `outputs/eval_unsw/preds.csv`, `outputs/eval_unsw/metrics_eval.json`, `outputs/eval_unsw/classification_report_eval.csv`, `outputs/eval_unsw/confusion_matrix_eval.csv`, `reports/unsw_bin/metrics_again.json`, `reports/unsw_bin/confusion_matrix_unsw_bin.png`, `reports/unsw_bin/f1_per_class_unsw_bin.png`, `reports/confusion_matrix_unsw_bin.csv`, `reports/confusion_matrix_unsw_bin.md`.
- Metricas consolidadas: precision_macro=0.855385, recall_macro=0.899872, f1_macro=0.865582, accuracy=0.874268, n=175341.
- Latencia media: stage1=0.000058 ms, stage2=1.401346 ms, total=1.401404 ms.
- Lacunas de rastreabilidade: seed, data original da execucao, hardware e duracao nao aparecem no snapshot atual.

## Execucao 3 - Baseline XGBoost no CIC robusto

- Script de proveniencia observado: `scripts/baseline_xgb_cic_robust.py`.
- Entradas rastreaveis: `data/train_cic_robust.csv`, `data/cic_eval_robust.csv`.
- Saidas rastreaveis: `outputs/cic_robust_xgb_baseline/metrics_cic_robust_xgb_baseline.csv`, `outputs/cic_robust_xgb_baseline/confusion_matrix_cic_robust_xgb_baseline.csv`, `reports/confusion_matrix_baseline.csv`, `reports/confusion_matrix_baseline.md`.
- Metricas consolidadas: precision_macro=0.975840, recall_macro=0.977333, f1_macro=0.976239, accuracy=0.976280, n=100000.
- Latencia: nao disponivel no artefato atual.
- Lacunas de rastreabilidade: seed, data original da execucao, hardware e duracao nao aparecem no snapshot atual.

## Artefatos de consolidacao gerados nesta revisao

- `reports/table_main_results.csv`
- `reports/table_main_results.md`
- `reports/table_baseline_comparison.csv`
- `reports/table_baseline_comparison.md`
- `reports/latency_summary.csv`
- `reports/latency_summary.md`
- `reports/confusion_matrix_main.csv`
- `reports/confusion_matrix_main.md`
- `reports/confusion_matrix_unsw_bin.csv`
- `reports/confusion_matrix_unsw_bin.md`
- `reports/confusion_matrix_baseline.csv`
- `reports/confusion_matrix_baseline.md`
- `reports/README.md`
- `reports/run_manifest.md`

## Limites do manifesto

- Este arquivo nao substitui um log de execucao em tempo real.
- Ele consolida apenas o que pode ser inferido com seguranca a partir do snapshot atual.
- Qualquer reexecucao futura deve registrar seed, data, hardware e comando efetivamente usado para fechar a rastreabilidade externa.
