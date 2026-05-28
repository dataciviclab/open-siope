select
    trim(column0) as codice_voce,
    trim(column1) as codice_gestione,
    trim(column2) as descrizione_codice,
    try_cast(column3 as date) as data_inizio,
    try_cast(column4 as date) as data_fine,
    case when trim(column0) like '9.%' then true else false end as is_titolo_9,
    case
        when trim(column0) like '1.01.%' then 'Imposte proprie'
        when trim(column0) like '1.03.%' then 'Fondi perequativi'
        when trim(column0) like '2.01.%' then 'Trasferimenti correnti'
        when trim(column0) like '4.02.%' then 'Contributi agli investimenti'
        else 'Altro'
    end as macro_categoria_v2
from raw_input;
