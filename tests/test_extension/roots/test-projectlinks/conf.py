project = 'Project links docs-versions-menu test'

extensions = [
    'docs_versions_menu',
]

docs_versions_menu_conf = dict(
    github_project_url="https://github.com/goerz/docs_versions_menu",
    project_links={
        'On GitLab': {
            'Project Home': 'https://gitlab.example.com/acme/widget',
            'Issues': 'https://gitlab.example.com/acme/widget/-/issues',
        },
    },
)
