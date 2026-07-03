with entrate as (
    select
        'entrate' as lato,
        codice_comparto,
        anno, periodo,
        codice_ente, codice_voce,
        denominazione_ente, tipo_ente,
        codice_istat_comune,
        codice_provincia, provincia, regione,
        codice_sottocomparto, descrizione_sottocomparto,
        descrizione_comparto,
        is_titolo_9, macro_categoria_v2,
        null::varchar as macro_area,
        null::varchar as macro_categoria,
        descrizione_codice,
        has_codgest_match,
        importo,
        importo_eur
    from read_parquet('{root}/data/clean/siope_entrate/{year}/siope_entrate_{year}_clean.parquet')
),
uscite as (
    select
        'uscite' as lato,
        codice_comparto,
        anno, periodo,
        codice_ente, codice_voce,
        denominazione_ente, tipo_ente,
        codice_istat_comune,
        codice_provincia, provincia, regione,
        codice_sottocomparto, descrizione_sottocomparto,
        descrizione_comparto,
        is_titolo_9,
        null::varchar as macro_categoria_v2,
        macro_area,
        macro_categoria,
        descrizione_codice,
        has_codgest_match,
        importo,
        importo_eur
    from read_parquet('{root}/data/clean/siope_uscite/{year}/siope_uscite_{year}_clean.parquet')
)
select * from entrate
union all
select * from uscite;
