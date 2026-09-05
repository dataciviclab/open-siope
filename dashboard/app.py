#!/usr/bin/env python3
"""
SIOPE · Dashboard Streamlit
Bilancio della PA italiana — entrate, uscite, saldi per ente e voce SIOPE.
"""

import streamlit as st
from lab_connectors.branding import apply_branding

st.set_page_config(
    page_title="SIOPE · Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_branding(repo_name="open-siope", repo_url="https://github.com/dataciviclab/open-siope")

pages = {
    "": [
        st.Page("pages/01_Panoramica.py", title="Panoramica", icon="📊", default=True),
    ],
    "Analisi": [
        st.Page("pages/02_Scheda_Ente.py", title="Scheda Ente", icon="🏛️"),
        st.Page("pages/03_Enti.py", title="Top Enti", icon="📈"),
        st.Page("pages/04_Saldo.py", title="Saldo", icon="⚖️"),
        st.Page("pages/05_Territorio.py", title="Territorio", icon="🗺️"),
        st.Page("pages/06_Voci_Bilancio.py", title="Voci Bilancio", icon="📋"),
        st.Page("pages/07_Trend.py", title="Trend", icon="📉"),
    ],
    "Strumenti": [
        st.Page("pages/08_SQL.py", title="Query SQL", icon="🧪"),
    ],
}

pg = st.navigation(pages, position="sidebar")

pg.run()
