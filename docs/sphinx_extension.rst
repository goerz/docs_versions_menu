.. _sphinx_extension:

========================
Step 1: Sphinx extension
========================

In your Documentation's ``conf.py``, add ``'docs_versions_menu'`` to your
:confval:`extensions`.

That's it.

See the Docs Versions Menu's |conf_py|_ for an example.

.. |conf_py| replace:: ``conf.py``
.. _conf_py: https://github.com/goerz/docs_versions_menu/blob/master/docs/conf.py

This will inject a javascript file ``docs-versions-menu.js`` into every
generated page of the documentation that displays a versions menu when the
documentation is hosted on Github Pages (the ``gh-pages`` branch of the project
repository). The contents of the menu is derived from a file ``versions.json``
that must be present in the root of ``gh-pages``.


.. Note::

    By default, the versions menu will only appear when the documentation is
    viewed at a Github Pages URL (``https://<username>.github.io/<project>/<version>/``)
    and if a file ``versions.json`` is present in the ``<project>`` folder
    (that is, the root of the ``gh-pages`` branch).
    It will not appear when viewing documentation locally.


Sphinx themes
-------------

For best results, use the `Read the Docs Sphinx Theme`_ (``sphinx_rtd_theme``).
This is the default theme for documentation hosted on ``readthedocs.org`` (RTD).
However, it can also be used when hosting documentation outside of RTD!

Especially for documentation that includes extensive reference (API) content,
the RTD theme provides a much better visual structure than Sphinx' default ``alabaster``
theme which is also used on this page [#f1]_.

With ``sphinx_rtd_theme``, the versions menu will be displayed as part of the
navigation bar on the left side of the screen (just like on RTD). For any other
Sphinx theme, the versions menu will be shown as a "badge" in the bottom right
corner of the page (like on this page; and, like for documentation hosted on
RTD that doesn't use the default theme).

The theme is automatically detected based on the value of :confval:`html_theme`
in the Sphinx ``conf.py`` file. If this is anything other than
``"sphinx_rtd_theme"``, the badge-style versions menu is used. This implies
that in addition to the javascript file ``docs-versions-menu.js``, a
``badge_only.css`` file as well as a number of `Font Awesome`_ files will be
included in the generated documentation.

.. [#f1] The ``alabaster`` theme is used here to serve as a self-test for a badge-style versions menu. A version of this documentation using the RTD theme is available through the versions menu.


.. _sphinx_ext_customization:

Settings in ``conf.py``
-----------------------

The settings for the Sphinx extensions are taken from a dict
``docs_versions_menu_conf`` in Sphinx' ``conf.py`` configuration file.

The dict may contain the following keys:

* ``json_file`` (str): The local (absolute) path to the json file that contains version information. Defaults to ``/<project>/versions.json`` with ``<project>`` dynamically set based on the current Github Pages URL (``https://<username>.github.io/<project>/<version>/...``)
* ``github_project_url`` (str): The full URL to the project on Github. By default, this is dynamically derived from the current Github Pages URL (see above).
* ``current_folder`` (str): The name of the current folder. By default, dynamically set to the ``<version>`` from the current Github Pages URL (see above).
* ``badge_only`` (bool): Whether to render the version menu as a "badge" in the lower right corner (defaults to True unless :confval:`html_theme` is ``"sphinx_rtd_theme"``)
* ``menu_title`` (str): The label to be shown in to left corner of the full versions menu (if not ``badge_only``). Defaults to "Docs".

Do not use the setting ``badge_only=False`` together with the
``sphinx_rtd_theme``. In order to avoid the ``badge_only.css`` and font files
being injected if you are using a completely custom template, do set ``badge_only=False``
and supply your own CSS files e.g. in a :confval:`html_static_path` folder.


.. _Read the Docs Sphinx Theme: https://sphinx-rtd-theme.readthedocs.io/
.. _Font Awesome: https://fontawesome.com
.. _default template: https://github.com/goerz/docs_versions_menu/blob/master/src/docs_versions_menu/_template/docs-versions-menu.js_t
.. _this project's conf.py for an example: https://github.com/goerz/docs_versions_menu/blob/65e87b09e696c82db92169718b8df8ba822e05b3/docs/conf.py#L23-L36
.. _Doctr: https://drdoctr.github.io
