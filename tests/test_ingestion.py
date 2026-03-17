"""Testes para o módulo de ingestão."""

import pytest
import pandas as pd
from pathlib import Path
from io import StringIO

from finance_tracker.ingestion import load_nubank_csv, load_multiple_nubank_csvs, REQUIRED_COLUMNS


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


# --- load_multiple_nubank_csvs ---

VALID_CSV_2 = "Data,Valor,Identificador,Descrição\n02/02/2026,-20.00,def456,Compra no débito - MERCADO\n"
VALID_CSV_DUPLICATE = "Data,Valor,Identificador,Descrição\n01/02/2026,-41.00,abc123,Compra no débito - LANCHERIA\n"


def test_load_multiple_concatenates_files(tmp_path):
    f1 = tmp_path / "jan.csv"
    f2 = tmp_path / "fev.csv"
    f1.write_text(VALID_CSV, encoding="utf-8")
    f2.write_text(VALID_CSV_2, encoding="utf-8")
    df = load_multiple_nubank_csvs([f1, f2])
    assert len(df) == 2
    assert set(df["Identificador"]) == {"abc123", "def456"}


def test_load_multiple_deduplicates_by_identificador(tmp_path):
    f1 = tmp_path / "jan.csv"
    f2 = tmp_path / "jan_copia.csv"
    f1.write_text(VALID_CSV, encoding="utf-8")
    f2.write_text(VALID_CSV_DUPLICATE, encoding="utf-8")
    df = load_multiple_nubank_csvs([f1, f2])
    assert len(df) == 1
    assert df.iloc[0]["Identificador"] == "abc123"


def test_load_multiple_raises_if_file_missing(tmp_path):
    f1 = tmp_path / "jan.csv"
    f1.write_text(VALID_CSV, encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        load_multiple_nubank_csvs([f1, tmp_path / "nao_existe.csv"])
