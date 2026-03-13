from __future__ import annotations
from pathlib import Path
from typing import Dict

def load_feature_costs(path: str | Path | None = None) -> Dict[str, float]:
    """
    Carrega o custo associado à extração de cada feature.
    Em sistemas do mundo real (ex: redes de computadores), extrair o "Tamanho do Pacote" pode ser
    muito mais rápido do que extrair o "Tempo de Resposta TCP".
    
    Este arquivo pode ser opcionalmente provido como um CSV ou TXT no formato:
    nome_da_feature,custo
    
    Se não houver arquivo, assumimos que todas as features custam 1.0 (custo igualitário).
    """
    costs: Dict[str, float] = {}
    
    # Se não foi passado arquivo, retorna dicionário vazio
    if path is None:
        return costs
        
    p = Path(path)
    if not p.exists():
        return costs
        
    # Lê linha por linha
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        # Ignora linhas vazias ou comentários (que começam com #)
        if not s or s.startswith("#"):
            continue
            
        # Suporta separador por Ponto e Vírgula (;) ou Vírgula (,)
        parts = [x.strip() for x in s.replace(";", ",").split(",")]
        
        # Garante que temos as duas partes: Nome e Custo
        if len(parts) < 2:
            continue
            
        feat, cost = parts[0], parts[1]
        try:
            # Converte e armazena
            costs[feat] = float(cost)
        except ValueError:
            # Ignora se o custo não for um número válido
            continue
            
    return costs

def estimate_set_cost(features: list[str], costs: Dict[str, float] | None = None) -> float:
    """
    Dado um conjunto de Features, calcula a "Soma Total dos Custos".
    Isso é usado para penalizar conjuntos (pools) de atributos que são muito caros 
    computacionalmente de serem extraídos em tempo real.
    """
    if not features:
        return 0.0
        
    # Usa o dicionário passado, ou um vazio se nenhum foi provido
    costs = costs or {}
    
    # Soma. Se a feature não estiver no dicionário de custos, assume custo 1.0 Default.
    return float(sum(costs.get(f, 1.0) for f in features))
