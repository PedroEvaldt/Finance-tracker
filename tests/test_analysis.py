"""Testes para o módulo de análise."""

import pandas as pd
import pytest

from finance_tracker.analysis import (
    summary_by_category,
    summary_by_establishment,
    summary_by_month,
    transactions_for_review,
    recurring_transactions,
)


@pytest.fixture
def df_sample() -> pd.DataFrame:
    return pd.DataFrame([
        {"valor": -50.0,  "valor_abs": 50.0,  "categoria": "alimentacao", "estabelecimento_normalizado": "kampeki",          "ano_mes": "2026-02", "revisao_manual": False},
        {"valor": -30.0,  "valor_abs": 30.0,  "categoria": "alimentacao", "estabelecimento_normalizado": "ifood",             "ano_mes": "2026-02", "revisao_manual": False},
        {"valor": -100.0, "valor_abs": 100.0, "categoria": "mercado",     "estabelecimento_normalizado": "zaffari",           "ano_mes": "2026-02", "revisao_manual": False},
        {"valor": 1600.0, "valor_abs": 1600.0,"categoria": "receita",     "estabelecimento_normalizado": "transferencia pix", "ano_mes": "2026-02", "revisao_manual": False},
        {"valor": -20.0,  "valor_abs": 20.0,  "categoria": "outros",      "estabelecimento_normalizado": "loja desconhecida", "ano_mes": "2026-02", "revisao_manual": True},
    ])


# --- summary_by_category ---

def test_summary_by_category_soma_por_categoria(df_sample):
    result = summary_by_category(df_sample)
    totais = result.set_index("categoria")["total"]
    assert totais["alimentacao"] == pytest.approx(80.0)
    assert totais["mercado"] == pytest.approx(100.0)


def test_summary_by_category_exclui_receitas(df_sample):
    result = summary_by_category(df_sample)
    assert "receita" not in result["categoria"].values


def test_summary_by_category_ordenado_decrescente(df_sample):
    result = summary_by_category(df_sample)
    totais = result["total"].tolist()
    assert totais == sorted(totais, reverse=True)


def test_summary_by_category_colunas_corretas(df_sample):
    result = summary_by_category(df_sample)
    assert list(result.columns) == ["categoria", "total"]


def test_summary_by_category_sem_despesas():
    df = pd.DataFrame([
        {"valor": 1000.0, "valor_abs": 1000.0, "categoria": "receita",
         "estabelecimento_normalizado": "pix", "ano_mes": "2026-02", "revisao_manual": False},
    ])
    result = summary_by_category(df)
    assert result.empty


# --- summary_by_month ---

def test_summary_by_month_separa_receita_e_despesa(df_sample):
    result = summary_by_month(df_sample)
    assert "receita" in result.columns
    assert "despesa" in result.columns


def test_summary_by_month_valores_corretos(df_sample):
    result = summary_by_month(df_sample)
    row = result[result["ano_mes"] == "2026-02"].iloc[0]
    assert row["receita"] == pytest.approx(1600.0)
    assert row["despesa"] == pytest.approx(200.0)  # 50 + 30 + 100 + 20


def test_summary_by_month_multiplos_meses():
    df = pd.DataFrame([
        {"valor": -50.0,  "valor_abs": 50.0,  "ano_mes": "2026-01"},
        {"valor": 1000.0, "valor_abs": 1000.0, "ano_mes": "2026-01"},
        {"valor": -80.0,  "valor_abs": 80.0,  "ano_mes": "2026-02"},
    ])
    result = summary_by_month(df)
    assert len(result) == 2
    assert set(result["ano_mes"]) == {"2026-01", "2026-02"}


def test_summary_by_month_preenche_zero_quando_ausente():
    df = pd.DataFrame([
        {"valor": -50.0, "valor_abs": 50.0, "ano_mes": "2026-01"},
    ])
    result = summary_by_month(df)
    row = result.iloc[0]
    assert row["despesa"] == pytest.approx(50.0)
    assert row["receita"] == pytest.approx(0.0)


# --- summary_by_establishment ---

def test_summary_by_establishment_soma_por_estabelecimento(df_sample):
    result = summary_by_establishment(df_sample)
    totais = result.set_index("estabelecimento_normalizado")["total"]
    assert totais["kampeki"] == pytest.approx(50.0)
    assert totais["zaffari"] == pytest.approx(100.0)


def test_summary_by_establishment_exclui_receitas(df_sample):
    result = summary_by_establishment(df_sample)
    assert "transferencia pix" not in result["estabelecimento_normalizado"].values


