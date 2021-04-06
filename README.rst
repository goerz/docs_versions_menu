==================
Docs-Versions-Menu
==================

.. image:: https://img.shields.io/badge/goerz-docs__versions__menu-blue.svg?logo=github
   :alt: Source code on Github
   :target: https://github.com/goerz/docs_versions_menu

.. image:: https://img.shields.io/badge/docs-gh--pages-blue.svg
   :alt: Documentation
   :target: https://goerz.github.io/docs_versions_menu/

.. image:: https://img.shields.io/pypi/v/docs_versions_menu.svg
   :alt: docs-versions-menu on the Python Package Index
   :target: https://pypi.org/project/docs-versions-menu

.. image:: https://img.shields.io/conda/vn/conda-forge/docs-versions-menu.svg
   :alt: docs-versions-menu on conda-forge
   :target: https://anaconda.org/conda-forge/docs-versions-menu

.. image:: https://github.com/goerz/docs_versions_menu/workflows/Docs/badge.svg?branch=master
   :alt: Docs
   :target: https://github.com/goerz/docs_versions_menu/actions?query=workflow%3ADocs

.. image:: https://github.com/goerz/docs_versions_menu/workflows/PyPI/badge.svg?branch=master
   :alt: PyPI
   :target: https://github.com/goerz/docs_versions_menu/actions?query=workflow%3APyPI

.. image:: https://github.com/goerz/docs_versions_menu/workflows/Tests/badge.svg?branch=master
   :alt: Tests
   :target: https://github.com/goerz/docs_versions_menu/actions?query=workflow%3ATests

.. image:: https://codecov.io/gh/goerz/docs_versions_menu/branch/master/graph/badge.svg
   :alt: Codecov
   :target: https://codecov.io/gh/goerz/docs_versions_menu

.. image:: https://img.shields.io/badge/License-MIT-green.svg
   :alt: MIT License
   :target: https://opensource.org/licenses/MIT

A versions-menu for Sphinx_-based documentation.

Historically, many open source projects have hosted their documentation on `Read the Docs`_ (RTD). However, RTD has a fixed `build process <https://docs.readthedocs.io/en/stable/builds.html>`_ that is essentially limited to just running Sphinx_. Moreover, RTD will inject advertisements into your documentation.

A more flexible approach is to build the documentation with continuous integration (e.g., `Github Actions`_) and to deploy the result to `Github Pages`_ or any other static site hosting. There are no restrictions on the build process: it may involve make_, tox_, latex_, or any number of custom scripts to augment Sphinx_.

The one difficulty that comes with self-hosting project documentation is that out of the box, there is no support for showing multiple releases or branches of the project. This project aims to remedy this. It **provides a Sphinx extension and a command-line tool that work together to generate a dynamic versions-menu similar to that on RTD pages.**

.. image:: https://raw.githubusercontent.com/goerz/docs_versions_menu/master/docs/_static/docs-versions-menu-screenshot.png
  :alt: Docs-Versions-Menu Screenshot

The different "Versions" derive from the folder structure of the hosted documentation, e.g., for `Github Pages`_, the folders in the root of the ``gh-pages`` branch. The ``docs-versions-menu`` command-line tool, running on the ``gh-pages`` branch or on the server hosting the documentation, collects the available versions based on the folders it sees.

The ``docs_versions_menu`` Sphinx extension, running during the Sphinx build process, adds Javascript to the documentation that will inject a menu to switch between the found versions. It can also show warnings for outdated or unreleased versions.

See the Docs-Versions-Menu documentation itself for a `live example <online_>`_.

Development of Docs-Versions-Menu happens on `Github`_.
You can read the full documentation online_.

Installation
------------

To install the latest released version of ``docs-versions-menu``, run:

.. code-block:: shell

    pip install docs-versions-menu

Or, to install the latest development version of ``docs-versions-menu`` from `Github`_:

.. code-block:: shell

    pip install git+https://github.com/goerz/docs_versions_menu.git@master#egg=docs_versions_menu


