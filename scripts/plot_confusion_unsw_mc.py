"""
Gera a matriz de confusão multi-classe (attack_cat) do UNSW-NB15 usando os resultados do 2D-AEF.
Leitura: outputs/unsw_mc/confusion_matrix_unsw_mc.csv (sem cabeçalho).
Saída: figs/fig2_unsw_confusion_matrix.png
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


CONF_PATH = Path("outputs/unsw_mc/confusion_matrix_unsw_mc.csv")
FIG_DIR = Path("figs")
FIG_PATH = FIG_DIR / "fig2_unsw_confusion_matrix.png"

CLASS_LABELS = [
    "Analysis",
    "Backdoor",
    "DoS",
    "Exploits",
    "Fuzzers",
    "Generic",
    "Normal",
    "Reconnaissance",
    "Shellcode",
    "Worms",
]


def plot_confusion_matrix(cm: np.ndarray, labels: list[str], out_png: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
    ax.set_title("Matriz de confusão – UNSW-NB15 (attack_cat, 2D-AEF)")
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)

    # Anotação de valores por célula
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=7)

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png)
    plt.close(fig)


def main() -> None:
    if not CONF_PATH.exists():
        raise FileNotFoundError(f"Arquivo de matriz de confusão não encontrado: {CONF_PATH}")

    # CSV salvo via confusion_matrix(...).to_csv(index=False), portanto sem cabeçalho
    df_cm = pd.read_csv(CONF_PATH, header=None)
    cm = df_cm.values

    if cm.shape != (len(CLASS_LABELS), len(CLASS_LABELS)):
        raise ValueError(f"Shape inesperado da matriz: {cm.shape}, esperado {(len(CLASS_LABELS), len(CLASS_LABELS))}")

    plot_confusion_matrix(cm, CLASS_LABELS, FIG_PATH)
    print(f"[OK] Figura salva em {FIG_PATH}")


if __name__ == "__main__":
    main()
