# This script is called from travis.yml for the "Docs" job
#
# Actual deployment will only happen if the TRAVIS environment variable is set.
# It is possible to run this script locally (outside of Travis) for a test of
# artifact building by setting only the TRAVIS_TAG variable, e.g.:
#
#   TRAVIS_TAG=v1.0.0-rc1 sh .travis/doctr_build.sh
#
# This will leave artifacts in the docs/_build/artifacts folder.

echo "# DOCTR - deploy documentation"

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

echo "## Generate main html documentation"
tox -e docs

if [ ! -z "$TRAVIS_TAG" ]; then

    echo "Building as tag '$TRAVIS_TAG'"

    echo "## Generate documentation downloads"
    # We generate documentation downloads only for tags (which are assumed to
    # correspond to releases). Otherwise, we'd quickly fill up git with binary
    # artifacts for every single push.
    mkdir docs/_build/artifacts

    # We build the documentation artifacts in the temporary
    # docs/_build/artifacts. These are then deployed to the cloud, and a
    # _download file is written to the main html documentation containing links
    # to all the artifacts. The find_downloads function in doctr_post_process
    # will then later transfer those links into versions.json

    echo "### [zip]"
    cp -r docs/_build/html "docs/_build/doctr_versions_menu-$TRAVIS_TAG"
    cd docs/_build || exit 1
    zip -r "doctr_versions_menu-$TRAVIS_TAG.zip" "doctr_versions_menu-$TRAVIS_TAG"
    rm -rf "doctr_versions_menu-$TRAVIS_TAG"
    cd ../../ || exit 1
    mv "docs/_build/doctr_versions_menu-$TRAVIS_TAG.zip" docs/_build/artifacts/

    echo "### [pdf]"
    tox -e docs -- -b latex _build/latex
    tox -e run-cmd -- python docs/build_pdf.py docs/_build/latex/*.tex
    echo "finished latex compilation"
    mv docs/_build/latex/*.pdf "docs/_build/artifacts/doctr_versions_menu-$TRAVIS_TAG.pdf"

    echo "### [epub]"
    tox -e docs -- -b epub _build/epub
    mv docs/_build/epub/*.epub "docs/_build/artifacts/doctr_versions_menu-$TRAVIS_TAG.epub"

    if [ ! -z "$TRAVIS" ] && [ "$TRAVIS_EVENT_TYPE" != "pull_request" ]; then

        # upload to bintray
        # Depends on $BINTRAY_USER, $BINTRAY_SUBJECT, $BINTRAY_REPO, $BINTRAY_PACKAGE, and secret $BINTRAY_TOKEN from .travis.yml
        echo "Upload artifacts to bintray"
        for filename in docs/_build/artifacts/*; do
            url="https://api.bintray.com/content/$BINTRAY_SUBJECT/$BINTRAY_REPO/$BINTRAY_PACKAGE/$TRAVIS_TAG/$(basename $filename)"
            echo "Uploading $filename artifact to $url"
            response=$(curl --upload-file "$filename" --user "$BINTRAY_USER:$BINTRAY_TOKEN" "$url")
            if [ -z "${response##*success*}" ]; then
                echo "Uploaded $filename: $response"
                echo "https://dl.bintray.com/$BINTRAY_SUBJECT/$BINTRAY_REPO/$(basename $filename)" >> docs/_build/html/_downloads
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

        echo "docs/_build/html/_downloads:"
        cat docs/_build/html/_downloads

        rm -rf docs/_build/artifacts

    fi

elif [ ! -z "$TRAVIS_BRANCH" ]; then

    echo "Building as branch '$TRAVIS_BRANCH'"

else

    echo "At least one of TRAVIS_TAG and TRAVIS_BRANCH must be set"
    sync
    exit 1

fi

# Deploy
if [ ! -z "$TRAVIS" ] && [ "$TRAVIS_EVENT_TYPE" != "pull_request" ]; then
    echo "## pip install doctr"
    python -m pip install doctr
    echo "## doctr deploy"
    if [ ! -z "$TRAVIS_TAG" ]; then
        DEPLOY_DIR="$TRAVIS_TAG"
    else
        case "$TRAVIS_BRANCH" in
            master|develop) DEPLOY_DIR="$TRAVIS_BRANCH";;
            *)      echo "Not deploying branch $TRAVIS_BRANCH (not in whitelist)";;
        esac
    fi
    if [ ! -z "$DEPLOY_DIR" ]; then
        python -m doctr deploy --key-path docs/doctr_deploy_key.enc \
            --command="git show $TRAVIS_COMMIT:.travis/doctr_post_process.py > post_process.py && git show $TRAVIS_COMMIT:.travis/versions.py > versions.py && python post_process.py" \
            --built-docs docs/_build/html --no-require-master --build-tags "$DEPLOY_DIR"
    fi
else
    echo "Not deploying to gh-pages (PR or not on Travis)"
fi

echo "# DOCTR - DONE"
