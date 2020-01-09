===================
Doctr Versions Menu
===================

.. image:: https://img.shields.io/badge/github-goerz/doctr__versions__menu-blue.svg
   :alt: Source code on Github
   :target: https://github.com/goerz/doctr_versions_menu

.. image:: https://img.shields.io/badge/docs-doctr-blue.svg
   :alt: Documentation
   :target: https://goerz.github.io/doctr_versions_menu/

.. image:: https://img.shields.io/pypi/v/doctr_versions_menu.svg
   :alt: doctr-versions-menu on the Python Package Index
   :target: https://pypi.python.org/pypi/doctr_versions_menu

.. image:: https://img.shields.io/travis/goerz/doctr_versions_menu.svg
   :alt: Travis Continuous Integration
   :target: https://travis-ci.org/goerz/doctr_versions_menu

.. image:: https://ci.appveyor.com/api/projects/status/tg95oketoqa94alp/branch/master?svg=true
   :alt: AppVeyor Continuous Integration
   :target: https://ci.appveyor.com/project/goerz/doctr-versions-menu

.. image:: https://img.shields.io/coveralls/github/goerz/doctr_versions_menu/master.svg
   :alt: Coveralls
   :target: https://coveralls.io/github/goerz/doctr_versions_menu?branch=master

.. image:: https://img.shields.io/badge/License-MIT-green.svg
   :alt: MIT License
   :target: https://opensource.org/licenses/MIT

Sphinx_ extension and utility to add a versions menu to Doctr_-deployed documentation.

Doctr_ is a tool that deploys Sphinx_ documentation to `Github Pages`_. It is an
alternative to the popular `Read the Docs`_ (RTD). Compared to RTD, Doctr gives
full control over the documentation build process. However, Doctr
out of the box does not support documentation for multiple versions of a
package at the same time (unlike RTD).

The ``doctr-versions-menu`` package aims to remedy this. It provides a Sphinx
extension and a command line tool that work together to generate a dynamic
versions menu similar to that on RTD pages:

.. image:: https://raw.githubusercontent.com/goerz/doctr_versions_menu/master/docs/_static/doctr-versions-menu-screenshot.png
  :alt: Doctr Versions Menu Screenshot

It also injects warnings for outdated or unreleased versions.

See the ``doctr-versions-menu`` documentation itself for a `live example <online_>`_.

Development of Doctr Versions Menu happens on `Github`_.
You can read the full documentation online_.

⚠️  **WARNING**: This implementation is work in progress. No public release is
available at this time, nor should the current development version (``master``)
be considered functional.


Installation
------------
To install the latest released version of doctr-versions-menu, run this command in your terminal:

.. code-block:: console

    $ pip install doctr-versions-menu

This is the preferred method to install Doctr Versions Menu, as it will always install the most recent stable release.

If you don't have `pip`_ installed, the `Python installation guide`_, respectively the `Python Packaging User Guide`_  can guide
you through the process.

To install the latest development version of ``doctr-versions-menu`` from `Github`_.

.. code-block:: console

    $ pip install git+https://github.com/goerz/doctr_versions_menu.git@master#egg=doctr_versions_menu


Usage
-----

Showing a versions menu in your documentation requires two steps:

1.  Add ``'doctr_versions_menu'`` to the list of extensions in your Sphinx ``conf.py``.

    This adds javascript to your rendered documentation that displays a dynamic versions menu based on information in a ``versions.json`` file it expects to find in the root for your ``gh-pages`` branch.


2.  Call the ``doctr-versions-menu`` command as part of ``doctr deploy``.

    For example,

    .. code-block:: console

        python -m doctr deploy --command="doctr-versions-menu" --no-require-master --build-tags "$DEPLOY_DIR"

    This causes ``doctr-versions-menu`` to be executed in the root of the ``gh-pages`` branch. The script examines the folders that exist there, and generates the ``versions.json`` file that step 1 relies on.

See the `full documentation <online_>`_ for Step 1 and Step 2 for details.


.. _Github: https://github.com/goerz/doctr_versions_menu
.. _Github pages: https://pages.github.com
.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/
.. _Python Packaging User Guide: https://packaging.python.org/tutorials/installing-packages/
.. _Doctr: https://drdoctr.github.io
.. _Sphinx: https://www.sphinx-doc.org/
.. _online: https://goerz.github.io/doctr_versions_menu/
.. _Read the Docs: https://readthedocs.org
