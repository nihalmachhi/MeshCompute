PYTHON ?= python
PIP ?= $(PYTHON) -m pip

.PHONY: install up down migrate lint typecheck test check demo bench
install:
	$(PIP) install -e ".[dev]"
up:
	docker compose up --build
down:
	docker compose down
migrate:
	alembic upgrade head
lint:
	ruff check src tests scripts benchmarks
typecheck:
	mypy src
test:
	pytest
check: lint typecheck test
demo:
	$(PYTHON) scripts/run_demo.py
bench:
	$(PYTHON) -m benchmarks.run_benchmark
