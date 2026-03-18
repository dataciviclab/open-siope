select
    trim(column0) as codice_voce,
    trim(column1) as codice_gestione,
    trim(column2) as descrizione_codice,
    try_cast(column3 as date) as data_inizio,
    try_cast(column4 as date) as data_fine
from raw_input;
