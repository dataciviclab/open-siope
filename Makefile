PYTHON ?= python3
TOOLKIT = $(PYTHON) -m toolkit.cli.app

# --- Anagrafica seeds (eseguire prima dei dataset principali) ---

ANAG_SEEDS = \
	anagrafica/anag-comparti \
	anagrafica/anag-sottocomparti \
	anagrafica/anag-enti \
	anagrafica/anag-codgest-entrate \
	anagrafica/anag-codgest-uscite \
	anagrafica/anag-reg-prov \
	anagrafica/anag-comuni

.PHONY: seeds seeds-smoke
seeds:
	@for d in $(ANAG_SEEDS); do \
		echo "=== $$d ==="; \
		$(TOOLKIT) run all --config $$d/dataset.yml || exit 1; \
	done

seeds-smoke:
	@for d in $(ANAG_SEEDS); do \
		echo "=== $$d (smoke) ==="; \
		$(TOOLKIT) run all --config $$d/dataset.yml --smoke || exit 1; \
	done

# --- Dataset principali ---

.PHONY: run-entrate run-uscite run-all
run-entrate:
	$(TOOLKIT) run all --config entrate/comuni/dataset.yml

run-uscite:
	$(TOOLKIT) run all --config uscite/comuni/dataset.yml

run-all: seeds run-entrate run-uscite

# --- Smoke test (1000 righe, rapido) ---
# RAW viene eseguito senza --smoke (lo ZIP troncato non si estrae),
# CLEAN usa --smoke (1000 righe), MART processa solo quelle.

.PHONY: smoke smoke-entrate smoke-uscite
smoke: seeds smoke-entrate smoke-uscite

smoke-entrate:
	$(TOOLKIT) run raw --config entrate/comuni/dataset.yml --year 2025
	$(TOOLKIT) run clean --config entrate/comuni/dataset.yml --year 2025 --smoke
	$(TOOLKIT) run mart --config entrate/comuni/dataset.yml --year 2025

smoke-uscite:
	$(TOOLKIT) run raw --config uscite/comuni/dataset.yml --year 2025
	$(TOOLKIT) run clean --config uscite/comuni/dataset.yml --year 2025 --smoke
	$(TOOLKIT) run mart --config uscite/comuni/dataset.yml --year 2025

# --- Validazione config ---

.PHONY: check
check:
	@for f in $$(find . -name dataset.yml -not -path './.git/*' | sort); do \
		echo "→ $$f"; \
		$(TOOLKIT) inspect paths --config "$$f" --year 2024 > /dev/null 2>&1 || exit 1; \
	done
	@echo "✅ All configs valid"

# --- Pulizia ---

.PHONY: clean
clean:
	rm -rf out/data/_runs out/data/probe out/data/raw out/data/clean out/data/mart out/data/cross .tmp/

.PHONY: clean-runs
clean-runs:
	rm -rf out/data/_runs/

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:' Makefile | sort
