CAND ?= baseline
SUBSET ?= core
REFS ?= 0
PY := .venv/bin/python
GUARD := $(PY) -I scripts/resource_guard.py --
.PHONY: setup fetch prepare inventory build gate render checks verify site site-agent-install site-agent-uninstall
setup:
	uv sync --frozen
	$(PY) -I -m playwright install chromium webkit
fetch:
	scripts/fetch_upstream.sh
prepare:
	$(GUARD) $(PY) -I scripts/run.py prepare
inventory:
	$(PY) -I scripts/run.py inventory
build:
	$(GUARD) $(PY) -I scripts/run.py build --cand "$(CAND)" --subset "$(SUBSET)" $(if $(ICONS_DIR),--icons-dir "$(ICONS_DIR)",)
gate:
	$(GUARD) $(PY) -I scripts/run.py gate --cand "$(CAND)" $(if $(ICONS_DIR),--icons-dir "$(ICONS_DIR)",) $(if $(GATE_SUMMARY),--summary "$(GATE_SUMMARY)",)
render:
	$(GUARD) $(PY) -I scripts/run.py render --cand "$(CAND)" --out "$(OUT)" --refs "$(REFS)" --map "$(MAP)" $(if $(ICONS_DIR),--icons-dir "$(ICONS_DIR)",) $(if $(IDENTITY),--identity "$(IDENTITY)",)
checks:
	$(GUARD) $(PY) -I scripts/run.py checks --cand "$(CAND)" $(if $(ICONS_DIR),--icons-dir "$(ICONS_DIR)",)
verify:
	$(GUARD) $(PY) -I scripts/run.py verify
# Owner specimen site (opens from disk). FORCE=1 regenerates even if nothing changed.
site:
	$(PY) -I scripts/site.py $(if $(FORCE),--force,)
site-agent-install:
	$(PY) -I scripts/site.py agent-install
site-agent-uninstall:
	$(PY) -I scripts/site.py agent-uninstall
