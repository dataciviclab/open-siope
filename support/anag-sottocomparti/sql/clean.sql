select
    normalize_string(column0) as codice_sottocomparto,
    normalize_string(column1) as descrizione_sottocomparto,
    normalize_string(column2) as codice_comparto
from raw_input;
