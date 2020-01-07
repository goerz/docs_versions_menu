.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.


Code of Conduct
---------------

Everyone interacting in the Doctr Versions Menu project's code base,
issue tracker, and any communication channels is expected to follow the
`PyPA Code of Conduct`_.

.. _`PyPA Code of Conduct`: https://www.pypa.io/en/latest/code-of-conduct/


Report Bugs
-----------

Report bugs at https://github.com/goerz/doctr_versions_menu/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug, ideally a minimal but complete script or
  notebook.
* All error messages in full, as plain text. If the output is long, attach it
  as a file.


Submit Feedback
---------------

The best way to send feedback is to file an issue at https://github.com/goerz/doctr_versions_menu/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)


Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated.
3. Check https://travis-ci.org/goerz/doctr_versions_menu/pull_requests
   and make sure that the tests pass for all supported Python versions.



Get Started!
------------

Ready to contribute? Follow `Aaron Meurer's Git Workflow Notes`_ (with ``goerz/doctr_versions_menu`` instead of ``sympy/sympy``)

In short,

1. Clone the repository from ``git@github.com:goerz/doctr_versions_menu.git``
2. Fork the repo on GitHub to your personal account.
3. Add your fork as a remote.
4. Pull in the latest changes from the master branch.
5. Create a topic branch.
6. Make your changes and commit them (testing locally).
7. Push changes to the topic branch on *your* remote.
8. Make a pull request against the base master branch through the Github website of your fork.

The project uses tox_ for automated testing accross multiple versions of Python
and for various development tasks such as linting and generating the
documentation. See :ref:`DevelopmentPrerequisites` for details.

There is also a ``Makefile`` that wraps around tox, for
convenience on Unix-based systems. In your checked-out clone, run

.. code-block:: console

    $ make help

to see the available make targets. If you cannot use ``make``, but want to use
``tox`` directly (e.g., on Windows), run

.. code-block:: console

    $ tox -av

to see a list of tox environments and a description.

.. _tox: https://tox.readthedocs.io

.. _Aaron Meurer's Git Workflow Notes:  https://www.asmeurer.com/git-workflow/


.. _DevelopmentPrerequisites:

Development Prerequisites
-------------------------

Contributing to the package's developments requires that you have Python 3.8
and tox_ installed. It is strongly recommended that you also have installations
of all other supported Python versions. The recommended way to install multiple
versions of Python at the same time is through pyenv_ (or pyenv-win_ on
Windows).


.. _pyenv: https://github.com/pyenv/pyenv
.. _pyenv-win: https://github.com/pyenv-win/pyenv-win


.. _BranchingModel:

Branching Model
---------------

For developers with direct access to the repository,
Doctr Versions Menu uses a simple branching model where all
developments happens directly on the ``master`` branch. Releases are tags on
``master``. All commits on ``master`` *should* pass all tests and be
well-documented. This is so that ``git bisect`` can be effective. For any
non-trivial issue, it is recommended to create a topic branch, instead of
working on ``master``. There are no restrictions on commits on topic branches,
they do not need to contain complete documentation, pass any tests, or even be
able to run.

To create a topic-branch named ``issue1``::

    $ git branch issue1
    $ git checkout issue1

You can then make commits, and push them to Github to trigger Continuous
Integration testing::

    $ git push -u origin issue1

Commit early and often! At the same time, try to keep your topic branch
as clean and organized as possible. If you have not yet pushed your topic
branch to the "origin" remote:

* Avoid having a series of meaningless granular commits like "start bugfix",
  "continue development", "add more work on bugfix", "fix typos", and so forth.
  Instead, use ``git commit --amend`` to add to your previous commit. This is
  the ideal way to "commit early and often". You do not have to wait until a
  commit is "perfect"; it is a good idea to make hourly/daily "snapshots" of
  work in progress. Amending a commit also allows you to change the commit
  message of your last commit.
* You can combine multiple existing commits by "squashing" them. For example,
  use ``git rebase -i HEAD~4`` to combined the previous four commits into one.
  See the `"Rewriting History" section of Pro Git book`_ for details (if you
  feel this is too far outside of your git comfort zone, just skip it).
* If you work on a topic branch for a long time, and there is significant work
  on ``master`` in the meantime, periodically rebase your topic branch on the
  current master (``git rebase master``). Avoid merging ``master`` into your
  topic branch. See `Merging vs. Rebasing`_.

