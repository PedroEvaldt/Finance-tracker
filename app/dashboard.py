"""Interface Streamlit para visualização e edição das análises financeiras."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from finance_tracker.analysis import (
    summary_by_category,
    summary_by_establishment,
    summary_by_month,
)

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "output"
OVERRIDES_PATH = OUTPUT_DIR / "category_overrides.csv"

CATEGORIAS = [
    "alimentacao",
    "mercado",
    "transporte",
    "moradia",
    "saude",
    "educacao",
    "lazer",
    "assinaturas",
    "transferencias",
    "receita",
    "investimentos",
    "outros",
]


def load(filename: str) -> pd.DataFrame | None:
    path = OUTPUT_DIR / filename
    if not path.exists():
        return None
    return pd.read_csv(path)


def load_overrides() -> pd.DataFrame:
    if not OVERRIDES_PATH.exists():
        return pd.DataFrame(columns=["identificador", "categoria"])
    return pd.read_csv(OVERRIDES_PATH)


def save_overrides(changes: pd.DataFrame) -> None:
    existing = load_overrides()
    combined = (
        pd.concat([existing, changes])
        .drop_duplicates(subset="identificador", keep="last")
        .reset_index(drop=True)
    )
    combined.to_csv(OVERRIDES_PATH, index=False)


def apply_overrides_to_df(df: pd.DataFrame, overrides: pd.DataFrame) -> pd.DataFrame:
    if overrides.empty:
        return df
    df = df.copy()
    override_map = overrides.set_index("identificador")["categoria"].to_dict()
    mask = df["identificador"].isin(override_map)
    df.loc[mask, "categoria"] = df.loc[mask, "identificador"].map(override_map)
    return df


# --- Configuração da página ---
st.set_page_config(page_title="Finance Tracker — Nubank", layout="wide")
st.title("Finance Tracker — Nubank")

# --- Carregamento dos dados ---
df_cat = load("transactions_categorized.csv")

if df_cat is None:
    st.warning("Nenhum dado processado encontrado. Execute a pipeline primeiro via `python main.py <csv>`.")
    st.stop()

overrides = load_overrides()
df_cat = apply_overrides_to_df(df_cat, overrides)

# --- Sidebar: filtro por mês ---
st.sidebar.header("Filtros")
meses = sorted(df_cat["ano_mes"].unique(), reverse=True)
mes_selecionado = st.sidebar.selectbox("Mês", ["Todos"] + list(meses))

df = df_cat if mes_selecionado == "Todos" else df_cat[df_cat["ano_mes"] == mes_selecionado]

# --- Métricas do período ---
total_receita = df[df["valor"] > 0]["valor"].sum()
total_despesas = df[df["valor"] < 0]["valor_abs"].sum()
saldo = total_receita - total_despesas

col1, col2, col3 = st.columns(3)
col1.metric("Receita", f"R$ {total_receita:,.2f}")
col2.metric("Despesas", f"R$ {total_despesas:,.2f}")
col3.metric("Saldo", f"R$ {saldo:,.2f}")

st.divider()

# --- Gastos por categoria ---
st.header("Gastos por categoria")
cat_summary = summary_by_category(df)

if not cat_summary.empty:
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(cat_summary, width="stretch", hide_index=True)
    with col2:
        fig = px.pie(
            cat_summary,
            names="categoria",
            values="total",
            hole=0.35,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")
else:
    st.info("Nenhum gasto no período selecionado.")

st.divider()

# --- Resumo mensal ---
st.header("Resumo mensal")
monthly = summary_by_month(df_cat)

if not monthly.empty:
    fig = px.bar(
        monthly,
        x="ano_mes",
        y=["receita", "despesa"],
        barmode="group",
        labels={"value": "R$", "ano_mes": "Mês", "variable": "Tipo"},
        color_discrete_map={"receita": "#2ecc71", "despesa": "#e74c3c"},
    )
    fig.update_layout(legend_title_text="")
    st.plotly_chart(fig, width="stretch")
    st.dataframe(monthly, width="stretch", hide_index=True)

st.divider()

# --- Gastos por estabelecimento ---
st.header("Gastos por estabelecimento")
est_summary = summary_by_establishment(df)

if not est_summary.empty:
    top_n = st.slider(
        "Exibir top N estabelecimentos",
        min_value=5,
        max_value=min(30, len(est_summary)),
        value=min(10, len(est_summary)),
    )
    est_top = est_summary.head(top_n)
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(est_top, width="stretch", hide_index=True)
    with col2:
        fig = px.bar(
            est_top.sort_values("total"),
            x="total",
            y="estabelecimento_normalizado",
            orientation="h",
            labels={"total": "R$", "estabelecimento_normalizado": ""},
        )
        fig.update_layout(yaxis_title=None)
        st.plotly_chart(fig, width="stretch")

st.divider()

# --- Transações para revisão ---
st.header("Transações para revisão manual")
review = df[df["revisao_manual"] == True].copy()

if not review.empty:
    st.dataframe(
        review[["data", "descricao", "valor", "categoria", "estabelecimento_normalizado"]],
        width="stretch",
        hide_index=True,
    )
else:
    st.success("Nenhuma transação aguardando revisão.")

st.divider()

# --- Todas as transações com edição de categoria ---
st.header("Todas as transações")
st.caption("Edite a coluna **categoria** diretamente na tabela. As alterações são salvas automaticamente.")

COLS_DISPLAY = [
    "data", "descricao", "valor", "categoria",
    "estabelecimento_normalizado", "tipo_movimentacao", "identificador",
]
df_display = df[COLS_DISPLAY].copy()

edited = st.data_editor(
    df_display,
    column_config={
        "data":                        st.column_config.TextColumn("Data", disabled=True),
        "descricao":                   st.column_config.TextColumn("Descrição", disabled=True),
        "valor":                       st.column_config.NumberColumn("Valor", disabled=True, format="R$ %.2f"),
        "categoria":                   st.column_config.SelectboxColumn("Categoria", options=CATEGORIAS, required=True),
        "estabelecimento_normalizado": st.column_config.TextColumn("Estabelecimento", disabled=True),
        "tipo_movimentacao":           st.column_config.TextColumn("Tipo", disabled=True),
        "identificador":               st.column_config.TextColumn("ID", disabled=True),
    },
    width="stretch",
    hide_index=True,
    key="transaction_editor",
)

changed_mask = edited["categoria"] != df_display["categoria"]
if changed_mask.any():
    changes = edited.loc[changed_mask, ["identificador", "categoria"]]
    save_overrides(changes)
    st.success(f"{changed_mask.sum()} categoria(s) atualizada(s).")
    st.rerun()
