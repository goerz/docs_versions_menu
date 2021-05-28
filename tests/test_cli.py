"""Test the docs-versions-menu CLI interface."""
import json
import logging
import os
import subprocess
import sys
from distutils.dir_util import copy_tree
from pathlib import Path

from click.testing import CliRunner
from pkg_resources import parse_version

import docs_versions_menu
from docs_versions_menu.cli import main as docs_versions_menu_command


def test_version():
    """Test ``docs-versions-menu --version``."""
    runner = CliRunner()
    result = runner.invoke(docs_versions_menu_command, ['--version'])
    assert result.exit_code == 0
    normalized_version = str(parse_version(docs_versions_menu.__version__))
    assert normalized_version in result.output


def get_staged_files():
    """Return output of `git ls-files` as list of Path objects."""
    proc = subprocess.run(
        ['git', 'ls-files'],
        check=True,
        universal_newlines=True,
        stdout=subprocess.PIPE,
    )
    return [Path(file) for file in proc.stdout.split("\n")]


def test_default_run(caplog):
    """Test docs-versions-menu "default" run."""
    root = Path(__file__).with_suffix('') / 'gh_pages_default'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(docs_versions_menu_command)
        assert result.exit_code == 0
        staged = get_staged_files()
        expected_files = [
            'index.html',
            '.nojekyll',
            'versions.json',
            'versions.py',
        ]
        for file in expected_files:
            assert (cwd / file).is_file()
            assert Path(file) in staged
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert versions_data['folders'] == ['main', 'v0.1.0', 'v1.0.0']
            assert versions_data['versions'] == ['main', 'v1.0.0', 'v0.1.0']
            assert versions_data['labels'] == {
                'main': 'main',
                'v0.1.0': 'v0.1.0',
                'v1.0.0': 'v1.0.0 (latest)',
            }
            assert 'outdated' in versions_data['warnings']['v0.1.0']
            assert versions_data['latest'] == 'v1.0.0'
            assert versions_data['downloads']['main'] == [
                ['pdf', '/main/main.pdf'],
                ['zip', '/main/main.zip'],
                ['epub', '/main/main.epub'],
            ]
            assert versions_data['downloads']['v1.0.0'] == [
                ['pdf', 'https://host/v1.0.0/v1.0.0.pdf'],
                ['html', 'https://host/v1.0.0/v1.0.0.zip'],
                ['epub', 'https://host/v1.0.0/v1.0.0.epub'],
            ]
        index_html = (cwd / 'index.html').read_text()
        # fmt: off
        assert '<meta http-equiv="Refresh" content="0; url=v1.0.0" />' in index_html
        assert '<p>Go to the <a href="v1.0.0">default documentation</a>.</p>' in index_html
        # fmt: on


def test_no_git_run(caplog):
    """Test docs-versions-menu "default" run w/o git."""
    root = Path(__file__).with_suffix('') / 'gh_pages_default'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        # WE DO NOT RUN 'git init' HERE, SO WORKING DIR IS NOT A GIT REPO
        copy_tree(str(root), str(cwd))
        result = runner.invoke(docs_versions_menu_command)
        assert result.exit_code == 0
        expected_files = [
            'index.html',
            '.nojekyll',
            'versions.json',
            'versions.py',
        ]
        for file in expected_files:
            assert (cwd / file).is_file()


def test_no_default_branch_run(caplog):
    """Test docs-versions-menu "no_default_branch" run.

    This test the situation where neither main, master, nor any released
    version exists. This will run through with a warning, and render an index
    file that links to the first available folder.
    """
    root = Path(__file__).with_suffix('') / 'gh_pages_no_default_branch'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(docs_versions_menu_command)
        assert result.exit_code == 0
        staged = get_staged_files()
        expected_files = [
            'index.html',
            '.nojekyll',
            'versions.json',
            'versions.py',
        ]
        for file in expected_files:
            assert (cwd / file).is_file()
            assert Path(file) in staged
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert versions_data['folders'] == ['mybranch']
            assert versions_data['versions'] == ['mybranch']
            assert versions_data['labels'] == {
                'mybranch': 'mybranch',
            }
            assert versions_data['latest'] is None
        index_html = (cwd / 'index.html').read_text()
        # fmt: off
        assert '<p>Go to the <a href="mybranch">default documentation</a>.</p>' in index_html
        # fmt: on
    warnings = [
        x.message
        for x in caplog.get_records("call")
        if x.levelno == logging.WARNING
    ]
    assert len(warnings) == 1
    assert "No default branch" in warnings[0]


