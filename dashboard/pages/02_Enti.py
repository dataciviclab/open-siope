"""Enti — Top enti per entrate/uscite + scatter importo vs popolazione."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from sources import query_bilancio, YEARS, get_comparti

st.title("🏛️ Enti")

# ── Filtri ──────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    year = st.selectbox("Anno", YEARS, index=len(YEARS) - 1)
with col2:
    lato = st.selectbox("Lato", ["Entrate", "Uscite"])
with col3:
    top_n = st.slider("Top N", 5, 50, 20)

comparto_filter = ""
_comparti = get_comparti(year)
comparto = st.selectbox(
    "Comparto (opzionale)",
    ["Tutti"] + [c[0] for c in _comparti],
    format_func=lambda x: "Tutti" if x == "Tutti" else next(
        (f"{c[0]} — {c[1]}" for c in _comparti if c[0] == x), x
    ),
)
if comparto != "Tutti":
    comparto_filter = f"AND codice_comparto = '{comparto}'"

lato_val = "entrate" if lato == "Entrate" else "uscite"

# ── Tabella top enti ───────────────────────────────────────────────
df = query_bilancio(f"""
    SELECT
        denominazione_ente,
        tipo_ente,
        regione,
        provincia,
        SUM(importo_eur) AS totale
    FROM clean_input
    WHERE anno = {year} AND lato = '{lato_val}'
    {comparto_filter}
    GROUP BY denominazione_ente, tipo_ente, regione, provincia
    ORDER BY totale DESC
    LIMIT {top_n}
""", years=(year,))

if df.empty:
    st.warning("Nessun dato disponibile.")
    st.stop()

st.dataframe(df, use_container_width=True)

# ── Distribuzione per tipo ente ────────────────────────────────────
st.subheader("Distribuzione per Tipo Ente")

df_tipo = query_bilancio(f"""
    SELECT
        tipo_ente,
        SUM(importo_eur) AS totale,
        COUNT(DISTINCT codice_ente) AS nr_enti
    FROM clean_input
    WHERE anno = {year} AND lato = '{lato_val}'
    {comparto_filter}
    GROUP BY tipo_ente
    ORDER BY totale DESC
""", years=(year,))

if not df_tipo.empty:
    col1, col2 = st.columns(2)
    with col1:
        st.bar_chart(df_tipo.set_index("tipo_ente")["totale"] / 1e9)
    with col2:
        st.dataframe(df_tipo, use_container_width=True, hide_index=True)

# ── Scatter: Importo vs Popolazione (solo per COMUNE) ─────────────
st.subheader("📍 Importo vs Popolazione (Comuni)")

df_scatter = query_bilancio(f"""
    SELECT
        b.codice_ente,
        b.denominazione_ente,
        SUM(b.importo_eur) AS totale,
        TRY_CAST(e.popolazione AS INTEGER) AS popolazione
    FROM clean_input b
    LEFT JOIN read_parquet(
        'https://storage.googleapis.com/dataciviclab-clean/siope/siope_anag_enti_seed/2026/siope_anag_enti_seed_2026_clean.parquet'
    ) e ON b.codice_ente = e.codice_ente
    WHERE b.anno = {year} AND b.lato = '{lato_val}'
        AND b.tipo_ente = 'COMUNE'
        AND TRY_CAST(e.popolazione AS INTEGER) > 0
    GROUP BY b.codice_ente, b.denominazione_ente, popolazione
""", years=(year,))

if not df_scatter.empty:
    df_scatter["importo_per_abitante"] = df_scatter["totale"] / df_scatter["popolazione"]
    df_scatter["pop_migliaia"] = df_scatter["popolazione"] / 1000

    try:
        import plotly.express as px
        fig = px.scatter(
            df_scatter,
            x="pop_migliaia",
            y="importo_per_abitante",
            hover_name="denominazione_ente",
            size="totale",
            color="regione",
            title=f"Importo {lato} per abitante vs Popolazione",
            labels={
                "pop_migliaia": "Popolazione (migliaia)",
                "importo_per_abitante": f"{lato} per abitante (€)",
            },
            height=600,
        )
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        st.info("Installa plotly per lo scatter.")
        st.scatter_chart(df_scatter.set_index("pop_migliaia")["importo_per_abitante"])

