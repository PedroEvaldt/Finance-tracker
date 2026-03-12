"""Interface Streamlit para visualização das análises financeiras."""

from pathlib import Path

import pandas as pd
import streamlit as st

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "output"


def load(filename: str) -> pd.DataFrame | None:
    path = OUTPUT_DIR / filename
    if not path.exists():
        return None
    return pd.read_csv(path)


st.set_page_config(page_title="Finance Tracker", layout="wide")
st.title("Finance Tracker — Nubank")

df_cat = load("transactions_categorized.csv")

if df_cat is None:
    st.warning(
        "Nenhum dado processado encontrado. Execute a pipeline primeiro via `main.py`."
    )
    st.stop()

# --- Resumo por categoria ---
st.header("Gastos por categoria")
cat_summary = load("category_summary.csv")
if cat_summary is not None:
    st.dataframe(cat_summary, use_container_width=True)
    st.bar_chart(cat_summary.set_index("categoria")["total"])

# --- Resumo mensal ---
st.header("Resumo mensal")
monthly = load("monthly_summary.csv")
if monthly is not None:
    st.dataframe(monthly, use_container_width=True)

# --- Transações para revisão ---
st.header("Transações para revisão manual")
review = load("review_needed.csv")
if review is not None and not review.empty:
    st.dataframe(review, use_container_width=True)
else:
    st.success("Nenhuma transação aguardando revisão.")

# --- Tabela completa ---
st.header("Todas as transações")
st.dataframe(df_cat, use_container_width=True)
