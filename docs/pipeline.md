# Pipeline

## Struttura del repository

- `entrate/`: dataset entrate
- `uscite/`: dataset uscite
- `anagrafica/`: seed anagrafiche (enti, codici gestionali, comparti, reg/prov)
- `scripts/`: utility (verify_output.py)
- `.github/workflows/`: CI/CD (check + pipeline dispatch)

## Esecuzione

Eseguire prima i seed anagrafici:

```bash
make seeds
```

Poi i dataset principali:

```bash
python3 -m toolkit.cli.app run all --config entrate/dataset.yml
python3 -m toolkit.cli.app run all --config uscite/dataset.yml
```

Il workflow CI su GitHub Actions fa tutto automaticamente via dispatch.

## Output — Entrate

| Layer | Descrizione |
|---|---|
| `clean` | 21 colonne: dati mensili + territorio, comparto, classificazione |
| `siope_entrate_pro` | aggregato voci + territorio (comuni, PRO) |
| `siope_entrate_reg` | regioni e province autonome |
| `siope_entrate_san` | ASL, AO, IRCCS |
| `siope_entrate_uni` | atenei e dipartimenti |

## Output — Uscite

| Layer | Descrizione |
|---|---|
| `clean` | 21 colonne: dati mensili + territorio, comparto, classificazione |
| `siope_uscite_pro` | aggregato voci + territorio (comuni, PRO) |
| `siope_uscite_reg` | regioni e province autonome |
| `siope_uscite_san` | ASL, AO, IRCCS |
| `siope_uscite_uni` | atenei e dipartimenti |

Il dataset consolidato `siope_bilancio_unificato` (UNION ALL di entrate+uscite)
è ora gestito dal compose [`siope-bilancio-unificato`](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/siope-bilancio-unificato)
in dataset-incubator, che ne produce anche i mart analitici (sintesi, trend, enti).

## Limiti noti

- i mart detail mensili non sono generati di default (artifact CI più compatto)
- per confronti descrittivi sui totali, usare come base `is_titolo_9 = false`
- gli importi originari sono in centesimi di euro
- i dati SIOPE sono aggiornati a cadenza mensile dalla fonte; il progetto va rieseguito periodicamente
