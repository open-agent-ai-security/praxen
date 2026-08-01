#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Check that .claude-plugin/marketplace.json mirrors the canonical community index.

The canonical Claude Code marketplace for the org lives in
https://github.com/open-agent-ai-security/plugins; this repo keeps an in-repo
mirror so installs added from the legacy path (open-agent-ai-security/praxen)
keep updating. The two files differ by design in exactly two ways:

  - the praxen entry's ``source`` ("./" here vs a pinned git URL there) and
    ``version`` (required here by build.sh's version guard; absent there,
    where each plugin repo's plugin.json is the version authority);
  - ``metadata`` prose (the mirror says it is a mirror).

Everything users actually see must match: the marketplace name, the set of
plugin names, and each entry's description, license, keywords, and category.
Non-praxen entries must also match on source, so a drifted pin is caught.

Usage: check_marketplace_mirror.py [--canonical PATH_OR_URL]
Exit 0 in sync, 1 on drift, 2 on fetch/parse failure.
"""
import json
import sys
import urllib.request
from pathlib import Path

CANONICAL_URL = (
    "https://raw.githubusercontent.com/open-agent-ai-security/plugins/"
    "main/.claude-plugin/marketplace.json"
)
MIRROR_PATH = Path(__file__).resolve().parents[2] / ".claude-plugin" / "marketplace.json"
COMPARED_FIELDS = ("description", "license", "keywords", "category")


def load_canonical(ref: str):
    if ref.startswith(("http://", "https://")):
        with urllib.request.urlopen(ref, timeout=30) as resp:
            return json.load(resp)
    return json.loads(Path(ref).read_text())


def main() -> int:
    ref = CANONICAL_URL
    if len(sys.argv) == 3 and sys.argv[1] == "--canonical":
        ref = sys.argv[2]
    elif len(sys.argv) != 1:
        print(__doc__)
        return 2

    try:
        canonical = load_canonical(ref)
        mirror = json.loads(MIRROR_PATH.read_text())
    except Exception as e:  # fetch/parse problems are not "drift"
        print(f"error: could not load manifests: {e}", file=sys.stderr)
        return 2

    drift = []
    if canonical.get("name") != mirror.get("name"):
        drift.append(
            f"marketplace name: canonical {canonical.get('name')!r} "
            f"vs mirror {mirror.get('name')!r}"
        )

    c_by_name = {p["name"]: p for p in canonical.get("plugins", [])}
    m_by_name = {p["name"]: p for p in mirror.get("plugins", [])}
    if set(c_by_name) != set(m_by_name):
        drift.append(
            f"plugin sets differ: canonical {sorted(c_by_name)} vs mirror {sorted(m_by_name)}"
        )

    for name in sorted(set(c_by_name) & set(m_by_name)):
        c, m = c_by_name[name], m_by_name[name]
        for field in COMPARED_FIELDS:
            if c.get(field) != m.get(field):
                drift.append(
                    f"{name}.{field}: canonical {c.get(field)!r} vs mirror {m.get(field)!r}"
                )
        if name != "praxen" and c.get("source") != m.get("source"):
            drift.append(
                f"{name}.source: canonical {c.get('source')!r} vs mirror {m.get('source')!r}"
            )

    if drift:
        print("marketplace mirror has drifted from the canonical index:")
        for d in drift:
            print(f"  - {d}")
        print(
            "\nfix: align .claude-plugin/marketplace.json with "
            "https://github.com/open-agent-ai-security/plugins (or update the "
            "canonical index first if this repo is the intended change)."
        )
        return 1

    print("marketplace mirror is in sync with the canonical index.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
