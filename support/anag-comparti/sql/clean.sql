select
    normalize_string(column0) as codice_comparto,
    normalize_string(column1) as descrizione_comparto
from raw_input;
