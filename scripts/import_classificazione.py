#!/usr/bin/env python3
"""Importa la classificazione ufficiale dei codici gestionali SIOPE e genera
le mappe consumate dai seed (mapping/uscite_categorie.csv, entrate_categorie.csv).

Fonti ufficiali RGS (scaricare in /tmp/opencode o passare --dir):
- Glossario SIOPE enti territoriali (XLSX) — codici puntati PRO/REG/UNI → piano dei conti
  https://www.rgs.mef.gov.it/_Documenti/VERSIONE-I/e-GOVERNME1/SIOPE/glossario_codici_gestionali/Glossario-SIOPE-enti-territoriali-del-2026.xlsx
- Glossario SIOPE Sanità (XLS) — codici compatti SAN → sezioni
  https://www.rgs.mef.gov.it/_Documenti/VERSIONE-I/e-GOVERNME1/SIOPE/glossario_codici_gestionali/Glossario_SIOPE-SanitA-dal-1-gennaio-2025.xls

Strategia: la categoria di ogni codice è una RIGA ESPLICITA nel CSV (nessuna
regola testuale a runtime). Fonte ufficiale dove esiste (puntati dal glossario
enti territoriali, SAN dal glossario sanità); baseline dal dizionario SIOPE
per i comparti senza glossario scaricabile (STA, CDC, ... — descrizioni
auto-classificanti) e per i residui (0.00.00.99.x = partite di giro).

Usage:
    python scripts/import_classificazione.py --dir /tmp/opencode
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import openpyxl
import xlrd

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "mapping"

# ── Tabella ufficiale (piano dei conti): macroaggregato → macro_categoria ──
USCITE = {
    ("U", "1", "01"): "Personale", ("U", "1", "02"): "Imposte e tasse",
    ("U", "1", "03"): "Acquisto beni e servizi", ("U", "1", "04"): "Trasferimenti correnti",
    ("U", "1", "05"): "Trasferimenti correnti", ("U", "1", "06"): "Trasferimenti correnti",
    ("U", "1", "07"): "Interessi passivi", ("U", "1", "08"): "Altre spese",
    ("U", "1", "09"): "Poste correttive", ("U", "1", "10"): "Altre spese",
    ("U", "2", "01"): "Imposte e tasse", ("U", "2", "02"): "Investimenti fissi",
    ("U", "2", "03"): "Contributi investimenti", ("U", "2", "04"): "Trasferimenti c/capitale",
    ("U", "2", "05"): "Altre spese",
    ("U", "3", "01"): "Incremento attivita' finanziarie", ("U", "3", "02"): "Incremento attivita' finanziarie",
    ("U", "3", "03"): "Incremento attivita' finanziarie", ("U", "3", "04"): "Incremento attivita' finanziarie",
    ("U", "4", "01"): "Rimborso prestiti", ("U", "4", "02"): "Rimborso prestiti",
    ("U", "4", "03"): "Rimborso prestiti", ("U", "4", "04"): "Rimborso prestiti",
    ("U", "4", "05"): "Rimborso prestiti",
    ("U", "5", "01"): "Anticipazioni", ("U", "7", "01"): "Altre spese", ("U", "7", "02"): "Altre spese",
}
ENTRATE = {
    ("E", "1", "01"): "Imposte proprie", ("E", "1", "03"): "Fondi perequativi",
    ("E", "2", "01"): "Trasferimenti correnti",
    ("E", "3", "01"): "Entrate extratributarie", ("E", "3", "02"): "Entrate extratributarie",
    ("E", "3", "03"): "Entrate extratributarie", ("E", "3", "04"): "Entrate extratributarie",
    ("E", "3", "05"): "Entrate extratributarie",
    ("E", "4", "01"): "Imposte proprie", ("E", "4", "02"): "Contributi agli investimenti",
    ("E", "4", "03"): "Trasferimenti c/capitale", ("E", "4", "04"): "Entrate extratributarie",
    ("E", "4", "05"): "Entrate extratributarie",
    ("E", "5", "01"): "Altro", ("E", "5", "02"): "Altro", ("E", "5", "03"): "Altro", ("E", "5", "04"): "Altro",
    ("E", "6", "01"): "Altro", ("E", "6", "02"): "Altro", ("E", "6", "03"): "Altro", ("E", "6", "04"): "Altro",
    ("E", "7", "01"): "Altro", ("E", "9", "01"): "Altro", ("E", "9", "02"): "Altro",
}

# ── Sezioni glossario sanità → macro_categoria ──
SAN_USCITE = {
    "PERSONALE": "Personale", "Competenze a favore del personale": "Personale",
    "Ritenute a carico del personale": "Personale", "Contributi  a carico dell'ente": "Personale",
    "Interventi assistenziali": "Personale", "Altre spese di personale": "Personale",
    "ACQUISTO DI BENI": "Acquisto beni e servizi", "Acquisto di beni sanitari": "Acquisto beni e servizi",
    "Acquisto di beni non sanitari": "Acquisto beni e servizi",
    "ACQUISTI DI SERVIZI": "Acquisto beni e servizi", "Acquisti di servizi sanitari": "Acquisto beni e servizi",
    "Acquisti di servizi non sanitari": "Acquisto beni e servizi",
    "Interessi passivi e oneri finanziari diversi": "Interessi passivi", "IMPOSTE E TASSE": "Imposte e tasse",
    "ONERI STRAORDINARI GESTIONE CORRENTE": "Altre spese", "TITOLO 2°: SPESE IN CONTO CAPITALE": "Altre spese",
    "ACQUISIZIONE BENI IMMOBILI": "Investimenti fissi", "ESPROPRI E SERVITU' ONEROSE": "Investimenti fissi",
    "ACQUISTO DI BENI SPECIFICI PER REALIZZAZIONI IN ECONOMIA": "Investimenti fissi",
    "UTILIZZO DI BENI DI TERZI PER REALIZZAZIONI IN ECONOMIA": "Investimenti fissi",
    "CONTRIBUTI E TRASFERIMENTI": "Trasferimenti c/capitale", "ALTRE SPESE CORRENTI": "Altre spese",
    "INVESTIMENTI FISSI": "Investimenti fissi", "OPERAZIONI FINANZIARIE": "Incremento attivita' finanziarie",
    "SPESE PER RIMBORSO DI PRESTITI": "Rimborso prestiti",
}
SAN_ENTRATE = {
    "ENTRATE DERIVANTI DALLA PRESTAZIONE DI SERVIZI E DALLA VENDITA DI BENI DI CONSUMO": "Entrate extratributarie",
    "Entrate da strutture sanitarie pubbliche della Regione e della Provincia autonoma per prestazioni sanitarie e sociosanitarie a rilevanza sanitaria": "Entrate extratributarie",
    "CONTRIBUTI E TRASFERIMENTI  CORRENTI": "Trasferimenti correnti",
    "Contributi e trasferimenti correnti da Amministrazioni pubbliche": "Trasferimenti correnti",
    "Contributi e trasferimenti correnti da soggetti privati": "Trasferimenti correnti",
    "Contributi e trasferimenti correnti dall'estero": "Trasferimenti correnti",
    "ALTRE ENTRATE CORRENTI": "Entrate extratributarie", "Concorsi, recuperi e rimborsi": "Entrate extratributarie",
    "Entrate patrimoniali": "Entrate extratributarie",
    "ENTRATE DERIVANTI DA ALIENAZIONI DI BENI": "Altro",
    "Alienazione di immobilizzazioni materiali": "Altro", "Alienazione di immobilizzazioni finanziarie": "Altro",
    "CONTRIBUTI E TRASFERIMENTI  IN C/CAPITALE": "Trasferimenti c/capitale",
    "Contributi e trasferimenti in c/capitale  da Amministrazioni pubbliche": "Trasferimenti c/capitale",
    "Contributi e trasferimenti in conto capitale da soggetti privati": "Trasferimenti c/capitale",
    "Contributi e trasferimenti in c/capitale  dall'estero": "Trasferimenti c/capitale",
    "OPERAZIONI FINANZIARIE": "Altro", "ENTRATE DERIVANTI DA ACCENSIONE DI PRESTITI": "Altro",
    "Mutui da Cassa depositi e prestiti": "Altro",
}

AREA_CORR = {"Personale", "Imposte e tasse", "Acquisto beni e servizi", "Trasferimenti correnti",
             "Interessi passivi", "Poste correttive", "Altre spese"}


def area_of(cat: str) -> str:
    if cat in AREA_CORR:
        return "Spese correnti"
    if cat in ("Investimenti fissi", "Contributi investimenti", "Trasferimenti c/capitale"):
        return "Spese in conto capitale"
    if cat == "Incremento attivita' finanziarie":
        return "Incremento attivita' finanziarie"
    if cat == "Rimborso prestiti":
        return "Rimborso prestiti"
    if cat == "Anticipazioni":
        return "Anticipazioni e partite di giro"
    return "Altre spese"


def san_cat(sez: str | None, mappa: dict[str, str]) -> str | None:
    if not sez:
        return None
    if sez in mappa:
        return mappa[sez]
    for k, v in mappa.items():
        if k in sez or sez in k:
            return v
    return None


def parse_glossario_enti(path: Path) -> dict[str, tuple[str, str, str]]:
    """XLSX glossario enti territoriali → {codice_siope: (macro, l1, l2)}."""
    wb = openpyxl.load_workbook(path, read_only=True)
    ws = wb["Allegato A"]
    out: dict[str, tuple[str, str, str]] = {}
    for r in ws.iter_rows(min_row=9, values_only=True):
        cod = str(r[7]).strip() if r[7] else ""
        if not cod:
            continue
        p = cod.split(".")
        out[".".join(p[1:])] = (str(r[0]).strip(), str(r[1]).strip(), str(r[2]).strip())
    return out


def parse_glossario_sanita(path: Path) -> dict[tuple[str, str], str]:
    """XLS glossario sanità → {(lato, codice): sezione}."""
    wb = xlrd.open_workbook(path)
    out: dict[tuple[str, str], str] = {}
    for sn, lato in (("SPESE", "U"), ("ENTRATE", "E")):
        sh = wb.sheet_by_name(sn)
        cur = None
        for i in range(4, sh.nrows):
            cod = str(sh.cell_value(i, 0)).strip()
            desc = str(sh.cell_value(i, 1)).strip()
            if not cod and desc and not desc.startswith("STRUTTURE"):
                cur = desc
            elif cod:
                out[(lato, cod.split(".")[0])] = cur
    return out


def load_baseline() -> tuple[dict[str, tuple[str, str]], dict[str, str]]:
    """Baseline: classificazione attuale dai seed (per i comparti senza fonte)."""
    import duckdb
    con = duckdb.connect()
    W = str(ROOT)
    pu = f"{W}/out/data/clean/siope_anag_codgest_uscite_seed/2026/siope_anag_codgest_uscite_seed_2026_clean.parquet"
    pe = f"{W}/out/data/clean/siope_anag_codgest_entrate_seed/2026/siope_anag_codgest_entrate_seed_2026_clean.parquet"
    u = {r[0]: (r[1], r[2]) for r in con.execute(
        f"select distinct codice_voce, macro_area, macro_categoria from read_parquet('{pu}')").fetchall()}
    e = {r[0]: r[1] for r in con.execute(
        f"select distinct codice_voce, macro_categoria_v2 from read_parquet('{pe}')").fetchall()}
    return u, e


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--dir", default="/tmp/opencode", help="Dir con i file XLS/XLSX ufficiali")
    args = p.parse_args()
    d = Path(args.dir)

    g_enti = parse_glossario_enti(d / "glossario_enti_2026.xlsx")
    g_san = parse_glossario_sanita(d / "glossario_sanita.xls")
    baseline_u, baseline_e = load_baseline()

    final_u: dict[str, tuple[str, str]] = {}
    final_e: dict[str, str] = {}
    for cod, (macro, l1, l2) in g_enti.items():
        if macro == "U":
            cat = USCITE.get((macro, l1, l2))
            if cat:
                final_u[cod] = (area_of(cat), cat)
        else:
            cat = ENTRATE.get((macro, l1, l2))
            if cat:
                final_e[cod] = cat
    for (lato, cod), sez in g_san.items():
        if lato == "U":
            cat = san_cat(sez, SAN_USCITE)
            if cat:
                final_u[cod] = (area_of(cat), cat)
        else:
            cat = san_cat(sez, SAN_ENTRATE)
            if cat:
                final_e[cod] = cat
    for cod, (a, c) in baseline_u.items():
        final_u.setdefault(cod, (a, c))
    for cod, c in baseline_e.items():
        final_e.setdefault(cod, c)

    MAPPING.mkdir(exist_ok=True)
    with (MAPPING / "uscite_categorie.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["codice_voce", "macro_area", "macro_categoria"])
        w.writerows((k, v[0], v[1]) for k, v in sorted(final_u.items()))
    with (MAPPING / "entrate_categorie.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["codice_voce", "macro_categoria_v2"])
        w.writerows((k, v) for k, v in sorted(final_e.items()))
    print(f"mappa scritta: uscite {len(final_u)}, entrate {len(final_e)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
