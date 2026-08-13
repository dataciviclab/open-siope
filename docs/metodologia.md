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

- il perimetro copre `2021-2026`; il `clean` copre tutti i comparti SIOPE (PRO, REG, SAN, UNI, STA, CDC, VSN, ...), i `mart` per-comparto sono generati per i 4 principali (PRO/REG/SAN/UNI)
- entrate e uscite hanno entrambe notebook di analisi e verifica
- il dataset consolidato `siope_bilancio_unificato` e' ora gestito dal compose in [dataset-incubator](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/siope-bilancio-unificato) (v. [pipeline.md](pipeline.md))
- il terzo campo delle entrate viene trattato come `periodo` (`01..12`), non come `codice_gestione`
- il join contestuale del labeled usa `codice_comparto = codice_gestione` sul perimetro comuni
- i confronti descrittivi sui totali devono partire da `is_titolo_9 = false`
- territorio: ogni comune ha codice provincia (da ANAG_ENTI_SIOPE), arricchito con provincia e regione via join con ANAG_REG_PROV
- gerarchia territoriale: disponibile nei mart hierarchy (comune → provincia → regione) a 3 livelli

## Validita' temporale

I join anagrafici usano `make_date(anno, 12, 31)` come data di validita'
dell'anno (scelta metodologica semplice e stabile; da rivalutare se emergono
enti con transizioni infra-annuali rilevanti).

## Unita' di misura

- `importo`: centesimi di euro
- `importo_totale_eur`: euro derivati dal totale aggregato

Gli output prodotti sono descritti in [pipeline.md](pipeline.md).

## Classificazione per macro-categoria (entrate e uscite)

Nel `clean` arricchito (e nei `mart`) esistono `macro_categoria_v2` (entrate) e
`macro_area` / `macro_categoria` (uscite), calcolate nel dizionario codgest
(support seed) tramite **JOIN con la mappa versionata** `mapping/*.categorie.csv`
— nessuna regola testuale a runtime.

**Fonte: classificazione ufficiale RGS**, importata da
`scripts/import_classificazione.py`:

- **Glossario SIOPE enti territoriali** (RGS): ogni codice gestionale SIOPE dei
  puntati (PRO/REG/UNI) è mappato al piano dei conti integrato (titolo +
  macroaggregato) → macro_area / macro_categoria. Match verificato: ~99% dei
  codici, ~100% del denaro.
- **Glossario SIOPE Sanità** (RGS): i codici compatti SAN sono organizzati per
  sezioni (PERSONALE, ACQUISTO DI BENI, ACQUISTI DI SERVIZI, TRASFERIMENTI,
  IMPOSTE E TASSE, ...) che sono le categorie → macro_categoria. Match: 100%.
- **Baseline** (comparti senza glossario scaricabile — STA, CDC, VSN, ... e
  residui `0.00.00.99.x`): classificazione dalle descrizioni, generata una
  volta e versionata nella mappa.

`macro_area` (uscite) è derivata dalla categoria (coerenza garantita).
`is_titolo_9` (partite di giro): nelle **uscite** è il **titolo 7** del piano
dei conti (U7 = uscite per conto terzi e partite di giro, es. split payment)
più i compatti `999x`; nelle **entrate** il titolo 9 più i `999x`.

**Griglia entrate** (5 categorie): Imposte proprie · Fondi perequativi ·
Trasferimenti correnti · Contributi agli investimenti · Entrate extratributarie
(il titolo E3 del piano dei conti è ora una categoria esplicita, non più
sparso in "Altro") · Altro (finanziarie e partite di giro).

**Copertura** (misurata su 2024, % del denaro in "Altro"/"Altre spese"):
entrate PRO 21% → 6% · REG → 6,5% · UNI → 11,1%; uscite STA 3,8% · SAN 2,3%.
Per le uscite, "Altre spese" è la categoria ufficiale del piano (U1.10 altre
spese correnti, U2.05 altre spese in conto capitale) — non un fallback.

Questa classificazione non sostituisce la lettura puntuale delle singole
`descrizione_codice`, ma rende più stabili i confronti pubblici come autonomia
fiscale vs dipendenza esterna e la composizione della spesa per categoria.
