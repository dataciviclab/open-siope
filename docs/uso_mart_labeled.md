# Uso operativo del mart labeled

> **⚠️ Documento storico (v1)**
> Questo documento si riferisce alla configurazione **pre-rename** del progetto,
> quando il perimetro era limitato a `entrate/comuni` con nome legacy
> `siope_entrate_comuni`. Oggi i dataset si chiamano `siope_entrate`/`siope_uscite`
> e il dataset consolidato e' `siope_bilancio_unificato` (v. `docs/pipeline.md`).
> I nomi di tabella e path qui sotto non sono piu' aggiornati.

- dataset: `entrate/comuni` (v1)
- tabella: `siope_entrate_comuni_agg_labeled` (ora `siope_entrate_pro`)

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

## Arricchimento nel clean

Le etichette (territorio, comparto, classificazione) vengono aggiunte nel layer
`clean` tramite join con le anagrafiche SIOPE:

- `enti` → denominazione_ente, tipo_ente, codice_provincia
- `sottocomparti` + `comparti` → codice_comparto, descrizione_comparto
- `regprov` → provincia, regione
- `codgest_entrate` → descrizione_codice, macro_categoria_v2, is_titolo_9

Il join contestuale del dizionario entrate usa:

- `codice_comparto = codice_gestione` (dal dizionario)
- `codice_voce` (match puntuale della voce contabile)
- validità temporale con pivot al `31 dicembre`

I mart ereditano le etichette dal clean e fanno sola aggregazione annuale.

## Limiti da tenere presenti

- perimetro tecnico attuale: `comuni / entrate / 2021-2025`
- il primo output pubblico storico del repo resta invece su `2023-2024`
- il `clean` legge sempre l'ultimo snapshot disponibile dei seed anagrafici `mart`
- il join anagrafico usa una validita' annuale con pivot al `31 dicembre`
- i `mart` ereditano le etichette dal `clean` e non fanno più join diretti
- `codice_col6`, `codice_col7`, `codice_col8` non sono campi interpretativi pubblici
- `macro_categoria_v2` e' una proxy minima: utile per follow-up pubblici, ma non
  sostituisce l'analisi puntuale di tutte le voci `2.*`, `4.*` o `7.*`
- la categoria `Altro` resta eterogenea e include anche proventi da servizi,
  anticipazioni e altre voci di finanziamento che vanno lette a livello di
  `codice_voce` quando il confronto pubblico lo richiede

## Query di partenza

Esempio logico per confronti descrittivi (da GCS pubblico):

```sql
select
    denominazione_ente,
    anno,
    sum(importo_totale_eur) as totale_entrate_eur
from read_parquet('https://storage.googleapis.com/dataciviclab-mart/siope/siope_entrate_comuni/2024/siope_entrate_comuni_agg_labeled.parquet')
where is_titolo_9 = false
group by 1, 2;
```

La query va adattata al file/anno corretto. Il punto metodologico e' il filtro su `is_titolo_9`.

Stessa logica vale per le uscite: `siope_uscite_comuni_agg_labeled` con `macro_area` e `macro_categoria` al posto di `macro_categoria_v2`.
