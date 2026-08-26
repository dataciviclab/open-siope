"""Trend — Andamento mensile/annuale."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from sources import query_bilancio, YEARS

st.title("📈 Trend")

# ── Filtri ──────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    lato = st.selectbox("Lato", ["Entrate", "Uscite"])
with col2:
    view = st.selectbox("Vista", ["Mensile", "Annuale"])

lato_val = "entrate" if lato == "Entrate" else "uscite"

# ── Trend annuale ──────────────────────────────────────────────────
st.subheader(f"Trend Annuale — {lato}")

df_annuale = query_bilancio(f"""
    SELECT
        anno,
        SUM(importo_eur) AS totale
    FROM clean_input
    WHERE lato = '{lato_val}'
    GROUP BY anno
    ORDER BY anno
""")

if not df_annuale.empty:
    st.line_chart(df_annuale.set_index("anno")["totale"])

# ── Trend mensile (anno selezionato) ──────────────────────────────
if view == "Mensile":
    st.subheader(f"Trend Mensile — {lato}")

    year_sel = st.selectbox("Anno", YEARS, index=len(YEARS) - 1)

    df_mensile = query_bilancio(f"""
        SELECT
            periodo,
            SUM(importo_eur) AS totale
        FROM clean_input
        WHERE anno = {year_sel} AND lato = '{lato_val}'
        GROUP BY periodo
        ORDER BY periodo
    """, years=(year_sel,))

    if not df_mensile.empty:
        st.bar_chart(df_mensile.set_index("periodo")["totale"])

    # ── Confronto mensile anno vs anno ─────────────────────────────
    st.subheader("Confronto Mensile Anno vs Anno")

    df_confronto = query_bilancio(f"""
        SELECT
            anno,
            periodo,
            SUM(importo_eur) AS totale
        FROM clean_input
        WHERE lato = '{lato_val}'
        GROUP BY anno, periodo
        ORDER BY anno, periodo
    """)

    if not df_confronto.empty:
        import pandas as pd
        pivot = df_confronto.pivot(index="periodo", columns="anno", values="totale")
        st.line_chart(pivot)

# ── Trend per comparto ────────────────────────────────────────────
st.subheader("Trend per Comparto")

df_comparti = query_bilancio(f"""
    SELECT
        anno,
        codice_comparto,
        SUM(importo_eur) AS totale
    FROM clean_input
    WHERE lato = '{lato_val}'
    GROUP BY anno, codice_comparto
    ORDER BY anno, codice_comparto
""")

if not df_comparti.empty:
    import pandas as pd
    pivot = df_comparti.pivot(index="anno", columns="codice_comparto", values="totale")
    st.line_chart(pivot)
