with base as (
    select
        trim(column0) as codice_ente,
        try_cast(column1 as integer) as anno,
        trim(column2) as periodo,
        trim(column3) as codice_voce,
        try_cast(column4 as bigint) as importo
    from raw_input
)
select
    b.codice_ente,
    b.anno,
    b.periodo,
    b.codice_voce,
    b.importo,
    b.importo / 100.0 as importo_eur,
    a.denominazione_ente,
    a.tipo_ente,
    a.codice_istat_comune,
    a.codice_provincia,
    r.provincia,
    r.regione,
    s.codice_sottocomparto,
    s.descrizione_sottocomparto,
    s.codice_comparto,
    c.descrizione_comparto,
    coalesce(g.is_titolo_9, false) as is_titolo_9,
    coalesce(g.macro_area, 'Altre spese') as macro_area,
    coalesce(g.macro_categoria, 'Altre spese') as macro_categoria,
    g.descrizione_codice,
    case when g.codice_voce is not null then true else false end as has_codgest_match
from base b
left join read_parquet('{support.enti.mart}') a
    on b.codice_ente = a.codice_ente
   and make_date(b.anno, 12, 31) between a.data_inizio and a.data_fine
left join read_parquet('{support.sottocomparti.mart}') s
    on a.tipo_ente = s.codice_sottocomparto
left join read_parquet('{support.comparti.mart}') c
    on s.codice_comparto = c.codice_comparto
left join read_parquet('{support.regprov.mart}') r
    on a.codice_provincia = r.codice_provincia
left join read_parquet('{support.codgest_uscite.mart}') g
    on s.codice_comparto = g.codice_gestione
   and b.codice_voce = g.codice_voce
   and make_date(b.anno, 12, 31) between g.data_inizio and g.data_fine;
