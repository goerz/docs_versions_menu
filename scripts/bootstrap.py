#!/usr/bin/env python
"""Bootstrap script for setting up tox and pre-commit hooks

This scripts is called by invocation of the Makefile.
"""
import os
import pathlib
import shutil
import sys


_TOX_ERR_MSG = r'''
tox is not available. See https://tox.readthedocs.io for installation
instructions.
'''


def main(argv=None):
    """Main function"""
    if argv is None:
        argv = sys.argv
    root = pathlib.Path(__file__).parent.parent

    # Ensure tox is installed
    try:
        import tox
    except ImportError:
        print(_TOX_ERR_MSG)
        sys.exit(1)

    # Ensure pre-commit hooks are installed
    if (root / ".git").is_dir():
        if not (root / ".git" / "hooks" / "pre-commit").is_file():
            # we're using the tox.ini environments that we got from step 1
            print("bootstrapping pre-commit hook")
            cmdline = ['-e', 'run-cmd', '--', 'pre-commit', 'install']
            print("tox " + " ".join(cmdline))
            tox.cmdline(cmdline)


if __name__ == '__main__':
    sys.exit(main())
