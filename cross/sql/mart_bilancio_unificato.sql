with entrate_pro as (
    select
        'entrate' as lato,
        'PRO' as comparto,
        anno, codice_ente, codice_voce,
        denominazione_ente, tipo_ente,
        codice_provincia, provincia, regione,
        macro_categoria_v2, is_titolo_9,
        descrizione_codice,
        importo_totale_eur
    from read_parquet('{root}/data/mart/siope_entrate_comuni/*/siope_entrate_comuni_agg_labeled.parquet')
),
entrate_reg as (
    select
        'entrate' as lato,
        'REG' as comparto,
        anno, codice_ente, codice_voce,
        denominazione_ente, tipo_ente,
        codice_provincia, provincia, regione,
        macro_categoria_v2, is_titolo_9,
        descrizione_codice,
        importo_totale_eur
    from read_parquet('{root}/data/mart/siope_entrate_comuni/*/siope_entrate_regioni_agg_labeled.parquet')
),
entrate_san as (
    select
        'entrate' as lato,
        'SAN' as comparto,
        anno, codice_ente, codice_voce,
        denominazione_ente, tipo_ente,
        codice_provincia, provincia, regione,
        macro_categoria_v2, is_titolo_9,
        descrizione_codice,
        importo_totale_eur
    from read_parquet('{root}/data/mart/siope_entrate_comuni/*/siope_entrate_sanita_agg_labeled.parquet')
),
entrate_uni as (
    select
        'entrate' as lato,
        'UNI' as comparto,
        anno, codice_ente, codice_voce,
        denominazione_ente, tipo_ente,
        codice_provincia, provincia, regione,
        macro_categoria_v2, is_titolo_9,
        descrizione_codice,
        importo_totale_eur
    from read_parquet('{root}/data/mart/siope_entrate_comuni/*/siope_entrate_universita_agg_labeled.parquet')
),
uscite_pro as (
    select
        'uscite' as lato,
        'PRO' as comparto,
        anno, codice_ente, codice_voce,
        denominazione_ente, tipo_ente,
        codice_provincia, provincia, regione,
        is_titolo_9,
        null::varchar as macro_categoria_v2,
        macro_area,
        macro_categoria,
        descrizione_codice,
        importo_totale_eur
    from read_parquet('{root}/data/mart/siope_uscite_comuni/*/siope_uscite_comuni_agg_labeled.parquet')
),
uscite_reg as (
    select
        'uscite' as lato,
        'REG' as comparto,
        anno, codice_ente, codice_voce,
        denominazione_ente, tipo_ente,
        codice_provincia, provincia, regione,
        is_titolo_9,
        null::varchar as macro_categoria_v2,
        macro_area,
        macro_categoria,
        descrizione_codice,
        importo_totale_eur
    from read_parquet('{root}/data/mart/siope_uscite_comuni/*/siope_uscite_regioni_agg_labeled.parquet')
),
uscite_san as (
    select
        'uscite' as lato,
        'SAN' as comparto,
        anno, codice_ente, codice_voce,
        denominazione_ente, tipo_ente,
        codice_provincia, provincia, regione,
        is_titolo_9,
        null::varchar as macro_categoria_v2,
        macro_area,
        macro_categoria,
        descrizione_codice,
        importo_totale_eur
    from read_parquet('{root}/data/mart/siope_uscite_comuni/*/siope_uscite_sanita_agg_labeled.parquet')
),
uscite_uni as (
    select
        'uscite' as lato,
        'UNI' as comparto,
        anno, codice_ente, codice_voce,
        denominazione_ente, tipo_ente,
        codice_provincia, provincia, regione,
        is_titolo_9,
        null::varchar as macro_categoria_v2,
        macro_area,
        macro_categoria,
        descrizione_codice,
        importo_totale_eur
    from read_parquet('{root}/data/mart/siope_uscite_comuni/*/siope_uscite_universita_agg_labeled.parquet')
)
select * from entrate_pro
union all select * from entrate_reg
union all select * from entrate_san
union all select * from entrate_uni
union all select * from uscite_pro
union all select * from uscite_reg
union all select * from uscite_san
union all select * from uscite_uni;
