"""Query SQL — Interroga direttamente i dati SIOPE."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lab_connectors.duckdb.sql_page import render_sql_query
from sources import get_registry, PREFIX

render_sql_query(
    registry=get_registry(),
    prefix=PREFIX,
    default_slug="siope_bilancio_unificato",
    title="🧪 Query SQL",
    description="Interroga direttamente i dati SIOPE. Scrivi SQL su ``clean_input``.",
)