The ``docs-versions-menu`` package can also be installed through conda_, using
the conda-forge_ channel. See the `instructions in the Docs-Versions-Menu
Feedstock <conda-feedstock-instructions_>`_.

Usage
-----

Showing a versions-menu in your documentation requires two steps:

1.  Add ``'docs_versions_menu'`` to the list of extensions in your Sphinx ``conf.py``.

    This adds Javascript to your rendered documentation that displays a dynamic versions-menu based on information in a ``versions.json`` file it expects to find in the webroot of the hosted documentation, e.g. the root of the ``gh-pages`` branch.


2.  Set up the deployment of the documentation such that it runs the ``docs-versions-menu`` command in the webroot.

    The command creates the file ``versions.json`` that step 1 depends on by analyzing the folders it finds in the webroot.

    How to invoke ``docs-versions-menu`` depends on the specifics of how the documentation is deployed:

    * For `Github Actions`_ deploying to `Github Pages`_, check out the ``gh-pages`` branch, run ``docs-versions-menu``, and commit and push the resulting files.
      See the `workflow file`_ for Docs-Versions-Menu's documentation.

    * For Travis_ deploying to `Github Pages`_ with Doctr_, tell ``doctr deploy`` to invoke the ``docs-versions-menu`` command:

      .. code-block:: shell

          doctr deploy --command=docs-versions-menu --no-require-master --build-tags "$DEPLOY_DIR"

    * For deployments to a static web host, use ``ssh`` to run the ``docs-versions-menu`` command on the server


See the `full documentation <online_>`_ on Step 1 and Step 2 for details.


Default assumptions
-------------------

For projects that follow standard best practices, **you should not require any customization beyond the above two steps**.

* Releases should be tagged as e.g. ``v0.1.0`` and deployed to a folder of the
  same name. That is, a lower case letter ``v`` followed by a :PEP:`440`-compatible
  version identifier.
* The ``master`` branch should be deployed to a folder ``master``, respectively
  ``main`` to a folder ``main`` for projects that `use "main" as the default branch name <https://github.blog/changelog/2020-10-01-the-default-branch-for-newly-created-repositories-is-now-main/>`_.
* Any other branch for which documentation is to be deployed should go in a
  folder matching the branch name.


Examples
--------

The following projects use Docs-Versions-Menu_, respectively `its predecessor Doctr-Versions-Menu <Doctr-Versions-Menu-PyPI_>`_:

* Krotov_
* caproto_
* pcds-ci-helpers_ (an example of shared Travis CI configurations using docs-versions-menu)
* lcls-twincat-general_ (among many other PLC projects at the LCLS)

.. _Docs-Versions-Menu: https://pypi.org/project/docs-versions-menu
.. _Doctr-Versions-Menu-PyPI: https://pypi.org/project/doctr-versions-menu
.. _Github: https://github.com/goerz/docs_versions_menu
.. _Github Actions: https://github.com/features/actions
.. _Github Pages: https://pages.github.com
.. _Sphinx: https://www.sphinx-doc.org/
.. _online: https://goerz.github.io/docs_versions_menu/
.. _Read the Docs: https://readthedocs.org
.. _Travis: https://travis-ci.org
.. _tox: https://tox.readthedocs.io
.. _Doctr: https://drdoctr.github.io
.. _Krotov: https://qucontrol.github.io/krotov/
.. _caproto: https://caproto.github.io/caproto/
.. _pcds-ci-helpers: https://github.com/pcdshub/pcds-ci-helpers/blob/d1bb15ace06cfd8fdda3f5ccad0981fcc59dfbe0/travis/shared_configs/doctr-upload.yml
.. _lcls-twincat-general: https://pcdshub.github.io/lcls-twincat-general/
.. _conda: https://docs.conda.io
.. _conda-forge: https://conda-forge.org
.. _conda-feedstock-instructions: https://github.com/conda-forge/docs-versions-menu-feedstock#installing-docs-versions-menu
.. _make: https://www.gnu.org/software/make/manual/make.html
.. _latex: https://www.latex-project.org
.. _workflow file: https://github.com/goerz/docs_versions_menu/blob/master/.github/workflows/docs.yml
