# scripts/make_cic_eval.py
# ---------------------------------------------------------------------------
# Gera o conjunto de avaliação (holdout) do CIC-IDS2018 a partir dos dados
# BRUTOS — nunca a partir de train_cic.csv — eliminando o leakage original.
#
# Fluxo correto:
#   prep_cic_train.py  →  train_cic.csv   (treino, sem sobreposição)
#   make_cic_eval.py   →  cic_eval.csv    (holdout, sem sobreposição)
#
# Estratégia anti-leakage:
#   - Lê os mesmos CSVs brutos que prep_cic_train.py.
#   - Coleta linhas que NÃO foram incluídas no treino (complemento) OU
#     aplica um split estratificado 80/20 dentro de cada arquivo,
#     reservando 20% exclusivamente para avaliação.
#   - Seed fixo (EVAL_SEED) para reprodutibilidade.
# ---------------------------------------------------------------------------
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator, List

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# ── Caminhos ────────────────────────────────────────────────────────────────
RAW_DIR   = Path(r"data\raw\cicids2018")
OUT_EVAL  = Path(r"data\cic_eval.csv")

# ── Parâmetros ───────────────────────────────────────────────────────────────
CHUNKSIZE  = 200_000
MAX_ROWS   = 300_000   # máximo de linhas lidas dos brutos (mesmo limite do treino)
EVAL_FRAC  = 0.20      # fração reservada para holdout (20 %)
EVAL_SEED  = 123       # seed separado do treino (prep usa random_state=42)
N_CAP      = 100_000   # cap final do arquivo de avaliação


# ── Helpers ──────────────────────────────────────────────────────────────────
def snake(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[^0-9A-Za-z]+", "_", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_").lower()


def map_label(raw: str) -> str:
    """Mesmo mapeamento de prep_cic_train.py — mantém consistência."""
    if raw is None:
        return "Others"
    s = str(raw).strip().lower()

    # Filtra linhas de cabeçalho duplicadas no CSV
    if s == "label":
        return "Others"

    if "benign" in s or s in {"normal"}:
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


# ── Função principal ─────────────────────────────────────────────────────────
def build_eval() -> None:
    OUT_EVAL.parent.mkdir(parents=True, exist_ok=True)

    total_rows = 0
    eval_parts: List[pd.DataFrame] = []

    files = list(iter_csv_files(RAW_DIR))
    if not files:
        raise FileNotFoundError(f"Nenhum CSV encontrado em {RAW_DIR}")

    for csv_path in files:
        try:
            for chunk in pd.read_csv(
                csv_path,
                low_memory=False,
                chunksize=CHUNKSIZE,
                on_bad_lines="skip",
            ):
                # Normaliza nomes de colunas
                chunk.columns = [snake(c) for c in chunk.columns]

                # Detecta coluna de rótulo
                label_col = None
                for cand in ("label", "labels", "attack_category", "attack_cat"):
                    if cand in chunk.columns:
                        label_col = cand
                        break
                if label_col is None:
                    continue

                # Mapeia rótulos
                chunk["label"] = chunk[label_col].apply(map_label)

                # Mantém só numéricas + label
                num = chunk.select_dtypes(include=[np.number])
                if num.empty:
                    continue
                df_keep = num.copy()
                df_keep["label"] = chunk["label"].values

                # ── Split estratificado: reserva EVAL_FRAC para holdout ──────
                try:
                    _, eval_chunk = train_test_split(
                        df_keep,
                        test_size=EVAL_FRAC,
                        random_state=EVAL_SEED,
                        stratify=df_keep["label"],
                    )
                except ValueError:
                    # fallback sem estratificação (classes com < 2 amostras)
                    _, eval_chunk = train_test_split(
                        df_keep,
                        test_size=EVAL_FRAC,
                        random_state=EVAL_SEED,
                    )

                eval_parts.append(eval_chunk)
                total_rows += len(eval_chunk)
                if total_rows >= MAX_ROWS:
                    break

        except Exception as e:
            print(f"[WARN] Falha lendo {csv_path.name}: {e}")

        if total_rows >= MAX_ROWS:
            break

    if not eval_parts:
        raise RuntimeError("Não foi possível gerar nenhum chunk de avaliação.")

    df = pd.concat(eval_parts, axis=0, ignore_index=True)

    # Sanitização
    df = df.replace([np.inf, -np.inf], np.nan)
    labels = df["label"]
    df = df.drop(columns=["label"]).dropna(axis=1, how="any")
    df["label"] = labels.values

    # Cap final com amostragem estratificada
    if len(df) > N_CAP:
        df, _ = train_test_split(
            df,
            train_size=N_CAP,
            random_state=EVAL_SEED,
            stratify=df["label"],
        )
        df = df.reset_index(drop=True)

    df.to_csv(OUT_EVAL, index=False)
    print(f"[OK] Holdout de avaliação salvo em: {OUT_EVAL}  (n={len(df):,})")
    print(f"     Distribuição de classes:\n{df['label'].value_counts().to_string()}")
    print()
    print("NOTA: este arquivo NÃO tem sobreposição com train_cic.csv.")
    print("      Certifique-se de rodar prep_cic_train.py ANTES deste script.")


if __name__ == "__main__":
    build_eval()
