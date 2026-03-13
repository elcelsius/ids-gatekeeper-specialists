import argparse
from pathlib import Path
from loguru import logger

from twodaef.reports.aggregate_xai import aggregate_xai

def main():
    """
    Interface CLI auxiliar/genérica para formatar o relatório consolidado de Interpretabilidade (XAI).
    
    Explicação:
    Esse script funciona como um atalho limpo para transformar dados densos de processamento em tabelas.
    Produz instantaneamente a sua saída em CSV (para carregar no excel) e em formato Markdown.
    """
    ap = argparse.ArgumentParser(description="Agrega XAI (SHAP) em CSV + Markdown.")
    ap.add_argument("--base_dir", type=Path, required=True, help="Pasta base com class_* (ex.: outputs/xai_unsw)")
    ap.add_argument("--out_dir", type=Path, required=True, help="Pasta de saída para os artefatos consolidados")
    ap.add_argument("--top_k", type=int, default=10, help="Top-K features por classe")
    args = ap.parse_args()

    res = aggregate_xai(str(args.base_dir), str(args.out_dir), top_k=args.top_k)
    logger.info(f"OK — CSV: {res['csv']} | MD: {res['md']}")

if __name__ == "__main__":
    main()
