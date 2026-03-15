# Plano Mestre de Execução Experimental do Paper

## 1. Objetivo do plano

Este documento define a estratégia de execução experimental do artigo, com o objetivo de transformar o manuscrito atual em um paper empiricamente sustentado, reprodutível e defensável.

O foco do artigo é Inteligência Artificial aplicada a problemas complexos de classificação, utilizando detecção de intrusões em redes como estudo de caso. Assim, a execução experimental deve produzir evidências suficientes para sustentar, de forma conservadora, a análise da arquitetura em dois estágios baseada em gatekeeper e especialistas.

Este plano parte do princípio de que o manuscrito já existe em versão avançada e que o snapshot atual já materializa os três blocos centrais do paper (CIC multiclasse, UNSW binário e baseline robusto). O trabalho remanescente concentra-se em consolidar governança, tabelas sintéticas e rastreabilidade final sem perder coerência com os artefatos já produzidos.

---

## 2. Meta final da campanha experimental

Ao término da execução experimental, o projeto deve possuir um pacote mínimo publicável composto por:

- resultados reproduzíveis do cenário principal;
- pelo menos um baseline comparável;
- métricas agregadas e por classe;
- matrizes de confusão em formato utilizável;
- artefatos de predição ou equivalentes;
- medidas de custo/latência, quando disponíveis;
- tabela principal do paper;
- rastreabilidade de seeds, parâmetros, scripts e ambiente.

---

## 3. Pergunta experimental do paper

A campanha experimental deve responder, de forma objetiva:

**A arquitetura em dois estágios, baseada em gatekeeper e especialistas, constitui uma estratégia plausível e empiricamente defensável de IA aplicada a problemas complexos de classificação, quando avaliada em detecção de intrusões como estudo de caso?**

Essa pergunta deve ser sustentada por:
- desempenho;
- comportamento por classe;
- análise de erro;
- custo inferencial;
- comparação com baseline;
- consistência entre cenários.

---

## 4. Escopo experimental do artigo

### 4.1 Cenário principal
- **Dataset principal:** CIC-IDS2018
- **Formulação principal:** multiclasse agregada (7 classes)
- **Arquitetura principal:** gatekeeper + especialistas

### 4.2 Cenário secundário
- **Dataset secundário:** UNSW-NB15
- **Formulação secundária:** binária
- **Função no paper:** verificação complementar de consistência externa, não eixo principal

### 4.3 Baseline obrigatório
Pelo menos um baseline monolítico comparável deve ser incluído.

No snapshot atual, o baseline oficial já suportado é o XGBoost global no recorte robusto do CIC (`scripts/baseline_xgb_cic_robust.py`).

Prioridade:
1. XGBoost global, se já houver suporte no projeto;
2. outro classificador global já existente no pipeline;
3. gatekeeper isolado, apenas se for a única comparação viável e claramente justificada.

### 4.4 Escopo excluído da rodada principal
Não faz parte do núcleo mínimo desta campanha:
- taxonomias mais granulares do que as sete classes já consolidadas no CIC;
- excesso de variações ablatórias;
- experimentos exploratórios sem ligação com o paper;
- expansão de datasets sem necessidade.

---

## 5. Princípios de execução

A execução experimental deve seguir os princípios abaixo:

### 5.1 Conservadorismo
Executar primeiro apenas o que o paper realmente precisa.

### 5.2 Reprodutibilidade
Toda execução relevante deve deixar rastros claros:
- script utilizado;
- dataset;
- parâmetros;
- seed;
- saída gerada;
- local de salvamento.

### 5.3 Comparabilidade
Baseline e arquitetura principal devem ser comparados em condições compatíveis.

### 5.4 Rastreabilidade
Todo resultado usado no paper deve apontar para artefato concreto no repositório.

No snapshot atual, `reports/README.md` deve ser usado como índice editorial para distinguir o pacote oficial do paper dos artefatos legados mantidos apenas por histórico ou apoio complementar.

### 5.5 Honestidade experimental
Se algum artefato não for gerado, isso deve ser tratado como lacuna real, não mascarado no manuscrito.

---

## 6. Fases da campanha experimental

## Fase 1 — Auditoria experimental do projeto

### Objetivo
Mapear o que já existe, o que ainda funciona e o que falta para a campanha final.

