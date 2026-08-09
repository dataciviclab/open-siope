-- siope_entrate — mart_san: entrate annuali per ente e codice voce nel comparto SAN (ASL, AO, IRCCS, policlinici).
select
    codice_ente,
    anno,
    codice_voce,
    any_value(denominazione_ente) as denominazione_ente,
    any_value(tipo_ente) as tipo_ente,
    any_value(codice_provincia) as codice_provincia,
    any_value(provincia) as provincia,
    any_value(regione) as regione,
    any_value(codice_sottocomparto) as codice_sottocomparto,
    any_value(descrizione_sottocomparto) as descrizione_sottocomparto,
    any_value(codice_comparto) as codice_comparto,
    any_value(descrizione_comparto) as descrizione_comparto,
    sum(importo) as importo_totale,
    count(*) as righe,
    count(distinct periodo) as periodi_coperti,
    min(periodo) as periodo_min,
    max(periodo) as periodo_max,
    sum(importo) / 100.0 as importo_totale_eur,
    min(is_titolo_9) as is_titolo_9,
    min(macro_categoria_v2) as macro_categoria_v2,
    any_value(descrizione_codice) as descrizione_codice,
    min(has_codgest_match) as has_codgest_match
from clean_input
where codice_comparto = 'SAN'
group by codice_ente, anno, codice_voce;
