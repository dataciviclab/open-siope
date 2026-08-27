"""Panoramica — KPI e sunburst del bilancio SIOPE."""

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
col2.metric("💰 Entrate", f"€ {row['tot_entrate']/1e9:,.1f} mld")
col3.metric("💸 Uscite", f"€ {row['tot_uscite']/1e9:,.1f} mld")
col4.metric("📊 Saldo", f"€ {row['saldo']/1e9:,.1f} mld")

# ── Sunburst: Comparto → Tipo Ente (Entrate) ──────────────────────
st.subheader("🌅 Distribuzione Entrate — Comparto → Tipo Ente")

df_sun = query_bilancio(f"""
    SELECT
        codice_comparto,
        tipo_ente,
        SUM(importo_eur) AS totale
    FROM clean_input
    WHERE anno = {year} AND lato = 'entrate'
    GROUP BY codice_comparto, tipo_ente
    ORDER BY totale DESC
""", years=(year,))

if not df_sun.empty:
    try:
        import plotly.express as px

        # Etichette leggibili per comparto
        df_sun["comparto_label"] = df_sun["codice_comparto"]
        fig = px.sunburst(
            df_sun,
            path=["comparto_label", "tipo_ente"],
            values="totale",
            color="comparto_label",
            title="Entrate per Comparto e Tipo Ente",
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        st.info("Installa plotly per il sunburst: `pip install plotly`")

# ── Entrate vs Uscite per comparto (bar chart) ────────────────────
st.subheader("Entrate vs Uscite per Comparto")

df_comparti = query_bilancio(f"""
    SELECT
        codice_comparto,
        SUM(CASE WHEN lato = 'entrate' THEN importo_eur ELSE 0 END) AS entrate,
        SUM(CASE WHEN lato = 'uscite' THEN importo_eur ELSE 0 END) AS uscite
    FROM clean_input
    WHERE anno = {year}
    GROUP BY codice_comparto
    ORDER BY entrate DESC
""", years=(year,))

if not df_comparti.empty:
    df_chart = df_comparti.set_index("codice_comparto")[["entrate", "uscite"]] / 1e9
    df_chart.columns = ["Entrate (mld)", "Uscite (mld)"]
    st.bar_chart(df_chart)

# ── Titolo 9 — Split Payment ──────────────────────────────────────
st.subheader("📑 Titolo 9 — Ritenute e Split Payment")

df_t9 = query_bilancio(f"""
    SELECT
        codice_comparto,
        SUM(importo_eur) AS totale_t9,
        COUNT(DISTINCT codice_ente) AS enti
    FROM clean_input
    WHERE anno = {year} AND lato = 'entrate' AND is_titolo_9 = true
    GROUP BY codice_comparto
    ORDER BY totale_t9 DESC
""", years=(year,))

if not df_t9.empty:
    tot_t9 = df_t9["totale_t9"].sum()
    pct = tot_t9 / row["tot_entrate"] * 100 if row["tot_entrate"] else 0

    col1, col2 = st.columns(2)
    col1.metric("Totale Titolo 9", f"€ {tot_t9/1e9:,.1f} mld")
    col2.metric("% sul totale entrate", f"{pct:.1f}%")

    st.caption(
        "Le voci del Titolo 9 comprendono ritenute erariali, scissione contabile IVA "
        "(split payment) e ritenute per conto terzi — sono importi che transitano "
        "dall'ente ma non ne rappresentano un真正的 entrata."
    )

    df_t9_chart = df_t9.set_index("codice_comparto")["totale_t9"] / 1e9
    df_t9_chart.name = "Titolo 9 (mld)"
    st.bar_chart(df_t9_chart)
