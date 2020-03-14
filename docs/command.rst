==================
Step 2: Deployment
==================


.. _doctr-versions-menu-cli:

``doctr-versions-menu``
-----------------------

The Doctr Versions Menu package includes a ``doctr-versions-menu``
executable. This executable should be invoked when deploying the documentation
on Travis_, through |doctr_deploy_command_flag|_.

As the explicit purpose of the Doctr Versions Menu is to enable documentation
for multiple versions of a package at the same time, you'll likely want to
invoke ``doctr deploy`` also with the |no_require_master_flag|_ and
|build_tags_flag|_ options.

.. |doctr_deploy_command_flag| replace:: ``doctr deploy``'s ``--command`` flag
.. _doctr_deploy_command_flag: https://drdoctr.github.io/commandline.html#cmdoption-doctr-deploy-command

.. |no_require_master_flag| replace:: ``--no-required-master``
.. _no_require_master_flag: https://drdoctr.github.io/commandline.html#cmdoption-doctr-deploy-no-require-master

.. |build_tags_flag| replace:: ``--build-tags``
.. _build_tags_flag: https://drdoctr.github.io/commandline.html#cmdoption-doctr-deploy-build-tags

For example, your ``.travis.yml`` file might include the following
for deploying previously built documentation:

.. code-block:: shell

    if [ ! -z "$TRAVIS_TAG" ]; then DEPLOY_DIR="$TRAVIS_TAG"; else DEPLOY_DIR="$TRAVIS_BRANCH"; fi

    doctr deploy --command=doctr-versions-menu --no-require-master --build-tags "$DEPLOY_DIR"


See the deploy-section of the Doctr Versions Menu's |doctr_build_sh_script|_
(which is sourced from |travis_yml|_) for a more detailed example.

The main purpose of the ``doctr-versions-menu`` command is to generate the
``versions.json`` file that the :ref:`Sphinx extension <sphinx_extension>`
relies on, in the root of the ``gh-pages`` branch.

.. |doctr_build_sh_script| replace:: ``doctr_build.sh`` script
.. _doctr_build_sh_script: https://github.com/goerz/doctr_versions_menu/blob/master/.travis/doctr_build.sh

.. |travis_yml| replace:: ``.travis.yml``
.. _travis_yml: https://github.com/goerz/doctr_versions_menu/blob/master/.travis.yml


Debugging
---------

If the ``doctr-versions-menu`` command behaves unexpectedly, add the ``--debug`` flag as follows:

.. code-block:: shell

    doctr deploy --command="doctr-versions-menu --debug" --no-require-master --build-tags "$DEPLOY_DIR"

Make sure to include the debug output when reporting bugs.


Default assumptions
-------------------

You should not have to customize ``doctr-versions-menu`` provided you stick to the following sensible assumptions:

* Releases should be tagged as e.g. ``v0.1.0`` and deployed to a folder of the
  same name. That is, a lower case letter ``v`` followed by a :PEP:`440`-compatible
  version identifier.
* The ``master`` branch should be deployed to a folder ``master``.
* Any other branch for which documentation is to be deployed should go in a folder matching the branch name.

By default, the ``index.html`` file will forward to the documentation of the
latest public release (excluding pre-releases such as ``v1.0.0-rc1``), or to
``master`` if there have been no releases. There is no support for an RTD-style
"latest"/"stable" folder. This is by design: deep-linking to "latest" documentation
is a bad practice, as such links easily become invalid when a new version is
released.


.. _download-links:

Download links
--------------

By default, ``doctr-versions-menu`` looks for a file ``_downloads`` inside each
folder on the ``gh-pages`` branch. Each line in this file should have the
markdown-like format ``[label]: url``, e.g.

.. code-block:: md

    [html]: https://dl.bintray.com/goerz/doctr_versions_menu/doctr_versions_menu-v0.1.0.zip

These links will be shown in the versions menu in a section "Downloads", using
the label as the link text. See :ref:`doc_artifacts` for further
information on how to build and upload the underlying files.


Customization
-------------

.. _doctr-versions-menu-conf:

``doctr-versions-menu.conf`` configuration file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you do need to customize ``doctr-versions-menu``'s behavior, the recommended
way to do so it to place a configuration file ``doctr-versions-menu.conf`` in
the root of the ``gh-pages`` branch. This configuration file can contain
definitions matching ``doctr-versions-menu``'s :ref:`command-line-options`,
formatted according to `Configobj's unrepr mode`_.

Every long-form flag has a corresponding config file variable, obtained by
replacing hyphens with underscores. For boolean flags, the variable name is
derived from the *first* flag option.

For example, the settings

.. code-block::

    downloads_file = ".downloads"
    ensure_no_jekyll = False

correspond to ``--downloads-file=.downloads`` and ``--ignore-no-jekyll``.

See also the Doctr Versions Menu's own `doctr-versions-menu.conf file`_, which
illustrates some advanced usage.

.. _doctr-versions-menu.conf file: https://github.com/goerz/doctr_versions_menu/blob/gh-pages/doctr-versions-menu.conf


.. _command-line-options:

Command line options
~~~~~~~~~~~~~~~~~~~~


.. click:: doctr_versions_menu.cli:main
   :prog: doctr-versions-menu


Folders included in the menu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, the version menu lists the ``master`` branch first, then any
releases from newest to oldest, and then any non-release branches in
reverse-alphabetical order. Having the "newest" releases appear first matches the
behavior of Read-the-Docs.

The folders that are listed in the versions menu and their order can be
customized via the :option:`--versions` flag (``versions`` in the config file).
This receives a :ref:`folder specification <folderspecs>` as an argument that
specifies the folders to appear in the menu in reverse order (bottom/right to
top/left).

