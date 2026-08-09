# Pipeline

## Struttura del repository

- `datasets/siope-entrate/`: dataset entrate (dataset.yml + sql/)
- `datasets/siope-uscite/`: dataset uscite (dataset.yml + sql/)
- `support/`: support seed — anagrafiche SIOPE (enti, codici gestionali, comparti, reg/prov, comuni)
- `scripts/`: utility (verify_output.py, build_registry.py)
- `registry/`: artifact catalogo `registry.json` (generato dalla pipeline post-merge)
- `.github/workflows/`: CI/CD (check + pipeline)

## Esecuzione

Eseguire prima i support seed:

```bash
make seeds
```

Poi i dataset principali:

```bash
toolkit run --config datasets/siope-entrate/dataset.yml
toolkit run --config datasets/siope-uscite/dataset.yml
```

Il comando `run` esegue la pipeline completa RAW → CLEAN → MART per il dataset.
Il workflow CI (`pipeline.yml`) fa tutto automaticamente: su merge di una PR esegue
solo i dataset/support toccati, su schedule (5 del mese) o dispatch esegue entrate+uscite,
sincronizza i parquet su GCS, genera `registry/registry.json` e apre una PR draft
`chore(post-merge)` se il catalogo cambia.

## Output — Entrate

| Layer | Descrizione |
|---|---|
| `clean` | 18 colonne: dati mensili + territorio, comparto, classificazione |
| `mart_pro` | aggregato voci + territorio (comuni, PRO) |
| `mart_reg` | regioni e province autonome |
| `mart_san` | ASL, AO, IRCCS |
| `mart_uni` | atenei e dipartimenti |
| `mart_sintesi` | scheda ente annuale: totale, totale no-titolo9, n voci, n mesi |
| `mart_trend` | multi-anno per ente: first/last, delta, variazione %, CAGR |

## Output — Uscite

| Layer | Descrizione |
|---|---|
| `clean` | 19 colonne: dati mensili + territorio, comparto, classificazione |
| `mart_pro` | aggregato voci + territorio (comuni, PRO) |
| `mart_reg` | regioni e province autonome |
| `mart_san` | ASL, AO, IRCCS |
| `mart_uni` | atenei e dipartimenti |
| `mart_sintesi` | scheda ente annuale: totale, totale no-titolo9, n voci, n mesi |
| `mart_trend` | multi-anno per ente: first/last, delta, variazione %, CAGR |

Il dataset consolidato `siope_bilancio_unificato` (UNION ALL di entrate+uscite)
è ora gestito dal compose [`siope-bilancio-unificato`](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/siope-bilancio-unificato)
in dataset-incubator, che ne produce anche i mart analitici (sintesi, trend, enti).

## Limiti noti

- i mart detail mensili non sono generati di default (artifact CI più compatto)
- per confronti descrittivi sui totali, usare come base `is_titolo_9 = false`
- gli importi originari sono in centesimi di euro
- i dati SIOPE sono aggiornati a cadenza mensile dalla fonte; il progetto va rieseguito periodicamente
