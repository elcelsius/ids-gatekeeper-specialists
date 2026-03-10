# Checklist Operacional de Execução Experimental do Paper

## 1. Objetivo

Este checklist operacional tem como finalidade acompanhar a execução real da campanha experimental do artigo, garantindo que os cenários principais, os baselines e os artefatos necessários ao paper sejam executados, rastreados e consolidados de forma reprodutível.

Este documento deriva do Plano Mestre de Execução Experimental e deve ser atualizado conforme cada etapa for sendo concluída.

---

## 2. Regras de uso

Antes de marcar qualquer etapa como concluída, verificar:

- se o script realmente executou sem erro crítico;
- se os artefatos esperados foram gerados;
- se os arquivos de saída ficaram salvos em local padronizado;
- se os resultados podem ser rastreados depois;
- se os relatórios estão coerentes com o cenário executado.

Cada etapa deve registrar:
- data;
- status;
- observações;
- caminhos dos artefatos gerados.

### Legenda de status
- `[ ]` não iniciado
- `[~]` em andamento
- `[x]` concluído
- `[!]` concluído com ressalvas
- `[falha]` falhou / precisa correção

---

## 3. Preparação do ambiente

### 3.1 Verificação inicial do repositório
- [ ] Confirmar que o projeto está na versão correta do paper
- [ ] Confirmar que `src/`, `scripts/`, `artifacts/`, `configs/`, `reports/` e `references/` estão presentes
- [ ] Confirmar que a estrutura do artigo está atualizada
- [ ] Confirmar que a bibliografia mínima já está criada
- [ ] Confirmar que os artefatos antigos e novos estão claramente separados

**Data:**  
**Status:**  
**Observações:**

### 3.2 Ambiente Python
- [ ] Criar/ativar ambiente virtual
- [ ] Instalar dependências a partir de `requirements.txt` ou `pyproject.toml`
- [ ] Confirmar versões principais das bibliotecas
- [ ] Registrar versão do Python
- [ ] Registrar sistema operacional e hardware usado

**Data:**  
**Status:**  
**Observações:**

### 3.3 Sanidade da pipeline
- [ ] Identificar os scripts realmente utilizados no paper
- [ ] Verificar se os caminhos para datasets estão válidos
- [ ] Verificar se os arquivos de configuração existem
- [ ] Verificar se os mapeamentos JSON e feature pools estão íntegros
- [ ] Executar um teste rápido de sanidade, se houver script smoke

**Data:**  
**Status:**  
**Observações:**

---

## 4. Auditoria experimental do projeto

### 4.1 Levantamento dos scripts
Preencher a tabela abaixo:

| Etapa | Script | Confirmado? | Observações |
|---|---|---:|---|
| Preparação CIC binário |  |  |  |
| Preparação UNSW binário |  |  |  |
| Treino gatekeeper |  |  |  |
| Treino especialistas |  |  |  |
| Inferência two-stage |  |  |  |
| Avaliação |  |  |  |
| Geração de matriz de confusão |  |  |  |
| Geração de F1 por classe |  |  |  |
| Baseline principal |  |  |  |
| Latência/custo |  |  |  |
| XAI |  |  |  |

### 4.2 Levantamento dos artefatos atuais
- [ ] Identificar quais artefatos em `reports/` são herdados
- [ ] Identificar quais artefatos serão regenerados
- [ ] Identificar quais artefatos não podem ser usados como evidência principal
- [ ] Listar lacunas experimentais atuais

**Artefatos herdados relevantes:**  
**Artefatos que precisam ser regenerados:**  
**Lacunas identificadas:**

---

## 5. Protocolo oficial do paper

### 5.1 Cenário principal
- [ ] Dataset principal definido
- [ ] Formulação principal definida
- [ ] Script de preparação identificado
- [ ] Script de treino identificado
- [ ] Script de inferência identificado
- [ ] Script de avaliação identificado

