.. _options:

===============
Program Options
===============

If you do need to customize ``docs-versions-menu``'s behavior, there are two options:

1. Call the ``docs-versions-menu`` executable with explicit command line options
2. Set ``DOCS_VERSIONS_MENU_*`` environment variables, each variable corresponding to a command line option

The latter option is generally preferred.

.. click:: docs_versions_menu.cli:main
   :prog: docs-versions-menu


.. _download-links:

Download links
--------------

By default, ``docs-versions-menu`` looks for a file ``_downloads`` inside each
folder that appears in the menu. Each line in this file should have the
markdown-like format ``[label]: url``, e.g.

.. code-block:: md

    [html]: https://dl.bintray.com/goerz/docs_versions_menu/docs_versions_menu-v0.1.0.zip

These links will be shown in the versions menu in a section "Downloads", using
the label as the link text.  The name of the file can be changed via the
``DOCS_VERSIONS_MENU_DOWNLOADS_FILE`` environment variable (see
:option:`--downloads-file`).

See :ref:`github_releases` for an example workflow of creating a suitable
``_downloads`` file from an annotated git tag.

If the ``_downloads`` file is missing, you will see a warning message during
the deploy. To disable use of a ``_downloads`` file (ignore existing files, and
don't warn for missing files), set ``DOCS_VERSIONS_MENU_DOWNLOADS_FILE`` to an
empty string (see :option:`--no-downloads-file`).


Debugging
---------

If the ``docs-versions-menu`` command behaves unexpectedly, set the environment variable

.. code-block:: shell

    DOCS_VERSIONS_MENU_DEBUG=true

or use the :option:`--debug` option.

Make sure to include the debug output when reporting bugs.


Folders
-------

The entries in the versions menu are based on the folders that are present in
the deployed documentation root. We assume here that the folder names
correspond to branch or tag names in the project repository. This is
irrespective of the *label* that appears for given foler in the menu, see
:ref:`below <labels-in-the-versions-menu>`.

By default, the versions menu lists the folder for the default branch (``main``
or ``master``, see :option:`--default-branch`) first, then any releases from
newest to oldest, and then any non-release branches in reverse-alphabetical
order. Having the "newest" releases appear first matches the behavior of
Read-the-Docs.

The folders that are listed in the versions menu and their order can be
customized via the :option:`--versions` flag (``DOCS_VERSIONS_MENU_VERSIONS``
environment variable).
This receives a :ref:`folder specification <folderspecs>` as an argument that
specifies the folders to appear in the menu in reverse order (bottom/right to
top/left).

To un-reverse the default order of folders in the menu, so that the newest
versions and the default branch appear last, you would set

.. code-block:: yaml

    DOCS_VERSIONS_MENU_VERSIONS: '((<branches> not in <default-branch>), <releases>, <default-branch>)[::-1]'

in the definitions of environment variables.


.. _labels-in-the-versions-menu:

Menu labels
-----------

By default, the label for each folder that appears in the menu is simply the
name of the folder. The "latest public release", identified by
:option:`--latest` (the latest public release by default), has
"(latest)" appended. This can be customized with
:option:`--suffix-latest` (``DOCS_VERSIONS_MENU_SUFFIX_LATEST`` environment
variable).

More generally, the :option:`--label` option may be used to define label
templates for specific groups of folders. The option can be given multiple
times. Each :option:`--label` receives two arguments, a :ref:`folder
specification <folderspecs>` for the folders to which the template should
apply, and a Jinja-template-string that should receive the variable ``folder``
for rendering. For example,

.. code-block:: shell

    docs-versions-menu --label '<releases>'  "{{ folder | replace('v', '', 1) }}" --label master '{{ folder }} (latest dev branch)'

drops the initial ``v`` from the folder name of released versions (``v1.0.0`` →
``1.0.0``) and appends a label " (latest dev branch)" to the label for the
``master`` folder.

When specifying the labels via the ``DOCS_VERSIONS_MENU_LABEL`` environment
variable, the multiple ``--label`` options are combined into a single value,
separated by semicolons, and the two arguments separated by a colon. For the
above example, an appropriate definition in a `Github Actions`_ workflow_ would
be

.. code-block:: yaml

    DOCS_VERSIONS_MENU_LABEL: '<releases>: {{ folder | replace("v", "", 1) }}; master: {{ folder }} (latest dev branch)'

.. note::
    Read-the-Docs uses "latest" to refer to the latest development
    version (usually ``main``/``master``) instead of the latest public release,
    and instead labels the latest public release as "stable". You may adopt
    Read-the-Docs nomeclature with e.g.

    .. code-block:: shell

        --suffix-latest=" (stable)" --label master 'master (latest)'

    or

    .. code-block:: shell

        --suffix-latest=" (stable)" --label master latest


Custom warning messages
-----------------------

By default, the ``docs_versions_menu`` extension injects warnings in the
rendered HTML files, within the following types of folders:

* an 'outdated' warning for ``<releases>`` older than the latest public release (identified by :option:`--latest`)
* an 'unreleased' warning for ``<branches>`` (anything that is not a :pep:`440`-conforming release), or ``<local-releases>`` (typically not used)
* a 'prereleased' warning for anything considered a pre-release by :pep:`440`, e.g. ``v1.0.0-rc1``

Which folders are included in the above three categories can be modified via the :option:`--warning` option.
This options receives two arguments, a "warning label" string (the above
'outdated', 'unreleased', or 'prereleased'), and a
:ref:`folder specification <folderspecs>` for the
folders to which the warning should apply. The option can be given multiple
times. An empty specification would disable the warning, e.g.

.. code-block:: shell

    docs-versions-menu --warning prereleased ''

to disable the warning message on pre-releases.

It is also possible to define entirely new warning labels using :option:`--warning`. For example,

.. code-block:: shell

    docs-versions-menu --warning post '<post-releases>'

would define a warning 'post' for all post-releases.

The information about which folders should display which warnings is stored
internally in the resulting ``versions.json`` file, in a dict 'warnings' that
maps folder names to a list of warning labels.

To actually show this new custom warning, the :ref:`docs-versions-menu.js
template <customizing_docs_versions_menu_js>` would have to be modified to pick
up on the 'post' label.

Similarly to :ref:`labels-in-the-versions-menu`, when configuring the warnings
via the ``DOCS_VERSIONS_MENU_WARNING`` environment variable, multiple
:option:`--warning` options are combined into a single value, separated by
semicolons, and the warning label and folder specification separated by a
colon.

For the above two options, you might include the following the definition of
the environment variables in a `Github Actions`_ workflow_:

.. code-block:: yaml

    DOCS_VERSIONS_MENU_WARNING: 'post: <post-relases>; prereleased:'

.. _Github Actions: https://github.com/features/actions
.. _Github Pages: https://pages.github.com
.. _workflow: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions
