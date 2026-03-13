from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Tuple
import json
import time
import importlib

import joblib
import numpy as np
import pandas as pd
from loguru import logger
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder

from twodaef.utils.metrics import f1_per_class

# ---------- Modelo Factory (Fábrica Dinâmica de Modelos) ----------
# Esta função verifica quais bibliotecas de Machine Learning estão instaladas no ambiente
# e retorna um dicionário de funções (lambdas) prontas para instanciar os modelos.
# Isso torna o código flexível: se o XGBoost não estiver instalado, ele simplesmente não será usado.
def _available_models() -> Dict[str, Any]:
    models: Dict[str, Any] = {}
    
    # Tenta carregar o LightGBM (rápido e focado em árvores balanceadas por folhas)
    if importlib.util.find_spec("lightgbm"):
        from lightgbm import LGBMClassifier
        models["lgbm"] = lambda: LGBMClassifier(
            n_estimators=300, learning_rate=0.05, num_leaves=63, subsample=0.8, colsample_bytree=0.8
        )
        
    # Tenta carregar o XGBoost (robusto e muito utilizado em competições do Kaggle)
    if importlib.util.find_spec("xgboost"):
        from xgboost import XGBClassifier
        models["xgb"] = lambda: XGBClassifier(
            n_estimators=400, max_depth=8, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
            tree_method="hist", eval_metric="mlogloss", n_jobs=0
        )
        
    # Tenta carregar o CatBoost (excelente para dados com valores categóricos e robusto a overfitting)
    if importlib.util.find_spec("catboost"):
        from catboost import CatBoostClassifier
        models["cat"] = lambda: CatBoostClassifier(
            iterations=500, depth=8, learning_rate=0.05, loss_function="MultiClass", verbose=False
        )
        
    # Sempre teremos estes modelos (padrões da biblioteca Scikit-Learn) como plano B
    # HistGradientBoostingClassifier é a implementação nativa mais rápida do Scikit-Learn para Gradient Boosting
    models["sk_hgb"] = lambda: HistGradientBoostingClassifier(max_depth=None, learning_rate=0.1)
    models["sk_rf"]  = lambda: RandomForestClassifier(n_estimators=300, n_jobs=-1, random_state=42)
    
    return models

@dataclass
class TrainConfig:
    """
    Configurações de Treinamento dos Especialistas (Estágio 2).
    """
    train_csv: str                         # Base de dados de treino em formato CSV
    target_col: str                        # Nome da coluna que o modelo deve prever (a resposta)
    feature_pool_json: str                 # Arquivo com várias sugestões de 'subconjuntos de atributos/features' a testar
    out_dir: str = "artifacts/specialists" # Pasta onde os modelos treinados serão salvos
    map_path: str = "artifacts/specialist_map.json" # Onde salvar o dicionário de roteamento Especialista -> Classe
    test_size: float = 0.2                 # Proporção dos dados reservados para validação (20%)
    seed: int = 42                         # Semente para garantir resultados consistentes e reprodutíveis
    models: List[str] | None = None        # Lista explícita de modelos a testar (ex: ["xgb", "sk_rf"]). Deixe None para "Todos disponíveis"
    max_features_per_set: int | None = None# Opção para limitar a quantidade de features por set testado, forçando testes menores

def _load_feature_pool(path: str) -> List[Dict[str, Any]]:
    """Carrega as definições (grupos de features) para testar os especialistas."""
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    
    # Se já seguir o padrão esperado, tendo a chave "pool" que mapeia para uma lista
    if isinstance(d, dict) and "pool" in d:
        return d["pool"]
        
    # Se seguir o formato {"feature_sets": {"name": [feats...]}}
    if isinstance(d, dict) and "feature_sets" in d and isinstance(d["feature_sets"], dict):
        fs = d["feature_sets"]
        return [{"name": k, "features": v} for k, v in fs.items()]
        
    # Formato fallback (Assume que o arquivo em si é apenas o pool inteiro)
    return d

def _subset_columns(df: pd.DataFrame, feats: List[str]) -> List[str]:
    """Filtra apenas as colunas que efetivamente existem no DataFrame e são Numéricas."""
    return [c for c in feats if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]

