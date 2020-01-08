========================
Step 1: Sphinx extension
========================

In your Documentation's ``conf.py``, add ``'doctr_versions_menu'`` to your
:confval:`extensions`.
This will inject the necessary javascript to display a versions menu when the
documentation is hosted on Github pages.

.. Note::

    By default, the versions menu will only appear when the documentation is
    viewed at a Github Pages URL (``https://<username>.github.io/<project>/<version>/``)
    and if a file ``versions.json`` is present in the ``<project>`` folder.
    It will not appear when viewing documentation locally.

