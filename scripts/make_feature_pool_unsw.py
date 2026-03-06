import json
import pandas as pd
from pathlib import Path

# Caminho do CSV de treino bruto do UNSW
csv_path = "data/raw/unsw/UNSW_NB15_training-set.csv"

print(f"Lendo {csv_path} ...")
df = pd.read_csv(csv_path, low_memory=False)

# Coluna-alvo binária (ajuste se no seu CSV o nome divergir)
target_col = "label"

# Seleciona apenas colunas numéricas, exceto o alvo
num_cols = [
    c for c in df.columns
    if pd.api.types.is_numeric_dtype(df[c]) and c != target_col
]

print(f"Encontradas {len(num_cols)} colunas numéricas para o UNSW.")

# Aqui criamos 2 feature sets de exemplo, só para ter diversidade
feature_sets = {
    "UNSW_FS_1": num_cols[:20],          # primeiras 20 features
    "UNSW_FS_2": num_cols[20:40],       # próximas 20 (ajuste se tiver menos)
}

feature_pool = {"feature_sets": feature_sets}

out_path = Path("artifacts/feature_pool_unsw.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(feature_pool, indent=2), encoding="utf-8")

print(f"Feature pool salvo em: {out_path.resolve()}")
