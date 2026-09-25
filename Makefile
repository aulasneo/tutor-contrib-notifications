.DEFAULT_GOAL := help
.PHONY: help clean upgrade requirements build dist test test-format test-lint test-types test-dist test-tutor format isort

PYTHON ?= python3
SRC_DIRS = ./tutornotifications
BLACK_OPTS = --exclude templates ${SRC_DIRS}

clean: ## Remove build artifacts
	rm -rf build dist *.egg-info

upgrade: ## Upgrade development dependencies
	$(PYTHON) -m pip install --upgrade --upgrade-strategy eager -e '.[dev]'

requirements: ## Install the package and development dependencies
	$(PYTHON) -m pip install -e '.[dev]'

build: clean ## Build the package
	$(PYTHON) -m build

dist: ## Upload package to PyPI
	$(PYTHON) -m twine upload dist/*

test: test-lint test-types test-format test-dist test-tutor ## Run static, packaging, and Tutor integration checks.

test-format: ## Run code formatting tests
	$(PYTHON) -m black --check --diff $(BLACK_OPTS) tests

test-lint: ## Run code linting tests
	$(PYTHON) -m pylint --errors-only --enable=unused-import,unused-argument --ignore=templates --ignore=docs/_ext ${SRC_DIRS}

test-types: ## Run type checks.
	$(PYTHON) -m mypy --exclude=templates --ignore-missing-imports --implicit-reexport --strict ${SRC_DIRS}

test-dist: ## Build and validate distributions in a temporary directory
	@set -eu; check_dist_dir=$$(mktemp -d); \
	trap 'rm -rf "$$check_dist_dir"' EXIT; \
	$(PYTHON) -m build --outdir "$$check_dist_dir"; \
	$(PYTHON) -m twine check "$$check_dist_dir"/*

test-tutor: ## Test commands and rendered environments with isolated Tutor roots
	$(PYTHON) -m unittest discover -s tests -v

format: ## Format code automatically
	$(PYTHON) -m black $(BLACK_OPTS) tests

isort: ##  Sort imports. This target is not mandatory because the output may be incompatible with black formatting. Provided for convenience purposes.
	$(PYTHON) -m isort --skip=templates ${SRC_DIRS}

ESCAPE = 
help: ## Print this help
	@grep -E '^([a-zA-Z_-]+:.*?## .*|######* .+)$$' Makefile \
		| sed 's/######* \(.*\)/@               $(ESCAPE)[1;31m\1$(ESCAPE)[0m/g' | tr '@' '\n' \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'
