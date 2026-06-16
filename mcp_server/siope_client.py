"""Client DuckDB per dati SIOPE su GCS pubblico.

Legge parquet da GCS via DuckDB con gcs_connect (lab_connectors).
I risultati sono cached con TtlCache (TTL 120s).

Tutti gli input utente sono validati con allowlist/cast per evitare
SQL injection tramite tool MCP esposti pubblicamente.
"""

from __future__ import annotations

from typing import Any

from lab_connectors.duckdb import gcs_connect
from lab_connectors.mcp.cache import TtlCache

# ── Costanti ──────────────────────────────────────────────────────────────────

GCS_BASE = "https://storage.googleapis.com/dataciviclab-clean/siope"
ANNI = {2021, 2022, 2023, 2024, 2025}
LATI = {"entrate", "uscite"}
COMPARTI_VALIDI = {
    "PRO", "REG", "SAN", "UNI", "MON", "CDC", "AAI", "ASP", "EGP", "EPF",
    "FLS", "RIC", "VCE", "VCF", "VSN", "STA",
}

ENTI_URL = (
    f"{GCS_BASE}/siope_anag_enti_seed/2026"
    "/siope_anag_enti_seed_2026_clean.parquet"
)
SOTTOCOMPARTI_URL = (
    f"{GCS_BASE}/siope_anag_sottocomparti_seed/2026"
    "/siope_anag_sottocomparti_seed_2026_clean.parquet"
)

_cache = TtlCache(ttl_seconds=120)

# ── Validazione input ────────────────────────────────────────────────────────


def _validate_lato(lato: str) -> str:
    if lato not in LATI:
        raise ValueError(f"lato deve essere 'entrate' o 'uscite', non '{lato}'")
    return lato


def _validate_anno(anno: int) -> int:
    if anno not in ANNI:
        raise ValueError(f"anno deve essere in {sorted(ANNI)}, non {anno}")
    return anno


def _validate_comparto(comparto: str | None) -> str | None:
    if comparto is not None and comparto not in COMPARTI_VALIDI:
        raise ValueError(
            f"comparto non valido: '{comparto}'. "
            f"Validi: {sorted(COMPARTI_VALIDI)}"
        )
    return comparto


def _validate_limit(limit: int) -> int:
    limit = int(limit)
    if limit < 1:
        limit = 1
    if limit > 500:
        limit = 500
    return limit


def _escape_sql(val: str) -> str:
    """Escaping minimo per stringhe SQL (singoli apici)."""
    return val.replace("'", "''")


def _parquet_url(lato: str, anno: int) -> str:
    return (
        f"{GCS_BASE}/siope_{lato}_comuni/{anno}"
        f"/siope_{lato}_comuni_{anno}_clean.parquet"
    )


# ── Esecuzione query ─────────────────────────────────────────────────────────


def _query(sql: str, parquet_url: str | None = None) -> list[tuple]:
    cached = _cache.get(sql)
    if cached is not None:
        return cached

    path = parquet_url or ENTI_URL
    with gcs_connect(path) as con:
        result = con.sql(sql).fetchall()
        _cache.set(sql, result)
        return result


def _query_path(sql_template: str, parquet_url: str, **kwargs) -> list[tuple]:
    """Build SQL with params, execute via gcs_connect."""
    sql = sql_template.format(**kwargs)
    cached = _cache.get(sql)
    if cached is not None:
        return cached
    with gcs_connect(parquet_url) as con:
        result = con.sql(sql).fetchall()
        _cache.set(sql, result)
        return result


# ── Tool implementations ─────────────────────────────────────────────────────


