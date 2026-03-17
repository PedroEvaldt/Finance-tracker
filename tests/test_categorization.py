"""Testes para o módulo de categorização."""

import pandas as pd
import pytest
from pathlib import Path

from finance_tracker.categorization import categorize, apply_overrides, _classify


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


# --- apply_overrides ---

def make_categorized_df() -> pd.DataFrame:
    return pd.DataFrame({
        "identificador":       ["id-001", "id-002", "id-003"],
        "descricao":           ["Kampeki", "iFood", "Loja X"],
        "categoria":           ["alimentacao", "alimentacao", "outros"],
        "confianca_categoria": ["alta", "alta", "baixa"],
        "revisao_manual":      [False, False, True],
    })


def test_apply_overrides_altera_categoria(tmp_path):
    overrides = tmp_path / "overrides.csv"
    overrides.write_text("identificador,categoria\nid-003,lazer\n", encoding="utf-8")
    result = apply_overrides(make_categorized_df(), overrides_path=overrides)
    assert result.loc[2, "categoria"] == "lazer"


def test_apply_overrides_marca_confianca_manual(tmp_path):
    overrides = tmp_path / "overrides.csv"
    overrides.write_text("identificador,categoria\nid-003,lazer\n", encoding="utf-8")
    result = apply_overrides(make_categorized_df(), overrides_path=overrides)
    assert result.loc[2, "confianca_categoria"] == "manual"


def test_apply_overrides_desmarca_revisao_manual(tmp_path):
    overrides = tmp_path / "overrides.csv"
    overrides.write_text("identificador,categoria\nid-003,lazer\n", encoding="utf-8")
    result = apply_overrides(make_categorized_df(), overrides_path=overrides)
    assert result.loc[2, "revisao_manual"] == False


def test_apply_overrides_nao_afeta_outras_linhas(tmp_path):
    overrides = tmp_path / "overrides.csv"
    overrides.write_text("identificador,categoria\nid-003,lazer\n", encoding="utf-8")
    result = apply_overrides(make_categorized_df(), overrides_path=overrides)
    assert result.loc[0, "categoria"] == "alimentacao"
    assert result.loc[1, "categoria"] == "alimentacao"


def test_apply_overrides_sem_arquivo_retorna_df_original(tmp_path):
    overrides = tmp_path / "nao_existe.csv"
    df = make_categorized_df()
    result = apply_overrides(df, overrides_path=overrides)
    pd.testing.assert_frame_equal(result, df)


def test_apply_overrides_retorna_copia(tmp_path):
    overrides = tmp_path / "overrides.csv"
    overrides.write_text("identificador,categoria\nid-003,lazer\n", encoding="utf-8")
    df = make_categorized_df()
    apply_overrides(df, overrides_path=overrides)
    assert df.loc[2, "categoria"] == "outros"
