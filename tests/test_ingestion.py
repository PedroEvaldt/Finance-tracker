"""Testes para o módulo de ingestão."""

import pytest
import pandas as pd
from pathlib import Path
from io import StringIO

from finance_tracker.ingestion import load_nubank_csv, REQUIRED_COLUMNS


VALID_CSV = "Data,Valor,Identificador,Descrição\n01/02/2026,-41.00,abc123,Compra no débito - LANCHERIA\n"


def test_load_valid_csv(tmp_path):
    f = tmp_path / "test.csv"
    f.write_text(VALID_CSV, encoding="utf-8")
    df = load_nubank_csv(f)
    assert set(df.columns) == REQUIRED_COLUMNS


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_nubank_csv("/nao/existe.csv")


def test_missing_column(tmp_path):
    f = tmp_path / "bad.csv"
    f.write_text("Data,Valor\n01/02/2026,-10.00\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Colunas obrigatórias ausentes"):
        load_nubank_csv(f)
