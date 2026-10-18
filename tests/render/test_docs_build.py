#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Smoke tests for docs_build.py — the docs-site generator.

No pytest dependency — run directly:

    python3 tests/render/test_docs_build.py

docs_build.py had no tests. The docs-freshness CI job only regenerates
`guide/` and diffs it, which cannot notice a change that regenerates
*consistently* — deleting the Mermaid font gate (#264) passes that job
cleanly, and the only symptom is clipped diagram labels on the published
site, which nothing automated looks at.

Imports only the module's constants, so it needs no `markdown` package and
runs on the dependency-free CI test job.
"""
from __future__ import annotations

import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GUIDE = os.path.join(REPO_ROOT, "guide")
sys.path.insert(0, REPO_ROOT)

_passed = 0
_failed = 0


def check(name, cond, detail=""):
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  ok   {name}")
    else:
        _failed += 1
        print(f"  FAIL {name}" + (f"  — {detail}" if detail else ""))


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def main():
    # Pull the constants without importing the module: docs_build imports
    # `markdown`, which the CI test job deliberately does not install.
    src = read(os.path.join(REPO_ROOT, "docs_build.py"))
    m = re.search(r'MERMAID_SCRIPT = f"""(.*?)"""', src, re.S)
    check("docs_build.py defines MERMAID_SCRIPT", bool(m))
    if not m:
        print(f"\n{_passed} passed, {_failed} failed")
        sys.exit(1)
    script = m.group(1)

    print("\n1. The Mermaid font gate (#264)")
    # Mermaid sizes nodes by measuring label text. Drawing before the web font
    # loads measures the fallback face, so every label overflows its box once
    # Inter swaps in and is clipped by its last glyph. Each assertion below is
    # one load-bearing piece of the gate; losing any of them brings #264 back.
    check("run() is not called unconditionally at top level",
          not re.search(r'^\s*mermaid\.run\(', script, re.M),
          "an unguarded mermaid.run() draws before the font is available")
    check("rendering is gated on the Font Loading API",
          "document.fonts" in script and "fonts.ready" in script)
    check("the gate degrades when the API is absent",
          re.search(r'if \(!document\.fonts[^)]*\) \{\{? ?run\(\)', script) is not None,
          "a browser without document.fonts must still get a diagram")
    check("a deadline guarantees a render even if the font never arrives",
          "setTimeout" in script and "Promise.race" in script,
          "a blocked font CDN would leave a bare code block")
    check("a deadline render is redrawn once the font lands",
          "redraw" in script and "data-processed" in script,
          "rendering early in the fallback face and never redrawing is #264 "
          "again, just delayed")
    check("the measured faces match Mermaid's configured fontFamily",
          "Inter" in script and re.search(r"fontFamily:\s*'\"Inter\"", script) is not None)

    print("\n2. Every generated page carrying a diagram carries the gate")
    pages = sorted(f for f in os.listdir(GUIDE) if f.endswith(".html"))
    check("found generated guide pages", bool(pages))
    with_diagram = [f for f in pages if 'pre class="mermaid"' in read(os.path.join(GUIDE, f))]
    check("at least one generated page carries a diagram", bool(with_diagram),
          "if the docs lose every diagram this test stops proving anything")
    missing = [f for f in with_diagram
               if "document.fonts" not in read(os.path.join(GUIDE, f))]
    check(f"all {len(with_diagram)} diagram page(s) embed the font gate",
          not missing, f"ungated: {missing}")
    # The inverse: a page with no diagram should not be carrying the runtime.
    stray = [f for f in pages
             if f not in with_diagram and "mermaid.min.js" in read(os.path.join(GUIDE, f))]
    check("pages without a diagram do not load the Mermaid runtime",
          not stray, f"needless runtime on: {stray}")

    print(f"\n{_passed} passed, {_failed} failed")
    sys.exit(1 if _failed else 0)


if __name__ == "__main__":
    main()