To un-reverse the default order of folders in the menu, so that the newest
versions appear last, you could use the following specification in the config
file::

    versions = '((<branches> != master), <releases>, master)[::-1]'


Labels in the versions menu
~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, the label for each folder that appears in the menu is simply the
name of the folder. The "latest public release", identified by
:option:`--latest` (the latest public release by default), has
" (latest)" appended. This can be customized with the
:option:`--suffix-latest`.

Note that Read-the-Docs uses "(latest)" to refer to the latest development
version (usually ``master``), and labels the latest public release as
"(stable)". You may use ``--suffix-latest=" (stable)"`` to emulate
Read-the-Docs' behavior.

More generally, the :option:`--label` option may be used to define label
templates for specific groups of folders. The :option:`--label` receives two
arguments, a :ref:`folder specification <folderspecs>` for the folders to which
the template should apply, and a Jinja-template-string that should receive the
variable "folder" for rendering. For example,

.. code-block:: shell

    doctr-versions-menu --label '<releases>'  "{{ folder | replace('v', '', 1) }}" --label master '{{ folder }} (latest dev branch)'

drops the initial "v" from the folder name of released versions (``v1.0.0`` →
``1.0.0``) and appends a label " (latest dev branch)" to the label for the
``master`` folder.

In the config file (the recommended way to set custom labels), the above options would be specified as::

    label = '''[
        ('<releases>', "{{ folder | replace('v', '', 1) }}"),
        ('master', '{{ folder }} (latest dev branch)')
    ]'''

Note the triple-quotes required for a multi-line entry.


Custom warning messages
~~~~~~~~~~~~~~~~~~~~~~~

By default, the Doctr Versions Menu plugin injects warnings in the rendered
HTML files, within the following types of folders:

* an 'outdated' warning for ``<releases>`` older than the latest stable release (:option:`--latest`)
* an 'unreleased' warning for ``<branches>`` (anything that is not a :pep:`440`-conforming release) or ``<local-releases>`` (typically not used)
* a 'prereleased' warning for anything considered a pre-release by :pep:`440`, e.g. ``v1.0.0-rc1``

Which folders are included in the above three categories can be modified via the :option:`--warning` option.
This options receives two arguments, a "warning label" string (the above
'outdated', 'unreleased', or 'prereleased'), and a
:ref:`folder specification <folderspecs>` for the
folders to which the warning should apply. An empty specification would disable
the warning, e.g.

.. code-block:: shell

    doctr-versions-menu --warning prereleased ''

to disable the warning message on pre-releases.

It is also possible to define entirely new warning labels using :option:`--warning`. For example,

.. code-block:: shell

    doctr-versions-menu --warning post '<post-releases>'

would define a warning 'post' for all post-releases.

The information about which folders should display which warnings is stored
internally in the resulting ``versions.json`` file, in a dict 'warnings' the
maps folder names to a list of warning labels.

To actually show the warning, the ``doctr-versions-menu.js_t`` template would
have to be modified to pick up on the 'post' label, see the instructions for
the :ref:`sphinx_ext_customization` of the ``doctr_versions_menu`` Sphinx
extension.

In the config file, the above options may be configured as e.g.::

    warning = '''[
        ('post', '<post-releases>'),
        ('prereleased', ''),
    ]'''

The default settings (with the default ``--latest``) correspond to::

    warning = '''[
        ('outdated', '(<releases> < (<public-releases>)[-1])'),
        ('unreleased',  '<branches>, <local-releases>'),
        ('prereleased', '<pre-releases>'),
    ]'''

Note the triple-quotes required for a multi-line entry.


.. _customizing_index_html:

Customizing ``index.html``
~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, ``doctr-versions-menu`` generates an ``index.html`` file in the
root of the ``gh-pages`` branch that redirects to the current "default folder".
This is the folder for the most current stable release (:option:`--latest`), or
``master`` if no stable release exists.

The generated ``index.html`` file can be customized by placing an
``index.html_t`` Jinja_ template into the root of the ``gh-pages`` branch.
This template will be rendered receiving a dict ``version_data`` containing the
data in ``versions.json`` (see the :ref:`versions_json_structure`).

The default template is

.. literalinclude:: ../src/doctr_versions_menu/_template/index.html_t
    :language: html

Alternatively, if you want a completely static ``index.html``, you could also
just add that file by hand and use :option:`--no-write-index-html`
(that is, ``write_index_html=False`` in the :ref:`doctr-versions-menu-conf`).


.. _Configobj's unrepr mode: https://configobj.readthedocs.io/en/latest/configobj.html#unrepr-mode
.. _Jinja: https://jinja.palletsprojects.com/en/2.10.x/
.. _Travis: https://travis-ci.org


Maintenance on ``gh-pages``
---------------------------

Unless :option:`--no-write-index-html` is given, running
``doctr-versions-menu`` will generate a script ``versions.py`` in the root of
the ``gh-pages`` branch that may be used to regenerate the ``versions.json``
file. This script is intended for manual maintenance on the ``gh-pages``
branch, that is, outside of the normal automatic Doctr-deployment through
Travis. For example, you may occasionally want to remove folders for outdated
branches or pre-releases from the ``gh-pages`` branch, or update existing
download links.

After any such change, run the ``versions.py`` script before committing and
pushing the ``gh-pages`` branch.

Remember that each folder on the ``gh-pages`` branch generally contains its own
``doctr-versions-menu.js`` script. Switching a project to a new major version
of ``doctr-versions-menu``, if that version changes the internal data structure of
``versions.json``, may require updating the ``doctr-versions-menu.js`` script
in existing folders by hand.
