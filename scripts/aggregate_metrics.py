"""
aggregate_metrics.py

Lê arquivos metrics_again.json (UNSW, CIC, etc.) e gera:
- Uma tabela CSV comparando as métricas entre datasets
- (Opcional) um resumo em Markdown para o artigo

Uso sugerido (a partir da raiz do projeto):

    python -m scripts.aggregate_metrics \
        --unsw reports/unsw_bin/metrics_again.json \
        --cic reports/cic/metrics_again.json \
        --out_csv reports/metrics_comparados.csv \
        --out_md  reports/metrics_comparados.md
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any


def flatten_dict(d: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """
    Achata dicionários aninhados usando chaves com ponto.
    Ex.: {"per_class": {"Benign": {"f1": 0.99}}}
    -> {"per_class.Benign.f1": 0.99}
    """
    items: Dict[str, Any] = {}
    for k, v in d.items():
        new_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key))
        else:
            items[new_key] = v
    return items


def load_metrics(label: str, path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    flat = flatten_dict(data)
    # adiciona o nome do dataset na linha
    flat["dataset"] = label
    return flat


def to_csv(rows: Dict[str, Dict[str, Any]], out_csv: Path) -> None:
    """
    rows: mapeia dataset -> dict(flattened metrics)
    """
    # coletar todas as chaves existentes
    all_keys = set()
    for row in rows.values():
        all_keys.update(row.keys())

    # garantir ordem: dataset primeiro, depois resto
    all_keys = ["dataset"] + sorted(k for k in all_keys if k != "dataset")

    lines = []
    # header
    lines.append(",".join(all_keys))

    # linhas
    for dataset, row in rows.items():
        values = []
        for k in all_keys:
            v = row.get(k, "")
            if isinstance(v, float):
                # formata bonito, mas sem perder informação
                v = f"{v:.6f}"
            values.append(str(v))
        lines.append(",".join(values))

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_csv.write_text("\n".join(lines), encoding="utf-8")


def to_markdown(rows: Dict[str, Dict[str, Any]], out_md: Path) -> None:
    """
    Gera um resumo simples em Markdown com algumas métricas chave,
    se existirem (nomes genéricos justamente para não depender
    de um schema específico).
    """
    # tentar pegar algumas métricas comuns
    candidates = [
        "f1_macro",
        "f1_micro",
        "accuracy",
        "balanced_accuracy",
        "roc_auc",
    ]

    # descobrir quais realmente existem
    first = next(iter(rows.values()))
    present = [m for m in candidates if m in first]

    lines = []
    lines.append("# Comparação de métricas entre datasets\n")

    if not present:
        lines.append("_Nenhuma das métricas padrão (f1_macro, accuracy, etc.) foi encontrada; veja o CSV para detalhes completos._\n")
    else:
        # tabela
        header = "| Dataset | " + " | ".join(present) + " |"
        sep = "|--------|" + "|".join(["-----------"] * len(present)) + "|"
        lines.append(header)
        lines.append(sep)

        for dataset, row in rows.items():
            vals = []
            for m in present:
                v = row.get(m, "")
                if isinstance(v, float):
                    v = f"{v:.4f}"
                vals.append(str(v))
            lines.append(f"| {dataset} | " + " | ".join(vals) + " |")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Agrega metrics_again.json de múltiplos datasets.")
    parser.add_argument("--unsw", type=str, help="Caminho para metrics_again.json do UNSW")
    parser.add_argument("--cic", type=str, help="Caminho para metrics_again.json do CIC")
    parser.add_argument("--out_csv", type=str, default="reports/metrics_comparados.csv")
    parser.add_argument("--out_md", type=str, default="reports/metrics_comparados.md")

    args = parser.parse_args()

    rows: Dict[str, Dict[str, Any]] = {}

    if args.unsw:
        rows["UNSW-NB15"] = load_metrics("UNSW-NB15", Path(args.unsw))

    if args.cic:
        rows["CIC-IDS2018"] = load_metrics("CIC-IDS2018", Path(args.cic))

    if not rows:
        raise SystemExit("Nenhum dataset informado (use --unsw e/ou --cic).")

    out_csv = Path(args.out_csv)
    out_md = Path(args.out_md)

    to_csv(rows, out_csv)
    to_markdown(rows, out_md)

    print(f"[OK] CSV gerado em: {out_csv}")
    print(f"[OK] Markdown gerado em: {out_md}")


if __name__ == "__main__":
    main()
