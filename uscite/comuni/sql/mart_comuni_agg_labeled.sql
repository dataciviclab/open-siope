with anag_enti as (
    select * from read_parquet('{support.enti.mart}')
),
sottocomparti_map as (
    select * from read_parquet('{support.sottocomparti.mart}')
),
comparti_map as (
    select * from read_parquet('{support.comparti.mart}')
),
codgest as (
    select * from read_parquet('{support.codgest_uscite.mart}')
),
regprov as (
    select * from read_parquet('{support.regprov.mart}')
),
comuni as (
    select
        e.codice_ente,
        e.anno,
        e.codice_voce,
        a.denominazione_ente,
        a.tipo_ente,
        a.codice_provincia,
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
        a.codice_provincia,
        s.codice_sottocomparto,
        s.descrizione_sottocomparto,
        s.codice_comparto,
        c.descrizione_comparto
)
select
    c.codice_ente,
    c.anno,
    c.codice_voce,
    c.denominazione_ente,
    c.tipo_ente,
    c.codice_provincia,
    r.provincia,
    r.regione,
    c.codice_sottocomparto,
    c.descrizione_sottocomparto,
    c.codice_comparto,
    c.descrizione_comparto,
    c.importo_totale,
    c.righe,
    c.periodi_coperti,
    c.periodo_min,
    c.periodo_max,
    c.importo_totale / 100.0 as importo_totale_eur,
    g.descrizione_codice,
    g.data_inizio as codgest_data_inizio,
    g.data_fine as codgest_data_fine,
    case
        when g.codice_voce is not null then true
        else false
    end as has_codgest_match
from comuni c
left join regprov r
    on c.codice_provincia = r.codice_provincia
left join codgest g
    on c.codice_comparto = g.codice_gestione
   and c.codice_voce = g.codice_voce
   and make_date(c.anno, 12, 31) between g.data_inizio and g.data_fine;
