-- siope_bilancio_unificato — clean: aggregazione ANNUALE entrate+uscite
--
-- Legge i clean mensili di entrate/uscite (locali, placeholder {year}) e
-- aggrega per ente × voce × anno, con colonna lato ('entrate'/'uscite').
-- Tutti i comparti (PRO, REG, SAN, UNI, STA, CDC, ...). La classificazione
-- macro_categoria viene dal lato rispettivo (entrate: macro_categoria_v2;
-- uscite: macro_categoria).

with entrate as (
    select
        anno, codice_ente, denominazione_ente, tipo_ente,
        codice_comparto, descrizione_comparto, codice_sottocomparto, descrizione_sottocomparto,
        codice_istat_comune, codice_provincia, provincia, regione,
        codice_voce, descrizione_codice, has_codgest_match, is_titolo_9,
        macro_categoria_v2 as macro_categoria,
        round(sum(importo_eur), 2) as importo_eur
    from read_parquet('out/data/clean/siope_entrate/{year}/siope_entrate_{year}_clean.parquet')
    group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17
),
uscite as (
    select
        anno, codice_ente, denominazione_ente, tipo_ente,
        codice_comparto, descrizione_comparto, codice_sottocomparto, descrizione_sottocomparto,
        codice_istat_comune, codice_provincia, provincia, regione,
        codice_voce, descrizione_codice, has_codgest_match, is_titolo_9,
        macro_categoria as macro_categoria,
        round(sum(importo_eur), 2) as importo_eur
    from read_parquet('out/data/clean/siope_uscite/{year}/siope_uscite_{year}_clean.parquet')
    group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17
)
select 'entrate' as lato, * from entrate
union all
select 'uscite' as lato, * from uscite;
