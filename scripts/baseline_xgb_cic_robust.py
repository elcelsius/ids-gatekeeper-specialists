"""
Baseline global (XGBoost) para CIC-IDS2018 robusto (sem porta de destino).

Explicação para estudantes:
O que é um "Baseline"? 
Em Inteligência Artificial, um baseline é o "modelo mais básico possível" ou o 
"padrão da indústria" que você usa como régua de comparação. Se o seu modelo 
novo ou seu funil complexo (como o nosso de Especialistas) não superar este 
XGBoost "simples e poderoso", então a sua complexidade não se justifica na prática!

Fluxo do Baseline:
- Lê as bases de dados e mapeia rótulos para binário: Benign/Attack.
- Usa todas as colunas numéricas (exceto o rótulo) como características (features).
- Treina um XGBClassifier único e global (sem divisão por especialistas).
- Avalia no conjunto de teste e salva as métricas e a matriz de confusão.
"""
from __future__ import annotations

from pathlib import Path
import sys
import json

import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix

try:
    from xgboost import XGBClassifier
except Exception as e:  # pragma: no cover - guard para ambiente sem xgboost
    sys.stderr.write(
        "[ERRO] xgboost não está instalado. Instale no venv (ex.: pip install xgboost) para rodar este baseline.\n"
    )
    sys.stderr.write(f"Detalhes: {e}\n")
    sys.exit(1)


TRAIN_CSV = Path("data/train_cic_robust.csv")
EVAL_CSV = Path("data/cic_eval_robust.csv")
OUT_DIR = Path("outputs/cic_robust_xgb_baseline")
TARGET_COL = "label"


def _label_to_code(val: object) -> int:
    """Normaliza para 0 (Benign) / 1 (Attack) para treino/avaliação interna."""
    s = str(val).strip().lower()
    if s in {"0", "benign", "normal", "benign traffic", "benign_traffic"}:
        return 0
    try:
        if int(val) == 0:
            return 0
    except Exception:
        pass
    return 1


def _code_to_str(v: int) -> str:
    return "Benign" if int(v) == 0 else "Attack"


def main() -> None:
    if not TRAIN_CSV.exists() or not EVAL_CSV.exists():
        raise FileNotFoundError(f"Arquivos de entrada não encontrados: {TRAIN_CSV} / {EVAL_CSV}")

    print(f"[LOAD] {TRAIN_CSV}")
    train = pd.read_csv(TRAIN_CSV, low_memory=False)
    print(f"[LOAD] {EVAL_CSV}")
    eval_df = pd.read_csv(EVAL_CSV, low_memory=False)

    # Features: numéricas exceto alvo
    num_cols = [c for c in train.columns if c != TARGET_COL and pd.api.types.is_numeric_dtype(train[c])]
    if not num_cols:
        raise RuntimeError("Nenhuma coluna numérica encontrada para o baseline.")

    X_train = train[num_cols]
    y_train = train[TARGET_COL].apply(_label_to_code)

    X_eval = eval_df[num_cols]
    y_true = eval_df[TARGET_COL].apply(_label_to_code)

    print(f"[INFO] Features usadas: {len(num_cols)} colunas numéricas.")

    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        tree_method="hist",
        eval_metric="logloss",
        random_state=42,
        n_jobs=0,
    )

    print("[FIT] Treinando XGBClassifier global (baseline)...")
    model.fit(X_train, y_train)

    print("[PRED] Avaliando no conjunto robusto de validação...")
    y_pred = model.predict(X_eval)
    y_true_str = pd.Series(y_true).apply(_code_to_str)
    y_pred_str = pd.Series(y_pred).apply(_code_to_str)

    labels = ["Benign", "Attack"]
    rep = classification_report(y_true_str, y_pred_str, labels=labels, zero_division=0, output_dict=True)
    cm = confusion_matrix(y_true_str, y_pred_str, labels=labels)

    # Salvando saídas
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics_path = OUT_DIR / "metrics_cic_robust_xgb_baseline.csv"
    cm_path = OUT_DIR / "confusion_matrix_cic_robust_xgb_baseline.csv"

    # classification_report em CSV
    pd.DataFrame(rep).to_csv(metrics_path, encoding="utf-8")
    pd.DataFrame(cm, index=[f"true_{l}" for l in labels], columns=[f"pred_{l}" for l in labels]).to_csv(
        cm_path, encoding="utf-8"
    )

    print(f"[OK] classification_report salvo em {metrics_path}")
    print(f"[OK] matriz de confusão salva em {cm_path}")

    # Impressão legível
    print("\n=== Classification report (Benign vs Attack) ===")
    print(json.dumps(rep, indent=2))
    print("\n=== Confusion matrix ===")
    print(pd.DataFrame(cm, index=labels, columns=labels))


if __name__ == "__main__":
    main()
