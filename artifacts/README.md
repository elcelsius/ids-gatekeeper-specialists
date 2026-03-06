# artifacts/

Artefatos gerados em execução de treino e inferência.

## Organização

- `feature_pools/`: arquivos `feature_pool_*.json`.
- `trained_models/`: modelos `.joblib` e diretórios de especialistas.
- Mapeamentos JSON foram realocados para `configs/mappings/`.

## Observações

- Binários de modelo são temporários do experimento e não devem ser versionados.
- Preserve somente artefatos essenciais para reprodutibilidade documental.
