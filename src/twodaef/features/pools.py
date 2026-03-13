from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
import math
import random

import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_classif
from sklearn.preprocessing import LabelEncoder

from twodaef.features.costs import load_feature_costs, estimate_set_cost

@dataclass
class PoolConfig:
    """
    Configurações da Geração do "Pool de Features" (Conjunto de Atributos).
    Utilizamos Algoritmos Heurísticos (Biologicamente Inspirados) para testar 
    quais conjuntos de atributos trazem o maior ganho de informação para os modelos.
    """
    target_col: str                          # Nome da coluna que dita a classe/ataque
    max_features_per_set: int = 20           # Tamanho máximo de features num único teste
    total_sets: int = 30                     # Número total de "Baterias de teste" (População da heurística)
    seed: int = 42                           # Semente aleatória para consistência
    # Proporções (pesos paramétricos) para cada um dos 3 algoritmos inspirados na natureza
    ratio_pso: float = 0.34                  # Particle Swarm Optimization (Nuvem de Partículas)
    ratio_gwo: float = 0.33                  # Grey Wolf Optimizer (Busca de Lobos Cinzentos)
    ratio_ffa: float = 0.33                  # Firefly Algorithm (Algoritmo dos Vaga-lumes)
    feature_costs_path: str | None = None    # Dicionário do custo exigido de extração de cada feature (opicional)

def _score_features_mi(df: pd.DataFrame, target_col: str) -> pd.Series:
    """
    Calcula o "Mutual Information" (Informação Mútua - MI) de cada Feature.
    Basicamente, ele responde: "O quão bem saber o valor da variável X ajuda a prever a resposta Y?"
    Valores maiores significam que a Feature tem muita correlação com a classe do ataque.
    """
    y_raw = df[target_col].values
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    
    # --- Blacklist (Segurança contra Vazamento de Dados) ---
    blacklist = {target_col, "Label", "label", "attack_cat", "Attack_cat", "id", "ID"}

    X = df.drop(columns=[c for c in blacklist if c in df.columns])
    # Mantém apenas colunas numéricas (Algoritmos de MI lidam melhor com números puros)
    X = X.select_dtypes(include=[np.number]).copy()
    
    # Remove colunas com problemas estocásticos (infinitos ou vazios)
    X = X.replace([np.inf, -np.inf], np.nan).dropna(axis=1, how="any")
    sel_cols = X.columns.tolist()
    
    if not sel_cols:
        raise ValueError("Nenhuma coluna numérica disponível após limpeza.")
        
    # O coração da função: Calcula O ganho de informação (Mutual Info) de cada variável isolada perante Y.
    mi = mutual_info_classif(X[sel_cols], y, discrete_features=False, random_state=0)
    
    # Retorna uma Série do Pandas ordenada do mais forte pro mais fraco. Ex: {"Duracao: 0.9", "Tamanho pckt: 0.8"...}
    return pd.Series(mi, index=sel_cols).sort_values(ascending=False)

def _clip_set(s: List[str], k: int) -> List[str]:
    """Utilitário: Limita a quantidade do Array e remove duplicados asism mantendo a ordem importada."""
    seen = set()
    out = []
    for f in s:
        if f in seen:
            continue
        seen.add(f)
        out.append(f)
        if len(out) >= k:
            break
    return out

def _random_subset(candidates: List[str], k: int) -> List[str]:
    """Utilitário: Extrai K elementos aleatórios do conjunto universal."""
    if k <= 0:
        return []
    if len(candidates) <= k:
        return candidates[:]
    return random.sample(candidates, k)

def _local_mutation(feats: List[str], universe: List[str], k: int, p_swap: float = 0.3) -> List[str]:
    """
    Simulação Genética de Mutação:
    Para cada 'Feature' do indivíduo (conjunto a ser testado), há uma chance aleatória (p_swap: 30%) 
    deve ser trocada subitamente por alguma outra feature do Universo.
    Garante que os algoritmos de buscas explorem novos horizontes e não fiquem estagnados em falsos positivos.
    """
    feats = feats[:]
    for i in range(len(feats)):
        if random.random() < p_swap:
            # Troca por uma feature aleatória que ainda NÃO ESTEJA no conjunto (Max de 5 tentativas)
            cand = random.choice(universe)
            tries = 0
            while cand in feats and tries < 5:
                cand = random.choice(universe)
                tries += 1
            feats[i] = cand
    return _clip_set(feats, k)

