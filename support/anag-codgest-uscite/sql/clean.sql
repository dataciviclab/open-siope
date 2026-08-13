-- Dizionario codgest uscite: classificazione da MAPPING UFFICIALE versionato
-- (mapping/uscite_categorie.csv — generato da scripts/import_classificazione.py
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
    -- Partite di giro: nelle uscite sono il TITOLO 7 (U7 = uscite per conto
    -- terzi e partite di giro del piano dei conti) + i compatti 999x
    -- (pagamenti da regolarizzare).
    case
        when b.codice_voce like '7.%' or b.codice_voce like '999%' then true
        else false
    end as is_titolo_9,
    coalesce(m.macro_categoria, 'Altre spese') as macro_categoria,
    coalesce(m.macro_area, 'Altre spese') as macro_area
from base b
left join read_csv('mapping/uscite_categorie.csv', auto_detect=true, header=true) m
    on b.codice_voce = m.codice_voce;
