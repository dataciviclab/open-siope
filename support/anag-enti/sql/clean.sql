select
    normalize_string(column0) as codice_ente,
    try_cast(column1 as date) as data_inizio,
    try_cast(column2 as date) as data_fine,
    normalize_string(column3) as codice_fiscale,
    normalize_string(column4) as denominazione_ente,
    normalize_string(column5) as codice_istat_comune,
    normalize_string(column6) as codice_provincia,
    normalize_string(column7) as popolazione,
    normalize_string(column8) as tipo_ente
from raw_input;
