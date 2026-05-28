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

.PHONY: seeds
seeds:
	@for d in $(ANAG_SEEDS); do \
		echo "=== $$d ==="; \
		$(TOOLKIT) run all --config $$d/dataset.yml || exit 1; \
	done

# --- Dataset principali ---

.PHONY: run-entrate run-uscite run-all
run-entrate:
	$(TOOLKIT) run all --config entrate/dataset.yml

run-uscite:
	$(TOOLKIT) run all --config uscite/dataset.yml

run-all: seeds run-entrate run-uscite

.PHONY: comparti
comparti:
	@echo "Comparti disponibili:"
	@echo "  PRO    — Comuni, Province, Citta' metropolitane"
	@echo "  REG    — Regioni e province autonome"
	@echo "  SAN    — ASL, AO, IRCCS, Policlinici"
	@echo "  UNI    — Universita' e dipartimenti"
	@echo "Si eseguono con: make run-entrate / make run-uscite"

# --- Smoke test (--sample-rows 1000, root isolato in out/smoke/) ---

.PHONY: smoke smoke-entrate smoke-uscite
smoke: seeds-smoke smoke-entrate smoke-uscite

seeds-smoke:
	@for d in $(ANAG_SEEDS); do \
		echo "=== $$d (smoke) ==="; \
		$(TOOLKIT) run all --config $$d/dataset.yml --sample-rows 1000 || exit 1; \
	done

smoke-entrate:
	$(TOOLKIT) run all --config entrate/dataset.yml --year 2025 --sample-rows 1000

smoke-uscite:
	$(TOOLKIT) run all --config uscite/dataset.yml --year 2025 --sample-rows 1000

# --- Validazione config ---

.PHONY: check
check:
	@for f in $$(find . -path '*/anagrafica/*' -name dataset.yml | sort); do \
		echo "→ $$f"; \
		$(TOOLKIT) inspect paths --config "$$f" --year 2026 > /dev/null 2>&1 || exit 1; \
	done
	@for f in $$(find . \( -path '*/entrate/*' -o -path '*/uscite/*' \) -name dataset.yml | sort); do \
		echo "→ $$f"; \
		$(TOOLKIT) inspect paths --config "$$f" --year 2025 > /dev/null 2>&1 || exit 1; \
	done
	@for f in $$(find . -path '*/cross/*' -name dataset.yml | sort); do \
		echo "→ $$f"; \
		$(TOOLKIT) inspect paths --config "$$f" --year 2025 > /dev/null 2>&1 || exit 1; \
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

# --- Explorer Observable ---

.PHONY: explorer
explorer:
	cd explorer && npm run build
	@echo "✅ Explorer built in docs/explorer/"
