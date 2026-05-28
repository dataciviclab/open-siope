# siope-comuni

Progetto DataCivicLab per i dati SIOPE — entrate e uscite degli enti pubblici italiani.
Pipeline RAW → CLEAN → MART via toolkit DuckDB.

## Stato

| Perimetro | Copertura |
|---|---|
| **Comparti** | PRO (comuni, province, città metrop.) · REG (regioni) · SAN (ASL, AO, IRCCS) · UNI (atenei) |
| **Annualità** | 2021-2025 |
| **Output** | Mart annuali aggregati + gerarchia territoriale (comune → provincia → regione) |
| **CI** | `check` su PR (validazione config) · `pipeline` dispatch (run completo, artifact .zip ~200MB) |

## Struttura

- `entrate/`: dataset entrate (PRO comuni/province + REG + SAN + UNI)
- `uscite/`: dataset uscite (PRO comuni/province + REG + SAN + UNI)
- `anagrafica/anag-enti/`: seed anagrafica enti (cod. istat comune, provincia, popolazione)
- `anagrafica/anag-codgest-entrate/`: seed dizionario voci entrate
- `anagrafica/anag-codgest-uscite/`: seed dizionario voci uscite
- `anagrafica/anag-comparti/`: seed comparti
- `anagrafica/anag-sottocomparti/`: seed sottocomparti
- `anagrafica/anag-reg-prov/`: seed regioni e province
- `anagrafica/anag-comuni/`: seed anagrafe comuni
- `docs/`: metodologia e backlog tecnico

## Come eseguire

Eseguire prima i seed anagrafici:

```bash
make seeds
```

Poi eseguire i dataset principali:

```bash
python3 -m toolkit.cli.app run all --config entrate/dataset.yml
python3 -m toolkit.cli.app run all --config uscite/dataset.yml
```

## Output attesi

`entrate/` produce:

- `clean` canonico delle entrate
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
- `macro_categoria_v2`, `is_titolo_9` (entrate) / `macro_area`, `macro_categoria` (uscite)

`uscite/` produce:

- `clean` canonico delle uscite
- `siope_uscite_comuni_agg_labeled` — aggregato con voci, territorio e classificazione spesa
- `siope_uscite_regioni_agg_labeled` — regioni e province autonome
- `siope_uscite_sanita_agg_labeled` — ASL, AO, IRCCS
- `siope_uscite_universita_agg_labeled` — atenei e dipartimenti
- `h_uscite_comune` — gerarchia: comune × macro_categoria
- `h_uscite_provincia` — gerarchia: provincia × macro_area
- `h_uscite_regione` — gerarchia: regione × macro_area


## Documenti utili

- [docs/uso_mart_labeled.md](docs/uso_mart_labeled.md)
- [docs/output_v1_entrate_comuni_2023_2024.md](docs/output_v1_entrate_comuni_2023_2024.md)
  Documento storico del primo output pubblico stretto su `2023-2024`.
- [entrate/notebooks/d3_entrate_comuni_2021_2025.ipynb](entrate/notebooks/d3_entrate_comuni_2021_2025.ipynb)
  Notebook di follow-up sul perimetro `2021-2025`: segnali `2024 -> 2025` e breakdown di `Altro`.
- [uscite/notebooks/d1_uscite_grandi_comuni_2021_2025.ipynb](uscite/notebooks/d1_uscite_grandi_comuni_2021_2025.ipynb)
  Primo notebook sul lato `uscite`: grandi comuni, `2021 -> 2025`, spesa corrente, investimenti e flussi tecnici.

## Limiti noti

- i mart detail mensili non sono generati di default (artifact CI più compatto)
- per confronti descrittivi sui totali, usare come base `is_titolo_9 = false`
- gli importi originari sono in centesimi di euro
- i dati siope sono aggiornati a cadenza mensile dalla fonte, il progetto va ri-eseguito periodicamente

Dettagli in [docs/metodologia.md](docs/metodologia.md) e [docs/backlog_tecnico.md](docs/backlog_tecnico.md).
