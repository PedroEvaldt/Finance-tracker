"""Leitura e validação de arquivos CSV da Nubank."""

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {"Data", "Valor", "Identificador", "Descrição"}


def load_nubank_csv(filepath: str | Path) -> pd.DataFrame:
    """Lê um CSV da Nubank e retorna um DataFrame validado."""
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    try:
        df = pd.read_csv(path, encoding="utf-8", sep=",")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="latin-1", sep=",")

    _validate_columns(df, path)
    return df


def _validate_columns(df: pd.DataFrame, path: Path) -> None:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"Colunas obrigatórias ausentes em '{path.name}': {sorted(missing)}"
        )
