"""Voci Bilancio — Analisi per codice voce SIOPE."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from sources import query_bilancio, query_entrate, query_uscite, YEARS

st.title("📋 Voci Bilancio")

# ── Filtri ──────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    year = st.selectbox("Anno", YEARS, index=len(YEARS) - 1)
with col2:
    lato = st.selectbox("Lato", ["Entrate", "Uscite"])

lato_val = "entrate" if lato == "Entrate" else "uscite"
macro_col = "macro_categoria"

# ── Top macro categorie ────────────────────────────────────────────
st.subheader(f"Top Macro Categorie — {lato}")

df_macro = query_bilancio(f"""
    SELECT
        COALESCE({macro_col}, 'Altro') AS macro,
        SUM(importo_eur) AS totale
    FROM clean_input
    WHERE anno = {year} AND lato = '{lato_val}'
    GROUP BY macro
    ORDER BY totale DESC
""", years=(year,))

if not df_macro.empty:
    # Treemap via plotly
    try:
        import plotly.express as px
        fig = px.treemap(df_macro, path=["macro"], values="totale", title="Macro Categorie")
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        st.bar_chart(df_macro.set_index("macro")["totale"])

# ── Dettaglio voci ─────────────────────────────────────────────────
st.subheader("Dettaglio Voci")

if not df_macro.empty:
    selected_macro = st.multiselect(
        "Filtra per macro categoria",
        df_macro["macro"].tolist(),
        default=df_macro["macro"].head(3).tolist(),
    )
else:
    selected_macro = []

macro_in = ""
if selected_macro:
    values_sql = ", ".join(f"'{m.replace(chr(39), chr(39)*2)}'" for m in selected_macro)
    macro_in = f"AND COALESCE({macro_col}, 'Altro') IN ({values_sql})"
df_voci = query_bilancio(f"""
    SELECT
        codice_voce,
        descrizione_codice,
        COALESCE({macro_col}, 'Altro') AS macro,
        SUM(importo_eur) AS totale
    FROM clean_input
    WHERE anno = {year} AND lato = '{lato_val}'
    {macro_in}
    GROUP BY codice_voce, descrizione_codice, macro
    ORDER BY totale DESC
    LIMIT 50
""", years=(year,))

if not df_voci.empty:
    st.dataframe(df_voci, use_container_width=True, hide_index=True)

# ── Trend per macro categoria ──────────────────────────────────────
st.subheader("Trend per Macro Categoria")

if not df_macro.empty:
    top3 = df_macro["macro"].head(3).tolist()
    escaped = [m.replace("'", "''") for m in top3]
    values_sql_3 = ", ".join(f"'{m.replace(chr(39), chr(39)*2)}'" for m in top3)
    macro_in_3 = f"AND COALESCE({macro_col}, 'Altro') IN ({values_sql_3})"
    df_trend = query_bilancio(f"""
        SELECT
            anno,
            COALESCE({macro_col}, 'Altro') AS macro,
            SUM(importo_eur) AS totale
        FROM clean_input
        WHERE lato = '{lato_val}'
        {macro_in_3}
        GROUP BY anno, macro
        ORDER BY anno, macro
    """)

    if not df_trend.empty:
        pivot = df_trend.pivot(index="anno", columns="macro", values="totale")
        st.line_chart(pivot)
