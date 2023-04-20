"""Docs Versions Menu.

This package does not define a public API: it publicly provides only a Sphinx
extension and a command line program.
"""

__version__ = '0.5.2'

# All members whose name does not start with an underscore must be listed
# either in __all__ or in __private__
__all__ = []
__private__ = ['setup']

from . import cli, ext


def setup(app):
    """Set up the Sphinx extension."""

    app.add_config_value(
        name="doctr_versions_menu_conf",
        default={},
        rebuild="html",
    )
    app.add_config_value(
        name="docs_versions_menu_conf",
        default={},
        rebuild="html",
    )
    app.connect('builder-inited', ext.add_versions_menu_js_file)
    app.connect('build-finished', ext.cleanup)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
