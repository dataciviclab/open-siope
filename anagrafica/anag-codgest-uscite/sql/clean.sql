select
    trim(column0) as codice_voce,
    trim(column1) as codice_gestione,
    trim(column2) as descrizione_codice,
    try_cast(column3 as date) as data_inizio,
    try_cast(column4 as date) as data_fine,
    case when trim(column0) like '9.%' then true else false end as is_titolo_9,
    case
        when trim(column0) like '1.%' then 'Spese correnti'
        when trim(column0) like '2.%' then 'Spese in conto capitale'
        when trim(column0) like '3.%' then 'Incremento attivita'' finanziarie'
        when trim(column0) like '4.%' then 'Rimborso prestiti'
        when trim(column0) like '7.%' then 'Anticipazioni e partite di giro'
        else 'Altre spese'
    end as macro_area,
    case
        when trim(column0) like '1.01.%' then 'Personale'
        when trim(column0) like '1.02.%' then 'Imposte e tasse'
        when trim(column0) like '1.03.%' then 'Acquisto beni e servizi'
        when trim(column0) like '1.04.%' then 'Trasferimenti correnti'
        when trim(column0) like '1.05.%' then 'Interessi passivi'
        when trim(column0) like '1.07.%' then 'Poste correttive'
        when trim(column0) like '2.01.%' then 'Investimenti fissi'
        when trim(column0) like '2.02.%' then 'Contributi investimenti'
        when trim(column0) like '2.03.%' then 'Trasferimenti c/capitale'
        when trim(column0) like '4.%' then 'Rimborso prestiti'
        when trim(column0) like '7.%' then 'Anticipazioni'
        else 'Altre spese'
    end as macro_categoria
from raw_input;
