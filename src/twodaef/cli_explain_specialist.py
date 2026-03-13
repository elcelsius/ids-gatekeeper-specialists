import argparse
from pathlib import Path
from loguru import logger

from twodaef.xai.shap_explain import run_xai_for_specialist

def main():
    """
    Interface CLI para gerar explicações visuais e numéricas (SHAP / LIME) para um Especialista.
    
    Explicação:
    No fluxo de Machine Learning moderno (XAI), não basta o modelo acertar. Temos que saber o PORQUÊ.
    Com este arquivo você roda na linha de comando e ele cospe os gráficos dizendo:
    "A Classe X foi escolhida por causa da variável Y e Z".
    """
    ap = argparse.ArgumentParser(description="XAI para especialista (SHAP/LIME).")
    ap.add_argument("--specialist_map", type=Path, required=True, help="artifacts/specialist_map.json")
    ap.add_argument("--class_key", type=str, required=True, help="chave da classe no mapa (ex.: '0', '1', 'DoS', 'Web')")
    ap.add_argument("--input_csv", type=Path, required=True, help="dados para explicação (ex.: UNSW_NB15_testing-set.csv)")
    ap.add_argument("--output_dir", type=Path, required=True, help="pasta onde salvar artefatos XAI")
    ap.add_argument("--fill_missing", type=float, default=0.0)
    ap.add_argument("--limit_samples", type=int, default=200)
    ap.add_argument("--top_k_global", type=int, default=10)
    ap.add_argument("--top_k_local", type=int, default=10)
    args = ap.parse_args()

    res = run_xai_for_specialist(
        specialist_map_json=str(args.specialist_map),
        class_key=args.class_key,
        input_csv=str(args.input_csv),
        output_dir=str(args.output_dir),
        fill_missing=args.fill_missing,
        limit_samples=args.limit_samples,
        top_k_global=args.top_k_global,
        top_k_local=args.top_k_local,
    )
    logger.info(f"OK — método: {res['method']} | out: {res['output_dir']}")

if __name__ == "__main__":
    main()
