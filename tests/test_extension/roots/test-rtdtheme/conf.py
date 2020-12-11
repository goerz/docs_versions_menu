project = 'Basic doctr-versions-menu test'

import sphinx_rtd_theme


html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

extensions = [
    'doctr_versions_menu',
]

doctr_versions_menu_conf = dict(
    menu_title="Docs",
)
