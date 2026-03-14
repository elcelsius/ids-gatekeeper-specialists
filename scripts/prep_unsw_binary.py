# scripts/prep_unsw_binary.py
# ---------------------------------------------------------------------------
# Prepara o dataset UNSW-NB15 para o cenário BINÁRIO do paper:
#   label = 0 (Normal) / 1 (Attack)
#
# Gera três artefatos:
#   data/train_unsw.csv   — treino  (80 % estratificado, sem leakage)
#   data/unsw_eval.csv    — holdout (20 % estratificado, sem leakage)
#   data/unsw_infer.csv   — amostra pequena para inferência rápida (sem label)
#
# Fonte preferencial (quando disponível via download_unsw.py):
#   UNSW_NB15_training-set.csv  →  usado como base de treino
#   UNSW_NB15_testing-set.csv   →  usado diretamente como holdout oficial
#
# Fallback (quando só existem os arquivos brutos _1.csv a _4.csv):
#   Concatena e faz split 80/20 estratificado internamente.
#
# Convenções mantidas iguais ao CIC (prep_cic_train.py):
#   - Normalização de nomes de colunas via snake_case
#   - Mantém apenas colunas numéricas + label
#   - Remove NaN / Inf
#   - Seeds fixos e documentados
# ---------------------------------------------------------------------------
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# ── Caminhos ────────────────────────────────────────────────────────────────
RAW_DIR    = Path(r"data\raw\unsw")

# Arquivos com split oficial (preferencial)
OFFICIAL_TRAIN = RAW_DIR / "UNSW_NB15_training-set.csv"
OFFICIAL_TEST  = RAW_DIR / "UNSW_NB15_testing-set.csv"

# Arquivos brutos (fallback)
RAW_FILES_GLOB = "UNSW-NB15_*.csv"

# Saídas
OUT_TRAIN = Path(r"data\train_unsw.csv")
OUT_EVAL  = Path(r"data\unsw_eval.csv")
OUT_INFER = Path(r"data\unsw_infer.csv")

# ── Parâmetros ───────────────────────────────────────────────────────────────
CHUNKSIZE   = 200_000
MAX_ROWS    = 400_000   # total máximo lido dos brutos (fallback)
TRAIN_SEED  = 42        # mesmo seed do CIC para consistência
EVAL_SEED   = 123       # mesmo seed do make_cic_eval.py
EVAL_FRAC   = 0.20      # 20 % para holdout (só usado no fallback)
INFER_ROWS  = 1_000     # linhas na amostra de inferência rápida


# ── Helpers ──────────────────────────────────────────────────────────────────
def snake(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[^0-9A-Za-z]+", "_", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_").lower()


def map_label_unsw(raw) -> str:
    """
    Converte o rótulo binário do UNSW-NB15 para string padronizada.

    Nos arquivos oficiais (training/testing-set):
        coluna 'label' contém 0 (Normal) ou 1 (Attack)

    Nos arquivos brutos (_1 a _4):
        coluna 'Label' contém 0 ou 1 também
        coluna 'attack_cat' contém nome da categoria (pode ser usada no futuro)
    """
    try:
        v = int(float(str(raw).strip()))
        return "Attack" if v == 1 else "Normal"
    except (ValueError, TypeError):
        s = str(raw).strip().lower()
        if s in {"normal", "0", "benign"}:
            return "Normal"
        return "Attack"