def test_summary_by_establishment_ordenado_decrescente(df_sample):
    result = summary_by_establishment(df_sample)
    totais = result["total"].tolist()
    assert totais == sorted(totais, reverse=True)


def test_summary_by_establishment_colunas_corretas(df_sample):
    result = summary_by_establishment(df_sample)
    assert list(result.columns) == ["estabelecimento_normalizado", "total"]


# --- transactions_for_review ---

def test_transactions_for_review_retorna_apenas_marcadas(df_sample):
    result = transactions_for_review(df_sample)
    assert len(result) == 1
    assert result.iloc[0]["estabelecimento_normalizado"] == "loja desconhecida"


def test_transactions_for_review_vazio_quando_nenhuma():
    df = pd.DataFrame([
        {"valor": -50.0, "valor_abs": 50.0, "categoria": "alimentacao",
         "estabelecimento_normalizado": "kampeki", "ano_mes": "2026-02", "revisao_manual": False},
    ])
    result = transactions_for_review(df)
    assert result.empty


def test_transactions_for_review_retorna_copia(df_sample):
    result = transactions_for_review(df_sample)
    result.iloc[0, result.columns.get_loc("categoria")] = "modificado"
    assert df_sample.loc[df_sample["revisao_manual"], "categoria"].iloc[0] != "modificado"


# --- recurring_transactions ---

@pytest.fixture
def df_recorrentes() -> pd.DataFrame:
    return pd.DataFrame([
        # medialane: 3 meses, valor fixo R$49.90
        {"valor": -49.90, "valor_abs": 49.90, "categoria": "assinaturas", "estabelecimento_normalizado": "medialane", "ano_mes": "2025-09", "revisao_manual": False},
        {"valor": -49.90, "valor_abs": 49.90, "categoria": "assinaturas", "estabelecimento_normalizado": "medialane", "ano_mes": "2025-10", "revisao_manual": False},
        {"valor": -49.90, "valor_abs": 49.90, "categoria": "assinaturas", "estabelecimento_normalizado": "medialane", "ano_mes": "2025-11", "revisao_manual": False},
        # kampeki: 2 meses, valor variável
        {"valor": -80.00, "valor_abs": 80.00, "categoria": "alimentacao", "estabelecimento_normalizado": "kampeki",  "ano_mes": "2025-09", "revisao_manual": False},
        {"valor": -120.00,"valor_abs": 120.00,"categoria": "alimentacao", "estabelecimento_normalizado": "kampeki",  "ano_mes": "2025-10", "revisao_manual": False},
        # loja unica: só 1 mês, não deve aparecer
        {"valor": -30.00, "valor_abs": 30.00, "categoria": "outros",      "estabelecimento_normalizado": "loja x",   "ano_mes": "2025-09", "revisao_manual": False},
        # receita: não deve aparecer (valor > 0)
        {"valor": 1600.0, "valor_abs": 1600.0,"categoria": "receita",     "estabelecimento_normalizado": "pix",      "ano_mes": "2025-09", "revisao_manual": False},
    ])


def test_recurring_retorna_apenas_multiplos_meses(df_recorrentes):
    result = recurring_transactions(df_recorrentes)
    assert set(result["estabelecimento_normalizado"]) == {"medialane", "kampeki"}
    assert "loja x" not in result["estabelecimento_normalizado"].values


def test_recurring_exclui_receitas(df_recorrentes):
    result = recurring_transactions(df_recorrentes)
    assert "pix" not in result["estabelecimento_normalizado"].values


def test_recurring_classifica_fixo(df_recorrentes):
    result = recurring_transactions(df_recorrentes)
    row = result[result["estabelecimento_normalizado"] == "medialane"].iloc[0]
    assert row["tipo"] == "fixo"


def test_recurring_classifica_variavel(df_recorrentes):
    result = recurring_transactions(df_recorrentes)
    row = result[result["estabelecimento_normalizado"] == "kampeki"].iloc[0]
    assert row["tipo"] == "variavel"


def test_recurring_min_months_parametro(df_recorrentes):
    result = recurring_transactions(df_recorrentes, min_months=3)
    assert set(result["estabelecimento_normalizado"]) == {"medialane"}


def test_recurring_colunas_corretas(df_recorrentes):
    result = recurring_transactions(df_recorrentes)
    expected = {"estabelecimento_normalizado", "categoria", "meses_presentes",
                "media_mensal", "total_meses", "coef_variacao", "tipo"}
    assert expected.issubset(set(result.columns))
