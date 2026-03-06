# scripts/make_feature_pool_min.py
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_csv", required=True, help="CSV de treino (ex.: data/train_cic.csv)")
    ap.add_argument("--out", dest="out_json", required=True, help="Saída JSON (ex.: artifacts/feature_pool_cic.json)")
    ap.add_argument("--target", dest="target_col", default="label")
    ap.add_argument("--max_per_set", dest="max_per_set", type=int, default=20)
    args = ap.parse_args()

    in_csv  = Path(args.in_csv)
    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)

    print(f"[MAKE] Lendo {in_csv} …")
    df = pd.read_csv(in_csv, low_memory=False)

    # apenas numéricas, exceto o rótulo
    num_cols = [c for c in df.columns if c != args.target_col and pd.api.types.is_numeric_dtype(df[c])]
    if not num_cols:
        raise RuntimeError("Nenhuma coluna numérica encontrada para o pool de features.")

    # ordena por variância (desc)
    var = df[num_cols].var(numeric_only=True).sort_values(ascending=False)
    ordered = list(var.index)

    # dois conjuntos simples (ajuste à vontade depois)
    k = max(1, args.max_per_set)
    sets = {
        "PSO_4": ordered[:k],
        "PSO_5": ordered[k: 2*k]
    }

    payload = {"feature_sets": sets}
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] feature_pool salvo em {out_json} com chave 'feature_sets'.")

if __name__ == "__main__":
    main()
