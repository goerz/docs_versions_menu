"""Classification of folders into groups according to :pep:`440`."""
from packaging.version import LegacyVersion
from packaging.version import parse as parse_version


def get_groups(folders):
    """Sort the given folder names into groups.

    Returns a dict `groups` with the following group names as keys: and a set
    of folder names for each group as values:

    * 'local-releases': anything that has a "local version part" according to
      PEP440 (e.g. "+dev" suffix)
    * 'dev-releases': any `folders` whose name PEP440 considers a development
      release ("-dev[N]" suffix)
    * 'pre-releases': any `folders` whose name PEP440 considers a pre-release
      (suffixes like '-rc1', '-a1', etc.). This includes dev-releases.
    * 'post-releases': any `folders` whose name PEP440 recognizes as a
      post-release ("-post[N]" suffix)
    * 'final-releases': any `folders` containing only of a release segment (no
      local-, dev-, pre-, or post-releases)
    * 'public-releases': combination of final-releases and post-releases
    * 'branches': Any folder that PEP400 does not recognize as a release
    * 'releases': Any folder that PEP400 recognizes as a release
    * 'all': Set of all folders
    """
    groups = {
        'dev-releases': set(),
        'local-releases': set(),
        'pre-releases': set(),
        'post-releases': set(),
        'final-releases': set(),
        'public-releases': set(),
        'branches': set(),
        'releases': set(),
    }
    for folder in folders:
        version = parse_version(folder)
        if isinstance(version, LegacyVersion):
            groups['branches'].add(folder)
        else:
            groups['releases'].add(folder)
            is_final = True
            if version.local is not None:
                groups['local-releases'].add(folder)
                is_final = False
            if version.is_devrelease:
                groups['dev-releases'].add(folder)
                is_final = False
            if version.is_prerelease:
                groups['pre-releases'].add(folder)
                is_final = False
            if version.is_postrelease:
                groups['post-releases'].add(folder)
                groups['public-releases'].add(folder)
                is_final = False
            if is_final:
                groups['final-releases'].add(folder)
                groups['public-releases'].add(folder)
    groups['all'] = set(folders)
    return groups
