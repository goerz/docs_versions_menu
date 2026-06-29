#!/usr/bin/env python3
"""Validate HISTORY.rst for consistent RST link references.

Checks that every hyperlink reference has a link definition, and reports
definitions that are never referenced. Missing definitions are errors (non-zero
exit); orphaned definitions are warnings only.
"""

# /// script
# requires-python = ">=3.10"
# ///

import re
import sys
from pathlib import Path

HISTORY = Path(__file__).parent.parent / 'HISTORY.rst'

# .. _label:  or  .. _label: URL
RE_DEF = re.compile(r'^\.\. _(.+?):', re.MULTILINE)

# `label`_  (not `label`__ which is anonymous)
RE_BACKTICK_REF = re.compile(r'`([^`<]+)`_(?!_)')

# `Display Text <label_>`_  →  captures label (without trailing _)
RE_INDIRECT_REF = re.compile(r'<([A-Za-z#@][^>]*)_>')

# word_ bare reference (e.g. Travis_, conda-feedstock_)
# Negative lookbehind excludes `<@-` to avoid double-matching inside <@label_>
# spans and hyphenated subwords (e.g. the "feedstock" part of "conda-feedstock_").
RE_BARE_REF = re.compile(
    r'(?<![`<@-])\b([A-Za-z][A-Za-z0-9]*(?:[-_.][A-Za-z0-9]+)*)_(?!\w)'
)


def main():
    text = HISTORY.read_text()

    defs = {m.group(1) for m in RE_DEF.finditer(text)}

    # Strip definition lines and code spans before scanning for references
    body = re.sub(r'^\.\. _.+', '', text, flags=re.MULTILINE)
    body = re.sub(r'``[^`]+``', '', body)

    refs = set()
    for m in RE_BACKTICK_REF.finditer(body):
        refs.add(m.group(1).strip())
    for m in RE_INDIRECT_REF.finditer(body):
        refs.add(m.group(1).strip())
    for m in RE_BARE_REF.finditer(body):
        refs.add(m.group(1))

    ok = True
    for ref in sorted(refs):
        if ref not in defs:
            print(f'ERROR: `{ref}`_ is referenced but has no definition')
            ok = False
    for defn in sorted(defs):
        if defn not in refs:
            print(f'WARNING: .. _{defn}: is defined but never referenced')

    if ok:
        print('HISTORY.rst OK')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
