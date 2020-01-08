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

Development of Doctr Versions Menu happens on `Github`_.
You can read the full documentation online_.



⚠️  **WARNING**: This implementation is work in progress. No public release is
available at this time, nor should the current development version (``master``)
be considered functional.


Installation
------------
To install the latest released version of doctr-versions-menu, run this command in your terminal:

.. code-block:: console

    $ pip install doctr_versions_menu

This is the preferred method to install Doctr Versions Menu, as it will always install the most recent stable release.

If you don't have `pip`_ installed, the `Python installation guide`_, respectively the `Python Packaging User Guide`_  can guide
you through the process.

To install the latest development version of doctr-versions-menu from `Github`_.

.. code-block:: console

    $ pip install git+https://github.com/goerz/doctr_versions_menu.git@master#egg=doctr_versions_menu


Usage
-----

Showing a versions menu in your documentation requires two steps:

1. Add ``'doctr_versions_menu'`` to the list of extensions in your Sphinx ``conf.py``.
2. Call the ``doctr-versions-menu`` command as part of ``doctr deploy``.

See the `full documentation <online_>`_ for Step 1 and Step 2 for details.


.. _Github: https://github.com/goerz/doctr_versions_menu
.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/
.. _Python Packaging User Guide: https://packaging.python.org/tutorials/installing-packages/
.. _Doctr: https://drdoctr.github.io
.. _Sphinx: https://www.sphinx-doc.org/
.. _online: https://goerz.github.io/doctr_versions_menu/
