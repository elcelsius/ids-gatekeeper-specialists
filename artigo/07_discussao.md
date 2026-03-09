# 07 Discussion

## 7.1 Interpretação dos resultados no contexto de IDS

Os resultados disponíveis sugerem que a arquitetura em dois estágios é operacionalmente viável no recorte binário adotado, com desempenho agregado elevado no cenário CIC e desempenho também consistente, porém inferior, no cenário UNSW. Em termos de IDS, esse comportamento é compatível com a expectativa de que diferentes bases imponham níveis distintos de dificuldade de separação entre tráfego benigno e malicioso.

Sem extrapolar além dos artefatos versionados, a leitura mais prudente é que o pipeline se mostrou capaz de produzir classificações com bom nível de acerto agregado nos dois cenários avaliados, mas com sensibilidade ao contexto de dados e à configuração de execução. A presença de duas versões de métricas para o UNSW (`unsw_bin` e `unsw` legado), com variações pequenas porém observáveis, reforça essa interpretação.

## 7.2 Relevância das métricas para a análise

No domínio de detecção de intrusões, métricas agregadas como acurácia e F1-macro são úteis para visão global, mas não esgotam a avaliação de risco. A ênfase em recall e precision da classe maliciosa permanece metodologicamente central: recall baixo implica ataques não detectados; precision baixa implica aumento de alarmes indevidos.

As figuras de F1 por classe e matriz de confusão disponíveis em `reports/` contribuem para avaliar distribuição de erros além da média agregada. Contudo, como os artefatos versionados não incluem, no estado atual, tabelas estruturadas com TP, FP, TN e FN por cenário, a discussão quantitativa fina desses erros precisa ser tratada com cautela e reconhecida como limitação empírica desta etapa.

## 7.3 Papel conceitual da arquitetura em dois estágios

Do ponto de vista conceitual, os resultados são compatíveis com a hipótese metodológica de decomposição hierárquica: o gatekeeper atua como etapa inicial de triagem e os especialistas assumem a decisão final com maior granularidade. Essa organização é coerente com o objetivo de reduzir a rigidez de modelos globais únicos em cenários com heterogeneidade de padrões de ataque.

A estratégia de especialistas por classe também dialoga com o desenho de seleção por pares (modelo, conjunto de atributos), permitindo que cada classe seja tratada com configuração potencialmente distinta. Ainda que essa escolha aumente o número de componentes a gerenciar, ela oferece flexibilidade para ajustar o classificador às características de cada classe no espaço de atributos disponível.

## 7.4 Trade-offs entre detecção, custo computacional e complexidade

Os artefatos de latência indicam que o custo computacional não é uniforme entre cenários: no UNSW, o estágio especialista concentra a maior parcela do tempo de inferência, enquanto no CIC os valores reportados são substancialmente menores. Isso sugere que o custo da arquitetura em dois estágios depende do perfil do dataset e da combinação efetiva de modelos/atributos selecionada.

Em termos práticos, a arquitetura oferece uma troca explícita: maior flexibilidade e potencial de adaptação por classe em contrapartida de maior complexidade de configuração, rastreamento de artefatos e governança experimental (mapeamentos, pools de atributos, versões de execução). Assim, a avaliação da abordagem deve considerar simultaneamente desempenho, latência e custo de manutenção metodológica.

## 7.5 Comentário sobre interpretabilidade (XAI)

Os artefatos de XAI disponíveis para o CIC (`reports/cic/xai/xai_shap_consolidado.csv` e `reports/cic/XAI_BRIEF.md`) mostram que decisões dos especialistas estão associadas a atributos de tráfego identificáveis, como `dst_port`, `fwd_seg_size_min` e variáveis de temporalidade/interação de pacotes. Esse resultado fortalece o uso de interpretabilidade como apoio à auditoria técnica do modelo.

Ainda assim, a evidência de XAI deve ser tratada como complementar: importância de atributos não equivale a relação causal e não substitui avaliação preditiva por métricas de classificação. Além disso, há sinais de múltiplos snapshots de consolidação no repositório, o que demanda controle rigoroso de versão para interpretações reproduzíveis.

## 7.6 Limitações do estudo e do material experimental

A discussão dos achados é condicionada por limitações objetivas do material disponível:

- ausência, em `reports/`, de matrizes de confusão absolutas em formato estruturado (TP/FP/TN/FN) para todos os cenários;
- ausência dos arquivos `preds.csv` no versionamento (referenciados em `outputs/`, pasta não versionada);
- coexistência de resultados agregados distintos para UNSW em execuções diferentes (`unsw_bin` e `unsw` legado);
- tabela de comparação entre famílias de especialistas em `reports/cic/EXPERIMENTOS_BOOSTERS.md` ainda não preenchida;
- informações de ambiente de execução (hardware e configuração completa) não consolidadas em um único relatório padronizado.

Esses pontos não invalidam os resultados apresentados, mas restringem o nível de inferência comparativa possível nesta versão do estudo.

## 7.7 Implicações acadêmicas e técnicas

No plano acadêmico, o trabalho contribui ao documentar, de forma reprodutível e conservadora, a aplicação de uma arquitetura hierárquica de IA para IDS, articulando desempenho agregado, custo de inferência e evidências de interpretabilidade no mesmo escopo experimental.

No plano técnico, os resultados indicam que o desenho em dois estágios é promissor como estratégia de engenharia para cenários binários de detecção de intrusão, desde que acompanhado por governança de artefatos, padronização de relatórios e consolidação rigorosa de métricas por classe e por tipo de erro. Essa combinação é essencial para transformar desempenho experimental em evidência robusta para uso prático.
