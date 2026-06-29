.PHONY: help develop test test-lowest coverage docs docs-pdf docs-serve \
        black black-check isort isort-check flake8 pylint lint check-history \
        shell devrepl dist dist-check test-upload upload release \
        upgrade clean distclean pre-commit-install

.DEFAULT_GOAL := help

# Python version for the development environment. Override on the command line,
# e.g. `make PYTHON=3.11 test`. uv downloads the interpreter if it is missing.
PYTHON ?= 3.12

# Dependency resolution strategy. Use `make RESOLUTION=lowest-direct test` to
# verify the project against the lowest declared dependency versions.
RESOLUTION ?= highest

# Each Python version gets its own environment so that switching PYTHON does not
# force a re-sync. `make distclean` removes the whole .venv tree.
export UV_PROJECT_ENVIRONMENT := .venv/py$(PYTHON)

# All development tooling lives in dependency groups (see pyproject.toml).
UV := uv run --python $(PYTHON) --resolution $(RESOLUTION) --all-groups

TESTS ?= src tests README.rst
SOURCES ?= src tests scripts

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
    match = re.match(r'^([a-z0-9A-Z_-]+):.*?## (.*)$$', line)
    if match:
        target, help = match.groups()
        print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:  ## Show this help
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

develop: .git/hooks/pre-commit  ## Create or sync the development environment

# Install the pre-commit git hook whenever the config or dependencies change.
.git/hooks/pre-commit: .pre-commit-config.yaml pyproject.toml
	uv sync --python $(PYTHON) --resolution $(RESOLUTION) --all-groups
	$(UV) pre-commit install

pre-commit-install:  ## (Re-)install the pre-commit git hook
	$(UV) pre-commit install

test: | .git/hooks/pre-commit  ## Run the test suite
	$(UV) pytest -vvv --doctest-modules --cov=docs_versions_menu --durations=10 -x -s $(TESTS)

test-lowest:  ## Run the test suite against the lowest declared dependency versions
	$(MAKE) RESOLUTION=lowest-direct test

coverage:  ## Run tests with coverage and write an HTML report to ./htmlcov
	$(UV) pytest -vvv --doctest-modules --cov=docs_versions_menu --cov-report=term --cov-report=html --durations=10 -s $(TESTS)
	@echo "open htmlcov/index.html"

docs:  ## Build the HTML documentation
	$(UV) sphinx-build -W -b html docs docs/_build/html
	@echo "open docs/_build/html/index.html"

docs-pdf:  ## Build the PDF documentation via LaTeX
	$(UV) sphinx-build -b latex docs docs/_build/latex
	$(UV) python docs/build_pdf.py docs/_build/latex/*.tex

docs-serve:  ## Serve the documentation locally with auto-rebuild
	$(UV) sphinx-autobuild docs docs/_build/html

black: | .git/hooks/pre-commit  ## Reformat the code with black
	$(UV) black $(SOURCES)

black-check: | .git/hooks/pre-commit  ## Check code formatting with black
	$(UV) black --check --diff $(SOURCES)

isort: | .git/hooks/pre-commit  ## Sort imports with isort
	$(UV) isort $(SOURCES)

isort-check: | .git/hooks/pre-commit  ## Check import sorting with isort
	$(UV) isort --check-only --diff $(SOURCES)

flake8: | .git/hooks/pre-commit  ## Check style with flake8
	$(UV) flake8 $(SOURCES)

pylint: | .git/hooks/pre-commit  ## Check the code with pylint
	$(UV) pylint src

lint: black-check isort-check check-history  ## Run all linters

check-history:  ## Validate HISTORY.rst link references
	uv run scripts/check_history.py

shell:  ## Open a shell inside the development environment
	$(UV) $$SHELL

devrepl:  ## Launch an IPython REPL with the editable package and dev tools
	$(UV) ipython

dist:  ## Build a source distribution and wheel into ./dist
	uv build

dist-check: dist  ## Check the built distributions with twine
	uvx twine check dist/*

test-upload: dist-check  ## Upload a release to test.pypi.org
	uvx twine upload --repository-url https://test.pypi.org/legacy/ dist/*

upload: dist-check  ## Upload a release to pypi.org
	uvx twine upload dist/*

release:  ## Create a new version, package, and upload it
	$(UV) python scripts/release.py

upgrade:  ## Upgrade locked dependency versions to the latest compatible release
	uv lock --upgrade

clean:  ## Remove build, test, and documentation artifacts
	rm -rf build dist .eggs *.egg-info src/*.egg-info
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache
	rm -rf docs/_build
	find . -type d -name __pycache__ -exec rm -rf {} +

distclean: clean  ## Remove all generated files, including the .venv environments
	rm -rf .venv uv.lock .tox

# How to execute notebook files
%.ipynb.log: %.ipynb
	$(UV) jupyter nbconvert --to notebook --execute --inplace \
		--allow-errors --ExecutePreprocessor.kernel_name='python3' \
		--ExecutePreprocessor.timeout=-1 --config=/dev/null \
		$< 2>&1 | tee $@
