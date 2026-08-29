"""Territorio — Analisi geografica per regione/provincia."""

import streamlit as st
from sources import query_bilancio, YEARS

st.title("🗺️ Territorio")

# ── Filtri ──────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    year = st.selectbox("Anno", YEARS, index=len(YEARS) - 1)
with col2:
    lato = st.selectbox("Lato", ["Entrate", "Uscite"])

lato_val = "entrate" if lato == "Entrate" else "uscite"

# ── Per regione ────────────────────────────────────────────────────
st.subheader(f"Totale {lato} per Regione")

df_reg = query_bilancio(f"""
    SELECT
        regione,
        SUM(importo_eur) AS totale,
        COUNT(DISTINCT codice_ente) AS nr_enti
    FROM clean_input
    WHERE anno = {year} AND lato = '{lato_val}'
    GROUP BY regione
    ORDER BY totale DESC
""", years=(year,))

if not df_reg.empty:
    st.bar_chart(df_reg.set_index("regione")["totale"])

# ── Drill-down provincia ───────────────────────────────────────────
st.subheader("Drill-down per Provincia")

regione = st.selectbox("Seleziona Regione", ["Tutte"] + sorted(df_reg["regione"].dropna().astype(str).tolist()) if not df_reg.empty else ["Tutte"])

regione_filter = f"AND regione = '{regione}'" if regione != "Tutte" else ""

df_prov = query_bilancio(f"""
    SELECT
        provincia,
        regione,
        SUM(importo_eur) AS totale,
        COUNT(DISTINCT codice_ente) AS nr_enti
    FROM clean_input
    WHERE anno = {year} AND lato = '{lato_val}'
    {regione_filter}
    GROUP BY provincia, regione
    ORDER BY totale DESC
""", years=(year,))

if not df_prov.empty:
    st.bar_chart(df_prov.set_index("provincia")["totale"])
    st.dataframe(df_prov, width='stretch', hide_index=True)

# ── Confronto anno vs anno ─────────────────────────────────────────
st.subheader("Confronto Anno vs Anno")

df_trend = query_bilancio(f"""
    SELECT
        anno,
        SUM(importo_eur) AS totale
    FROM clean_input
    WHERE lato = '{lato_val}'
    {regione_filter}
    GROUP BY anno
    ORDER BY anno
""")

if not df_trend.empty:
    st.line_chart(df_trend.set_index("anno")["totale"])
