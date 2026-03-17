"""Testes para o módulo de enriquecimento."""

import pandas as pd
from datetime import datetime

from finance_tracker.enrichment import enrich, _detect_tipo, _extract_estabelecimento


def _base_df() -> pd.DataFrame:
    return pd.DataFrame({
        "data": [pd.Timestamp("2026-02-01")],
        "valor": [-41.0],
        "descricao_normalizada": ["compra no debito - lancheria elkik"],
    })


def test_enrich_adds_date_columns():
    df = enrich(_base_df())
    assert df["ano"].iloc[0] == 2026
    assert df["mes"].iloc[0] == 2
    assert df["ano_mes"].iloc[0] == "2026-02"
    assert df["dia_semana"].iloc[0] == "Sunday"
    assert df["dia_mes"].iloc[0] == 1


def test_enrich_adds_valor_abs():
    df = enrich(_base_df())
    assert df["valor_abs"].iloc[0] == 41.0


def test_detect_tipo_debito():
    assert _detect_tipo("compra no debito - foo") == "debito"


def test_detect_tipo_pix():
    assert _detect_tipo("transferencia enviada pelo pix - joao") == "pix"


def test_detect_tipo_outro():
    assert _detect_tipo("algo desconhecido") == "outro"


def test_extract_estabelecimento_debito():
    result = _extract_estabelecimento("compra no debito - lancheria elkik")
    assert result == "lancheria elkik"


def test_extract_estabelecimento_pix():
    result = _extract_estabelecimento("transferencia enviada pelo pix - joao silva - cpf")
    assert result == "joao silva"
