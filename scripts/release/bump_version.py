#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Bump Praxen's version everywhere it lives, in one shot.

The version lives in SIX coupled places, and until now every one of them was
edited by hand — usually while cutting a release under time pressure. The
guards (`build.sh`'s four-way check, `tests/render/test_plugin_manifests.py`)
catch drift, but only *after* a half-edited bump is already sitting in a PR.
This script makes the bump one command and demotes the guards to a backstop:

  - ``PRAXEN_SPEC.md``                    → ``**Version:** X.Y.Z`` (the
    authority ``build.sh`` and ``release.yml`` read; ships in the zip)
  - ``.claude-plugin/plugin.json``        → ``version``
  - ``.claude-plugin/marketplace.json``   → the **praxen** entry's ``version``
    (looked up BY NAME — the mirror lists other plugins that deliberately
    carry no version) and ``metadata.version``
  - ``.codex-plugin/plugin.json``         → ``version``
  - ``README.md``                         → the static shields release badge
    (a literal ``-`` in a prerelease is escaped ``--`` per shields rules)

Then it re-verifies every surface by parsing — the same checks the invariant
tests enforce — so CI stays green. It does NOT commit; review the diff, add
the CHANGELOG entry, and open a PR yourself.

Ported from socxen's ``scripts/bump_version.py`` (same shape: edit,
verify-all-surfaces, print next steps, never commit). Praxen has no AI-BOM to
regenerate; its only derived surface would be ``guide/`` via
``docs_build.py``, and only if a version string appeared in
``docs/*.md`` — it doesn't today, but the script warns if that changes.

Usage:
    python3 scripts/release/bump_version.py 1.2.1
    python3 scripts/release/bump_version.py 1.2.1 --dry-run
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SPEC = ROOT / "PRAXEN_SPEC.md"
CLAUDE_PLUGIN = ROOT / ".claude-plugin/plugin.json"
MARKETPLACE = ROOT / ".claude-plugin/marketplace.json"
CODEX_PLUGIN = ROOT / ".codex-plugin/plugin.json"
README = ROOT / "README.md"
DOCS_DIR = ROOT / "docs"

SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(1)


def _sub_once(text, pattern, repl, what):
    new, n = re.subn(pattern, repl, text, count=1)
    if n != 1:
        fail(f"{what}: expected exactly 1 match, found {n} — file layout may have changed")
    return new


def _badge(version):
    # shields escapes a literal '-' in the badge message as '--'
    # (release-v1.2.1--rc.1-blue → "1.2.1-rc.1")
    return version.replace("-", "--")


def main(argv):
    positional = [a for a in argv if not a.startswith("-")]
    dry = "--dry-run" in argv or "-n" in argv
    if len(positional) != 1 or not SEMVER.match(positional[0]):
        fail("usage: bump_version.py X.Y.Z[-prerelease] [--dry-run]")
    new = positional[0]
    old = json.loads(CLAUDE_PLUGIN.read_text())["version"]
    if old == new:
        fail(f"version is already {new}")

    # Preconditions on the marketplace mirror, checked by PARSING (not regex):
    # the praxen entry and metadata must both sit at `old`, and no OTHER entry
    # may carry a version at all — the mirror's non-praxen entries deliberately
    # omit it, and a stray one would make the textual edit below ambiguous.
    m = json.loads(MARKETPLACE.read_text())
    entries = {p.get("name"): p for p in m.get("plugins", [])}
    if "praxen" not in entries:
        fail("marketplace.json has no praxen entry")
    if entries["praxen"].get("version") != old:
        fail(f"marketplace.json praxen entry is at {entries['praxen'].get('version')!r}, expected {old!r}")
    if (m.get("metadata") or {}).get("version") != old:
        fail(f"marketplace.json metadata.version is {(m.get('metadata') or {}).get('version')!r}, expected {old!r}")
    strays = [n for n, p in entries.items() if n != "praxen" and "version" in p]
    if strays:
        fail(f"marketplace.json entries other than praxen carry a version ({strays}) — update this script's edit logic first")

    print(f"bump {old} -> {new}" + ("  (dry run — no files written)" if dry else ""))

    ver_pat = r'("version"\s*:\s*")' + re.escape(old) + r'(")'
    ver_repl = r"\g<1>" + new + r"\g<2>"

    # marketplace.json holds `old` in exactly two places (entry + metadata),
    # proven by the parse above — so replace both, and demand exactly 2.
    market_text, n = re.subn(ver_pat, ver_repl, MARKETPLACE.read_text())
    if n != 2:
        fail(f"marketplace.json: expected exactly 2 version fields at {old}, found {n}")

    edits = [
        (SPEC, _sub_once(SPEC.read_text(),
                         r"(\*\*Version:\*\*[ \t]*)" + re.escape(old),
                         r"\g<1>" + new, "PRAXEN_SPEC.md version line")),
        (CLAUDE_PLUGIN, _sub_once(CLAUDE_PLUGIN.read_text(), ver_pat, ver_repl,
                                  ".claude-plugin/plugin.json version")),
        (MARKETPLACE, market_text),
        (CODEX_PLUGIN, _sub_once(CODEX_PLUGIN.read_text(), ver_pat, ver_repl,
                                 ".codex-plugin/plugin.json version")),
        (README, _sub_once(README.read_text(),
                           r"(badge/release-v)" + re.escape(_badge(old)) + r"(-)",
                           r"\g<1>" + _badge(new) + r"\g<2>", "README release badge")),
    ]

    if dry:
        for path, _ in edits:
            print(f"  would edit {path.relative_to(ROOT)}")
        return 0

    for path, content in edits:
        path.write_text(content)
        print(f"  edited {path.relative_to(ROOT)}")

    # Verify every surface by parsing — mirrors test_plugin_manifests.py, so a
    # surface this script forgets shows up HERE, not in CI. (Lesson from
    # socxen: when a surface changes, the verify block must move with the edit
    # block — its bump once crashed post-write on a stale verify reference.)
    m = json.loads(MARKETPLACE.read_text())
    rb = re.search(r"img\.shields\.io/badge/release-v(.+?)-[A-Za-z0-9]+\)", README.read_text())
    sv = re.search(r"^\*\*Version:\*\*[ \t]*(\S+)", SPEC.read_text(), flags=re.MULTILINE)
    got = {
        "PRAXEN_SPEC.md": sv.group(1) if sv else None,
        "claude plugin.json": json.loads(CLAUDE_PLUGIN.read_text()).get("version"),
        "marketplace praxen entry": next((p.get("version") for p in m.get("plugins", [])
                                          if p.get("name") == "praxen"), None),
        "marketplace metadata": (m.get("metadata") or {}).get("version"),
        "codex plugin.json": json.loads(CODEX_PLUGIN.read_text()).get("version"),
        "README release badge": rb.group(1).replace("--", "-") if rb else None,
    }
    mismatch = {k: v for k, v in got.items() if v != new}
    if mismatch:
        fail(f"post-bump mismatch (expected {new}): {mismatch}")
    print(f"\n✓ all 6 version surfaces at {new}")

    # Derived-surface tripwire: guide/ is built from docs/*.md, which today
    # carries no version strings. If one appears, the bump must also rebuild
    # guide/ (docs_build.py) — warn rather than silently skip.
    hits = [p.name for p in sorted(DOCS_DIR.glob("*.md")) if old in p.read_text()]
    if hits:
        print(f"  warning: old version {old} still appears in docs/ ({', '.join(hits)}) — "
              "fix by hand and rebuild guide/ (docs_build.py)", file=sys.stderr)

    print("\nnext: add the CHANGELOG entry, review the diff, run ./build.sh, and open a PR to dev.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
