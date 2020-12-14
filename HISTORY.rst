=======
History
=======

0.4.0 (2020-12-14)
------------------

* Added: The label in the top left corner of the version menu can now be configured in ``conf.py`` (setting ``menu_title``).
* Added: ``--default-branch`` option, ``<default-branch>`` group for folder specifications, and ``default-branch`` field in ``versions.json`` (`#12`_)
* Changed: The default ``--versions`` now uses ``<default-branch>``, automatically picking up on either "master" or "main" as the default branch (`#12`_)
* Changed: The default template for ``index.html`` now automatically forwards to the default-branch (based on the ``--default-branch`` option, instead of just "master"), or the first available branch if there is no released version (`#12`_)

This release addresses two major compatibility issues:

1. Both `git <GitMainDefaultBranch_>`_ and `Github <GithubMainDefaultBranch_>`_ have recently switched the name of the default branch from "master" to "main". This release adds support for new projects using "main" as their default branch.
2. As of December 2020, Travis CI has `stopped their support for open source <TravisDemiseHN_>`_. Consequently, Doctr_ can no longer be used to deploy documentation at no cost. This release adds rudimentary support for deploying the documenation with `Github Actions`_ instead of Doctr, see `Deployment with Github Actions <https://goerz.github.io/doctr_versions_menu/v0.4.0/command.html#deployment-with-github-actions>`_.


0.3.0 (2020-08-03)
------------------

* Added: ``--no-downloads-file`` option, ``downloads_file = False`` in config. (`#4`_, thanks to `Tyler Pennebaker <@ZryletTC_>`_)
* Fixed: ``versions.py`` on ``gh-pages`` branch was not being committed (`#5`_)
* Fixed: Compatibility with any ``pyparsing`` version ``>= 2.0.2`` (`#8`_, thanks to `Hugo Slepicka <@hhslepicka_>`_)
* Added: The ``doctr-versions-menu`` executable can now be configured through environment variables. This allows to keep configuration on the source branch, in the ``.travis.yml`` file (`#6`_, thanks to `Tyler Pennebaker <@ZryletTC_>`_)
* The Doctr Versions Menu package can now be installed via `conda <conda-feedstock_>`_ (thanks to `Hugo Slepicka <@hhslepicka_>`_)


0.2.0 (2020-03-14)
------------------

* Added: ``--versions`` option for customizing which folders appear in the versions menu and in which order.
* Added: ``--label`` option for customizing the labels appearing the versions menu
* Added: ``--warning`` option for customizing on which folders specific warnings are displayed
* Added: ``--latest`` option for configuring which folder is the "latest stable release"
* Added: Write a script ``versions.py`` to the root of the ``gh-pages`` branch (``--write-versions-py`` option)
* Changed: unreleased and pre-released versions now show different warnings by default
* Changed: ``index.html`` template is now rendered with full ``version_data``
* Changed: development/pre-release versions now longer have the "dev" suffix in the versions menu by default
* Changed: The versions menu now uses the same ordering of versions as Read-the-Docs, by default: the folders are ordered from most current to least current.
* Changed: internal format of ``versions.json``
* Removed: ``--default-branch`` option. This is replaced by the new ``--latest`` option and enhanced template rendering of the ``index.html``
* Removed: ``--suffix-unreleased`` option. This can now be achieved via the ``--label`` option

This is a major release that breaks backwards compatibility.

Specifically, due to the changes in ``versions.json``, when upgrading from older versions, it
may be necessary to replace ``doctr-versions-menu.js`` files in existing
folders in a project's ``gh-pages`` branch.


0.1.0 (2020-01-11)
------------------

* Initial release


.. _GithubMainDefaultBranch: https://github.blog/changelog/2020-10-01-the-default-branch-for-newly-created-repositories-is-now-main/
.. _GitMainDefaultBranch: https://github.blog/2020-07-27-highlights-from-git-2-28/#introducing-init-defaultbranch
.. _TravisDemiseHN: https://news.ycombinator.com/item?id=25338983
.. _Doctr: https://drdoctr.github.io
.. _Github Actions: https://github.com/features/actions
.. _@ZryletTC: https://github.com/ZryletTC
.. _@hhslepicka: https://github.com/hhslepicka
.. _#4: https://github.com/goerz/doctr_versions_menu/issues/4
.. _#5: https://github.com/goerz/doctr_versions_menu/issues/5
.. _#6: https://github.com/goerz/doctr_versions_menu/issues/6
.. _#8: https://github.com/goerz/doctr_versions_menu/issues/8
.. _#12: https://github.com/goerz/doctr_versions_menu/issues/12
.. _conda-feedstock: https://github.com/conda-forge/doctr-versions-menu-feedstock#readme
