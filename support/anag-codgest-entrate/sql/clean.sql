-- Dizionario codgest entrate: classificazione da MAPPING UFFICIALE versionato
-- (mapping/entrate_categorie.csv — generato da scripts/import_classificazione.py
-- da fonti RGS: glossario enti territoriali + glossario sanità + baseline).
-- Nessuna regola testuale: la categoria di ogni codice è una riga esplicita.

with base as (
    select
        normalize_string(column0) as codice_voce,
        normalize_string(column1) as codice_gestione,
        normalize_string(column2) as descrizione_codice,
        try_cast(column3 as date) as data_inizio,
        try_cast(column4 as date) as data_fine
    from raw_input
)
select
    b.codice_voce,
    b.codice_gestione,
    b.descrizione_codice,
    b.data_inizio,
    b.data_fine,
    -- Partite di giro: nelle entrate sono il TITOLO 9 (E9 = entrate per conto
    -- terzi e partite di giro) + i compatti 999x (incassi da regolarizzare).
    case
        when b.codice_voce like '9.%' or b.codice_voce like '999%' then true
        else false
    end as is_titolo_9,
    coalesce(m.macro_categoria_v2, 'Altro') as macro_categoria_v2
from base b
left join read_csv('mapping/entrate_categorie.csv', auto_detect=true, header=true) m
    on b.codice_voce = m.codice_voce
    and b.codice_gestione = m.codice_gestione;
