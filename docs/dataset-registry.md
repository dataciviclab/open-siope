# Dataset registry

`registry/registry.json` è l'**artifact catalogo** del repo (fusion ADR, toolkit v1.49+):
un unico file con le sezioni `datasets`, `marts`, `signals`, `codelists`, `entities`.

Viene generato da `scripts/build_registry.py` (wrapper sul builder condiviso
`toolkit.registry`) e **non è committato manualmente**: lo produce la pipeline
post-merge dopo ogni run e lo pubblica con una PR draft `chore(post-merge)`.

## Come è fatto

| Sezione | Contenuto |
|---|---|
| `datasets` | Inventario dei clean parquet: slug, name, description, source_id, period, years, tags, category, columns (role + semantic_type), location GCS, mart_refs, blocco `run` |
| `marts` | Tabelle mart (`{dataset}__{table}`) con primary_key, required_columns, min_rows, location GCS |
| `signals` | Health check operativo dell'ultimo run per dataset |
| `codelists` | Dizionari (per siope vuota: i dizionari sono i support seed) |
| `entities` | Grafo entità → dataset derivato dai semantic_type delle colonne (es. `municipality_code` → Comune) |

## Dataset

| Slug | Cosa contiene |
|---|---|
| `siope_entrate` | Entrate mensili di tutti gli enti pubblici (2021-2026) |
| `siope_uscite` | Uscite mensili di tutti gli enti pubblici (2021-2026) |
| `siope_anag_*_seed` (7) | Anagrafiche/dizionari di supporto (enti, codici gestionali, comparti, sottocomparti, reg/prov, comuni) |

Layout GCS: `gs://dataciviclab-clean/siope/{slug}/{year}/` e
`gs://dataciviclab-mart/siope/{slug}/{year}/`.

## Accesso

- **Locale**: parquet in `out/data/clean|mart/` (dopo un run)
- **GCS**: `gs://dataciviclab-clean/siope/` e `gs://dataciviclab-mart/siope/`
- **MCP toolkit**: `toolkit_find`, `toolkit_dataset_overview`, `toolkit_layer`,
  `toolkit_registry_show repo=open-siope` — vedi README

## Aggiornamento

```bash
python3 scripts/build_registry.py           # dry-run (riepilogo)
python3 scripts/build_registry.py --write   # scrive registry/registry.json
```
