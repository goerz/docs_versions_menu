"""Sphinx extension for showing the Doctr Versions Menu."""
import os
import shutil
import tempfile
from pathlib import Path

from sphinx.util.template import SphinxRenderer


class _JS(str):
    """Javascript code wrapper.

    The default ``docs-versions-menu.jt_t`` template renders variables via
    their __repr__. Normal strings have a quoted __repr__, this :class:`JS`
    wrapper does not.
    """

    def __repr__(self):
        return self


def add_versions_menu_js_file(app):
    """Add docs-versions-menu.js file as a static js file to Sphinx."""
    tmpdir = tempfile.mkdtemp()
    app.config._docs_versions_menu_temp_dir = tmpdir
    js_file_name = 'docs-versions-menu.js'
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
    context = dict(
        json_file=_JS(
            '"/" + window.location.pathname.split("/")[1] + "/versions.json"'
        ),
        github_project_url=_JS('getGithubProjectUrl()'),
        current_folder=_JS('getGhPagesCurrentFolder()'),
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
    js_file_path = Path(tmpdir) / js_file_name
    template = renderer.env.get_template(template_name)
    print(
        "creating %s from template %s for docs-versions-menu"
        % (js_file_name, template.filename)
    )
    with js_file_path.open('w') as js_file:
        js_file.write(template.render(**context))
    app.config.html_static_path.append(tmpdir)
    app.add_js_file(js_file_name)
    if context['badge_only']:
        app.config.html_static_path.extend(
            [
                str(Path(__file__).parent / '_css'),
                str(Path(__file__).parent / '_fonts'),
            ]
        )
        app.add_css_file('badge_only.css')


def cleanup(app, exception):
    """Remove temporary files."""
    shutil.rmtree(app.config._docs_versions_menu_temp_dir)
