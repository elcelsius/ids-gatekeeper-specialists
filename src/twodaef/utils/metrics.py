from __future__ import annotations
from typing import Dict, Any, Sequence
import numpy as np
from sklearn.metrics import f1_score

def f1_per_class(y_true: Sequence, y_pred: Sequence) -> Dict[Any, float]:
    """
    Cálculo manual do F1-Score isolado Classe por Classe.
    
    O F1-Score é a média harmônica entre a Precisão (Quantos dos previstos estavam corretos)
    e o Recall (Quantos dos reais nós conseguimos encontrar). É a métrica rainha de avaliação
    quando seus dados são 'Desbalanceados' (Ex: Você tem só 5 vírus mas tem 5000 acessos normais).
    
    Esta utilidade pega todas as classes identificadas (Ex: 0 e 1, Benzign e Attack) e roda uma avaliação
    do tipo 1-contra-todos de cada uma separadamente. Retornará um dicionário informando a proficiência do 
    modelo lidando isoladamente com a classe '0' e a classe '1' etc.
    """
    
    # Padroniza as listas do Python como as matrizes uniformes do ecosistema do Numpy (Para matemática de alto nível)
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    # Extrai estritamente a lista de rótulos únicos (Classes que existem como classe '0', classe '1')
    classes = np.unique(y_true)
    out: Dict[Any, float] = {}
    
    # Intera sobre a classe, tratando aquele 'loop' numérico, tornando os acertos nela em (1) e outros em (0) temporariamente
    for c in classes:
        # Cria matrizes binárias artificiais onde o que for igual à 'classe C' vira 1 e o resta ignora vira 0
        y_true_bin = (y_true == c).astype(int)
        y_pred_bin = (y_pred == c).astype(int)
        
        # Calcula a pontuação e insere no documento de saída
        # Zero_division=0 significa: Se o modelo nunca chutou essa classe por incapacidade, anote como Força Zero (Zere do invés de crashar alertando infinito matematico).
        out[c] = f1_score(y_true_bin, y_pred_bin, zero_division=0)
        
    return out
