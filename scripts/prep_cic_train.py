# scripts/prep_cic_train.py
# ---------------------------------------------------------------------------
# Gera train_cic.csv e cic_infer.csv a partir dos CSVs brutos do CIC-IDS2018.
#
# Achados do EDA:
#   - 80 colunas por arquivo, todas numéricas (exceto 02-20 com 79)
#   - 03-01-2018.csv tem cabeçalho duplicado no meio -> 0 numéricas -> pulado
#   - Apenas flow_byts_s e flow_pkts_s têm Inf/NaN (02-28, 03-01, 03-02)
#   - Não existe coluna timestamp
#
# Sanitização:
#   1. to_numeric(errors='coerce')          — força features numéricas
#   2. replace([inf, -inf], nan)            — Inf -> NaN
#   3. dropna(axis=1, how='all')            — remove colunas 100% NaN
#   4. fillna(0)                            — preenche NaN restante com 0
#   5. valida chunk/features e concatena    — alinha colunas entre arquivos
# ---------------------------------------------------------------------------
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator, List, Optional

import numpy as np
import pandas as pd

RAW_DIR   = Path(r"data\raw\cicids2018")
OUT_TRAIN = Path(r"data\train_cic.csv")
OUT_INFER = Path(r"data\cic_infer.csv")

CHUNKSIZE     = 200_000
ROWS_PER_FILE = 30_000   # linhas coletadas por arquivo para o treino
MAX_ROWS      = 300_000  # cap final do dataset de treino
INFER_ROWS    = 1_000
TRAIN_SEED    = 42
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
    Rótulos observados no EDA:
      Benign, FTP-BruteForce, DoS attacks-GoldenEye, DoS attacks-SlowHTTPTest,
      DDoS attacks-LOIC-HTTP, DDOS attack-LOIC-UDP, Brute Force -Web,
      Brute Force -XSS, SQL Injection, Bot
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


# ── Leitura por arquivo ───────────────────────────────────────────────────────

def load_csv_sample(csv_path: Path, rows: int) -> Optional[pd.DataFrame]:
    """
    Lê até `rows` linhas do CSV, aplicando sanitização completa.
    Retorna None se o arquivo não tiver colunas numéricas válidas.
    """
    collected: List[pd.DataFrame] = []
    total = 0

    try:
        for chunk in pd.read_csv(
            csv_path,
            low_memory=False,
            chunksize=CHUNKSIZE,
            on_bad_lines="skip",
        ):
            chunk.columns = [snake(c) for c in chunk.columns]
            chunk = chunk.drop(columns=[c for c in COLS_TO_DROP if c in chunk.columns])

            # Detecta coluna de rótulo
            label_col = None
            for cand in ("label", "labels", "attack_category", "attack_cat"):
                if cand in chunk.columns:
                    label_col = cand
                    break
            if label_col is None:
                continue

            chunk["label"] = chunk[label_col].apply(map_label)

            # 1. Coerce das features para numérico (texto/corrompido -> NaN)
            feature_cols = [
                c for c in chunk.columns
                if c not in {"label", "labels", "attack_category", "attack_cat"}
            ]
            if not feature_cols:
                continue

            features = chunk[feature_cols].apply(pd.to_numeric, errors="coerce")

            # 2. Inf -> NaN
            features = features.replace([np.inf, -np.inf], np.nan)

            # 3. Remove colunas 100% NaN (ex.: coluna corrompida inteira)
            features = features.dropna(axis=1, how="all")

            # 4. Preenche NaN restante com 0 (ex.: flow_byts_s, flow_pkts_s)
            features = features.fillna(0)

            if features.empty:
                continue

            df_keep = features.copy()
            df_keep["label"] = chunk["label"].values

            if df_keep.empty:
                continue

            # Cap preciso por arquivo
            restante = rows - total
            if len(df_keep) > restante:
                df_keep = df_keep.iloc[:restante]

            collected.append(df_keep)
            total += len(df_keep)

            if total >= rows:
                break

    except Exception as e:
        print(f"[WARN] Falha lendo {csv_path.name}: {e}")
        return None

    if not collected:
        return None

    return pd.concat(collected, axis=0, ignore_index=True)


# ── Pipeline principal ────────────────────────────────────────────────────────

def load_build_train() -> None:
    OUT_TRAIN.parent.mkdir(parents=True, exist_ok=True)
    OUT_INFER.parent.mkdir(parents=True, exist_ok=True)

    files = list(iter_csv_files(RAW_DIR))
    if not files:
        raise FileNotFoundError(f"Nenhum CSV encontrado em {RAW_DIR}")

    print(f"[INFO] {len(files)} arquivos encontrados em {RAW_DIR}")
    print(f"[INFO] Coletando até {ROWS_PER_FILE:,} linhas por arquivo\n")

    parts: List[pd.DataFrame] = []

    for csv_path in files:
        print(f"[INFO] Lendo {csv_path.name} ...")
        df_part = load_csv_sample(csv_path, ROWS_PER_FILE)
        if df_part is None or df_part.empty:
            print(f"       -> PULADO (sem colunas numéricas válidas)")
            continue
        parts.append(df_part)
        dist = df_part["label"].value_counts().to_dict()
        print(f"       -> {len(df_part):,} linhas | {len(df_part.columns)-1} features | classes: {dist}")

    if not parts:
        raise RuntimeError("Nenhum chunk válido encontrado.")

    # Alinha colunas: mantém apenas as presentes em TODOS os arquivos
    shared_cols = set.intersection(*[set(df.columns) for df in parts])
    ordered_cols = [
        c for c in parts[0].columns if c in shared_cols and c != "label"
    ] + ["label"]
    parts = [df[ordered_cols] for df in parts]

    df = pd.concat(parts, axis=0, ignore_index=True)
    df["label"] = df["label"].astype(str)

    # Cap final estratificado
    if len(df) > MAX_ROWS:
        df = (
            df.groupby("label", group_keys=False)
            .apply(lambda g: g.sample(frac=MAX_ROWS / len(df), random_state=TRAIN_SEED))
            .reset_index(drop=True)
        )

    # Embaralha
    df = df.sample(frac=1, random_state=TRAIN_SEED).reset_index(drop=True)

    df.to_csv(OUT_TRAIN, index=False, float_format="%.10f")
    print(f"\n[OK] Train salvo em: {OUT_TRAIN}  (n={len(df):,}, features={len(df.columns)-1})")
    print(f"     Distribuição:\n{df['label'].value_counts().to_string()}")

    infer = df.sample(n=min(INFER_ROWS, len(df)), random_state=TRAIN_SEED).drop(columns=["label"])
    infer.to_csv(OUT_INFER, index=False, float_format="%.10f")
    print(f"\n[OK] Infer salvo em: {OUT_INFER}  (n={len(infer):,})")


if __name__ == "__main__":
    load_build_train()
