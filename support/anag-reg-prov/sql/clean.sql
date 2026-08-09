select
    normalize_string(column0) as area_geografica,
    normalize_string(column1) as codice_regione,
    normalize_string(column2) as regione,
    normalize_string(column3) as codice_provincia,
    normalize_string(column4) as provincia
from raw_input;
