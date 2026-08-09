select
    normalize_string(column0) as codice_voce,
    normalize_string(column1) as codice_gestione,
    normalize_string(column2) as descrizione_codice,
    try_cast(column3 as date) as data_inizio,
    try_cast(column4 as date) as data_fine,
    case when normalize_string(column0) like '9.%' then true else false end as is_titolo_9,
    case
        when normalize_string(column0) like '1.%' then 'Spese correnti'
        when normalize_string(column0) like '2.%' then 'Spese in conto capitale'
        when normalize_string(column0) like '3.%' then 'Incremento attivita'' finanziarie'
        when normalize_string(column0) like '4.%' then 'Rimborso prestiti'
        when normalize_string(column0) like '7.%' then 'Anticipazioni e partite di giro'
        else 'Altre spese'
    end as macro_area,
    case
        when normalize_string(column0) like '1.01.%' then 'Personale'
        when normalize_string(column0) like '1.02.%' then 'Imposte e tasse'
        when normalize_string(column0) like '1.03.%' then 'Acquisto beni e servizi'
        when normalize_string(column0) like '1.04.%' then 'Trasferimenti correnti'
        when normalize_string(column0) like '1.05.%' then 'Interessi passivi'
        when normalize_string(column0) like '1.07.%' then 'Poste correttive'
        when normalize_string(column0) like '2.01.%' then 'Investimenti fissi'
        when normalize_string(column0) like '2.02.%' then 'Contributi investimenti'
        when normalize_string(column0) like '2.03.%' then 'Trasferimenti c/capitale'
        when normalize_string(column0) like '4.%' then 'Rimborso prestiti'
        when normalize_string(column0) like '7.%' then 'Anticipazioni'
        else 'Altre spese'
    end as macro_categoria
from raw_input;
