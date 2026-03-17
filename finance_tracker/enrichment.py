"""Criação de colunas derivadas para enriquecer o DataFrame."""

import re

import pandas as pd

_TIPO_PATTERNS = [
    (r"compra no debito", "debito"),
    (r"pix", "pix"),
    (r"transferencia", "transferencia"),
    (r"pagamento de fatura", "fatura"),
    (r"resgate|aplicacao|investimento", "investimento"),
]


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Adiciona colunas derivadas ao DataFrame limpo."""
    df = df.copy()
    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month
    df["ano_mes"] = df["data"].dt.to_period("M").astype(str)
    df["dia_semana"] = df["data"].dt.day_name()
    df["dia_mes"] = df["data"].dt.day
    df["valor_abs"] = df["valor"].abs()
    df["tipo_movimentacao"] = df["descricao_normalizada"].apply(_detect_tipo)
    df["estabelecimento_normalizado"] = df["descricao_normalizada"].apply(
        _extract_estabelecimento
    )
    return df


def _detect_tipo(descricao: str) -> str:
    for pattern, tipo in _TIPO_PATTERNS:
        if re.search(pattern, descricao):
            return tipo
    return "outro"


def _extract_estabelecimento(descricao: str) -> str:
    """Extrai o nome do estabelecimento da descrição normalizada."""
    # Remove prefixos comuns da Nubank
    prefixes = [
        r"compra no debito\s*-\s*",
        r"transferencia enviada pelo pix\s*-\s*",
        r"transferencia recebida pelo pix\s*-\s*",
        r"pagamento de fatura\s*-\s*",
    ]
    result = descricao
    for prefix in prefixes:
        result = re.sub(prefix, "", result, flags=re.IGNORECASE)

    # Pega apenas a primeira parte antes de " - " (nome do estabelecimento/pessoa)
    parts = result.split(" - ")
    return parts[0].strip()
