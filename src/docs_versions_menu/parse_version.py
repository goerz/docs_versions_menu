"""Parse a version string

The ``parse_version`` function provided here is functionally equivalent to
``packaging.version.parse`` in ``packaging < 22.0``.
"""
import packaging.version


def parse_version(version):
    """Parse `version` string into an object that allows version comparisons."""
    return packaging.version.parse(version)
