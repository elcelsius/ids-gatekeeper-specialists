import pandas as pd
from pathlib import Path

# Caminhos de entrada padrão do CIC (ajuste se no seu repo estiver diferente)
train_in = "data/train_cic.csv"
eval_in  = "data/cic_eval.csv"

print(f"Lendo treino: {train_in}")
train = pd.read_csv(train_in, low_memory=False)

print(f"Lendo eval:   {eval_in}")
eval_ = pd.read_csv(eval_in, low_memory=False)

# Nomes possíveis da coluna de porta de destino no CIC
candidate_cols = ["dst_port", "Destination Port", "Dst Port", "dst_port_num"]

drop_cols = [c for c in candidate_cols if c in train.columns]

if not drop_cols:
    raise ValueError(f"Nenhuma coluna de porta de destino encontrada entre: {candidate_cols}")

print(f"Removendo colunas de porta de destino: {drop_cols}")

train_robust = train.drop(columns=drop_cols)
eval_robust  = eval_.drop(columns=drop_cols)

out_train = "data/train_cic_robust.csv"
out_eval  = "data/cic_eval_robust.csv"

Path("data").mkdir(parents=True, exist_ok=True)

print(f"Salvando treino robusto em: {out_train}")
train_robust.to_csv(out_train, index=False)

print(f"Salvando eval robusto em:   {out_eval}")
eval_robust.to_csv(out_eval, index=False)

print("OK: versões robustas do CIC geradas (sem porta de destino).")
