"""Enti — Top enti per entrate/uscite."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from sources import query_bilancio, YEARS

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
comparto = st.selectbox(
    "Comparto (opzionale)",
    ["Tutti", "PRO", "SAN", "UNI", "REG"],
    format_func=lambda x: {
        "Tutti": "Tutti",
        "PRO": "Province / Comuni",
        "SAN": "Sanità",
        "UNI": "Università",
        "REG": "Regioni",
    }.get(x, x),
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
    import pandas as pd
    col1, col2 = st.columns(2)
    with col1:
        st.bar_chart(df_tipo.set_index("tipo_ente")["totale"])
    with col2:
        st.dataframe(df_tipo, use_container_width=True, hide_index=True)
