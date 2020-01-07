"""Set up the environment for doctests

This file is automatically evaluated by py.test. It ensures that we can write
doctests without distracting import statements in the doctest.
"""
import pytest

import doctr_versions_menu


@pytest.fixture(autouse=True)
def set_doctest_env(doctest_namespace):
    doctest_namespace['doctr_versions_menu'] = doctr_versions_menu
