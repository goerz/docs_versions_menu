.. _folderspecs:

=====================
Folder Specifications
=====================

Several of the :ref:`command line options <options>`, e.g. :option:`--versions
<docs-versions-menu --versions>`, :option:`--latest <docs-versions-menu
--latest>`, :option:`--warning <docs-versions-menu --warning>`, and
:option:`--label <docs-versions-menu --label>`, use "folder specifications".

A folder specification is a comma-separated list of group names, folder names,
conditionals, slice-expressions, and sort-groupings, and it expands to an
ordered list of folders existing in the root of the deployed documentation.

Examples are:

1. The default specification for the folders shown in the versions menu:

   .. code-block:: shell

       (<branches> != <default-branch>), <releases>, <default-branch>

   which is equivalent to

   .. code-block:: shell

       (<branches> != master), <releases>, <default-branch>

   for projects that use ``master`` as their default branch, and

   .. code-block:: shell

       (<branches> != main), <releases>, <default-branch>

   for projects that use ``main`` as their default branch.


2. A specification for the folders shown in the versions menu in the reverse order:

   .. code-block:: shell

       ((<branches> != <default-branch>), <releases>, <default-branch>)[::-1]

3. The default specification of the "latest stable release" to which warning
   messages and ``index.html`` link:

   .. code-block:: shell

       (<public-releases>)[-1]

   equivalent to:

   .. code-block:: shell

       (<releases> not in (<local-releases>, <pre-releases>))[-1]

4. Specification for the folders showing an "outdated" warning (assuming the
   default :option:`--latest <docs-versions-menu --latest>`):

   .. code-block:: shell

       (<releases> < (<public-releases>)[-1])



Group Names
-----------

Groups are denoted by angled brackets (``<``, ``>``), e.g. ``<branches>``,
``<releases>``, etc. in the examples. They are automatically expanded to the
relevant *existing* folders in increasing order (following :pep:`440`,
respectively alphabetical for branch names). The available
groups correspond to the various classifications within :pep:`440`:

* ``<local-releases>``: list of folders whose name ends in a `local version label`_ separated from the public version part by a plus sign. E.g. "v1.0.0+dev"
* ``<dev-releases>``:  list of folders whose name ends in a `developmental release segment`_, e.g. "v1.0.0-dev0"
* ``<pre-releases>``:  list of folders whose name ends in a `pre-release segment`_, e.g. "v1.0.0-rc1". This includes dev-releases.
* ``<post-releases>``: list of folders whose name ends in a `post-release segment`_, e.g. "v1.0.0.post1"
* ``<final-releases>``: list of folders whose name ends in a `consists solely of a release segment`_ (no local-, pre-, or post-segments), e.g. "v1.0.0"
* ``<public-releases>``: combination of final-releases and post-releases, i.e., releases intended for the general public
* ``<releases>``: list of folders whose name is a :pep:`440`-conforming release. This includes all of the above groups.
* ``<default-branch>``: list of folders matching the specification in the :option:`--default-branch <docs-versions-menu --default-branch>` option. This *should* contain only a single value, the name of the default branch, e.g. "main" or "master".
* ``<branches>``: list of folders whose name is not a :pep:`440`-conforming release. These are assumed to be branch names, e.g. "master".
* ``<all>``: list of all folders (combination of ``<releases>`` and ``<branches>``)

.. _local version label: https://www.python.org/dev/peps/pep-0440/#local-version-identifiers
.. _developmental release segment: https://www.python.org/dev/peps/pep-0440/#developmental-releases
.. _pre-release segment: https://www.python.org/dev/peps/pep-0440/#pre-releases
.. _consists solely of a release segment: https://www.python.org/dev/peps/pep-0440/#final-releases
.. _post-release segment: https://www.python.org/dev/peps/pep-0440/#post-releases

Note that for :pep:`440`, the leading ``v`` in a folder name is ignored
(``v1.0.0`` and ``1.0.0`` is the same). It is customary to include the leading
``v`` in tagged releases, and thus your folder names should include the leading
``v``.


Folder Names
------------

Folder names, e.g. ``master``, are directly included in the expanded
specification, *if and only if the exist*.


Conditionals
------------

A conditional expression is enclosed in parentheses, containing a folder
specification followed by one or more conditions. Each condition consists of a
logical operator followed by another folder specification, for example

* ``(<branches> != master)`` cf. example 1
* ``(<releases> not in (<local-releases>, <pre-releases>))`` in example 3.
* ``(<releases> < (<public-releases>)[-1])``, example 4

There may be multiple conditions, e.g. ``(<releases> >= 1.0 < 2.0)`` will
evaluate to include all the folders for ``1.*`` releases.

The full list of logical operators are:

* ``in``: selects a subset
* ``not in``: excludes a subset
* ``<=``: selects all folders lower than or matching the given version (or set of versions), according to :pep:`440`.
* ``<``:  selects all folders lower than the given version
* ``!=``: excludes a specific version (or a subset; `!=` is equivalent to ``not in`` if the operand is a set)
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
examples 2, 3 and 4.

The notation ``[::-1]`` (example 2) simply reverses the order of the list.
Technically, example 3 evaluates to a single-item list, but within the folder
specification mini-language, the distinction between an item and a single-item
list is meaningless.


Sort-Groupings
--------------

A sub-expression enclosed in parentheses is expanded and then sorted
in its entirety according to :pep:`440`. The sorting only happens if the
parentheses are not followed by a slice specification:

* ``v1.0.0, v0.2.0, v1.1.1`` is not sorted
* ``(v1.0.0, v0.2.0, v1.1.1)`` is sorted as ``v0.2.0, v1.0.0, v1.1.1``
* ``(v1.0.0, v0.2.0, v1.1.1)[::-1]`` is not sorted (due to the slice specification)
* ``((v1.0.0, v0.2.0, v1.1.1))[::-1]`` is sorted as ``v1.1.1, v1.0.0, v0.2.0``
