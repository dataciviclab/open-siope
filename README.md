# siope-comuni

Repo progetto DataCivicLab dedicata a SIOPE, con focus iniziale su `entrate / comuni / 2023-2024`.

## Stato

Repo privata in consolidamento. La v1 e' volutamente stretta:

- perimetro: comuni
- lato contabile: entrate
- annualita': 2023, 2024
- pipeline: `RAW -> CLEAN -> MART` via `toolkit`

`uscite` resta fuori dalla v1.

## Struttura

- `entrate/comuni_2023_2024/`: dataset principale
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
py -m toolkit.cli.app run all --config entrate/comuni_2023_2024/dataset.yml
py -m toolkit.cli.app validate all --config entrate/comuni_2023_2024/dataset.yml
```

## Output attesi

Il dataset principale produce:

- `clean` canonico delle entrate
- `siope_entrate_comuni`
- `siope_entrate_comuni_agg`
- `siope_entrate_comuni_agg_labeled`

Il `mart` labeled espone almeno:

- `importo_totale`
- `importo_totale_eur`
- `descrizione_codice`
- `is_titolo_9`

## Documenti utili

- [docs/uso_mart_labeled.md](/C:/Users/gabry/OneDrive/Desktop/dataciviclab-workspace/siope-comuni/docs/uso_mart_labeled.md)
- [docs/output_v1_entrate_comuni_2023_2024.md](/C:/Users/gabry/OneDrive/Desktop/dataciviclab-workspace/siope-comuni/docs/output_v1_entrate_comuni_2023_2024.md)

## Limiti noti

- per confronti descrittivi sui totali, usare come base `is_titolo_9 = false`
- gli importi originari sono in centesimi di euro
- alcuni riferimenti anagrafici sono ancora hardcodati allo snapshot `2024`

Dettagli in [docs/metodologia.md](/C:/Users/gabry/OneDrive/Desktop/dataciviclab-workspace/siope-comuni/docs/metodologia.md) e [docs/backlog_tecnico.md](/C:/Users/gabry/OneDrive/Desktop/dataciviclab-workspace/siope-comuni/docs/backlog_tecnico.md).
