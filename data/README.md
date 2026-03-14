# data/

Esta pasta contém os datasets usados nos experimentos do paper.
Os arquivos de dados **não são versionados** no Git (ver `.gitignore`).

---

## Estrutura esperada

```
data/
├── raw/
│   ├── cicids2018/          # CSVs brutos do CIC-IDS2018 (download via Kaggle)
│   └── unsw/                # CSVs brutos do UNSW-NB15   (download via Kaggle)
│
├── train_cic.csv            # Treino CIC binário        (~300 000 linhas)
├── cic_eval.csv             # Holdout CIC binário       (~100 000 linhas)
├── cic_infer.csv            # Amostra CIC sem rótulo    (~1 000 linhas)
├── train_cic_robust.csv     # Treino CIC sem dst_port   (recorte robusto)
├── cic_eval_robust.csv      # Holdout CIC sem dst_port  (recorte robusto)
│
├── train_unsw.csv           # Treino UNSW binário       (~175 000 linhas)
├── unsw_eval.csv            # Holdout UNSW binário      (~82 000 linhas)
└── unsw_infer.csv           # Amostra UNSW sem rótulo   (~1 000 linhas)
```

---

## Como gerar os arquivos

### 1. Baixar os dados brutos

```powershell
# CIC-IDS2018
python scripts\download_cicids2018.py

# UNSW-NB15
python scripts\download_unsw.py
```

Ambos requerem credencial Kaggle em `%USERPROFILE%\.kaggle\kaggle.json`.

### 2. Gerar os splits de treino e avaliação

```powershell
# CIC — cenário principal
python scripts\prep_cic_train.py    # → train_cic.csv, cic_infer.csv
python scripts\make_cic_eval.py     # → cic_eval.csv  (holdout, sem leakage)
python scripts\prep_cic_robust.py   # → variantes sem dst_port

# UNSW — cenário secundário
python scripts\prep_unsw_binary.py  # → train_unsw.csv, unsw_eval.csv, unsw_infer.csv
```

---

## Política anti-leakage

> **Regra fundamental:** `cic_eval.csv` e `unsw_eval.csv` nunca são
> derivados dos arquivos de treino. Ambos são gerados diretamente
> a partir dos dados brutos com seeds separadas.

| Arquivo | Origem | Seed |
|---|---|---|
| `train_cic.csv` | brutos CIC | `TRAIN_SEED=42` |
| `cic_eval.csv` | brutos CIC (split independente) | `EVAL_SEED=123` |
| `train_unsw.csv` | `UNSW_NB15_training-set.csv` (oficial) | — |
| `unsw_eval.csv` | `UNSW_NB15_testing-set.csv` (oficial) | — |

Para o UNSW, quando os arquivos oficiais de train/test estão disponíveis
(modo preferencial), o split é o definido pelos criadores do dataset.
No fallback (arquivos brutos `_1` a `_4`), o split é 80/20 estratificado
com `EVAL_SEED=123`.

---

## Rótulos por dataset

| Dataset | Coluna | Valores |
|---|---|---|
| CIC-IDS2018 | `label` | `Benign` / `Others` (agregado de todas as classes de ataque) |
| UNSW-NB15 | `label` | `Normal` / `Attack` |

---

## Política de versionamento

- Dados brutos e arquivos CSV nunca devem ser commitados.
- Apenas scripts, configurações e relatórios são versionados.
- Para reproduzir os dados: execute os scripts de download e preparação acima.