If you have already pushed your topic branch to the remote origin, you have to
be a bit more careful. If you are sure that you are the only one working on
that topic branch, you can still follow the above guidelines, and force-push
the issue branch (``git push --force``). This also applies if you are an
external contributor preparing a pull request in your own clone of the project.
If you are collaborating with others on the topic branch, coordinate with them
whether they are OK with rewriting the history. If not, merge instead of
rebasing. You must never rewrite history on the ``master`` branch (nor will you
be able to, as the ``master`` branch is "protected" and can only be force-pushed to
in coordination with the project maintainer).  If something goes wrong with any
advanced "history rewriting", there is always `"git reflog"`_ as a safety net
-- you will never lose work that was committed before.

When you are done with a topic branch (the issue has been fixed), finish up by
merging the topic branch back into ``master``::

    $ git checkout master
    $ git merge --no-ff issue1

The ``--no-ff`` option is critical, so that an explicit merge commit is created
(especially if you rebased).  Summarize the changes of the branch relative to
``master`` in the commit message.

Then, you can push master and delete the topic branch both locally and on Github::

    $ git push origin master
    $ git push --delete origin issue1
    $ git branch -D issue1

.. _"Rewriting History" section of Pro Git book: https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History
.. _Merging vs. Rebasing: https://www.atlassian.com/git/tutorials/merging-vs-rebasing
.. _"git reflog": https://www.atlassian.com/git/tutorials/rewriting-history/git-reflog


Commit Message Guidelines
-------------------------

Write commit messages according to this template:

.. code-block:: none

    Short (50 chars or less) summary ("subject line")

    More detailed explanatory text. Wrap it to 72 characters. The blank
    line separating the summary from the body is critical (unless you omit
    the body entirely).

    Write your subject line in the imperative: "Fix bug" and not "Fixed
    bug" or "Fixes bug." This convention matches up with commit messages
    generated by commands like git merge and git revert. A properly formed
    git commit subject line should always be able to complete the sentence
    "If applied, this commit will <your subject line here>".

    Further paragraphs come after blank lines.

    - Bullet points are okay, too.
    - Typically a hyphen or asterisk is used for the bullet, followed by a
      single space. Use a hanging indent.

    You should reference any issue that is being addressed in the commit, as
    e.g. "#1" for issue #1. If the commit closes an issue, state this on the
    last line of the message (see below). This will automatically close the
    issue on Github as soon as the commit is pushed there.

    Closes #1

See `Closing issues using keywords`_ for details on references to issues that
Github will understand.


Testing
-------

Doctr Versions Menu includes a full test-suite using pytest_.
We strive for a `test coverage`_ above 90%.


From a checkout of the ``doctr_versions_menu`` repository  you can use

.. code-block:: console

    $ make test

to run the entire test suite, or

.. code-block:: console

    $ tox -e py35-test,py36-test,py37-test,py38-test

if ``make`` is not available.

The tests are organized in the ``tests`` subfolder. It includes python scripts
whose name start with ``test_``, which contain functions whose names also start
with ``test_``. Any such functions in any such files are picked up by `pytest`_
for testing. In addition, doctests_ from any docstring or any documentation
file (``*.rst``) are picked up (by the `pytest doctest plugin`_).


.. _test coverage: https://coveralls.io/github/goerz/doctr_versions_menu?branch=master
.. _pytest: https://docs.pytest.org/en/latest/
.. _doctests: https://docs.python.org/3.7/library/doctest.html
.. _pytest doctest plugin: https://docs.pytest.org/en/latest/doctest.html


Code Style
----------

All code must be compatible with :pep:`8`. The line length limit
is 79 characters, although exceptions are permissible if this improves
readability significantly.


Beyond :pep:`8`, this project adopts the `Black code style`_, with
``--skip-string-normalization --line-length 79``. You can
run ``make black-check`` or ``tox -e run-blackcheck`` to check adherence to the
code style, and ``make black`` or ``tox -e run-black`` to apply it.


.. _Black code style: https://github.com/ambv/black/#the-black-code-style


Imports within python modules must be sorted according to the isort_
configuration in ``setup.cfg``. The command ``make isort-check`` or ``tox -e
run-isortcheck`` checks whether all imports are sorted correctly, and ``make
isort`` or ``tox -e run-isort`` modifies all Python modules in-place with the
proper sorting.

.. _isort: https://github.com/timothycrosley/isort#readme


The code style is enforced as part of the test suite, as well as through git
pre-commit hooks that prevent committing code not does not meet the
requirements. These hooks are managed through the `pre-commit framework`_.


.. _pre-commit framework: https://pre-commit.com

You may use ``make flake8-check`` or ``tox -e run-flake8`` and ``make
pylint-check`` or ``tox -e run-pylint`` for additional checks on the code with
flake8_ and pylint_, but there is no strict requirement for a perfect score
with either one of these linters. They only serve as a guideline for code that
might be improved.

.. _flake8: http://flake8.pycqa.org
.. _pylint: http://pylint.pycqa.org




