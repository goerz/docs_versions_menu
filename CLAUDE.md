# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Docs-Versions-Menu provides a versions-menu for Sphinx docs, as an alternative to Read the Docs. Two cooperating pieces:

1. A **Sphinx extension** (`docs_versions_menu`) that injects JavaScript into rendered docs; that JS reads `versions.json` from the webroot and renders a version-selector.
2. A **CLI tool** (`docs-versions-menu`) that runs in the webroot (e.g. the root of a `gh-pages` branch) and generates `versions.json` from the deployed folders.

They communicate only through `versions.json`. The package has no public Python API (see `__init__.py`): only `setup` for Sphinx and the CLI entry point.

## Development commands

Uses `uv` + `Makefile`; all tooling lives in `[dependency-groups]` in `pyproject.toml`. Run `make help` for the full list.

- `make develop` — sync the dev environment
- `make test` — full suite (pytest, doctests, coverage, `-x`); `make test-lowest` runs against lowest declared dependency versions
- `make lint` — black-check, isort-check, flake8, pylint (`make black`/`make isort` to apply)
- `make docs` — build HTML docs (`-W`, warnings are errors)
- `make release` — runs `scripts/release.py`

Override the interpreter with `make PYTHON=3.11 test` (each version gets its own `.venv/py<version>`). For a single test, bypass the Makefile:

```
uv run --all-groups pytest tests/test_cli.py::test_name -vvv
```

Doctests run on `src` modules, so docstring examples are part of the suite.

## Architecture (`src/docs_versions_menu/`)

CLI data pipeline, in dependency order:

- **`parse_version.py`** — `parse_version` + `NonVersionFolderName`, a fake "version" for non-PEP-440 folder names that sorts before real versions (reimplements LegacyVersion dropped in `packaging >= 22.0`).
- **`groups.py`** — classifies folder names into PEP 440 groups (local/dev/pre/post-releases, default-branch folders).
- **`folder_spec.py`** — `pyparsing`-based parser for the user-facing folder-specification mini-language (`versions_spec`, `latest_spec`, etc.).
- **`version_data.py`** — `get_version_data`: the core that turns folders + specs into the `versions.json` dict.
- **`cli.py`** — `click` entry point; collects folders, calls `get_version_data`, writes/`git add`s `versions.json`, renders an `index.html` redirect.
- **`ext.py`** — Sphinx side; copies the JS template into build static files. The `_JS` str subclass renders without quotes so vars emit as raw JS.

Shipped `package-data`: `_template/` (Jinja `*.js_t`/`*.html_t`), `_css/`, `_fonts/`, `_script/versions.py`.

## Conventions

- Line length 79; `black` with `skip-string-normalization` (single quotes kept). `requires-python = ">=3.10"`.
- Version single-sourced from `__version__` in `__init__.py`. Build backend is still `setuptools`; `uv` manages only environments and tasks.
- The rendered menu needs jQuery, unbundled since Sphinx 6.0 — consumers may need `sphinxcontrib.jquery` in their `conf.py`.

## Changelog (`HISTORY.rst`)

Keep `HISTORY.rst` up to date as you work. Add bullets to the `Unreleased` section at the top for any user-facing change: new features, behavior changes, removed options, dependency version changes (new minimums or newly supported major versions), and supported Python version changes. Skip pure dev-tooling changes (CI, Makefile, pre-commit config).

Format: RST bullet list, one bullet per logical change. Link issues/PRs with backtick refs (`` `#N`_ ``) and add the corresponding `.. _#N: URL` definition at the bottom of the file alongside the existing ones. Run `make check-history` to verify all references have definitions.
