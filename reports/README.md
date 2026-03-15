# Reports README

## Objetivo

Este diretorio concentra o **pacote textual e grafico do snapshot atual** usado pelo manuscrito, alem de alguns artefatos **legados** mantidos apenas para historico ou apoio complementar.

Regra pratica:
- se um arquivo estiver listado em **Artefatos oficiais do snapshot atual**, ele pode ser usado como evidencia do paper atual;
- se estiver em **Artefatos legados ou complementares**, ele nao deve ser tratado como evidencia principal do cenario multiclasse atual sem nova execucao ou nova consolidacao.

## Artefatos oficiais do snapshot atual

### Consolidacao transversal do paper
- `run_manifest.md`: manifesto do snapshot atual, com proveniencia minima dos blocos experimentais.
- `table_main_results.csv`
- `table_main_results.md`
- `table_baseline_comparison.csv`
- `table_baseline_comparison.md`
- `latency_summary.csv`
- `latency_summary.md`
- `confusion_matrix_main.csv`
- `confusion_matrix_main.md`
- `confusion_matrix_unsw_bin.csv`
- `confusion_matrix_unsw_bin.md`
- `confusion_matrix_baseline.csv`
- `confusion_matrix_baseline.md`
- `metrics_comparados.csv`
- `metrics_comparados.md`

### Cenario principal - CIC-IDS2018 multiclasse
- `cic/metrics_again.json`
- `cic/confusion_matrix_cic.png`
- `cic/f1_per_class_cic.png`
- `cic/RELATORIO_CIC.md`

### Cenario complementar - UNSW-NB15 binario
- `unsw_bin/metrics_again.json`
- `unsw_bin/confusion_matrix_unsw_bin.png`
- `unsw_bin/f1_per_class_unsw_bin.png`
- `unsw_bin/RELATORIO_UNSW.md`

## Artefatos legados ou complementares

### UNSW legado
- `unsw_bin/metrics_again_unsw_legacy.json`
  - snapshot antigo do UNSW;
  - nao usar como base do manuscrito atual;
  - mantido apenas para historico comparativo interno.

### XAI legado do CIC
- `cic/XAI_BRIEF.md`
- `cic/xai/xai_shap_consolidado.csv`
- `cic/xai/xai_shap_consolidado.md`
  - todos correspondem a um **snapshot binario legado** do CIC (`Benign` vs `Others`);
  - servem apenas como material complementar historico de interpretabilidade;
  - nao descrevem o cenario principal atual em 7 classes.

### Experimentos internos legados
- `cic/EXPERIMENTOS_BOOSTERS.md`
  - nota experimental historica para comparacao de familias de modelos em um snapshot binario legado do CIC;
  - nao usar como evidencia principal do paper atual.

## O que este diretorio nao resolve sozinho

Mesmo com a consolidacao atual em `reports/`, parte da rastreabilidade continua dependente de artefatos fora deste diretorio:
- `outputs/` permanece fora do versionamento;
- modelos treinados em `artifacts/` permanecem locais;
- seed, hardware, data original da execucao e duracao nao estao completamente rastreados no snapshot atual.

Por isso, `reports/` deve ser lido como **pacote de evidencia textual e grafica do snapshot atual**, e nao como substituto integral de uma reproducao do zero.

## Ordem recomendada de leitura

1. `run_manifest.md`
2. `table_main_results.md`
3. `table_baseline_comparison.md`
4. `latency_summary.md`
5. `confusion_matrix_main.md`
6. `confusion_matrix_unsw_bin.md`
7. `confusion_matrix_baseline.md`
8. `cic/RELATORIO_CIC.md`
9. `unsw_bin/RELATORIO_UNSW.md`

## Criterio editorial

Se um arquivo de `reports/` trouxer numeros diferentes dos usados no manuscrito, o criterio correto e:
1. conferir se ele pertence ao snapshot atual ou ao bloco legado;
2. priorizar os artefatos listados na secao **Artefatos oficiais do snapshot atual**;
3. em caso de conflito, usar `run_manifest.md`, `table_main_results.md` e os artefatos derivados diretamente de `outputs/` como referencia primaria.
