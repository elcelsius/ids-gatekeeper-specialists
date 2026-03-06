"""
Gera gráfico de barras com as latências médias do pipeline 2D-AEF no CIC-IDS2018 robusto (binário).
Entrada: outputs/cic_robust/preds.csv
Saída:  figs/fig4_cic_robust_latency.png
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


PREDS_PATH = Path("outputs/cic_robust/preds.csv")
FIG_DIR = Path("figs")
FIG_PATH = FIG_DIR / "fig4_cic_robust_latency.png"


def main() -> None:
    if not PREDS_PATH.exists():
        raise FileNotFoundError(f"Arquivo de predições não encontrado: {PREDS_PATH}")

    df = pd.read_csv(PREDS_PATH, low_memory=False)
    cols = ["latency_ms_stage1", "latency_ms_stage2", "latency_ms_total_est"]
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"Colunas de latência ausentes em preds.csv: {missing}")

    means = [df[c].mean() for c in cols]
    labels = ["Gatekeeper", "Especialistas", "Total"]

    fig, ax = plt.subplots(figsize=(5, 3), dpi=300)
    bars = ax.bar(labels, means, color=["#4C78A8", "#F58518", "#54A24B"])
    ax.set_title("Latência média – CIC-IDS2018 robusto (2D-AEF)")
    ax.set_ylabel("Latência média (ms)")

    # Rótulos nas barras
    for bar, val in zip(bars, means):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{val:.6f}",
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
