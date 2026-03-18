# siope-comuni

Repo progetto DataCivicLab dedicata a SIOPE, con base tecnica attuale su `entrate / comuni / 2021-2025`.

## Stato

Repo privata in consolidamento. Il perimetro tecnico oggi e':

- perimetro: comuni
- lato contabile: entrate
- annualita': 2021-2025
- pipeline: `RAW -> CLEAN -> MART` via `toolkit`
- cross-year disponibile sul `mart` labeled multi-anno

`uscite` resta ancora fuori dal perimetro implementato.

## Struttura

- `entrate/comuni/`: dataset principale entrate comuni
- `anagrafica/anag-enti/`: seed anagrafica enti
- `anagrafica/anag-codgest-entrate/`: seed dizionario voci entrate
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
```

Poi eseguire il dataset principale:

```powershell
py -m toolkit.cli.app run all --config entrate/comuni/dataset.yml
py -m toolkit.cli.app validate all --config entrate/comuni/dataset.yml
py -m toolkit.cli.app run cross_year --config entrate/comuni/dataset.yml
```

## Output attesi

Il dataset principale produce:

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
