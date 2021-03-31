#!/usr/bin/env python
"""Automation script for making a release.

Must be run from the root for the repository.

The release proceeds in the following stages:

1. Prepare the release locally.

This involves creating a release branch, bumping the package version,
prompting for release notes, and running thorough tests of the package, the
documentation, and the packaging process.

2. Make a release to test-PyPI.

The release branch is pushed to the remote. Depending on the --use-workflow
flag, the package will be released to test-PyPI, or it is assumed that a
Github workflow will do the release in reaction to the push of the release
branch.

3. Make a release to the regular PyPI.

The release branch is merged into the master/main branch and tagged with an
annotated (preferably signed) tag of the form "v<version>".  Depending on the
--use-workflow flag, the package will be released to PyPI, or it is assumed
that a Github workflow will do the release in reaction to the push of the tag.

4. Bump the version in post-release.

Optionally, commit and push the post-release bump to the remote.

The release process can be easily aborted in stage 1. In stage 2, it is still
possible to abort the release or to modify the release branch, except that it
will not be possible to upload the same release to the test-PyPI. In stage 3,
aborting the release will require history rewriting of the remote master/main
branch, which should only be done in extreme circumstances. Any release to PyPI
cannot be undone.

Note that after a successful release, there will be a single tagged release
commit on the main/master branch, and only that commit will have a non-dev
__version__. Depending on the `--squash` options, the commit will be a squashed
merge of the release branch (where the release branch is deleted), or an
explicit merge commit of the release branch (preserving the release branch).
"""
# Note: Version scheme according to https://www.python.org/dev/peps/pep-0440
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from os.path import join
from subprocess import CalledProcessError, run

import click
from pkg_resources import parse_version


# Project settings ############################################################
MAIN_BRANCH = 'master'

SQUASH = True
USE_WORKFLOW = True
SIGN = True
HISTORY = 'HISTORY.rst'
###############################################################################


RX_VERSION = re.compile(
    r'^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)'
    r'(?P<prepost>\.post\d+|-(dev|a|b|rc)\d+)?'
    r'(?P<devsuffix>[+-]dev)?$'
)


def make_release(
    package_name,
    require_clean=True,
    squash=SQUASH,
    use_workflow=USE_WORKFLOW,
    sign=SIGN,
    check_docs=True,
    run_tests=True,
):
    """Interactively create and publish a new release for the package."""

    # Stage 1: local operations
    click.confirm("Do you want to make a release?", abort=True)
    if require_clean:
        _check_git_clean()
    _check_repo_status()
    new_version = ask_for_release_version(package_name)
    release_branch = "release-%s" % new_version
    _create_release_branch(release_branch)
    _set_version(join('.', 'src', package_name, '__init__.py'), new_version)
    _edit_history(new_version)
    _check_dist()
    _create_release_commit(new_version)
    if check_docs:
        _check_docs()
    if run_tests:
        _run_tests()

    # Stage 2: Push release branch to release to Test-PyPI
    click.confirm(
        "Are you ready to release to Test-PyPI?", default=True, abort=True
    )
    # You can still make fixes to the release branch if there if you find
    # something wrong with the Test-PyPI release, but you won't be able to make
    # another Test-PyPI release.
    _push_release_commit(release_branch)
    if not use_workflow:
        _make_upload(test=True)

    # Stage 3: Merge release branch and tag it to release to PyPI
    click.confirm(
        "Are you ready to release to PyPI? There is no going back!",
        default=True,
        abort=True,
    )
    _merge_release_branch(
        release_branch, new_version, into=MAIN_BRANCH, squash=squash
    )
    _push_release_commit(MAIN_BRANCH)
    _create_and_push_tag(
        tag="v%s" % new_version, version=new_version, sign=sign
    )
    if not use_workflow:
        _make_upload(test=False)

    # Stage 4: Post-release
    next_dev_version = new_version + '+dev'
    _set_version(
        join('.', 'src', package_name, '__init__.py'), next_dev_version
    )
    _create_next_dev_version_commit(next_dev_version)


