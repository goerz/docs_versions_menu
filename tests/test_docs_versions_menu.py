"""Tests for `docs_versions_menu` package."""

import pytest
from pkg_resources import parse_version

import docs_versions_menu


def test_valid_version():
    """Check that the package defines a valid ``__version__``."""
    v_curr = parse_version(docs_versions_menu.__version__)
    v_orig = parse_version("0.1.0-dev")
    assert v_curr >= v_orig
