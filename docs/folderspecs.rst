.. _folderspecs:

=====================
Folder Specifications
=====================

Several of the :ref:`command-line-options`, e.g. ``--versions``, ``--latest``,
``--warning``, and ``--label``, use "folder specifications".

A folder specification is a comma-separated list of group names, folder names,
conditionals, slice-expressions, and sort-groupings, and it expands to an
ordered list of folders existing in the root of the ``gh-pages`` branch.

Examples are:

1. The default specification for the folders shown in the versions menu:

   .. code-block:: shell

       (<branches> != master), <releases>, master

2. A specification for the folders shown in the versions menu in the reverse order:

   .. code-block:: shell

       ((<branches> != master), <releases>, master)[::-1]

3. The default specification of the "latest stable release" to which warning
   messages and ``index.html`` link:

   .. code-block:: shell

       (<releases> not in (<local-releases>, <pre-releases>))[-1]

4. Specification for the folders showing an "outdated" warning, if the latest stable release is ``v1.0.0``.:

   .. code-block:: shell

       (<releases> < 1.0.0)



Group Names
-----------

Groups are denoted by angled brackets (``<``, ``>``), e.g. ``<branches>``,
``<releases>``, etc. in the examples. They are automatically expanded to the
relevant *existing* folders in increasing order (following :pep:`440`,
respectively alphabetical for branch names). The available
groups correspond to the various classifications within pep:`440`:

* ``<local-releases>``: list of folders whose name ends in a `local version label`_ separated from the public version part by a plus sign. E.g. "v1.0.0+dev"
* ``<dev-releases>``:  list of folders whose name ends in a `developmental release segment`_, e.g. "v1.0.0-dev0"
* ``<pre-releases>``:  list of folders whose name ends in a `pre-release segment`_, e.g. "v1.0.0-rc1". This includes dev-releases.
* ``<post-releases>``: list of folders whose name ends in a `post-release segment`_, e.g. "v1.0.0.post1"
* ``<releases>``: list of folders whose name is a :pep:`440`-conforming release. This includes all of the above groups.
* ``<branches>``: list of folders whose name is not a :pep:`440`-conforming release. These are assumed to be branch names, e.g. "master".
* ``<all>``: list of all folders (combination of ``<releases>`` and ``<branches>``

.. _local version label: https://www.python.org/dev/peps/pep-0440/#local-version-identifiers
.. _developmental release segment: https://www.python.org/dev/peps/pep-0440/#developmental-releases
.. _pre-release segment: https://www.python.org/dev/peps/pep-0440/#pre-releases
.. _post-release segment: https://www.python.org/dev/peps/pep-0440/#post-releases

Note that for :pep:`440`, the leading ``v`` in a folder name is ignored
(``v1.0.0`` and ``1.0.0`` is the same). It is customary to include the leading
``v`` in tagged releases, and thus your folder names should include the leading
``v``.


Folder Names
------------

Folder names, e.g. ``master`` in examples 1 and 2, are directly included in the
expanded specification, *if and only if the exist*.


Conditionals
------------

A conditional expression is enclosed in parentheses, containing a folder
specification followed by one or more conditions. Each condition consists of a
logical operator followed by another folder specification, for example

* ``(<branches> != master)`` in examples 1,2
* ``(<releases> not in (<local-releases>, <pre-releases>))`` in example 3.
* ``(<releases> < 1.0.0)``, example 4

There may be multiple conditions, e.g. ``(<releases> >= 1.0 < 2.0)`` will
evaluate to include all the folders for ``1.*`` releases.

The full list of logical operators are:

* ``in``: selects a subset
* ``not int``: excludes a subset
* ``<=``: selects all folders lower than or matching the given version (or set of versions), according to :pep:`440`.
* ``<``:  selects all folders lower than the given version
* ``!=``: excludes a specific version.
* ``==``: selects a specific version
* ``>=``: selects all folders higher than or matching the given version (or set of versions)
* ``>``: selects all folders higher than the given version

The conditional may be followed directly by a slice specification (see below),
as in example 3

Slice-Expressions
-----------------

A slice-expression is enclosed in parentheses, and is followed by the standard
Python slice notation ``[start:end:step]``, where ``start`` is inclusive,
``end`` is exclusive, and negative values count backwards from the end, as in
examples 2 and 3.

The notation ``[::-1]`` (example 2) simply reverses the order of the list.
Technically, example 3 evaluates to a single-item list, but within the folder
specification mini-language, the distinction between an item and a single-item
list is meaningless.


Sort-Groupings
--------------

A sub-expression enclosed in parentheses, e.g.
``(<local-releases>, <pre-releases>)`` in example 3, is expanded and then sorted
according to :pep:`440` (not that the sorting makes any difference to the
subset selection in example 3). The sorting only happens if the parentheses are
not followed by a slice specification:

* ``v1.0.0, v0.2.0, v1.1.1`` is not sorted
* ``(v1.0.0, v0.2.0, v1.1.1)`` is sorted as ``v0.2.0, v1.0.0, v1.1.1``
* ``(v1.0.0, v0.2.0, v1.1.1)[::-1]`` is not sorted (due to the slice specification)
* ``((v1.0.0, v0.2.0, v1.1.1))[::-1]`` is sorted as ``v1.1.1, v1.0.0, v0.2.0``