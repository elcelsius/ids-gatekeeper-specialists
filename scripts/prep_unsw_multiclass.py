import pandas as pd
from pathlib import Path

# Caminhos de entrada (brutos)
train_in = "data/raw/unsw/UNSW_NB15_training-set.csv"
test_in  = "data/raw/unsw/UNSW_NB15_testing-set.csv"

print(f"Lendo treino: {train_in}")
train = pd.read_csv(train_in, low_memory=False)

print(f"Lendo teste:  {test_in}")
test = pd.read_csv(test_in, low_memory=False)

# Garante que attack_cat exista e não tenha NaN
if "attack_cat" not in train.columns:
    raise ValueError("Coluna 'attack_cat' não encontrada no treino UNSW.")
if "attack_cat" not in test.columns:
    raise ValueError("Coluna 'attack_cat' não encontrada no teste UNSW.")

train["attack_cat"] = train["attack_cat"].fillna("Normal")
test["attack_cat"]  = test["attack_cat"].fillna("Normal")

# Diretório de saída
Path("data").mkdir(parents=True, exist_ok=True)

train_out = "data/UNSW_train_mc.csv"
test_out  = "data/UNSW_test_mc.csv"

print(f"Salvando treino multi-classe em: {train_out}")
train.to_csv(train_out, index=False)

print(f"Salvando teste multi-classe em: {test_out}")
test.to_csv(test_out, index=False)

print("OK: UNSW multi-classe preparado.")
