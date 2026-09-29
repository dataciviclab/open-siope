#!/usr/bin/env python3
"""
verify_output.py — Certificazione qualità output pipeline SIOPE.

Legge da out/data/ (locale). Exit code: 0 = PASS, 1 = CRITICAL.

Usage:
  python3 scripts/verify_output.py                         # entrate+uscite, 2025
  python3 scripts/verify_output.py --lato entrate --year 2025
  python3 scripts/verify_output.py --lato entrate --year 2021,2025
  python3 scripts/verify_output.py --ci        # JSON per CI, parametri da env
"""

import argparse, datetime, json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "out" / "data"
# Default: range completo SIOPE (2021-2026). Se --config e' passato,
# gli anni vengono letti dal dataset.yml per allineamento automatico.
ANNI_DISPONIBILI = [2021, 2022, 2023, 2024, 2025, 2026]

LATI_CONFIG = {
    "entrate": {
        "clean": "clean/siope_entrate/{a}/siope_entrate_{a}_clean.parquet",
        "class_col": "macro_categoria",
        "class_altro": "Altro",
        "mart": {
            "anno_comparto": "mart/siope_entrate/{a}/mart_anno_comparto.parquet",
            "ente": "mart/siope_entrate/{a}/mart_ente.parquet",
        },
    },
    "uscite": {
        "clean": "clean/siope_uscite/{a}/siope_uscite_{a}_clean.parquet",
        "class_col": "macro_categoria",
        "class_altro": "Altre spese",
        "mart": {
            "anno_comparto": "mart/siope_uscite/{a}/mart_anno_comparto.parquet",
            "ente": "mart/siope_uscite/{a}/mart_ente.parquet",
        },
    },
}

SOGLIE = {
    "clean_min_rows_full": 1_000_000,
    "clean_min_rows_floor": 100_000,
    "join_territorio_pct": 95.0,
    "join_codgest_pct":   95.0,
    "importi_negativi_max": 100,
}


def periodi_attesi(anno: int) -> int:
    """Numero di periodi mensili attesi per anno.
    - Anni passati: 12 (gen-dic completi)
    - Anno corrente: ultimo mese completo (mese_corrente - 1)
    """
    oggi = datetime.date.today()
    if anno < oggi.year:
        return 12
    # Anno corrente: mese corrente - 1 (es. a giugno → 5 periodi, gen-mag)
    return max(oggi.month - 1, 1)


def clean_min_rows(anno: int) -> int:
    """Soglia righe minime per clean, proporzionale ai mesi disponibili.
    - Anni passati: 1_000_000 (anno intero)
    - Anno corrente: proporzionale ai mesi completi, floor 100K
    """
    oggi = datetime.date.today()
    if anno < oggi.year:
        return SOGLIE["clean_min_rows_full"]
    mesi = periodi_attesi(anno)
    return max(SOGLIE["clean_min_rows_floor"],
               int(SOGLIE["clean_min_rows_full"] * mesi / 12))


def resolve(cfg, anno):
    return str(ROOT / cfg.format(a=anno))


def check_clean(con, lato, anno, cfg):
    path = resolve(cfg["clean"], anno)
    if not Path(path).exists():
        return {"check": f"clean_{lato}_{anno}", "esito": "CRITICAL",
                "dettaglio": f"FILE MANCANTE: {path}"}

    r = con.execute(f"""
        select count(*), count(distinct codice_ente), count(distinct periodo),
               count(*) filter (where importo < 0),
               count(*) filter (where codice_ente is null)
        from read_parquet('{path}')
    """).fetchone()

    righe, enti, periodi, neg, null_ente = r
    attesi = periodi_attesi(anno)
    min_righe = clean_min_rows(anno)
    esito = "PASS"
    if righe < min_righe:
        esito = "CRITICAL"
    if periodi != attesi:
        esito = "WARN" if anno == datetime.date.today().year else "CRITICAL"
    if neg > SOGLIE["importi_negativi_max"]:
        esito = "CRITICAL"
    # null_ente è già bloccato a runtime da clean.validate.not_null nel dataset.yml

    return {"check": f"clean_{lato}_{anno}", "esito": esito,
            "dettaglio": {"righe": righe, "enti": enti, "periodi": periodi,
                          "periodi_attesi": attesi,
                          "min_righe": min_righe,
                          "importi_neg": neg, "null_ente": null_ente}}


def check_join(con, lato, anno, cfg):
    path = resolve(cfg["clean"], anno)
    if not Path(path).exists():
        return {"check": f"join_{lato}_{anno}", "esito": "SKIP", "dettaglio": "clean non presente"}

    r = con.execute(f"""
        select
            round(100.0 * count(*) filter (where provincia is not null) / count(*), 2),
            round(100.0 * count(*) filter (where has_codgest_match) / count(*), 2),
            round(100.0 * count(*) filter (where denominazione_ente is not null) / count(*), 2)
        from read_parquet('{path}')
    """).fetchone()

    pct_terr, pct_codg, pct_enti = r
    esito = "PASS"
    if pct_terr < SOGLIE["join_territorio_pct"] or pct_codg < SOGLIE["join_codgest_pct"]:
        esito = "CRITICAL"

    return {"check": f"join_{lato}_{anno}", "esito": esito,
            "dettaglio": {"territorio_pct": pct_terr, "codgest_pct": pct_codg, "enti_pct": pct_enti}}