def test_no_default_branch_release_run(caplog):
    """Test docs-versions-menu "no_default_branch_release" run.

    This test the situation where neither main nor master exists, but there is
    a stable release. This will run through with a warning, the render and
    index file the links to the released version.
    """
    root = (
        Path(__file__).with_suffix('') / 'gh_pages_no_default_branch_release'
    )
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(docs_versions_menu_command)
        assert result.exit_code == 0
        staged = get_staged_files()
        expected_files = [
            'index.html',
            '.nojekyll',
            'versions.json',
            'versions.py',
        ]
        for file in expected_files:
            assert (cwd / file).is_file()
            assert Path(file) in staged
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert versions_data['folders'] == ['mybranch', 'v1.0.0']
            assert versions_data['versions'] == ['v1.0.0', 'mybranch']
            assert versions_data['labels'] == {
                'mybranch': 'mybranch',
                'v1.0.0': 'v1.0.0 (latest)',
            }
            assert versions_data['latest'] == 'v1.0.0'
        index_html = (cwd / 'index.html').read_text()
        # fmt: off
        assert '<p>Go to the <a href="v1.0.0">default documentation</a>.</p>' in index_html
        # fmt: on
    warnings = [
        x.message
        for x in caplog.get_records("call")
        if x.levelno == logging.WARNING
    ]
    assert len(warnings) == 1
    assert "No default branch" in warnings[0]


def test_many_releases(caplog):
    """Test docs-versions-menu run for project with many releases."""
    root = Path(__file__).with_suffix('') / 'gh_pages_many_releases'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(docs_versions_menu_command)
        assert result.exit_code == 0
        assert (cwd / 'index.html').is_file()
        assert (cwd / '.nojekyll').is_file()
        assert (cwd / 'versions.json').is_file()
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert versions_data == {
                'downloads': {
                    'doc-testing': [],
                    'master': [
                        ['pdf', '/master/master.pdf'],
                        ['zip', '/master/master.zip'],
                        ['epub', '/master/master.epub'],
                    ],
                    'testing': [],
                    'v0.1.0': [
                        ['pdf', '/v0.1.0/v0.1.0.pdf'],
                        ['html', '/v0.1.0/v0.1.0.zip'],
                        ['epub', '/v0.1.0/v0.1.0.epub'],
                    ],
                    'v0.2.0': [
                        ['pdf', '/v0.2.0/v0.2.0.pdf'],
                        ['html', '/v0.2.0/v0.2.0.zip'],
                        ['epub', '/v0.2.0/v0.2.0.epub'],
                    ],
                    'v1.0.0': [
                        ['pdf', 'https://host/v1.0.0/v1.0.0.pdf'],
                        ['html', 'https://host/v1.0.0/v1.0.0.zip'],
                        ['epub', 'https://host/v1.0.0/v1.0.0.epub'],
                    ],
                    'v1.0.0+dev': [],
                    'v1.0.0-dev0': [],
                    'v1.0.0-post1': [
                        ['pdf', 'https://host/v1.0.0/v1.0.0.pdf'],
                        ['html', 'https://host/v1.0.0/v1.0.0.zip'],
                        ['epub', 'https://host/v1.0.0/v1.0.0.epub'],
                    ],
                    'v1.0.0-rc1': [],
                    'v1.1.0-rc1': [],
                },
                'folders': [
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
                ],
                'default-branch': 'master',
                'labels': {
                    'doc-testing': 'doc-testing',
                    'master': 'master',
                    'testing': 'testing',
                    'v0.1.0': 'v0.1.0',
                    'v0.2.0': 'v0.2.0',
                    'v1.0.0': 'v1.0.0',
                    'v1.0.0+dev': 'v1.0.0+dev',
                    'v1.0.0-dev0': 'v1.0.0-dev0',
                    'v1.0.0-post1': 'v1.0.0-post1 (latest)',
                    'v1.0.0-rc1': 'v1.0.0-rc1',
                    'v1.1.0-rc1': 'v1.1.0-rc1',
                },
                'latest': 'v1.0.0-post1',
                'versions': [
                    'master',
                    'v1.1.0-rc1',
                    'v1.0.0-post1',
                    'v1.0.0+dev',
                    'v1.0.0',
                    'v1.0.0-rc1',
                    'v1.0.0-dev0',
                    'v0.2.0',
                    'v0.1.0',
                    'testing',
                    'doc-testing',
                ],
                'warnings': {
                    'doc-testing': ['unreleased'],
                    'master': ['unreleased'],
                    'testing': ['unreleased'],
                    'v0.1.0': ['outdated'],
                    'v0.2.0': ['outdated'],
                    'v1.0.0': ['outdated'],
                    'v1.0.0+dev': ['outdated', 'unreleased'],
                    'v1.0.0-dev0': ['outdated', 'prereleased'],
                    'v1.0.0-post1': [],
                    'v1.0.0-rc1': ['outdated', 'prereleased'],
                    'v1.1.0-rc1': ['prereleased'],
                },
            }


