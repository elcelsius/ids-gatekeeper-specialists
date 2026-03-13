from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import json
import joblib
import numpy as np
import pandas as pd


# =========================
# Utilitários de Diretórios
# =========================
def ensure_dir(path: str | Path) -> Path:
    """
    Garante que a pasta (diretório) desejada exista. Se não existir, ele a cria automaticamente.
    Isso evita o clássico erro 'FileNotFoundError: No such file or directory' ao salvar arquivos.
    
    Aceita tanto um caminho de pasta ('pasta/subpasta')
    quanto um caminho de arquivo ('pasta/subpasta/arquivo.txt').
    """
    p = Path(path)
    
    # Se o caminho contiver um sufixo (ex: .txt, .csv), tratamos como arquivo
    # e criamos a pasta 'pai' (parent) onde este arquivo deveria residir.
    if p.suffix:
        p.parent.mkdir(parents=True, exist_ok=True)
        return p.parent
        
    # Se não tiver sufixo, assumimos que já é uma pasta e a criamos
    p.mkdir(parents=True, exist_ok=True)
    return p


# =========================
# Manipulação de Modelos (joblib)
# =========================
# O Joblib é uma biblioteca super eficiente para salvar (serializar) e carregar
# objetos grandes do Python na memória, ideal para grandes Modelos de Machine Learning (como Scikit-Learn ou XGBoost).
def save_joblib(obj: Any, path: str | Path) -> None:
    """Salva um objeto Python complexo (como um Modelo de IA Treinado) em um arquivo na máquina."""
    p = Path(path)
    ensure_dir(p.parent)  # Garante que a pasta existe antes de tentar salvar
    joblib.dump(obj, p)


def load_joblib(path: str | Path) -> Any:
    """Carrega de volta para a memória um objeto Python salvo com Joblib."""
    return joblib.load(Path(path))


# =========================
# Leitura e Escrita de Tabelas (CSV) em UTF-8
# =========================
def read_csv_utf8(path: str | Path) -> pd.DataFrame:
    """
    Leitura robusta de arquivo CSV (Tabelas) para um DataFrame do Pandas.
    A definição de 'encoding="utf-8"' previne dores de cabeça com acentos e caracteres especiais.
    """
    # low_memory=False desativa uma heurística do pandas que fatiaria a checagem de tipos de coluna
    # o que requer mais memória RAM, mas evita bugs estranhos em dados mistos.
    return pd.read_csv(Path(path), encoding="utf-8", low_memory=False)


def write_csv_utf8(df: pd.DataFrame, path: str | Path) -> None:
    """
    Salva a Tabela (DataFrame) do Pandas para um arquivo físico no computador .CSV.
    """
    p = Path(path)
    ensure_dir(p.parent)
    # index=False impede que o número da linha de registro (0, 1, 2...) seja salvo no arquivo
    df.to_csv(p, index=False, encoding="utf-8")


# =========================
# Leitura e Escrita de JSON (Configurações e Metadados)
# =========================
def read_json_utf8(path: str | Path) -> Dict[str, Any]:
    """
    Lê um arquivo .JSON (Usado massivamente para configurações e mapas de metadados) 
    e o transforma em um Dicionário padrão do Python.
    """
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8"))


def write_json_utf8(obj: Dict[str, Any], path: str | Path) -> None:
    """
    Pega um Dicionário do Python e o escreve estilizado num arquivo .JSON.
    """
    p = Path(path)
    ensure_dir(p.parent)
    # indent=2 adiciona tabulações estéticas deixando o arquivo legível para o ser humano
    # ensure_ascii=False garante que palavras como 'maçã' não quebrem o json no meio do caminho.
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


# =========================
# Sanitização de Tabelas de Dados Numéricos
# =========================
def sanitize_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa uma tabela do Pandas retirando nela valores matematicamente invariaveis
    provindos de calculos que falharam.
    Modelos de Inteligencia Artificial quebram duramente caso recebam coisas como 'Infinito' ou 'Sem numero'.
    
    Substitui:
    1. ±infinito (provindo de divisão por zero na extração) por -> Not a Number (NaN)
    2. Valores Vazios (Not a Number - NaN) -> por -> 0.
    """
    clean = df.replace([np.inf, -np.inf], np.nan)
    return clean.fillna(0)
