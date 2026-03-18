# siope-comuni

Repo progetto DataCivicLab dedicata a SIOPE, con base tecnica attuale su `comuni / 2021-2025`, lato `entrate` gia consolidato e lato `uscite` in v1 tecnica.

## Stato

Repo privata in consolidamento. Il perimetro tecnico oggi e':

- perimetro: comuni
- lato contabile: entrate + uscite
- annualita': 2021-2025
- pipeline: `RAW -> CLEAN -> MART` via `toolkit`
- cross-year disponibile oggi solo per `entrate`

## Struttura

- `entrate/comuni/`: dataset principale entrate comuni
- `uscite/comuni/`: dataset v1 uscite comuni
- `anagrafica/anag-enti/`: seed anagrafica enti
- `anagrafica/anag-codgest-entrate/`: seed dizionario voci entrate
- `anagrafica/anag-codgest-uscite/`: seed dizionario voci uscite
- `anagrafica/anag-comparti/`: seed comparti
- `anagrafica/anag-sottocomparti/`: seed sottocomparti
- `docs/`: metodologia e backlog tecnico

## Come eseguire

Eseguire prima i seed anagrafici:

```powershell
py -m toolkit.cli.app run all --config anagrafica/anag-comparti/dataset.yml
py -m toolkit.cli.app run all --config anagrafica/anag-sottocomparti/dataset.yml
py -m toolkit.cli.app run all --config anagrafica/anag-enti/dataset.yml
py -m toolkit.cli.app run all --config anagrafica/anag-codgest-entrate/dataset.yml
py -m toolkit.cli.app run all --config anagrafica/anag-codgest-uscite/dataset.yml
```

Poi eseguire i dataset principali:

```powershell
py -m toolkit.cli.app run all --config entrate/comuni/dataset.yml
py -m toolkit.cli.app validate all --config entrate/comuni/dataset.yml
py -m toolkit.cli.app run cross_year --config entrate/comuni/dataset.yml
py -m toolkit.cli.app run all --config uscite/comuni/dataset.yml
py -m toolkit.cli.app validate all --config uscite/comuni/dataset.yml
```

## Output attesi

`entrate/comuni` produce:

- `clean` canonico delle entrate
- `siope_entrate_comuni`
- `siope_entrate_comuni_agg`
- `siope_entrate_comuni_agg_labeled`
- `siope_entrate_comuni_agg_labeled_multi_anno`

Il `mart` labeled espone almeno:

- `importo_totale`
- `importo_totale_eur`
- `descrizione_codice`
- `is_titolo_9`

`uscite/comuni` produce:

- `clean` canonico delle uscite
- `siope_uscite_comuni`
- `siope_uscite_comuni_agg`
- `siope_uscite_comuni_agg_labeled`

## Documenti utili

- [docs/uso_mart_labeled.md](docs/uso_mart_labeled.md)
- [docs/output_v1_entrate_comuni_2023_2024.md](docs/output_v1_entrate_comuni_2023_2024.md)
  Documento storico del primo output pubblico stretto su `2023-2024`.
- [entrate/comuni/notebooks/d3_entrate_comuni_2021_2025.ipynb](entrate/comuni/notebooks/d3_entrate_comuni_2021_2025.ipynb)
  Follow-up interno sul perimetro `2021-2025`: segnali `2024 -> 2025` e breakdown di `Altro`.

## Limiti noti

- per confronti descrittivi sui totali, usare come base `is_titolo_9 = false`
- gli importi originari sono in centesimi di euro
- alcuni riferimenti anagrafici sono ancora hardcodati allo snapshot `2024`

Dettagli in [docs/metodologia.md](/C:/Users/gabry/OneDrive/Desktop/dataciviclab-workspace/siope-comuni/docs/metodologia.md) e [docs/backlog_tecnico.md](/C:/Users/gabry/OneDrive/Desktop/dataciviclab-workspace/siope-comuni/docs/backlog_tecnico.md).