def cerca_ente(query: str, tipo: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
    """Cerca enti per denominazione (LIKE %query%), opzionalmente filtra per tipo."""
    limit = _validate_limit(limit)
    safe = _escape_sql(query)
    tipo_filter = f"AND tipo_ente = '{_escape_sql(tipo)}'" if tipo else ""
    rows = _query(
        f"""
        SELECT codice_ente, denominazione_ente, tipo_ente,
               codice_provincia, codice_istat_comune
        FROM read_parquet('{ENTI_URL}')
        WHERE data_fine = '9999-12-31'
          AND denominazione_ente ILIKE '%{safe}%'
          {tipo_filter}
        ORDER BY
          CASE WHEN tipo_ente = 'COMUNE' THEN 0
               WHEN tipo_ente = 'ASL' THEN 1
               WHEN tipo_ente = 'REGIONE' THEN 2
               WHEN tipo_ente = 'ATENEO' THEN 3
               ELSE 4
          END,
          denominazione_ente
        LIMIT {limit}
        """
    )
    cols = ["codice_ente", "denominazione", "tipo_ente", "provincia", "comune_istat"]
    return [dict(zip(cols, r)) for r in rows]


def get_bilancio(
    codice_ente: str, anno: int, lato: str
) -> dict[str, Any]:
    """Totale entrate/uscite per un ente in un anno (da CLEAN)."""
    lato = _validate_lato(lato)
    anno = _validate_anno(anno)
    ente = _escape_sql(codice_ente)
    path = _parquet_url(lato, anno)
    row = _query_path(
        """
        SELECT count(*) as righe,
               count(DISTINCT codice_voce) as voci,
               sum(importo_eur) as totale_eur
        FROM read_parquet('{path}')
        WHERE codice_ente = '{ente}'
          AND is_titolo_9 = false
        """,
        path,
        path=path, ente=ente,
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
    lato = _validate_lato(lato)
    anno = _validate_anno(anno)
    ente = _escape_sql(codice_ente)
    path = _parquet_url(lato, anno)
    cat_col = "macro_categoria_v2" if lato == "entrate" else "macro_categoria"
    rows = _query_path(
        """
        SELECT {cat} as categoria,
               sum(importo_eur) as totale_eur,
               count(DISTINCT codice_voce) as voci
        FROM read_parquet('{path}')
        WHERE codice_ente = '{ente}'
          AND is_titolo_9 = false
        GROUP BY categoria
        ORDER BY totale_eur DESC
        """,
        path,
        cat=cat_col, path=path, ente=ente,
    )
    return [
        {"categoria": r[0], "totale_eur": round(r[1], 2), "voci": r[2]}
        for r in rows
    ]


def top_enti(
    anno: int, lato: str, comparto: str | None = None, limit: int = 10
) -> list[dict[str, Any]]:
    """Enti con maggiori entrate/uscite (da CLEAN)."""
    anno = _validate_anno(anno)
    lato = _validate_lato(lato)
    comparto = _validate_comparto(comparto)
    limit = _validate_limit(limit)
    path = _parquet_url(lato, anno)

    if comparto:
        extra = f"AND codice_comparto = '{comparto}'"
    else:
        extra = ""
    rows = _query_path(
        """
        SELECT codice_ente, denominazione_ente,
               sum(importo_eur) as totale_eur,
               codice_comparto
        FROM read_parquet('{path}')
        WHERE is_titolo_9 = false {extra}
        GROUP BY codice_ente, denominazione_ente, codice_comparto
        ORDER BY totale_eur DESC
        LIMIT {lim}
        """,
        path,
        path=path, extra=extra, lim=limit,
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
    lato = _validate_lato(lato)
    ente = _escape_sql(codice_ente)
    results: list[dict[str, Any]] = []
    for anno in sorted(ANNI):
        path = _parquet_url(lato, anno)
        row = _query_path(
            """
            SELECT coalesce(sum(importo_eur), 0) as totale_eur,
                   count(*) as righe
            FROM read_parquet('{path}')
            WHERE codice_ente = '{ente}'
              AND is_titolo_9 = false
            """,
            path,
            path=path, ente=ente,
        )[0]
        if row[0]:
            results.append({
                "anno": anno,
                "totale_eur": round(row[0], 2),
                "righe": row[1],
            })
    return results


def lookup_ente(codice_ente: str) -> dict[str, Any] | None:
    """Cerca un ente per codice_ente esatto. Restituisce dettagli o None."""
    safe = _escape_sql(codice_ente)
    rows = _query(
        f"""
        SELECT e.codice_ente, e.denominazione_ente, e.tipo_ente,
               e.codice_provincia, e.codice_istat_comune,
               s.codice_comparto, s.descrizione_sottocomparto
        FROM read_parquet('{ENTI_URL}') e
        LEFT JOIN read_parquet('{SOTTOCOMPARTI_URL}') s
          ON e.tipo_ente = s.codice_sottocomparto
        WHERE e.codice_ente = '{safe}'
          AND e.data_fine = '9999-12-31'
        LIMIT 1
        """
    )
    if not rows:
        return None
    r = rows[0]
    return {
        "codice_ente": r[0],
        "denominazione": r[1],
        "tipo_ente": r[2],
        "codice_provincia": r[3],
        "codice_istat_comune": r[4],
        "codice_comparto": r[5],
        "comparto_descrizione": r[6],
    }


def elenca_enti(
    comparto: str | None = None, tipo: str | None = None, limit: int = 50
) -> list[dict[str, Any]]:
    """Elenca enti, opzionalmente filtrati per comparto o tipo.

    Il filtro ``comparto`` usa ``codice_comparto`` (es. PRO, REG, SAN, UNI).
    Il filtro ``tipo`` usa ``tipo_ente`` dall'anagrafica (es. COMUNE, ASL, ATENEO).
    """
    comparto = _validate_comparto(comparto)
    limit = _validate_limit(limit)

    # Costruisce la SQL: join enti → sottocomparti per filtro comparto
    if comparto:
        sql = f"""
            SELECT e.codice_ente, e.denominazione_ente, e.tipo_ente,
                   e.codice_provincia, e.codice_istat_comune
            FROM read_parquet('{ENTI_URL}') e
            JOIN read_parquet('{SOTTOCOMPARTI_URL}') s
              ON e.tipo_ente = s.codice_sottocomparto
            WHERE e.data_fine = '9999-12-31'
              AND s.codice_comparto = '{comparto}'
            ORDER BY e.denominazione_ente
            LIMIT {limit}
        """
    else:
        conditions = ["e.data_fine = '9999-12-31'"]
        if tipo:
            safe_tipo = _escape_sql(tipo)
            conditions.append(f"e.tipo_ente = '{safe_tipo}'")
        where = " AND ".join(conditions)
        sql = f"""
            SELECT e.codice_ente, e.denominazione_ente, e.tipo_ente,
                   e.codice_provincia, e.codice_istat_comune
            FROM read_parquet('{ENTI_URL}') e
            WHERE {where}
            ORDER BY e.denominazione_ente
            LIMIT {limit}
        """

    rows = _query(sql, parquet_url=ENTI_URL if not comparto else None)
    cols = ["codice_ente", "denominazione", "tipo_ente", "provincia", "comune_istat"]
    return [dict(zip(cols, r)) for r in rows]
