from __future__ import annotations
from pathlib import Path
import argparse
import sys
import json
from loguru import logger

# Mantemos a rota antiga: se o módulo de treino real existir, chamamos; caso contrário avisamos.
try:
    # compat com seu layout atual
    from twodaef.specialists.train_specialists import TrainConfig, train_specialists  # type: ignore
except Exception:
    TrainConfig = None  # type: ignore
    train_specialists = None  # type: ignore

_DEF_AUTO_MODELS = ["lgbm", "xgb", "cat"]  # foco sugerido

def _parse_models_arg(models_arg: str | None) -> list[str] | None:
    if not models_arg or models_arg.strip().lower() == "auto":
        return _DEF_AUTO_MODELS
    items = [m.strip().lower() for m in models_arg.split(",") if m.strip()]
    # dedup preservando ordem
    seen, out = set(), []
    for m in items:
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out or _DEF_AUTO_MODELS

def _load_feature_pool(fp: Path) -> dict:
    if not fp.exists():
        raise FileNotFoundError(f"feature_pool_json não encontrado: {fp}")
    try:
        data = json.loads(fp.read_text(encoding="utf-8"))
    except Exception as e:
        raise RuntimeError(f"Falha ao ler JSON de {fp}: {e}") from e
    if "feature_sets" not in data or not isinstance(data["feature_sets"], dict):
        raise ValueError(f"{fp} não contém a chave 'feature_sets' (dict).")
    return data

def main() -> None:
    """
    Interface CLI para acionar a criação e treinamento completo da Matriz de Especialistas (2D-AEF).
    
    Explicação:
    Treinar os especialistas é o coração analítico do projeto! Eles são modelos parrudos 
    (como XGBoost e LightGBM) que olham com zoom os pacotes encaminhados pelo Gatekeeper.
    Este arquivo possibilita automatizar o treino em lote, garantindo que usemos as sub-listas de attributes
    do "feature_pool" para manter a diversidade do sistema.
    """
    ap = argparse.ArgumentParser(description="Treinar Matriz de Especialistas (2D-AEF).")
    ap.add_argument("--train_csv", type=Path, required=True)
    ap.add_argument("--target_col", type=str, required=True)
    ap.add_argument("--feature_pool_json", type=Path, required=True)
    ap.add_argument("--out_dir", type=Path, default=Path("artifacts/specialists"))
    ap.add_argument("--map_path", type=Path, default=Path("artifacts/specialist_map.json"))
    ap.add_argument("--test_size", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--models", type=str, default="auto",
                    help="auto ou lista separada por vírgula (ex: lgbm,xgb,cat,sk_hgb,sk_rf)")
    ap.add_argument("--max_features_per_set", type=int, default=None)
    ap.add_argument("--dry_run", action="store_true",
                    help="apenas validar e exibir o plano (não treina nada)")
    args = ap.parse_args()

    # Normalização dos argumentos
    models = _parse_models_arg(args.models)

    logger.info("== 2D-AEF :: specialists ==")
    logger.info(f"train_csv        : {args.train_csv}")
    logger.info(f"target_col       : {args.target_col}")
    logger.info(f"feature_pool_json: {args.feature_pool_json}")
    logger.info(f"out_dir          : {args.out_dir}")
    logger.info(f"map_path         : {args.map_path}")
    logger.info(f"test_size        : {args.test_size}")
    logger.info(f"seed             : {args.seed}")
    logger.info(f"models           : {models}")
    logger.info(f"max_feats_per_set: {args.max_features_per_set}")
    logger.info(f"dry_run          : {args.dry_run}")

    # Valida feature pool e mostra plano
    fp_data = _load_feature_pool(args.feature_pool_json)
    feature_sets: dict[str, list[str]] = fp_data["feature_sets"]

    logger.info("Plano dos conjuntos de features:")
    for set_name, cols in feature_sets.items():
        n = len(cols) if isinstance(cols, list) else 0
        logger.info(f" - {set_name}: {n} feats")

    if args.dry_run:
        # Apenas relata o que seria feito e sai com sucesso
        logger.success("Dry-run OK — nenhum modelo foi treinado.")
        sys.exit(0)

    # Execução real (usa seu pipeline atual baseado em TrainConfig/train_specialists)
    if TrainConfig is None or train_specialists is None:
        logger.error("Módulo de treino real não encontrado: twodaef.specialists.train_specialists")
        sys.exit(2)

    cfg = TrainConfig(
        train_csv=str(args.train_csv),
        target_col=args.target_col,
        feature_pool_json=str(args.feature_pool_json),
        out_dir=str(args.out_dir),
        map_path=str(args.map_path),
        test_size=args.test_size,
        seed=args.seed,
        models=None if args.models == "auto" else models,
        max_features_per_set=args.max_features_per_set
    )
    res = train_specialists(cfg)
    logger.info(f"Resumo: {res.get('specialists', {})}")
    logger.success("Treino de especialistas concluído.")

if __name__ == "__main__":
    main()
