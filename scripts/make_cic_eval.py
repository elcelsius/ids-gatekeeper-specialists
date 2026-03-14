# scripts/make_cic_eval.py
# ---------------------------------------------------------------------------
# Gera cic_eval.csv (holdout) a partir dos CSVs brutos do CIC-IDS2018.
#
# Anti-leakage: usa as linhas APÓS o offset ROWS_PER_FILE de cada arquivo,
# ou seja, as mesmas linhas que prep_cic_train.py NÃO coletou.
#
# Achados do EDA:
#   - 80 colunas por arquivo, todas numéricas (exceto 02-20 com 79)
#   - 03-01-2018.csv tem cabeçalho duplicado no meio -> 0 numéricas -> pulado
#   - Apenas flow_byts_s e flow_pkts_s têm Inf/NaN (02-28, 03-01, 03-02)
#
# Sanitização idêntica a prep_cic_train.py:
#   1. to_numeric(errors='coerce')
#   2. replace([inf, -inf], nan)
#   3. dropna(axis=1, how='all')
#   4. fillna(0)
#   5. valida chunk/features e concatena
# ---------------------------------------------------------------------------
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator, List, Optional

import numpy as np
import pandas as pd

RAW_DIR  = Path(r"data\raw\cicids2018")
OUT_EVAL = Path(r"data\cic_eval.csv")

CHUNKSIZE     = 200_000
ROWS_PER_FILE = 30_000   # deve ser igual ao de prep_cic_train.py (linhas do treino)
EVAL_PER_FILE = 10_000   # linhas de avaliação coletadas por arquivo (após offset)
N_CAP         = 100_000  # cap final do holdout
EVAL_SEED     = 123
COLS_TO_DROP  = {"flow_id", "src_ip", "dst_ip", "src_port"}


# ── Helpers ──────────────────────────────────────────────────────────────────

def snake(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[^0-9A-Za-z]+", "_", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_").lower()


def map_label(raw: str) -> str:
    """
    Mapeia rótulos reais do CIC-IDS2018 para classes agregadas.
    Idêntico ao map_label de prep_cic_train.py.
    """
    if raw is None:
        return "Others"
    s = str(raw).strip().lower()
    if s == "label":                                        # cabeçalho duplicado
        return "Others"
    if "benign" in s or s == "normal":
        return "Benign"
    if "ddos" in s:
        return "DDoS"
    if "dos" in s:
        return "DoS"
    if "sql" in s or "xss" in s or ("brute force" in s and "web" in s):
        return "Web"
    if "patator" in s or "bruteforce" in s or ("brute force" in s and "web" not in s):
        return "BruteForce"
    if "bot" in s:
        return "Bot"
    if "infiltration" in s:
        return "Infiltration"
    if "portscan" in s or "port scan" in s:
        return "PortScan"
    if "heartbleed" in s:
        return "Heartbleed"
    return "Others"


def iter_csv_files(dirpath: Path) -> Iterator[Path]:
    for p in sorted(dirpath.glob("*.csv")):
        yield p


# ── Leitura por arquivo (com offset anti-leakage) ────────────────────────────

