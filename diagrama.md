## Visão geral do fluxo 2D-AEF (CIC/UNSW)

```mermaid
flowchart LR
    A["Dados brutos (CSV)"] --> B["Preparação/robustez\nlimpeza + remoção de colunas sensíveis"]
    B --> C["Feature pool\nscripts/make_feature_pool_*"]
    B --> D["Gatekeeper\nárvore podada\npred_gatekeeper"]

    C --> E["Treino de especialistas\num por classe\nsalva specialist_map"]
    D --> F["Inferência 2 estágios\nEtapa1: gatekeeper\nEtapa2: especialista\npreds.csv + latências"]
    E --> F

    F --> G["Avaliação e relatórios\nmétricas, plots, XAI/SHAP\nablação e baseline XGBoost"]
    G --> H["Figuras e artigos\nfigs/*.png para o paper\nREADME/scripts de plot"]
```

Notas:
- Pipeline reprodutível via scripts CLI (prep, train, eval, plot, XAI).
- Resultados em `outputs/` e `figs/`; mapas/modelos em `artifacts/`.
- Baselines (ex.: XGBoost global) servem de comparação com o 2D-AEF.
