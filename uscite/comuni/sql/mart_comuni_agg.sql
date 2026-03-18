with anag_enti_seed as (
    select
        *,
        regexp_extract(replace(filename, '\', '/'), '.*/([0-9]{4})/[^/]+$', 1)::integer as snapshot_year
    from read_parquet('out/data/clean/siope_anag_enti_seed/*/*.parquet', filename = true)
),
anag_enti as (
    select * exclude (filename, snapshot_year)
    from anag_enti_seed
    where snapshot_year = (select max(snapshot_year) from anag_enti_seed)
),
sottocomparti_seed as (
    select
        *,
        regexp_extract(replace(filename, '\', '/'), '.*/([0-9]{4})/[^/]+$', 1)::integer as snapshot_year
    from read_parquet('out/data/clean/siope_anag_sottocomparti_seed/*/*.parquet', filename = true)
),
sottocomparti_map as (
    select * exclude (filename, snapshot_year)
    from sottocomparti_seed
    where snapshot_year = (select max(snapshot_year) from sottocomparti_seed)
),
comparti_seed as (
    select
        *,
        regexp_extract(replace(filename, '\', '/'), '.*/([0-9]{4})/[^/]+$', 1)::integer as snapshot_year
    from read_parquet('out/data/clean/siope_anag_comparti_seed/*/*.parquet', filename = true)
),
comparti_map as (
    select * exclude (filename, snapshot_year)
    from comparti_seed
    where snapshot_year = (select max(snapshot_year) from comparti_seed)
),
base as (
    select
        e.codice_ente,
        e.anno,
        e.codice_voce,
        a.denominazione_ente,
        a.tipo_ente,
        s.codice_sottocomparto,
        s.descrizione_sottocomparto,
        s.codice_comparto,
        c.descrizione_comparto,
        sum(e.importo) as importo_totale,
        count(*) as righe,
        count(distinct e.periodo) as periodi_coperti,
        min(e.periodo) as periodo_min,
        max(e.periodo) as periodo_max
    from clean_input e
    left join anag_enti a
        on e.codice_ente = a.codice_ente
       and make_date(e.anno, 12, 31) between a.data_inizio and a.data_fine
    left join sottocomparti_map s
        on a.tipo_ente = s.codice_sottocomparto
    left join comparti_map c
        on s.codice_comparto = c.codice_comparto
    where a.tipo_ente = 'COMUNE'
      and s.codice_comparto = 'PRO'
    group by
        e.codice_ente,
        e.anno,
        e.codice_voce,
        a.denominazione_ente,
        a.tipo_ente,
        s.codice_sottocomparto,
        s.descrizione_sottocomparto,
        s.codice_comparto,
        c.descrizione_comparto
)
select *
from base;
