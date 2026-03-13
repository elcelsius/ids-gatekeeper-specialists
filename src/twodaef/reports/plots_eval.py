from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import numpy as np
from loguru import logger
import matplotlib.pyplot as plt
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
        mapping = {"0": "Benign", "1": "Others"}
        acc = float(accuracy_score(y_true_m, y_pred_m))
        logger.info(f"Alinhamento automático aplicado (binário): {mapping} | acc={acc:.6f}")
        return y_true_m, y_pred_m, mapping

    # fallback: nada a fazer
    return y_true_raw, y_pred_raw, None


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
    fig, ax = plt.subplots(figsize=(6, 5), dpi=150)
    im = ax.imshow(cm, interpolation="nearest")
    ax.set_title(title)
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)

    # valores por célula
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center")

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
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
            f1s.append(f1_score(y_true_bin, y_pred_bin))

    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
    ax.bar(range(len(uniq)), f1s)
    ax.set_xticks(range(len(uniq)))
    # mostrar rótulos amigáveis
    try:
        xticks = [labels[li] if li < len(labels) else str(li) for li in uniq]
    except Exception:
        xticks = [str(li) for li in uniq]
    ax.set_xticklabels(xticks, rotation=45, ha="right")
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("F1-score")
    ax.set_title(title)
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
    if class_labels is not None:
        labels = class_labels
    else:
        if mapping:  # binário com rótulos amigáveis
            labels = ["Benign", "Others"]
        else:
            labels = [str(u) for u in uniq]

    # Métricas
    cm = confusion_matrix(y_true, y_pred, labels=uniq)
    f1_macro = float(f1_score(y_true, y_pred, average="macro"))
    acc = float(accuracy_score(y_true, y_pred))

    # Sufixo de arquivo por dataset
    suffix = f"_{dataset_tag.lower()}" if dataset_tag else ""
    cm_png = outp / f"confusion_matrix{suffix}.png"
    f1_png = outp / f"f1_per_class{suffix}.png"

    # Plots
    plot_confusion_matrix(cm, labels, cm_png, title=f"Confusion Matrix (2D-AEF{suffix})")
    plot_f1_per_class(y_true, y_pred, labels, f1_png, title=f"F1 per class (2D-AEF{suffix})")

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
