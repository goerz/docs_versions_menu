project = 'Basic docs-versions-menu test'

import sphinx_rtd_theme


html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

extensions = [
    'docs_versions_menu',
]

docs_versions_menu_conf = dict(
    menu_title="Docs",
)