def test_no_release(caplog):
    """Test docs-versions-menu for when there is no "latest public release"."""
    root = Path(__file__).with_suffix('') / 'gh_pages_no_release'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(docs_versions_menu_command)
        assert result.exit_code == 0
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert versions_data['latest'] is None
            assert versions_data['warnings'] == {
                'master': ['unreleased'],
                'v1.0.0-rc1': ['prereleased'],
            }
        index_html = (cwd / 'index.html').read_text()
        # fmt: off
        assert '<meta http-equiv="Refresh" content="0; url=master" />' in index_html
        assert '<p>Go to the <a href="master">default documentation</a>.</p>' in index_html
        # fmt: on


def test_custom_index_html(caplog):
    """Test using a custom index.html."""
    root = Path(__file__).with_suffix('') / 'gh_pages_custom_index'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(docs_versions_menu_command)
        assert result.exit_code == 0
        assert (cwd / 'index.html').is_file()
        assert (cwd / '.nojekyll').is_file()
        assert (cwd / 'versions.json').is_file()
        msg = "This is the index.html for the gh_pages_custom_index test."
        assert msg in (cwd / 'index.html').read_text()
    if sys.platform.startswith('win'):
        # Windows might have slightly different messages
        return
    assert 'Using index.html template from index.html_t' in caplog.messages


def test_custom_downloads_file(caplog):
    """Test using a custom downloads_file."""
    root = Path(__file__).with_suffix('') / 'gh_pages_custom_downloads'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(
            docs_versions_menu_command,
            ['--debug', '--downloads-file=downloads.md'],
        )
        assert result.exit_code == 0
        assert (cwd / 'versions.json').is_file()
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert versions_data['folders'] == ['master', 'v0.1.0', 'v1.0.0']
            assert versions_data['downloads']['master'] == [
                ['pdf', '/master/master.pdf'],
                ['zip', '/master/master.zip'],
            ]
            assert versions_data['downloads']['v1.0.0'] == [
                ['pdf', 'https://host/v1.0.0/v1.0.0.pdf'],
                ['html', 'https://host/v1.0.0/v1.0.0.zip'],
                ['epub', 'https://host/v1.0.0/v1.0.0.epub'],
            ]
    if sys.platform.startswith('win'):
        # Windows might have slightly different messages
        return
    assert 'Processing downloads_file master/downloads.md' in caplog.messages
    assert 'INVALID URL: ./master/master.epub' in caplog.messages


def test_no_downloads_file(caplog):
    """Test using ``--no-downloads-file``."""
    root = Path(__file__).with_suffix('') / 'gh_pages_custom_downloads'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(
            docs_versions_menu_command, ['--no-downloads-file', '--debug']
        )
        assert result.exit_code == 0
        assert (cwd / 'versions.json').is_file()
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert versions_data['folders'] == ['master', 'v0.1.0', 'v1.0.0']
            assert versions_data['downloads']['master'] == []
            assert versions_data['downloads']['v1.0.0'] == []
    assert 'Disable download links (downloads_file is None)' in caplog.messages


