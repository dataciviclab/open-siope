select
    normalize_string(column0) as codice_istat_comune,
    normalize_string(column1) as denominazione_comune,
    normalize_string(column2) as codice_provincia
from raw_input;
