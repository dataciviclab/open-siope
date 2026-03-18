# Uso operativo del mart labeled

Questa nota spiega come leggere in modo corretto il `mart` finale del progetto:

- dataset: `entrate/comuni`
- tabella: `siope_entrate_comuni_agg_labeled`

## Colonne da usare per prime

- `codice_ente`
- `denominazione_ente`
- `anno`
- `codice_voce`
- `descrizione_codice`
- `macro_categoria_v2`
- `importo_totale`
- `importo_totale_eur`
- `is_titolo_9`

## Regole di lettura

- usare `importo_totale_eur` per output leggibili e confronti descrittivi
- usare `importo_totale` solo per controlli tecnici o confronti con i valori raw
- per confronti sui totali tra comuni, partire da `is_titolo_9 = false`
- trattare `is_titolo_9 = true` come flussi tecnici o di giro, non come entrate strutturali
- per confronti su autonomia fiscale o dipendenza esterna, partire da `macro_categoria_v2`
  e poi scendere alle singole `descrizione_codice` solo nei casi che restano dubbi

## Join contestuale del dizionario entrate

Il labeled usa un join contestuale tra:

- `codice_comparto` del mart
- `codice_gestione` del dizionario entrate

Nel perimetro v1 dei comuni, il contesto corretto e':

- `tipo_ente = COMUNE`
- `codice_comparto = PRO`

Questa assunzione e' valida per il perimetro attuale dei comuni e va rivalutata se il progetto si estende ad altri comparti.

## Limiti da tenere presenti

- perimetro tecnico attuale: `comuni / entrate / 2021-2025`
- il primo output pubblico storico del repo resta invece su `2023-2024`
- alcuni path anagrafici sono ancora hardcodati allo snapshot `2024`
- il join anagrafico usa una validita' annuale con pivot al `31 dicembre`
- `codice_col6`, `codice_col7`, `codice_col8` non sono campi interpretativi pubblici
- `macro_categoria_v2` e' una proxy minima: utile per follow-up pubblici, ma non
  sostituisce l'analisi puntuale di tutte le voci `2.*`, `4.*` o `7.*`
- la categoria `Altro` resta eterogenea e include anche proventi da servizi,
  anticipazioni e altre voci di finanziamento che vanno lette a livello di
  `codice_voce` quando il confronto pubblico lo richiede

## Query di partenza

Esempio logico per confronti descrittivi:

```sql
select
    denominazione_ente,
    anno,
    sum(importo_totale_eur) as totale_entrate_eur
from read_parquet('out/data/mart/siope_entrate_comuni/2024/siope_entrate_comuni_agg_labeled.parquet')
where is_titolo_9 = false
group by 1, 2;
```

La query va adattata al file/anno corretto. Il punto metodologico e' il filtro su `is_titolo_9`.