def test_custom_suffix(caplog):
    """Test using a custom suffixes for latest versions."""
    root = Path(__file__).with_suffix('') / 'gh_pages_custom_suffix'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(
            docs_versions_menu_command,
            ['--suffix-latest= [latest]', '--no-write-versions-py'],
        )
        assert result.exit_code == 0
        assert (cwd / 'versions.json').is_file()
        assert not (cwd / 'versions.py').is_file()
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert versions_data['labels'] == {
                'master': 'master',
                'v0.1.0': 'v0.1.0',
                'v1.0.0': 'v1.0.0 [latest]',
            }


def test_custom_envvars(caplog):
    """Test using environment variables for configuration."""
    root = Path(__file__).with_suffix('') / 'gh_pages_envvars'
    # DOCS_VERSIONS_MENU and DOCTR_VERSIONS_MENU can be mixed
    env = {
        'DOCTR_VERSIONS_MENU_LATEST': 'master',
        'DOCS_VERSIONS_MENU_DEBUG': "true",
        'DOCS_VERSIONS_MENU_VERSIONS': "<branches>, <releases>",
        'DOCS_VERSIONS_MENU_SUFFIX_LATEST': " [latest]",
        'DOCS_VERSIONS_MENU_WRITE_VERSIONS_PY': 'false',
        'DOCS_VERSIONS_MENU_WRITE_INDEX_HTML': 'false',
        'DOCS_VERSIONS_MENU_ENSURE_NO_JEKYLL': 'false',
        'DOCTR_VERSIONS_MENU_DOWNLOADS_FILE': '',
        'DOCTR_VERSIONS_MENU_WARNING': "post: <post-releases>; outdated: (<releases> < 0.2); prereleased:",
        'DOCTR_VERSIONS_MENU_LABEL': "<releases>: {{ folder | replace('v', '', 1) }}; doc-testing: doc; testing: {{ folder }} (latest dev branch)",
    }
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    env_orig = os.environ.copy()
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(docs_versions_menu_command, env=env)
        assert result.exit_code == 0
        assert (cwd / 'versions.json').is_file()
        assert not (cwd / 'versions.py').is_file()
        assert not (cwd / 'index.html').is_file()
        assert not (cwd / '.nojekyll').is_file()
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert versions_data == {
                'downloads': {
                    'doc-testing': [],
                    'master': [],
                    'testing': [],
                    'v0.1.0': [],
                    'v0.2.0': [],
                    'v1.0.0': [],
                    'v1.0.0+dev': [],
                    'v1.0.0-dev0': [],
                    'v1.0.0-post1': [],
                    'v1.0.0-rc1': [],
                    'v1.1.0-rc1': [],
                },
                'folders': [
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
                ],
                'default-branch': 'master',
                'labels': {
                    'v0.1.0': '0.1.0',
                    'v0.2.0': '0.2.0',
                    'v1.0.0-dev0': '1.0.0-dev0',
                    'v1.0.0-rc1': '1.0.0-rc1',
                    'v1.0.0': '1.0.0',
                    'v1.0.0+dev': '1.0.0+dev',
                    'v1.0.0-post1': '1.0.0-post1',
                    'v1.1.0-rc1': '1.1.0-rc1',
                    'doc-testing': 'doc',
                    'master': 'master [latest]',
                    'testing': 'testing (latest dev branch)',
                },
                'latest': 'master',
                'versions': [
                    'v1.1.0-rc1',
                    'v1.0.0-post1',
                    'v1.0.0+dev',
                    'v1.0.0',
                    'v1.0.0-rc1',
                    'v1.0.0-dev0',
                    'v0.2.0',
                    'v0.1.0',
                    'testing',
                    'master',
                    'doc-testing',
                ],
                'warnings': {
                    'doc-testing': ['unreleased'],
                    'master': ['unreleased'],
                    'testing': ['unreleased'],
                    'v0.1.0': ['outdated'],
                    'v0.2.0': [],
                    'v1.0.0': [],
                    'v1.0.0+dev': ['unreleased'],
                    'v1.0.0-dev0': [],
                    'v1.0.0-post1': ['post'],
                    'v1.0.0-rc1': [],
                    'v1.1.0-rc1': [],
                },
            }
    os.environ = env_orig


