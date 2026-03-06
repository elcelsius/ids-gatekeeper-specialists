import json
import pandas as pd
from pathlib import Path

# Usa o treino multi-classe que você já gerou
csv_path = "data/UNSW_train_mc.csv"

print(f"Lendo {csv_path} ...")
df = pd.read_csv(csv_path, low_memory=False)

# Colunas que NÃO vão entrar nos conjuntos de atributos
target_cols = {"label", "attack_cat"}

# Pega só colunas numéricas, excluindo os alvos
num_cols = [
    c for c in df.columns
    if pd.api.types.is_numeric_dtype(df[c]) and c not in target_cols
]

print(f"Encontradas {len(num_cols)} colunas numéricas (sem label/attack_cat).")

# Cria alguns conjuntos de atributos (até 20 features cada)
feature_sets = {
    "UNSW_MC_FS_1": num_cols[:20],
    "UNSW_MC_FS_2": num_cols[20:40],
}

feature_pool = {"feature_sets": feature_sets}

out_path = Path("artifacts/feature_pool_unsw_mc.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(feature_pool, indent=2), encoding="utf-8")

print(f"Feature pool multi-classe salvo em: {out_path.resolve()}")
