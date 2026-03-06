with anag_enti as (
    select *
    from read_parquet('out/data/clean/siope_anag_enti_seed/2024/siope_anag_enti_seed_2024_clean.parquet')
),
sottocomparti_map as (
    select *
    from read_parquet('out/data/clean/siope_anag_sottocomparti_seed/2024/siope_anag_sottocomparti_seed_2024_clean.parquet')
),
comparti_map as (
    select *
    from read_parquet('out/data/clean/siope_anag_comparti_seed/2024/siope_anag_comparti_seed_2024_clean.parquet')
),
base as (
    select
        e.codice_ente,
        e.anno,
        e.periodo,
        e.codice_voce,
        e.importo,
        a.denominazione_ente,
        a.tipo_ente,
        s.codice_sottocomparto,
        s.descrizione_sottocomparto,
        s.codice_comparto,
        c.descrizione_comparto,
        a.data_inizio as anag_data_inizio,
        a.data_fine as anag_data_fine,
        a.codice_col6,
        a.codice_col7,
        a.codice_col8,
        case
            when a.codice_ente is not null then true
            else false
        end as has_anag_match,
        case
            when s.codice_sottocomparto is not null then 'tipo_ente_direct'
            when a.codice_ente is not null then 'anag_only'
            else 'no_anag_match'
        end as comparto_mapping_source
    from clean_input e
    left join anag_enti a
        on e.codice_ente = a.codice_ente
       and make_date(e.anno, 12, 31) between a.data_inizio and a.data_fine
    left join sottocomparti_map s
        on a.tipo_ente = s.codice_sottocomparto
    left join comparti_map c
        on s.codice_comparto = c.codice_comparto
)
select
    *
from base
where tipo_ente = 'COMUNE'
  and codice_comparto = 'PRO';
