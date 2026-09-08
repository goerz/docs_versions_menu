"""Command line utility for generating versions.json file."""

import copy
import functools
import json
import logging
import os
import pprint
import re
import subprocess
from collections import OrderedDict
from pathlib import Path

import click
import jinja2

from .url_scheme import UrlVersionScheme
from .version_data import get_version_data

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
    subprocess.run(['git', 'add', outfile], check=False)


def _write_index_html(
    url_version_scheme: UrlVersionScheme, version_data, default_language='en'
):
    """Write index.html files that redirect to the best available version.

    In no-translations mode, writes a single index.html at the root.
    In translations mode, writes:
    - Root index.html -> redirects to default_language/latest_version
    - Per-language index.html -> redirects to that language's best version
    """
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

    match url_version_scheme:
        case UrlVersionScheme.NO_TRANSLATIONS:
            with open("index.html", "w") as out_fh:
                out_fh.write(template.render(dict(version_data=version_data)))
            subprocess.run(['git', 'add', 'index.html'], check=False)

        case UrlVersionScheme.TRANSLATIONS:
            folders: list[str] = version_data['folders']
            available_languages: dict[str, list[str]] = version_data[
                'available-languages'
            ]
            languages = set(
                lang
                for langs in available_languages.values()
                for lang in langs
            )

            # Per-language index.html files
            for lang in sorted(languages):
                folders_in_lang = set(
                    f for f in folders if lang in available_languages[f]
                )
                lang_version_data = copy.deepcopy(version_data)
                lang_version_data["folders"] = [
                    f
                    for f in lang_version_data["folders"]
                    if f in folders_in_lang
                ]
                lang_version_data["versions"] = [
                    v
                    for v in lang_version_data["versions"]
                    if v in folders_in_lang
                ]
                if not lang_version_data["latest"] in folders_in_lang:
                    del lang_version_data["latest"]
                if not lang_version_data["default-branch"] in folders_in_lang:
                    del lang_version_data["default-branch"]

                with open(f"{lang}/index.html", "w") as out_fh:
                    out_fh.write(
                        template.render(dict(version_data=lang_version_data))
                    )
                subprocess.run(
                    ['git', 'add', f"{lang}/index.html"], check=False
                )

            # Main index.html file
            template_file_m = Path("index_translations_main.html_t")
            if template_file_m.is_file():
                logger.debug(
                    "Using index_translations_main.html_t template from %s",
                    template_file_m,
                )
            else:
                template_file_m = (
                    Path(__file__).parent
                    / '_template'
                    / 'index_translations_main.html_t'
                )
                logger.debug(
                    "Using default index_translations_main.html_t template"
                )
            template_m_str = template_file_m.read_text()
            template_m = jinja2.Environment().from_string(template_m_str)

            with open("index.html", "w") as out_fh:
                out_fh.write(
                    template_m.render(dict(version_data=version_data))
                )
            subprocess.run(['git', 'add', 'index.html'], check=False)

        case _:
            raise NotImplementedError()


def _write_versions_py():
    """Write a versions.py script for re-generating versions.json."""
    logger = logging.getLogger(__name__)
    logger.debug("Write versions.py")
    infile = Path(__file__).parent / '_script' / 'versions.py'
    outfile = Path('versions.py')
    docs_env = {
        key: val
        for (key, val) in os.environ.items()
        if key.startswith("DOCS_VERSIONS_MENU_")
    }
    with infile.open() as in_fh, outfile.open('w') as out_fh:
        for line in in_fh:
            if docs_env and line.startswith('DOCS_VERSIONS_ENV_VARS = {}'):
                line = "DOCS_VERSIONS_ENV_VARS = %s\n"
                out_fh.write("DOCS_VERSIONS_ENV_VARS = {\n")
                for key, val in docs_env.items():
                    out_fh.write("    %r: %r,\n" % (key, val))
                out_fh.write("}\n")
            else:
                out_fh.write(line)
    subprocess.run(['git', 'add', 'versions.py'], check=False)


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
        subprocess.run(['git', 'add', str(nojekyll)], check=False)


class _MultipleTuple(click.Tuple):
    def split_envvar_value(self, rv):
        return [
            s.replace(r'\:', ':').replace(r'\;', ';')
            for s in re.split(r'(?<!\\)[:;]\s*', rv)
        ]