def _fitness_mi(feats: List[str], mi_rank: pd.Series) -> float:
    """
    Calcula a Força (Fitness) de um indivíduo avaliando meramente seu ranking normalizado de Informação Mútua.
    Neste estágio rudimentar, se as features contiverem informações valiosas, terão "Pontuação Fitness" alta.
    """
    if not feats:
        return 0.0
    s = 0.0
    denom = float(mi_rank.max()) if mi_rank.max() > 0 else 1.0
    for f in feats:
        if f in mi_rank.index:
            s += float(mi_rank[f]) / denom
    return s

# ----------------- Heurísticas Inspiradas na Natureza -----------------

def _make_pso_like(mi_rank: pd.Series, k: int, n_sets: int, seed: int) -> List[List[str]]:
    """
    Geração estilo 'Particle Swarm Optimization - PSO' (Enxame de Partículas).
    Baseado no movimento de pássaros procurando alimentos. 
    Lembrando de seu melhor ponto local ("Inércia"), mas convergindo em direção ao melhor global.
    """
    random.seed(seed + 17)
    universe = mi_rank.index.tolist()
    sets: List[List[str]] = []
    
    # 1. Partícula inicial é sempre "As Top M.I. de fábrica" (Nosso 'Caminho mais seguro')
    gbest = universe[:k]
    sets.append(gbest)
    
    # 2. Iterações curtas para gerar nuvem e diversificar a caçada
    for _ in range(n_sets - 1):
        # 'Inércia:' Cada nova rota tenta manter uma poção do Topo (G_Best) original como base.
        keep = random.randint(max(1, k // 3), max(2, k // 2))
        candidate = _clip_set(gbest[:keep] + _random_subset(universe, k - keep), k)
        
        # Aplica uma pequena mutação para desbravar
        candidate = _local_mutation(candidate, universe, k, p_swap=0.2)
        
        # Se as variáveis do candidato gerarem uma matemática melhor que a "Liderança (g_best)", vira o novo Líder
        if _fitness_mi(candidate, mi_rank) > _fitness_mi(gbest, mi_rank):
            gbest = candidate
            
        sets.append(candidate)
    return sets

def _make_gwo_like(mi_rank: pd.Series, k: int, n_sets: int, seed: int) -> List[List[str]]:
    """
    Geração estilo 'Grey Wolf Optimizer - GWO' (Otimização dos Lobos Cinzentos).
    Simula uma alcateia: o líder 'Alpha' (Melhor), vice 'Beta', 'Delta' e submissos Omega.
    Os Ômegas seguem a direção estipulada pelos lobos superiores para cercar a "caça" das melhores Features.
    """
    random.seed(seed + 31)
    universe = mi_rank.index.tolist()
    sets: List[List[str]] = []
    
    # Iniciais (posições na matriz): Alpha (Top features), Beta (Bons medianos), Delta (Indiferentes)
    alpha = universe[:k]
    mid_start = max(0, len(universe)//3)
    beta = universe[mid_start:mid_start + k]
    delta = _random_subset(universe, k)
    
    sets.extend([alpha, beta, delta])
    
    while len(sets) < n_sets:
        # Pondera o comportamento (50% do líder Alpha, 30% do viçe Beta, 20% do Delta)
        w = [0.5, 0.3, 0.2]
        pool = []
        for src, weight in zip([alpha, beta, delta], w):
            take = max(1, int(math.ceil(weight * k)))
            pool.extend(src[:take])
            
        candidate = _clip_set(pool + _random_subset(universe, k), k)
        candidate = _local_mutation(candidate, universe, k, p_swap=0.25)
        
        # Como em toda alcateia: Desbancando cargos de Alpha ou Beta se o novo Lobo/Conjunto provar ser mais competente.
        if _fitness_mi(candidate, mi_rank) > _fitness_mi(alpha, mi_rank):
            # O novo vira Alpha, o Antigo vira Beta
            alpha, beta, delta = candidate, alpha, beta
        elif _fitness_mi(candidate, mi_rank) > _fitness_mi(beta, mi_rank):
            # O novo vira Beta
            beta, delta = candidate, beta
        else:
            delta = candidate
            
        sets.append(candidate)
    return sets[:n_sets]

def _make_ffa_like(mi_rank: pd.Series, k: int, n_sets: int, seed: int) -> List[List[str]]:
    """
    Geração estilo 'Firefly Algorithm - FFA' (Algoritmo do Vagalume).
    Vagalumes vagam o ar, se baseando no brilho um dos outros. 
    Se o Vagalume A for mais 'Brilhoso' (Maior Fitness) que o B, o B caminha na direção de A.
    """
    random.seed(seed + 59)
    universe = mi_rank.index.tolist()
    
    # Mapeia uma grande porção aleatória de Vagalumes dispersos + o Topk de partida
    population = [universe[:k]] + [_random_subset(universe, k) for _ in range(max(2, n_sets // 3))]
    
    def brightness(s: List[str]) -> float:
        return _fitness_mi(s, mi_rank)
        
    while len(population) < n_sets:
        # Coloca dois vagalumes para brigar ao acaso
        a, b = random.sample(population, 2)
        # Identifica quem brilha mais...
        best, worst = (a, b) if brightness(a) >= brightness(b) else (b, a)
        
        # Atração: O vagalume pior se aproxima do melhor (Troca 25% de suas features aleatórias pelas features do Campeão).
        merged = _clip_set(worst[:], k)
        for i in range(max(1, k // 4)):
            if i < len(best) and i < len(merged):
                merged[i] = best[i]
                
        # Mantém pequena incerteza/movimento da natureza (Mutação)
        merged = _local_mutation(merged, universe, k, p_swap=0.15)
        population.append(merged)
        
    return population[:n_sets]

def build_feature_pool(df: pd.DataFrame, cfg: PoolConfig) -> Dict[str, Any]:
    """
    Motor central que orquestra a Geração de Diferentes Pools (Apostas) de Conjtuntos de Features.
    Ele chama as três diferentes simulações naturais (PSO, Lobos e Vagalumes) e compila os 
    resultados sugeridos por elas para que o 'train_specialists' consiga testar todos depois e tirar uma decisão.
    """
    random.seed(cfg.seed)
    
    # 1. Analisa os dados reais e ranqueia as melhores features puras
    mi_rank = _score_features_mi(df, cfg.target_col)

    # 2. Divide as cotas de gerações da população para as 3 metodologias.
    n_pso = max(1, int(round(cfg.total_sets * cfg.ratio_pso)))
    n_gwo = max(1, int(round(cfg.total_sets * cfg.ratio_gwo)))
    n_ffa = max(1, int(cfg.total_sets - n_pso - n_gwo))

    k = cfg.max_features_per_set
    
    # 3. Invoca as heurísticas para gerar as "hipóteses" criativas.
    pso_sets = _make_pso_like(mi_rank, k, n_pso, cfg.seed)
    gwo_sets = _make_gwo_like(mi_rank, k, n_gwo, cfg.seed)
    ffa_sets = _make_ffa_like(mi_rank, k, n_ffa, cfg.seed)

    # 4. Cálculo auxiliar de Custos operacionais do modelo
    costs_map = load_feature_costs(cfg.feature_costs_path)
    def pack(name: str, feats: List[str]) -> Dict[str, Any]:
        """Encapsula gerando um dicionário legível das Features em questão."""
        return {
            "name": name,
            "features": feats,
            "k": len(feats),
            "score_mi_sum": float(sum(mi_rank.get(f, 0.0) for f in feats)),
            "est_cost": float(estimate_set_cost(feats, costs_map))
        }

    pool = []
    # 5. Organiza todos os grupos com nomes das Heurísticas.
    for i, s in enumerate(pso_sets):
        pool.append(pack(f"PSO_{i+1}", s))
    for i, s in enumerate(gwo_sets):
        pool.append(pack(f"GWO_{i+1}", s))
    for i, s in enumerate(ffa_sets):
        pool.append(pack(f"FFA_{i+1}", s))

    # 6. Ordena pela Força Natural do Mutual Information (Apenas para organização estética do JSON).
    pool = sorted(pool, key=lambda d: d["score_mi_sum"], reverse=True)

    # Documenta os metadados gerados que serão consumidos pelo avaliador/treinador mais tarde.
    return {
        "target_col": cfg.target_col,
        "max_features_per_set": cfg.max_features_per_set,
        "total_sets": cfg.total_sets,
        "seed": cfg.seed,
        "pool": pool,
        "mi_top10": mi_rank.head(10).to_dict(),
        "n_features_universe": int(mi_rank.shape[0]),
    }
