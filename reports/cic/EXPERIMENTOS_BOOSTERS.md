# 2D-AEF - Experimentos por Classe (CIC) - referencia legada

> Objetivo historico: comparar **LGBM**, **XGB** e **CatBoost** nos especialistas de um **snapshot binario legado** do CIC, reportando **F1 por classe**, **F1-macro** e observacoes de **latencia**.

## Aviso de escopo

Este arquivo **nao** descreve o cenario principal atual do paper.

Escopo real do documento:
- CIC em formulacao binaria legado;
- uso como nota experimental interna;
- nao usar como evidencia principal do manuscrito multiclasse atual.

## Como reproduzir (resumo)
1. Treinar especialistas por familia de modelo (flag `--models`).
2. Rodar inferencia e avaliacao para cada variacao.
3. Consolidar metricas em CSV e preencher a tabela abaixo.
4. Gerar graficos, se necessario.

## Tabela de resultados

| Familia | F1 (Benign) | F1 (Others) | F1-macro | Latencia esp. (ms/amostra) | Observacoes |
| --- | --- | --- | --- | --- | --- |
| LGBM |  |  |  |  |  |
| XGB |  |  |  |  |  |
| CatBoost |  |  |  |  |  |

## Notas
- manter este arquivo como registro historico interno;
- nao inferir a partir dele conclusoes sobre o GKS multiclasse atual;
- para o snapshot atual do paper, usar `reports/cic/RELATORIO_CIC.md`, `reports/table_main_results.md` e `reports/table_baseline_comparison.md`.
