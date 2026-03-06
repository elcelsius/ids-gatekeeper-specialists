# 2D-AEF — Experimentos por Classe (CIC) — v0.2.0

> Objetivo: comparar **LGBM**, **XGB** e **CatBoost** nos especialistas do CIC (binário), reportando **F1 por classe** e **F1-macro**, além de observações de **latência**.

## Como reproduzir (resumo)
1. Treinar especialistas por família de modelo (flag `--models`):
   - `train-specialists --models lgbm ...`
   - `train-specialists --models xgb ...`
   - `train-specialists --models cat ...`
2. Rodar `infer-twostage` e `eval-twostage` para cada variação.
3. Consolidar métricas em CSV e preencher a tabela abaixo.
4. (Opcional) Gerar gráfico de barras de F1-macro.

---

## Tabela de resultados

| Família     | F1 (Benign) | F1 (Others) | F1-macro | Latência esp. (ms/amostra) | Observações |
|-------------|--------------|-------------|----------|-----------------------------|-------------|
| **LGBM**    |              |             |          |                             |             |
| **XGB**     |              |             |          |                             |             |
| **CatBoost**|              |             |          |                             |             |

> Preencha “Latência esp. (ms/amostra)” medindo a média de N=3 rodadas por especialista com batch pequeno (ex.: 256).

---

## Setup (anotar versões/hardware)
- Python:
- lightgbm:
- xgboost:
- catboost:
- CPU / GPU:
- SO:

---

## Notas
- Fixar `random_state` para reprodutibilidade.
- Salvar qual família foi usada por classe no `specialist_map_cic.json`.
- Manter este arquivo versionado (não subir `.joblib`).