def sanitize(df: pd.DataFrame, label_col: str) -> Optional[pd.DataFrame]:
    """Normaliza colunas, aplica rótulo, mantém só numéricas + label."""
    df.columns = [snake(c) for c in df.columns]

    # Renomeia a coluna de rótulo detectada para "label"
    if label_col in df.columns and label_col != "label":
        df = df.rename(columns={label_col: "label"})

    if "label" not in df.columns:
        return None

    df["label"] = df["label"].apply(map_label_unsw)

    # Mantém só numéricas + label
    num = df.select_dtypes(include=[np.number])
    if num.empty:
        return None
    result = num.copy()
    result["label"] = df["label"].values
    return result


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Remove NaN/Inf e garante label como string."""
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(axis=1, how="any")
    df["label"] = df["label"].astype(str)
    return df


def detect_label_col(columns: List[str]) -> Optional[str]:
    """Detecta o nome da coluna de rótulo."""
    for cand in ("label", "labels", "attack_cat", "attack_category", "class"):
        if cand in columns:
            return cand
    return None


# ── Modo 1: arquivos oficiais train/test disponíveis ─────────────────────────
def load_official() -> tuple[pd.DataFrame, pd.DataFrame]:
    print("[INFO] Usando arquivos oficiais de train/test do UNSW-NB15.")

    df_train_raw = pd.read_csv(OFFICIAL_TRAIN, low_memory=False)
    df_test_raw  = pd.read_csv(OFFICIAL_TEST,  low_memory=False)

    cols_train = [snake(c) for c in df_train_raw.columns]
    df_train_raw.columns = cols_train
    cols_test = [snake(c) for c in df_test_raw.columns]
    df_test_raw.columns = cols_test

    label_col_tr = detect_label_col(cols_train)
    label_col_te = detect_label_col(cols_test)

    if label_col_tr is None or label_col_te is None:
        raise RuntimeError("Coluna de rótulo não encontrada nos arquivos oficiais.")

    df_train = sanitize(df_train_raw, label_col_tr)
    df_test  = sanitize(df_test_raw,  label_col_te)

    if df_train is None or df_test is None:
        raise RuntimeError("Falha na sanitização dos arquivos oficiais.")

    return df_train, df_test


# ── Modo 2: fallback — arquivos brutos _1 a _4 ───────────────────────────────
def load_raw_fallback() -> tuple[pd.DataFrame, pd.DataFrame]:
    print("[INFO] Arquivos oficiais não encontrados. Usando arquivos brutos (fallback).")

    raw_files = sorted(RAW_DIR.glob(RAW_FILES_GLOB))
    if not raw_files:
        raise FileNotFoundError(
            f"Nenhum arquivo CSV encontrado em {RAW_DIR}\n"
            "Execute primeiro: python scripts/download_unsw.py"
        )

    total_rows = 0
    collected: List[pd.DataFrame] = []

    for csv_path in raw_files:
        try:
            for chunk in pd.read_csv(
                csv_path,
                low_memory=False,
                chunksize=CHUNKSIZE,
                on_bad_lines="skip",
            ):
                cols = [snake(c) for c in chunk.columns]
                chunk.columns = cols
                label_col = detect_label_col(cols)
                if label_col is None:
                    continue

                df_chunk = sanitize(chunk, label_col)
                if df_chunk is None:
                    continue

                collected.append(df_chunk)
                total_rows += len(df_chunk)
                if total_rows >= MAX_ROWS:
                    break

        except Exception as e:
            print(f"[WARN] Falha lendo {csv_path.name}: {e}")

        if total_rows >= MAX_ROWS:
            break

    if not collected:
        raise RuntimeError("Nenhum chunk válido extraído dos arquivos brutos.")

    df_all = pd.concat(collected, axis=0, ignore_index=True)

    # Split estratificado 80/20
    try:
        df_train, df_eval = train_test_split(
            df_all,
            test_size=EVAL_FRAC,
            random_state=EVAL_SEED,
            stratify=df_all["label"],
        )
    except ValueError:
        df_train, df_eval = train_test_split(
            df_all,
            test_size=EVAL_FRAC,
            random_state=EVAL_SEED,
        )

    return df_train, df_eval


# ── Função principal ─────────────────────────────────────────────────────────
def build_unsw_binary() -> None:
    for p in (OUT_TRAIN, OUT_EVAL, OUT_INFER):
        p.parent.mkdir(parents=True, exist_ok=True)

    # Escolhe modo de carregamento
    if OFFICIAL_TRAIN.exists() and OFFICIAL_TEST.exists():
        df_train, df_eval = load_official()
    else:
        df_train, df_eval = load_raw_fallback()

    # Sanitização final
    df_train = clean(df_train)
    df_eval  = clean(df_eval)

    # Garante que os dois conjuntos têm as mesmas colunas
    shared_cols = list(set(df_train.columns) & set(df_eval.columns))
    shared_cols = [c for c in df_train.columns if c in shared_cols]  # preserva ordem
    df_train = df_train[shared_cols]
    df_eval  = df_eval[shared_cols]

    # Salva treino
    df_train.to_csv(OUT_TRAIN, index=False)
    print(f"\n[OK] Treino salvo em:   {OUT_TRAIN}  (n={len(df_train):,})")
    print(f"     Distribuição:\n{df_train['label'].value_counts().to_string()}")

    # Salva holdout de avaliação
    df_eval.to_csv(OUT_EVAL, index=False)
    print(f"\n[OK] Holdout salvo em:  {OUT_EVAL}  (n={len(df_eval):,})")
    print(f"     Distribuição:\n{df_eval['label'].value_counts().to_string()}")

    # Salva amostra para inferência rápida (sem label)
    n_infer = min(INFER_ROWS, len(df_train))
    infer = (
        df_train
        .drop(columns=["label"])
        .sample(n=n_infer, random_state=TRAIN_SEED)
    )
    infer.to_csv(OUT_INFER, index=False)
    print(f"\n[OK] Infer salvo em:    {OUT_INFER}  (n={len(infer):,})")

    print()
    print("NOTA: train_unsw.csv e unsw_eval.csv NÃO têm sobreposição.")
    print("Próximo passo: treinar o gatekeeper com train_unsw.csv")


if __name__ == "__main__":
    build_unsw_binary()
