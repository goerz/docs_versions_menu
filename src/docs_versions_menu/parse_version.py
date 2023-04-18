"""Parse a version string

The ``parse_version`` function provided here is functionally equivalent to
``packaging.version.parse`` in ``packaging < 22.0``.

We leverage the ``packvers`` package for the desired behavior.
"""
import packvers.version


LegacyVersion = packvers.version.LegacyVersion


def parse_version(version):
    """Parse `version` string into an object that allows version comparisons."""
    return packvers.version.parse(version)
