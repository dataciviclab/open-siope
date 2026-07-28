# Metodologia

## Origine dati

Il progetto usa i download open di SIOPE:

- `SIOPE_ENTRATE.{year}.zip` per il lato entrate
- `SIOPE_USCITE.{year}.zip` per il lato uscite
- `SIOPE_ANAGRAFICHE.zip` per i seed di supporto

## Pipeline

La pipeline segue il contract del `toolkit`:

- `raw`: download e extraction degli archivi ZIP
- `clean`: arricchimento con join alle anagrafiche (enti, territorio, comparto, dizionario voci)
- `mart`: filtro per comparto e aggregazione annuale (da cui la gerarchia territoriale)

## Regole metodologiche iniziali

- il perimetro copre `2021-2026` per 4 comparti: PRO (comuni/province), REG (regioni), SAN (ASL/AO/IRCCS), UNI (universita')
- entrate e uscite hanno entrambe notebook di analisi e verifica
- il dataset consolidato `siope_bilancio_unificato` e' ora gestito dal compose in [dataset-incubator](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/siope-bilancio-unificato) (v. [pipeline.md](pipeline.md))
- il terzo campo delle entrate viene trattato come `periodo` (`01..12`), non come `codice_gestione`
- il join contestuale del labeled usa `codice_comparto = codice_gestione` sul perimetro comuni
- i confronti descrittivi sui totali devono partire da `is_titolo_9 = false`
- territorio: ogni comune ha codice provincia (da ANAG_ENTI_SIOPE), arricchito con provincia e regione via join con ANAG_REG_PROV
- gerarchia territoriale: disponibile nei mart hierarchy (comune → provincia → regione) a 3 livelli

## Unita' di misura

- `importo`: centesimi di euro
- `importo_totale_eur`: euro derivati dal totale aggregato

Gli output prodotti sono descritti in [pipeline.md](pipeline.md).

## Classificazione minima per letture pubbliche

Nel `clean` arricchito (e di conseguenza nei `mart` aggregati) esiste una
`macro_categoria_v2` pensata per evitare due ambiguità emerse nei follow-up pubblici:

- non confondere i `Fondi perequativi` con le `Imposte proprie`
- non leggere i `Contributi agli investimenti` come se fossero semplici
  `Trasferimenti correnti`

La proxy v2 usa regole volutamente semplici sui codici voce:

- `1.01.*` -> `Imposte proprie`
- `1.03.01.01.001` -> `Fondi perequativi`
- `2.01.*` -> `Trasferimenti correnti`
- `4.02.*` -> `Contributi agli investimenti`
- tutto il resto -> `Altro`

Questa classificazione non sostituisce la lettura puntuale delle singole
`descrizione_codice`, ma rende più stabili confronti pubblici come autonomia
fiscale vs dipendenza esterna nei follow-up `D2`, `D3` e `D4`.
