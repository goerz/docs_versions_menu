#!/usr/bin/env python
import os
import subprocess
from pathlib import Path

from versions import get_versions_data, write_versions_json


INDEX_HTML = r'''<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="Refresh" content="0; url={default_branch}" />
  </head>
  <body>
    <p>Got to <a href="{default_branch}">default documentation</a>.</p>
  </body>
</html>
'''


def write_index_html(default_branch):
    """Write an index.html that redirects to the DEFAULT_BRANCH."""
    with open("index.html", "w") as out_fh:
        out_fh.write(INDEX_HTML.format(default_branch=default_branch))
    subprocess.run(['git', 'add', 'index.html'], check=True)


def ensure_no_jekyll():
    """Create a .nojekyll file.

    This prevents Github from messing with folders that start with an
    underscore.
    """
    Path('.jekyll').touch()
    subprocess.run(['git', 'add', '.jekyll'], check=True)


def find_downloads(folder):
    """Find artifact links in _downloads file.

    The _downloads file should be created by the doctr_build.sh script.
    If no _downloads file exists, return an empty list.
    """
    downloads = []
    try:
        with open(Path(folder) / "_downloads") as in_fh:
            for url in in_fh:
                url = url.strip()
                label = url.split(".")[-1].lower()
                print("For %s, download link %r => %r" % (folder, label, url))
                downloads.append((label, url))
    except IOError:
        print("WARNING: $%s contains no _downloads" % folder)
    return downloads


def main():
    """Main function."""
    print("Post-processing documentation on gh-pages")
    subprocess.run(['git', 'add', __file__], check=True)
    subprocess.run(['git', 'add', 'versions.py'], check=True)
    print("Gather versions info")
    versions_data = get_versions_data(find_downloads=find_downloads)
    latest_release = versions_data['latest_release']
    if latest_release is None:
        latest_release = 'master'
    print("Write index.html")
    write_index_html(latest_release)
    ensure_no_jekyll()
    print("Write versions.json")
    write_versions_json(versions_data, outfile='versions.json')
    print("DONE post-processing")


if __name__ == "__main__":
    main()
