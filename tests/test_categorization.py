"""Testes para o módulo de categorização."""

import pandas as pd
import pytest
from pathlib import Path

from finance_tracker.categorization import categorize, _classify


MOCK_RULES = {
    "alimentacao": ["lancheria", "restaurante"],
    "transporte": ["uber", "taxi"],
}


def test_classify_known_keyword():
    categoria, confianca = _classify("lancheria elkik", MOCK_RULES)
    assert categoria == "alimentacao"
    assert confianca == "alta"


def test_classify_unknown_returns_outros():
    categoria, confianca = _classify("pagamento desconhecido", MOCK_RULES)
    assert categoria == "outros"
    assert confianca == "baixa"


def test_categorize_sets_revisao_manual(tmp_path):
    config = tmp_path / "categories.yaml"
    config.write_text("alimentacao:\n  - lancheria\n", encoding="utf-8")

    df = pd.DataFrame({
        "descricao_normalizada": ["lancheria elkik", "coisa estranha"],
        "valor": [-10.0, -5.0],
    })
    result = categorize(df, config_path=config)

    assert result.loc[0, "categoria"] == "alimentacao"
    assert result.loc[0, "revisao_manual"] == False
    assert result.loc[1, "revisao_manual"] == True
