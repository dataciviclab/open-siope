# MCP Server SIOPE

Tool parlanti per interrogare i dati SIOPE — entrate e uscite degli enti pubblici italiani.
Legge parquet da GCS pubblico — **nessun file locale, nessun secret necessario**.

🟢 **Live**: `https://siope-mcp-217326868340.europe-west1.run.app/mcp`

## Tool

| Tool | Cosa fa |
|---|---|
| `siope_cerca_ente` | Cerca enti per nome |
| `siope_get_bilancio` | Totale entrate/uscite annuo di un ente |
| `siope_spesa_categoria` | Composizione per macro-categoria |
| `siope_top_enti` | Classifica enti per importo |
| `siope_serie_storica` | Trend 2021-2026 |
| `siope_enti_comparto` | Elenca enti per comparto/tipo |
| `siope_lookup_ente` | Dettaglio ente per codice |

## Modalità d'uso

### Locale (stdio)

```json
{
  "mcpServers": {
    "siope": {
      "command": ["python", "/path/to/open-siope/mcp_server/server.py"],
      "enabled": true
    }
  }
}
```

Dipendenze: `pip install -r mcp_server/requirements.txt`

### Remoto (streamable-HTTP)

Nessuna installazione — solo un URL nella config MCP:

```json
{
  "mcpServers": {
    "siope": {
      "url": "https://siope-mcp-217326868340.europe-west1.run.app/mcp"
    }
  }
}
```

Funziona da qualsiasi client MCP (Claude Desktop, OpenCode, Copilot, Cursor).

```python
# Test rapido in Python
import httpx, json

url = "https://siope-mcp-217326868340.europe-west1.run.app/mcp"
headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}

with httpx.Client() as c:
    sid = c.post(url, json={"jsonrpc":"2.0","id":1,"method":"initialize",
        "params":{"protocolVersion":"2024-11-05","capabilities":{},
                  "clientInfo":{"name":"test","version":"0.1"}}},
        headers=headers).headers.get("mcp-session-id","")
    h2 = {**headers, "mcp-session-id": sid}
    r = c.post(url, json={"jsonrpc":"2.0","id":2,"method":"tools/call",
        "params":{"name":"siope_cerca_ente","arguments":{"query":"Roma","limit":2}}}, headers=h2)
    print(r.text)
```

## Deploy

Il server è deployato su **Cloud Run**. Per aggiornarlo dopo modifiche:

```bash
git push  # eventuali modifiche in locale
gcloud run deploy siope-mcp --source . --region europe-west1 --allow-unauthenticated
```

### Build manuale con Docker

```bash
docker build -t siope-mcp -f Dockerfile .
docker run -e SIOPE_TRANSPORT=streamable-http -p 8000:8000 siope-mcp
```

### Variabili d'ambiente

| Variabile | Default | Descrizione |
|---|---|---|
| `SIOPE_TRANSPORT` | `stdio` | `streamable-http` per deploy remoto |
| `SIOPE_HOST` | `0.0.0.0` | Host di ascolto (HTTP) |
| `SIOPE_PORT` | `8000` | Porta (fallback a `$PORT` per Cloud Run) |
| `SIOPE_ALLOWED_HOST` | (dominio .run.app) | Host per DNS rebinding protection |

## API

Con trasporto `streamable-http`, il server espone:

| Endpoint | Metodo | Descrizione |
|---|---|---|
| `/mcp` | POST | Endpoint MCP Streamable HTTP |

## License

Vedi [LICENSE](../LICENSE).
