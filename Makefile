.PHONY: test proof demo docs bundle clean

PYTHON ?= $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi)

test:
	$(PYTHON) -m pytest -q

proof:
	$(PYTHON) run_full_proof.py

demo:
	$(PYTHON) scripts/state_tree_demo.py

docs:
	@echo "Public documentation lives under docs/. See docs/index.md."

bundle:
	@echo "Public source export: use git archive or rsync with exclusions from docs/public_release_doctrine.md"

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +
