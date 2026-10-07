.PHONY: help install sync lint format typecheck test test-cov check clean demo

# ─── Aide ────────────────────────────────────────────────
help:  ## Affiche cette aide
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\n"} \
		/^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# ─── Environnement ───────────────────────────────────────
install:  ## Installe uv si absent
	@command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh

sync:  ## Sync toutes les dépendances du workspace
	uv sync --all-packages --all-extras

# ─── Qualité ─────────────────────────────────────────────
lint:  ## Vérifie le code avec ruff
	uv run ruff check .

format:  ## Formate le code avec ruff
	uv run ruff format .
	uv run ruff check --fix .

typecheck:  ## Vérifie les types avec mypy strict
	uv run mypy packages brain runtime protocols

# ─── Tests ───────────────────────────────────────────────
test:  ## Lance les tests
	uv run pytest

test-cov:  ## Lance les tests avec couverture
	uv run pytest --cov --cov-report=term-missing --cov-report=html

# ─── Qualité globale ─────────────────────────────────────
check: lint typecheck test  ## Lance lint + typecheck + tests

# ─── Pré-commit ──────────────────────────────────────────
pre-commit-install:  ## Installe les hooks pre-commit
	uv run pre-commit install

pre-commit-run:  ## Lance les hooks sur tous les fichiers
	uv run pre-commit run --all-files

# ─── Démo (à venir v0.1) ─────────────────────────────────
demo:  ## Lance la démo v0.1 (pick red cube)
	@echo "🚧 Demo v0.1 not yet implemented. Coming soon."
	@echo "   Target: same brain, N simulated robots, one goal."

# ─── Nettoyage ───────────────────────────────────────────
clean:  ## Nettoie les artefacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
