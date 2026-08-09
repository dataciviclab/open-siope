-- siope_uscite — mart_sintesi: totale uscite per ente e anno (scheda ente annuale)
--
-- Grano: ente × anno. 1 riga = 1 (anno, ente). Roll-up dei mart per-comparto:
-- risponde a "quanto spende l'ente, con quante voci e per quanti mesi".
-- totale_eur_no_titolo9 esclude le voci tecniche (titolo 9) — base consigliata
-- per confronti descrittivi (vedi docs/metodologia.md).

select
    anno,
    codice_ente,
    any_value(denominazione_ente) as denominazione_ente,
    any_value(tipo_ente) as tipo_ente,
    any_value(codice_comparto) as codice_comparto,
    any_value(descrizione_comparto) as descrizione_comparto,
    any_value(codice_istat_comune) as codice_istat_comune,
    any_value(codice_provincia) as codice_provincia,
    any_value(provincia) as provincia,
    any_value(regione) as regione,
    round(sum(importo_eur), 2) as totale_eur,
    round(coalesce(sum(importo_eur) filter (where not is_titolo_9), 0), 2) as totale_eur_no_titolo9,
    count(distinct codice_voce) as n_voci,
    count(distinct periodo) as n_mesi
from clean_input
group by anno, codice_ente;