###############################################################################


class ReleaseError(ValueError):
    pass


def git_cmd(cmd, msg=False):
    """Run a git sub-command and return its (captured) stdout."""
    _git_cmd = ["git"] + cmd
    proc = run(
        _git_cmd,
        stdout=subprocess.PIPE,
        check=True,
        universal_newlines=True,
    )
    out = proc.stdout.rstrip("\n")
    if msg:
        if not isinstance(msg, str):
            msg = " ".join(_git_cmd)
        click.echo("%s: %s" % (msg, out))
    return out


def get_package_name():
    """Find and return the package name from src"""
    for name in os.listdir('src'):
        if 'egg-info' in name:
            continue
        if os.path.isdir(os.path.join('src', name)):
            return name
    raise ReleaseError("Cannot find package name")


def get_pypi_versions(package_name):
    """Return list of versions for the given package on PyPI"""
    url = "https://pypi.python.org/pypi/%s/json" % (package_name,)
    data = json.load(urllib.request.urlopen(urllib.request.Request(url)))
    versions = list(data["releases"].keys())
    versions.sort(key=parse_version)
    return versions


def get_local_versions():
    """Return list of versions based on local tags.

    For every version, there must be a tag "v<version>"
    """
    tags_info = git_cmd(['show-ref', '--tags'])
    tag_names = [line.split("/")[-1] for line in tags_info.splitlines()]
    return [tag[1:] for tag in tag_names if tag.startswith("v")]


def get_version(filename):
    """Extract the package version, as a str."""
    with open(filename) as in_fh:
        for line in in_fh:
            if line.startswith('__version__'):
                return line.split('=')[1].strip()[1:-1]
    raise ReleaseError("Cannot extract version from %s" % filename)


def edit(filename):
    """Open filename in EDITOR."""
    editor = os.getenv('EDITOR', 'vi')
    if click.confirm("Open %s in %s?" % (filename, editor), default=True):
        run([editor, filename])


def _check_repo_status():
    """Check git repo state in respect to remote."""

    current_branch = git_cmd(
        ['rev-parse', '--abbrev-ref', 'HEAD'], msg="Current branch"
    )
    if current_branch != MAIN_BRANCH:
        click.confirm(
            "You are on %r, not on %r. Continue anyway?"
            % (current_branch, MAIN_BRANCH),
            default=False,
            abort=True,
        )
    run(['git', 'fetch'], check=True)
    local_sha = git_cmd(["rev-parse", "@"], msg="Local SHA")
    remote_sha = git_cmd(["rev-parse", "@{u}"], msg="Remote SHA")
    base_sha = git_cmd(["merge-base", "@", "@{u}"], msg="Base SHA")
    if local_sha == remote_sha:
        click.echo("Repo is up to date")
    elif local_sha == base_sha:
        raise ReleaseError("Repository not up to date. You need to pull")
    elif remote_sha == base_sha:
        click.confirm(
            "You have local un-pushed commits. Continue anyway?",
            default=False,
            abort=True,
        )
    else:
        raise ReleaseError("Repository has diverged")


def _check_git_clean():
    """Ensure that a given current working directory is clean."""
    if git_cmd(["diff", "HEAD"]):
        run(['git', 'status'], check=True)
        raise ReleaseError("Repository must be in a clean state")
    untracked_files = git_cmd(
        ["ls-files", "--others", "--exclude-standard"]
    ).splitlines()
    if untracked_files:
        click.echo("WARNING: there are untracked files:")
        for filename in untracked_files:
            click.echo("\t%s" % filename)
        click.confirm("Continue?", default=False, abort=True)


def _create_release_branch(branch):
    """Create a new branch for the release."""
    click.echo("Create %s branch and switch to it" % branch)
    git_cmd(["checkout", "-b", branch])


