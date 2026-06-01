# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Shared helpers for the Praxen baseline coverage-report generators
(owasp_coverage.py and raise_coverage.py)."""
import sys
from pathlib import Path

# tests/baselines/theme_utils.py -> repo root -> assets/praxen-theme.css
THEME_CSS = Path(__file__).resolve().parents[2] / "assets" / "praxen-theme.css"


def load_theme_css() -> str:
    """Return the shared design system (assets/praxen-theme.css) so a coverage
    report can inline it and stay a self-contained single file. Edit that file
    to retheme every surface (both coverage reports and the landing page) from
    one place."""
    try:
        return THEME_CSS.read_text(encoding="utf-8")
    except OSError:
        print(f"theme_utils: warning: shared theme not found at {THEME_CSS}; "
              "report will use report-specific CSS only", file=sys.stderr)
        return ""
