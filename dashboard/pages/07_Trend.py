"""Trend — Andamento mensile/annuale con dati raw (entrate/uscite)."""

import streamlit as st
from sources import query_entrate, query_uscite, YEARS

st.title("📈 Trend")

# ── Filtri ──────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    lato = st.selectbox("Lato", ["Entrate", "Uscite"])
with col2:
    view = st.selectbox("Vista", ["Mensile", "Annuale"])

lato_val = "entrate" if lato == "Entrate" else "uscite"
query_fn = query_entrate if lato_val == "entrate" else query_uscite

# ── Trend annuale ──────────────────────────────────────────────────
st.subheader(f"Trend Annuale — {lato}")

df_annuale = query_fn("""
    SELECT anno, SUM(importo_eur) AS totale
    FROM clean_input
    GROUP BY anno
    ORDER BY anno
""")

if not df_annuale.empty:
    st.line_chart(df_annuale.set_index("anno")["totale"] / 1e9)

# ── Trend mensile (anno selezionato) ──────────────────────────────
st.subheader(f"Trend Mensile — {lato}")

year_sel = st.selectbox("Anno", YEARS, index=len(YEARS) - 1)

df_mensile = query_fn(f"""
    SELECT
        LPAD(periodo, 2, '0') AS mese,
        SUM(importo_eur) AS totale
    FROM clean_input
    WHERE anno = {year_sel}
    GROUP BY mese
    ORDER BY mese
""", years=(year_sel,))

if not df_mensile.empty:
    st.bar_chart(df_mensile.set_index("mese")["totale"] / 1e9)

# ── Confronto mensile anno vs anno ────────────────────────────────
st.subheader("Confronto Mensile Anno vs Anno")

df_confronto = query_fn("""
    SELECT
        anno,
        LPAD(periodo, 2, '0') AS mese,
        SUM(importo_eur) AS totale
    FROM clean_input
    GROUP BY anno, mese
    ORDER BY anno, mese
""")

if not df_confronto.empty:
    import pandas as pd
    pivot = df_confronto.pivot(index="mese", columns="anno", values="totale") / 1e9
    st.line_chart(pivot)

# ── Trend per comparto ────────────────────────────────────────────
st.subheader("Trend per Comparto")

df_comparti = query_fn("""
    SELECT
        anno,
        codice_comparto,
        SUM(importo_eur) AS totale
    FROM clean_input
    GROUP BY anno, codice_comparto
    ORDER BY anno, codice_comparto
""")

if not df_comparti.empty:
    import pandas as pd
    pivot = df_comparti.pivot(index="anno", columns="codice_comparto", values="totale") / 1e9
    st.line_chart(pivot)
