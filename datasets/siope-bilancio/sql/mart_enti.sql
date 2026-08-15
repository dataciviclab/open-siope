-- mart_enti — SIOPE: benchmark entrate/uscite per ente × tipo_ente
--
-- Entrate/uscite totali per singolo ente (codice_ente).
-- Benchmark per tipo_ente: media nazionale, percentile, fascia.
-- Confronto tra enti dello stesso tipo (es. COMUNE vs COMUNE).

with
enti_bilancio as (
    select
        anno,
        codice_ente,
        denominazione_ente,
        tipo_ente,
        codice_istat_comune,
        provincia,
        regione,
        descrizione_comparto as comparto,
        round(sum(case when lato = 'entrate' then importo_eur end), 0) as entrate_eur,
        round(sum(case when lato = 'uscite' then importo_eur end), 0) as uscite_eur,
        round(
            coalesce(sum(case when lato = 'entrate' then importo_eur end), 0)
            - coalesce(sum(case when lato = 'uscite' then importo_eur end), 0)
        , 0) as saldo_eur
    from clean_input
    where codice_ente is not null
      and codice_ente != ''
    group by anno, codice_ente, denominazione_ente, tipo_ente, codice_istat_comune, provincia, regione, descrizione_comparto
)
select
    *,
    -- Benchmark per tipo ente: media entrate
    round(avg(entrate_eur) over (partition by anno, tipo_ente), 0) as media_entrate_per_tipo,
    -- Media uscite per tipo ente
    round(avg(uscite_eur) over (partition by anno, tipo_ente), 0) as media_uscite_per_tipo,
    -- Deviazione standard entrate per tipo ente
    round(stddev(entrate_eur) over (partition by anno, tipo_ente), 0) as std_entrate_per_tipo,
    -- Percentile entrate per tipo ente
    case
        when entrate_eur is null then null
        else round(percent_rank() over (partition by anno, tipo_ente order by entrate_eur), 4)
    end as percentile_entrate,
    -- Percentile uscite per tipo ente
    case
        when uscite_eur is null then null
        else round(percent_rank() over (partition by anno, tipo_ente order by uscite_eur), 4)
    end as percentile_uscite,
    -- Fascia entrate
    case
        when entrate_eur is null then null
        when percent_rank() over (partition by anno, tipo_ente order by entrate_eur) >= 0.8 then 'ELEVATO'
        when percent_rank() over (partition by anno, tipo_ente order by entrate_eur) >= 0.6 then 'SOPRA_MEDIA'
        when percent_rank() over (partition by anno, tipo_ente order by entrate_eur) >= 0.4 then 'MEDIA'
        when percent_rank() over (partition by anno, tipo_ente order by entrate_eur) >= 0.2 then 'SOTTO_MEDIA'
        else 'BASSO'
    end as fascia_entrate
from enti_bilancio
order by anno desc, tipo_ente, entrate_eur desc;
