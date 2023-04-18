"""Test the parse_version function"""
from docs_versions_menu.parse_version import parse_version


def test_parse_version():
    """Test that :func:`parse_version` behaves like ``packaging.version.parse`
    in ``packaging < 22.0``.
    """
    versions = [
        "1.0",
        "0.8.3",
        "v0.1.0",
        "v0.2.1",
        "v0.2.1+dev",
        "v0.2.1-dev",
        "v0.2.1-rc1",
        "v0.2.1-rc2",
        "main",
        "master",
        "fix-bug",
    ]
    for version in versions:
        assert parse_version(version) is not None  # should not error
    sorted_versions = sorted(versions, key=parse_version)
    assert sorted_versions == [
        'fix-bug',
        'main',
        'master',
        'v0.1.0',
        'v0.2.1-dev',
        'v0.2.1-rc1',
        'v0.2.1-rc2',
        'v0.2.1',
        'v0.2.1+dev',
        '0.8.3',
        '1.0',
    ]