.. _write-documentation:

Write Documentation
-------------------

Doctr Versions Menu could always use more documentation, whether
as part of the official docs, in docstrings, or even on the web in blog posts,
articles, and such.

The package documentation is generated with Sphinx_, the
documentation (and docstrings) are formatted using the
`Restructured Text markup language`_ (file extension ``rst``).
See also the `Matplotlib Sphinx cheat sheet`_ for some helpful tips.

Each function or class must have a docstring_; this docstring must
be written in the `"Google Style" format`_ (as implemented by
Sphinx' `napoleon extension`_). Docstrings and any other part of the
documentation can include `mathematical formulas in LaTeX syntax`_
(using mathjax_).

For module variables and class attributes, use a docstring "inline" immediately
after the definition. However, for instance attributes, it is preferable to include
an "Attributes:" section in the class docstring (instead of using "attribute
docstrings" in ``__init__``). While attribute docstrings have the benefit that
it is less likely for there to be a mismatch between the documentation and the
implementation, they also have some significant drawbacks, for example: They do
not show up in ``help(<class>)`` or ``<class>?`` in IPython, they tend to make
``__init__`` much harder to read, and they don't work for classes defined via
attrs_.

The ``__init__`` method should never have a docstring; it's arguments are
described in the class docstring instead.

At any point, from a checkout of the ``doctr_versions_menu``
repository, you may run

.. code-block:: console

    $ make docs

or

.. code-block:: console

    $ tox -e docs


to generate the documentation locally.

.. _Sphinx: http://www.sphinx-doc.org/en/master/
.. _Restructured Text markup language: http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
.. _docstring: https://www.python.org/dev/peps/pep-0257/
.. _"Google Style" format: http://www.sphinx-doc.org/en/master/usage/extensions/example_google.html#example-google
.. _napoleon extension: http://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
.. _mathematical formulas in LaTeX syntax: http://www.sphinx-doc.org/en/1.6/ext/math.html
.. _mathjax: http://www.sphinx-doc.org/en/master/usage/extensions/math.html#module-sphinx.ext.mathjax
.. _BibTeX: https://sphinxcontrib-bibtex.readthedocs.io/en/latest/
.. _Matplotlib Sphinx cheat sheet: https://matplotlib.org/sampledoc/cheatsheet.html
.. _attrs: http://www.attrs.org


Versioning
----------

Releases should follow `Semantic Versioning`_, and version numbers published to
PyPI_ must be compatible with :pep:`440`.

In short, versions number follow the pattern `major.minor.patch`, e.g.
``0.1.0`` for the first release, and ``1.0.0`` for the first *stable* release.
If necessary, pre-release versions might be published as e.g:

.. code-block:: none

    1.0.0-dev1  # developer's preview 1 for release 1.0.0
    1.0.0-rc1   # release candidate 1 for 1.0.0

Errors in the release metadata or documentation only may be fixed in a
post-release, e.g.:

.. code-block:: none

    1.0.0.post1  # first post-release after 1.0.0

Post-releases should be used sparingly, but they are acceptable even though
they are not supported by the `Semantic Versioning`_ specification.

Between releases, ``__version__`` on the master branch should either be the
version number of the last release, with "+dev" appended (as a
`"local version identifier"`_), or the version number of the next planned
release, with "-dev" appended (`"pre-release identifier"`_ with extra dash).
The version string "1.0.0-dev1+dev" is a valid value after the "1.0.0-dev1"
pre-release. The "+dev" suffix must never be included in a release to PyPI_.

Note that twine_ applies normalization_ to the above recommended forms to
make them strictly compatible with :pep:`440`, before uploading to PyPI_. Users
installing the package through pip_ may use the original version specification
as well as the normalized one (or any other variation that normalizes to the
same result).

When making a release via

.. code-block:: shell

    $ make release

the above versioning conventions will be taken into account automatically.

Releases must be tagged in git, using the version string prefixed by "v",
e.g. ``v1.0.0-dev1`` and ``v1.0.0``. This makes them available at
https://github.com/goerz/doctr_versions_menu/releases.

.. _Semantic Versioning: https://semver.org
.. _"local version identifier": https://www.python.org/dev/peps/pep-0440/#local-version-identifiers
.. _"pre-release identifier": https://www.python.org/dev/peps/pep-0440/#pre-releases
.. _normalization: https://legacy.python.org/dev/peps/pep-0440/#id29
.. _PyPI: http://pypi.org
.. _twine: https://twine.readthedocs.io/en/latest/
.. _pip: https://pip.readthedocs.io/en/stable/
.. _Closing issues using keywords: https://help.github.com/articles/closing-issues-using-keywords/
