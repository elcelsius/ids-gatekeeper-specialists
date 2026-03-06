# scripts/make_gatekeeper_cols_from_csv.py
from __future__ import annotations
from pathlib import Path
import argparse
import pandas as pd
import numpy as np

def main():
    ap = argparse.ArgumentParser(description="Gera lista de colunas numéricas para o Gatekeeper (uma por linha).")
    ap.add_argument("--csv", type=Path, default=Path(r"data\train_cic.csv"), help="CSV de treino rotulado.")
    ap.add_argument("--out", type=Path, default=Path(r"gatekeeper_cic_cols.txt"), help="Arquivo .txt de saída.")
    ap.add_argument("--max_cols", type=int, default=12, help="Limite de colunas (para latência baixa).")
    args = ap.parse_args()

    if not args.csv.exists():
        raise FileNotFoundError(f"CSV não encontrado: {args.csv}")
    # lê só o cabeçalho + primeira parte para inferir dtypes
    df = pd.read_csv(args.csv, nrows=2000, low_memory=False)
    if "label" in df.columns:
        df = df.drop(columns=["label"])
    nums = df.select_dtypes(include=[np.number]).columns.tolist()
    if not nums:
        raise RuntimeError("Nenhuma coluna numérica encontrada no CSV.")
    cols = nums[: args.max_cols]
    args.out.write_text("\n".join(cols), encoding="utf-8")
    print(f"[OK] {len(cols)} colunas salvas em {args.out}")
    for c in cols:
        print(" -", c)

if __name__ == "__main__":
    main()