def test_custom_labels_warnings(caplog):
    """Test custom versions, labels, and warnings."""
    root = Path(__file__).with_suffix('') / 'gh_pages_custom_labels_warnings'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    env = {
        'DOCS_VERSIONS_MENU_SUFFIX_LATEST': " (stable)",
        'DOCS_VERSIONS_MENU_VERSIONS': "((<branches> != master), <releases>, master)[::-1]",
        'DOCS_VERSIONS_MENU_WRITE_VERSIONS_PY': 'false',
        'DOCS_VERSIONS_MENU_WARNING': "post: <post-releases>; outdated: (<releases> < 0.2); prereleased:",
        'DOCS_VERSIONS_MENU_LATEST': 'v1.0.0',
        'DOCS_VERSIONS_MENU_LABEL': "<releases>: {{ folder | replace('v', '', 1) }}; doc-testing: doc; master: {{ folder }} (latest dev branch)",
    }
    expected_versions_data = {
        'downloads': {
            'doc-testing': [],
            'master': [],
            'testing': [],
            'v0.1.0': [],
            'v0.2.0': [],
            'v1.0.0': [],
            'v1.0.0+dev': [],
            'v1.0.0-dev0': [],
            'v1.0.0-post1': [],
            'v1.0.0-rc1': [],
            'v1.1.0-rc1': [],
        },
        'folders': [
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
        ],
        'default-branch': 'master',
        'labels': {
            'doc-testing': 'doc',
            'master': 'master (latest dev branch)',
            'testing': 'testing',
            'v0.1.0': '0.1.0',
            'v0.2.0': '0.2.0',
            'v1.0.0': '1.0.0 (stable)',
            'v1.0.0+dev': '1.0.0+dev',
            'v1.0.0-dev0': '1.0.0-dev0',
            'v1.0.0-post1': '1.0.0-post1',
            'v1.0.0-rc1': '1.0.0-rc1',
            'v1.1.0-rc1': '1.1.0-rc1',
        },
        'latest': 'v1.0.0',
        'versions': [
            'doc-testing',
            'testing',
            'v0.1.0',
            'v0.2.0',
            'v1.0.0-dev0',
            'v1.0.0-rc1',
            'v1.0.0',
            'v1.0.0+dev',
            'v1.0.0-post1',
            'v1.1.0-rc1',
            'master',
        ],
        'warnings': {
            'doc-testing': ['unreleased'],
            'master': ['unreleased'],
            'testing': ['unreleased'],
            'v0.1.0': ['outdated'],
            'v0.2.0': [],
            'v1.0.0': [],
            'v1.0.0+dev': ['unreleased'],
            'v1.0.0-dev0': [],
            'v1.0.0-post1': ['post'],
            'v1.0.0-rc1': [],
            'v1.1.0-rc1': [],
        },
    }
    env_orig = os.environ.copy()
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(
            docs_versions_menu_command, ['--debug'], env=env
        )
        assert result.exit_code == 0
        assert (cwd / 'index.html').is_file()
        assert (cwd / '.nojekyll').is_file()
        assert (cwd / 'versions.json').is_file()
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert versions_data == expected_versions_data
    os.environ = env_orig

    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(
            docs_versions_menu_command,
            [
                '--suffix-latest= (stable)',
                '--versions',
                '((<branches> != master), <releases>, master)[::-1]',
                '--no-write-versions-py',
                '--warning',
                'post',
                '<post-releases>',
                '--warning',
                'outdated',
                '(<releases> < 0.2)',
                '--warning',
                'prereleased',
                '',
                '--latest=v1.0.0',
                '--label',
                '<releases>',
                "{{ folder | replace('v', '', 1) }}",
                '--label',
                'doc-testing',
                'doc',
                '--label',
                'master',
                '{{ folder }} (latest dev branch)',
            ],
        )
        assert result.exit_code == 0
        assert (cwd / 'index.html').is_file()
        assert (cwd / '.nojekyll').is_file()
        assert (cwd / 'versions.json').is_file()
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert versions_data == expected_versions_data
