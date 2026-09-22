"""Sphinx extension for showing the Doctr Versions Menu."""

import os
from pathlib import Path

from sphinx.util.template import SphinxRenderer


def add_versions_menu_js_file(app):
    """Add docs-versions-menu.js static file as well as boostrap code to each page."""
    app.config.html_static_path.append(str(Path(__file__).parent / '_js'))
    app.add_js_file('docs-versions-menu-lib.js')

    template_path = [
        os.path.join(app.confdir, folder)
        for folder in app.config.templates_path
    ]
    template_name = 'docs-versions-menu.js_t'
    legacy_template_name = 'doctr-versions-menu.js_t'
    for folder in template_path:
        t_legacy = os.path.join(folder, legacy_template_name)
        t_new = os.path.join(folder, template_name)
        if os.path.isfile(t_legacy) and not os.path.isfile(t_new):
            print(
                "WARNING: using legacy template %s. This file should be "
                "renamed to %s" % (t_legacy, t_new)
            )
            template_name = legacy_template_name

    template_path.append(str(Path(__file__).parent / '_template'))
    renderer = SphinxRenderer(template_path=template_path)
    # Jinja's `tojson` filter sorts dict keys alphabetically by default,
    # which would silently reorder the sections/links in `project_links`.
    renderer.env.policies['json.dumps_kwargs'] = {'sort_keys': False}
    context = dict(
        github_project_url=None,
        project_links=None,
        badge_only=(app.config.html_theme != 'sphinx_rtd_theme'),
        menu_title="Docs",
    )
    if app.config.doctr_versions_menu_conf:
        print(
            "WARNING: using legacy options from "
            "`doctr_versions_menu_conf`. This option should be "
            "renamed to `docs_versions_menu_conf`"
        )
        context.update(app.config.doctr_versions_menu_conf)
    context.update(app.config.docs_versions_menu_conf)
    template = renderer.env.get_template(template_name)
    print(
        "injecting configuration from template %s for docs-versions-menu"
        % template.filename
    )
    app.add_js_file(None, body=template.render(**context))

    if context['badge_only']:
        app.config.html_static_path.extend(
            [
                str(Path(__file__).parent / '_css'),
                str(Path(__file__).parent / '_fonts'),
            ]
        )
        app.add_css_file('badge_only.css')
