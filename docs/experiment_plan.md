# Experiment Plan

## Meta

Executar e documentar experimentos de IDS para alimentar o artigo acadêmico com resultados reproduzíveis.

## Etapas

1. Validar datasets e partições em `data/`.
2. Treinar gatekeeper com colunas de `configs/cols/`.
3. Gerar feature pools em `artifacts/feature_pools/`.
4. Treinar especialistas em `artifacts/trained_models/`.
5. Salvar/atualizar mapas em `configs/mappings/`.
6. Rodar inferência e avaliação, consolidando evidências em `reports/`.
7. Transferir resultados validados para `artigo/06_resultados.md` e discussão.

## Critérios de registro

- Identificar dataset, seed, versão de código e timestamp.
- Salvar caminhos de entrada/saída usados em cada experimento.
- Não registrar conclusões sem evidência em artefatos produzidos.
