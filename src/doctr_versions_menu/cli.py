"""Command line utility for generating versions.json file."""
import json
import logging
import pprint
import re
import shutil
import subprocess
from collections import OrderedDict
from pathlib import Path

import click
import jinja2
from packaging.version import parse as parse_version

from .click_config_file import configuration_option
from .folder_spec import resolve_folder_spec
from .groups import get_groups


__all__ = []


def write_versions_json(version_data, outfile, quiet=False):
    """Write the versions data to a json file and add it to the git index.

    This json file will be processed by the javascript that generates the
    version-selector.
    """
    with open(outfile, 'w') as out_fh:
        json.dump(version_data, out_fh)
    if not quiet:
        print("version_data =", json.dumps(version_data, indent=2))
    subprocess.run(['git', 'add', outfile], check=True)


def get_version_data(
    *,
    hidden=None,
    sort_key=None,
    suffix_latest,
    versions_spec,
    latest_spec,
    warnings,
    label_specs,
    downloads_file
):
    """Get the versions data, to be serialized to json."""
    if hidden is None:
        hidden = []
    if sort_key is None:
        sort_key = parse_version

    folders = sorted(
        [
            str(f)
            for f in Path().iterdir()
            if (
                f.is_dir()
                and not str(f).startswith('.')
                and not str(f).startswith('_')
                and str(f) not in hidden
            )
        ]
    )

    groups = get_groups(folders)

    labels = {}
    for (spec, template_str) in label_specs:
        label_folders = resolve_folder_spec(spec, groups)
        for folder in label_folders:
            label_template = jinja2.Environment().from_string(template_str)
            labels[folder] = label_template.render(folder=folder)
    for folder in folders:
        if folder not in labels:
            labels[folder] = folder

    try:
        latest_release = resolve_folder_spec(latest_spec, groups)[-1]
        labels[latest_release] += suffix_latest
    except IndexError:
        latest_release = None

    if 'outdated' not in warnings:
        warnings['outdated'] = '(<releases> < ' + str(latest_release) + ')'
        # spec '(<releases> < None) is an empty list
    if 'unreleased' not in warnings:
        warnings['unreleased'] = '<branches>, <local-releases>'
    if 'prereleased' not in warnings:
        warnings['prereleased'] = '<pre-releases>'
    versions = resolve_folder_spec(versions_spec, groups)
    versions = list(reversed(versions))  # newest first
    version_data = {
        # list of *all* folders
        'folders': folders,
        #
        # folder => labels for every folder in "Versions"
        'labels': labels,
        #
        # list folders that appear in "Versions"
        'versions': versions,
        #
        # list of folders that do not appear in "Versions"
        'hidden': hidden,
        #
        # map of folders to warning labels
        'warnings': {f: [] for f in folders},
        #
        # the latest stable release folder
        'latest_release': latest_release,
        #
        # folder => list of (label, file)
        'downloads': {
            folder: _find_downloads(folder, downloads_file)
            for folder in folders
        },
    }

    for (name, warning_spec) in warnings.items():
        warning_folders = resolve_folder_spec(warning_spec, groups)
        for folder in version_data['warnings'].keys():
            if folder in warning_folders:
                version_data['warnings'][folder].append(name)

    return version_data


def _write_index_html(version_data):
    """Write an index.html that redirects to `default_folder`."""
    logger = logging.getLogger(__name__)
    logger.debug("Write index.html")
    template_file = Path("index.html_t")
    if template_file.is_file():
        logger.debug("Using index.html template from %s", template_file)
    else:
        template_file = Path(__file__).parent / '_template' / 'index.html_t'
        logger.debug("Using default index.html template")
    template_str = template_file.read_text()
    template = jinja2.Environment().from_string(template_str)
    with open("index.html", "w") as out_fh:
        out_fh.write(template.render(dict(version_data=version_data)))
    subprocess.run(['git', 'add', 'index.html'], check=True)


def _write_versions_py():
    """Write a versions.py script for re-generating versions.json."""
    logger = logging.getLogger(__name__)
    logger.debug("Write versions.py")
    shutil.copy(
        str(Path(__file__).parent / '_script' / 'versions.py'), 'versions.py'
    )


def _ensure_no_jekyll():
    """Create a .nojekyll file.

    This prevents Github from messing with folders that start with an
    underscore.
    """
    logger = logging.getLogger(__name__)
    nojekyll = Path('.nojekyll')
    if nojekyll.is_file():
        logger.debug("%s exists", nojekyll)
    else:
        logger.debug("creating %s", nojekyll)
        nojekyll.touch()
        subprocess.run(['git', 'add', str(nojekyll)], check=True)


def _find_downloads(folder, downloads_file):
    """Find artifact links in downloads_file file.

    The `downloads_file` should be created during the build procedure (on
    Travis).  If no `downloads_file` exists, return an empty list.

    Each line in the `downloads_file` should have the form ``[label]: url``.
    For backwards compatibility, having only the url is also acceptable. In
    this case, the label is derived from the file extension.
    """
    logger = logging.getLogger(__name__)
    downloads = []
    rx_line = re.compile(r'^\[(?P<label>.*)\]:\s*(?P<url>.*)$')
    rx_url = re.compile(r'^(\w+:/)?/')  # /... or http://...
    try:
        downloads_file = Path(folder) / downloads_file
        with downloads_file.open() as in_fh:
            logger.debug("Processing downloads_file %s", downloads_file)
            for line in in_fh:
                match = rx_line.match(line)
                if match:
                    url = match.group('url')
                    label = match.group('label')
                else:
                    logger.warning(
                        "Invalid line %r in %s: does not match '[label]: url'",
                        line.strip(),
                        downloads_file,
                    )
                    url = line.strip()
                    label = url.split(".")[-1].lower()
                if not rx_url.match(url):
                    logger.error("INVALID URL: %s", url)
                    logger.warning(
                        "Skipping invalid URL %r (must be absolute path or "
                        "external URL)",
                        url,
                    )
                    continue
                logger.debug(
                    "For %s, download link %r => %r", folder, label, url
                )
                downloads.append((label, url))
    except IOError:
        logger.warning("folder '%s' contains no %s", folder, downloads_file)
    return downloads


