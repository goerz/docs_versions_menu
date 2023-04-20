"""Parse a version-based folder name.

The ``parse_version`` function provided here is functionally equivalent to
``packaging.version.parse`` in ``packaging < 22.0``.
"""
import packaging.version


class NonVersionFolderName(packaging.version._BaseVersion):
    """A "version" that is just an arbitrary folder name"""

    def __init__(self, name):
        name = str(name)
        self.name = name
        self._key = (-1, (f'*{name}', '*final'))
        # The _key mimics the _key of a LegacyVersion in packaging < 22.0.
        # The "-1" is a hard-coded "epoch" here. A PEP 440 version can only
        # have a epoch greater than or equal to 0. This will sort
        # NonVersionFolderName before any PEP 440 version.
        #
        # Sorting behavior is inherited from _BaseVersion

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<NonVersionFolderName('{self}')>"


class VersionFolderName(packaging.version.Version):
    """A PEP440-compatible version name."""

    def __repr__(self):
        return f"<VersionFolderName('{self}')>"


def parse_version(name):
    """Parse `name` string into either a `VersionFolderName` or a
    `NonVersionFolderName` object."""
    try:
        return VersionFolderName(name)
    except packaging.version.InvalidVersion:
        return NonVersionFolderName(name)