**Dataset:** CIC-IDS2018  
**Formulação:** Binária  
**Arquitetura:** Gatekeeper + especialistas  
**Status:**  

### 5.2 Cenário secundário
- [ ] Dataset secundário definido
- [ ] Formulação secundária definida
- [ ] Scripts correspondentes identificados

**Dataset:** UNSW-NB15  
**Formulação:** Binária  
**Status:**  

### 5.3 Baseline principal
- [ ] Baseline escolhido
- [ ] Script identificado
- [ ] Compatibilidade com cenário principal verificada

**Baseline escolhido:**  
**Status:**  

### 5.4 Métricas oficiais
- [ ] Recall
- [ ] Precision
- [ ] F1-score
- [ ] Acurácia
- [ ] Matriz de confusão absoluta
- [ ] Latência/custo, se suportado
- [ ] Predições ou artefato equivalente

**Status:**  

---

## 6. Execução do cenário principal — CIC binário

### 6.1 Preparação dos dados
- [ ] Identificar script oficial de preparação CIC
- [ ] Executar preparação
- [ ] Confirmar geração dos dados necessários
- [ ] Registrar caminhos de entrada e saída

**Comando usado:**  
**Saídas geradas:**  
**Status:**  
**Observações:**

### 6.2 Treinamento do gatekeeper
- [ ] Identificar comando de treino
- [ ] Executar treino
- [ ] Confirmar modelo salvo
- [ ] Confirmar log ou relatório correspondente

**Comando usado:**  
**Artefato gerado:**  
**Status:**  
**Observações:**

### 6.3 Treinamento dos especialistas
- [ ] Identificar comando de treino dos especialistas
- [ ] Executar treino
- [ ] Confirmar modelos salvos
- [ ] Confirmar mapeamentos coerentes

**Comando usado:**  
**Artefatos gerados:**  
**Status:**  
**Observações:**

### 6.4 Inferência two-stage
- [ ] Identificar comando de inferência
- [ ] Executar inferência
- [ ] Confirmar geração de predições ou equivalente
- [ ] Confirmar rastros do especialista acionado, se houver

**Comando usado:**  
**Artefatos gerados:**  
**Status:**  
**Observações:**

### 6.5 Avaliação
- [ ] Executar avaliação
- [ ] Confirmar métricas agregadas
- [ ] Confirmar métricas por classe
- [ ] Confirmar matriz de confusão absoluta
- [ ] Confirmar gráfico(s), se previsto

**Comando usado:**  
**Artefatos gerados:**  
**Status:**  
**Observações:**

### 6.6 Critério de conclusão do cenário principal
Marcar concluído apenas se existirem:

- [ ] Métricas agregadas
- [ ] Métricas por classe
- [ ] Matriz de confusão absoluta
- [ ] Predições ou equivalente
- [ ] Relatório sintético do cenário
- [ ] Registro de parâmetros / seed / ambiente

**Status final do cenário principal:**  

---

## 7. Execução do baseline principal

### 7.1 Preparação
- [ ] Script do baseline identificado
- [ ] Recorte compatível com CIC binário confirmado
- [ ] Métricas equivalentes definidas

**Baseline:**  
**Status:**  

### 7.2 Execução
- [ ] Treino executado
- [ ] Inferência executada
- [ ] Avaliação executada

**Comando usado:**  
**Artefatos gerados:**  
**Status:**  
**Observações:**

### 7.3 Consolidação
- [ ] Métricas agregadas disponíveis
- [ ] Métricas por classe disponíveis
- [ ] Matriz de confusão disponível
- [ ] Latência disponível, se suportado
- [ ] Comparação com arquitetura principal viável

**Status final do baseline:**  

---

## 8. Execução do cenário secundário — UNSW binário

### 8.1 Preparação
- [ ] Script de preparação identificado
- [ ] Configurações e mapeamentos verificados
- [ ] Recorte binário confirmado

**Status:**  

