"""Geração de resumos analíticos a partir do DataFrame categorizado."""

import pandas as pd


def summary_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Resumo de gastos por categoria, apenas despesas."""
    despesas = df[df["valor"] < 0].copy()
    return (
        despesas.groupby("categoria")["valor_abs"]
        .sum()
        .reset_index()
        .rename(columns={"valor_abs": "total"})
        .sort_values("total", ascending=False)
    )


def summary_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """Resumo de receitas e despesas por mês."""
    result = (
        df.groupby(["ano_mes", df["valor"].apply(lambda v: "receita" if v > 0 else "despesa")])["valor_abs"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )
    result.columns.name = None
    return result


def summary_by_establishment(df: pd.DataFrame) -> pd.DataFrame:
    """Resumo de gastos por estabelecimento, apenas despesas."""
    despesas = df[df["valor"] < 0].copy()
    return (
        despesas.groupby("estabelecimento_normalizado")["valor_abs"]
        .sum()
        .reset_index()
        .rename(columns={"valor_abs": "total"})
        .sort_values("total", ascending=False)
    )


def transactions_for_review(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna transações marcadas para revisão manual."""
    return df[df["revisao_manual"]].copy()
