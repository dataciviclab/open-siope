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
(support seed) in due passaggi:

1. **Regole sul codice** per i codici strutturati (piano dei conti puntato):
   - entrate: `1.01.*` → Imposte proprie · `1.03.*` → Fondi perequativi ·
     `2.01.*` → Trasferimenti correnti · `4.02.*` → Contributi agli investimenti
   - uscite: `1.01.*` → Personale · `1.02.*` → Imposte e tasse · `1.03.*` →
     Acquisto beni e servizi · `1.04.*` → Trasferimenti correnti · `1.05.*` →
     Interessi passivi · `1.07.*` → Poste correttive · `2.01.*` → Investimenti
     fissi · `2.02.*` → Contributi investimenti · `2.03.*` → Trasferimenti
     c/capitale · `3.*` → attività finanziarie · `4.*` → Rimborso prestiti ·
     `7.*` → Anticipazioni

2. **Fallback sulla descrizione** (ILIKE) per i codici compatti e i macroaggregati
   alfanumerici, il cui codice non ha la struttura a punti:
   - macroaggregati dello Stato (`A0100`-`I6100`): la categoria è nel testo
     ("TRASFERIMENTI CORRENTI AD AMMINISTRAZIONI PUBBLICHE" → Trasferimenti correnti)
   - compatti sanità e altri comparti (`1103` → Personale, `2101` → Acquisto beni,
     `2102` → Trasferimenti correnti, ...)
   - tributarie entrate esplicite (imposta/addizionale/IRAP/IVA/IMU/TARI/canone)

`macro_area` (uscite) è derivata dalla categoria, garantendo la coerenza.
`is_titolo_9` (partite di giro) include anche i codici compatti `999x`
(pagamenti da regolarizzare).

**Copertura** (misurata su 2024, % del denaro non classificato):
STA uscite 100% → 3.4%, SAN uscite 100% → 6.4%, SAN entrate 100% → 7.4%.
Il residuo `Altro` delle entrate include le entrate extra-tributarie
(servizi, proventi, rimborsi): la griglia entrate (5 categorie) non le
distingue — per analizzarle servirebbe una categoria dedicata.

Questa classificazione non sostituisce la lettura puntuale delle singole
`descrizione_codice`, ma rende più stabili i confronti pubblici come autonomia
fiscale vs dipendenza esterna e la composizione della spesa per categoria.
