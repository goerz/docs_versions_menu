#!/usr/bin/env python
"""Lokal pre-commit hook

- no trailing whitespace in any file
- no lines with a "DEBUG" comment in a python file

This can be extended with project-specific checks. You may also consider
third-party hooks available from https://pre-commit.com/hooks.html
"""
import re
import sys
from argparse import ArgumentParser, RawTextHelpFormatter


try:
    from tox.session import load_config
except ImportError:
    print("tox must be available for pre-commit hooks.")
    print("See https://tox.readthedocs.io for installation instructions.")
    sys.exit(1)


def no_trailing_whitespace(filenames):
    """Check that files have no trailing whitespace."""
    success = True
    for filename in filenames:
        with open(filename) as in_fh:
            for (line_index, line) in enumerate(in_fh):
                if line.endswith(" \n"):
                    print(
                        "%s:%d has trailing whitespace"
                        % (filename, line_index + 1)
                    )
                    success = False
    return success


def no_debug_comment(filenames):
    """Check that files have to DEBUG comments."""
    success = True
    for filename in filenames:
        print("Checking %s for debug comments" % filename)
        if filename.endswith(".py"):
            rx_debug = re.compile(r'#\s*DEBUG')
            with open(filename) as in_fh:
                for (line_index, line) in enumerate(in_fh):
                    if rx_debug.search(line):
                        print(
                            "%s:%d has a DEBUG marker comment"
                            % (filename, line_index + 1)
                        )
                        success = False
    return success


CHECKS = {
    'whitespace': no_trailing_whitespace,
    'debug-comments': no_debug_comment,
}


def main(argv=None):
    """Main function"""
    description = "Perform the given CHECK on the given FILENAMES.\n\n"
    description += "The following CHECKs are available:\n\n"
    for (name, check) in CHECKS.items():
        description += "    " + name + ":\n"
        description += "        " + check.__doc__.splitlines()[0] + "\n"
    parser = ArgumentParser(
        description=description, formatter_class=RawTextHelpFormatter
    )
    parser.add_argument('CHECK', help='Name of check')
    parser.add_argument('FILENAMES', nargs='*', help='Filenames to check')
    args = parser.parse_args(argv)

    return_code = 0
    success = True

    check = CHECKS[args.CHECK]
    try:
        success = check(args.FILENAMES)
    except (ValueError, OSError) as exc_info:
        print(
            "Cannot check %s with %s: %s"
            % (args.FILENAMES, args.CHECK, exc_info)
        )
        return_code = 1
    if not success:
        return_code = 1
    return return_code


if __name__ == '__main__':
    sys.exit(main())
