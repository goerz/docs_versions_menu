"""Test the doctr-versions-menu CLI interface."""
import json
import logging
import platform
import subprocess
import sys
from distutils.dir_util import copy_tree
from pathlib import Path

from click.testing import CliRunner
from pkg_resources import parse_version

import doctr_versions_menu
from doctr_versions_menu.cli import main as doctr_versions_menu_command


def test_version():
    """Test ``doctr-versions-menu --version``."""
    runner = CliRunner()
    result = runner.invoke(doctr_versions_menu_command, ['--version'])
    assert result.exit_code == 0
    normalized_version = str(parse_version(doctr_versions_menu.__version__))
    assert normalized_version in result.output


def test_bad_config():
    """Test ``doctr-versions-menu --config for non-existing config``."""
    runner = CliRunner()
    result = runner.invoke(
        doctr_versions_menu_command, ['--debug', '--config', 'xxx']
    )
    assert result.exit_code != 0
    if sys.platform.startswith('win'):
        # Windows might have slightly different messages
        return
    msg = "Cannot read configuration file: File 'xxx' does not exist"
    if platform.python_version().startswith('3.5'):
        # Python 3.5 hits the IOError earlier, resulting in a different message
        msg = "No such file or directory"
    assert msg in result.stdout


def test_default_run(caplog):
    """Test doctr-versions-menu "default" run."""
    root = Path(__file__).with_suffix('') / 'gh_pages_default'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(doctr_versions_menu_command)
        assert result.exit_code == 0
        assert (cwd / 'index.html').is_file()
        assert (cwd / '.nojekyll').is_file()
        assert (cwd / 'versions.json').is_file()
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert set(versions_data['folders']) == set(
                ['master', 'v0.1.0', 'v1.0.0']
            )
            assert versions_data['versions'] == ['master', 'v1.0.0', 'v0.1.0']
            assert versions_data['labels'] == {
                'master': 'master (dev)',
                'v0.1.0': 'v0.1.0',
                'v1.0.0': 'v1.0.0 (latest release)',
            }
            assert 'v0.1.0' in versions_data['outdated']
            assert versions_data['latest_release'] == 'v1.0.0'
            assert versions_data['downloads']['master'] == [
                ['pdf', '/master/master.pdf'],
                ['zip', '/master/master.zip'],
                ['epub', '/master/master.epub'],
            ]
            assert versions_data['downloads']['v1.0.0'] == [
                ['pdf', 'https://host/v1.0.0/v1.0.0.pdf'],
                ['html', 'https://host/v1.0.0/v1.0.0.zip'],
                ['epub', 'https://host/v1.0.0/v1.0.0.epub'],
            ]


def test_many_releases(caplog):
    """Test doctr-versions-menu run for project with many releases."""
    root = Path(__file__).with_suffix('') / 'gh_pages_many_releases'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(doctr_versions_menu_command)
        assert result.exit_code == 0
        assert (cwd / 'index.html').is_file()
        assert (cwd / '.nojekyll').is_file()
        assert (cwd / 'versions.json').is_file()
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            versions_data['folders'] = set(versions_data['folders'])
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
                'folders': {
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
                },
                'hidden': [],
                'labels': {
                    'doc-testing': 'doc-testing (dev)',
                    'master': 'master (dev)',
                    'testing': 'testing (dev)',
                    'v0.1.0': 'v0.1.0',
                    'v0.2.0': 'v0.2.0',
                    'v1.0.0': 'v1.0.0',
                    'v1.0.0+dev': 'v1.0.0+dev (dev)',
                    'v1.0.0-dev0': 'v1.0.0-dev0',
                    'v1.0.0-post1': 'v1.0.0-post1 (latest release)',
                    'v1.0.0-rc1': 'v1.0.0-rc1',
                    'v1.1.0-rc1': 'v1.1.0-rc1',
                },
                'latest_release': 'v1.0.0-post1',
                'outdated': [
                    'v0.1.0',
                    'v0.2.0',
                    'v1.0.0-dev0',
                    'v1.0.0-rc1',
                    'v1.0.0',
                    'v1.0.0+dev',
                ],
                'unreleased': [
                    'doc-testing',
                    'master',
                    'testing',
                    'v1.0.0+dev',
                ],
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
            }


def test_custom_index_html(caplog):
    """Test using a custom index.html."""
    root = Path(__file__).with_suffix('') / 'gh_pages_custom_index'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(doctr_versions_menu_command)
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
        result = runner.invoke(doctr_versions_menu_command, ['--debug'])
        assert result.exit_code == 0
        assert (cwd / 'versions.json').is_file()
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert set(versions_data['folders']) == set(
                ['master', 'v0.1.0', 'v1.0.0']
            )
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


def test_custom_suffix(caplog):
    """Test using a custom suffixes for latest/dev versions.

    Also tests the the -c / --config flag.
    """
    root = Path(__file__).with_suffix('') / 'gh_pages_custom_suffix'
    runner = CliRunner()
    caplog.set_level(logging.DEBUG)
    with runner.isolated_filesystem():
        cwd = Path.cwd()
        subprocess.run(['git', 'init'], check=True)
        copy_tree(str(root), str(cwd))
        result = runner.invoke(doctr_versions_menu_command, ['-c', 'config'])
        assert result.exit_code == 0
        assert (cwd / 'versions.json').is_file()
        with (cwd / 'versions.json').open() as versions_json:
            versions_data = json.load(versions_json)
            assert versions_data['labels'] == {
                'master': 'master[unreleased]',
                'v0.1.0': 'v0.1.0',
                'v1.0.0': 'v1.0.0 [latest]',
            }
