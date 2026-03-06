# data/

Esta pasta é reservada para datasets usados nos experimentos de IDS.

## Estrutura esperada

- `data/raw/unsw/` para arquivos do UNSW-NB15.
- `data/raw/cicids2018/` para arquivos do CIC-IDS2018.
- Arquivos derivados locais (ex.: `train_*.csv`, `*_eval.csv`) podem existir nesta pasta.

## Política de versionamento

- Dados brutos e arquivos grandes não devem ser versionados no Git.
- Mantenha apenas placeholders/documentação (`README.md`, `.gitkeep`) quando necessário.
- O histórico experimental deve ser representado por scripts, configs e relatórios, não por dumps de dados.
