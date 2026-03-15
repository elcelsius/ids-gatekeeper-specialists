# src/twodaef/eval/evaluate.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, List, Any, Dict

import json
import numpy as np
import pandas as pd
from loguru import logger
from sklearn.metrics import f1_score, accuracy_score, confusion_matrix, classification_report

@dataclass
class EvalConfig:
    """
    Configurações do módulo de Avaliação (Evaluation).
    Este módulo verifica o quão bom foi o modelo comparando o "Predito" (prediction)
    com a "Realidade" (ground truth).
    """
    preds_csv: str                        # Caminho para o CSV de predições gerado no passo "two_stage"
    label_col: str                        # Nome da coluna que contém a resposta verdadeira (ex: "label", "attack_cat")
    specialist_map: Optional[str] = None  # (Opcional) Mapa json com as meta-informações gerado durante o treinamento
    out_dir: Optional[str] = None         # (Opcional) Onde guardar os arquivos com os resultados visuais/relatórios

def _load_classes_from_map(path: Optional[str]) -> Optional[List[str]]:
    """Tenta extrair a lista oficial de classes originais que foram descobertas no treinamento."""
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        logger.warning(f"specialist_map não encontrado: {p}")
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        # Extrai a tag "classes" de dentro do JSON
        classes = d.get("classes")
        if isinstance(classes, list) and classes:
            return [str(x) for x in classes]
    except Exception as e:
        logger.warning(f"Falha ao ler specialist_map {p}: {e}")
    return None

def _coerce_label_types(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    classes: Optional[List[str]] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Uniformização e conversão de Tipos.
    O principal problema em avaliação de M.L. é alinhar as "Anotações Reais" com as "Predições".
    Se a Anotação Real está como ['Benign', 'Attack'] e a predição como [0, 1], o Scikit-Learn
    vai gerar um erro pois acha que são categorias distintas. Esta função sincroniza isso 
    convertendo inteligentemente números preditos para as respectivas classes (strings).
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    # Identifica formato de dados real contra o predito
    true_is_str = y_true.dtype.kind in {"U", "S", "O"}  # U/S (Unicode/String), Object
    pred_is_num = np.issubdtype(y_pred.dtype, np.number)

    # Se a realidade é Texto, e a predição for número, precisamos cruzar.
    if true_is_str and pred_is_num and classes is not None:
        max_idx = int(np.max(y_pred)) if y_pred.size else -1
        # Verifica se ocorreu predição absurda (fora do índice de conhecimento)
        if max_idx >= len(classes):
            logger.warning(
                f"Predições possuem índice ({max_idx}) fora do range de classes ({len(classes)}). "
                "Aplicando fallback para string puro."
            )
        else:
            # Substitui cada predição 'N' pela palavra mapeada no array (Ex: `classes[1]` = 'DDoS')
            mapped = []
            for v in y_pred:
                try:
                    mapped.append(classes[int(v)])
                except Exception:
                    mapped.append(str(v))
            return y_true.astype(str), np.asarray(mapped, dtype=str)

    # 'Fallback': Se der errado, forçamos os dois a serem texto simples e reza para baterem.
    return y_true.astype(str), y_pred.astype(str)

def run_eval_twostage(
    preds_csv: str,
    label_col: str,
    specialist_map: Optional[str] = None,
    out_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executa a Avaliação Final para todos os resultados provindos do CSV do Two-Stage.
    Gera relatórios, matriz de confusão e métricas em arquivos limpos.
    """
    p = Path(preds_csv)
    if not p.exists():
        raise FileNotFoundError(f"preds_csv não encontrado: {p}")

    # Carrega as tabelas predita (gerada pelo nosso pipeline)
    df = pd.read_csv(p, low_memory=False)
    if label_col not in df.columns:
        raise RuntimeError(f"Coluna de rótulo (gabrito) '{label_col}' não encontrada em {p}")

    if "pred_final" not in df.columns:
        raise RuntimeError(f"Coluna 'pred_final' gerada pelo sistema não encontrada em {p}.")

    y_true_raw = df[label_col].values
    y_pred_raw = df["pred_final"].values

    # Garante normalização de Label entre a realidade e nossa predição
    classes = _load_classes_from_map(specialist_map)
    y_true, y_pred = _coerce_label_types(y_true_raw, y_pred_raw, classes)

    # ---------- Cálculo de Métricas Matemáticas ----------
    # F1-Macro: Tira a média equilibrada entre Precisão e Recall.
    # average="macro" garante que cada classe tenha o mesmo peso. (Bom para dados desbalanceados)
    f1_macro = float(f1_score(y_true, y_pred, average="macro"))
    # Acurácia: % Geral de Acertos Absolutos (cuidado, mente para dados desbalanceados)
    acc = float(accuracy_score(y_true, y_pred))
    n = int(df.shape[0])

    logger.success(f"Avaliação concluída -> F1-macro={f1_macro:.6f} | Acc={acc:.6f} | n_samples={n}")

    # ---------- Salvamento dos Relatórios (Artefatos) ----------
    out = Path(out_dir) if out_dir else p.parent
    out.mkdir(parents=True, exist_ok=True)

    # Ordena esteticamente as labels
    labels_sorted = sorted(set(np.unique(y_true).tolist() + np.unique(y_pred).tolist()))
    
    # Matriz de Confusão: Permite ver exatamente quem errou e virou o quê (Ex: Confundiu Dos com DDoS)
    cm = confusion_matrix(y_true, y_pred, labels=labels_sorted)
    cm_df = pd.DataFrame(cm, index=[f"true_{x}" for x in labels_sorted], columns=[f"pred_{x}" for x in labels_sorted])
    cm_df.to_csv(out / "confusion_matrix_eval.csv", index=True, encoding="utf-8")

    # Relatório de Classificação (Reporte detalhado da precisão, recall, suporte e f1 por classe)
    cls_rep = classification_report(y_true, y_pred, labels=labels_sorted, zero_division=0, output_dict=True)
    pd.DataFrame(cls_rep).to_csv(out / "classification_report_eval.csv", encoding="utf-8")

    # Arquivo consolidado final (Fica salvo pra poder ser carregado por outros painéis no futuro)
    metrics = {
        "f1_macro": f1_macro,
        "accuracy": acc,
        "n_samples": n,
        "labels": labels_sorted,
        "classes_from_map": classes,
        "preds_csv": str(p),
    }
    
    (out / "metrics_eval.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    logger.success(f"Relatórios, Documentos JSON e CSV detalhados, salvos na pasta {out}")
    return metrics
