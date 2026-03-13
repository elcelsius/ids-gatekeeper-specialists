from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple
import json
import pandas as pd
from loguru import logger


def _read_summary_csv(dir_path: Path) -> pd.DataFrame:
    """
    Função auxiliar para ler o arquivo CSV de resumo de importâncias (SHAP).
    Ela valida se o arquivo existe e se as colunas esperadas estão presentes, 
    evitando que o código quebre mais à frente.
    
    Args:
        dir_path: Caminho do diretório (Path) contendo o arquivo 'summary_mean_abs_shap.csv'.
        
    Returns:
        Um DataFrame do Pandas contendo os dados do CSV.
    """
    csv_path = dir_path / "summary_mean_abs_shap.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Não encontrado: {csv_path}")
    
    # Lê os dados do arquivo CSV
    df = pd.read_csv(csv_path)
    
    # Valida de forma defensiva se as colunas essenciais estão no arquivo lido.
    # O uso do issubset garante que 'feature' e 'mean_abs_shap' sejam pelo menos um subconjunto
    # das colunas existentes no CSV. Se não forem, o assert lançará um erro claro.
    assert {"feature", "mean_abs_shap"}.issubset(df.columns), f"Colunas esperadas não encontradas em {csv_path}"
    
    return df


def aggregate_xai(base_dir: str, out_dir: str, top_k: int = 10) -> Dict[str, str]:
    """
    Lê as pastas class_* (que representam diferentes classes ou especialistas) dentro 
    de um diretório base e agrega (combina) os resultados de interpretabilidade (XAI).
    
    O que essa função faz de forma educativa:
      1. Percorre todos os diretórios de saída das diferentes classes do modelo.
      2. Pega as `top_k` features (características) mais relevantes para cada classe.
      3. Junta tudo em um único arquivo CSV consolidado (ideal para análise numéricas).
      4. Gera também um Markdown com tabelas fáceis de ler por humanos.
      
    Args:
        base_dir: Diretório que contém as pastas das classes com os resultados individuais.
        out_dir: Diretório onde os arquivos consolidados finais serão salvos.
        top_k: Top K atributos que mais influenciaram a decisão do modelo (padrão é 10).
        
    Returns:
        Um dicionário contendo os caminhos exatos dos dois artefatos gerados:
        'csv' (dados puros) e 'md' (apresentação visual).
    """
    base = Path(base_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Encontra e ordena todas as subpastas que começam com o nome 'class_' 
    class_dirs = sorted([p for p in base.glob("class_*") if p.is_dir()])
    if not class_dirs:
        raise RuntimeError(f"Nenhuma pasta class_* encontrada em {base_dir}")

    # Lista vazia que vai acumular as informações em formato de dicionário (que depois vai virar o DF final)
    records: List[Dict[str, object]] = []
    
    # Inicializa o corpo do relatório Markdown com um título Markdown
    md_parts: List[str] = ["# Relatório XAI Consolidado (SHAP)\n"]

    for cdir in class_dirs:
        # Extrai apenas o valor da classe, substituindo a string 'class_' por uma string vazia
        class_key = cdir.name.replace("class_", "", 1)
        
        # Lê e seleciona as linhas das top K variáveis usando sort_values e head
        df = _read_summary_csv(cdir).sort_values("mean_abs_shap", ascending=False).head(top_k)
        
        # 'reset_index(drop=True)' reconstrói o índice [0, 1, 2...] que poderia estar fora de ordem,
        # devido à ordenação e seleção feita pelo pandas acima.
        df = df.reset_index(drop=True)

        # CSV consolidado (acumula)
        for i, row in df.iterrows():
            records.append({
                "class_key": class_key,
                "rank": i + 1,
                "feature": row["feature"],
                "mean_abs_shap": float(row["mean_abs_shap"]),
            })

        # Tabela em Markdown
        md_parts.append(f"## Classe {class_key}\n")
        md_parts.append("| Rank | Feature | |SHAP| médio |\n|---:|---|---:|\n")
        for i, row in df.iterrows():
            md_parts.append(f"| {i+1} | `{row['feature']}` | {row['mean_abs_shap']:.6f} |\n")
        md_parts.append("\n")

    # Salva CSV consolidado
    df_all = pd.DataFrame.from_records(records)
    csv_out = out / "xai_shap_consolidado.csv"
    df_all.to_csv(csv_out, index=False)

    # Salva Markdown
    md_out = out / "xai_shap_consolidado.md"
    md_out.write_text("".join(md_parts), encoding="utf-8")

    logger.success(f"Consolidado CSV: {csv_out}")
    logger.success(f"Consolidado MD:  {md_out}")
    return {"csv": str(csv_out), "md": str(md_out)}
