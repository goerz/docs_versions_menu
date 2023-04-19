"""Parse a version string

The ``parse_version`` function provided here is functionally equivalent to
``packaging.version.parse`` in ``packaging < 22.0``.

We leverage the ``packvers`` package for the desired behavior.
"""
import packvers.version


class NonVersionFolderName(packvers.version.LegacyVersion):
    """A "version" that is just an arbitrary folder name"""

    # We rely on the sorting properties of LegacyVersion relative to to a
    # proper Version, even though arbitrary folder names aren't in any sense
    # "legacy versions"
    pass


def parse_version(version):
    """Parse `version` string into either a `Version` or a
    `NonVersionFolderName` object."""
    try:
        return packvers.version.Version(version)
    except packvers.version.InvalidVersion:
        return NonVersionFolderName(version)
