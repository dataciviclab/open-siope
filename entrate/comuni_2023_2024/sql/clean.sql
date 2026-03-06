select
    trim(column0) as codice_ente,
    try_cast(column1 as integer) as anno,
    trim(column2) as periodo,
    trim(column3) as codice_voce,
    try_cast(column4 as bigint) as importo
from raw_input;
