"""Interface Streamlit para visualização e edição das análises financeiras."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from finance_tracker.analysis import (
    summary_by_category,
    summary_by_establishment,
    summary_by_month,
    recurring_transactions,
    month_over_month,
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

_DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
_DAY_PT = {
    "Monday": "Seg", "Tuesday": "Ter", "Wednesday": "Qua",
    "Thursday": "Qui", "Friday": "Sex", "Saturday": "Sáb", "Sunday": "Dom",
}


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
st.set_page_config(page_title="Finance Tracker — Nubank", page_icon="💰", layout="wide")
st.title("💰 Finance Tracker — Nubank")

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

# --- Tabs ---
tab_categorias, tab_mensal, tab_padroes, tab_estabelecimentos, tab_transacoes = st.tabs([
    "📊 Categorias",
    "📅 Evolução Mensal",
    "🔥 Padrões",
    "🏪 Estabelecimentos",
    "📋 Transações",
])


# ── Tab 1: Categorias ──────────────────────────────────────────────────────────
with tab_categorias:
    st.header("Gastos por categoria")
    cat_summary = summary_by_category(df)

    if not cat_summary.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(cat_summary, use_container_width=True, hide_index=True)
        with col2:
            fig = px.pie(
                cat_summary,
                names="categoria",
                values="total",
                hole=0.35,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum gasto no período selecionado.")


# ── Tab 2: Evolução Mensal ─────────────────────────────────────────────────────
with tab_mensal:
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
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(monthly, use_container_width=True, hide_index=True)

    st.divider()

    # Comparação mês a mês
    st.header("Comparação mês a mês")
    meses_disponiveis = sorted(df_cat["ano_mes"].unique())

    if len(meses_disponiveis) >= 2:
        col1, col2 = st.columns(2)
        with col1:
            mes_atual_mom = st.selectbox(
                "Mês atual", meses_disponiveis,
                index=len(meses_disponiveis) - 1, key="mom_atual"
            )
        with col2:
            opcoes_anterior = [m for m in meses_disponiveis if m < mes_atual_mom]
            mes_anterior_mom = st.selectbox(
                "Comparar com", opcoes_anterior,
                index=len(opcoes_anterior) - 1, key="mom_anterior"
            ) if opcoes_anterior else None

        if mes_anterior_mom:
            mom = month_over_month(df_cat, mes_atual_mom, mes_anterior_mom)

            mom_valido = mom.dropna(subset=["variacao_pct"])
            if not mom_valido.empty:
                mom_valido = mom_valido.copy()
                mom_valido["cor"] = mom_valido["variacao_pct"].apply(
                    lambda v: "Aumentou" if v > 0 else "Reduziu"
                )
                fig_mom = px.bar(
                    mom_valido.sort_values("variacao_pct"),
                    x="variacao_pct",
                    y="categoria",
                    orientation="h",
                    color="cor",
                    color_discrete_map={"Aumentou": "#e74c3c", "Reduziu": "#2ecc71"},
                    labels={"variacao_pct": "Variação (%)", "categoria": "", "cor": ""},
                    title=f"Variação por categoria: {mes_anterior_mom} → {mes_atual_mom}",
                )
                fig_mom.add_vline(x=0, line_dash="dash", line_color="gray")
                fig_mom.update_layout(showlegend=True)
                st.plotly_chart(fig_mom, use_container_width=True)

            mom_display = mom.copy()
            mom_display["variacao_pct"] = mom_display["variacao_pct"].map(
                lambda v: f"{v:+.1f}%" if pd.notna(v) else "novo"
            )
            mom_display["variacao_abs"] = mom_display["variacao_abs"].map(
                lambda v: f"R$ {v:+,.2f}"
            )
            st.dataframe(
                mom_display.rename(columns={
                    "categoria": "Categoria",
                    "anterior": f"{mes_anterior_mom} (R$)",
                    "atual": f"{mes_atual_mom} (R$)",
                    "variacao_abs": "Variação (R$)",
                    "variacao_pct": "Variação (%)",
                }),
                use_container_width=True, hide_index=True,
            )
    else:
        st.info("São necessários pelo menos 2 meses de dados para comparação.")


# ── Tab 3: Padrões ─────────────────────────────────────────────────────────────
with tab_padroes:
    st.header("Padrões de gasto")

    despesas = df[df["valor"] < 0].copy()

    if "dia_mes" not in despesas.columns:
        despesas["dia_mes"] = pd.to_datetime(despesas["data"], dayfirst=True).dt.day

    if not despesas.empty:
        col1, col2 = st.columns(2)

        with col1:
            pivot_semana = (
                despesas.groupby(["ano_mes", "dia_semana"])["valor_abs"]
                .sum()
                .unstack(fill_value=0)
                .reindex(columns=_DAY_ORDER, fill_value=0)
            )
            pivot_semana.columns = [_DAY_PT[d] for d in pivot_semana.columns]
            fig_semana = px.imshow(
                pivot_semana,
                labels={"x": "Dia da semana", "y": "Mês", "color": "R$"},
                color_continuous_scale="Reds",
                title="Gastos por dia da semana",
                text_auto=".0f",
                aspect="auto",
            )
            fig_semana.update_xaxes(side="bottom")
            st.plotly_chart(fig_semana, use_container_width=True)

        with col2:
            pivot_dia = (
                despesas.groupby(["ano_mes", "dia_mes"])["valor_abs"]
                .sum()
                .unstack(fill_value=0)
                .reindex(columns=list(range(1, 32)), fill_value=0)
            )
            fig_dia = px.imshow(
                pivot_dia,
                labels={"x": "Dia do mês", "y": "Mês", "color": "R$"},
                color_continuous_scale="Reds",
                title="Gastos por dia do mês",
                text_auto=".0f",
                aspect="auto",
            )
            fig_dia.update_xaxes(side="bottom", dtick=1)
            st.plotly_chart(fig_dia, use_container_width=True)

    st.divider()

    # Gastos recorrentes
    st.header("Gastos recorrentes")
    st.caption(
        "Estabelecimentos que aparecem em múltiplos meses. "
        "**Fixo** = valor praticamente constante. "
        "**Variável** = frequente mas com valor oscilando."
    )

    recorrentes = recurring_transactions(df_cat)

    if not recorrentes.empty:
        fixos = recorrentes[recorrentes["tipo"] == "fixo"]
        variaveis = recorrentes[recorrentes["tipo"] == "variavel"]

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Fixos (assinaturas e compromissos)")
            if not fixos.empty:
                total_fixo = fixos["media_mensal"].sum()
                st.metric("Comprometido por mês", f"R$ {total_fixo:,.2f}")
                st.dataframe(
                    fixos[["estabelecimento_normalizado", "categoria", "meses_presentes", "media_mensal"]]
                    .rename(columns={
                        "estabelecimento_normalizado": "estabelecimento",
                        "meses_presentes": "meses",
                        "media_mensal": "média/mês",
                    }),
                    use_container_width=True, hide_index=True,
                )
            else:
                st.info("Nenhum gasto fixo identificado.")

        with col2:
            st.subheader("Variáveis (hábitos regulares)")
            if not variaveis.empty:
                st.dataframe(
                    variaveis[["estabelecimento_normalizado", "categoria", "meses_presentes", "media_mensal", "coef_variacao"]]
                    .rename(columns={
                        "estabelecimento_normalizado": "estabelecimento",
                        "meses_presentes": "meses",
                        "media_mensal": "média/mês",
                        "coef_variacao": "variação",
                    }),
                    use_container_width=True, hide_index=True,
                )
            else:
                st.info("Nenhum hábito regular identificado.")
    else:
        st.info("Nenhum gasto recorrente identificado.")


# ── Tab 4: Estabelecimentos ────────────────────────────────────────────────────
with tab_estabelecimentos:
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
            st.dataframe(est_top, use_container_width=True, hide_index=True)
        with col2:
            fig = px.bar(
                est_top.sort_values("total"),
                x="total",
                y="estabelecimento_normalizado",
                orientation="h",
                labels={"total": "R$", "estabelecimento_normalizado": ""},
            )
            fig.update_layout(yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum dado de estabelecimento disponível.")


# ── Tab 5: Transações ──────────────────────────────────────────────────────────
with tab_transacoes:
    # Revisão manual
    st.header("Transações para revisão manual")
    review = df[df["revisao_manual"] == True].copy()

    if not review.empty:
        st.dataframe(
            review[["data", "descricao", "valor", "categoria", "estabelecimento_normalizado"]],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.success("Nenhuma transação aguardando revisão.")

    st.divider()

    # Todas as transações com edição
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
        use_container_width=True,
        hide_index=True,
        key="transaction_editor",
    )

    changed_mask = edited["categoria"] != df_display["categoria"]
    if changed_mask.any():
        changes = edited.loc[changed_mask, ["identificador", "categoria"]]
        save_overrides(changes)
        st.success(f"{changed_mask.sum()} categoria(s) atualizada(s).")
        st.rerun()
