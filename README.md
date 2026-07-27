# open-siope — La spesa pubblica italiana, aperta e interrogabile

**Quanto spende il tuo comune? E quanto incassa? Mese per mese, voce per voce.**

open-siope nasce dai dati SIOPE (Sistema Informativo sulle Operazioni degli Enti Pubblici)
della Ragioneria Generale dello Stato. Li abbiamo puliti, arricchiti e resi pubblici.

## Cosa contiene

| | |
|---|---|
| **Enti coperti** | ~18.000 (comuni, ASL, università, regioni, province) |
| **Periodo** | 2021 — 2026 |
| **Voci entrate** | ~2.000 codici (IMU, TARI, IRPEF, trasferimenti...) |
| **Voci uscite** | ~2.700 codici (personale, beni, investimenti, interessi...) |
| **Comparti** | PRO (territorio) · REG (regioni) · SAN (sanità) · UNI (università) |

## Esempi di domande

- **Quanto spende il tuo comune in manutenzione strade?** E in refezione scolastica?
- **Quali enti incassano più IMU pro-capite?**
- **Come cambia la spesa sanitaria tra regioni?**
- **Quanto vale il FFO (Fondo di Finanziamento Ordinario) della tua università?**
- **Quali comuni dipendono di più dai trasferimenti statali?**

## Tre modi per accedere ai dati

### 1. Via MCP (clean-query)

Il dataset `siope_bilancio_unificato` è accessibile via SQL arbitrario
dal server MCP clean-query del Lab.

```
"Quanto ha speso il Comune di Milano nel 2024?"
"Quali sono le 10 voci di uscita più grandi delle ASL lombarde?"
```

### 2. Via DuckDB diretto

```python
import duckdb
duckdb.sql("""
    SELECT anno, SUM(importo_eur) AS entrate
    FROM read_parquet('gs://dataciviclab-clean/siope/*.parquet')
    WHERE codice_ente = '000000047' AND lato = 'entrate'
    GROUP BY anno ORDER BY anno
""").show()
```

### 3. Via download parquet

Bucket pubblico: `gs://dataciviclab-clean/siope/` (accessibile anche via HTTPS)

## Approfondimenti

- Discussion per comparto: [Territorio](https://github.com/dataciviclab/open-siope/discussions/categories/territorio) · [Sanità](https://github.com/dataciviclab/open-siope/discussions/categories/sanit%C3%A0-san) · [Regioni](https://github.com/dataciviclab/open-siope/discussions/categories/regioni-reg) · [Università](https://github.com/dataciviclab/open-siope/discussions/categories/universit%C3%A0-uni)
- [Analisi: Dove vanno i soldi dei comuni italiani?](https://github.com/dataciviclab/dataciviclab/tree/main/analisi/siope_uscite_comuni)

## Partecipa

- **Hai una domanda sui dati?** Apri una [Discussion](https://github.com/dataciviclab/open-siope/discussions/new?category=Q-A)
- **Vuoi contribuire?** Vedi [CONTRIBUTING.md](CONTRIBUTING.md)

## Documenti tecnici

- [Pipeline](docs/pipeline.md) — esecuzione, struttura, output
- [Metodologia](docs/metodologia.md) — origini dati, classificazioni
- [Uso mart](docs/uso_mart_labeled.md) — tabelle aggregate

Questo progetto fa parte di [DataCivicLab](https://github.com/dataciviclab).
