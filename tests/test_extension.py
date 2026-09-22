"""Test for the docs_versions_menu Sphinx extension."""

from pathlib import Path

import pytest


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
    return Path(__file__).with_suffix('') / 'roots'


@pytest.mark.sphinx('html', testroot='basic')
def test_basic(app, status, warning):
    """Test building documentation with the docs_versions_menu extension.

    This tests the default configuration in ./test_extension/roots/test-basic/
    """
    app.build()
    _build = Path(app.outdir)
    assert (_build / 'index.html').is_file()
    assert (_build / '_static' / 'docs-versions-menu-lib.js').is_file()
    assert (_build / '_static' / 'badge_only.css').is_file()
    html = (_build / 'index.html').read_text()
    assert 'src="_static/docs-versions-menu-lib.js' in html


@pytest.mark.sphinx('html', testroot='rtdtheme')
def test_rtdtheme(app, status, warning):
    """Test building documentation with the docs_versions_menu extension.

    This tests a configuration using the RTD theme, in
    ./test_extension/roots/test-rtdtheme/
    """
    app.build()
    _build = Path(app.outdir)
    assert (_build / 'index.html').is_file()
    assert (_build / '_static' / 'docs-versions-menu-lib.js').is_file()
    assert not (_build / '_static' / 'badge_only.css').is_file()
    html = (_build / 'index.html').read_text()
    assert 'src="_static/docs-versions-menu-lib.js' in html


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
    assert (_build / '_static' / 'docs-versions-menu-lib.js').is_file()
    assert not (_build / '_static' / 'badge_only.css').is_file()
    html = (_build / 'index.html').read_text()
    assert 'src="_static/docs-versions-menu-lib.js' in html
    assert "var my_var = 'custom variable';" in html
    assert (
        "var github_project_url = 'https://github.com/goerz/docs_versions_menu';"
        in html
    )
    assert "var menu_title = 'Docs'" in html


@pytest.mark.sphinx('html', testroot='projectlinks')
def test_project_links(app, status, warning):
    """Test building documentation with a custom ``project_links`` setting.

    This tests the default ``docs-versions-menu.js_t`` template (unlike
    ``test_custom`` above, which overrides it with a legacy custom
    template), and that both ``project_links`` and ``github_project_url``
    from ``docs_versions_menu_conf`` are forwarded to the rendered
    JavaScript; see ./test_extension/roots/test-projectlinks/
    """
    app.build()
    _build = Path(app.outdir)
    assert (_build / 'index.html').is_file()
    html = (_build / 'index.html').read_text()
    assert 'src="_static/docs-versions-menu-lib.js' in html
    assert (
        'githubProjectUrl: "https://github.com/goerz/docs_versions_menu"'
        in html
    )
    assert '"On GitLab"' in html
    assert '"Project Home": "https://gitlab.example.com/acme/widget"' in html
    assert (
        '"Issues": "https://gitlab.example.com/acme/widget/-/issues"' in html
    )
    # `project_links` insertion order must be preserved (not resorted
    # alphabetically, which would put "Issues" before "Project Home").
    assert html.index('"Project Home"') < html.index('"Issues"')
