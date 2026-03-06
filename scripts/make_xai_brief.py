from __future__ import annotations
from pathlib import Path
import argparse
import pandas as pd

TEMPLATE = """# XAI Brief — CIC (binário)

Este resumo foi gerado automaticamente a partir de `{src}`.
Ele lista as *TOP {topk}* features globais (|SHAP| médio) por classe.

## Visão rápida
- Classes: {classes}
- Arquivo de origem: `{src}`

---

{sections}
"""

SECTION = """### Classe: {cls}

| Rank | Feature | |SHAP| médio |
|-----:|---------|-------------:|
{rows}

"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in",  dest="src_csv", required=True, help="CSV consolidado do SHAP (xai_shap_consolidado.csv)")
    ap.add_argument("--out", dest="out_md", required=True, help="Arquivo .md de saída")
    ap.add_argument("--topk", type=int, default=12, help="Top-K por classe (default=12)")
    args = ap.parse_args()

    src = Path(args.src_csv)
    if not src.exists():
        raise FileNotFoundError(f"Não encontrei o consolidado: {src}")

    df = pd.read_csv(src)

    # Normaliza nomes de colunas:
    cols = {c.lower(): c for c in df.columns}
    # aceita 'class' OU 'class_key'
    class_col = cols.get("class", None) or cols.get("class_key", None)
    feat_col  = cols.get("feature", None)
    mean_col  = cols.get("mean_abs_shap", None)
    rank_col  = cols.get("rank", None)  # opcional

    if not (class_col and feat_col and mean_col):
        raise ValueError(f"CSV não possui colunas esperadas. Achei: {list(df.columns)} "
                         f"(precisa conter 'class' ou 'class_key', 'feature' e 'mean_abs_shap').")

    # agrupa por classe
    sections = []
    classes = []
    for cls, g in df.groupby(class_col):
        classes.append(str(cls))
        # Se já tem rank, usa; senão ordena por mean_abs_shap desc
        if rank_col and rank_col in g.columns:
            g_sorted = g.sort_values(rank_col, ascending=True)
        else:
            g_sorted = g.sort_values(mean_col, ascending=False)
        top = g_sorted.head(args.topk)

        rows = []
        for i, r in enumerate(top.itertuples(index=False), start=1):
            # rank preferencialmente do CSV; senão usa o enumerado
            rank_val = getattr(r, rank_col) if rank_col and hasattr(r, rank_col) else i
            feat_val = getattr(r, feat_col)
            mean_val = getattr(r, mean_col)
            rows.append(f"| {rank_val} | `{feat_val}` | {mean_val:.6f} |")

        sections.append(SECTION.format(cls=cls, rows="\n".join(rows)))

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    content = TEMPLATE.format(
        topk=args.topk,
        classes=", ".join(classes),
        src=src.as_posix(),
        sections="\n".join(sections),
    )
    out_md.write_text(content, encoding="utf-8")
    print(f"[OK] XAI Brief salvo em {out_md}")

if __name__ == "__main__":
    main()
