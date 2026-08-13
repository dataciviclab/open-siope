"""Golden set della classificazione SIOPE (mappe ufficiali RGS).

Regressione: verifica che le mappe (mapping/*.categorie.csv) assegnino le
categorie attese ai codici noti, inclusi i casi multi-gestione che hanno
causato i falsi positivi delle vecchie regole ILIKE.

Markers: contract (contratto pubblico, artifact format).
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]

USCITE = {
    # (codice_voce, codice_gestione) → (macro_area, macro_categoria)
    ("1.01.01.01.002", "PRO"): ("Spese correnti", "Personale"),   # puntato ufficiale
    ("1.01.01.01.002", "UNI"): ("Spese correnti", "Personale"),
    ("2.01.01.09.012", "PRO"): ("Spese in conto capitale", "Investimenti fissi"),
    ("1103", "SAN"): ("Spese correnti", "Personale"),              # glossario sanità
    ("2101", "SAN"): ("Spese correnti", "Acquisto beni e servizi"),
    ("1255", "UNI"): ("Spese correnti", "Personale"),              # multi-gestione: UNI arretrati ricercatori
    ("1255", "REG"): ("Spese correnti", "Altre spese"),            # multi-gestione: REG accertamenti sanitari
    ("2102", "RIC"): ("Spese correnti", "Personale"),              # multi-gestione: RIC assegni di ricerca
    ("2102", "SAN"): ("Spese correnti", "Acquisto beni e servizi"),
    ("A0400", "STA"): ("Spese correnti", "Trasferimenti correnti"),
    ("9999", "SAN"): ("Altre spese", "Altre spese"),               # partita di giro (compatti 999x)
}

ENTRATE = {
    ("1.01.01.06.001", "PRO"): "Imposte proprie",                  # IMU
    ("3.01.01.01.004", "PRO"): "Entrate extratributarie",          # titolo E3
    ("2102", "SAN"): "Trasferimenti correnti",                     # glossario sanità
    ("1301", "SAN"): "Entrate extratributarie",                    # prestazioni sanitarie
}


@pytest.fixture(scope="module")
def con():
    return duckdb.connect()


@pytest.mark.contract
def test_uscite_golden(con):
    m = con.execute(
        "select codice_gestione, codice_voce, macro_area, macro_categoria "
        "from read_csv('mapping/uscite_categorie.csv')"
    ).fetchall()
    got = {(r[0], r[1]): (r[2], r[3]) for r in m}
    for key, expected in USCITE.items():
        assert got.get(key) == expected, f"{key}: atteso {expected}, trovato {got.get(key)}"


@pytest.mark.contract
def test_entrate_golden(con):
    m = con.execute(
        "select codice_gestione, codice_voce, macro_categoria_v2 "
        "from read_csv('mapping/entrate_categorie.csv')"
    ).fetchall()
    got = {(r[0], r[1]): r[2] for r in m}
    for key, expected in ENTRATE.items():
        assert got.get(key) == expected, f"{key}: atteso {expected}, trovato {got.get(key)}"


@pytest.mark.contract
def test_copertura_dizionario(con):
    """Ogni riga (gestione, voce) del dizionario ha una riga in mappa — la
    guardia contro il COALESCE silenzioso sul non-mappato."""
    for seed, mappa, cols in [
        ("support/anag-codgest-uscite", "mapping/uscite_categorie.csv", "codice_voce, codice_gestione"),
        ("support/anag-codgest-entrate", "mapping/entrate_categorie.csv", "codice_voce, codice_gestione"),
    ]:
        # il seed materializzato deve esistere; altrimenti skip (nessun run locale)
        parquet = ROOT / "out" / "data" / "clean" / f"{seed.split('/')[-1]}_seed" / "2026" / f"{seed.split('/')[-1]}_seed_2026_clean.parquet"
        if not parquet.exists():
            pytest.skip("seed non materializzato localmente")
        miss = con.execute(f"""
            select count(*) from read_parquet('{parquet}') d
            left join read_csv('{mappa}') m
              on d.codice_voce = m.codice_voce and d.codice_gestione = m.codice_gestione
            where m.codice_voce is null
        """).fetchone()[0]
        assert miss == 0, f"{mappa}: {miss} righe del dizionario senza categoria in mappa"
