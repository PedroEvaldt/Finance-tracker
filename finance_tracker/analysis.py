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
    for col in ("receita", "despesa"):
        if col not in result.columns:
            result[col] = 0.0
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


def recurring_transactions(df: pd.DataFrame, min_months: int = 2) -> pd.DataFrame:
    """Detecta gastos recorrentes: estabelecimentos que aparecem em múltiplos meses.

    Classifica cada recorrente como:
    - fixo: coeficiente de variação <= 0.15 (valor praticamente igual todo mês)
    - variavel: coeficiente de variação > 0.15 (frequente mas com valor oscilando)
    """
    total_meses = df["ano_mes"].nunique()
    despesas = df[df["valor"] < 0].copy()

    stats = despesas.groupby("estabelecimento_normalizado").agg(
        categoria=("categoria", "first"),
        meses_presentes=("ano_mes", "nunique"),
        media_mensal=("valor_abs", "mean"),
        desvio=("valor_abs", "std"),
    ).reset_index()

    stats["total_meses"] = total_meses
    stats["coef_variacao"] = (stats["desvio"] / stats["media_mensal"]).fillna(0)
    stats["tipo"] = stats["coef_variacao"].apply(
        lambda cv: "fixo" if cv <= 0.15 else "variavel"
    )

    recorrentes = (
        stats[stats["meses_presentes"] >= min_months]
        .drop(columns="desvio")
        .sort_values(["meses_presentes", "media_mensal"], ascending=[False, False])
        .reset_index(drop=True)
    )
    return recorrentes
