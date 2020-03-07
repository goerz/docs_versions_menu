"""Command line utility for generating versions.json file."""
import json
import logging
import pprint
import re
import subprocess
from pathlib import Path

import click
import jinja2
from packaging.version import LegacyVersion
from packaging.version import parse as parse_version

from .click_config_file import configuration_option
from .folder_spec import resolve_folder_spec


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


def get_groups(folders):
    """Sort the given folder names into groups.

    Returns a dict `groups` with the following group names as keys: and a list
    of folder names for each group as values:

    * 'local-releases': anything that has a "local version part" according to
      PEP440 (e.g. "+dev" suffix)
    * 'dev-releases': any `folders` whose name PEP440 considers a development
      release ("-dev[N]" suffix)
    * 'pre-releases': any `folders` whose name PEP440 considers a pre-release
      but not a development release (suffixes like '-rc1', '-a1', etc.). This
      includes dev-releases.
    * 'post-releases': any `folders` whose name PEP440 recognizes as a
      post-release ("-post[N]" suffix)
    * 'branches': Any folder that PEP400 does not recognize as a release
    * 'releases': Any folder that PEP400 recognizes as a release
    """
    groups = {
        'dev-releases': [],
        'local-releases': [],
        'pre-releases': [],
        'post-releases': [],
        'branches': [],
        'releases': [],
    }
    for folder in folders:
        version = parse_version(folder)
        if isinstance(version, LegacyVersion):
            groups['branches'].append(folder)
        else:
            groups['releases'].append(folder)
            if version.local is not None:
                groups['local-releases'].append(folder)
            if version.is_devrelease:
                groups['dev-releases'].append(folder)
            if version.is_prerelease:
                groups['pre-releases'].append(folder)
            if version.is_postrelease:
                groups['post-releases'].append(folder)
    return groups


def get_version_data(
    *,
    hidden=None,
    sort_key=None,
    suffix_latest,
    suffix_unreleased,
    versions_spec=r'(<branches> != master), <releases>, (<branches> == master)',
    latest_spec=r'(<releases> not in (<local-releases>, <pre-releases>))[-1]',
    warnings=None,
    downloads_file
):
    """Get the versions data, to be serialized to json."""
    if hidden is None:
        hidden = []
    if sort_key is None:
        sort_key = parse_version

    folders = [
        str(f)
        for f in Path().iterdir()
        if (
            f.is_dir()
            and not str(f).startswith('.')
            and not str(f).startswith('_')
            and str(f) not in hidden
        )
    ]
    labels = {f: f for f in folders}
    groups = get_groups(folders)

    try:
        latest_release = resolve_folder_spec(latest_spec, groups)[-1]
        labels[latest_release] += suffix_latest
    except IndexError:
        latest_release = None

    if warnings is None:
        warnings = (
            ('outdated', '(<releases> < ' + str(latest_release) + ')'),
            # spec '(<releases> if < None) is an empty list
            ('unreleased', '<branches>, <local-releases>, <pre-releases>'),
        )

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

    for (warning_lbl, warning_spec) in warnings:
        for folder in version_data['warnings'].keys():
            if folder in resolve_folder_spec(warning_spec, groups):
                version_data['warnings'][folder].append(warning_lbl)

    unreleased = resolve_folder_spec(
        '<branches>, <local-releases>, <pre-releases>', groups
    )
    for folder in unreleased:
        labels[folder] += suffix_unreleased

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
    '--write-index-html/--no-write-index-html',
    default=True,
    help=(
        'Whether to write an index.html that forwards to the latest release. '
        'In the config file, override this as ``write_index_html=False``.'
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
    help='Suffix for the label of the latest stable release.',
    show_default=True,
)
@click.option(
    '--suffix-unreleased',
    default=' (dev)',
    help='Suffix for development branches and pre-releases',
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
    write_index_html,
    ensure_no_jekyll,
    downloads_file,
    suffix_latest,
    suffix_unreleased,
):
    """Generate version json file in OUTFILE.

    Except for debugging, it is recommended to set options through the config
    file (``doctr-versions-menu.conf`` in the current working directory)
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
    version_data = get_version_data(
        downloads_file=downloads_file,
        suffix_latest=suffix_latest,
        suffix_unreleased=suffix_unreleased,
    )
    if write_index_html:
        _write_index_html(version_data=version_data)
    if ensure_no_jekyll:
        _ensure_no_jekyll()
    logger.info("Write versions.json")
    write_versions_json(version_data, outfile=outfile)
    logger.debug("End of doctr-versions-menu")
