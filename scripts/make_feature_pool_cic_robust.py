import json
import pandas as pd
from pathlib import Path

csv_path = "data/train_cic_robust.csv"

print(f"Lendo {csv_path} ...")
df = pd.read_csv(csv_path, low_memory=False)

# Coluna alvo binária (ajuste se o nome divergir no seu CSV)
target_col = "label"

# Seleciona apenas colunas numéricas, exceto o alvo
num_cols = [
    c for c in df.columns
    if pd.api.types.is_numeric_dtype(df[c]) and c != target_col
]

print(f"Encontradas {len(num_cols)} colunas numéricas no CIC robusto.")

# Cria alguns feature sets com até 20 atributos cada
feature_sets = {
    "CIC_RB_FS_1": num_cols[:20],
    "CIC_RB_FS_2": num_cols[20:40],
}

feature_pool = {"feature_sets": feature_sets}

out_path = Path("artifacts/feature_pool_cic_robust.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(feature_pool, indent=2), encoding="utf-8")

print(f"Feature pool CIC robusto salvo em: {out_path.resolve()}")
