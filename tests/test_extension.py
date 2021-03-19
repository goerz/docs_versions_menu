"""Test for the docs_versions_menu Sphinx extension."""
from pathlib import Path

import pytest
from sphinx.testing.path import path as sphinx_path


@pytest.fixture
def rootdir():
    """The directory in which to search for testroots.

    This is used by any test using the pytest.mark.sphinx decorator. For a
    `testroot` specified in the decorator, the rootdir will be
    "./test_extension/roots/test-<testroot>".

    The rootdir must contain a conf.py file. All of the rootdir's content will
    be copied to a temporary folder, and the Sphinx builder will be invoked
    inside that folder.
    """
    return sphinx_path(str(Path(__file__).with_suffix('') / 'roots'))


@pytest.mark.sphinx('html', testroot='basic')
def test_basic(app, status, warning):
    """Test building documentation with the docs_versions_menu extension.

    This tests the default configuration in ./test_extension/roots/test-basic/
    """
    app.build()
    _build = Path(app.outdir)
    assert (_build / 'index.html').is_file()
    assert (_build / '_static' / 'docs-versions-menu.js').is_file()
    assert (_build / '_static' / 'badge_only.css').is_file()
    html = (_build / 'index.html').read_text()
    assert 'src="_static/docs-versions-menu.js"' in html


@pytest.mark.sphinx('html', testroot='rtdtheme')
def test_rtdtheme(app, status, warning):
    """Test building documentation with the docs_versions_menu extension.

    This tests a configuration using the RTD theme, in
    ./test_extension/roots/test-rtdtheme/
    """
    app.build()
    _build = Path(app.outdir)
    assert (_build / 'index.html').is_file()
    assert (_build / '_static' / 'docs-versions-menu.js').is_file()
    assert not (_build / '_static' / 'badge_only.css').is_file()
    html = (_build / 'index.html').read_text()
    assert 'src="_static/docs-versions-menu.js"' in html
    js = (_build / '_static' / 'docs-versions-menu.js').read_text()
    assert "<span class='fa fa-book'> Docs </span>" in js


@pytest.mark.sphinx('html', testroot='custom')
def test_custom(app, status, warning):
    """Test building documentation with the docs_versions_menu extension.

    This tests a configuration with full customization (custom template for the
    JS file, and a custom docs_versions_menu_conf dict in conf.py;
    ./test_extension/roots/test-custom/
    """
    app.build()
    _build = Path(app.outdir)
    assert (_build / 'index.html').is_file()
    assert (_build / '_static' / 'docs-versions-menu.js').is_file()
    assert not (_build / '_static' / 'badge_only.css').is_file()
    html = (_build / 'index.html').read_text()
    assert 'src="_static/docs-versions-menu.js"' in html
    js = (_build / '_static' / 'docs-versions-menu.js').read_text()
    # fmt: off
    assert "var my_var = 'custom variable';" in js
    assert 'var current_folder = getGhPagesCurrentFolder();' in js
    assert "var github_project_url = 'https://github.com/goerz/docs_versions_menu';" in js
    assert 'var json_file = "/" + window.location.pathname.split("/")[1] + "/versions.json";' in js
    assert "var menu_title = 'Docs'" in js
    # fmt: on
