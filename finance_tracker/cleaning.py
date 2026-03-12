"""Limpeza e normalização do DataFrame da Nubank."""

import re
import unicodedata

import pandas as pd


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica todas as etapas de limpeza e retorna um novo DataFrame."""
    df = df.copy()
    df = _rename_columns(df)
    df = _parse_dates(df)
    df = _parse_values(df)
    df = _normalize_descriptions(df)
    return df


def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(
        columns={
            "Data": "data",
            "Valor": "valor",
            "Identificador": "identificador",
            "Descrição": "descricao",
        }
    )


def _parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")
    invalid = df["data"].isna().sum()
    if invalid:
        raise ValueError(f"{invalid} linha(s) com data inválida encontrada(s).")
    return df


def _parse_values(df: pd.DataFrame) -> pd.DataFrame:
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    invalid = df["valor"].isna().sum()
    if invalid:
        raise ValueError(f"{invalid} linha(s) com valor inválido encontrado(s).")
    return df


def _normalize_descriptions(df: pd.DataFrame) -> pd.DataFrame:
    df["descricao"] = df["descricao"].str.strip()
    df["descricao_normalizada"] = df["descricao"].apply(_normalize_text)
    return df


def _normalize_text(text: str) -> str:
    """Remove acentos, converte para minúsculas e colapsa espaços."""
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text
