# 06 Results

Esta seção apresenta exclusivamente os resultados disponíveis nos artefatos versionados do projeto, com base principal em `reports/` e suporte em relatórios de `docs/` quando necessário para completar informações de execução. Não são introduzidos valores externos aos arquivos do repositório.

## 6.1 Base de evidências utilizada

Foram considerados, como fontes primárias de resultado:

- `reports/cic/metrics_again.json`
- `reports/unsw_bin/metrics_again.json`
- `reports/unsw_bin/metrics_again_unsw_legacy.json`
- `reports/metrics_comparados.csv` e `reports/metrics_comparados.md`
- `reports/cic/confusion_matrix_cic.png` e `reports/cic/f1_per_class_cic.png`
- `reports/unsw_bin/confusion_matrix_unsw.png` e `reports/unsw_bin/f1_per_class_unsw.png`
- `reports/cic/xai/xai_shap_consolidado.csv` e `reports/cic/XAI_BRIEF.md`

Como apoio documental, foram utilizados:

- `reports/cic/RELATORIO_CIC.md` (versão `v0.2.0-cic`, data 2025-11-19)
- `reports/unsw_bin/RELATORIO_UNSW.md` (versão `v0.1.0-unsw-mvp`, data 2025-10-31)
- `docs/cic_eval_report.md` e `docs/unsw_eval_report.md`

## 6.2 Métricas agregadas por cenário

A Tabela 1 consolida os valores agregados explicitamente presentes nos arquivos JSON de métricas.

**Tabela 1 — Métricas agregadas disponíveis nos artefatos versionados**

| Cenário | Arquivo-fonte | F1-macro | Acurácia | n |
|---|---|---:|---:|---:|
| CIC-IDS2018 (binário) | `reports/cic/metrics_again.json` | 1.000000 | 1.000000 | 100000 |
| UNSW-NB15 (binário, execução `unsw_bin`) | `reports/unsw_bin/metrics_again.json` | 0.890069 | 0.898432 | 175341 |
| UNSW-NB15 (binário, execução `unsw` legado) | `reports/unsw_bin/metrics_again_unsw_legacy.json` | 0.892938 | 0.900987 | 175341 |

Observa-se a coexistência de dois artefatos de métricas para o UNSW-NB15 (`unsw_bin` e `unsw` legado), com pequena variação nos valores agregados e caminhos de saída distintos (`outputs/unsw_bin/preds.csv` e `outputs/eval_unsw/preds.csv`).

## 6.3 Métricas por classe e matrizes de confusão

Para o experimento CIC, estão disponíveis as figuras `reports/cic/f1_per_class_cic.png` e `reports/cic/confusion_matrix_cic.png`. Para o experimento UNSW binário, estão disponíveis `reports/unsw_bin/f1_per_class_unsw.png` e `reports/unsw_bin/confusion_matrix_unsw.png`.

Esses arquivos registram visualmente a distribuição de desempenho por classe e os padrões de erro de classificação em cada cenário. No conjunto versionado atual, entretanto, os valores numéricos detalhados por classe (em formato tabular) e as contagens absolutas da matriz de confusão (TP, FP, TN, FN em arquivo estruturado) não estão disponibilizados diretamente em `reports/`.

## 6.4 Custo de inferência reportado

No relatório UNSW versionado em `reports/unsw_bin/RELATORIO_UNSW.md`, consta latência média de inferência total de aproximadamente **0.8776 ms** por amostra, com decomposição em estágio de gatekeeper (~**0.000038 ms**) e estágio especialista (~**0.877536 ms**).

Para o CIC, a síntese numérica de latência explícita está registrada em `docs/cic_eval_report.md` (execução `v0.1.0-cic-mvp`), com valor total aproximado de **0.0001 ms** por amostra (gatekeeper ~**0.00008 ms**, especialista ~**0.00000 ms**). No relatório `reports/cic/RELATORIO_CIC.md` (versão `v0.2.0-cic`), a ênfase está na descrição do pipeline e dos artefatos, sem tabela agregada específica de latência.

## 6.5 Consolidação inter-datasets

Os arquivos `reports/metrics_comparados.csv` e `reports/metrics_comparados.md` apresentam uma consolidação entre CIC-IDS2018 e UNSW-NB15 com os seguintes valores:

- UNSW-NB15: `f1_macro = 0.8929`, `accuracy = 0.9010`;
- CIC-IDS2018: `f1_macro = 1.0000`, `accuracy = 1.0000`.

Essa consolidação utiliza a execução UNSW identificada como `unsw` (legado), coerente com `metrics_again_unsw_legacy.json`.

## 6.6 Artefatos de interpretabilidade (XAI) disponíveis

No cenário CIC binário, o projeto contém consolidação SHAP em `reports/cic/xai/xai_shap_consolidado.csv` e resumo em `reports/cic/XAI_BRIEF.md`. Entre as variáveis com maior contribuição média absoluta (|SHAP| médio), destacam-se:

- Classe `Benign`: `dst_port` (0.0239138633), `fwd_seg_size_min` (0.0107793954), `bwd_pkts_s` (0.0026201308);
- Classe `Others`: `fwd_seg_size_min` (0.0217095731), `init_fwd_win_byts` (0.0159603954), `flow_iat_max` (0.0062686020).

Esses valores são reportados como evidência descritiva de importância de atributos e não como métrica de desempenho classificatório.

## 6.7 Completude e limitações dos resultados versionados

Com base no estado atual do repositório, os resultados agregados (F1-macro, acurácia e tamanho amostral), as figuras de matriz de confusão/F1 por classe e os artefatos de XAI estão disponíveis e passíveis de rastreamento.

Por outro lado, alguns itens previstos em documentos de planejamento aparecem incompletos ou ausentes no material versionado: (i) não há, em `reports/`, arquivos tabulares de matriz de confusão absoluta por dataset (`TP`, `FP`, `TN`, `FN`) no formato JSON explicitado no plano experimental; (ii) os arquivos `preds.csv` referenciados nas métricas apontam para `outputs/`, pasta não versionada; e (iii) o relatório `reports/cic/EXPERIMENTOS_BOOSTERS.md` mantém a tabela comparativa entre famílias de modelos sem preenchimento de resultados.
