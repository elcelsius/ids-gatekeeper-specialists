"""
Smoke test rápido para validar suporte multi-classe end-to-end:
- Cria um dataset sintético com 3 classes (strings).
- Treina gatekeeper + especialistas com target_col="class".
- Roda infer-twostage e verifica que pred_final está no domínio original (strings).
"""
from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, f1_score
import joblib

from twodaef.gatekeeper import GatekeeperModel, GatekeeperConfig
from twodaef.specialists.train_specialists import TrainConfig, train_specialists
from twodaef.infer.two_stage import TwoStageConfig, TwoStageInferencer


def main() -> None:
    np.random.seed(0)
    base_dir = Path("outputs/tmp_mc")
    base_dir.mkdir(parents=True, exist_ok=True)

    # 1) Dataset sintético
    rows = []
    for i in range(90):
        if i < 30:
            cls = "Normal"
            f1, f2 = np.random.normal(0, 0.5), np.random.normal(0, 0.5)
        elif i < 60:
            cls = "Fuzzers"
            f1, f2 = np.random.normal(3, 0.5), np.random.normal(3, 0.5)
        else:
            cls = "DoS"
            f1, f2 = np.random.normal(-3, 0.5), np.random.normal(3, 0.5)
        rows.append({"f1": f1, "f2": f2, "class": cls})
    df = pd.DataFrame(rows)
    csv_path = base_dir / "toy_mc.csv"
    df.to_csv(csv_path, index=False)

    # 2) Feature pool simples
    fp_payload = {"feature_sets": {"fs1": ["f1", "f2"]}}
    fp_path = Path("artifacts/feature_pool_toy_mc.json")
    fp_path.parent.mkdir(parents=True, exist_ok=True)
    fp_path.write_text(json.dumps(fp_payload, indent=2), encoding="utf-8")

    # 3) Gatekeeper: DecisionTree simples
    gk_feats = ["f1", "f2"]
    gk_feats_path = base_dir / "gatekeeper_feats.txt"
    gk_feats_path.write_text("\n".join(gk_feats), encoding="utf-8")

    gk = GatekeeperModel(GatekeeperConfig(max_depth=4, min_samples_leaf=2))
    gk.fit(df[gk_feats], df["class"])
    gk_model_path = Path("artifacts/gatekeeper_toy_mc.joblib")
    joblib.dump(gk, gk_model_path)

    # 4) Especialistas
    spec_cfg = TrainConfig(
        train_csv=str(csv_path),
        target_col="class",
        feature_pool_json=str(fp_path),
        out_dir=str(base_dir / "specs"),
        map_path=str(base_dir / "specialist_map.json"),
        test_size=0.2,
        seed=0,
        models=["sk_rf"],  # mais rápido no toy
        max_features_per_set=None,
    )
    train_specialists(spec_cfg)

    # 5) Inferência two-stage
    out_preds = base_dir / "preds.csv"
    inf_cfg = TwoStageConfig(
        gatekeeper_model=str(gk_model_path),
        gatekeeper_features_file=str(gk_feats_path),
        specialist_map_json=str(base_dir / "specialist_map.json"),
        input_csv=str(csv_path),
        output_csv=str(out_preds),
        fill_missing=0.0,
        gatekeeper_labelmap_json=None,
    )
    TwoStageInferencer(inf_cfg).predict_csv()

    # 6) Validação rápida: pred_final no domínio original e F1 > 0 em alguma classe
    preds = pd.read_csv(out_preds)
    assert preds["class"].dtype == object, "target precisa ser string"
    assert preds["pred_final"].dtype == object, "pred_final precisa ser string"

    rep = classification_report(preds["class"], preds["pred_final"], zero_division=0, output_dict=True)
    f1_macro = f1_score(preds["class"], preds["pred_final"], average="macro")
    assert f1_macro > 0.5, f"F1 macro muito baixo: {f1_macro}"

    print("[OK] smoke multiclass")
    print("F1 macro:", f1_macro)
    print("classes:", rep.keys())
    print(preds.head())


if __name__ == "__main__":
    main()
