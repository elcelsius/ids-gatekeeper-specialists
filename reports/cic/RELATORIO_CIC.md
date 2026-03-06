# Relatório de Avaliação – CIC-IDS2018 (2D-AEF)

**Versão:** v0.2.0-cic  
**Data:** 2025-11-19

Este relatório documenta o pipeline completo do **CIC-IDS2018 (formulação binária: `Benign` vs `Others`)** usando o framework **2D-AEF** (Gatekeeper + Especialistas por classe), incluindo:

- preparação de dados;
- treino do gatekeeper;
- treino dos especialistas por classe;
- inferência em dois estágios;
- avaliação (métricas + gráficos);
- explicabilidade (XAI via SHAP);
- consolidação de métricas entre UNSW e CIC.

Todos os caminhos e comandos são relativos à raiz do repositório `2D-AEF`.

---

## 1) Dados e partições

- Treino: `data/train_cic.csv`
- Avaliação: `data/cic_eval.csv`
- (Opcional) Inferência pura: `data/cic_infer.csv`

Os arquivos em `data/` **não são versionados** (ignorados via `.gitignore`) e devem ser gerados pelos scripts de preparação do CIC.

A coluna de rótulo utilizada em todas as etapas é:

- `label` ∈ {`Benign`, `Others`}

---

## 2) Gatekeeper CIC

### 2.1 Colunas do gatekeeper

As colunas utilizadas pelo gatekeeper estão em:

- `gatekeeper_cic_cols.txt`  *(versionado)*

Exemplo de geração (a partir do CSV de treino):

```powershell
python scripts\make_gatekeeper_cols_from_csv.py `
  --csv data\train_cic.csv `
  --out gatekeeper_cic_cols.txt
```

### 2.2 Treino do gatekeeper

O gatekeeper é um modelo leve responsável por decidir, para cada fluxo, qual especialista (ou conjunto de especialistas) será acionado.

- Modelo treinado (não versionado):  
  `artifacts/gatekeeper_cic.joblib`

Comando de treino:

```powershell
gatekeeper-train `
  --train_csv data\train_cic.csv `
  --target_col label `
  --features gatekeeper_cic_cols.txt `
  --model_out artifacts\gatekeeper_cic.joblib
```

---

## 3) Especialistas CIC

### 3.1 Pool de atributos

O pool de atributos mínimos para o CIC é mantido em:

- `artifacts/feature_pool_cic.json` *(versionado)*

Esse arquivo é gerado pelo script `make_feature_pool_min.py`, cuja assinatura atual é:

```text
usage: make_feature_pool_min.py [-h]
  --in IN_CSV
  --out OUT_JSON
  [--target TARGET_COL]
  [--max_per_set MAX_PER_SET]
```

Exemplo consistente com o experimento atual:

```powershell
python scripts\make_feature_pool_min.py `
  --in data\train_cic.csv `
  --out artifacts\feature_pool_cic.json `
  --target label `
  --max_per_set 20
```

### 3.2 Treino dos especialistas por classe

O mapeamento **classe → especialista(s)** é armazenado em:

- `artifacts/specialist_map_cic.json` *(versionado)*

Os pesos dos modelos individuais ficam em:

- diretório não versionado: `artifacts/specialists_cic/`

Treino dos especialistas (CIC binário):

```powershell
train-specialists `
  --train_csv data\train_cic.csv `
  --target_col label `
  --feature_pool_json artifacts\feature_pool_cic.json `
  --out_dir artifacts\specialists_cic `
  --map_path artifacts\specialist_map_cic.json `
  --models auto `
  --max_features_per_set 20
```

Critério: melhor **F1 por classe** (com desempate por latência e custo de atributos).

---

## 4) Inferência em dois estágios (Gatekeeper + Especialistas)

A inferência para avaliação é executada sobre `data/cic_eval.csv`, gerando um arquivo de predições consolidado:

```powershell
infer-twostage `
  --gatekeeper_model artifacts\gatekeeper_cic.joblib `
  --gatekeeper_features gatekeeper_cic_cols.txt `
  --specialist_map artifacts/specialist_map_cic.json `
  --input_csv data/cic_eval.csv `
  --output_csv outputs/eval_cic/preds.csv
```