class DoctrLegacyCommand(click.Command):
    """Command with pre-processing of legacy environment variables.

    This translates any legacy DOCTR_VERSIONS_MENU_* environment variable into
    the correct corresponding DOCS_VERSIONS_MENU_* variable, and print a
    warning.
    """

    def main(self, *args, **kwargs):
        for name in list(os.environ.keys()):
            if name.startswith('DOCTR_VERSIONS_MENU'):
                fixed_name = name.replace(
                    'DOCTR_VERSIONS_MENU', 'DOCS_VERSIONS_MENU'
                )
                if fixed_name in os.environ:
                    click.echo(
                        "WARNING: ignoring environment variable "
                        "%s in favor of %s" % (name, fixed_name),
                        err=True,
                    )
                else:
                    click.echo(
                        "WARNING: setting environment variable %s from "
                        "deprecated %s" % (fixed_name, name),
                        err=True,
                    )
                    os.environ[fixed_name] = os.environ[name]
        super().main(*args, **kwargs)


@click.command(
    context_settings={"auto_envvar_prefix": "DOCS_VERSIONS_MENU"},
    cls=DoctrLegacyCommand,
)
@click.version_option()
@click.option(
    '--debug', is_flag=True, help='enable debug logging', show_envvar=True
)
@click.option(
    '-o',
    '--outfile',
    default='versions.json',
    help='File to which to write json data',
    metavar='OUTFILE',
    type=click.Path(),
    show_default=True,
    show_envvar=True,
)
@click.option(
    '--url-version-scheme',
    default='no-translations',
    type=click.Choice(['no-translations', 'translations']),
    help=(
        'The URL scheme for versioned documentation. '
        '"no-translations" uses /<version>/<filename>. '
        '"translations" uses /<language>/<version>/<filename> '
        '(Read the Docs style).'
    ),
    show_default=True,
    show_envvar=True,
)
@click.option(
    '--default-branch',
    default='master, main',
    metavar='DEFAULT_BRANCH',
    help=(
        "The name or possible names of the default branch for the project. "
        "If the project has no public releases, the default index.html "
        "should forward to the first available default branch. "
        "Traditionally, most projects have used 'master' as the "
        "default branch. More recently, the name 'main' has become standard."
    ),
    show_default=True,
    show_envvar=True,
)
@click.option(
    '--versions',
    default=r'(<branches> != <default-branch>), <releases>, <default-branch>',
    metavar='SPEC',
    help=(
        "Specification of versions to be included in the menu, from "
        "oldest/lowest priority to newest/highest priority. "
        "The newest/highest priority items will be shown first. "
        "See the online documentation for the SPEC syntax."
    ),
    show_default=True,
    show_envvar=True,
)
@click.option(
    '--latest',
    default=r'(<public-releases>)[-1]',
    metavar='SPEC',
    help=(
        "Specification of which version is considered the "
        '"latest public release". '
        "If it exists, the main index.html should forward to this version, "
        "and warnings e.g. for \"outdated\" versions should link to it. "
        "See the online documentation for the SPEC syntax."
    ),
    show_default=True,
    show_envvar=True,
)
@click.option(
    '--warning',
    type=_MultipleTuple([str, str]),
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
        "If specified via an environment variable, use the form "
        "\"NAME: SPEC; NAME: SPEC; ...\". "
        "Any colons and semi-colons in NAME and SPEC must be escaped "
        "in this case. See the online documentation for details."
    ),
    show_envvar=True,
)
@click.option(
    '--label',
    type=_MultipleTuple([str, str]),
    multiple=True,
    metavar="SPEC LABELTEMPLATE",
    help=(
        "Set a template for labels in the versions menu. "
        "The LABELTEMPLATE applies to all folders matching the given SPEC. "
        "See the online documentation for the syntax of SPEC. "
        "The LABELTEMPLATE is rendered with Jinja, receiving the ``folder`` "
        "name. "
        "See the online documentation for details. "
        "This option may be given multiple times. "
        "If specified via an environment variables, use the form "
        "\"SPEC: LABELTEMPLATE; SPEC: LABELTEMPLATE; ...\". "
        "Any colons and semi-colons in SPEC and LABELTEMPLATE must be escaped "
        "in this case. See the online documentation for details."
    ),
    show_envvar=True,
)
@click.option(
    '--write-index-html/--no-write-index-html',
    default=True,
    help=(
        'Whether to write an index.html that forwards to the latest public '
        'release. In the config file, override this as '
        '``write_index_html=False``.'
    ),
    show_default=True,
    show_envvar=True,
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
    show_envvar=True,
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
    show_envvar=True,
)
@click.option(
    '--downloads-file',
    default='_downloads',
    metavar='FILE',
    help=(
        'The name of the file inside of each folder from which to read the '
        'download links. Each line in the file must be of the form '
        '``[label]: url``. To disable download links, use '
        '``--no-downloads-file`` or set the environment variable to '
        'an empty string.'
    ),
    show_default=True,
    show_envvar=True,
)
@click.option(
    '--no-downloads-file',
    is_flag=True,
    help=(
        'Disable the downloads file. In the config file, use '
        '``downloads_file = False``. Or, using an environment variable, set '
        'DOCS_VERSIONS_MENU_DOWNLOADS_FILE="".'
    ),
)
@click.option(
    '--suffix-latest',
    default=' (latest)',
    help=(
        'Suffix for the label of the latest public release. This is used in '
        'addition to any label set via the --label option'
    ),
    show_default=True,
    show_envvar=True,
)
@click.option(
    '--default-language',
    default='en',
    metavar='LANG',
    help=(
        'The default language code for translations mode. Used by the root '
        'index.html redirect and by the JavaScript menu for fallback when '
        'switching to a version that does not exist in the current language. '
        'Has no effect in no-translations mode.'
    ),
    show_default=True,
    show_envvar=True,
)
def main(
    debug,
    outfile,
    url_version_scheme,
    versions,
    default_branch,
    latest,
    warning,
    label,
    write_index_html,
    write_versions_py,
    ensure_no_jekyll,
    downloads_file,
    no_downloads_file,
    suffix_latest,
    default_language,
):
    """Generate versions json file in OUTFILE.

    This should be run from the root of a ``gh-pages`` branch of a project
    using the Docs Versions Menu.
    """
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)
    if debug:
        logger.setLevel(logging.DEBUG)
    if downloads_file == "_downloads":
        # Work around changes in click 8.1, see
        # https://github.com/pallets/click/issues/2146
        # For backward compatibility, we want a defined but empty environment
        # variable to disable the downloads file, not set it to the default.
        if "DOCS_VERSIONS_MENU_DOWNLOADS_FILE" in os.environ:
            if os.environ["DOCS_VERSIONS_MENU_DOWNLOADS_FILE"] == "":
                downloads_file = None
        elif "DOCTR_VERSIONS_MENU_DOWNLOADS_FILE" in os.environ:
            if os.environ["DOCTR_VERSIONS_MENU_DOWNLOADS_FILE"] == "":
                downloads_file = None
    if no_downloads_file:
        downloads_file = None
    logger.debug("Start of docs-versions-menu")
    logger.debug("arguments = %s", pprint.pformat(locals()))
    logger.debug("cwd: %s", Path.cwd())
    logger.debug("ENV: %s", os.environ)
    logger.debug("Gather versions info")
    if Path('doctr-versions-menu.conf').is_file():
        click.echo(
            "ERROR: Found legacy doctr-versions-menu.conf file. Config file "
            "settings are no longer supported. Use environment variables "
            "instead.",
            err=True,
        )
        raise click.Abort()
    warnings = OrderedDict([(name.lower(), spec) for (name, spec) in warning])
    url_version_scheme = UrlVersionScheme.parse(url_version_scheme)
    version_data = get_version_data(
        url_version_scheme=url_version_scheme,
        downloads_file=(downloads_file or None),  # False (in config) → None
        default_branch_spec=default_branch,
        suffix_latest=suffix_latest,
        versions_spec=versions,
        latest_spec=latest,
        warnings=warnings,
        label_specs=label,
        default_language=default_language,
    )
    if write_index_html:
        _write_index_html(
            url_version_scheme=url_version_scheme,
            version_data=version_data,
            default_language=default_language,
        )
    if write_versions_py:
        _write_versions_py()
    if ensure_no_jekyll:
        _ensure_no_jekyll()
    logger.info("Write versions.json")
    write_versions_json(version_data, outfile=outfile)
    logger.debug("End of docs-versions-menu")
