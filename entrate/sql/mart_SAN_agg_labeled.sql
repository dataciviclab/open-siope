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
    select * from read_parquet('{support.codgest_entrate.mart}')
),
regprov as (
    select * from read_parquet('{support.regprov.mart}')
),
entrate_agg as (
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
    where s.codice_comparto = 'SAN'
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
    a.codice_ente,
    a.anno,
    a.codice_voce,
    a.denominazione_ente,
    a.tipo_ente,
    a.codice_provincia,
    r.provincia,
    r.regione,
    a.codice_sottocomparto,
    a.descrizione_sottocomparto,
    a.codice_comparto,
    a.descrizione_comparto,
    a.importo_totale,
    a.righe,
    a.periodi_coperti,
    a.periodo_min,
    a.periodo_max,
    a.importo_totale / 100.0 as importo_totale_eur,
    g.is_titolo_9,
    g.macro_categoria_v2,
    g.descrizione_codice,
    g.data_inizio as codgest_data_inizio,
    g.data_fine as codgest_data_fine,
    case
        when g.codice_voce is not null then true
        else false
    end as has_codgest_match
from entrate_agg a
left join regprov r
    on a.codice_provincia = r.codice_provincia
left join codgest g
    on a.codice_comparto = g.codice_gestione
   and a.codice_voce = g.codice_voce
   and make_date(a.anno, 12, 31) between g.data_inizio and g.data_fine;
