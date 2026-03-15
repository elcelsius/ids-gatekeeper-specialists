from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import numpy as np
from loguru import logger
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from sklearn.metrics import classification_report, confusion_matrix, f1_score, accuracy_score

# I/O helpers centralizados
from twodaef.utils.io import (
    read_csv_utf8,
    write_json_utf8,
    ensure_dir,
)


def _try_align_spaces(y_true_raw: np.ndarray, y_pred_raw: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Optional[Dict[str, str]]]:
    """
    Tenta alinhar os domínios/rótulos verdadeiros e preditos caso estejam em formatos diferentes.
    
    Explicação para estudantes:
    Na prática de Machine Learning, é muito comum que os dados originais (y_true) estejam como strings 
    (ex. "Benigno", "Malicioso"), enquanto as predições do modelo (y_pred) estejam como inteiros (0, 1).
    Isso vai gerar erro na hora de calcular métricas. Esta função tenta consertar esse desalinhamento 
    de forma automática, adivinhando a correspondência (heurística binária).
    
    Args:
        y_true_raw: O array NumPy com os rótulos corretos originais.
        y_pred_raw: O array NumPy com os rótulos que o modelo previu.
    Returns:
        Um conjunto (Tuple) contendo os índices verdadeiros corrigidos para inteiro, os índices preditos 
        corrigidos para inteiro, e caso haja tido conversão, um dicionário explicando qual string virou qual inteiro.
    """
    # Se ambos já vierem como rótulos textuais binários válidos,
    # preserva exatamente como estão (evita remapeamento indevido do UNSW).
    def _is_named_binary(a: np.ndarray) -> bool:
        vals = {str(v).strip().lower() for v in a}
        vals.discard("")
        if not vals:
            return False
        allowed = {
            "0",
            "1",
            "normal",
            "attack",
            "benign",
            "other",
            "others",
            "clean",
            "legit",
            "malicious",
            "anomaly",
            "intrusion",
        }
        has_named = any(v not in {"0", "1"} for v in vals)
        return has_named and vals.issubset(allowed)

    if _is_named_binary(y_true_raw) and _is_named_binary(y_pred_raw):
        y_true_txt = np.asarray([str(v) for v in y_true_raw], dtype=str)
        y_pred_txt = np.asarray([str(v) for v in y_pred_raw], dtype=str)
        return y_true_txt, y_pred_txt, None

    # já inteiros?
    def _to_int_safe(a):
        try:
            return a.astype(int), True
        except Exception:
            return a, False

    y_true_int, ok_true = _to_int_safe(y_true_raw)
    y_pred_int, ok_pred = _to_int_safe(y_pred_raw)

    if ok_true and ok_pred:
        return y_true_int, y_pred_int, None

    # Heurística binária
    # Função auxiliar interna que tenta converter uma string sem padrão para 0 ou 1
    def _str2bin(x: Any) -> Optional[int]:
        # Formata a string: remove espaços (strip) e deixa tudo em minúsculo (lower)
        s = str(x).strip().lower()
        if s in {"0", "1"}:
            return int(s)
            
        # Se na string contiver palavras indicando algo normal/benigno, retornamos a classe 0 (negativa)
        if any(t in s for t in ("benign", "normal", "clean", "legit")):
            return 0
            
        # Se na string contiver palavras indicando ataque/anomalia, retornamos a classe 1 (positiva)
        if any(t in s for t in ("mal", "attack", "other", "others", "anomaly", "intrusion")):
            return 1
            
        # Retorna None caso a string não caia em nenhuma heurística
        return None

    def _map_array(a: np.ndarray) -> Tuple[np.ndarray, bool]:
        # Percorremos cada valor para aplicar a transformação
        out = []
        for v in a:
            try:
                # Primeiro, tentamos simplesmente forçar a virar inteiro
                out.append(int(v))
            except Exception:
                # Se der erro (ex: não é um número e sim uma palavra), usamos nossa heurística
                b = _str2bin(v)
                if b is None:
                    # Se nossa heurística falhar, descartamos o processo completo
                    return a, False
                out.append(b)
        return np.asarray(out, dtype=int), True

    y_true_m, ok_true_m = _map_array(y_true_raw)
    y_pred_m, ok_pred_m = _map_array(y_pred_raw)

    if ok_true_m and ok_pred_m:
        tokens = {str(v).strip().lower() for v in np.concatenate((y_true_raw, y_pred_raw))}
        if any("normal" in t for t in tokens) and any("attack" in t for t in tokens):
            mapping = {"0": "Normal", "1": "Attack"}
        else:
            mapping = {"0": "Benign", "1": "Others"}
        acc = float(accuracy_score(y_true_m, y_pred_m))
        logger.info(f"Alinhamento automático aplicado (binário): {mapping} | acc={acc:.6f}")
        return y_true_m, y_pred_m, mapping

    # fallback: nada a fazer
    return y_true_raw, y_pred_raw, None