def train_specialists(cfg: TrainConfig) -> Dict[str, Any]:
    """
    O Coração do Treinamento dos Especialistas.
    Aqui testamos diferentes algoritmos e conjuntos de features (atributos) 
    para descobrir a MELHOR combinação para classificar cada classe específica (ataque ou classe do target).
    """
    # 1. Preparando os Dados
    df = pd.read_csv(cfg.train_csv)
    assert cfg.target_col in df.columns, f"target_col {cfg.target_col} não existe em {cfg.train_csv}"
    
    # Extrai o vetor de respostas "Y" originais.
    y_raw = df[cfg.target_col].values
    
    # --- Blacklist (Lista Negra) ---
    # Remove colunas de identificação e da própria resposta (evitando 'Data Leakage' ou 'Vazamento de Dados').
    # Vazamento de dados ocorre quando o modelo aprende as respostas através de variáveis "injustas".
    blacklist = {cfg.target_col, "Label", "label", "attack_cat", "Attack_cat", "id", "ID"}
    X = df.drop(columns=[c for c in blacklist if c in df.columns])

    # Filtra apenas colunas numéricas (Modelos avançados precisam de números) e remove linhas com falha/nula.
    X = X.select_dtypes(include=[np.number]).replace([np.inf, -np.inf], np.nan).dropna(axis=1, how="any")
    cols_universe = X.columns.tolist()

    # Transforma classes textuais (ex: 'DoS', 'DDoS') em índices inteiros (0, 1, 2...)
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    classes_enc = le.classes_.tolist()

    # Separa os dados em Treino e Validação, preservando a proporção de cada classe (stratify=y)
    X_tr, X_va, y_tr, y_va = train_test_split(X, y, test_size=cfg.test_size, random_state=cfg.seed, stratify=y)

    # 2. Carrega as combinações de atributos que serão experimentadas (Feature pool)
    pool = _load_feature_pool(cfg.feature_pool_json)
    
    # Se foi definido um limite máximo de features nos testes
    if cfg.max_features_per_set:
        for p in pool:
            p["features"] = p["features"][: cfg.max_features_per_set]

    # 3. Modelos Candidatos (Quais algoritmos vamos submeter aos testes)
    avail = _available_models()
    if cfg.models:
        # Se foi fornecido no config, usamos apenas os solicitados (que estejam instalados) 
        model_keys = [m for m in cfg.models if m in avail]
    else:
        # Caso contrário, preferencialmente testamos todos os Gradient Boosters pesados primeiro, e depois Scikit-Learn
        pref = ["lgbm", "xgb", "cat", "sk_hgb", "sk_rf"]
        model_keys = [m for m in pref if m in avail]

    logger.info(f"Modelos candidatos: {model_keys}")
    logger.info(f"Total de feature sets testados: {len(pool)}")

    # 4. A Busca ('Grid/Search' manual) do melhor especialista para CADA CLASSE
    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Persistimos os metadados para que na hora da Inferência (predict) não nos percamos 
    results: Dict[str, Any] = {
        "target_col": cfg.target_col,
        "classes": classes_enc,                   # Nomes originais. Ex: ['Benign', 'DDoS', 'DoS']
        "class_encoding": {str(i): cls for i, cls in enumerate(classes_enc)}, # '0': 'Benign', '1': 'DDoS'...
        "models_used": model_keys,
        "specialists": {}  # Aqui será populado com { "Nome da Classe": {qual modelo, qual featureset, f1_score...} }
    }

    # Avaliamos CADA uma das classes tentando descobrir quem é o "Especialista" perfeito para identificá-la.
    for k_idx, k_name in enumerate(classes_enc):
        best: Dict[str, Any] | None = None

        # Testa algoritmos
        for mkey in model_keys:
            model_fn = avail[mkey]

            # Testa as combinações de colunas/features listadas no pool
            for f in pool:
                feats = _subset_columns(X_tr.assign(**X_va), f["features"])  # Filtra e cruza
                if len(feats) == 0:
                    continue

                # Cria o modelo cru
                clf = model_fn()
                
                # 4.1 Treinamento ('Fit')
                clf.fit(X_tr[feats], y_tr)

                # 4.2 Avaliação da Qualidade
                # Qual a pontuação F1 (equilíbrio entre falsos positivos e falsos negativos) para ESSA classe 'k'?
                y_pred = clf.predict(X_va[feats])
                f1_dict = f1_per_class(y_va, y_pred)
                f1_k = float(f1_dict.get(k_idx, 0.0))

                # 4.3 Avaliação da Latência
                # Tão importante quanto prever certo, é prever RÁPIDO. O especialista precisa ser viável no mundo real.
                t0 = time.perf_counter()
                _ = clf.predict(X_va[feats])
                dt = (time.perf_counter() - t0)
                latency_ms = (dt / max(1, X_va.shape[0])) * 1000.0

                cand = {
                    "model_key": mkey,
                    "feature_set_name": f["name"],
                    "k": int(len(feats)),
                    "f1_k": f1_k,
                    "latency_ms": latency_ms,
                    "features": feats,
                }
                
                # Regra de decisão para o campeão:
                # Se for melhor F1... OU, em caso de empate numérico na pontuação de F1, se for mais RÁPIDO (menor latência)
                if (best is None) or (f1_k > best["f1_k"]) or (np.isclose(f1_k, best["f1_k"]) and latency_ms < best["latency_ms"]):
                    best = cand

        # Se depois de testar tudo nenhum der certo
        if best is None:
            logger.warning(f"Nenhum especialista coerente encontrado para a classe {k_name}.")
            continue

        # 5. Campeão Encontrado!
        # Agora nós re-treinamos o MELHOR modelo da MELHOR forma possível usando TODOS os dados da base
        # garantindo o modelo final mais robusto possível para aquela classe.
        final_model = avail[best["model_key"]]()
        feats = best["features"]
        final_model.fit(X[feats], y)

        # Salva (Exporta) este modelo em arquivo .joblib físico no disco.
        class_name = str(k_name)
        class_dir = out_dir / class_name
        class_dir.mkdir(parents=True, exist_ok=True)
        model_path = class_dir / "model.joblib"
        joblib.dump(final_model, model_path)

        best["model_path"] = str(model_path)
        results["specialists"][class_name] = best
        
        # Consolida resultados
        logger.success(f"Especialista Campeão para '{k_name}': {best['model_key']} com features '{best['feature_set_name']}' "
                       f"(F1 (específico para k)={best['f1_k']:.4f}, usando {best['k']} features e latência {best['latency_ms']:.4f} ms)")

    # 6. Salvar o índice principal ou "Mapa de Roteamento" 
    # (Este arquivo é fundamental para a fase de Inferência - Fase 2 do Estágio)
    map_path = Path(cfg.map_path)
    map_path.parent.mkdir(parents=True, exist_ok=True)
    map_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    
    logger.success(f"Construção civil do modelo especialista finalizada. Mapa salvo em {map_path}")
    return results
