# Paper Experimental Plan – 2D-AEF IDS

## Objetivo
Transformar o artigo atual (survey) em artigo experimental reprodutível, respondendo:
- matrizes de confusão absolutas (TP, FP, TN, FN)
- ênfase em recall (classe ataque)
- custo computacional (treino + inferência)
- (opcional) UNSW binário como cenário principal

## Artefatos obrigatórios
- reports/<dataset>/preds.csv (y_true, y_pred, latências)
- reports/<dataset>/metrics.json (acc, precision, recall, f1, etc.)
- reports/<dataset>/confusion_matrix.json (TP, FP, TN, FN)
- reports/metrics_comparados.(md|csv) consolidado

## Experimentos (mínimo publicável)
### Dataset 1: CIC (binário: Benign vs Attack/Others)
- [ ] Treinar gatekeeper
- [ ] Treinar especialistas (se aplicável)
- [ ] Gerar preds.csv com latências
- [ ] Gerar matriz de confusão absoluta + métricas

### Dataset 2: UNSW-NB15 (binário: Normal vs Attack)
- [ ] Preparar binarização
- [ ] Repetir pipeline
- [ ] Gerar preds.csv + matriz + métricas

## Seção de Resultados (formato)
- Tabela única por dataset com:
  Modelo | Acc | Precision | Recall(Ataque) | F1 | Treino(s) | Inferência(ms/amostra)
- Apêndice: matrizes TP/FP/TN/FN (por dataset)

## Entregável ao orientador
- docx atualizado
- tabela única consolidada
- matrizes absolutas
- parágrafo de justificativa: recall > precision em IDS
- parágrafo custo computacional (trade-off ensemble)