def _build_paper_confusion_cmap() -> LinearSegmentedColormap:
    """
    Paleta contínua clara para paper:
    começa em lilás suave e termina em coral claro, evitando o roxo muito escuro.
    """
    return LinearSegmentedColormap.from_list(
        "paper_confusion",
        [
            "#f6eeff",  # lilás muito claro
            "#ddd2ff",  # roxo suave
            "#cfe2ff",  # azul claro
            "#d8f3ef",  # verde-água
            "#fff3c6",  # amarelo pastel
            "#ffd9b0",  # pêssego
            "#f4a7a7",  # coral claro
        ],
        N=256,
    )


def _build_series_palette(n: int) -> list[Any]:
    base = ["#d9c5ff", "#c7dcff", "#c9efe6", "#fff0b8", "#ffd8ab", "#ffbfc0", "#d8e2ff"]
    if n <= len(base):
        return base[:n]
    cmap = _build_paper_confusion_cmap()
    return [cmap(v) for v in np.linspace(0.10, 0.95, n)]


def _relative_luminance(rgba: Tuple[float, float, float, float]) -> float:
    def _linearize(channel: float) -> float:
        if channel <= 0.03928:
            return channel / 12.92
        return ((channel + 0.055) / 1.055) ** 2.4

    r, g, b, _ = rgba
    return 0.2126 * _linearize(r) + 0.7152 * _linearize(g) + 0.0722 * _linearize(b)


def _build_display_labels(classes: list[Any], labels: list[str]) -> list[str]:
    if len(labels) != len(classes):
        return [str(c) for c in classes]
    return [str(label) for label in labels]


def plot_confusion_matrix(cm: np.ndarray, labels: list[str], out_png: Path, title: str = "Confusion Matrix") -> None:
    """
    Desenha e salva uma Matriz de Confusão em formato de imagem (PNG).
    
    Explicação para estudantes:
    A Matriz de Confusão é uma tabela que nos permite visualizar o desempenho de um algoritmo de classificação. 
    As linhas representam as classes verdadeiras (o que realmente era) e as colunas representam as 
    classes preditas (o que o modelo achou que era). 
    A diagonal principal mostra os acertos, enquanto as outras células mostram os erros.
    
    Args:
        cm: Matriz de confusão já calculada (array 2D do NumPy).
        labels: Nome das classes para colocar nos eixos X e Y.
        out_png: Caminho onde a imagem será salva.
        title: Título do gráfico.
    """
    display_labels = _build_display_labels(list(range(len(labels))), labels)
    cmap = _build_paper_confusion_cmap()
    fig_w = max(6.0, len(display_labels) * 0.9)
    fig_h = max(5.0, len(display_labels) * 0.75)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=180)
    im = ax.imshow(cm, interpolation="nearest", cmap=cmap)
    ax.set_title(title)
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_xticks(range(len(display_labels)))
    ax.set_yticks(range(len(display_labels)))
    ax.set_xticklabels(display_labels, rotation=45, ha="right")
    ax.set_yticklabels(display_labels)
    ax.set_facecolor("#fffaf7")
    ax.set_xticks(np.arange(-0.5, len(display_labels), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(display_labels), 1), minor=True)
    ax.grid(which="minor", color=(1, 1, 1, 0.85), linestyle="-", linewidth=1.0)
    ax.tick_params(which="minor", bottom=False, left=False)

    # valores por célula
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            rgba = im.cmap(im.norm(cm[i, j]))
            text_color = "#111111" if _relative_luminance(rgba) >= 0.45 else "#ffffff"
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", color=text_color, fontsize=9)

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Count")
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)


