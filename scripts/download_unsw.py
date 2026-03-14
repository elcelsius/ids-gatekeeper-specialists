# scripts/download_unsw.py
# ---------------------------------------------------------------------------
# Baixa o dataset UNSW-NB15 via Kaggle API.
#
# Pré-requisito:
#   pip install kaggle
#   Credencial em %USERPROFILE%\.kaggle\kaggle.json  (Windows)
#              ou ~/.kaggle/kaggle.json              (Linux/macOS)
#
# Dataset Kaggle: mrwellsdavid/unsw-nb15
#   Contém os 4 arquivos CSV originais do UNSW-NB15:
#     UNSW_NB15_training-set.csv   (~175 k linhas, usado como treino)
#     UNSW_NB15_testing-set.csv    (~82 k linhas,  usado como holdout)
#     UNSW-NB15_1.csv ... _4.csv   (dados brutos completos, ~2,5 M linhas)
#
# Uso:
#   python scripts/download_unsw.py
# ---------------------------------------------------------------------------
from __future__ import annotations

import os
from pathlib import Path

DEST = Path(r"data\raw\unsw")

# Identificador do dataset no Kaggle
KAGGLE_DATASET = "mrwellsdavid/unsw-nb15"


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)

    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError:
        raise ImportError(
            "Pacote 'kaggle' não encontrado.\n"
            "Instale com: pip install kaggle\n"
            "E configure a credencial em ~/.kaggle/kaggle.json"
        )

    api = KaggleApi()
    api.authenticate()
    print(f"Autenticação OK. Baixando dataset '{KAGGLE_DATASET}'…")

    api.dataset_download_files(
        dataset=KAGGLE_DATASET,
        path=str(DEST),
        unzip=True,
    )

    arquivos = list(DEST.glob("*.csv"))
    print(f"\n[OK] Download concluído. Arquivos em: {DEST}")
    for f in sorted(arquivos):
        size_mb = f.stat().st_size / (1024 ** 2)
        print(f"     {f.name:50s}  {size_mb:7.1f} MB")

    print()
    print("Próximo passo: python scripts/prep_unsw_binary.py")


if __name__ == "__main__":
    main()
