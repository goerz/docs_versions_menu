"""Doctr Versions Menu."""

__version__ = '0.1.0-dev'

# All members whose name does not start with an underscore must be listed
# either in __all__ or in __private__
__all__ = []
__private__ = ['setup']


def setup(app):
    """Set up the Sphinx extension."""
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
