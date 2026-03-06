# artigo-ia

Repositório derivado do framework principal **2D-AEF** para um segundo artigo acadêmico da disciplina de Inteligência Artificial.

## Propósito

Este projeto separa de forma explícita duas camadas:

1. **Camada experimental/técnica**: pipeline IDS/ML (gatekeeper, especialistas, inferência em dois estágios, avaliação e XAI).
2. **Camada acadêmica/editorial**: materiais de escrita, planejamento e organização do artigo.

O foco técnico permanece em **IA aplicada à detecção de intrusões (IDS)**, com ênfase em reprodutibilidade experimental e documentação para publicação.

## Origem do Projeto

- Baseado no framework principal `2D-AEF`.
- Este repositório tem identidade própria para a disciplina de IA.
- A lógica do código-fonte em `src/twodaef/` foi preservada nesta reorganização.

## Estrutura Atual

```text
artigo-ia/
├── article/                    # escrita do artigo (seções e rascunho consolidado)
├── artifacts/
│   ├── feature_pools/          # pools de features gerados
│   ├── trained_models/         # modelos treinados e diretórios de especialistas
│   └── README.md
├── configs/
│   ├── cols/                   # listas de colunas para gatekeeper
│   └── mappings/               # mapeamentos JSON (specialist_map, gk_labelmap)
├── data/
│   └── README.md               # datasets esperados e política de versionamento
├── docs/                       # escopo e plano experimental + docs técnicas
├── references/
│   ├── papers/                 # artigos científicos base
│   ├── inherited_material/     # materiais herdados do projeto principal
│   └── references.bib
├── reports/                    # relatórios e métricas por dataset
├── scripts/                    # automações e utilitários experimentais
├── src/twodaef/                # código-fonte da pipeline
├── pyproject.toml
└── requirements.txt
```

## Convenções de Caminho (reorganizadas)

- Colunas de gatekeeper: `configs/cols/*.txt`
- Mapeamentos: `configs/mappings/*.json`
- Feature pools: `artifacts/feature_pools/*.json`
- Modelos treinados: `artifacts/trained_models/`
- Relatórios UNSW binário: `reports/unsw_bin/`

## Execução (exemplo de argumentos)

Os comandos CLI continuam os mesmos; atualize apenas os caminhos dos arquivos:

```powershell
gatekeeper-train \
  --train_csv data\raw\unsw\UNSW_NB15_training-set.csv \
  --target_col label \
  --features configs\cols\gatekeeper_unsw_cols.txt \
  --model_out artifacts\trained_models\gatekeeper_unsw.joblib

train-specialists \
  --train_csv data\raw\unsw\UNSW_NB15_training-set.csv \
  --target_col label \
  --feature_pool_json artifacts\feature_pools\feature_pool_unsw.json \
  --out_dir artifacts\trained_models\specialists_unsw_bin \
  --map_path configs\mappings\specialist_map_unsw_bin.json

infer-twostage \
  --gatekeeper_model artifacts\trained_models\gatekeeper_unsw.joblib \
  --gatekeeper_features configs\cols\gatekeeper_unsw_cols.txt \
  --specialist_map configs\mappings\specialist_map_unsw_bin.json \
  --input_csv data\raw\unsw\UNSW_NB15_testing-set.csv \
  --output_csv outputs\unsw_bin\preds.csv
```

## Observações

- Não versionar dados brutos e binários pesados.
- Não inventar resultados: `article/` e `docs/` usam placeholders estruturados.
- Compatível com `pyproject.toml` e `requirements.txt` atuais.
