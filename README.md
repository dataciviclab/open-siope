# open-siope — La spesa pubblica italiana, aperta e interrogabile

> **Quanto spende e quanto incassa ogni ente pubblico italiano, mese per mese.**

open-siope nasce dai dati SIOPE (Sistema Informativo sulle Operazioni degli Enti Pubblici) della Ragioneria Generale dello Stato. Li abbiamo puliti, arricchiti, e resi pubblici.

La discussione è qui — partecipa, chiedi, approfondisci.

---

## 💬 Partecipa

Le discussioni sono il cuore del progetto. Trovi già i primi temi aperti:

- **🏘️ [Territorio](https://github.com/dataciviclab/open-siope/discussions/categories/territorio)** — IMU, TARI, personale, manutenzione strade, refezione scolastica
- **🏥 [Sanità](https://github.com/dataciviclab/open-siope/discussions/categories/sanit%C3%A0-san)** — ASL, ospedali, farmaceutica, spesa sanitaria
- **🏛️ [Regioni](https://github.com/dataciviclab/open-siope/discussions/categories/regioni-reg)** — IRAP, trasporti, fondi europei
- **🎓 [Università](https://github.com/dataciviclab/open-siope/discussions/categories/universit%C3%A0-uni)** — tasse, FFO, ricerca, edilizia
- **🔗 [Trasversale](https://github.com/dataciviclab/open-siope/discussions/categories/trasversale)** — temi che tagliano tutti i comparti (consulenze, debito, personale)

Vedi un dato curioso? Apri una discussione. Hai una domanda? Usa **Q&A**.

---

## 📦 I dati in breve

| Cosa | Quanto |
|---|---|
| **Enti coperti** | ~18.000 (comuni, ASL, università, regioni, province) |
| **Periodo** | 2021 — 2026 |
| **Comparti** | PRO (territorio) · REG (regioni) · SAN (sanità) · UNI (università) |
| **Voci entrate** | ~2.000 codici (IMU, TARI, IRPEF, trasferimenti, ...) |
| **Voci uscite** | ~2.700 codici (personale, beni, investimenti, interessi, ...) |

I dati puliti (CLEAN) e aggregati (MART) sono pubblici su **Google Cloud Storage**:

```
gs://dataciviclab-clean/siope/...
gs://dataciviclab-mart/siope/...
```

Accessibili via HTTPS: `https://storage.googleapis.com/dataciviclab-clean/siope/...`

---

## 🧭 Come si usa

- **Esplora le discussioni** — ogni tema parte da una domanda aperta
- **Chiedi una query** — nei commenti, chiedi un estratto dati specifico
- **Scarica i parquet** — dai bucket GCS pubblici
- **Interroga con SQL** — via DuckDB, Python, o clean-query MCP
- **Esegui la pipeline** — vedi [docs/pipeline.md](docs/pipeline.md) per dettagli tecnici

---

## 📚 Documenti tecnici

I dettagli su pipeline, metodologia e output vivono separati dal README per non appesantirlo:

- [Pipeline](docs/pipeline.md) — come eseguire, struttura, output
- [Metodologia](docs/metodologia.md) — origini dati, classificazioni, unità di misura
- [Backlog tecnico](docs/backlog_tecnico.md) — cose ancora da fare
- [Uso mart](docs/uso_mart_labeled.md) — guida alle tabelle aggregate

---

## 🏛️ DataCivicLab

open-siope è un progetto di [DataCivicLab](https://github.com/dataciviclab) — un laboratorio civico di dati aperti italiani.
