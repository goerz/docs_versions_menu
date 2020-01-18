.. _doc_artifacts:

=======================
Documentation Artifacts
=======================


`Read the Docs`_ can build the documentation in alternative formats (epub, pdf,
zipped html) and shows download links to these in the versions menu. The Doctr
Versions Menu also supports such "Downloads" links: the
:ref:`doctr-versions-menu-cli` utility looks for :ref:`download-links` in a
file ``_downloads`` in every subfolder of ``gh-pages``.

This ``_downloads`` file should be generated as part of building documentation, in
the ``.travis.yml`` file: Travis should build all binary documentation
artifacts (epub/pdf/zip), upload them to an external provider, and write the
appropriate labels and links to the ``_downloads`` file (e.g. in
``docs/_build/html/_downloads``).

If building the documentation artifacts on Travis is too complicated, you could
also create them on your local workstation as part of the release process,
upload them manually (e.g. to your project's `Github Releases`_ page), and have
Travis only write the (anticipated) links to the ``_downloads`` file. In any
case, you should not add documentation artifacts to your ``gh-pages``
branch: Git is not good at keeping large binary objects; you will blow up the
size of your repository.


Building artifacts
------------------

As an example for how build documentation, see the ``doctr_version_menu``
package's |doctr_build_sh_script|_ (which is sourced from |travis_yml|_):

.. |doctr_build_sh_script| replace:: ``doctr_build.sh`` script
.. _doctr_build_sh_script: https://github.com/goerz/doctr_versions_menu/blob/master/.travis/doctr_build.sh

.. |travis_yml| replace:: ``.travis.yml``
.. _travis_yml: https://github.com/goerz/doctr_versions_menu/blob/master/.travis.yml


The `following excerpt <artifactbuildsnippet_>`_ handles building the artifacts, after the main html
documentation has already been built in ``docs/_build/html``.

.. code-block:: bash

    mkdir docs/_build/artifacts

    echo "### [zip]"
    zip-folder --debug -a -o "docs/_build/artifacts/doctr_versions_menu-$TRAVIS_TAG.zip" docs/_build/html


    echo "### [pdf]"
    tox -e docs -- -b latex _build/latex
    tox -e run-cmd -- python docs/build_pdf.py docs/_build/latex/*.tex
    echo "finished latex compilation"
    mv docs/_build/latex/*.pdf "docs/_build/artifacts/doctr_versions_menu-$TRAVIS_TAG.pdf"


    echo "### [epub]"
    tox -e docs -- -b epub _build/epub
    mv docs/_build/epub/*.epub "docs/_build/artifacts/doctr_versions_menu-$TRAVIS_TAG.epub"


Obviously, the above depends on the specifics of the |tox file|_, and a
|build_pdf|_ script. The zip artifact is created using ``zip-folder`` from the
zip-files_ package.

.. |tox file| replace:: ``.tox.`` file
.. _tox file: https://github.com/goerz/doctr_versions_menu/blob/master/tox.ini

.. |build_pdf| replace:: ``docs/build_pdf.py``
.. _build_pdf: https://github.com/goerz/doctr_versions_menu/blob/master/docs/build_pdf.py

.. _zip-files: https://github.com/goerz/zip_files


LaTeX on Travis
~~~~~~~~~~~~~~~

Building the pdf artifact will require installing LaTeX (texlive_) on Travis.
The ``doctr_versions_menu`` package provides an example how to do this.

Consider the following excerpt from |travis_yml|_:

.. code-block:: yaml

    install:
      # any failure stops the build
      - set -e
      - export PATH=/tmp/texlive/bin/x86_64-linux:$PATH
      - travis_wait source .travis/texlive/texlive_install.sh
      - pip install tox
      - pip freeze
      - printenv
    cache:
      directories:
        - /tmp/texlive
        - $HOME/.texlive

This installs texlive via the support scripts in |travis_texlive|_. Due to the
use of caching, the installation only takes significant time on the first
Travis run of a given branch.

.. |travis_texlive| replace:: ``.travis/texlive``
.. _travis_texlive: https://github.com/goerz/doctr_versions_menu/blob/master/.travis/texlive


Uploading artifacts
-------------------

The |doctr_build_sh_script|_ also gives an example on how to upload the
artifacts to an external service. Future releases of ``doctr_versions_menu``
may include tools to simplify uploading documentation artifacts to third-party
providers.


Uploading to Bintray
~~~~~~~~~~~~~~~~~~~~

Bintray_ has a generous free account for open source project. Create an account
there, and set up a "repo" and "package" mirroring the names of the Github
project.

Uploading to Bintray requires to set the ``BINTRAY_USER``, ``BINTRAY_SUBJECT``,
``BINTRAY_REPO``, ``BINTRAY_PACKAGE`` and ``BINTRAY_TOKEN`` environment
variables in |travis_yml|_.

In the |doctr_build_sh_script|_, you can verify that these environment variables
are set correctly:

.. code-block:: bash

   if [ ! -z "$TRAVIS" ] && [ "$TRAVIS_EVENT_TYPE" != "pull_request" ]; then
       echo "## Check bintray status"
       # We *always* do this check: we don't just want to find out about
       # authentication errors when making a release
       if [ -z "$BINTRAY_USER" ]; then
           echo "BINTRAY_USER must be set" && sync && exit 1
       fi
       if [ -z "$BINTRAY_TOKEN" ]; then
           echo "BINTRAY_TOKEN must be set" && sync && exit 1
       fi
       if [ -z "$BINTRAY_PACKAGE" ]; then
           echo "BINTRAY_PACKAGE must be set" && sync && exit 1
       fi
       url="https://api.bintray.com/repos/$BINTRAY_SUBJECT/$BINTRAY_REPO/packages"
       response=$(curl --user "$BINTRAY_USER:$BINTRAY_TOKEN" "$url")
       if [ -z "${response##*$BINTRAY_PACKAGE*}" ]; then
           echo "Bintray OK: $url -> $response"
       else
           echo "Error: Cannot find $BINTRAY_PACKAGE in $url: $response" && sync && exit 1
       fi
   fi

Then *only when deploying the documentation of a tagged release*, and assuming
the documentation artifacts have been generated in ``docs/_build/artifacts``,
the following code uploads them:

.. code-block:: bash

   echo "Upload artifacts to bintray"
   for filename in docs/_build/artifacts/*; do
       url="https://api.bintray.com/content/$BINTRAY_SUBJECT/$BINTRAY_REPO/$BINTRAY_PACKAGE/$TRAVIS_TAG/$(basename $filename)"
       echo "Uploading $filename artifact to $url"
       response=$(curl --upload-file "$filename" --user "$BINTRAY_USER:$BINTRAY_TOKEN" "$url")
       if [ -z "${response##*success*}" ]; then
           case "$filename" in
               *.zip)  filelabel="html";;
               *.epub) filelabel="epub";;
               *.pdf)  filelabel="pdf";;
               *)      echo "Unknown type $filename";;
           esac
           echo "Uploaded $filename: $response"
           echo "[$filelabel]: https://dl.bintray.com/$BINTRAY_SUBJECT/$BINTRAY_REPO/$(basename $filename)" >> docs/_build/html/_downloads
       else
           echo "Error: Failed to upload $filename: $response" && sync && exit 1
       fi
   done
   echo "Publishing release on bintray"
   url="https://api.bintray.com/content/$BINTRAY_SUBJECT/$BINTRAY_REPO/$BINTRAY_PACKAGE/$TRAVIS_TAG/publish"
   response=$(curl --request POST --user "$BINTRAY_USER:$BINTRAY_TOKEN" "$url")
   if [ -z "${response##*files*}" ]; then
       echo "Finished bintray release : $response"
   else
       echo "Error: Failed publish release on bintray: $response" && sync && exit 1
   fi


Uploading to Github Releases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Attaching files to a Github release requires a ``GITHUB_TOKEN`` for
authorization in the ``.travis.yml`` file.

Note that such a token has very broad authorization to *all* repositories for a
particular user account. If you use such a token, you might as well use it also
for deploying Doctr (in lieu of the more `fine-tuned deploy key
<https://drdoctr.github.io/#faq>`__).

In ``doctr_build.sh``, the ``GITHUB_TOKEN`` can be verified as

.. code-block:: bash

   if [ ! -z "$TRAVIS" ] && [ "$TRAVIS_EVENT_TYPE" != "pull_request" ]; then
       echo "## Check GITHUB_TOKEN status"
       # We *always* do this check: we don't just want to find out about
       # authentication errors when making a release
       if [ -z "$GITHUB_TOKEN" ]; then
           echo "GITHIB_TOKEN must be set" && sync && exit 1
       fi
       GH_AUTH_HEADER="Authorization: token $GITHUB_TOKEN"
       url="https://api.github.com/repos/$TRAVIS_REPO_SLUG"
       curl -o /dev/null -sH "$AUTH" "$url" || { echo "Error: Invalid repo, token or network issue!";  sync; exit 1; }
   fi

Then, for tagged releases where the documentation artifacts have been built in
``docs/_build/artifacts``, the files could be uploaded with:

.. code:: bash

   url="https://api.github.com/repos/$TRAVIS_REPO_SLUG/releases"
   echo "Make release from tag $TRAVIS_TAG: $url"
   API_JSON=$(printf '{"tag_name": "%s","target_commitish": "master","name": "%s","body": "Release %s","draft": false,"prerelease": false}' "$TRAVIS_TAG" "$TRAVIS_TAG" "$TRAVIS_TAG")
   echo "submitted data = $API_JSON"
   response=$(curl --data "$API_JSON" --header "$GH_AUTH_HEADER" "$url")
   echo "Release response: $response"
   url="https://api.github.com/repos/$TRAVIS_REPO_SLUG/releases/tags/$TRAVIS_TAG"
   echo "verify $url"
   response=$(curl --silent --header "$GH_AUTH_HEADER" "$url")
   echo "$response"
   eval $(echo "$response" | grep -m 1 "id.:" | grep -w id | tr : = | tr -cd '[[:alnum:]]=')
   echo "id = $id"
   for filename in docs/_build/artifacts/*; do
       url="https://uploads.github.com/repos/$TRAVIS_REPO_SLUG/releases/$id/assets?name=$(basename $filename)"
       echo "Uploading $filename as release asset to $url"
       response=$(curl "$GITHUB_OAUTH_BASIC" --data-binary @"$filename" --header "$GH_AUTH_HEADER" --header "Content-Type: application/octet-stream" "$url")
       echo "Uploaded $filename: $response"
        case "$filename" in
            *.zip)  filelabel="html";;
            *.epub) filelabel="epub";;
            *.pdf)  filelabel="pdf";;
            *)      echo "Unknown type $filename";;
        esac
       echo $response | python -c 'import json,sys;print(json.load(sys.stdin)["browser_download_url"])' | sed "s/^/[$filelabel]: /" >> docs/_build/html/_downloads
   done



.. _Read the Docs: https://github.com/readthedocs/readthedocs.org
.. _Github Releases: https://help.github.com/en/github/administering-a-repository/creating-releases
.. _artifactbuildsnippet: https://github.com/goerz/doctr_versions_menu/blob/ecc84be68f15e74f4b09ece3bbf8fda343dee184/.travis/doctr_build.sh#L42-L65
.. _texlive: https://www.tug.org/texlive/
.. _Bintray: https://bintray.com