def plot_f1_per_class(y_true: np.ndarray, y_pred: np.ndarray, labels: list[str], out_png: Path, title: str = "F1 per class") -> None:
    """
    Calcula o F1-Score para cada classe individualmente e gera um gráfico de barras.
    
    Explicação para estudantes:
    O F1-Score é a média harmônica entre a Precisão (Quantos ele acertou do total que disse que era positivo?) 
    e o Recall (Quantos ele acertou do total de exemplos positivos reais?). 
    Isso é especialmente importante em dados desbalanceados (ex: mais ataques do que tráfego normal), 
    onde a Acurácia simples pode esconder que o modelo está errando muito na classe minoritária.
    
    Args:
        y_true: Array NumPy com os rótulos verdadeiros.
        y_pred: Array NumPy com as previsões do modelo.
        labels: Lista com os nomes das classes legíveis por humanos.
        out_png: Local para salvar a imagem PNG.
        title: Título do gráfico a ser plotado no topo.
    """
    # calcula f1 individual por label na ordem de `labels`
    f1s = []
    uniq = sorted(set(y_true) | set(y_pred))
    for li in uniq:
        mask_pos = (y_true == li)
        if mask_pos.sum() == 0:
            f1s.append(0.0)
        else:
            y_true_bin = (y_true == li).astype(int)
            y_pred_bin = (y_pred == li).astype(int)
            f1s.append(f1_score(y_true_bin, y_pred_bin, zero_division=0))

    display_labels = _build_display_labels(uniq, labels)
    fig_w = max(6.0, len(display_labels) * 0.95)
    fig, ax = plt.subplots(figsize=(fig_w, 4.6), dpi=180)
    bars = ax.bar(
        range(len(uniq)),
        f1s,
        color=_build_series_palette(len(uniq)),
        edgecolor="#5a5266",
        linewidth=0.8,
    )
    ax.set_xticks(range(len(uniq)))
    ax.set_xticklabels(display_labels, rotation=45, ha="right")
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("F1-score")
    ax.set_title(title)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linestyle="--", alpha=0.28)

    for bar, value in zip(bars, f1s):
        y = min(1.055, value + 0.02)
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            y,
            f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=8,
            color="#1a1a1a",
        )

    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)


