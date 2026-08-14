-- mart_sintesi — SIOPE: entrate/uscite per comparto × regione × anno
--
-- Rimpiazza il vecchio mart.sql (SELECT *).
-- ATTENZIONE: lato nel dato è minuscolo ("entrate"/"uscite").

with
-- Enti totali per (anno, regione, comparto) — senza lato
enti_per_area as (
    select
        anno,
        regione,
        descrizione_comparto as comparto,
        count(distinct codice_ente) as enti
    from clean_input
    where regione is not null and regione != ''
    group by anno, regione, descrizione_comparto
),
-- Importi per (anno, regione, comparto, lato) — una riga per lato
importi_per_lato as (
    select
        anno,
        regione,
        descrizione_comparto as comparto,
        lato,
        round(sum(importo_eur), 0) as totale_eur
    from clean_input
    where regione is not null and regione != ''
    group by anno, regione, descrizione_comparto, lato
)
select
    i.anno,
    i.regione,
    i.comparto,
    e.enti,
    round(sum(case when i.lato = 'entrate' then i.totale_eur end), 0) as entrate_eur,
    round(sum(case when i.lato = 'uscite' then i.totale_eur end), 0) as uscite_eur,
    round(
        coalesce(sum(case when i.lato = 'entrate' then i.totale_eur end), 0)
        - coalesce(sum(case when i.lato = 'uscite' then i.totale_eur end), 0)
    , 0) as saldo_eur,
    case
        when sum(case when i.lato = 'entrate' then i.totale_eur end) > 0
        then round(
            sum(case when i.lato = 'uscite' then i.totale_eur end)
            / sum(case when i.lato = 'entrate' then i.totale_eur end) * 100
        , 1)
    end as rapporto_uscite_entrate_pct
from importi_per_lato i
left join enti_per_area e
    on i.anno = e.anno and i.regione = e.regione and i.comparto = e.comparto
group by i.anno, i.regione, i.comparto, e.enti
order by i.anno desc, i.regione, i.comparto;
