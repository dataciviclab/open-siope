-- mart_trend — SIOPE: CAGR entrate/uscite per comparto × regione (multi-anno)
--
-- Legge TUTTI gli anni dal clean via mart.tables[].years + source_layer=clean
-- (il toolkit unisce i parquet multi-anno in clean_input). 1 riga = 1 (regione,
-- comparto).
--
-- SEMANTICA ANNI PARZIALI: il CAGR/delta sono calcolati SOLO sugli anni
-- COMPLETI (n_periodi >= 12). L'anno in corso parziale (es. 2026 a 8 mesi)
-- non entra nel calcolo della tendenza — altrimenti produrrebbe crolli/boom
-- fantasma (l'anno parziale vale ~2/3 di un anno intero). La parzialità è
-- segnalata da `ultimo_anno_parziale` e `mesi_ultimo_anno_parziale`.

with
all_clean as (
    select anno, regione, descrizione_comparto as comparto, lato, importo_eur, n_periodi
    from clean_input
    where regione is not null and regione != ''
),
per_anno as (
    select
        anno,
        regione,
        comparto,
        max(n_periodi) as n_periodi,
        round(sum(case when lato = 'entrate' then importo_eur end), 0) as entrate_eur,
        round(sum(case when lato = 'uscite' then importo_eur end), 0) as uscite_eur
    from all_clean
    group by anno, regione, comparto
),
-- solo anni completi per la tendenza
completi as (
    select * from per_anno where n_periodi >= 12
),
trend as (
    select
        regione,
        comparto,
        min(anno) as primo_anno,
        max(anno) as ultimo_anno,
        count(*) as anni_coperti,
        min(entrate_eur) filter (where anno = (select min(a2.anno) from completi a2 where a2.regione = p.regione and a2.comparto = p.comparto)) as entrate_iniziali,
        max(entrate_eur) filter (where anno = (select max(a2.anno) from completi a2 where a2.regione = p.regione and a2.comparto = p.comparto)) as entrate_finali,
        round(
            max(entrate_eur) filter (where anno = (select max(a2.anno) from completi a2 where a2.regione = p.regione and a2.comparto = p.comparto))
            - min(entrate_eur) filter (where anno = (select min(a2.anno) from completi a2 where a2.regione = p.regione and a2.comparto = p.comparto))
        , 0) as delta_entrate_eur,
        case
            when min(entrate_eur) filter (where anno = (select min(a2.anno) from completi a2 where a2.regione = p.regione and a2.comparto = p.comparto)) > 0
                 and max(anno) > min(anno)
            then round((power(
                max(entrate_eur) filter (where anno = (select max(a2.anno) from completi a2 where a2.regione = p.regione and a2.comparto = p.comparto))
                / nullif(min(entrate_eur) filter (where anno = (select min(a2.anno) from completi a2 where a2.regione = p.regione and a2.comparto = p.comparto)), 0),
                1.0 / (max(anno) - min(anno))
            ) - 1) * 100, 2)
        end as cagr_entrate_pct,
        case
            when min(uscite_eur) filter (where anno = (select min(a2.anno) from completi a2 where a2.regione = p.regione and a2.comparto = p.comparto)) > 0
                 and max(anno) > min(anno)
            then round((power(
                max(uscite_eur) filter (where anno = (select max(a2.anno) from completi a2 where a2.regione = p.regione and a2.comparto = p.comparto))
                / nullif(min(uscite_eur) filter (where anno = (select min(a2.anno) from completi a2 where a2.regione = p.regione and a2.comparto = p.comparto)), 0),
                1.0 / (max(anno) - min(anno))
            ) - 1) * 100, 2)
        end as cagr_uscite_pct,
        -- flag parzialità: ultimo anno osservato NON completo (n_periodi < 12)
        (select max(a3.anno) from per_anno a3
         where a3.regione = p.regione and a3.comparto = p.comparto and a3.n_periodi < 12) as ultimo_anno_parziale
    from completi p
    group by regione, comparto
)
select
    regione,
    comparto,
    primo_anno,
    ultimo_anno,
    anni_coperti,
    round(entrate_iniziali / 1e9, 1) as entrate_iniziali_mld,
    round(entrate_finali / 1e9, 1) as entrate_finali_mld,
    round(delta_entrate_eur / 1e9, 1) as delta_entrate_mld,
    cagr_entrate_pct,
    cagr_uscite_pct,
    case
        when cagr_entrate_pct is null then null
        when cagr_entrate_pct > 10 then 'CRESCITA_FORTE'
        when cagr_entrate_pct > 3 then 'CRESCITA_MODERATA'
        when cagr_entrate_pct > -3 then 'STABILE'
        when cagr_entrate_pct > -10 then 'CALO_MODERATO'
        else 'CALO_FORTE'
    end as segnale_trend_entrate,
    ultimo_anno_parziale,
    (select a4.n_periodi from per_anno a4
     where a4.regione = trend.regione and a4.comparto = trend.comparto
       and a4.anno = trend.ultimo_anno_parziale) as mesi_ultimo_anno_parziale
from trend
where comparto not in ('STATO')
order by abs(coalesce(delta_entrate_eur, 0)) desc;
