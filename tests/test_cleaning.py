"""Testes para o módulo de limpeza."""

import pandas as pd
import pytest

from finance_tracker.cleaning import clean, _normalize_text


def _make_df(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def test_rename_columns():
    df = _make_df([{"Data": "01/02/2026", "Valor": "-10.00", "Identificador": "x", "Descrição": "Teste"}])
    result = clean(df)
    assert "data" in result.columns
    assert "valor" in result.columns
    assert "descricao" in result.columns


def test_parse_date():
    df = _make_df([{"Data": "15/03/2025", "Valor": "-5.00", "Identificador": "x", "Descrição": "Foo"}])
    result = clean(df)
    assert result["data"].dtype == "datetime64[ns]"
    assert result["data"].iloc[0].month == 3


def test_parse_value():
    df = _make_df([{"Data": "01/02/2026", "Valor": "-41.00", "Identificador": "x", "Descrição": "Foo"}])
    result = clean(df)
    assert result["valor"].iloc[0] == -41.0


def test_normalize_text_removes_accents():
    assert _normalize_text("Descrição") == "descricao"


def test_normalize_text_lowercases():
    assert _normalize_text("LANCHERIA ELKIK") == "lancheria elkik"


def test_normalize_text_collapses_spaces():
    assert _normalize_text("foo   bar") == "foo bar"
