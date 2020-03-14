=======
History
=======

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
