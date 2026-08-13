with base as (
    select
        normalize_string(column0) as codice_voce,
        normalize_string(column1) as codice_gestione,
        normalize_string(column2) as descrizione_codice,
        try_cast(column3 as date) as data_inizio,
        try_cast(column4 as date) as data_fine
    from raw_input
),
classificato as (
    select
        b.codice_voce,
        b.codice_gestione,
        b.descrizione_codice,
        b.data_inizio,
        b.data_fine,
        -- Partite di giro: codici puntati 9.x e compatti 999x (regolarizzare)
        case
            when b.codice_voce like '9.%' or b.codice_voce like '999%' then true
            else false
        end as is_titolo_9,
        -- macro_categoria: prima i codici strutturati (piano dei conti puntato),
        -- poi fallback sulla DESCRIZIONE per macroaggregati alfanumerici (STA)
        -- e codici compatti (SAN/CDC/...), il cui codice non ha la struttura a punti.
        case
            -- ── codici strutturati (piano dei conti puntato) ──
            when b.codice_voce like '1.01.%' then 'Personale'
            when b.codice_voce like '1.02.%' then 'Imposte e tasse'
            when b.codice_voce like '1.03.%' then 'Acquisto beni e servizi'
            when b.codice_voce like '1.04.%' then 'Trasferimenti correnti'
            when b.codice_voce like '1.05.%' then 'Interessi passivi'
            when b.codice_voce like '1.07.%' then 'Poste correttive'
            when b.codice_voce like '2.01.%' then 'Investimenti fissi'
            when b.codice_voce like '2.02.%' then 'Contributi investimenti'
            when b.codice_voce like '2.03.%' then 'Trasferimenti c/capitale'
            when b.codice_voce like '3.%' then 'Incremento attivita'' finanziarie'
            when b.codice_voce like '4.%' then 'Rimborso prestiti'
            when b.codice_voce like '7.%' then 'Anticipazioni'
            -- ── fallback: descrizione (macroaggregati STA A/I, compatti SAN/...) ──
            when b.descrizione_codice ilike '%contributi agli investimenti%' then 'Contributi investimenti'
            when b.descrizione_codice ilike '%trasferimenti in conto capitale%' then 'Trasferimenti c/capitale'
            when b.descrizione_codice ilike '%investimenti fissi%' then 'Investimenti fissi'
            when b.descrizione_codice ilike '%fabbricati%' then 'Investimenti fissi'
            when b.descrizione_codice ilike '%acquisizioni di attivita'' finanziarie%' then 'Incremento attivita'' finanziarie'
            when b.descrizione_codice ilike '%rimborso passivita'' finanziarie%' then 'Rimborso prestiti'
            when b.descrizione_codice ilike '%anticipazioni%' then 'Anticipazioni'
            when b.descrizione_codice ilike '%trasferimenti correnti%' then 'Trasferimenti correnti'
            when b.descrizione_codice ilike '%trasferimenti%' then 'Trasferimenti correnti'
            when b.descrizione_codice ilike '%contributi%' then 'Trasferimenti correnti'
            when b.descrizione_codice ilike '%personale%' or b.descrizione_codice ilike '%competenz%' then 'Personale'
            when b.descrizione_codice ilike '%interessi passivi%' then 'Interessi passivi'
            when b.descrizione_codice ilike '%poste correttive%' then 'Poste correttive'
            when b.descrizione_codice ilike '%imposte%' or b.descrizione_codice ilike '%tasse%'
                 or b.descrizione_codice ilike '%iva%' or b.descrizione_codice ilike '%irap%' then 'Imposte e tasse'
            when b.descrizione_codice ilike '%prodott%' or b.descrizione_codice ilike '%farmaceut%'
                 or b.descrizione_codice ilike '%alimentari%' or b.descrizione_codice ilike '%materiali%'
                 or b.descrizione_codice ilike '%beni di consumo%' or b.descrizione_codice ilike '%dispositivi%' then 'Acquisto beni e servizi'
            when b.descrizione_codice ilike '%servizi%' or b.descrizione_codice ilike '%formazione%'
                 or b.descrizione_codice ilike '%consulenz%' or b.descrizione_codice ilike '%manutenzion%'
                 or b.descrizione_codice ilike '%riparazion%' or b.descrizione_codice ilike '%ristorazion%'
                 or b.descrizione_codice ilike '%utenz%' or b.descrizione_codice ilike '%prestazioni%'
                 or b.descrizione_codice ilike '%noleggi%' then 'Acquisto beni e servizi'
            else 'Altre spese'
        end as macro_categoria
    from base b
)
select
    c.codice_voce,
    c.codice_gestione,
    c.descrizione_codice,
    c.data_inizio,
    c.data_fine,
    c.is_titolo_9,
    c.macro_categoria,
    -- macro_area derivata dalla categoria (coerenza garantita)
    case
        when c.macro_categoria in ('Personale', 'Imposte e tasse', 'Acquisto beni e servizi',
                                   'Trasferimenti correnti', 'Interessi passivi', 'Poste correttive') then 'Spese correnti'
        when c.macro_categoria in ('Investimenti fissi', 'Contributi investimenti', 'Trasferimenti c/capitale') then 'Spese in conto capitale'
        when c.macro_categoria = 'Incremento attivita'' finanziarie' then 'Incremento attivita'' finanziarie'
        when c.macro_categoria = 'Rimborso prestiti' then 'Rimborso prestiti'
        when c.macro_categoria = 'Anticipazioni' then 'Anticipazioni e partite di giro'
        else 'Altre spese'
    end as macro_area
from classificato c;
