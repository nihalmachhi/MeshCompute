PYTHON ?= python

.PHONY: install up down migrate lint typecheck test check demo bench bench-sim reproduce site-fixtures
install:
	uv sync --extra dev
up:
	docker compose up --build
down:
	docker compose down
migrate:
	uv run alembic upgrade head
lint:
	uv run ruff check .
typecheck:
	uv run mypy src
test:
	uv run pytest
check: lint typecheck test
demo:
	uv run python scripts/run_demo.py
bench:
	uv run python -m benchmarks.run_benchmark
bench-sim:
	uv run python -m meshcompute.sim.report
reproduce:
	uv run python -m meshcompute.sim.report
site-fixtures:
	python site/scripts/export_fixtures.py