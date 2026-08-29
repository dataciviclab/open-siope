"""Data sources for the SIOPE dashboard — wraps DuckDB + GCS."""

from __future__ import annotations

import streamlit as st
from pathlib import Path

from lab_connectors.duckdb.queries import (
    load_clean,
    load_mart_flat as _load_mart_flat,
    query_clean,
    years_from_registry,
)
from lab_connectors.registry import load_registry

PREFIX = "siope/"

_registry = load_registry(Path(__file__).parent.parent / "registry" / "registry.json")
_all_years = years_from_registry(_registry)
YEARS = list(range(min(_all_years), max(_all_years) + 1)) if _all_years else []

_registry_by_slug = {ds.slug: ds for ds in _registry.datasets}


# ── bilancio unificato ──────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner="Caricamento bilancio…")
def load_bilancio(years: tuple[int, ...] = tuple(YEARS)):
    return load_clean("siope_bilancio_unificato", list(years), prefix=PREFIX)


def query_bilancio(sql: str, years: tuple[int, ...] = tuple(YEARS)):
    return query_clean("siope_bilancio_unificato", sql, list(years), prefix=PREFIX)


# ── entrate ─────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner="Caricamento entrate…")
def load_entrate(years: tuple[int, ...] = tuple(YEARS)):
    return load_clean("siope_entrate", list(years), prefix=PREFIX)


def query_entrate(sql: str, years: tuple[int, ...] = tuple(YEARS)):
    return query_clean("siope_entrate", sql, list(years), prefix=PREFIX)


# ── uscite ──────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner="Caricamento uscite…")
def load_uscite(years: tuple[int, ...] = tuple(YEARS)):
    return load_clean("siope_uscite", list(years), prefix=PREFIX)


def query_uscite(sql: str, years: tuple[int, ...] = tuple(YEARS)):
    return query_clean("siope_uscite", sql, list(years), prefix=PREFIX)


# ── support seeds ───────────────────────────────────────────────────

_SEED_SLUGS = [
    "siope_anag_codgest_entrate_seed",
    "siope_anag_codgest_uscite_seed",
    "siope_anag_comparti_seed",
    "siope_anag_comuni_seed",
    "siope_anag_enti_seed",
    "siope_anag_reg_prov_seed",
    "siope_anag_sottocomparti_seed",
]


@st.cache_data(ttl=3600, show_spinner="Caricamento anagrafiche…")
def load_seeds():
    import pandas as pd

    frames = []
    for slug in _SEED_SLUGS:
        try:
            df = load_clean(slug, [2026], prefix=PREFIX)
            frames.append(df)
        except Exception:
            pass
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def get_comparti(year: int = 2026):
    """Return list of (codice, descrizione) for all comparti in the data."""
    df = query_bilancio("""
        SELECT DISTINCT codice_comparto, descrizione_comparto
        FROM clean_input
        WHERE codice_comparto IS NOT NULL
        ORDER BY codice_comparto
    """, years=(year,))
    return list(zip(df["codice_comparto"], df["descrizione_comparto"]))


def get_registry():
    return _registry


def get_registry_by_slug():
    return _registry_by_slug