def _run_tests():
    """Run 'make test'"""
    success = False
    while not success:
        try:
            run(['make', 'test'], check=True)
        except CalledProcessError as exc_info:
            click.echo("Failed tests: %s\n" % exc_info)
            click.echo("Fix the tests and ammend the release commit.")
            click.echo("Then continue.\n")
            click.confirm("Continue?", default=True, abort=True)
        else:
            success = True


def split_version(version, base=True):
    """Split `version` into a tuple

    If `base` is True, only return (<major>, <minor>, <patch>) as a tuple of
    ints, stripping out pre/post/dev release tags. Otherwise, the are included
    as a possible fourth and fifth element in the tuple (as strings)
    """
    version = str(version)
    if not RX_VERSION.match(version):
        raise ValueError("Invalid version: %s" % version)
    if base:
        return tuple(
            [
                int(v)
                for v in str(parse_version(version).base_version).split(".")
            ]
        )
    else:
        m = RX_VERSION.match(version)
        if m:
            res = [
                int(m.group('major')),
                int(m.group('minor')),
                int(m.group('patch')),
            ]
            if m.group('prepost') is not None:
                res.append(m.group('prepost'))
            if m.group('devsuffix') is not None:
                res.append(m.group('devsuffix'))
            return tuple(res)
        else:
            raise ValueError("Invalid version string: %s" % version)


def list_versions(package_name):
    """List previously released versions

    This prints each released version on a new line, and returns the list of
    all released versions (based on PyPI and local tags)
    """
    try:
        pypi_versions = get_pypi_versions(package_name)
    except OSError:
        click.echo("PyPI versions no available")
        pypi_versions = []
    local_versions = get_local_versions()
    normalized_local_versions = set(
        [str(parse_version(v)) for v in local_versions]
    )
    versions = local_versions.copy()
    for version in pypi_versions:
        if version not in normalized_local_versions:
            versions.append(version)
    versions = sorted(versions, key=parse_version)
    for version in versions:
        normalized_version = str(parse_version(version))
        if (
            normalized_version in pypi_versions
            and normalized_version in normalized_local_versions
        ):
            status = 'PyPI/local'
        elif normalized_version in pypi_versions:
            status = 'PyPI only!'
        elif normalized_version in normalized_local_versions:
            status = 'local only!'
        click.echo("%-20s %s" % (version, status))
    return versions


def version_ok(version, dev_version, released_versions=None):
    """Check that `version` is a valid version for an upcoming release

    The `version` must be newer than the `dev_version` (from __version__, which
    should end in '-dev' or '+dev')
    """
    if released_versions is None:
        released_versions = []
    m = RX_VERSION.match(version)
    if m:
        if m.group('devsuffix') is not None:
            click.echo("Version %s contains a development suffix" % version)
            return False
        if version in released_versions:
            click.echo("Version %s is already released" % version)
            return False
        if parse_version(version) > parse_version(dev_version):
            return True
        else:
            click.echo("Version %s not newer than %s" % (version, dev_version))
            return False
    else:
        click.echo("Invalid version: %s" % version)
        return False


def propose_next_version(dev_version):
    """Return the most likely release version based on the current
    __version__"""
    dev_version = str(dev_version)
    if parse_version(dev_version).is_prerelease:
        return parse_version(dev_version).base_version
    else:
        base_version = parse_version(dev_version).base_version
        v = split_version(base_version)
        return "%d.%d.%d" % (v[0], v[1], v[2] + 1)


def ask_for_release_version(package_name):
    """Ask for the version number of the release.

    The version number is checked to be a valid next release
    """
    dev_version = get_version(join('.', 'src', package_name, '__init__.py'))
    proposed_version = propose_next_version(dev_version)
    released_versions = list_versions(package_name)
    new_version = click.prompt(
        "What version would you like to release?", default=proposed_version
    )
    while not version_ok(new_version, dev_version, released_versions):
        new_version = click.prompt(
            "What version would you like to release?", default=proposed_version
        )
    click.confirm("Confirm version %s?" % new_version, abort=True)
    return str(new_version)


