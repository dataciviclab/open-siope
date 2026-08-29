"""Saldo — Enti in attivo vs passivo per regione/comparto."""

import streamlit as st
from lab_connectors.formatters import fmt_eur
from sources import query_bilancio, YEARS, get_comparti

st.title("⚖️ Saldo Bilancio")

# ── Filtri ──────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    year = st.selectbox("Anno", YEARS, index=len(YEARS) - 1)
with col2:
    raggruppa = st.selectbox("Raggruppa per", ["Regione", "Comparto", "Tipo Ente"])

# ── Query saldo ────────────────────────────────────────────────────
if raggruppa == "Regione":
    group_col = "regione"
elif raggruppa == "Comparto":
    group_col = "codice_comparto"
else:
    group_col = "tipo_ente"

df = query_bilancio(f"""
    SELECT
        {group_col} AS gruppo,
        SUM(CASE WHEN lato = 'entrate' THEN importo_eur ELSE 0 END) AS entrate,
        SUM(CASE WHEN lato = 'uscite' THEN importo_eur ELSE 0 END) AS uscite,
        SUM(CASE WHEN lato = 'entrate' THEN importo_eur ELSE 0 END)
            - SUM(CASE WHEN lato = 'uscite' THEN importo_eur ELSE 0 END) AS saldo,
        COUNT(DISTINCT codice_ente) AS nr_enti
    FROM clean_input
    WHERE anno = {year} AND {group_col} IS NOT NULL
    GROUP BY gruppo
    ORDER BY saldo
""", years=(year,))

if df.empty:
    st.warning("Nessun dato disponibile.")
    st.stop()

# ── KPI sommari ────────────────────────────────────────────────────
nr_in_rosso = int((df["saldo"] < 0).sum())
nr_in_verde = int((df["saldo"] >= 0).sum())
tot_rosso = df.loc[df["saldo"] < 0, "saldo"].sum()
tot_verde = df.loc[df["saldo"] >= 0, "saldo"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("🔴 In passivo", f"{nr_in_rosso}")
col2.metric("💰 Tot. passivo", fmt_eur(abs(tot_rosso), compact=True))
col3.metric("🟢 In attivo", f"{nr_in_verde}")
col4.metric("💰 Tot. attivo", fmt_eur(tot_verde, compact=True))

# ── Bar chart saldo (rosso/verde) ─────────────────────────────────
st.subheader(f"Saldo per {raggruppa}")

try:
    import plotly.graph_objects as go

    colors = ["#e74c3c" if s < 0 else "#27ae60" for s in df["saldo"]]
    fig = go.Figure(
        go.Bar(
            x=df["gruppo"],
            y=df["saldo"] / 1e9,
            marker_color=colors,
            text=[f"€{s/1e9:+,.1f} mld" for s in df["saldo"]],
            textposition="outside",
        )
    )
    fig.update_layout(
        height=500,
        xaxis_title=raggruppa,
        yaxis_title="Saldo (mld €)",
        yaxis_tickformat=",.0f",
    )
    st.plotly_chart(fig, width='stretch')
except ImportError:
    st.info("Installa plotly per il grafico colorato.")
    df_display = df.set_index("gruppo")[["saldo"]] / 1e9
    st.bar_chart(df_display)

# ── Tabella dettaglio ─────────────────────────────────────────────
st.subheader("Dettaglio")

df["saldo_fmt"] = df["saldo"].apply(lambda x: fmt_eur(x, compact=True))
df["entrate_fmt"] = df["entrate"].apply(lambda x: fmt_eur(x, compact=True))
df["uscite_fmt"] = df["uscite"].apply(lambda x: fmt_eur(x, compact=True))

st.dataframe(
    df[["gruppo", "nr_enti", "entrate_fmt", "uscite_fmt", "saldo_fmt"]].rename(columns={
        "gruppo": raggruppa,
        "nr_enti": "Enti",
        "entrate_fmt": "Entrate",
        "uscite_fmt": "Uscite",
        "saldo_fmt": "Saldo",
    }),
    width='stretch',
    hide_index=True,
)