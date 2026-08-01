#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Check that .claude-plugin/marketplace.json mirrors the canonical community index.

The canonical Claude Code marketplace for the org lives in
https://github.com/open-agent-ai-security/plugins; this repo keeps an in-repo
mirror so installs added from the legacy path (open-agent-ai-security/praxen)
keep updating. The two files may differ in exactly three places:

  - the praxen entry's ``source`` ("./" here vs a pinned git URL there);
  - the praxen entry's ``version`` (required here by build.sh's version guard;
    absent there, where each plugin repo's plugin.json is the version
    authority);
  - ``metadata`` prose (the mirror says it is a mirror).

Everything else fails closed: entries are compared by FULL equality after
excluding only those exemptions, and the top level likewise (full equality
minus ``metadata`` and the per-entry-compared ``plugins``), so a field the
canonical index grows later (a version, a homepage, a new top-level key)
surfaces as drift instead of slipping through an allow-list. The praxen
``source`` exemption is asymmetric: the mirror's ``./`` is ignored, but the
CANONICAL praxen source — where users' installs actually clone from — must
equal the expected pin exactly.

Usage: check_marketplace_mirror.py [--canonical PATH_OR_URL]
Exit 0 in sync, 1 on drift, 2 on fetch/parse/structure failure.
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
# The one canonical field exempted from mirror comparison is also the most
# security-relevant one for this repo's own plugin — pin it explicitly.
EXPECTED_CANONICAL_PRAXEN_SOURCE = {
    "source": "url",
    "url": "https://github.com/open-agent-ai-security/praxen.git",
    "ref": "main",
}


def load_canonical(ref: str):
    if ref.startswith(("http://", "https://")):
        with urllib.request.urlopen(ref, timeout=30) as resp:
            return json.load(resp)
    return json.loads(Path(ref).read_text())


def entries_by_name(manifest, label: str):
    """Index plugins by name, or raise ValueError on structural problems."""
    plugins = manifest.get("plugins")
    if not isinstance(plugins, list):
        raise ValueError(f"{label}: 'plugins' is not a list")
    by_name = {}
    for i, e in enumerate(plugins):
        if not isinstance(e, dict) or not isinstance(e.get("name"), str) or not e["name"]:
            raise ValueError(f"{label}: plugins[{i}] lacks a non-empty string 'name'")
        if e["name"] in by_name:
            raise ValueError(f"{label}: duplicate plugin name {e['name']!r}")
        by_name[e["name"]] = e
    return by_name


def normalized(name: str, entry: dict, is_mirror: bool) -> dict:
    """Strip exactly the documented mirror exemptions before comparing."""
    e = dict(entry)
    if name == "praxen":
        e.pop("source", None)  # './' here vs pinned git URL there — by design
        if is_mirror:
            e.pop("version", None)  # required here (build.sh guard), absent there
    return e


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
        c_by_name = entries_by_name(canonical, "canonical")
        m_by_name = entries_by_name(mirror, "mirror")
    except Exception as e:  # fetch/parse/structure problems are not "drift"
        print(f"error: could not load manifests: {e}", file=sys.stderr)
        return 2

    drift = []
    c_top = {k: v for k, v in canonical.items() if k not in ("metadata", "plugins")}
    m_top = {k: v for k, v in mirror.items() if k not in ("metadata", "plugins")}
    for field in sorted(set(c_top) | set(m_top)):
        if c_top.get(field) != m_top.get(field):
            drift.append(
                f"marketplace {field}: canonical {c_top.get(field)!r} "
                f"vs mirror {m_top.get(field)!r}"
            )

    c_praxen_src = (c_by_name.get("praxen") or {}).get("source")
    if c_praxen_src is not None and c_praxen_src != EXPECTED_CANONICAL_PRAXEN_SOURCE:
        drift.append(
            f"canonical praxen source deviates from the expected pin: "
            f"{c_praxen_src!r} != {EXPECTED_CANONICAL_PRAXEN_SOURCE!r}"
        )

    if set(c_by_name) != set(m_by_name):
        drift.append(
            f"plugin sets differ: canonical {sorted(c_by_name)} vs mirror {sorted(m_by_name)}"
        )

    for name in sorted(set(c_by_name) & set(m_by_name)):
        c = normalized(name, c_by_name[name], is_mirror=False)
        m = normalized(name, m_by_name[name], is_mirror=True)
        if c == m:
            continue
        for field in sorted(set(c) | set(m)):
            if c.get(field) != m.get(field):
                drift.append(
                    f"{name}.{field}: canonical {c.get(field)!r} vs mirror {m.get(field)!r}"
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
