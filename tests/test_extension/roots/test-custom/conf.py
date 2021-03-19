from pathlib import Path


project = 'docs-versions-menu test'

extensions = [
    'docs_versions_menu',
]

templates_path = [str(Path(__file__).parent / '_templates')]
# temlates_path entries are supposed to be relative to the the configuration
# directory, but for some reason this is not working (maybe a bug in
# sphinx.testing?). Thus, we set an absolute path here.

docs_versions_menu_conf = dict(
    github_project_url="https://github.com/goerz/docs_versions_menu",
    my_var="custom variable",
    badge_only=False,
    menu_title="Docs",
)
