"""Test folder list specifications."""
import pytest

from doctr_versions_menu.cli import resolve_folder_spec


@pytest.fixture
def groups():
    g = {
        'main-branches': ['master', 'develop'],
        'extra-branches': ['test', 'docs'],
        'pre-releases': ['v0.1.0-rc1', 'v0.1.0-rc2', 'v0.2.0-dev1'],
        'unstable-releases': ['v0.1.0', 'v0.2.1', 'v0.2.0', 'v0.3.0'],
        'stable-releases': ['v1.0.0', 'v1.1.0', 'v1.1.1'],
        'post-releases': ['v1.0.0-post1', 'v1.0.0-post2', 'v1.1.0-post1'],
    }
    g['branches'] = g['main-branches'] + g['extra-branches']
    g['releases'] = (
        g['pre-releases']
        + g['unstable-releases']
        + g['stable-releases']
        + g['post-releases']
    )
    return g


def test_folder_spec(groups):
    """Test :func:`resolve_folder_spec`."""
    # fmt: off
    expected = [
        'v1.1.1', 'v1.1.0-post1', 'v1.1.0', 'v1.0.0-post2', 'v1.0.0-post1',
        'v1.0.0', 'v0.3.0', 'v0.2.1', 'v0.2.0', 'v0.2.0-dev1', 'v0.1.0',
        'v0.1.0-rc2', 'v0.1.0-rc1', 'test', 'master', 'docs', 'develop',
    ]
    # fmt: on
    res = resolve_folder_spec("<branches>, <releases>", groups)
    assert res == expected
    res = resolve_folder_spec("<branches>, <releases>", groups, reverse=True)
    assert res == expected
    res = resolve_folder_spec(
        "(<extra-branches>,<main-branches>), (<pre-releases>,<unstable-releases>,<stable-releases>,<post-releases>)",
        groups,
    )
    assert res == expected

    res1 = resolve_folder_spec("<branches[::-1]>, <releases[::-1]>", groups)
    res2 = resolve_folder_spec("<releases>,<branches>", groups, reverse=False)
    res3 = resolve_folder_spec(
        "(<extra-branches>,<main-branches>[::-1]), (<pre-releases>,<unstable-releases>,<stable-releases>,<post-releases>[::-1])",
        groups,
    )
    assert res1 == res2 == res3

    # fmt: off
    expected = [
        'v1.1.0-post1', 'v1.0.0-post2', 'v1.0.0', 'v0.2.1', 'v0.2.0-dev1',
        'v0.1.0-rc2',
    ]
    # fmt: on
    res = resolve_folder_spec("<releases[1::2]>", groups)
    assert res == expected
    res = resolve_folder_spec("(<releases>[1::2])", groups)
    assert res == expected

    assert resolve_folder_spec("(<releases>[1])", groups) == ['v0.1.0-rc2']
    assert resolve_folder_spec("(<releases>[-1])", groups) == ['v1.1.1']
    assert resolve_folder_spec("(<releases>[-2])", groups) == ['v1.1.0-post1']

    # fmt: off
    expected = [
        'master', 'v1.1.1', 'v1.1.0-post1', 'v1.1.0', 'v1.0.0-post2',
        'v1.0.0-post1', 'v1.0.0', 'v0.3.0', 'v0.2.1', 'v0.2.0', 'v0.2.0-dev1',
        'v0.1.0', 'v0.1.0-rc2', 'v0.1.0-rc1', 'develop', 'test', 'docs'
    ]
    # fmt: on
    res = resolve_folder_spec(
        "<extra-branches>,<main-branches[0]>,<releases>,<main-branches>",
        groups,
    )
    assert res == expected
    res = resolve_folder_spec(
        "<extra-branches>,develop,<releases>,master", groups,
    )
    assert res == expected


def test_custom_group_name(groups):
    """Test use of a non-standard group name in `groups`."""
    groups = groups.copy()
    groups['mygroup'] = ['branch-a', 'branch-b', 'branch-c']
    # fmt: off
    expected = [
        'test', 'master', 'docs', 'develop', 'branch-c', 'branch-b',
        'branch-a',
    ]
    # fmt: on
    res = resolve_folder_spec("(<branches>, <mygroup>)", groups)
    assert res == expected


def test_invalid_spec(groups):
    """Test ValueError for invalid folder specifications."""

    with pytest.raises(ValueError) as exc_info:
        resolve_folder_spec("<branches> <releases>", groups)
    msg = "Invalid specification (marked '*'): '<branches> *<releases>'"
    assert msg == str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        resolve_folder_spec("<invalid>, <releases>", groups)
    msg = "Invalid specification (marked '*'): '<*invalid>, <releases>'"
    assert msg == str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        resolve_folder_spec("(<branches>, <releases>)[1:]", groups)
    msg = "Invalid specification (marked '*'): '(<branches>, <releases>)*[1:]'"
    assert msg == str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        resolve_folder_spec("master, <releases[]>", groups)
    msg = "Invalid specification (marked '*'): 'master*, <releases[]>'"
    assert msg == str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        resolve_folder_spec("master, <releases[a]>", groups)
    msg = "Invalid specification (marked '*'): 'master*, <releases[a]>'"
    assert msg == str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        resolve_folder_spec("master, <releases[1:2:3:4]>", groups)
    msg = "Invalid specification (marked '*'): 'master*, <releases[1:2:3:4]>'"
    assert msg == str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        resolve_folder_spec("[master, <releases>]", groups)
    msg = "Invalid specification (marked '*'): '*[master, <releases>]'"
    assert msg == str(exc_info.value)
