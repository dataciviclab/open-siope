"""Panoramica — KPI del bilancio SIOPE."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from sources import query_bilancio, YEARS, get_comparti

st.title("📊 Panoramica Bilancio SIOPE")

# ── Filtri ──────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    year = st.selectbox("Anno", YEARS, index=len(YEARS) - 1)
with col2:
    _comparti = get_comparti(year)
    comparto = st.selectbox(
        "Comparto",
        ["Tutti"] + [c[0] for c in _comparti],
        format_func=lambda x: "Tutti" if x == "Tutti" else next(
            (f"{c[0]} — {c[1]}" for c in _comparti if c[0] == x), x
        ),
    )

# ── KPI ─────────────────────────────────────────────────────────────
comparto_filter = f"AND codice_comparto = '{comparto}'" if comparto != "Tutti" else ""

df_kpi = query_bilancio(f"""
    SELECT
        COUNT(DISTINCT codice_ente) AS nr_enti,
        SUM(CASE WHEN lato = 'entrate' THEN importo_eur ELSE 0 END) AS tot_entrate,
        SUM(CASE WHEN lato = 'uscite' THEN importo_eur ELSE 0 END) AS tot_uscite,
        SUM(CASE WHEN lato = 'entrate' THEN importo_eur ELSE 0 END)
            - SUM(CASE WHEN lato = 'uscite' THEN importo_eur ELSE 0 END) AS saldo
    FROM clean_input
    WHERE anno = {year}
    {comparto_filter}
""", years=(year,))

if df_kpi.empty:
    st.warning("Nessun dato disponibile per l'anno selezionato.")
    st.stop()

row = df_kpi.iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("🏛️ Enti", f"{int(row['nr_enti']):,}")
col2.metric("💰 Entrate", f"€ {row['tot_entrate']:,.0f}")
col3.metric("💸 Uscite", f"€ {row['tot_uscite']:,.0f}")
col4.metric("📊 Saldo", f"€ {row['saldo']:,.0f}")

# ── Entrate vs Uscite per comparto ─────────────────────────────────
st.subheader("Entrate vs Uscite per Comparto")

df_comparti = query_bilancio(f"""
    SELECT
        descrizione_comparto,
        SUM(CASE WHEN lato = 'entrate' THEN importo_eur ELSE 0 END) AS entrate,
        SUM(CASE WHEN lato = 'uscite' THEN importo_eur ELSE 0 END) AS uscite
    FROM clean_input
    WHERE anno = {year}
    GROUP BY descrizione_comparto
    ORDER BY entrate DESC
""", years=(year,))

if not df_comparti.empty:
    import pandas as pd
    df_chart = df_comparti.set_index("descrizione_comparto")[["entrate", "uscite"]]
    st.bar_chart(df_chart)

# ── Top 10 macro categorie entrate ─────────────────────────────────
st.subheader("Top 10 Macro Categorie Entrate")

df_macro = query_bilancio(f"""
    SELECT
        COALESCE(macro_categoria, 'Altro') AS macro_categoria,
        SUM(importo_eur) AS totale
    FROM clean_input
    WHERE anno = {year} AND lato = 'entrate'
    GROUP BY macro_categoria
    ORDER BY totale DESC
    LIMIT 10
""", years=(year,))

if not df_macro.empty:
    st.bar_chart(df_macro.set_index("macro_categoria")["totale"])

# ── Top 10 macro categorie uscite ──────────────────────────────────
st.subheader("Top 10 Macro Categorie Uscite")

df_macro_usc = query_bilancio(f"""
    SELECT
        COALESCE(macro_categoria, 'Altro') AS macro_categoria,
        SUM(importo_eur) AS totale
    FROM clean_input
    WHERE anno = {year} AND lato = 'uscite'
    GROUP BY macro_categoria
    ORDER BY totale DESC
    LIMIT 10
""", years=(year,))

if not df_macro_usc.empty:
    st.bar_chart(df_macro_usc.set_index("macro_categoria")["totale"])