@click.command()
@click.version_option()
@click.option('--debug', is_flag=True, help='enable debug logging')
@click.option(
    '-o',
    '--outfile',
    default='versions.json',
    help='File to which to write json data',
    metavar='OUTFILE',
    type=click.Path(),
    show_default=True,
)
@click.option(
    '--versions',
    default=r'(<branches> != master), <releases>, master',
    metavar='SPEC',
    help=(
        "Specification of versions to be included in the menu, from "
        "oldest/lowest priority to newest/highest priority. "
        "The newest/highest priority items will be shown first. "
        "See the online documentation for the SPEC syntax."
    ),
    show_default=True,
)
@click.option(
    '--latest',
    default=r'(<public-releases>)[-1]',
    metavar='SPEC',
    help=(
        "Specification of which version is considered the "
        '"latest stable release". '
        "If it exists, the main index.html should forward to this version, "
        "and warnings e.g. for \"outdated\" versions should link to it. "
        "See the online documentation for the SPEC syntax."
    ),
    show_default=True,
)
@click.option(
    '--warning',
    type=(str, str),
    multiple=True,
    metavar="NAME SPEC",
    help=(
        "Define a warning. The NAME is a lowercase label that will appear "
        "in the warnings data in versions.json and maybe be picked up by "
        "the javascript rendering warning in the HTML output. The SPEC is "
        "a folder specification for all folders that should show the "
        "warning. See the online documentation for the syntax of SPEC. "
        "The SPEC should give given as a quoted string. "
        "This option may be given multiple times."
    ),
)
@click.option(
    '--label',
    type=(str, str),
    multiple=True,
    metavar="SPEC LABELTEMPLATE",
    help=(
        "Set a template for labels in the versions menu. "
        "The LABELTEMPLATE applies to all folders matching the given SPEC. "
        "See the online documentation for the syntax of SPEC. "
        "The LABELTEMPLATE is rendered with Jinja, receiving the 'folder' "
        "name. "
        "See the online documentation for details. "
        "This option may be given multiple times."
    ),
)
@click.option(
    '--write-index-html/--no-write-index-html',
    default=True,
    help=(
        'Whether to write an index.html that forwards to the latest release. '
        'In the config file, override this as ``write_index_html=False``.'
    ),
    show_default=True,
)
@click.option(
    '--write-versions-py/--no-write-versions-py',
    default=True,
    help=(
        'Whether to write a script versions.py to the root of the gh-pages '
        'branch for regenerating versions.json. This is useful for '
        'maintenance on the gh-pages branch, e.g., removing outdated version.'
    ),
    show_default=True,
)
@click.option(
    '--ensure-no-jekyll/--ignore-no-jekyll',
    default=True,
    help=(
        'Whether to check that a .nojekyll file exist and create it '
        'otherwise. In the config file, override this as '
        '``ensure_no_jekyll=False``.'
    ),
    show_default=True,
)
@click.option(
    '--downloads-file',
    default='_downloads',
    help=(
        'The name of the file inside of each folder from which to read the '
        'download links. Each line in the file must be of the form '
        '"[label]: url".'
    ),
    show_default=True,
)
@click.option(
    '--suffix-latest',
    default=' (latest release)',
    help=(
        'Suffix for the label of the latest stable release. This is used in '
        'addition to any label set via the --label option'
    ),
    show_default=True,
)
@configuration_option(
    cmd_name='doctr-versions-menu',
    config_file_name='doctr-versions-menu.conf',
    implicit=True,
    help=(
        'Read configuration from FILE. Each line in FILE should be of the '
        'form "variable = value" in Python syntax, with variable names '
        'corresponding to any long-form command line flag, e.g. '
        '``ensure_no_jekyll = False``. '
        ' [default: doctr-versions-menu.conf]'
    ),
)
def main(
    debug,
    outfile,
    versions,
    latest,
    warning,
    label,
    write_index_html,
    write_versions_py,
    ensure_no_jekyll,
    downloads_file,
    suffix_latest,
):
    """Generate versions json file in OUTFILE.

    This should be run from the root of a ``gh-pages`` branch of a project
    using the Doctr Versions Menu.

    Except for debugging, it is recommended to set options through the config
    file (``doctr-versions-menu.conf`` in the ``gh-pages`` root)
    instead of via command line flags. Every long-form-flag has a corresponding
    config file variable, obtained by replacing hyphens with underscores
    (``--write-index-html`` → ``write_index_html``).
    """
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)
    if debug:
        logger.setLevel(logging.DEBUG)
    logger.debug("Start of doctr-versions-menu")
    logger.debug("arguments = %s", pprint.pformat(locals()))
    logger.debug("cwd: %s", Path.cwd())
    logger.debug("Gather versions info")
    warnings = OrderedDict([(name.lower(), spec) for (name, spec) in warning])
    version_data = get_version_data(
        downloads_file=downloads_file,
        suffix_latest=suffix_latest,
        versions_spec=versions,
        latest_spec=latest,
        warnings=warnings,
        label_specs=label,
    )
    if write_index_html:
        _write_index_html(version_data=version_data)
    if write_versions_py:
        _write_versions_py()
    if ensure_no_jekyll:
        _ensure_no_jekyll()
    logger.info("Write versions.json")
    write_versions_json(version_data, outfile=outfile)
    logger.debug("End of doctr-versions-menu")
