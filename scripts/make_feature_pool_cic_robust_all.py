import json
import pandas as pd
from pathlib import Path

csv_path = "data/train_cic_robust.csv"

print(f"Lendo {csv_path} ...")
df = pd.read_csv(csv_path, low_memory=False)

target_col = "label"

# Todas as colunas numéricas, exceto o alvo
num_cols = [
    c for c in df.columns
    if pd.api.types.is_numeric_dtype(df[c]) and c != target_col
]

print(f"Encontradas {len(num_cols)} colunas numéricas no CIC robusto (todas serão usadas).")

feature_sets = {
    "CIC_RB_ALL": num_cols
}

feature_pool = {"feature_sets": feature_sets}

out_path = Path("artifacts/feature_pool_cic_robust_all.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(feature_pool, indent=2), encoding="utf-8")

print(f"Feature pool 'sem seleção de atributos' salvo em: {out_path.resolve()}")