Saída principal:

- `outputs/eval_cic/preds.csv` *(não versionado)*  
  Contém, para cada linha de `cic_eval.csv`, o rótulo previsto pelo pipeline 2D-AEF (e, opcionalmente, probabilidades/logits, dependendo da versão da CLI).

---

## 5) Avaliação e figuras (CIC)

A avaliação do CIC é feita a partir de `preds.csv` e da coluna `label`:

```powershell
plot-eval `
  --dataset_tag cic `
  --label_col label `
  --out_dir reports\cic
```

Saídas principais (todas **versionadas**):

- `reports/cic/metrics_again.json`  
  → métricas agregadas (F1 por classe, **F1-macro**, acurácia, etc.).
- `reports/cic/confusion_matrix_cic.png`  
  → matriz de confusão do 2D-AEF no CIC.
- `reports/cic/f1_per_class_cic.png`  
  → F1-score por classe (`Benign`, `Others`).

Essas figuras são as referências oficiais para o experimento CIC nas versões atuais do repositório.

---

## 6) XAI (SHAP) dos especialistas – CIC

Para interpretar o comportamento de cada especialista no CIC, é executado XAI por classe, via SHAP, sobre amostras de `data/cic_eval.csv`.

### 6.1 Geração de XAI por classe

#### Classe `Benign`

```powershell
explain-specialist `
  --specialist_map artifacts/specialist_map_cic.json `
  --class_key Benign `
  --input_csv data/cic_eval.csv `
  --output_dir outputs/xai_cic `
  --limit_samples 200 `
  --top_k_global 12 `
  --top_k_local 12
```

#### Classe `Others`

```powershell
explain-specialist `
  --specialist_map artifacts/specialist_map_cic.json `
  --class_key Others `
  --input_csv data/cic_eval.csv `
  --output_dir outputs/xai_cic `
  --limit_samples 200 `
  --top_k_global 12 `
  --top_k_local 12
```

Saída:

- `outputs/xai_cic/`  
  → subdiretórios/arquivos com explicações globais e locais para cada classe do CIC.

### 6.2 Consolidação do XAI

As explicações são agregadas em um conjunto consolidado:

```powershell
aggregate-xai `
  --xai_root outputs/xai_cic `
  --out_dir outputs/xai_cic/_consolidado
```

Saídas típicas (não versionadas):

- `outputs/xai_cic/_consolidado/xai_shap_consolidado.csv`  
- arquivos auxiliares de resumo (por exemplo, breves em `.md`).

### 6.3 Versão consolidada em `reports/cic`

Para facilitar a análise e manter um snapshot estável no repositório, os artefatos consolidado de XAI podem ser copiados ou gerados em:

- `reports/cic/xai/xai_shap_consolidado.csv`
- `reports/cic/xai/xai_shap_consolidado.md`
- `reports/cic/XAI_BRIEF.md`  → resumo das **TOP features (|SHAP| médio)** por classe

Esses arquivos sintetizam, para cada classe do CIC:

- as features mais relevantes globalmente;
- exemplos de explicações locais (se incluídos nos scripts de exportação).

---

## 7) XAI Consolidado – Exemplo de interpretação

*(Exemplo ilustrativo baseado em uma execução recente; os valores numéricos podem variar com novas rodadas de treino.)*

### 7.1 Classe `Benign` – TOP features (|SHAP| médio)

- `dst_port`
- `fwd_seg_size_min`
- `bwd_pkts_s`
- `flow_iat_min`
- `flow_iat_mean`
- `init_fwd_win_byts`
- `fwd_pkts_s`
- `init_bwd_win_byts`
- `flow_duration`
- `fwd_header_len`

### 7.2 Classe `Others` – TOP features (|SHAP| médio)

- `dst_port`
- `fwd_seg_size_min`
- `flow_iat_mean`
- `bwd_pkts_s`
- `init_fwd_win_byts`
- `fwd_pkts_s`
- `init_bwd_win_byts`
- `fwd_iat_mean`
- `fwd_act_data_pkts`
- `flow_duration`

Em termos qualitativos:

- portas de destino (`dst_port`) e tamanho mínimo de segmentos (`fwd_seg_size_min`) aparecem como atributos dominantes em ambas as classes, o que é consistente com a natureza de muitos ataques no CIC (alterações de perfil de tráfego e portas alvo);
- features ligadas a temporalidade (`flow_iat_*`, `flow_duration`) e janelas TCP (`init_*_win_byts`) capturam diferenças de padrão entre fluxos benignos e maliciosos;
- taxas de pacotes (`*_pkts_s`) ajudam a discriminar padrões de ataques de alta intensidade versus tráfego normal.

---

## 8) Comparação UNSW × CIC (métricas agregadas)

Para comparar o desempenho do 2D-AEF entre **UNSW-NB15** e **CIC-IDS2018**, utiliza-se o script:

- `scripts/aggregate_metrics.py`  *(versionado)*

Comando:

```powershell
python -m scripts.aggregate_metrics `
  --unsw reports/UNSW/metrics_again.json `
  --cic  reports/cic/metrics_again.json `
  --out_csv reports/metrics_comparados.csv `
  --out_md  reports/metrics_comparados.md
