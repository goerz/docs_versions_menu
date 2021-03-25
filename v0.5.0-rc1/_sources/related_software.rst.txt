================
Related software
================

* Sphinx_: Documentation generator. The ``docs-versions-menu`` package works as a Sphinx extension, and is thus inherently tied to Sphinx.
* `Read the Docs`_ (RTD): Widely used documentation hoster. The motivation behind the ``docs-version-menu`` is to provide a versions menu nearly identical to the one injected by RTD. As the versions menu in ``docs-versions-menu`` was reverse-engineered directly from the RTD menu, ``docs-versions-menu`` includes CSS develped by Read the Docs.
* `Read the Docs Sphinx Theme`_: The recommended theme for Sphinx documentation (even when not hosted on http://readthedocs.org). While ``docs-versions-menu`` should work to inject a versions menu into any theme, the original RTD theme best integrates the menu.
* Doctr_: A tool for automatically deploying docs from `Travis CI`_ to `GitHub Pages`_. Originally the ``docs-versions-menu`` package (under its original name ``doctr-versions-menu``) was designed to work in conjunction with Doctr. Since Travis no longer provides free support for open source projects, Doctr has become obsolete in this context.

Alternatives
------------

The following projects attempt to solve the same fundamental problem as Docs-Versions-Menu, adding support for multiple versions to self-hosted documentation.

* `sphinxcontrib-versioning`_: Unmaintained, and `incompatible with the latest version of Sphinx <https://github.com/sphinx-contrib/sphinxcontrib-versioning/issues/77>`_.
* `sphinx-versions`_: Fork of ``sphinxcontrib-versioning``. Also incompatible with the latest version of Sphinx.
* `sphinx-multiversion`_: A package that adds versions support to Sphinx by building the documentation for all tags and branches in each deployment.


Comparison with sphinx-multiversion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As of March 2021, `sphinx-multiversion`_ is the only viable alternative to Docs-Versions-Menu. The fundamental difference is that ``sphinx-multiversion`` operates entirely at the *build* stage: `It builds the documentation for all branches locally, and then deploys the result <https://holzhaus.github.io/sphinx-multiversion/master/faq.html#how-does-it-work>`_. In contrast, Docs-Versions-Menu adds version support primarily at the *deploy* stage: it builds the documentation only for the local branch, and deploys that to a subfolder of the `gh-pages` branch or any other web host. After the deployment, the ``docs-versions-menu`` command line tool must run on the `gh-pages` branch or on the web host to collect the information for the versions menu.

Both approaches have their own merits and should be evaluated for the specific needs of a given project.

Pros of ``sphinx-multiversion``:

* Easy setup: Generating multi-version documentation at the build stage is conceptually simpler than Docs-Version-Menu's approach
* Static: No Javascript is required for showing versions information
* Consistency across versions: the settings from the latest ``conf.py`` are applied to all versions.

Cons of ``sphinx-multiversion``:

* Longer build times: building the documentation means building it for *all* branches.
* No actual version menu by default: `Setting up templates <https://holzhaus.github.io/sphinx-multiversion/master/templates.html>`_ is *required*.
* The sphinx ``conf.py`` on the latest branch must be compatible with the documentation of all branches.

Pros of ``Docs-Versions-Menu``:

* Shorter build times: Only the documentation for the current branch is built.
* Works out of the box: No customization is required for most projects.
* More customization options: At the same time, there are more customization options available to those who need it.
* RTD style menu: The default versions menu is a clone of the excellent design used by Read-the-Docs.

Cons of ``Docs-Versions-Menu``:

* More difficult to set up: Getting the ``docs-versions-menu`` command to run *on the deployed documentation* may require some creativity in the Continuous-Integration configuration.
* Depends on Javascript: In a non-Javascript browser, no versions menu will appear.
* Cannot be tested locally: The versions menu only appears in the deployed, online documentation
* Consistency between versions is not enforced: Breaking changes may require manually tweaking the deployed documentation for old versions


.. _Doctr: https://drdoctr.github.io
.. _Travis CI: https://travis-ci.org
.. _Github Pages: https://pages.github.com
.. _Sphinx: https://www.sphinx-doc.org
.. _Read the Docs: https://github.com/readthedocs/readthedocs.org
.. _Read the Docs Sphinx Theme: https://sphinx-rtd-theme.readthedocs.io/
.. _sphinxcontrib-versioning: https://github.com/sphinx-contrib/sphinxcontrib-versioning
.. _sphinx-versions: https://github.com/Smile-SA/sphinx-versions
.. _sphinx-multiversion: https://github.com/Holzhaus/sphinx-multiversion
