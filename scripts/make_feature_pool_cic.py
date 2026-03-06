import json
from pathlib import Path
import pandas as pd

in_csv = Path("data/train_cic.csv")
out_dir = Path("artifacts")
out_fp  = out_dir / "feature_pool_cic.json"

if out_fp.exists():
    print(f"[OK] {out_fp} já existe - mantendo como está.")
else:
    print(f"[MAKE] Gerando {out_fp} a partir de {in_csv}...")
    df = pd.read_csv(in_csv, low_memory=False)
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and c != "label"]

    var = df[num_cols].var(numeric_only=True).sort_values(ascending=False)
    ordered = list(var.index)

    sets = {
        "PSO_4": ordered[:20],
        "PSO_5": ordered[20:40],
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    out_fp.write_text(json.dumps({"feature_sets": sets}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] feature_pool salvo em {out_fp}")
