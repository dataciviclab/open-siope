-- siope_entrate — mart_trend: trend multi-anno per ente
--
-- Legge TUTTI gli anni dal clean via `mart.tables[].years` + `source_layer: clean`
-- (view clean_input bindata dal toolkit sui parquet multi-anno). 1 riga = 1 ente.
-- Metrica base: totale_eur_no_titolo9 (escluso titolo 9 — base consigliata per i
-- confronti). Etichette dall'ultimo anno presente (arg_max). CAGR = tasso annuo
-- composto tra primo e ultimo anno; NULL se l'ente ha un solo anno.

with per_anno as (
    select
        anno,
        codice_ente,
        any_value(denominazione_ente) as denominazione_ente,
        any_value(tipo_ente) as tipo_ente,
        any_value(codice_comparto) as codice_comparto,
        any_value(descrizione_comparto) as descrizione_comparto,
        any_value(regione) as regione,
        round(coalesce(sum(importo_eur) filter (where not is_titolo_9), 0), 2) as totale_eur
    from clean_input
    group by anno, codice_ente
)
select
    codice_ente,
    arg_max(denominazione_ente, anno) as denominazione_ente,
    arg_max(tipo_ente, anno) as tipo_ente,
    arg_max(codice_comparto, anno) as codice_comparto,
    arg_max(descrizione_comparto, anno) as descrizione_comparto,
    arg_max(regione, anno) as regione,
    min(anno) as first_year,
    max(anno) as last_year,
    arg_min(totale_eur, anno) as totale_first,
    arg_max(totale_eur, anno) as totale_last,
    round(arg_max(totale_eur, anno) - arg_min(totale_eur, anno), 2) as delta_eur,
    round(
        100.0 * (arg_max(totale_eur, anno) - arg_min(totale_eur, anno))
        / nullif(arg_min(totale_eur, anno), 0),
        1
    ) as variazione_pct,
    round(
        100.0 * (
            power(
                arg_max(totale_eur, anno) / nullif(arg_min(totale_eur, anno), 0),
                1.0 / nullif(max(anno) - min(anno), 0)
            ) - 1
        ),
        1
    ) as cagr_pct
from per_anno
group by codice_ente;
