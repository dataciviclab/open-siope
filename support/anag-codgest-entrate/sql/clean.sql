with base as (
    select
        normalize_string(column0) as codice_voce,
        normalize_string(column1) as codice_gestione,
        normalize_string(column2) as descrizione_codice,
        try_cast(column3 as date) as data_inizio,
        try_cast(column4 as date) as data_fine
    from raw_input
)
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
    -- macro_categoria_v2: prima i codici strutturati (piano dei conti puntato),
    -- poi fallback sulla DESCRIZIONE per i codici compatti (SAN/CDC/...)
    -- la cui classificazione non è nel codice ma nel testo.
    case
        -- ── codici strutturati (piano dei conti puntato) ──
        when b.codice_voce like '1.01.%' then 'Imposte proprie'
        when b.codice_voce like '1.03.%' then 'Fondi perequativi'
        when b.codice_voce like '2.01.%' then 'Trasferimenti correnti'
        when b.codice_voce like '4.02.%' then 'Contributi agli investimenti'
        -- ── fallback: descrizione (compatti SAN/CDC/...) ──
        when b.descrizione_codice ilike '%contributi agli investimenti%' then 'Contributi agli investimenti'
        when b.descrizione_codice ilike '%trasferimenti correnti%' then 'Trasferimenti correnti'
        when b.descrizione_codice ilike '%contributi e trasferimenti%' then 'Trasferimenti correnti'
        when b.descrizione_codice ilike '%trasferimenti%' then 'Trasferimenti correnti'
        when b.descrizione_codice ilike '%contributi%' then 'Trasferimenti correnti'
        when b.descrizione_codice ilike '%fondo perequativo%' then 'Fondi perequativi'
        when b.descrizione_codice ilike '%imposta%' or b.descrizione_codice ilike '%addizional%'
             or b.descrizione_codice ilike '%irap%'
             or regexp_matches(b.descrizione_codice, '(?i)\biva\b')
             or regexp_matches(b.descrizione_codice, '(?i)\btari\b')
             or regexp_matches(b.descrizione_codice, '(?i)\bimu\b')
             or regexp_matches(b.descrizione_codice, '(?i)\btribut\b')
             or regexp_matches(b.descrizione_codice, '(?i)\bcanone\b') then 'Imposte proprie'
        else 'Altro'
    end as macro_categoria_v2
from base b;
