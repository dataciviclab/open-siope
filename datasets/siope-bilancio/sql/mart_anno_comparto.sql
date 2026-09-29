-- mart_anno_comparto — SIOPE: totale entrate/uscite per anno × comparto × lato × macro_categoria
--
-- Grano: anno × comparto × lato × macro_categoria × is_titolo_9.
-- Risponde a: "quanto entra/esce in ogni comparto, per categoria, anno per anno".
-- Base per il confronto SIOPE ↔ BDAP (macro_categoria ≈ macroaggregato).
-- Esclude le righe con comparto NULL (entità non risolte, 0.009% dei dati).

select
    anno,
    descrizione_comparto as comparto,
    lato,
    coalesce(macro_categoria, 'Altro') as macro_categoria,
    is_titolo_9,
    round(sum(importo_eur), 0) as importo_eur,
    count(*) as righe,
    count(distinct codice_ente) as n_enti,
    count(distinct codice_voce) as n_voci
from clean_input
where codice_comparto is not null
group by anno, descrizione_comparto, lato, coalesce(macro_categoria, 'Altro'), is_titolo_9
order by anno, comparto, lato, importo_eur desc;
