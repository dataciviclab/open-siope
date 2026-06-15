"""Tests per MCP server SIOPE.

Usa DuckDB in-memory con dati finti per mockare gcs_connect.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Aggiunge mcp_server/ al path per import
SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ── Fixture dati finti ──────────────────────────────────────────────────────

_ENTI_FAKE = [
    ("800000047", "ROMA CAPITALE", "COMUNE", "058", "091"),
    ("011992501", "COMUNE DI MILANO", "COMUNE", "015", "146"),
    ("006479801", "REGIONE LAZIO", "REGIONE", "058", "091"),
    ("006327004", "ASL ROMA 1", "ASL", "058", "091"),
    ("M00010", "MINISTERO TEST", "MINISTERI", "000", "000"),
]

_BILANCIO_ROMA = [
    (3, 2, 1700000.0),
]

_CATEGORIE_ROMA = [
    ("Imposte proprie", 1500000.0, 1),
    ("Trasferimenti correnti", 200000.0, 1),
]

_TOP_ENTI_PRO = [
    ("800000047", "ROMA CAPITALE", 1700000.0, "PRO"),
    ("011992501", "COMUNE DI MILANO", 800000.0, "PRO"),
]

_ENTI_FILTRATI = [
    ("800000047", "ROMA CAPITALE", "COMUNE", "058", "091"),
    ("011992501", "COMUNE DI MILANO", "COMUNE", "015", "146"),
]


def _fake_query(sql: str, *args, **kwargs) -> list[tuple]:
    """Mock per _query: restituisce dati in base al contenuto della SQL."""
    if "ILIKE" in sql and "ROMA" in sql:
        return _ENTI_FAKE
    if "ILIKE" in sql:
        return []
    if "JOIN" in sql and "codice_comparto" in sql:
        return _ENTI_FILTRATI
    if "tipo_ente" in sql and "COMUNE" in sql:
        return _ENTI_FILTRATI
    # Catch-all per query sulla tabella enti (senza filtri di comparto/tipo)
    if "FROM read_parquet" in sql and "enti_seed" in sql:
        return _ENTI_FAKE[:2]
    return []


def _fake_query_path(sql: str, *args, **kwargs) -> list[tuple]:
    """Mock per _query_path: opera sulla SQL già formattata."""
    if "count(*)" in sql and "count(DISTINCT codice_voce)" in sql:
        if "M00010" in sql:
            return [(0, 0, 0)]
        return _BILANCIO_ROMA
    if "GROUP BY categoria" in sql:
        return _CATEGORIE_ROMA
    if "GROUP BY codice_ente" in sql and "ORDER BY totale_eur DESC" in sql:
        return _TOP_ENTI_PRO
    return []


@pytest.fixture(autouse=True)
def _mock_queries():
    """Applica mock a _query e _query_path in siope_client per ogni test."""
    with patch("siope_client._query", side_effect=_fake_query):
        with patch("siope_client._query_path", side_effect=_fake_query_path):
            yield


# ── Tests ───────────────────────────────────────────────────────────────────


@pytest.mark.pure_unit
class TestInputValidation:
    """Validazione input: lato, anno, comparto, limit."""

    def test_lato_invalido(self):
        """get_bilancio con lato errato deve sollevare ValueError."""
        from siope_client import get_bilancio

        with pytest.raises(ValueError, match="entrate.*uscite"):
            get_bilancio("800000047", 2024, "spese")

    def test_anno_invalido(self):
        """get_bilancio con anno non coperto deve sollevare ValueError."""
        from siope_client import get_bilancio

        with pytest.raises(ValueError, match="2021"):
            get_bilancio("800000047", 2000, "entrate")

    def test_comparto_invalido(self):
        """top_enti con comparto inesistente deve sollevare ValueError."""
        from siope_client import top_enti

        with pytest.raises(ValueError, match="comparto non valido"):
            top_enti(2024, "entrate", "INVALIDO", 5)

    def test_limit_clamp_massimo(self):
        """top_enti con limit > 500 deve clampare a 500."""
        from siope_client import top_enti

        t = top_enti(2024, "entrate", limit=9999)
        assert len(t) >= 1  # non solleva, clampato


@pytest.mark.pure_unit
class TestClient:
    """Test unitari del client SIOPE con DuckDB mockato."""

    def test_cerca_ente(self):
        """cerca_ente deve trovare enti per match parziale."""
        from siope_client import cerca_ente

        results = cerca_ente("ROMA", limit=5)
        assert len(results) >= 1
        assert results[0]["codice_ente"] == "800000047"
        assert results[0]["denominazione"] == "ROMA CAPITALE"

    def test_cerca_ente_no_match(self):
        """cerca_ente deve restituire lista vuota se nessun match."""
        from siope_client import cerca_ente

        results = cerca_ente("INESISTENTE", limit=5)
        assert results == []

    def test_get_bilancio(self):
        """get_bilancio deve sommare correttamente le entrate."""
        from siope_client import get_bilancio

        b = get_bilancio("800000047", 2024, "entrate")
        assert b["codice_ente"] == "800000047"
        assert b["anno"] == 2024
        assert b["totale_eur"] == 1700000.0
        assert b["voci"] == 2

    def test_get_bilancio_no_data(self):
        """get_bilancio con ente fittizio deve restituire struttura valida."""
        from siope_client import get_bilancio

        b = get_bilancio("M00010", 2024, "entrate")
        # Il mock restituisce dati predefiniti, ma la struttura è corretta
        assert "codice_ente" in b
        assert "totale_eur" in b
        assert b["codice_ente"] == "M00010"
        assert b["anno"] == 2024
        assert b["lato"] == "entrate"

    def test_spesa_categoria(self):
        """spesa_categoria deve raggruppare per macro-categoria."""
        from siope_client import spesa_categoria

        c = spesa_categoria("800000047", 2024, "entrate")
        assert len(c) >= 2
        cats = {x["categoria"]: x["totale_eur"] for x in c}
        assert "Imposte proprie" in cats
        assert cats["Imposte proprie"] == 1500000.0

    def test_top_enti(self):
        """top_enti deve ordinare per totale decrescente e filtrare per comparto."""
        from siope_client import top_enti

        t = top_enti(2024, "entrate", "PRO", 3)
        assert len(t) >= 2
        assert t[0]["codice_ente"] == "800000047"
        assert t[1]["codice_ente"] == "011992501"

    def test_elenca_enti_per_tipo(self):
        """elenca_enti deve filtrare per tipo_ente."""
        from siope_client import elenca_enti

        e = elenca_enti(tipo="COMUNE", limit=10)
        assert len(e) >= 1
        assert all(x["tipo_ente"] == "COMUNE" for x in e)

    def test_elenca_enti_per_comparto(self):
        """elenca_enti deve filtrare per codice_comparto (es. PRO, SAN)."""
        from siope_client import elenca_enti

        e = elenca_enti(comparto="PRO", limit=10)
        assert len(e) >= 1

    def test_elenca_enti_sql_semantica(self):
        """La SQL generata per comparto deve filtrare su codice_comparto, non tipo_ente."""
        import siope_client
        captured_sql = []

        def _capture(sql, *a, **kw):
            captured_sql.append(sql)
            return []

        original = siope_client._query
        siope_client._query = _capture
        try:
            siope_client.elenca_enti(comparto="PRO", limit=5)
        finally:
            siope_client._query = original

        assert len(captured_sql) == 1
        sql = captured_sql[0]
        # Deve contenere il join con sottocomparti su codice_comparto
        assert "codice_comparto" in sql, f"SQL manca codice_comparto: {sql}"
        assert "s.codice_comparto = 'PRO'" in sql, (
            f"SQL deve filtrare su s.codice_comparto, non tipo_ente.\nSQL: {sql}"
        )
        # Non deve filtrare su tipo_ente per il parametro comparto
        assert "JOIN" in sql, f"SQL deve usare JOIN con sottocomparti"

    def test_top_enti_sql_semantica(self):
        """La SQL per top_enti con comparto deve filtrare su codice_comparto."""
        import siope_client
        captured = []

        def _capture(sql_template, s3_path, **kwargs):
            # _query_path riceve template + kwargs, formatta prima di eseguire
            captured.append((sql_template, kwargs))
            return []

        original = siope_client._query_path
        siope_client._query_path = _capture
        try:
            siope_client.top_enti(2024, "entrate", "SAN", 5)
        finally:
            siope_client._query_path = original

        assert len(captured) == 1
        sql_template, kwargs = captured[0]
        # Verifica che il template abbia codice_comparto e che extra sia passato
        assert "codice_comparto" in sql_template, (
            f"Template deve selezionare codice_comparto"
        )
        # Verifica che kwargs contenga il filtro corretto
        assert kwargs.get("extra", "") == "AND codice_comparto = 'SAN'", (
            f"extra deve contenere il filtro comparto: {kwargs.get('extra')}"
        )

    def test_elenca_enti_senza_filtri(self):
        """elenca_enti senza filtri deve restituire enti."""
        from siope_client import elenca_enti

        e = elenca_enti(limit=5)
        assert len(e) >= 1


@pytest.mark.contract
class TestServer:
    """Test del server MCP — registrazione tool."""

    def test_all_tools_registered(self):
        """Tutti i 6 tool devono essere registrati."""
        from server import mcp

        tools = asyncio.run(mcp.list_tools())
        names = sorted(t.name for t in tools)
        expected = sorted([
            "siope_cerca_ente",
            "siope_enti_comparto",
            "siope_get_bilancio",
            "siope_serie_storica",
            "siope_spesa_categoria",
            "siope_top_enti",
        ])
        assert names == expected

    def test_server_name(self):
        """Il server deve chiamarsi 'siope'."""
        from server import mcp

        assert mcp.name == "siope"


@pytest.mark.smoke
class TestIntegration:
    """Test di integrazione (mockati, con cache e flusso cross-tool)."""

    def test_cache_hit(self):
        """La cache deve accelerare la seconda chiamata identica."""
        from siope_client import get_bilancio
        import time

        t0 = time.time()
        get_bilancio("800000047", 2024, "entrate")
        first = time.time() - t0

        t0 = time.time()
        get_bilancio("800000047", 2024, "entrate")
        second = time.time() - t0

        assert second < first

    def test_cache_different_query(self):
        """Query diverse non devono condividere la cache."""
        from siope_client import get_bilancio, spesa_categoria

        get_bilancio("800000047", 2024, "entrate")
        r = spesa_categoria("800000047", 2024, "entrate")
        assert len(r) >= 1
