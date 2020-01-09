==================
Step 2: Deployment
==================


``doctr-versions-menu``
-----------------------

The ``doctr_versions_menu`` package includes a ``doctr-versions-menu``
executable. This executable should be invoked when deploying the documentation
on Travis_, through |doctr_deploy_command_flag|_.

As the explicit purpose of ``doctr-versions-menu`` is to enable documentation
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

.. code-block:: console

    if [ ! -z "$TRAVIS_TAG" ]; then DEPLOY_DIR="$TRAVIS_TAG"; else DEPLOY_DIR="$TRAVIS_BRANCH"; fi
    doctr deploy --command=doctr-versions-menu --no-require-master --build-tags "$DEPLOY_DIR"


See the deploy-section of the ``doctr_version_menu``'s |doctr_build_sh_script|_
(which is sourced from |travis_yml|_) for a more detailed example.

.. |doctr_build_sh_script| replace:: ``doctr_build.sh`` script
.. _doctr_build_sh_script: https://github.com/goerz/doctr_versions_menu/blob/master/.travis/doctr_build.sh

.. |travis_yml| replace:: ``.travis.yml``
.. _travis_yml: https://github.com/goerz/doctr_versions_menu/blob/master/.travis.yml


Debugging
---------

If the ``doctr-versions-menu`` command behaves unexpectedly, add the ``--debug`` flag as follows:

.. code-block:: console

    doctr deploy --command="doctr-versions-menu --debug" --no-require-master --build-tags "$DEPLOY_DIR"


Default assumptions
-------------------

You should not have to customize ``doctr-versions-menu`` provided you stick to the following sensible assumptions:

* Releases should be tagged as e.g. ``v0.1.0`` and deployed to a folder of the
  same name. That is, a lower case letter ``v`` followed by a :PEP:`440`-compatible
  version identifier.
* The ``master`` branch should be deployed to a folder ``master``.
* Any other branch for which documentation is to be deployed should go in a folder matching the branch name.

By default, the ``index.html`` file will forward to the documentation of the
latest release (excluding pre-releases such as ``v1.0.0-rc1``), or to
``master`` if there have been no releases. There is no support for an RTD-style
"latest"/"stable" folder. This is a good thing: deep-linking to "latest" documentation
is a bad practice, as such links easily become invalid when a new version is
released.


Download links
--------------

By default, ``doctr-versions-menu`` looks for a file ``_downloads`` inside each
folder on the ``gh-pages`` branch. Each line in this file should have the
markdown-like format "[label]: url", e.g.

.. code-block:: markdown

    [html]: https://dl.bintray.com/goerz/doctr_versions_menu/doctr_versions_menu-v0.1.0.zip

These links will be shown in the versions menu in a section "Downloads", using
the label as the link text.


Customization
-------------

.. _doctr-versions-menu-conf:

``doctr-versions-menu.conf`` configuration file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you do need to customize ``doctr-versions-menu``'s behavior, the recommended
way to do so it to place a configuration file ``doctr-versions-menu.conf`` in
the root of the ``gh-pages`` branch. This configuration file may contain
options matching ``doctr-versions-menu``'s :ref:`command-line-options`,
formatted according to `Configobj's unrepr mode`_.

Every long-form flag has a corresponding config file variable, obtained by
replacing hyphens with underscores. For boolean flags, the variable name is
derived from the *first* flag option.

For example, the settings

.. code-block::

    default_branch = "develop"
    ensure_no_jekyll = False

correspond to ``--default-branch=develop`` and ``--ignore-no-jekyll``.




.. _command-line-options:

Command line options
~~~~~~~~~~~~~~~~~~~~


.. click:: doctr_versions_menu.cli:main
   :prog: doctr-versions-menu


.. _Travis: https://travis-ci.org


Customizing ``index.html``
~~~~~~~~~~~~~~~~~~~~~~~~~~

(TODO)

.. _Configobj's unrepr mode: https://configobj.readthedocs.io/en/latest/configobj.html#unrepr-mode
