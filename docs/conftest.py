"""This file is automatically executed by pytest when testing anything in the
docs folder"""
import pytest

import docs_versions_menu


@pytest.fixture(autouse=True)
def set_doctest_env(doctest_namespace):
    """Inject package itself into doctest namespace.

    This is so we don't need

    .. doctest::

        >>> import docs_versions_menu

    in any doctests
    """
    doctest_namespace['docs_versions_menu'] = docs_versions_menu