def _set_version(filename, version):
    """Set the package version (in main __init__.py)"""
    shutil.copyfile(filename, filename + '.bak')
    click.echo("Modifying %s to set version %s" % (filename, version))
    with open(filename + '.bak') as in_fh, open(filename, 'w') as out_fh:
        found_version_line = False
        for line in in_fh:
            if line.startswith('__version__'):
                found_version_line = True
                line = line.split('=')[0].rstrip() + " = '" + version + "'\n"
            out_fh.write(line)
    if get_version(filename) == version:
        os.remove(filename + ".bak")
    else:
        # roll back
        shutil.copyfile(filename + ".bak", filename)
        msg = "Failed to set version in %s (restored original)" % filename
        if not found_version_line:
            msg += ". Does not contain a line starting with '__version__'."
        raise ReleaseError(msg)


def _edit_history(version):
    """Interactively edit HISTORY"""
    click.echo(
        "Edit %s to add changelog and release date for %s" % (HISTORY, version)
    )
    edit(HISTORY)
    click.confirm("Is %s up to date?" % HISTORY, default=True, abort=True)


def _check_dist():
    """Quietly make dist and check it. This is mainly to ensure that the README
    and HISTORY metadata are well-formed"""
    success = False
    click.echo("Making and verifying dist and metadata...")
    while not success:
        try:
            shutil.rmtree("build", ignore_errors=True)
            shutil.rmtree("dist", ignore_errors=True)
            run(['make', 'dist'], check=True, stdout=subprocess.DEVNULL)
            run(['make', 'dist-check'], check=True)
            return True
        except CalledProcessError as exc_info:
            click.echo("ERROR: %s" % str(exc_info))
            click.echo("Fix the dist manually, then continue.")
            click.confirm("Continue?", default=True, abort=True)
        else:
            success = True


def _check_docs():
    """Verify the documentation (interactively)"""
    click.echo("Making the documentation....")
    run(['make', 'docs'], check=True, stdout=subprocess.DEVNULL)
    click.echo(
        "Check documentation in file://"
        + os.getcwd()
        + "/docs/_build/html/index.html"
    )
    click.confirm(
        "Does the documentation look correct?", default=True, abort=True
    )


def _create_release_commit(version):
    """Commit Release"""
    click.confirm("Make release commit?", default=True, abort=True)
    try:
        run(
            [
                'git',
                'commit',
                '-a',
                '-m',
                "Release %s" % version,
            ],
            check=True,
        )
    except CalledProcessError:
        click.confirm(
            "Try to commit manually! Continue?", default=False, abort=True
        )


def _make_upload(test=True):
    """Upload to PyPI or test.pypi"""
    if test:
        url = 'https://test.pypi.org'
        cmd = ['make', 'test-upload']
    else:
        url = 'https://pypi.org'
        cmd = ['make', 'upload']
    click.confirm(
        "Ready to upload release to %s?" % url, default=True, abort=True
    )
    success = False
    while not success:
        try:
            run(cmd, check=True)
        except CalledProcessError as exc_info:
            click.confirm(
                "Failed to upload: %s. Try again?" % str(exc_info),
                default=True,
                abort=(not test),
            )
            success = False
        else:
            success = True
            click.confirm(
                "Please check release on %s. Continue?" % url,
                default=True,
                abort=True,
            )


def _push_release_commit(branch):
    """Push local commits to origin."""
    click.confirm(
        "Push release commit to %s on origin?" % branch,
        default=True,
        abort=True,
    )
    run(['git', 'push', 'origin', branch], check=True)
    click.confirm(
        "Please check Continuous Integration success. Continue?",
        default=True,
        abort=True,
    )


