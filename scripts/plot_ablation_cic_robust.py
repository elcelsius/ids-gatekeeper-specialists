"""
Gera gráfico de barras comparando F1-macro no CIC-IDS2018 robusto (binário):
- 2D-AEF (FS≤20)
- 2D-AEF (ALL)
- XGBoost global
Entradas: metrics CSV (classification_report output_dict=True) com linha "macro avg" e coluna "f1-score".
Saída: figs/fig5_cic_robust_ablation_f1_macro.png
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


FILES = [
    ("2D-AEF (FS≤20)", Path("outputs/cic_robust/metrics_cic_robust_binary.csv")),
    ("2D-AEF (ALL)", Path("outputs/cic_robust_all/metrics_cic_robust_all_binary.csv")),
    ("XGBoost global", Path("outputs/cic_robust_xgb_baseline/metrics_cic_robust_xgb_baseline.csv")),
]
FIG_DIR = Path("figs")
FIG_PATH = FIG_DIR / "fig5_cic_robust_ablation_f1_macro.png"


def _get_f1_macro(csv_path: Path) -> float:
    if not csv_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")
    df = pd.read_csv(csv_path)

    # tentar reconstruir índice
    if "Unnamed: 0" in df.columns:
        df = df.set_index("Unnamed: 0")
    elif df.columns.size > 0:
        first_col = str(df.columns[0]).strip().lower()
        if first_col not in {"precision", "recall", "f1-score", "f1_score", "support"}:
            df = df.set_index(df.columns[0])

    # normaliza labels
    df.index = df.index.map(lambda x: str(x).strip())
    df.columns = df.columns.map(lambda x: str(x).strip())

    idx_lower = [i.lower() for i in df.index]
    col_lower = [c.lower() for c in df.columns]

    # 1) tentar achar macro avg como linha + f1 como coluna
    row_candidates = [df.index[i] for i, name in enumerate(idx_lower) if "macro" in name and "avg" in name]
    col_candidates = [df.columns[j] for j, name in enumerate(col_lower) if "f1" in name]
    if row_candidates and col_candidates:
        return float(df.loc[row_candidates[0], col_candidates[0]])

    # 1b) tentar achar macro avg como coluna + f1 como linha (layout invertido, ex.: baseline)
    col_macro_candidates = [df.columns[j] for j, name in enumerate(col_lower) if "macro" in name and "avg" in name]
    row_f1_candidates = [df.index[i] for i, name in enumerate(idx_lower) if "f1" in name]
    if col_macro_candidates and row_f1_candidates:
        return float(df.loc[row_f1_candidates[0], col_macro_candidates[0]])

    # 2) fallback: calcular F1-macro manual a partir de Benign/Attack
    benign_rows = [df.index[i] for i, name in enumerate(idx_lower) if "benign" in name]
    attack_rows = [df.index[i] for i, name in enumerate(idx_lower) if "attack" in name]
    if not benign_rows or not attack_rows:
        raise KeyError(f"Não encontrei macro avg nem linhas Benign/Attack em {csv_path}")
    f1_candidates = [c for c in df.columns if "f1" in c.lower()]
    if not f1_candidates:
        raise KeyError(f"Não encontrei coluna de f1 em {csv_path}")

    col = f1_candidates[0]
    f1_benign = float(df.loc[benign_rows[0], col])
    f1_attack = float(df.loc[attack_rows[0], col])
    return 0.5 * (f1_benign + f1_attack)


def main() -> None:
    labels = []
    values = []
    for lbl, path in FILES:
        labels.append(lbl)
        values.append(_get_f1_macro(path))

    fig, ax = plt.subplots(figsize=(5, 3), dpi=300)
    bars = ax.bar(labels, values, color=["#4C78A8", "#72B7B2", "#F58518"])
    ax.set_title("Ablação no CIC-IDS2018 robusto (F1-macro)")
    ax.set_ylabel("F1-macro")
    ax.set_ylim(0, 1.05 * max(values))  # espaço para o rótulo
    ax.set_xticklabels(labels, rotation=20, ha="right")

    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{val:.5f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    fig.tight_layout()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_PATH)
    plt.close(fig)
    print(f"[OK] Figura salva em {FIG_PATH}")


if __name__ == "__main__":
    main()
