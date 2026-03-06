select
    trim(column0) as codice_ente,
    try_cast(column1 as date) as data_inizio,
    try_cast(column2 as date) as data_fine,
    trim(column3) as codice_fiscale,
    trim(column4) as denominazione_ente,
    trim(column5) as codice_col6,
    trim(column6) as codice_col7,
    trim(column7) as codice_col8,
    trim(column8) as tipo_ente
from raw_input;