def _resolve_preds_csv(preds_csv: str | None, dataset_tag: str | None) -> Path:
    """
    Tenta localizar o arquivo `preds.csv` de forma inteligente, caso o usuário não informe o caminho exato,
    procurando dentro de pastas de saída conhecidas com base na tag do dataset.
    
    Args:
        preds_csv: Caminho direto passado pelo usuário (se existir).
        dataset_tag: Sigla/nome do dataset (ex: 'unsw' ou 'cic') usado para adivinhar a pasta.
        
    Returns:
        Um objeto Path apontando para o arquivo válido de predições.
    """
    if preds_csv:
        p = Path(preds_csv)
        if not p.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {p}")
        return p

    if not dataset_tag:
        raise ValueError("Forneça --preds_csv ou --dataset_tag.")

    tag = dataset_tag.strip().lower()
    candidates = [
        Path("outputs") / f"eval_{tag}" / "preds.csv",
        Path("reports") / tag / "preds.csv",
        Path("reports") / tag.upper() / "preds.csv",
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError(
        f"Não encontrei preds.csv para dataset_tag='{dataset_tag}'. "
        f"Tente passar --preds_csv explicitamente."
    )


def make_eval_plots(
    preds_csv: str | None,
    label_col: str,
    out_dir: str,
    dataset_tag: str | None = None,
    class_labels: list[str] | None = None,
    min_rows: int | None = None,
    allow_small_eval: bool = False,
) -> Dict[str, Any]:
    """
    Função principal/orquestradora que vai ler o arquivo de previsões (preds.csv), 
    calcular métricas oficiais (acurácia e f1 score macro) e também desenhar os gráficos 
    (matriz de confusão e barras de F1).
    
    Ela inclui defesas contra execuções acidentais em subconjuntos (ex, se tiver poucas linhas),
    o que poderia gerar métricas superestimadas ou incorretas de forma ilusória.
    
    Args:
        preds_csv: Caminho para o CSV contendo as predições.
        label_col: Nome da coluna que possui os dados reais corretos (y_true).
        out_dir: Diretório onde serão gravados os resultados (pngs, métricas.json).
        dataset_tag: Identificador do dataset (ex 'cic' ou 'unsw').
        class_labels: Rótulos customizados para eixos X e Y.
        min_rows: Limiar de segurança de quantidade mínima de linhas nas amostras.
        allow_small_eval: Força a execução msm se não atingir min_rows.
        
    Returns:
        Dicionário Payload com as métricas recomputadas para fácil log e armazenamento posterior.
    """
    preds_csv_p = _resolve_preds_csv(preds_csv, dataset_tag)
    outp = Path(out_dir)
    ensure_dir(outp)

    df = read_csv_utf8(preds_csv_p)
    if label_col not in df.columns:
        raise KeyError(f"Coluna '{label_col}' não está presente em {preds_csv_p}")

    # colunas obrigatórias
    if "pred_final" not in df.columns:
        raise KeyError(f"Coluna 'pred_final' não está presente em {preds_csv_p}")

    # sanity-check: evitar eval acidental com subconjunto minúsculo
    n_rows = int(df.shape[0])
    min_expected = min_rows
    if min_expected is None and dataset_tag:
        tag = dataset_tag.lower()
        if tag == "unsw":
            min_expected = 10_000
    if min_expected and n_rows < min_expected:
        msg = (
            f"preds.csv tem apenas {n_rows} linhas (<{min_expected}). "
            "Verifique se você está apontando para o arquivo completo de inferência."
        )
        if allow_small_eval:
            logger.warning(msg + " Prosseguindo por allow_small_eval=True.")
        else:
            raise ValueError(msg)

    y_true_raw = df[label_col].values
    y_pred_raw = df["pred_final"].values

    # alinhar espaços/formatos
    y_true, y_pred, mapping = _try_align_spaces(y_true_raw, y_pred_raw)

    # Labels (legendas) para o gráfico
    uniq = sorted(set(y_true) | set(y_pred))
    uniq_lc = {str(u).strip().lower() for u in uniq}
    if uniq_lc == {"normal", "attack"}:
        uniq = sorted(uniq, key=lambda u: 0 if str(u).strip().lower() == "normal" else 1)
    elif uniq_lc == {"benign", "others"}:
        uniq = sorted(uniq, key=lambda u: 0 if str(u).strip().lower() == "benign" else 1)

    if class_labels is not None:
        if len(class_labels) != len(uniq):
            logger.warning(
                f"class_labels tem {len(class_labels)} itens, mas encontrei {len(uniq)} classes; "
                "vou usar os rótulos detectados automaticamente."
            )
            labels = [str(u) for u in uniq]
        else:
            labels = class_labels
    else:
        if mapping:  # binário com rótulos amigáveis
            labels = [mapping.get("0", "0"), mapping.get("1", "1")]
        else:
            labels = [str(u) for u in uniq]

    # Métricas
    cm = confusion_matrix(y_true, y_pred, labels=uniq)
    f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    acc = float(accuracy_score(y_true, y_pred))

    # Sufixo de arquivo por dataset
    suffix = f"_{dataset_tag.lower()}" if dataset_tag else ""
    cm_png = outp / f"confusion_matrix{suffix}.png"
    f1_png = outp / f"f1_per_class{suffix}.png"

    # Plots
    plot_confusion_matrix(cm, labels, cm_png, title=f"Confusion Matrix (GKS{suffix})")
    plot_f1_per_class(y_true, y_pred, labels, f1_png, title=f"F1 per class (GKS{suffix})")

    # Salva métricas recomputadas
    payload = {
        "f1_macro": f1_macro,
        "accuracy": acc,
        "n": int(df.shape[0]),
        "labels": labels,
        "preds_csv": preds_csv_p.as_posix(),
        "out_dir": outp.as_posix(),
        "dataset_tag": dataset_tag or "",
    }
    write_json_utf8(payload, outp / "metrics_again.json")

    logger.success(f"Plots salvos em {outp} ({cm_png.name}, {f1_png.name})")
    logger.info(f"F1-macro={f1_macro:.6f} | Acc={acc:.6f} | n={df.shape[0]}")
    return payload
