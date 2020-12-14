===================
Doctr Versions Menu
===================

.. image:: https://img.shields.io/badge/goerz-doctr__versions__menu-blue.svg?logo=github
   :alt: Source code on Github
   :target: https://github.com/goerz/doctr_versions_menu

.. image:: https://img.shields.io/badge/docs-doctr-blue.svg
   :alt: Documentation
   :target: https://goerz.github.io/doctr_versions_menu/

.. image:: https://img.shields.io/pypi/v/doctr_versions_menu.svg
   :alt: doctr-versions-menu on the Python Package Index
   :target: https://pypi.python.org/pypi/doctr_versions_menu

.. image:: https://img.shields.io/travis/goerz/doctr_versions_menu.svg
   :alt: Travis Docs CD
   :target: https://travis-ci.com/goerz/doctr_versions_menu

.. image:: https://github.com/goerz/doctr_versions_menu/workflows/Tests/badge.svg?branch=master
   :alt: Tests
   :target: https://github.com/goerz/doctr_versions_menu/actions?query=workflow%3ATests

.. image:: https://img.shields.io/coveralls/github/goerz/doctr_versions_menu/master.svg
   :alt: Coveralls
   :target: https://coveralls.io/github/goerz/doctr_versions_menu?branch=master

.. image:: https://img.shields.io/badge/License-MIT-green.svg
   :alt: MIT License
   :target: https://opensource.org/licenses/MIT

Sphinx_ extension and command to add a versions menu to Doctr_-deployed documentation.

Doctr_ is a tool that deploys Sphinx_ documentation from `Travis CI <Travis_>`_
to `Github Pages`_. It is an alternative to the popular `Read the Docs`_ (RTD).
Compared to RTD, Doctr gives full control over the documentation build process.
However, Doctr out of the box does not support documentation for multiple
versions of a package at the same time (unlike RTD).

The ``doctr-versions-menu`` package aims to remedy this. It provides a Sphinx
extension and a command line tool that work together to generate a dynamic
versions menu similar to that on RTD pages:

.. image:: https://raw.githubusercontent.com/goerz/doctr_versions_menu/master/docs/_static/doctr-versions-menu-screenshot.png
  :alt: Doctr Versions Menu Screenshot

It also injects warnings for outdated or unreleased versions.

See the ``doctr-versions-menu`` documentation itself for a `live example <online_>`_.

Development of Doctr Versions Menu happens on `Github`_.
You can read the full documentation online_.

⚠️ **As of December 2020, Travis no longer provides free services to open source projects.** See `Deployment with Github Actions <https://goerz.github.io/doctr_versions_menu/v0.4.0/command.html#deployment-with-github-actions>`_ for a workaround.


Installation
------------

To install the latest released version of ``doctr-versions-menu``, run:

.. code-block:: shell

    pip install doctr-versions-menu

Or, to install the latest development version of ``doctr-versions-menu`` from `Github`_:

.. code-block:: shell

    pip install git+https://github.com/goerz/doctr_versions_menu.git@master#egg=doctr_versions_menu


The ``doctr-versions-menu`` package can also be installed through conda_, using
the conda-forge_ channel. See the `instructions in the Doctr Versions Menu
Feedstock <conda-feedstock-instructions_>`_.

In practice, you probably only have to install the ``doctr-versions-menu``
package on Travis_, for generating and deploying the documentation; or, e.g.,
in a local tox_ environment for generating documentation locally during
development.


Usage
-----

Showing a versions menu in your documentation requires two steps:

1.  Add ``'doctr_versions_menu'`` to the list of extensions in your Sphinx ``conf.py``.

    This adds javascript to your rendered documentation that displays a dynamic versions menu based on information in a ``versions.json`` file it expects to find in the root for your ``gh-pages`` branch.


2.  Call the ``doctr-versions-menu`` command as part of ``doctr deploy`` (in ``.travis.yml``).

    For example,

    .. code-block:: shell

        doctr deploy --command=doctr-versions-menu --no-require-master --build-tags "$DEPLOY_DIR"

    This causes ``doctr-versions-menu`` to be executed in the root of the ``gh-pages`` branch. The script examines the folders that exist there, and generates the ``versions.json`` file that step 1 relies on.

See the `full documentation <online_>`_ on Step 1 and Step 2 for details. However, for projects that follow normal best practices, **you should not require any customization beyond the above two steps**.


Examples
--------

The following projects use ``doctr-versions-menu``:

* Krotov_
* caproto_
* pcds-ci-helpers_ (an example of shared Travis CI configurations using doctr-versions-menu)
* lcls-twincat-general_ (among many other PLC projects at the LCLS)

.. _Github: https://github.com/goerz/doctr_versions_menu
.. _Github pages: https://pages.github.com
.. _Doctr: https://drdoctr.github.io
.. _Sphinx: https://www.sphinx-doc.org/
.. _online: https://goerz.github.io/doctr_versions_menu/
.. _Read the Docs: https://readthedocs.org
.. _Travis: https://travis-ci.org
.. _tox: https://tox.readthedocs.io
.. _Krotov: https://qucontrol.github.io/krotov/
.. _caproto: https://caproto.github.io/caproto/
.. _pcds-ci-helpers: https://github.com/pcdshub/pcds-ci-helpers/blob/d1bb15ace06cfd8fdda3f5ccad0981fcc59dfbe0/travis/shared_configs/doctr-upload.yml
.. _lcls-twincat-general: https://pcdshub.github.io/lcls-twincat-general/
.. _conda: https://docs.conda.io
.. _conda-forge: https://conda-forge.org
.. _conda-feedstock-instructions: https://github.com/conda-forge/doctr-versions-menu-feedstock#installing-doctr-versions-menu
