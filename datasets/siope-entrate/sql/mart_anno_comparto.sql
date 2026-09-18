-- siope_entrate — mart_anno_comparto: totale entrate per anno × comparto × macro_categoria
--
-- Grano: anno × comparto × macro_categoria × is_titolo_9.

select
    anno,
    codice_comparto,
    any_value(descrizione_comparto) as descrizione_comparto,
    macro_categoria as macro_categoria,
    is_titolo_9,
    round(sum(importo_eur), 0) as importo_eur,
    count(*) as righe,
    count(distinct codice_ente) as n_enti,
    count(distinct codice_voce) as n_voci
from clean_input
where codice_comparto is not null
group by anno, codice_comparto, macro_categoria, is_titolo_9
order by anno, codice_comparto, importo_eur desc;
