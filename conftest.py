import pytest

import docs_versions_menu

collect_ignore = ["tests/test_extension/roots", "docs/conf.py"]
collect_ignore_glob = ["conf.py"]


@pytest.fixture(autouse=True)
def set_doctest_env(doctest_namespace):
    doctest_namespace['docs_versions_menu'] = docs_versions_menu