def _merge_release_branch(branch, version, into=MAIN_BRANCH, squash=True):
    """Merge the given `branch`."""
    click.confirm(
        "Merge %s into %s?" % (branch, into), default=True, abort=True
    )
    try:
        run(['git', 'checkout', into], check=True)
        if squash:
            run(['git', 'merge', '--squash', branch], check=True)
            run(['git', 'commit', "-m", "Release %s" % version], check=True)
        else:
            run(
                [
                    'git',
                    'merge',
                    '--no-ff',
                    "-m",
                    "Release %s" % version,
                    branch,
                ]
            )
        run(['git', 'branch', "--delete", "--force", branch], check=True)
        run(['git', 'push', "origin", "--delete", branch], check=True)
    except CalledProcessError:
        click.echo("Manually merge %s into %s" % (branch, into))
        click.echo(
            "You can add additional commits to %s prior to merging" % branch
        )
        click.echo(
            "* Merge must be A SINGLE COMMIT on %s with commit message "
            "'Release %s' (--squash or --no-ff)" % (into, version)
        )
        click.echo(
            "* Delete the release branch %s locally and on origin" % branch
        )
        click.echo("")
        click.confirm("Continue?", default=False, abort=True)


def _create_and_push_tag(tag, version, sign=SIGN):
    """Create a tag for the release and push it."""
    click.confirm("Create and push tag %s?" % tag, default=True, abort=True)
    try:
        annotate = "--annotate"
        if sign:
            annotate = '--sign'
        cmd = [
            "git",
            "tag",
            annotate,
            "--message",
            "Release %s" % version,
            "--message",
            "# Add release notes in markdown format",
            '--edit',
            tag,
        ]
        run(cmd, check=True)
        run(['git', 'push', '--tags'], check=True)
    except CalledProcessError:
        click.echo(
            "Manually create an annotated/signed tag %s for release %s and "
            "push it to origin" % (tag, version)
        )
        click.echo("")
        click.confirm("Continue?", default=False, abort=True)


def _create_next_dev_version_commit(version):
    """Commit and push a bump to `version`."""
    if click.confirm(
        "Create a commit for new dev-version %s?" % version,
        default=True,
        abort=False,
    ):
        run(
            ['git', 'commit', '-a', '-m', "Bump version to %s" % version],
            check=True,
        )
        if click.confirm("Push to origin?", default=True, abort=False):
            run(['git', 'push', 'origin'], check=True)


###############################################################################


# run tests with `pytest -s scripts/release.py`


def test_list_versions():
    print("")
    versions = list_versions(get_package_name())
    print(versions)
    assert isinstance(versions, list)


def test_split_version():
    # fmt: off
    import pytest
    assert split_version('0.1.0') == (0, 1, 0)
    assert split_version('0.1.0', base=False) == (0, 1, 0)
    assert split_version('0.1.0-dev1', base=True) == (0, 1, 0)
    assert split_version('0.1.0-dev1', base=False) == (0, 1, 0, '-dev1')
    assert split_version('0.1.0.post1', base=True) == (0, 1, 0)
    assert split_version('0.1.0.post1', base=False) == (0, 1, 0, '.post1')
    assert split_version('0.1.0-rc1', base=True) == (0, 1, 0)
    assert split_version('0.1.0-rc1', base=False) == (0, 1, 0, '-rc1')
    assert split_version('0.1.0-rc1-dev', base=True) == (0, 1, 0)
    assert split_version('0.1.0-rc1-dev', base=False) == (0, 1, 0, '-rc1', '-dev')
    assert split_version('0.1.0-rc1+dev', base=True) == (0, 1, 0)
    assert split_version('0.1.0-rc1+dev', base=False) == (0, 1, 0, '-rc1', '+dev')
    assert split_version('0.1.0-dev', base=True) == (0, 1, 0)
    assert split_version('0.1.0-dev', base=False) == (0, 1, 0, '-dev')
    assert split_version('0.1.0+dev', base=True) == (0, 1, 0)
    assert split_version('0.1.0+dev', base=False) == (0, 1, 0, '+dev')
    with pytest.raises(ValueError):
        split_version('0.1.0.rc1')
    with pytest.raises(ValueError):
        split_version('0.1.0rc1')
    with pytest.raises(ValueError):
        split_version('0.1.0.1')
    with pytest.raises(ValueError):
        split_version('0.1')
    with pytest.raises(ValueError):
        split_version('0.1.0+dev1')
    # fmt: on