def load_csv_eval_slice(csv_path: Path, skip: int, take: int) -> Optional[pd.DataFrame]:
    """
    Pula as primeiras `skip` linhas (usadas pelo treino) e coleta até
    `take` linhas a partir daí, aplicando sanitização completa.
    """
    collected: List[pd.DataFrame] = []
    total_seen = 0
    total_kept = 0

    try:
        for chunk in pd.read_csv(
            csv_path,
            low_memory=False,
            chunksize=CHUNKSIZE,
            on_bad_lines="skip",
        ):
            chunk_len = len(chunk)

            # Pula chunks inteiramente dentro do offset
            if total_seen + chunk_len <= skip:
                total_seen += chunk_len
                continue

            # Chunk parcialmente dentro do offset: corta o início
            if total_seen < skip:
                offset_in_chunk = skip - total_seen
                chunk = chunk.iloc[offset_in_chunk:].reset_index(drop=True)
                total_seen = skip

            chunk.columns = [snake(c) for c in chunk.columns]
            chunk = chunk.drop(columns=[c for c in COLS_TO_DROP if c in chunk.columns])

            # Detecta coluna de rótulo
            label_col = None
            for cand in ("label", "labels", "attack_category", "attack_cat"):
                if cand in chunk.columns:
                    label_col = cand
                    break
            if label_col is None:
                total_seen += chunk_len
                continue

            chunk["label"] = chunk[label_col].apply(map_label)

            # 1. Coerce das features para numérico (texto/corrompido -> NaN)
            feature_cols = [
                c for c in chunk.columns
                if c not in {"label", "labels", "attack_category", "attack_cat"}
            ]
            if not feature_cols:
                total_seen += chunk_len
                continue

            features = chunk[feature_cols].apply(pd.to_numeric, errors="coerce")

            # 2. Inf -> NaN
            features = features.replace([np.inf, -np.inf], np.nan)

            # 3. Remove colunas 100% NaN
            features = features.dropna(axis=1, how="all")

            # 4. Preenche NaN restante com 0
            features = features.fillna(0)

            if features.empty:
                total_seen += chunk_len
                continue

            df_keep = features.copy()
            df_keep["label"] = chunk["label"].values

            if df_keep.empty:
                total_seen += chunk_len
                continue

            # Cap preciso por arquivo
            restante = take - total_kept
            if len(df_keep) > restante:
                df_keep = df_keep.iloc[:restante]

            collected.append(df_keep)
            total_kept += len(df_keep)
            total_seen += chunk_len

            if total_kept >= take:
                break

    except Exception as e:
        print(f"[WARN] Falha lendo {csv_path.name}: {e}")
        return None

    if not collected:
        return None

    return pd.concat(collected, axis=0, ignore_index=True)


# ── Pipeline principal ────────────────────────────────────────────────────────

def build_eval() -> None:
    OUT_EVAL.parent.mkdir(parents=True, exist_ok=True)

    files = list(iter_csv_files(RAW_DIR))
    if not files:
        raise FileNotFoundError(f"Nenhum CSV encontrado em {RAW_DIR}")

    print(f"[INFO] {len(files)} arquivos encontrados em {RAW_DIR}")
    print(f"[INFO] Offset (linhas do treino): {ROWS_PER_FILE:,} por arquivo")
    print(f"[INFO] Coletando até {EVAL_PER_FILE:,} linhas por arquivo após offset\n")

    parts: List[pd.DataFrame] = []

    for csv_path in files:
        print(f"[INFO] Lendo {csv_path.name} ...")
        df_part = load_csv_eval_slice(csv_path, skip=ROWS_PER_FILE, take=EVAL_PER_FILE)
        if df_part is None or df_part.empty:
            print(f"       -> PULADO (sem linhas válidas após offset)")
            continue
        parts.append(df_part)
        dist = df_part["label"].value_counts().to_dict()
        print(f"       -> {len(df_part):,} linhas | {len(df_part.columns)-1} features | classes: {dist}")

    if not parts:
        raise RuntimeError("Nenhum chunk válido para avaliação.")

    # Alinha colunas: mantém apenas as presentes em TODOS os arquivos
    shared_cols = set.intersection(*[set(df.columns) for df in parts])
    ordered_cols = [
        c for c in parts[0].columns if c in shared_cols and c != "label"
    ] + ["label"]
    parts = [df[ordered_cols] for df in parts]

    df = pd.concat(parts, axis=0, ignore_index=True)
    df["label"] = df["label"].astype(str)

    # Cap final estratificado
    if len(df) > N_CAP:
        df = (
            df.groupby("label", group_keys=False)
            .apply(lambda g: g.sample(frac=N_CAP / len(df), random_state=EVAL_SEED))
            .reset_index(drop=True)
        )

    # Embaralha
    df = df.sample(frac=1, random_state=EVAL_SEED).reset_index(drop=True)

    df.to_csv(OUT_EVAL, index=False, float_format="%.10f")
    print(f"\n[OK] Holdout salvo em: {OUT_EVAL}  (n={len(df):,}, features={len(df.columns)-1})")
    print(f"     Distribuição:\n{df['label'].value_counts().to_string()}")
    print()
    print(f"NOTA: treino usou linhas 0–{ROWS_PER_FILE:,} de cada arquivo.")
    print(f"      eval usou linhas {ROWS_PER_FILE:,}–{ROWS_PER_FILE+EVAL_PER_FILE:,} — sem sobreposição.")


if __name__ == "__main__":
    build_eval()
