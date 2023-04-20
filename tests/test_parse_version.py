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


def test_non_version_folder_name():
    """Test the behavior of NonVersionFolderName inherited from _BaseVersion"""
    v1 = parse_version("branch-a")
    v1_copy = parse_version("branch-a")
    v2 = parse_version("branch-b")
    v3 = parse_version("0.0.1-dev")

    assert repr(v1) == "<NonVersionFolderName('branch-a')>"

    assert repr(v3) == "<VersionFolderName('0.0.1.dev0')>"
    # Note the normalization!

    # __lt__
    assert v1 < v2
    assert v1 < v3
    assert not (v3 < v1)
    # __le__
    assert v1 <= v2
    assert v1 <= v1_copy
    assert not (v3 <= v1)
    # __eq__
    assert v1 == v1_copy
    assert not (v1 == v3)
    assert not (v3 == v1)
    # __ge__
    assert v2 >= v1
    assert v3 >= v1
    assert v1_copy >= v1
    # __gt__
    assert v2 > v1
    assert v3 > v1
    assert not (v1 > v3)
    # __ne__
    assert v1 != v2
    assert v1 != v3
    assert v3 != v1