```

Saídas (versionadas):

- `reports/metrics_comparados.csv`
- `reports/metrics_comparados.md`

Esses arquivos trazem uma tabela com as métricas principais (por exemplo, `f1_macro`, `accuracy`) para **UNSW vs CIC**, e são a base para as tabelas comparativas utilizadas no artigo.

---

## 9) Resumo de reprodutibilidade (pipeline CIC)

Fluxo mínimo para reproduzir o experimento CIC a partir da raiz do repositório:

```powershell
# 1) Preparar dados (não versionados) – gerar:
#    data/train_cic.csv, data/cic_eval.csv
#    (scripts específicos de preparação não mostrados aqui)

# 2) Gatekeeper
python scripts\make_gatekeeper_cols_from_csv.py `
  --csv data\train_cic.csv `
  --out gatekeeper_cic_cols.txt

gatekeeper-train `
  --train_csv data\train_cic.csv `
  --target_col label `
  --features gatekeeper_cic_cols.txt `
  --model_out artifacts\gatekeeper_cic.joblib

# 3) Pool de features + especialistas
python scripts\make_feature_pool_min.py `
  --in data\train_cic.csv `
  --out artifacts\feature_pool_cic.json `
  --target label `
  --max_per_set 20

train-specialists `
  --train_csv data\train_cic.csv `
  --target_col label `
  --feature_pool_json artifacts\feature_pool_cic.json `
  --out_dir artifacts\specialists_cic `
  --map_path artifacts\specialist_map_cic.json `
  --models auto `
  --max_features_per_set 20

# 4) Inferência em dois estágios
infer-twostage `
  --gatekeeper_model artifacts\gatekeeper_cic.joblib `
  --gatekeeper_features gatekeeper_cic_cols.txt `
  --specialist_map artifacts/specialist_map_cic.json `
  --input_csv data/cic_eval.csv `
  --output_csv outputs/eval_cic/preds.csv

# 5) Avaliação + plots
plot-eval `
  --dataset_tag cic `
  --label_col label `
  --out_dir reports\cic

# 6) XAI por classe + consolidação
explain-specialist `
  --specialist_map artifacts/specialist_map_cic.json `
  --class_key Benign `
  --input_csv data/cic_eval.csv `
  --output_dir outputs/xai_cic `
  --limit_samples 200 `
  --top_k_global 12 `
  --top_k_local 12

explain-specialist `
  --specialist_map artifacts/specialist_map_cic.json `
  --class_key Others `
  --input_csv data/cic_eval.csv `
  --output_dir outputs/xai_cic `
  --limit_samples 200 `
  --top_k_global 12 `
  --top_k_local 12

aggregate-xai `
  --xai_root outputs/xai_cic `
  --out_dir outputs/xai_cic/_consolidado

# 7) Agregação de métricas UNSW + CIC
python -m scripts.aggregate_metrics `
  --unsw reports/UNSW/metrics_again.json `
  --cic  reports/cic/metrics_again.json `
  --out_csv reports/metrics_comparados.csv `
  --out_md  reports/metrics_comparados.md
```

Com isso, o experimento CIC do 2D-AEF fica completamente documentado e reprodutível, pronto para ser referenciado na próxima release e no artigo científico associado.
