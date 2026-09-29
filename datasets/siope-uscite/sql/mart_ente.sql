-- siope_uscite — mart_ente: totale uscite per ente × anno, con breakdown macro_categoria
--
-- Grano: ente × anno.
-- Risponde a: "quanto spende l'ente, e come si compone la spesa".

select
    anno,
    codice_ente,
    any_value(denominazione_ente) as denominazione_ente,
    any_value(tipo_ente) as tipo_ente,
    any_value(codice_comparto) as codice_comparto,
    any_value(descrizione_comparto) as descrizione_comparto,
    any_value(regione) as regione,
    any_value(provincia) as provincia,
    round(coalesce(sum(importo_eur) filter (where not is_titolo_9), 0), 0) as totale_eur,
    round(sum(importo_eur) filter (where macro_categoria = 'Personale'), 0) as personale_eur,
    round(sum(importo_eur) filter (where macro_categoria = 'Acquisto beni e servizi'), 0) as beni_servizi_eur,
    round(sum(importo_eur) filter (where macro_categoria = 'Trasferimenti correnti'), 0) as trasferimenti_correnti_eur,
    round(sum(importo_eur) filter (where macro_categoria = 'Investimenti fissi'), 0) as investimenti_eur,
    round(sum(importo_eur) filter (where macro_categoria = 'Interessi passivi'), 0) as interessi_eur,
    round(sum(importo_eur) filter (where macro_categoria = 'Rimborso prestiti'), 0) as rimborso_prestiti_eur,
    round(sum(importo_eur) filter (where macro_categoria = 'Imposte e tasse'), 0) as imposte_eur,
    round(sum(importo_eur) filter (where macro_categoria = 'Trasferimenti c/capitale'), 0) as trasf_capitale_eur,
    round(sum(importo_eur) filter (where macro_categoria = 'Contributi investimenti'), 0) as contrib_invest_eur,
    round(sum(importo_eur) filter (where is_titolo_9), 0) as titolo9_eur,
    count(distinct codice_voce) as n_voci,
    count(distinct periodo) as n_mesi
from clean_input
where codice_comparto is not null
group by anno, codice_ente
order by anno desc, totale_eur desc;
