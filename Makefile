CAND ?= baseline
SUBSET ?= core
REFS ?= 0
PY := .venv/bin/python
GUARD := $(PY) -I scripts/resource_guard.py --
.PHONY: setup fetch prepare inventory build gate render verify
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
	$(GUARD) $(PY) -I scripts/run.py render --cand "$(CAND)" --out "$(OUT)" --refs "$(REFS)" --map "$(MAP)" $(if $(ICONS_DIR),--icons-dir "$(ICONS_DIR)",)
verify:
	$(GUARD) $(PY) -I scripts/run.py verify
