"""Client DuckDB per dati SIOPE su GCS pubblico.

Legge parquet direttamente dagli URL HTTPS dei bucket pubblici.
Non richiede autenticazione GCS — i bucket dataciviclab-clean
e dataciviclab-mart sono pubblici.

Ogni funzione usa una connessione DuckDB isolata per evitare
transactions abortite tra query successive.
"""

from __future__ import annotations

from typing import Any

import duckdb

GCS_CLEAN = "https://storage.googleapis.com/dataciviclab-clean/siope"
GCS_MART = "https://storage.googleapis.com/dataciviclab-mart/siope"

ANNI = [2021, 2022, 2023, 2024, 2025]

ENTI_URL = (
    f"{GCS_CLEAN}/siope_anag_enti_seed/2026/siope_anag_enti_seed_2026_clean.parquet"
)


def _query(sql: str) -> list[tuple]:
    """Esegue SQL su una connessione DuckDB isolata."""
    con = duckdb.connect()
    try:
        return con.sql(sql).fetchall()
    finally:
        con.close()


def _mart_url(lato: str, anno: int) -> str:
    return (
        f"{GCS_MART}/siope_{lato}_comuni/{anno}"
        f"/siope_{lato}_comuni_agg_labeled.parquet"
    )


def _clean_url(lato: str, anno: int) -> str:
    return (
        f"{GCS_CLEAN}/siope_{lato}_comuni/{anno}"
        f"/siope_{lato}_comuni_{anno}_clean.parquet"
    )


# ── Tool implementations ──────────────────────────────────────────────────


def cerca_ente(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """Cerca enti per denominazione (LIKE %query%)."""
    safe = query.replace("'", "''")
    rows = _query(
        f"""
        SELECT codice_ente, denominazione_ente, tipo_ente,
               codice_provincia, codice_istat_comune
        FROM read_parquet('{ENTI_URL}')
        WHERE data_fine = '9999-12-31'
          AND denominazione_ente ILIKE '%{safe}%'
        LIMIT {limit}
        """
    )
    cols = ["codice_ente", "denominazione", "tipo_ente", "provincia", "comune_istat"]
    return [dict(zip(cols, r)) for r in rows]


def get_bilancio(
    codice_ente: str, anno: int, lato: str
) -> dict[str, Any]:
    """Totale entrate/uscite per un ente in un anno (da CLEAN)."""
    url = _clean_url(lato, anno)
    row = _query(
        f"""
        SELECT count(*) as righe,
               count(DISTINCT codice_voce) as voci,
               sum(importo_eur) as totale_eur
        FROM read_parquet('{url}')
        WHERE codice_ente = '{codice_ente}'
          AND is_titolo_9 = false
        """
    )[0]
    return {
        "codice_ente": codice_ente,
        "anno": anno,
        "lato": lato,
        "righe": row[0],
        "voci": row[1],
        "totale_eur": round(row[2], 2) if row[2] else 0,
    }


def spesa_categoria(
    codice_ente: str, anno: int, lato: str
) -> list[dict[str, Any]]:
    """Breakdown per macro-categoria di un ente (da CLEAN)."""
    url = _clean_url(lato, anno)
    cat_col = "macro_categoria_v2" if lato == "entrate" else "macro_categoria"
    rows = _query(
        f"""
        SELECT {cat_col} as categoria,
               sum(importo_eur) as totale_eur,
               count(DISTINCT codice_voce) as voci
        FROM read_parquet('{url}')
        WHERE codice_ente = '{codice_ente}'
          AND is_titolo_9 = false
        GROUP BY categoria
        ORDER BY totale_eur DESC
        """
    )
    return [
        {"categoria": r[0], "totale_eur": round(r[1], 2), "voci": r[2]}
        for r in rows
    ]


def top_enti(
    anno: int, lato: str, comparto: str | None = None, limit: int = 10
) -> list[dict[str, Any]]:
    """Enti con maggiori entrate/uscite (da CLEAN)."""
    url = _clean_url(lato, anno)
    where = "AND is_titolo_9 = false"
    if comparto:
        where += f" AND codice_comparto = '{comparto}'"
    rows = _query(
        f"""
        SELECT codice_ente, denominazione_ente,
               sum(importo_eur) as totale_eur,
               codice_comparto
        FROM read_parquet('{url}')
        WHERE 1=1 {where}
        GROUP BY codice_ente, denominazione_ente, codice_comparto
        ORDER BY totale_eur DESC
        LIMIT {limit}
        """
    )
    return [
        {
            "codice_ente": r[0],
            "denominazione": r[1],
            "totale_eur": round(r[2], 2),
            "comparto": r[3],
        }
        for r in rows
    ]


def serie_storica(codice_ente: str, lato: str) -> list[dict[str, Any]]:
    """Trend pluriennale per un ente (da CLEAN)."""
    results = []
    for anno in ANNI:
        try:
            row = _query(
                f"""
                SELECT coalesce(sum(importo_eur), 0) as totale_eur,
                       count(*) as righe
                FROM read_parquet('{_clean_url(lato, anno)}')
                WHERE codice_ente = '{codice_ente}'
                  AND is_titolo_9 = false
                """
            )[0]
            if row[0]:
                results.append({
                    "anno": anno,
                    "totale_eur": round(row[0], 2),
                    "righe": row[1],
                })
        except Exception:
            continue
    return results


def elenca_enti(
    comparto: str | None = None, tipo: str | None = None, limit: int = 50
) -> list[dict[str, Any]]:
    """Elenca enti, opzionalmente filtrati per comparto o tipo."""
    where = ["data_fine = '9999-12-31'"]
    if comparto:
        where.append(f"tipo_ente = '{comparto}'")
    if tipo:
        where.append(f"tipo_ente = '{tipo}'")
    where_clause = " AND ".join(where)
    rows = _query(
        f"""
        SELECT codice_ente, denominazione_ente, tipo_ente,
               codice_provincia, codice_istat_comune
        FROM read_parquet('{ENTI_URL}')
        WHERE {where_clause}
        ORDER BY denominazione_ente
        LIMIT {limit}
        """
    )
    cols = ["codice_ente", "denominazione", "tipo_ente", "provincia", "comune_istat"]
    return [dict(zip(cols, r)) for r in rows]