def test_version_ok():
    assert version_ok('0.1.0', '0.1.0-dev')
    assert version_ok('0.1.0-a1', '0.1.0-dev')
    assert version_ok('0.1.0-b1', '0.1.0-dev')
    assert version_ok('0.1.0-rc1', '0.1.0-dev')
    assert version_ok('0.2.0', '0.1.0+dev')
    assert version_ok('0.2.0-a1', '0.1.0+dev')
    assert version_ok('0.2.0-b1', '0.1.0+dev')
    assert version_ok('0.2.0-rc1', '0.1.0+dev')
    assert version_ok('0.2.0-dev1', '0.1.0+dev')
    assert version_ok('0.1.0.post1', '0.1.0+dev')
    assert version_ok('0.1.0.post1', '0.1.0')
    assert version_ok('0.2.0', '0.1.0')
    assert version_ok('0.2.0', '0.1.0+dev', ['0.1.0', '0.1.0.post1', '0.1.1'])
    print("")
    assert not version_ok('0.0.1-dev', '0.1.0-dev')
    assert not version_ok('0.1.0', '0.1.0')
    assert not version_ok('0.1.0', '0.1.0+dev')
    assert not version_ok('0.1.0+dev', '0.1.0')
    assert not version_ok('0.2.0-dev', '0.1.0+dev')
    assert not version_ok('0.1.0.1', '0.1.0-dev')
    assert not version_ok('0.1.0a1', '0.1.0-dev')
    assert not version_ok('0.1.0b1', '0.1.0-dev')
    assert not version_ok('0.1.0rc1', '0.1.0-dev')
    assert not version_ok('0.1.0dev1', '0.1.0-dev')
    assert not version_ok('0.1.0-post1', '0.1.0+dev')
    assert not version_ok('0.2.0', '0.1.0+dev', ['0.1.0', '0.2.0'])


def test_propose_next_version():
    assert propose_next_version('0.1.0') == '0.1.1'
    assert propose_next_version('0.1.0-dev') == '0.1.0'
    assert propose_next_version('0.1.0-rc1') == '0.1.0'
    assert propose_next_version('0.1.0-rc1+dev') == '0.1.0'
    assert propose_next_version('0.1.0+dev') == '0.1.1'
    assert propose_next_version('0.1.0.post1') == '0.1.1'
    assert propose_next_version('0.1.0.post1+dev') == '0.1.1'


###############################################################################


@click.command(help=__doc__)
@click.help_option('--help', '-h')
@click.option(
    '--squash/--no-squash',
    default=SQUASH,
    show_default=True,
    help="Whether to squash the release branch.",
)
@click.option(
    '--use-workflow/--no-use-workflow',
    default=USE_WORKFLOW,
    show_default=True,
    help="Whether to rely on an external workflow for releasing to PyPI.",
)
@click.option(
    '--sign/--no-sign',
    default=SIGN,
    show_default=True,
    help="Whether to sign the annotated release tag.",
)
@click.option(
    '--require-clean/--no-require-clean',
    default=True,
    show_default=True,
    help="Whether to allow releases from an unclean repo.",
)
@click.option(
    '--check-docs/--no-check-docs',
    default=True,
    show_default=True,
    help="Whether to locally build the documentation for review.",
)
@click.option(
    '--run-tests/--no-run-tests',
    default=True,
    show_default=True,
    help="Whether to run tests locally.",
)
def main(squash, use_workflow, sign, require_clean, check_docs, run_tests):
    try:
        make_release(
            get_package_name(),
            require_clean=require_clean,
            squash=squash,
            use_workflow=use_workflow,
            sign=sign,
            check_docs=check_docs,
            run_tests=run_tests,
        )
    except Exception as exc_info:
        click.echo(str(exc_info))
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