def check_mart_anno_comparto(con, lato, anno, cfg):
    path = resolve(cfg["mart"]["anno_comparto"], anno)
    if not Path(path).exists():
        return {"check": f"mart_{lato}_{anno}_anno_comparto", "esito": "CRITICAL",
                "dettaglio": f"FILE MANCANTE: {path}"}

    class_col = cfg["class_col"]
    class_altro = cfg["class_altro"]

    r = con.execute(f"""
        select count(*),
               round(sum(importo_eur), 0),
               count(*) filter (where importo_eur < 0),
               count(*) filter (where {class_col} is null),
               round(100.0 * count(*) filter (where {class_col} = '{class_altro}') / count(*), 2),
               count(distinct codice_comparto),
               count(distinct n_enti)
        from read_parquet('{path}')
    """).fetchone()

    righe, totale, neg, null_class, altro_pct, n_comparti, n_enti_max = r
    esito = "PASS"
    if null_class > 0:
        esito = "CRITICAL"

    return {"check": f"mart_{lato}_{anno}_anno_comparto", "esito": esito,
            "dettaglio": {"righe": righe, "totale_eur": totale,
                          "negativi": neg, "null_class": null_class, "altro_pct": altro_pct,
                          "comparti_distinti": n_comparti}}


def check_mart_ente(con, lato, anno, cfg):
    path = resolve(cfg["mart"]["ente"], anno)
    if not Path(path).exists():
        return {"check": f"mart_{lato}_{anno}_ente", "esito": "CRITICAL",
                "dettaglio": f"FILE MANCANTE: {path}"}

    r = con.execute(f"""
        select count(*),
               round(sum(totale_eur), 0),
               count(*) filter (where totale_eur < 0),
               count(*) filter (where denominazione_ente is null),
               count(*) filter (where codice_comparto is null),
               count(distinct codice_ente),
               round(avg(n_mesi), 1)
        from read_parquet('{path}')
    """).fetchone()

    righe, totale, neg, null_ente, null_comparto, n_enti, avg_mesi = r
    esito = "PASS"
    if null_ente > 0:
        esito = "CRITICAL"

    return {"check": f"mart_{lato}_{anno}_ente", "esito": esito,
            "dettaglio": {"righe": righe, "totale_eur": totale,
                          "negativi": neg, "null_ente": null_ente,
                          "null_comparto": null_comparto,
                          "enti_distinti": n_enti, "avg_mesi": avg_mesi}}


def main():
    p = argparse.ArgumentParser(description="Certifica output SIOPE")
    p.add_argument("--lato", default="all", choices=["entrate", "uscite", "all"])
    p.add_argument("--year", default="2025", help="Anno/i separati da virgola o 'all'")
    p.add_argument("--config", type=str, default=None,
                   help="Path dataset.yml di entrate/uscite per leggere anni disponibili (es. datasets/siope-entrate/dataset.yml)")
    p.add_argument("--ci", action="store_true", help="Output JSON per CI")
    args = p.parse_args()

    # --lato
    lati = ["entrate", "uscite"] if args.lato == "all" else [args.lato]

    # --year: se 'all', usa ANNI_DISPONIBILI o li legge dal dataset.yml
    anni_source = ANNI_DISPONIBILI
    if args.config:
        try:
            import yaml
            with open(args.config) as f:
                cfg = yaml.safe_load(f)
            anni_source = cfg.get("dataset", {}).get("years", ANNI_DISPONIBILI)
        except Exception:
            pass  # fallback a default

    if args.year == "all":
        anni = anni_source
    else:
        anni = [int(y) for y in args.year.split(",")]

    from lab_connectors.duckdb import safe_connect
    with safe_connect() as con:
        checks = []

        for lato in lati:
            cfg = LATI_CONFIG[lato]
            for anno in anni:
                for check_fn, check_args in [
                    (check_clean, [con, lato, anno, cfg]),
                    (check_join, [con, lato, anno, cfg]),
                    (check_mart_anno_comparto, [con, lato, anno, cfg]),
                    (check_mart_ente, [con, lato, anno, cfg]),
                ]:
                    try:
                        checks.append(check_fn(*check_args))
                    except Exception as e:
                        checks.append({
                            "check": f"{check_fn.__name__}_{lato}_{anno}",
                            "esito": "CRITICAL",
                            "dettaglio": f"ERRORE ESECUZIONE: {e}",
                        })

    ok = sum(1 for c in checks if c["esito"] == "PASS")
    warn = sum(1 for c in checks if c["esito"] == "WARN")
    crit = sum(1 for c in checks if c["esito"] == "CRITICAL")
    skip = sum(1 for c in checks if c["esito"] == "SKIP")
    globale = "CRITICAL" if crit > 0 else "WARN" if warn > 0 else "PASS"

    if args.ci:
        print(json.dumps({"esito": globale, "checks": checks}, indent=2))
    else:
        print(f"\n{'='*50}")
        print(f"  VERIFICA OUTPUT SIOPE")
        print(f"{'='*50}")
        print(f"  Esito: {'PASS' if globale == 'PASS' else 'WARN' if globale == 'WARN' else 'CRITICAL'}")
        print(f"  Checks: {ok} PASS  {warn} WARN  {crit} CRITICAL  {skip} SKIP")
        print(f"{'='*50}\n")
        for c in checks:
            ico = {"PASS": "PASS", "WARN": "WARN", "CRITICAL": "CRITICAL", "SKIP": "SKIP"}
            det = c["dettaglio"]
            print(f"  {ico[c['esito']]} {c['check']}: {json.dumps(det) if not isinstance(det, str) else det}")

    sys.exit(1 if globale == "CRITICAL" else 0)


if __name__ == "__main__":
    main()
