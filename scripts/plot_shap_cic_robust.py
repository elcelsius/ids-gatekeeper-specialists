"""
Treina XGBoost global no CIC-IDS2018 robusto (binário) e gera summary plot SHAP (importância global).
Entrada: data/train_cic_robust.csv, data/cic_eval_robust.csv
Saída: figs/fig6_cic_robust_shap_importance.png
"""
from __future__ import annotations

from pathlib import Path
import sys
import json

import pandas as pd
import numpy as np
try:
    import matplotlib.pyplot as plt
except ImportError as e:  # pragma: no cover
    sys.stderr.write("[ERRO] matplotlib não está instalado. Instale com: pip install matplotlib\n")
    sys.stderr.write(f"Detalhes: {e}\n")
    sys.exit(1)

try:
    import shap
except ImportError as e:  # pragma: no cover
    sys.stderr.write("[ERRO] shap não está instalado. Instale com: pip install shap\n")
    sys.stderr.write(f"Detalhes: {e}\n")
    sys.exit(1)

try:
    from xgboost import XGBClassifier, Booster
except Exception as e:  # pragma: no cover
    sys.stderr.write("[ERRO] xgboost não está instalado. Instale no venv (ex.: pip install xgboost).\n")
    sys.stderr.write(f"Detalhes: {e}\n")
    sys.exit(1)


TRAIN_CSV = Path("data/train_cic_robust.csv")
EVAL_CSV = Path("data/cic_eval_robust.csv")
FIG_DIR = Path("figs")
FIG_PATH = FIG_DIR / "fig6_cic_robust_shap_importance.png"
TARGET_COL = "label"
SAMPLE_N = 10_000


def _label_to_code(val: object) -> int:
    """0 (Benign) / 1 (Attack)"""
    s = str(val).strip().lower()
    if s in {"0", "benign", "normal", "benign traffic", "benign_traffic"}:
        return 0
    try:
        if int(val) == 0:
            return 0
    except Exception:
        pass
    return 1


def main() -> None:
    if not TRAIN_CSV.exists() or not EVAL_CSV.exists():
        raise FileNotFoundError(f"Arquivos de entrada não encontrados: {TRAIN_CSV} / {EVAL_CSV}")

    print(f"[LOAD] {TRAIN_CSV}")
    train = pd.read_csv(TRAIN_CSV, low_memory=False)
    print(f"[LOAD] {EVAL_CSV}")
    eval_df = pd.read_csv(EVAL_CSV, low_memory=False)

    # Features numéricas
    num_cols = [c for c in train.columns if c != TARGET_COL and pd.api.types.is_numeric_dtype(train[c])]
    if not num_cols:
        raise RuntimeError("Nenhuma coluna numérica encontrada para o SHAP.")

    X_train = train[num_cols]
    y_train = train[TARGET_COL].apply(_label_to_code)

    X_eval = eval_df[num_cols]

    # Amostragem para SHAP
    if len(X_eval) > SAMPLE_N:
        X_eval_sample = X_eval.sample(n=SAMPLE_N, random_state=42)
    else:
        X_eval_sample = X_eval

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
        base_score=0.5,
    )

    print("[FIT] Treinando XGBClassifier global (baseline) para SHAP...")
    model.fit(X_train, y_train)

    print(f"[SHAP] Calculando SHAP values em {len(X_eval_sample)} amostras...")
    shap_values = None
    try:
        if hasattr(model, "save_config"):
            _orig_save_config = model.save_config

            def _clean_save_config(*args, **kwargs):
                conf = _orig_save_config(*args, **kwargs)
                return re.sub(r'"base_score":\s*"\[?([0-9.eE+-]+)\]?"', r'"base_score": "\1"', conf)

            model.save_config = _clean_save_config  # type: ignore[attr-defined]

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_eval_sample)
    except Exception as e:
        print(f"[WARN] TreeExplainer falhou ({e}); usando KernelExplainer com amostra reduzida.")
        bg = X_train.sample(n=min(500, len(X_train)), random_state=42)
        eval_sample_small = X_eval_sample.iloc[: min(500, len(X_eval_sample))]
        kexplainer = shap.KernelExplainer(lambda data: model.predict_proba(data)[:, 1], bg)
        shap_values = kexplainer.shap_values(eval_sample_small)
        X_eval_sample = eval_sample_small

    print(f"[PLOT] Salvando summary plot em {FIG_PATH}")
    shap.summary_plot(shap_values, X_eval_sample, plot_type="bar", show=False)
    plt.tight_layout()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(FIG_PATH, dpi=300)
    plt.close()
    print(f"[OK] Figura salva em {FIG_PATH}")


if __name__ == "__main__":
    main()
