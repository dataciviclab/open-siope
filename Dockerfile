FROM python:3.12-slim

# git serve per pip install da GitHub, poi lo rimuoviamo
RUN apt-get update -qq && apt-get install -y -qq git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# lab-connectors non è su PyPI — installiamo da GitHub via git, commit pinnato
# duckdb ha wheel precompilate, ok anche su slim
# PIN: 773db19 (HEAD lab-connectors al 2026-06-30)
RUN pip install --no-cache-dir \
    "lab-connectors[mcp] @ git+https://github.com/dataciviclab/lab-connectors.git@773db197159d96d3652a5aa979a440f24040236e" \
    "duckdb>=1.5.3,<2" && \
    apt-get purge -y git && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Server code
COPY mcp_server/server.py mcp_server/siope_client.py ./

# Default: streamable-http per deploy remoto
# Cloud Run inietta PORT automaticamente
ENV SIOPE_TRANSPORT=streamable-http \
    SIOPE_HOST=0.0.0.0

# Cloud Run inietta PORT (default 8080) — il server lo usa via fallback
EXPOSE 8080

CMD ["python", "server.py"]
