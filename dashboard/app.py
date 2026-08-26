#!/usr/bin/env python3
"""
SIOPE · Dashboard Streamlit
Bilancio della PA italiana — entrate, uscite, saldi per ente e voce SIOPE.
"""

import streamlit as st

st.set_page_config(
    page_title="SIOPE · Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = {
    "": [
        st.Page("pages/01_Panoramica.py", title="Panoramica", icon="📊", default=True),
    ],
    "Analisi": [
        st.Page("pages/02_Enti.py", title="Enti", icon="🏛️"),
        st.Page("pages/03_Territorio.py", title="Territorio", icon="🗺️"),
        st.Page("pages/04_Voci_Bilancio.py", title="Voci Bilancio", icon="📋"),
        st.Page("pages/05_Trend.py", title="Trend", icon="📈"),
    ],
    "Strumenti": [
        st.Page("pages/06_SQL.py", title="Query SQL", icon="🧪"),
    ],
}

pg = st.navigation(pages, position="sidebar")

st.sidebar.markdown("---")
st.sidebar.caption("Dati: [SIOPE Open Data](https://www.siope.it/) · MEF")
st.sidebar.caption("Codice: [dataciviclab/open-siope](https://github.com/dataciviclab/open-siope)")
st.sidebar.caption("[DataCivicLab](https://dataciviclab.org/) · CC BY 4.0")

pg.run()
