"""MCP server per interrogare i dati SIOPE in linguaggio naturale.

Tool parlanti: cerca enti, bilanci, categorie di spesa, top enti, serie storiche.
Legge parquet da GCS via DuckDB + lab-connectors.

Trasporto:
  - default (stdin/stdout): compatibile con configurazioni MCP locali
  - SIOPE_TRANSPORT=streamable-http: server HTTP remoto su SIOPE_HOST:SIOPE_PORT
    (usato per deploy Cloud Run / Docker)
"""

from __future__ import annotations

import os
from typing import Any

from lab_connectors.mcp import create_mcp_server, guard_timed

from siope_client import (
    cerca_ente,
    elenca_enti,
    get_bilancio,
    lookup_ente,
    serie_storica,
    spesa_categoria,
    top_enti,
)

SERVER = "siope"


def _list_response(result: Any) -> dict[str, Any]:
    """Wrappa una lista in dict con data/count per structured_output di FastMCP.

    FastMCP con ``structured_output=True`` e return type ``list[T]`` crea
    un pydantic model ``{name}Output(result=list[T])`` che wrappa il risultato
    in ``{"result": [...]}``. OpenCode non gestisce questo formato.

    Con ``dict[str, Any]`` FastMCP usa RootModel senza wrapping aggiuntivo.
    """
    if isinstance(result, dict) and ("error" in result or "code" in result):
        return result
    return {"data": result, "count": len(result)}


mcp = create_mcp_server(
    name=SERVER,
    instructions=(
        "Connettore MCP per i dati SIOPE (entrate e uscite degli enti pubblici italiani). "
        "Permette di: cercare enti per nome, ottenere il bilancio di un ente, "
        "vedere la composizione per categoria, confrontare enti e vedere serie storiche. "
        "I dati coprono 2021-2026 e tutti i comparti (PRO comuni, REG regioni, "
        "SAN sanità, UNI università, e altri).\n\n"
        "Esempi di codici ente: Roma=800000047, Milano=800000013, ASL Roma 1=006327004, "
        "REGIONE LAZIO=006479801."
    ),
)


@mcp.tool(
    description=(
        "Cerca enti pubblici italiani per nome o parte del nome. "
        "Opzionalmente filtra per tipo (es. COMUNE, ASL, ATENEO, REGIONE, MINISTERI). "
        "I COMUNE hanno priorità nei risultati. "
        "Restituisce codice, denominazione, tipo ente, provincia."
    ),
    structured_output=True,
)
def siope_cerca_ente(query: str, tipo: str | None = None, limit: int = 20) -> dict[str, Any]:
    return _list_response(guard_timed(cerca_ente, "siope_cerca_ente", query, tipo, limit, logger_name=SERVER))


@mcp.tool(
    description=(
        "Totale entrate o uscite di un ente in un anno specifico. "
        "lato='entrate' o 'uscite'. I valori sono in euro. "
        "Esempi: Roma=800000047, Milano=800000013."
    ),
    structured_output=True,
)
def siope_get_bilancio(codice_ente: str, anno: int, lato: str) -> dict[str, Any]:
    return guard_timed(get_bilancio, "siope_get_bilancio", codice_ente, anno, lato, logger_name=SERVER)


@mcp.tool(
    description=(
        "Composizione delle entrate/uscite di un ente per macro-categoria. "
        "Per entrate: Imposte proprie, Trasferimenti, Fondi perequativi, ecc. "
        "Per uscite: Personale, Acquisto beni, Investimenti, Interessi, ecc."
    ),
    structured_output=True,
)
def siope_spesa_categoria(codice_ente: str, anno: int, lato: str) -> dict[str, Any]:
    return _list_response(guard_timed(spesa_categoria, "siope_spesa_categoria", codice_ente, anno, lato, logger_name=SERVER))


@mcp.tool(
    description=(
        "Dato un codice_ente, restituisce denominazione, tipo, comparto. "
        "Utile quando hai un codice da un altro tool o da una discussione."
    ),
    structured_output=True,
)
def siope_lookup_ente(codice_ente: str) -> dict[str, Any] | None:
    return guard_timed(lookup_ente, "siope_lookup_ente", codice_ente, logger_name=SERVER)


@mcp.tool(
    description=(
        "Classifica degli enti con maggiori entrate o uscite in un anno. "
        "Opzionalmente filtra per comparto (PRO, REG, SAN, UNI, MON, CDC...). "
        "Utile per rispondere a 'qual è il comune che spende di più?'."
    ),
    structured_output=True,
)
def siope_top_enti(anno: int, lato: str, comparto: str | None = None, limit: int = 10) -> dict[str, Any]:
    return _list_response(guard_timed(top_enti, "siope_top_enti", anno, lato, comparto, limit, logger_name=SERVER))


@mcp.tool(
    description="Serie storica 2021-2026 delle entrate o uscite di un ente. Mostra l'andamento anno per anno.",
    structured_output=True,
)
def siope_serie_storica(codice_ente: str, lato: str) -> dict[str, Any]:
    return _list_response(guard_timed(serie_storica, "siope_serie_storica", codice_ente, lato, logger_name=SERVER))


@mcp.tool(
    description=(
        "Elenca gli enti di un comparto (PRO, REG, SAN, UNI, MON, CDC...) "
        "o di un tipo specifico (COMUNE, ASL, ATENEO, REGIONE...)."
    ),
    structured_output=True,
)
def siope_enti_comparto(comparto: str | None = None, tipo: str | None = None, limit: int = 50) -> dict[str, Any]:
    return _list_response(guard_timed(elenca_enti, "siope_enti_comparto", comparto, tipo, limit, logger_name=SERVER))


def main() -> None:
    """Entry point: avvia il server MCP con trasporto configurabile.

    Variabili d'ambiente:
      SIOPE_TRANSPORT  — "stdio" (default) o "streamable-http"
      SIOPE_HOST       — host su cui ascoltare (default "0.0.0.0" in HTTP, "127.0.0.1" in stdio)
      SIOPE_PORT       — porta (default 8000)
      PORT             — fallback per SIOPE_PORT (convenzione Cloud Run)
    """
    transport = os.environ.get("SIOPE_TRANSPORT", "stdio")

    if transport in ("streamable-http", "sse", "http"):
        mcp.settings.host = os.environ.get("SIOPE_HOST", "0.0.0.0")
        mcp.settings.port = int(os.environ.get("SIOPE_PORT", os.environ.get("PORT", "8000")))
        # FastMCP attiva DNS rebinding protection di default solo per localhost.
        # In Cloud Run l'Host header è il dominio .run.app — lo aggiungiamo agli
        # allowed_hosts (configurabile via SIOPE_ALLOWED_HOST per altri domini).
        from mcp.server.transport_security import TransportSecuritySettings
        cloud_run_host = os.environ.get(
            "SIOPE_ALLOWED_HOST",
            "siope-mcp-217326868340.europe-west1.run.app",
        )
        mcp.settings.transport_security = TransportSecuritySettings(
            allowed_hosts=[
                cloud_run_host,
                f"{cloud_run_host}:*",
                "127.0.0.1:*",
                "localhost:*",
            ],
            allowed_origins=[
                f"https://{cloud_run_host}",
            ],
        )
        mcp.run("streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
