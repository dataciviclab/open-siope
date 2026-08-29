"""Scheda Ente — Dettaglio singolo ente pubblico."""

import streamlit as st
from sources import query_bilancio, YEARS, get_comparti

st.title("🏛️ Scheda Ente")

# ── Ricerca ente ───────────────────────────────────────────────────
search = st.text_input("🔍 Cerca ente per nome", placeholder="es. COMUNE DI ROMA")

if not search:
    st.info("Inserisci il nome di un ente per visualizzare la scheda.")
    st.stop()

# Cerca enti che matchano
df_match = query_bilancio(f"""
    SELECT DISTINCT codice_ente, denominazione_ente, tipo_ente,
        codice_comparto, descrizione_comparto, regione, provincia
    FROM clean_input
    WHERE denominazione_ente ILIKE '%{search.replace("'", "''")}%'
    ORDER BY denominazione_ente
    LIMIT 20
""")

if df_match.empty:
    st.warning(f"Nessun ente trovato per '{search}'.")
    st.stop()

# Seleziona ente
ente_options = [f"{row['denominazione_ente']} ({row['codice_ente']})" for _, row in df_match.iterrows()]
selected = st.selectbox("Seleziona ente", ente_options)
codice_ente = selected.split("(")[-1].rstrip(")")

ente = df_match[df_match["codice_ente"] == codice_ente].iloc[0]

# ── Info ente ──────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Tipo", ente["tipo_ente"])
col2.metric("Comparto", ente["codice_comparto"])
col3.metric("Territorio", f"{ente['provincia']} ({ente['regione']})")

st.caption(f"Denominazione: **{ente['denominazione_ente']}** · Codice SIOPE: `{codice_ente}`")

# ── KPI bilancio ───────────────────────────────────────────────────
anno = st.selectbox("Anno", YEARS, index=len(YEARS) - 1)

df_kpi = query_bilancio(f"""
    SELECT
        SUM(CASE WHEN lato = 'entrate' THEN importo_eur ELSE 0 END) AS entrate,
        SUM(CASE WHEN lato = 'uscite' THEN importo_eur ELSE 0 END) AS uscite,
        SUM(CASE WHEN lato = 'entrate' THEN importo_eur ELSE 0 END)
            - SUM(CASE WHEN lato = 'uscite' THEN importo_eur ELSE 0 END) AS saldo,
        COUNT(DISTINCT codice_voce) AS nr_voci
    FROM clean_input
    WHERE codice_ente = '{codice_ente}' AND anno = {anno}
""", years=(anno,))

if df_kpi.empty:
    st.warning("Nessun dato bilancio per questo ente/anno.")
    st.stop()

row = df_kpi.iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Entrate", f"€ {row['entrate']/1e6:,.1f} mln")
col2.metric("💸 Uscite", f"€ {row['uscite']/1e6:,.1f} mln")
col3.metric("⚖️ Saldo", f"€ {row['saldo']/1e6:,.1f} mln")
col4.metric("📋 Voci", f"{int(row['nr_voci'])}")

# ── Breakdown voci bilancio ───────────────────────────────────────
st.subheader("Breakdown Voci Bilancio")

col1, col2 = st.columns(2)
with col1:
    lato_sel = st.radio("Lato", ["Entrate", "Uscite"], horizontal=True)

lato_val = "entrate" if lato_sel == "Entrate" else "uscite"

df_voci = query_bilancio(f"""
    SELECT
        codice_voce,
        descrizione_codice,
        COALESCE(macro_categoria, 'Altro') AS macro,
        SUM(importo_eur) AS totale
    FROM clean_input
    WHERE codice_ente = '{codice_ente}' AND anno = {anno} AND lato = '{lato_val}'
    GROUP BY codice_voce, descrizione_codice, macro
    ORDER BY totale DESC
""", years=(anno,))

if not df_voci.empty:
    try:
        import plotly.express as px

        # Top 15 voci per chart
        df_top = df_voci.head(15).copy()
        fig = px.bar(
            df_top,
            x="totale",
            y="descrizione_codice",
            color="macro",
            orientation="h",
            title=f"Top 15 Voci {lato_sel}",
            labels={"totale": "Importo (€)", "descrizione_codice": ""},
        )
        fig.update_layout(height=500, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, width='stretch')
    except ImportError:
        st.bar_chart(df_voci.set_index("descrizione_codice")["totale"])

    st.dataframe(df_voci, width='stretch', hide_index=True)

# ── Trend temporale ────────────────────────────────────────────────
st.subheader("Trend Temporale")

df_trend = query_bilancio(f"""
    SELECT
        anno,
        SUM(CASE WHEN lato = 'entrate' THEN importo_eur ELSE 0 END) AS entrate,
        SUM(CASE WHEN lato = 'uscite' THEN importo_eur ELSE 0 END) AS uscite
    FROM clean_input
    WHERE codice_ente = '{codice_ente}'
    GROUP BY anno
    ORDER BY anno
""")

if not df_trend.empty:
    df_trend_indexed = df_trend.set_index("anno")[["entrate", "uscite"]] / 1e6
    df_trend_indexed.columns = ["Entrate (mln)", "Uscite (mln)"]
    st.line_chart(df_trend_indexed)

# ── Confronto con enti simili ─────────────────────────────────────
st.subheader("Confronto con Enti Simili")

df_simili = query_bilancio(f"""
    SELECT
        b.codice_ente,
        b.denominazione_ente,
        SUM(CASE WHEN b.lato = 'entrate' THEN b.importo_eur ELSE 0 END) AS entrate,
        SUM(CASE WHEN b.lato = 'uscite' THEN b.importo_eur ELSE 0 END) AS uscite,
        SUM(CASE WHEN b.lato = 'entrate' THEN b.importo_eur ELSE 0 END)
            - SUM(CASE WHEN b.lato = 'uscite' THEN b.importo_eur ELSE 0 END) AS saldo
    FROM clean_input b
    WHERE b.anno = {anno}
        AND b.tipo_ente = '{ente['tipo_ente']}'
        AND b.codice_comparto = '{ente['codice_comparto']}'
    GROUP BY b.codice_ente, b.denominazione_ente
    HAVING COUNT(*) > 0
    ORDER BY entrate DESC
    LIMIT 20
""", years=(anno,))

if not df_simili.empty:
    # Evidenzia l'ente selezionato
    df_simili["highlight"] = df_simili["codice_ente"].apply(
        lambda x: "⭐ " + df_simili.loc[df_simili["codice_ente"] == x, "denominazione_ente"].iloc[0]
        if x == codice_ente else df_simili.loc[df_simili["codice_ente"] == x, "denominazione_ente"].iloc[0]
    )

    df_chart = df_simili.set_index("highlight")[["entrate", "uscite"]] / 1e6
    df_chart.columns = ["Entrate (mln)", "Uscite (mln)"]
    st.bar_chart(df_chart)
