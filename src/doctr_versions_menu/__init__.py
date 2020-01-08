"""Doctr Versions Menu."""

__version__ = '0.1.0-rc1'

# All members whose name does not start with an underscore must be listed
# either in __all__ or in __private__
__all__ = []
__private__ = ['setup']

from . import ext


def setup(app):
    """Set up the Sphinx extension."""

    app.add_config_value(
        name="doctr_versions_menu_conf", default={}, rebuild="html",
    )
    app.connect('builder-inited', ext.add_versions_menu_js_file)
    app.connect('build-finished', ext.cleanup)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
