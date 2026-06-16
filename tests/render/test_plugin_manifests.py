#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Self-contained structural checks for the plugin manifests (no pytest):

    python3 tests/render/test_plugin_manifests.py

These guard the install path that no other automated test covers. The Claude
Code marketplace + plugin manifests and the Codex plugin manifest are validated
by Claude Code's own marketplace schema, which CI does not run — so a bad
`source` field or a version drift here silently breaks `claude plugin install`
at release time. That is exactly how the bare-`"."` source shipped in v0.6.1 and
broke marketplace install for every tagged release until 0.6.2. This encodes the
known requirements so a regression fails the PR instead of the release.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
CLAUDE_PLUGIN = REPO_ROOT / ".claude-plugin" / "plugin.json"
CODEX_PLUGIN = REPO_ROOT / ".codex-plugin" / "plugin.json"
SPEC = REPO_ROOT / "PRAXEN_SPEC.md"

SEMVER = re.compile(r"^\d+\.\d+\.\d+")

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


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as e:  # noqa: BLE001 — any parse/IO error is a failure to report
        return None, str(e)


def summary():
    print(f"\n{_passed} passed, {_failed} failed")
    return 1 if _failed else 0


def main():
    mp, e1 = load(MARKETPLACE)
    cp, e2 = load(CLAUDE_PLUGIN)
    xp, e3 = load(CODEX_PLUGIN)
    check("marketplace.json is valid JSON", mp is not None, e1 or "")
    check(".claude-plugin/plugin.json is valid JSON", cp is not None, e2 or "")
    check(".codex-plugin/plugin.json is valid JSON", xp is not None, e3 or "")
    if not (mp and cp and xp):
        return summary()

    plugins = mp.get("plugins")
    check("marketplace has a non-empty plugins array",
          isinstance(plugins, list) and len(plugins) >= 1)
    entry = plugins[0] if isinstance(plugins, list) and plugins else {}
    src = entry.get("source")

    # The v0.6.1 install-breaker guard: a bare "." source parses fine but breaks
    # `claude plugin install`. Must be a repo-relative path ("./", not ".").
    check("marketplace plugin source is present and a string", isinstance(src, str), repr(src))
    check('marketplace plugin source is NOT the bare "." (the v0.6.1 install-breaker)',
          src != ".", f'source={src!r} — use "./", not "."')
    check("marketplace plugin source is a repo-relative path (./ or ../)",
          isinstance(src, str) and (src.startswith("./") or src.startswith("../")), repr(src))

    # Required keys.
    check("marketplace has name + owner + metadata.version",
          bool(mp.get("name") and mp.get("owner") and (mp.get("metadata") or {}).get("version")))
    for label, m in (("claude plugin.json", cp), ("codex plugin.json", xp)):
        check(f"{label} has name + version + skills",
              bool(m.get("name") and m.get("version") and m.get("skills")))
    iface = xp.get("interface") or {}
    check("codex plugin.json has interface.displayName + shortDescription",
          bool(iface.get("displayName") and iface.get("shortDescription")))
    for e in (plugins if isinstance(plugins, list) else []):
        check(f"marketplace plugin {e.get('name')!r} has name + source + version",
              bool(e.get("name") and e.get("source") and e.get("version")))

    # Name consistency across the three manifests.
    check("plugin name 'praxen' is consistent across the three manifests",
          cp.get("name") == "praxen" and xp.get("name") == "praxen" and entry.get("name") == "praxen",
          f"claude={cp.get('name')} codex={xp.get('name')} marketplace={entry.get('name')}")

    # Version consistency — the 4-way guard build.sh enforces, here as a unit test
    # (so it runs on every PR, even when build.sh's docs-freshness path is skipped).
    # Capture the full version INCLUDING any SemVer pre-release suffix (e.g.
    # 1.0.0-rc.1). A numeric-only capture silently drops the suffix and makes
    # this agreement check fail spuriously the moment we ship a release
    # candidate — build.sh reads the whole string, so the test must too.
    m = re.search(r"\*\*Version:\*\*\s*([0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?)",
                  SPEC.read_text(encoding="utf-8"))
    spec_ver = m.group(1) if m else None

    # README release pill is a STATIC shields badge (no GitHub-API dependency, so
    # it can't error or lag) — but a static badge can drift, so the version it
    # displays must agree with the manifests too. shields escapes a literal '-'
    # in the badge message as '--', e.g. release-v1.0.0--rc.1-blue → 1.0.0-rc.1.
    # Match badge/release-v<message>-<color>) : non-greedy message up to the
    # color segment, any alnum color (named or hex), anchored on the markdown
    # ')' so a greedy capture can't bleed into the link URL's own hyphens.
    README = REPO_ROOT / "README.md"
    rb = re.search(r"img\.shields\.io/badge/release-v(.+?)-[A-Za-z0-9]+\)",
                   README.read_text(encoding="utf-8"))
    readme_ver = rb.group(1).replace("--", "-") if rb else None

    versions = {
        "claude plugin.json": cp.get("version"),
        "codex plugin.json": xp.get("version"),
        "marketplace plugins[0]": entry.get("version"),
        "marketplace metadata": (mp.get("metadata") or {}).get("version"),
        "PRAXEN_SPEC.md": spec_ver,
        "README release badge": readme_ver,
    }
    check("all manifest versions + PRAXEN_SPEC.md + README badge agree",
          None not in versions.values() and len(set(versions.values())) == 1,
          f"versions={versions}")
    check("version is semver (MAJOR.MINOR.PATCH)",
          all(v and SEMVER.match(v) for v in versions.values()),
          f"versions={versions}")

    # License + the skills path actually resolving to the real skill.
    check("license is Apache-2.0 across the plugin manifests",
          cp.get("license") == "Apache-2.0" and xp.get("license") == "Apache-2.0"
          and entry.get("license") == "Apache-2.0")
    skill_dir = REPO_ROOT / "skills" / "behavior-verifier"
    check("the skills/ path resolves to the real behavior-verifier skill",
          skill_dir.is_dir() and (skill_dir / "SKILL.md").is_file())

    return summary()


if __name__ == "__main__":
    sys.exit(main())