### Tarefas
- listar scripts relevantes em `scripts/`;
- identificar comandos principais de:
  - preparação de dados;
  - treinamento do gatekeeper;
  - treinamento de especialistas;
  - inferência;
  - avaliação;
  - baselines;
  - geração de plots e relatórios;
- identificar artefatos já existentes em:
  - `artifacts/`
  - `reports/`
  - `configs/`
- identificar quais resultados do manuscrito vêm de artefatos antigos;
- separar artefatos herdados de artefatos que serão regenerados para o paper.

### Entregável
Um inventário objetivo com:
- scripts úteis;
- scripts obsoletos;
- artefatos utilizáveis;
- lacunas da pipeline.

---

## Fase 2 — Congelamento do protocolo do paper

### Objetivo
Definir o protocolo oficial da campanha experimental.

### Tarefas
- definir dataset principal;
- definir dataset secundário;
- definir baseline principal;
- definir métricas oficiais;
- definir quais seeds serão usadas;
- definir quais arquivos serão considerados “fonte oficial” do paper;
- definir nomenclatura padronizada das saídas.

### Entregável
Um protocolo fixo contendo:
- cenário principal;
- cenário secundário;
- baseline;
- métricas;
- seeds;
- caminhos de saída.

---

## Fase 3 — Execução do cenário principal

### Objetivo
Rodar o pipeline principal no CIC-IDS2018 multiclasse agregado.

### Tarefas
- executar preparação dos dados;
- executar treinamento do gatekeeper;
- executar treinamento dos especialistas;
- executar inferência;
- executar avaliação;
- gerar relatórios e gráficos principais.

### Artefatos mínimos esperados
- métricas agregadas;
- métricas por classe;
- matriz de confusão absoluta;
- arquivo de predições ou equivalente;
- latência por amostra ou por estágio, se suportada;
- relatório sintético do cenário.

### Critério de conclusão da fase
O cenário principal só é considerado concluído se todos os artefatos acima existirem de forma versionável ou regenerável.

---

## Fase 4 — Execução do baseline principal

### Objetivo
Rodar o baseline monolítico comparável.

### Tarefas
- identificar o script oficial do baseline;
- garantir que o recorte experimental seja compatível com o cenário principal;
- executar treino/inferência/avaliação;
- gerar métricas equivalentes às da arquitetura principal.

### Artefatos mínimos esperados
- métricas agregadas;
- métricas por classe;
- matriz de confusão;
- latência, se suportada;
- relatório sintético de baseline.

### Critério de conclusão da fase
O baseline deve poder ser colocado lado a lado com a arquitetura principal em uma tabela única.

---

## Fase 5 — Execução do cenário secundário

### Objetivo
Rodar a arquitetura principal em UNSW-NB15 binário como validação complementar.

### Tarefas
- repetir o pipeline no recorte secundário;
- verificar se os scripts e mapeamentos existentes suportam esse cenário;
- gerar relatórios equivalentes ao cenário principal.

### Artefatos mínimos esperados
- métricas agregadas;
- métricas por classe;
- matriz de confusão;
- relatório sintético do cenário secundário.

### Observação
Se essa fase falhar por lacunas reais da pipeline, o paper pode seguir com foco principal em CIC, desde que isso seja explicitado no texto.

---

## Fase 6 — Consolidação dos resultados do paper

### Objetivo
Transformar saídas dispersas em artefatos oficiais do artigo.

### Tarefas
- consolidar tabela principal;
- consolidar tabela de baseline;
- consolidar tabela de latência;
- consolidar figuras oficiais;
- consolidar matrizes de confusão;
- consolidar notas metodológicas sobre cada execução.

### Artefatos finais esperados
- `table_main_results.csv` e/ou `.md`
- `table_baseline_comparison.csv` e/ou `.md`
- `confusion_matrix_main.png`
- `confusion_matrix_baseline.png`
- `latency_summary.csv` e/ou `.md`
- `run_manifest.md` ou equivalente

---

## Fase 7 — Consolidação de interpretabilidade

### Objetivo
Decidir se XAI entra como artefato oficial do paper.

### Tarefas
- verificar se o pipeline de XAI roda de forma estável;
- confirmar se os artefatos gerados são compreensíveis e consistentes;
- decidir se a análise de XAI entra no corpo principal ou como apoio.

