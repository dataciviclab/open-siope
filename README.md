# siope-comuni

Repo progetto DataCivicLab dedicata a SIOPE, con base tecnica attuale su `comuni / 2021-2025`, lato `entrate` gia consolidato e lato `uscite` in v1 tecnica.

## Stato

Il perimetro tecnico oggi e':

- perimetro: comuni
- lato contabile: entrate + uscite
- annualita': 2021-2025
- pipeline: `RAW -> CLEAN -> MART` via `toolkit`
- territori: comune → provincia → regione (join con anagrafica SIOPE)
- gerarchia: mart automatico a 3 livelli (comune, provincia, regione)

## Struttura

- `entrate/comuni/`: dataset principale entrate comuni
- `uscite/comuni/`: dataset v1 uscite comuni
- `anagrafica/anag-enti/`: seed anagrafica enti (include cod. istat comune, cod. provincia, popolazione)
- `anagrafica/anag-codgest-entrate/`: seed dizionario voci entrate
- `anagrafica/anag-codgest-uscite/`: seed dizionario voci uscite
- `anagrafica/anag-comparti/`: seed comparti
- `anagrafica/anag-sottocomparti/`: seed sottocomparti
- `anagrafica/anag-reg-prov/`: seed regioni e province `[NUOVO]`
- `anagrafica/anag-comuni/`: seed anagrafe comuni `[NUOVO]`
- `docs/`: metodologia e backlog tecnico

## Come eseguire

Eseguire prima i seed anagrafici:

```powershell
py -m toolkit.cli.app run all --config anagrafica/anag-comparti/dataset.yml
py -m toolkit.cli.app run all --config anagrafica/anag-sottocomparti/dataset.yml
py -m toolkit.cli.app run all --config anagrafica/anag-enti/dataset.yml
py -m toolkit.cli.app run all --config anagrafica/anag-codgest-entrate/dataset.yml
py -m toolkit.cli.app run all --config anagrafica/anag-codgest-uscite/dataset.yml
py -m toolkit.cli.app run all --config anagrafica/anag-reg-prov/dataset.yml
py -m toolkit.cli.app run all --config anagrafica/anag-comuni/dataset.yml
```

Poi eseguire i dataset principali:

```powershell
py -m toolkit.cli.app run all --config entrate/dataset.yml
py -m toolkit.cli.app run all --config uscite/dataset.yml
```

## Output attesi

`entrate/` produce:

- `clean` canonico delle entrate
- `siope_entrate_comuni_agg` — aggregato per ente-anno-voce
- `siope_entrate_comuni_agg_labeled` — aggregato con voci e territorio (provincia + regione)
- `siope_entrate_regioni_agg_labeled` — regioni e province autonome
- `siope_entrate_sanita_agg_labeled` — ASL, AO, IRCCS
- `siope_entrate_universita_agg_labeled` — atenei e dipartimenti
- `h_entrate_comune_macro` — gerarchia: comune × macro_categoria
- `h_entrate_provincia_macro` — gerarchia: provincia × macro_categoria
- `h_entrate_regione_macro` — gerarchia: regione × macro_categoria

Il `mart` labeled espone almeno:

- `importo_totale`, `importo_totale_eur`
- `provincia`, `regione`
- `macro_categoria_v2`, `is_titolo_9`
- `descrizione_codice`

`uscite/` produce:

- `clean` canonico delle uscite
- `siope_uscite_comuni_agg` — aggregato per ente-anno-voce
- `siope_uscite_comuni_agg_labeled` — aggregato con voci e territorio
- `siope_uscite_regioni_agg_labeled` — regioni e province autonome
- `siope_uscite_sanita_agg_labeled` — ASL, AO, IRCCS
- `siope_uscite_universita_agg_labeled` — atenei e dipartimenti
- `h_uscite_comune` — gerarchia: comune
- `h_uscite_provincia` — gerarchia: provincia
- `h_uscite_regione` — gerarchia: regione

> **Nota**: i mart detail mensili (`siope_*_comuni.parquet`) non sono generati di default
> per contenere la dimensione dell'artifact CI (~200MB invece di 1GB).
> Per rigenerarli: aggiungere manualmente `sql/mart_PRO.sql` a `mart.tables`
> nel dataset.yml e rieseguire.

## Documenti utili

- [docs/uso_mart_labeled.md](docs/uso_mart_labeled.md)
- [docs/output_v1_entrate_comuni_2023_2024.md](docs/output_v1_entrate_comuni_2023_2024.md)
  Documento storico del primo output pubblico stretto su `2023-2024`.
- [entrate/comuni/notebooks/d3_entrate_comuni_2021_2025.ipynb](entrate/comuni/notebooks/d3_entrate_comuni_2021_2025.ipynb)
  Notebook di follow-up sul perimetro `2021-2025`: segnali `2024 -> 2025` e breakdown di `Altro`.
- [uscite/comuni/notebooks/d1_uscite_grandi_comuni_2021_2025.ipynb](uscite/comuni/notebooks/d1_uscite_grandi_comuni_2021_2025.ipynb)
  Primo notebook sul lato `uscite`: grandi comuni, `2021 -> 2025`, spesa corrente, investimenti e flussi tecnici.

## Limiti noti

- per confronti descrittivi sui totali, usare come base `is_titolo_9 = false`
- gli importi originari sono in centesimi di euro
- il lato `entrate` e' oggi piu' maturo del lato `uscite` sul piano analitico e documentale

Dettagli in [docs/metodologia.md](docs/metodologia.md) e [docs/backlog_tecnico.md](docs/backlog_tecnico.md).
