"""Test classification of folders into groups."""
from docs_versions_menu.groups import get_groups


def test_get_groups():
    """Test folder classification according to :pep:`440`."""
    folders = [
        'doc-testing',
        'master',
        'testing',
        'v0.1.0',
        'v0.2.0',
        'v1.0.0',
        'v1.0.0+dev',
        'v1.0.0-dev0',
        'v1.0.0-post1',
        'v1.0.0-rc1',
        'v1.1.0-rc1',
    ]
    groups = get_groups(folders)
    assert groups['dev-releases'] == {'v1.0.0-dev0'}
    assert groups['local-releases'] == {'v1.0.0+dev'}
    assert groups['pre-releases'] == {
        'v1.0.0-dev0',
        'v1.0.0-rc1',
        'v1.1.0-rc1',
    }
    assert groups['post-releases'] == {'v1.0.0-post1'}
    assert groups['final-releases'] == {'v0.1.0', 'v0.2.0', 'v1.0.0'}
    assert groups['public-releases'] == {
        'v0.1.0',
        'v0.2.0',
        'v1.0.0',
        'v1.0.0-post1',
    }
    assert groups['branches'] == {'doc-testing', 'master', 'testing'}
    assert groups['releases'] == {
        'v1.1.0-rc1',
        'v0.2.0',
        'v0.1.0',
        'v1.0.0-dev0',
        'v1.0.0-rc1',
        'v1.0.0-post1',
        'v1.0.0',
        'v1.0.0+dev',
    }
    assert groups['all'] == set(folders)
