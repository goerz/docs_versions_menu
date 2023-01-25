# -*- coding: utf-8 -*-
import datetime
import os
import sys
from pathlib import Path

import git

import docs_versions_menu


DOCS = Path(__file__).parent
ROOT = DOCS / '..'

sys.path.insert(0, os.path.abspath('_extensions'))

# -- General configuration -----------------------------------------------------

# Report broken links as warnings
nitpicky = True
nitpick_ignore = [('py:class', 'callable')]

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinxclick',
    'sphinx_copybutton',
    'docs_versions_menu',  # here's some dogfooding!
]


if os.getenv('SPELLCHECK'):
    extensions.append('sphinxcontrib.spelling')
    spelling_show_suggestions = True
    spelling_lang = os.getenv('SPELLCHECK')
    spelling_word_list_filename = 'spelling_wordlist.txt'
    spelling_ignore_pypi_package_names = True

intersphinx_mapping = {
    'python': ('https://docs.python.org/3.10', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

source_suffix = '.rst'
master_doc = 'index'
project = 'Docs Versions Menu'
year = str(datetime.datetime.now().year)
author = 'Michael Goerz'
copyright = '{0}, {1}'.format(year, author)
version = docs_versions_menu.__version__
release = version
git_tag = "v%s" % version
if version.endswith('dev'):
    try:
        last_commit = str(git.Repo(ROOT).head.commit)[:7]
        release = "%s (%s)" % (version, last_commit)
        git_tag = str(git.Repo(ROOT).head.commit)
    except git.exc.InvalidGitRepositoryError:
        git_tag = "master"
numfig = True

pygments_style = 'friendly'
extlinks = {
    'issue': ('https://github.com/goerz/docs_versions_menu/issues/%s', '#'),
    'pr': ('https://github.com/goerz/docs_versions_menu/pull/%s', 'PR #'),
}

# autodoc settings
autoclass_content = 'both'
autodoc_member_order = 'bysource'
autodoc_mock_imports = []  # e.g.: 'numpy', 'scipy', ...


html_last_updated_fmt = '%b %d, %Y'
html_split_index = False
html_sidebars = {'**': ['searchbox.html', 'globaltoc.html', 'sourcelink.html']}
html_short_title = '%s-%s' % (project, version)


# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# -- Options for HTML output ---------------------------------------------------

html_theme = "alabaster"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    'github_user': 'goerz',
    'github_repo': 'docs_versions_menu',
    'github_banner': True,
    'logo_name': True,
    'show_relbars': True,
    'show_related': True,
}

html_sidebars = {
    '**': ['globaltoc.html', 'sidebarhelp.html', 'searchbox.html'],
    'index': [
        'localtocindex.html',
        'globaltocindex.html',
        'sidebarhelp.html',
        'searchbox.html',
    ],
}

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
# html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
# html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = 'favicon.ico'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# JavaScript filenames, relative to html_static_path
html_js_files = []

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
# html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_domain_indices = True

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
# html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None


# -- Options for LaTeX output -------------------------------------------------

# latex_engine = 'lualatex'
latex_elements = {
    'preamble': r'''
\usepackage[titles]{tocloft}
\cftsetpnumwidth {1.25cm}\cftsetrmarg{1.5cm}
\setlength{\cftchapnumwidth}{0.75cm}
\setlength{\cftsecindent}{\cftchapnumwidth}
\setlength{\cftsecnumwidth}{1.25cm}
\usepackage{emptypage}
''',
    'fncychap': r'\usepackage[Bjornstrup]{fncychap}',
    'printindex': r'\footnotesize\raggedright\printindex',
    'babel': '',
}
latex_show_urls = 'no'


def setup(app):
    app.add_object_type(
        'confval',
        'confval',
        objname='configuration value',
        indextemplate='pair: %s; configuration value',
    )


# -- Options for Epub output --------------------------------------------------

epub_show_urls = 'no'

suppress_warnings = ['epub.unknown_project_files']
