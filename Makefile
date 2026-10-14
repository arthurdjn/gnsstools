.DEFAULT_GOAL := help

PACKAGE:=gnsstools
SRC:=$(PACKAGE)
CMD:=uv run --no-sync

# Environment

.PHONY: install
install: ## Create .venv with the package, its extras and the development tools
	uv sync --all-extras

.PHONY: lock
lock: ## Update uv.lock after editing the dependencies in pyproject.toml
	uv lock

# Linting, formatting, etc.

.PHONY: format
format: ## Format the source code
	$(CMD) ruff format $(SRC)

.PHONY: lint
lint: ## Lint the source code
	$(CMD) ruff check $(SRC)

.PHONY: lint-fix
lint-fix: ## Lint the source code and apply the safe fixes
	$(CMD) ruff check --fix $(SRC)

.PHONY: all
all: format lint-fix ## Run all formatting and linting commands

# Packaging

.PHONY: build
build: ## Build the sdist and the wheel into dist/
	uv build

# Misc

.PHONY: clean
clean: ## Clear local caches and build artifacts
	rm -rf `find . -name __pycache__ -not -path "./.venv/*"`
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -f .coverage
	rm -f .coverage.*
	rm -rf *.egg-info
	rm -rf build
	rm -rf dist

.PHONY: help
help: ## Show available commands
	@awk '/^[a-zA-Z0-9_-]+:.*?## .*$$/ { \
		helpCommand = substr($$0, 1, index($$0, ":")-1); \
		helpMessage = substr($$0, index($$0, "## ") + 3); \
		printf "\033[36m%-15s\033[0m %s\n", helpCommand, helpMessage; \
	}' $(MAKEFILE_LIST)