### Regra de decisão
XAI só entra se:
- estiver reprodutível;
- estiver minimamente consolidada;
- acrescentar algo à interpretação da arquitetura.

Se não estiver, deve permanecer como observação secundária ou trabalho futuro.

---

## Fase 8 — Revisão do manuscrito baseada na campanha experimental

### Objetivo
Atualizar o artigo com base apenas nos resultados finais da campanha.

### Seções a revisar após a execução
- `05_experimentos.md`
- `06_resultados.md`
- `07_discussao.md`
- `08_conclusao.md`
- `01_resumo.md`

### O que revisar
- números;
- tabelas;
- afirmações comparativas;
- limitações reais;
- baselines;
- conclusões.

---

## 7. Pacote mínimo publicável

O paper só deve ser considerado minimamente pronto quando houver:

### Obrigatório
- cenário principal executado do zero;
- baseline principal executado;
- métricas oficiais consolidadas;
- matriz de confusão do cenário principal;
- tabela comparativa principal;
- descrição clara do ambiente experimental;
- rastreabilidade dos scripts e artefatos.

### Desejável
- cenário secundário consolidado;
- latência formalmente comparada;
- XAI reexecutada e consolidada;
- ablação simples de atributos ou variante da arquitetura.

---

## 8. Tabelas e figuras obrigatórias do paper

## 8.1 Tabelas
### Tabela 1 — Resultado principal
Colunas mínimas:
- método;
- dataset;
- formulação;
- recall;
- precision;
- F1;
- acurácia;
- observações.

### Tabela 2 — Custo/latência
Colunas mínimas:
- método;
- latência média;
- latência por estágio, se disponível;
- observações.

### Tabela 3 — Baseline vs arquitetura
Colunas mínimas:
- método;
- cenário;
- métricas principais;
- diferenças relevantes.

## 8.2 Figuras
### Figura 1 — Arquitetura do pipeline
- entrada;
- gatekeeper;
- roteamento;
- especialistas;
- saída final.

### Figura 2 — Matriz de confusão principal
- cenário principal.

### Figura 3 — Gráfico complementar
Pode ser:
- F1 por classe;
- comparação entre métodos;
- latência;
- figura de XAI, se aprovada.

---

## 9. Registro obrigatório por execução

Cada rodada experimental relevante deve registrar:

- nome do experimento;
- dataset;
- formulação;
- script(s) usados;
- parâmetros principais;
- seed;
- data da execução;
- duração aproximada;
- pasta de saída;
- artefatos gerados;
- status final.

Sugestão:
criar um arquivo como:
- `reports/run_manifest.md`
ou
- `reports/experiments_manifest.csv`

---

## 10. Riscos principais da campanha

### Risco 1
O manuscrito ficar mais forte do que os resultados sustentam.

### Risco 2
Rodar cenários demais e não consolidar o que importa.

### Risco 3
Ficar sem baseline comparável.

### Risco 4
Gerar métricas agregadas sem matrizes de confusão ou predições.

### Risco 5
Misturar artefatos antigos e novos sem rastreabilidade.

### Risco 6
Descobrir tardiamente que parte da pipeline não roda mais.

---

## 11. Critérios de pronto

## 11.1 Pronto para revisão científica
O projeto estará pronto para revisão científica quando:
- cenário principal estiver executado e consolidado;
- baseline estiver executado e consolidado;
- tabelas e figuras mínimas existirem;
- manuscrito estiver atualizado com base nesses resultados.

## 11.2 Pronto para submissão
O projeto estará pronto para submissão quando:
- bibliografia e citações estiverem finalizadas;
- template do venue estiver aplicado;
- tabelas e figuras estiverem em formato final;
- conclusões refletirem apenas evidências efetivas;
- todos os artefatos do paper estiverem rastreados.

---

## 12. Próximo passo operacional

O próximo passo após este plano é manter o documento derivado já existente `artigo/checklist_execucao_experimental.md` sincronizado com o snapshot real do projeto, preenchendo:

- scripts efetivamente usados;
- ordem real ou reexecutável;
- status de cada etapa;
- artefatos comprovados;
- lacunas de governança que ainda faltam fechar.

Esse checklist deve seguir sendo o documento de uso operacional no dia a dia da auditoria e de eventuais reexecuções.
