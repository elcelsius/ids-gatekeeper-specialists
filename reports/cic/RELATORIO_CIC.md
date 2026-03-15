# Relatorio de Avaliacao - CIC-IDS2018 (2D-AEF)

## Natureza do documento

Este relatorio descreve o **snapshot atual** do cenario principal do paper: **CIC-IDS2018 em formulacao multiclasse agregada** com as classes `Benign`, `Bot`, `BruteForce`, `DDoS`, `DoS`, `Others` e `Web`, executado com a arquitetura **2D-AEF / GKS**.

Ele substitui a redacao antiga baseada no CIC binario (`Benign` vs `Others`). Os valores abaixo foram verificados diretamente em:

- `reports/cic/metrics_again.json`
- `outputs/eval_cic/preds.csv`
- `outputs/eval_cic/confusion_matrix_eval.csv`
- `outputs/eval_cic/classification_report_eval.csv`
- `reports/confusion_matrix_main.(csv|md)`
- `reports/table_baseline_comparison.(csv|md)`

Para a classificacao editorial entre artefatos oficiais e materiais legados em `reports/`, usar `reports/README.md`.

## 1) Metricas globais do snapshot atual

- **F1-macro:** **0.764278**
- **Acuracia:** **0.933080**
- **Amostras (n):** **100000**
- **Latencia media total por amostra:** **21.788869 ms**
- **Latencia media do gatekeeper:** **0.000056 ms**
- **Latencia media do especialista:** **21.788813 ms**

Esses valores correspondem ao snapshot local consolidado em 2026-03-15 e estao alinhados ao manuscrito atual.

## 2) Artefatos oficiais associados

### 2.1 Figuras
- `reports/cic/confusion_matrix_cic.png`
- `reports/cic/f1_per_class_cic.png`

### 2.2 Matrizes e tabelas textuais
- `reports/confusion_matrix_main.csv`
- `reports/confusion_matrix_main.md`
- `reports/table_main_results.csv`
- `reports/table_main_results.md`
- `reports/table_baseline_comparison.csv`
- `reports/table_baseline_comparison.md`
- `reports/latency_summary.csv`
- `reports/latency_summary.md`
- `reports/run_manifest.md`

## 3) Matriz de confusao tabular

No snapshot atual, a matriz multiclasse agregada do CIC e:

| true_label | pred_Benign | pred_Bot | pred_BruteForce | pred_DDoS | pred_DoS | pred_Others | pred_Web | row_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Benign | 46978 | 0 | 0 | 0 | 0 | 0 | 5 | 46983 |
| Bot | 1033 | 2874 | 0 | 0 | 0 | 0 | 0 | 3907 |
| BruteForce | 1 | 0 | 4953 | 0 | 5044 | 0 | 0 | 9998 |
| DDoS | 3 | 0 | 0 | 19996 | 0 | 0 | 0 | 19999 |
| DoS | 269 | 0 | 323 | 0 | 18506 | 0 | 14 | 19112 |
| Others | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| Web | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| col_total | 48284 | 2874 | 5276 | 19996 | 23550 | 1 | 19 | 100000 |

Leitura objetiva:
- `Benign`, `DDoS` e `DoS` concentram a maior parte dos acertos absolutos;
- `BruteForce` sofre confusao forte com `DoS` (**5044** casos);
- `Bot` perde recall principalmente para `Benign` (**1033** casos);
- `Web` nao aparece no holdout atual;
- `Others` aparece uma unica vez no holdout e foi corretamente reconhecida.

## 4) Comparacao com baseline e leitura auxiliar

O baseline oficial atual do paper e o **XGBoost global no recorte CIC robusto**, documentado em:

- `outputs/cic_robust_xgb_baseline/metrics_cic_robust_xgb_baseline.csv`
- `outputs/cic_robust_xgb_baseline/confusion_matrix_cic_robust_xgb_baseline.csv`
- `reports/confusion_matrix_baseline.(csv|md)`
- `reports/table_baseline_comparison.(csv|md)`

Valores do baseline oficial:
- **F1-macro:** **0.976239**
- **Acuracia:** **0.976280**
- **n:** **100000**

A comparacao continua metodologicamente assimetrica, porque o GKS oficial resolve um problema multiclasse em 7 categorias, enquanto o baseline resolve uma tarefa binaria robusta. Por isso, o arquivo `reports/table_baseline_comparison.md` tambem inclui uma linha auxiliar com o **colapso binario derivado** do GKS no CIC (`Benign` vs `Attack`), explicitamente marcada como nao oficial.

## 5) XAI no diretorio `reports/cic/`

O diretorio `reports/cic/` ainda contem artefatos de XAI, mas eles correspondem a um **snapshot binario legado** do CIC (`Benign` vs `Others`) e nao ao cenario multiclasse principal do paper.

Arquivos relevantes:
- `reports/cic/XAI_BRIEF.md`
- `reports/cic/xai/xai_shap_consolidado.csv`
- `reports/cic/xai/xai_shap_consolidado.md`

Esses arquivos devem ser interpretados apenas como material complementar historico de viabilidade. Eles nao sustentam, sozinhos, inferencias sobre o comportamento do GKS no cenario multiclasse atual.

## 6) Reprodutibilidade e limites

A trilha de proveniencia do snapshot atual e compatível com:

- `scripts/prep_cic_train.py`
- `scripts/make_cic_eval.py`
- `src/twodaef/cli_train_gatekeeper.py`
- `src/twodaef/cli_train_specialists.py`
- `src/twodaef/cli_infer_twostage.py`
- `src/twodaef/cli_eval_twostage.py`
- `src/twodaef/cli_plot_eval.py`
- `scripts/baseline_xgb_cic_robust.py`

Limites de rastreabilidade:
- a data original da execucao nao e recuperavel com seguranca a partir dos artefatos atuais;
- seed, hardware e duracao da execucao nao aparecem nos artefatos consolidados;
- este relatorio descreve o **snapshot atual**, nao uma release historica especifica.