### 8.2 Execução
- [ ] Treinamento executado
- [ ] Inferência executada
- [ ] Avaliação executada

**Comandos usados:**  
**Artefatos gerados:**  
**Status:**  
**Observações:**

### 8.3 Consolidação
- [ ] Métricas agregadas disponíveis
- [ ] Métricas por classe disponíveis
- [ ] Matriz de confusão disponível
- [ ] Relatório sintético disponível

**Status final do cenário secundário:**  

### 8.4 Regra de exceção
Se o cenário secundário não puder ser concluído por limitação real da pipeline:
- [ ] documentar a falha
- [ ] registrar causa
- [ ] definir se o paper seguirá apenas com CIC como cenário principal

**Observações da exceção:**  

---

## 9. Consolidação dos artefatos oficiais do paper

### 9.1 Tabelas
- [ ] Tabela principal de resultados criada
- [ ] Tabela de baseline criada
- [ ] Tabela de latência criada, se aplicável

**Arquivos gerados:**  
**Status:**  

### 9.2 Figuras
- [ ] Figura oficial da arquitetura pronta
- [ ] Matriz de confusão principal pronta
- [ ] Matriz de confusão do baseline pronta
- [ ] Figura complementar pronta

**Arquivos gerados:**  
**Status:**  

### 9.3 Predições e rastros
- [ ] Predições do cenário principal salvas
- [ ] Predições do baseline salvas
- [ ] Logs relevantes salvos
- [ ] Manifesto de execução atualizado

**Arquivos gerados:**  
**Status:**  

---

## 10. XAI / interpretabilidade

### 10.1 Verificação
- [ ] Script ou pipeline de XAI identificado
- [ ] Execução reproduzível confirmada
- [ ] Artefatos compreensíveis confirmados

**Status:**  
**Observações:**

### 10.2 Decisão editorial
- [ ] XAI entra no corpo principal
- [ ] XAI entra como material complementar
- [ ] XAI fica apenas como observação / trabalho futuro

**Decisão tomada:**  
**Justificativa:**  

---

## 11. Registro de execução

### 11.1 Manifesto de execução
- [ ] Criar ou atualizar `reports/run_manifest.md`
- [ ] Registrar todas as execuções relevantes
- [ ] Registrar datas, scripts, parâmetros, saídas e observações

**Status:**  

### 11.2 Dados mínimos por execução
Para cada execução relevante, registrar:

| Execução | Dataset | Script | Seed | Saída principal | Status | Observações |
|---|---|---|---:|---|---|---|
| Cenário principal |  |  |  |  |  |  |
| Baseline |  |  |  |  |  |  |
| Cenário secundário |  |  |  |  |  |  |
| XAI |  |  |  |  |  |  |

---

## 12. Atualização do manuscrito após a execução

### 12.1 Seções obrigatórias para revisão
- [ ] `01_resumo.md`
- [ ] `05_experimentos.md`
- [ ] `06_resultados.md`
- [ ] `07_discussao.md`
- [ ] `08_conclusao.md`

### 12.2 Itens a revisar
- [ ] Números finais
- [ ] Baselines
- [ ] Limitações confirmadas
- [ ] Custo/latência
- [ ] Tabelas e figuras
- [ ] Afirmações comparativas
- [ ] Trechos que dependiam de artefatos antigos

**Status:**  
**Observações:**

---

## 13. Critério de pronto para revisão científica

Marcar apenas quando todos os itens abaixo estiverem concluídos:

- [ ] cenário principal executado do zero
- [ ] baseline principal executado
- [ ] métricas principais consolidadas
- [ ] matriz de confusão principal consolidada
- [ ] tabela comparativa principal pronta
- [ ] manuscrito atualizado com os resultados reais
- [ ] limitações revisadas com base na execução real
- [ ] bibliografia e citações coerentes

**Status geral:**  

---

## 14. Observações livres

### Problemas encontrados
- 

### Decisões tomadas
- 

### Itens pendentes
- 

### Próxima ação
- 