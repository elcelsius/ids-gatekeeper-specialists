from dataclasses import dataclass
from typing import List, Optional, Tuple
import time
import numpy as np
import pandas as pd

# Importando o modelo de Árvore de Decisão do Scikit-Learn
from sklearn.tree import DecisionTreeClassifier
# Importando função para dividir os dados em conjuntos de treino e teste
from sklearn.model_selection import train_test_split
# Importando métricas essenciais para avaliação
from sklearn.metrics import f1_score, classification_report
# Importando o módulo tree para poder exportar as regras da árvore
from sklearn import tree

@dataclass
class GatekeeperConfig:
    """
    Configurações do modelo Gatekeeper.
    Este modelo age como um 'porteiro' inicial, utilizando uma árvore de decisão rápida
    e interpretável (DecisionTreeClassifier) para tomar decisões antes de modelos mais complexos.
    """
    # Profundidade máxima da árvore. Um valor baixo (ex: 6) evita overfitting e garante alta velocidade.
    max_depth: int = 6
    # Número mínimo de amostras necessárias para criar uma folha (nó final).
    min_samples_leaf: int = 10
    # Semente aleatória para garantir reprodutibilidade nos resultados.
    random_state: int = 42

class GatekeeperModel:
    """
    O GatekeeperModel é o estágio inicial (Stage 1) da arquitetura em dois estágios.
    Ele tenta classificar amostras de maneira rápida e com baixo custo computacional.
    Se a incerteza for alta, um 'especialista' (Stage 2) poderá ser chamado posteriormente.
    """
    def __init__(self, cfg: GatekeeperConfig | None = None):
        # Utiliza as configurações fornecidas ou as configurações padrão caso nenhuma seja passada
        self.cfg = cfg or GatekeeperConfig()
        
        # Instancia o modelo de Árvore de Decisão com os hiperparâmetros configurados
        self.model = DecisionTreeClassifier(
            max_depth=self.cfg.max_depth,
            min_samples_leaf=self.cfg.min_samples_leaf,
            random_state=self.cfg.random_state,
        )
        # Inicializa variáveis para armazenar nomes de atributos (features) e classes alvo
        self.feature_names_: Optional[List[str]] = None
        self.classes_: Optional[np.ndarray] = None

    def fit(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """
        Treina o modelo Gatekeeper a partir dos dados de entrada (X) e rótulos (y).
        Também separa internamente uma porção (20%) para validação rápida.
        """
        self.feature_names_ = list(X.columns)
        
        # Divide os dados de maneira estratificada (mantendo a proporção de cada classe)
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=self.cfg.random_state
        )
        
        # Treina (ajusta) a árvore de decisão aos dados de treino
        self.model.fit(X_train, y_train)
        
        # Avalia o modelo no conjunto de validação
        y_pred = self.model.predict(X_val)
        
        # A métrica F1 Macro calcula a média ponderada entre precisão e recall de maneira equilibrada
        f1 = f1_score(y_val, y_pred, average="macro")
        self.classes_ = self.model.classes_
        
        # Retorna as métricas de treino compiladas em um dicionário
        return {
            "f1_macro": float(f1),
            "report": classification_report(y_val, y_pred, zero_division=0)
        }

    def predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, float]:
        """
        Gera as predições para os dados informados, registrando além disso o tempo que levou
        para processar cada amostra, dado que a "baixa latência" é o grande trunfo deste modelo.
        """
        # Garante que as colunas na predição sigam a mesma ordem do treino
        if self.feature_names_ is None:
            self.feature_names_ = list(X.columns)
        X = X[self.feature_names_]
        
        # Registra o tempo inicial (alta precisão com time.perf_counter)
        t0 = time.perf_counter()
        
        # Faz a inferência usando a árvore de decisão treinada
        y_pred = self.model.predict(X)
        
        # Registra o tempo total decorrido em milissegundos
        lat_ms_total = (time.perf_counter() - t0) * 1000.0
        
        # Retorna: (Array de Predições, Latência média em MS por amostra)
        return y_pred, lat_ms_total / max(len(X), 1)

    def export_rules(self) -> str:
        """
        Exporta as regras geradas pela Árvore de Decisão em formato de texto.
        Issso promove interpretabilidade ('White Box') e transparência para o modelo.
        """
        return tree.export_text(self.model, feature_names=self.feature_names_ or None)
