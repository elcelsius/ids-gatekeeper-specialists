# Relatorio de Avaliacao - UNSW-NB15 (2D-AEF)

## Natureza do documento

Este relatorio descreve o **snapshot atual** do cenario complementar do paper: **UNSW-NB15 em formulacao binaria** (`Normal` vs `Attack`) executado com a arquitetura **2D-AEF / GKS** (gatekeeper + especialistas).

Ele substitui a versao textual anterior que reportava metricas e latencias de um snapshot legado. Os valores abaixo foram verificados diretamente em:

- `reports/unsw_bin/metrics_again.json`
- `outputs/eval_unsw/preds.csv`
- `outputs/eval_unsw/confusion_matrix_eval.csv`
- `outputs/eval_unsw/classification_report_eval.csv`
- `reports/confusion_matrix_unsw_bin.(csv|md)`

Para a classificacao editorial entre artefatos oficiais e materiais legados em `reports/`, usar `reports/README.md`.

## 1) Metricas globais do snapshot atual

- **F1-macro:** **0.865582**
- **Acuracia:** **0.874268**
- **Amostras (n):** **175341**
- **Latencia media total por amostra:** **1.401404 ms**
- **Latencia media do gatekeeper:** **0.000058 ms**
- **Latencia media do especialista:** **1.401346 ms**

Esses valores correspondem ao snapshot local consolidado em 2026-03-15 e estao alinhados ao manuscrito atual.

## 2) Artefatos oficiais associados

### 2.1 Figuras
- `reports/unsw_bin/confusion_matrix_unsw_bin.png`
- `reports/unsw_bin/f1_per_class_unsw_bin.png`

### 2.2 Matrizes e tabelas textuais
- `reports/confusion_matrix_unsw_bin.csv`
- `reports/confusion_matrix_unsw_bin.md`
- `reports/table_main_results.csv`
- `reports/table_main_results.md`
- `reports/latency_summary.csv`
- `reports/latency_summary.md`
- `reports/run_manifest.md`

## 3) Matriz de confusao tabular

No snapshot atual, a matriz binaria do UNSW e:

| true_label | pred_Normal | pred_Attack | row_total |
| --- | ---: | ---: | ---: |
| Normal | 54362 | 1638 | 56000 |
| Attack | 20408 | 98933 | 119341 |
| col_total | 74770 | 100571 | 175341 |

Leitura objetiva:
- o modelo classifica corretamente **54362** amostras `Normal`;
- o modelo classifica corretamente **98933** amostras `Attack`;
- ha **1638** falsos positivos (`Normal -> Attack`);
- ha **20408** falsos negativos (`Attack -> Normal`).

## 4) Interpretacao conservadora

O cenario UNSW atual apresenta desempenho agregado razoavel para a tarefa binaria complementar, mas nao sustenta mais a narrativa do snapshot antigo de F1-macro proximo de 0.893 e latencia sub-0.9 ms. O valor atual correto e **F1-macro 0.865582** com **1.401404 ms** por amostra.

Em termos operacionais, o gatekeeper continua tendo custo desprezivel e o especialista concentra praticamente toda a latencia. Em termos de erro, o principal problema esta na quantidade de ataques classificados como `Normal`, o que impõe cautela ao usar este cenario como evidencia de robustez sem qualificar a taxa de falsos negativos.

## 5) Reprodutibilidade e limites

A trilha de proveniencia do snapshot atual e compatível com:

- `scripts/prep_unsw_binary.py`
- `src/twodaef/cli_train_gatekeeper.py`
- `src/twodaef/cli_train_specialists.py`
- `src/twodaef/cli_infer_twostage.py`
- `src/twodaef/cli_eval_twostage.py`
- `src/twodaef/cli_plot_eval.py`

Limites de rastreabilidade:
- a data original da execucao nao e recuperavel com seguranca a partir dos artefatos atuais;
- seed, hardware e duracao da execucao nao aparecem nos artefatos consolidados;
- este relatorio descreve o **snapshot atual**, nao uma release historica especifica.

## 6) XAI neste cenario

Nao ha, no snapshot atual inspecionado para o paper, um pacote de XAI do UNSW consolidado em `reports/` com o mesmo papel de evidência textual usado no manuscrito principal. Se novos artefatos forem gerados, eles devem ser tratados como complemento e nao como evidencia retroativa desta campanha.
