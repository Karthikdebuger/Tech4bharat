.PHONY: help setup test lint typecheck check dev-backend dev-frontend demo gtverify

help:
	@echo "Gold Trust AI — Commands"
	@echo "  make setup        Install backend and frontend dependencies"
	@echo "  make test         Run all unit, property, and differential tests"
	@echo "  make lint         Run Ruff linter and formatter checks"
	@echo "  make typecheck    Run Mypy strict type checking"
	@echo "  make check        Run lint, typecheck, and import-linter contracts"
	@echo "  make demo         Launch demo backend and frontend"
	@echo "  make gtverify     Run independent CLI receipt verifier"

setup:
	cd backend && uv sync --extra dev
	cd frontend && npm install

test:
	cd backend && .venv/Scripts/pytest -v

lint:
	cd backend && .venv/Scripts/ruff check .
	cd backend && .venv/Scripts/ruff format --check .

typecheck:
	cd backend && .venv/Scripts/mypy app tests tools

check: lint typecheck
	cd backend && .venv/Scripts/lint-imports
	cd backend && .venv/Scripts/pytest -q

gtverify:
	cd backend && .venv/Scripts/python -m tools.gtverify.main tests/vectors/sample_receipt.json

demo:
	@echo "Starting Gold Trust AI Services..."
	cd deploy && docker compose up -d
