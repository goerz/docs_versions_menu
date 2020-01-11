"""Command line utility for generating versions.json file."""
import json
import logging
import pprint
import re
import subprocess
from pathlib import Path

import click
import jinja2
from pkg_resources import parse_version
from pkg_resources.extern.packaging.version import LegacyVersion

from .click_config_file import configuration_option


__all__ = []


def write_versions_json(versions_data, outfile, quiet=False):
    """Write the versions data to a json file and add it to the git index.

    This json file will be processed by the javascript that generates the
    version-selector.
    """
    with open(outfile, 'w') as out_fh:
        json.dump(versions_data, out_fh)
    if not quiet:
        print("versions_data =", json.dumps(versions_data, indent=2))
    subprocess.run(['git', 'add', outfile], check=True)


def _is_unreleased(folder):
    """Identify whether `folder` is an unreleased version.

    The following are considered "unreleased":

    * Anything that doesn't look like a proper version according to PEP440.
      Proper versions are e.g. "1.0.0", "v1.0.0", "1.0.0.post1". Specifically,
      any branch names like "master", "develop" are considered unreleased.
    * Anything that PEP440 considers a pre-release, e.g. "1.0.0-dev", "1.0-rc1"
    * Anything that includes a "local version identifier" according to PEP440,
      e.g. "1.0.0+dev"
    """
    version = parse_version(folder)
    if isinstance(version, LegacyVersion):
        return True
    if version.is_prerelease:
        return True
    if version.local is not None:
        return True
    return False


def _find_latest_release(folders):
    try:
        return sorted(folders, key=parse_version)[-1]
    except IndexError:
        return None


def get_versions_data(
    *,
    hidden=None,
    sort_key=None,
    suffix_latest,
    suffix_unreleased,
    downloads_file
):
    """Get the versions data, to be serialized to json."""
    if hidden is None:
        hidden = []
    if sort_key is None:
        sort_key = parse_version
    labels = {}
    folders = sorted(
        [
            str(f)
            for f in Path().iterdir()
            if (
                f.is_dir()
                and not f.is_symlink()
                and not str(f).startswith('.')
                and not str(f).startswith('_')
            )
        ],
        key=sort_key,
    )
    labels = {folder: labels.get(folder, str(folder)) for folder in folders}
    versions = []
    unreleased = []
    for folder in folders:
        if folder not in hidden:
            versions.append(folder)
        if _is_unreleased(folder):
            unreleased.append(folder)
            labels[folder] += suffix_unreleased
    latest_release = _find_latest_release(
        [f for f in versions if f not in unreleased]
    )
    outdated = []
    if latest_release is not None:
        labels[latest_release] += suffix_latest
        outdated = [
            folder
            for folder in versions
            if (folder != latest_release and folder not in unreleased)
        ]
    versions_data = {
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
        # list of folders that should warn & point to latest release
        'outdated': outdated,
        #
        # list of dev-folders that should warn & point to latest release
        'unreleased': unreleased,
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

    return versions_data


def _write_index_html(default_folder):
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
        out_fh.write(template.render(dict(default_folder=default_folder)))
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
    '--default-branch',
    default='master',
    help='The default folder if no stable release is found',
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
        '``default_branch = "develop"`` or ``ensure_no_jekyll = False``. '
        ' [default: doctr-versions-menu.conf]'
    ),
)
def main(
    debug,
    outfile,
    default_branch,
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
    (``--default-branch`` → ``default_branch``).
    """
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)
    if debug:
        logger.setLevel(logging.DEBUG)
    logger.debug("Start of doctr-versions-menu")
    logger.debug("arguments = %s", pprint.pformat(locals()))
    logger.debug("cwd: %s", Path.cwd())
    logger.debug("Gather versions info")
    versions_data = get_versions_data(
        downloads_file=downloads_file,
        suffix_latest=suffix_latest,
        suffix_unreleased=suffix_unreleased,
    )
    default_folder = versions_data['latest_release']
    if default_folder is None:
        default_folder = default_branch
    if write_index_html:
        _write_index_html(default_folder=default_folder)
    if ensure_no_jekyll:
        _ensure_no_jekyll()
    logger.info("Write versions.json")
    write_versions_json(versions_data, outfile=outfile)
    logger.debug("End of doctr-versions-menu")
