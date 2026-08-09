PYTHON ?= python3
# scripts/run_toolkit.py: wrapper che monkey-patcha duckdb.connect()
# per settare memory_limit e preserve_insertion_order — evita OOM in CI.
TOOLKIT = $(PYTHON) scripts/run_toolkit.py

# --- Support seeds (eseguire prima dei dataset principali) ---

ANAG_SEEDS = \
	support/anag-comparti \
	support/anag-sottocomparti \
	support/anag-enti \
	support/anag-codgest-entrate \
	support/anag-codgest-uscite \
	support/anag-reg-prov \
	support/anag-comuni

.PHONY: seeds
seeds:
	@for d in $(ANAG_SEEDS); do \
		echo "=== $$d ==="; \
		$(TOOLKIT) run --config $$d/dataset.yml || exit 1; \
	done

# --- Dataset principali ---

.PHONY: run-entrate run-uscite run-all
run-entrate:
	$(TOOLKIT) run --config datasets/siope-entrate/dataset.yml

run-uscite:
	$(TOOLKIT) run --config datasets/siope-uscite/dataset.yml

run-all: seeds run-entrate run-uscite

# --- Smoke test (--sample-rows 1000, root isolato in out/smoke/) ---

.PHONY: smoke smoke-entrate smoke-uscite
smoke: seeds-smoke smoke-entrate smoke-uscite

seeds-smoke:
	@for d in $(ANAG_SEEDS); do \
		echo "=== $$d (smoke) ==="; \
		$(TOOLKIT) run --config $$d/dataset.yml --sample-rows 1000 || exit 1; \
	done

smoke-entrate:
	$(TOOLKIT) run --config datasets/siope-entrate/dataset.yml --year 2025 --sample-rows 1000

smoke-uscite:
	$(TOOLKIT) run --config datasets/siope-uscite/dataset.yml --year 2025 --sample-rows 1000

# --- Validazione config ---

.PHONY: check
check:
	@for f in $$(find . -path '*/support/*' -name dataset.yml | sort); do \
		echo "→ $$f"; \
		$(TOOLKIT) run preflight --config "$$f" --years 2026 > /dev/null 2>&1 || exit 1; \
	done
	@for f in $$(find . -path '*/datasets/*' -name dataset.yml | sort); do \
		echo "→ $$f"; \
		$(TOOLKIT) run preflight --config "$$f" --years 2025 > /dev/null 2>&1 || exit 1; \
	done
	@echo "✅ All configs valid"

# --- Pulizia ---

.PHONY: clean
clean:
	rm -rf out/data/_runs out/data/probe out/data/raw out/data/clean out/data/mart out/data/cross .tmp/

.PHONY: clean-runs
clean-runs:
	rm -rf out/data/_runs/

# --- Verify output ---

.PHONY: verify
verify:
	python3 scripts/verify_output.py

# --- Registry (artifact catalogo — dry-run di default) ---

.PHONY: registry registry-write
registry:
	python3 scripts/build_registry.py

registry-write:
	python3 scripts/build_registry.py --write

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:' Makefile | sort
