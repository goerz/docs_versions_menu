Templates
=========

.. _customizing_index_html:

index.html template
-------------------

By default, ``docs-versions-menu`` generates an ``index.html`` file in the root
of the ``gh-pages`` branch that redirects to the current "default folder".
This is the folder for the most current public release (:option:`--latest
<docs-versions-menu --latest>`), or the default branch
(:option:`--default-branch <docs-versions-menu --default-branch>`) if no
public release exists.

The generated ``index.html`` file can be customized by placing an
``index.html_t`` Jinja_ template into the root of the ``gh-pages`` branch.
This template will be rendered receiving a dict ``version_data`` containing the
data in ``versions.json`` (see the :ref:`versions_json_structure`).

.. note::

    There is no support for an RTD-style "latest"/"stable" folder. This is by
    design: deep-linking to "latest" documentation is a bad practice, as such links
    easily become invalid when a new version is released.

The default template is

.. literalinclude:: ../src/docs_versions_menu/_template/index.html_t
    :language: html

Alternatively, if you want a completely static ``index.html``, you could also
just add that file by hand and use :option:`--no-write-index-html
<docs-versions-menu --no-write-index-html>` (that is,
``DOCS_VERSIONS_MENU_WRITE_INDEX_HTML=false`` as an environment variable).

.. _customizing_docs_versions_menu_js:

docs-versions-menu.js template
------------------------------

You may fully customize the versions menu by placing a Jinja_ template
file ``docs-versions-menu.js_t`` in a folder listed in your
:confval:`templates_path`.

This template will be rendered to produce ``docs-versions-menu.js``
using values from a dictionary ``docs_versions_menu_conf`` in your Sphinx
``conf.py`` file.


.. _Jinja: https://jinja.palletsprojects.com/en/2.10.x/
