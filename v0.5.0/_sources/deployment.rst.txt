.. _deployment:

==================
Step 2: Deployment
==================

The Docs-Versions-Menu package includes a ``docs-versions-menu``
executable. This executable should be run in the root of the *deployed*
documentation. That is, the root of the ``gh-pages`` branch when using
`Github Pages`_.

The main purpose of the ``docs-versions-menu`` command is to generate the
``versions.json`` file that the :ref:`Sphinx extension <sphinx_extension>`
relies on, in the root of the deployed documentation.


.. _deployment-with-github-actions:

Deployment with Github Actions
------------------------------

For projects on Github, using `Github Actions`_ to deploy to `Github Pages`_ is
the best-supported option without any external dependencies. Set up your
workflow_ with the following steps:

* Build the documentation by invoking Sphinx directly or in any other way that
  is convenient (``make``, ``tox``, etc.). You may also want to create
  *documentation artifacts*, i.e., a zipped archive of the HTML documentation,
  and PDF or EPUB versions of the documentation. For example, you might use the
  following workflow step:

  .. literalinclude:: ../.github/workflows/docs.yml
     :language: yaml
     :dedent: 6
     :start-after: - uses: actions/checkout@v2
     :end-before: - name: Make a Github release and set _downloads links

* Optionally, create a :ref:`Github release <github_releases>` and attach the
  documentation artifacts to it (:ref:`see below <github_releases>`)

* Deploy the built HTML documentation to ``gh-pages``:

  - Check out the ``gh-pages`` branch and use ``rsync`` to transfer the built html documentation to the appropriate subfolder in ``gh-pages``.
  - Run ``docs-versions-menu`` inside the ``gh-pages`` root
  - Commit and push the changes on the ``gh-pages`` branch

  For example, consider the following workflow step:

  .. literalinclude:: ../.github/workflows/docs.yml
     :language: yaml
     :dedent: 6
     :start-after: GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
     :end-before: - uses: actions/upload-artifact@v2

Note that a Github action is automatically authenticated to upload/download artifacts and to have push-access to the underlying repository.

`See docs-versions-menu's own workflow file <workflow_docs_yaml_>`_ for a full
example from which the above snippets originate.


.. _github_releases:

Github Releases
---------------

The version menu supports showing :ref:`download-links`. For a project using
`Github Actions`_, the easiest solution for hosting the linked files is as
"assets" of a Release_ on Github.

The `Github CLI`_ (``gh``) utility makes it easy to automate creating a release
via a workflow from an annotated git tag. Create an annotated tag with e.g.,

.. code-block:: shell

    git tag --annotate v0.5.0

Or, even better, if you have `gpg signing`_ set up,

.. code-block:: shell

    git tag --sign v0.5.0

Use e.g. "Release 0.5.0" as the subject of the tag message, and the release
notes in markdown format as the body of the tag message. Then push it with

.. code-block:: shell

    git push --tags


Consider the following example snippet from `docs-versions-menu's workflow
<workflow_docs_yaml_>`_ that automates creating a Release_.

.. literalinclude:: ../.github/workflows/docs.yml
   :language: yaml
   :dedent: 6
   :start-after: echo ::set-output name=VERSION::$VERSION
   :end-before: - name: Deploy documentation to gh-pages

This extracts the release notes from the tag message, and attaches local asset
files ``./docs-versions-menu-${{ steps.build.outputs.VERSION }}.*`` (zip, pdf,
epub) that were created earlier in the workflow. It then obtains the public URL
for those assets from the Github API with help from the jq_ utility and writes
them to a ``_downloads`` file that ``docs-versions-menu`` :ref:`will process
later <download-links>`.


Deployment with Travis and Doctr
--------------------------------


When using Travis_ to deploy to `Github Pages`_ via Doctr_, the
``docs-versions-menu`` command should be invoked through
|docs_deploy_command_flag|_.  As the explicit purpose of Docs-Versions-Menu
is to enable documentation for multiple versions of a package at the same time,
you'll likely want to invoke ``doctr deploy`` also with the
|no_require_master_flag|_ and |build_tags_flag|_ options.

.. |docs_deploy_command_flag| replace:: ``doctr deploy``'s ``--command`` flag
.. _docs_deploy_command_flag: https://drdoctr.github.io/commandline.html#cmdoption-doctr-deploy-command

.. |no_require_master_flag| replace:: ``--no-required-master``
.. _no_require_master_flag: https://drdoctr.github.io/commandline.html#cmdoption-doctr-deploy-no-require-master

.. |build_tags_flag| replace:: ``--build-tags``
.. _build_tags_flag: https://drdoctr.github.io/commandline.html#cmdoption-doctr-deploy-build-tags

For example, your ``.travis.yml`` file might include the following
for deploying previously built documentation:

.. code-block:: shell

    if [ ! -z "$TRAVIS_TAG" ]; then DEPLOY_DIR="$TRAVIS_TAG"; else DEPLOY_DIR="$TRAVIS_BRANCH"; fi

    doctr deploy --command=docs-versions-menu --no-require-master --build-tags "$DEPLOY_DIR"

.. note::

    Originally, ``docs-versions-menu`` was named ``doctr-versions-menu`` and
    targeted the above workflow. However, as of 2021, Travis no longer provides
    free services to open source projects and should be avoided.


Deployment to a static webhost
------------------------------

When deploying the documentation not to `Github Pages`_, but directly to a
static webhost, you will likely want to invoke rsync_ in your continuous
integration (e.g., `Github Actions`_ workflow) to upload the documentation to
the appropriate subfolder in the server's webroot. After the call to ``rsync``,
invoke the ``docs-versions-menu`` executable to run in the root of the deployed
documentation, via ``ssh``.


Interactive maintenance
-----------------------

Unless :option:`--no-write-versions-py <docs-versions-menu
--no-write-versions-py>` is given or
``DOCS_VERSIONS_MENU_WRITE_VERSIONS_PY=false`` is set, running
``docs-versions-menu`` will generate a script ``versions.py``. Running this
script again installs the Docs-Versions-Menu package into a temporary virtual
environment and runs ``docs-versions-menu`` with the same options that created
``versions.py`` in the first place.

The intent behind this is to allow for for manual, interactive maintenance, on
the ``gh-pages`` branch or in the server's webroot. For example, you may
occasionally want to remove folders for outdated branches or pre-releases from
the ``gh-pages`` branch, or update existing download links. After any such
change, run the ``versions.py`` script to updates ``versions.json``.

Remember that each folder on the ``gh-pages`` branch generally contains its own
``docs-versions-menu.js`` script. Switching a project to a new major version
of ``docs-versions-menu``, if that version changes the internal data structure of
``versions.json``, may require updating the ``docs-versions-menu.js`` script
in existing folders by hand.

.. _Travis: https://travis-ci.org
.. _Doctr: https://drdoctr.github.io
.. _Github Actions: https://github.com/features/actions
.. _Github Pages: https://pages.github.com
.. _Github CLI: https://cli.github.com
.. _workflow: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions
.. _rsync: https://en.wikipedia.org/wiki/Rsync
.. _Release: https://docs.github.com/en/github/administering-a-repository/releasing-projects-on-github
.. _workflow_docs_yaml: https://github.com/goerz/docs_versions_menu/blob/master/.github/workflows/docs.yml
.. _gpg signing: https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work
.. _jq: https://stedolan.github.io/jq/
