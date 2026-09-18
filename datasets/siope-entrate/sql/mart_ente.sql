-- siope_entrate — mart_ente: totale entrate per ente × anno, con breakdown macro_categoria

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
    round(sum(importo_eur) filter (where macro_categoria = 'Imposte proprie'), 0) as imposte_proprie_eur,
    round(sum(importo_eur) filter (where macro_categoria = 'Trasferimenti correnti'), 0) as trasferimenti_correnti_eur,
    round(sum(importo_eur) filter (where macro_categoria = 'Entrate extratributarie'), 0) as extra_tributarie_eur,
    round(sum(importo_eur) filter (where macro_categoria = 'Contributi agli investimenti'), 0) as contrib_invest_eur,
    round(sum(importo_eur) filter (where macro_categoria = 'Fondi perequativi'), 0) as fondi_pereq_eur,
    round(sum(importo_eur) filter (where macro_categoria = 'Trasferimenti c/capitale'), 0) as trasf_capitale_eur,
    round(sum(importo_eur) filter (where is_titolo_9), 0) as titolo9_eur,
    count(distinct codice_voce) as n_voci,
    count(distinct periodo) as n_mesi
from clean_input
where codice_comparto is not null
group by anno, codice_ente
order by anno desc, totale_eur desc;
