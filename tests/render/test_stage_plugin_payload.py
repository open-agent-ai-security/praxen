#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Regression tests for scripts/release/stage_plugin_payload.sh.

The stager produces the vendored plugin payload the community catalog
installs (plugins repo, "source": "./<dir>"). A silent staging defect ships
a broken or bloated install to every catalog user, so the packaging step is
tested like code:

  - a fresh stage succeeds and contains exactly the distribution allowlist
    minus zip-only entries, minus the legacy marketplace mirror;
  - the skill's runtime shape holds (SKILL.md's ../../WORKER_REMIT_template.md
    and manifest_to_findings.py's ../../.claude-plugin/plugin.json resolve);
  - no cruft, no zip-only dirs, no symlinks (the catalog validator rejects
    symlinks), no tests/;
  - --check passes against a fresh stage and fails once a byte drifts;
  - the shared manifest's entries all exist in the repo (a typo'd allowlist
    line otherwise degrades to a silent "skip (missing)");
  - build.sh and the stager read the same manifest file (the single-source
    point of the design).

Stdlib only, same check/print harness as the other tests here.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STAGER = REPO / "scripts" / "release" / "stage_plugin_payload.sh"
MANIFEST = REPO / "scripts" / "release" / "dist_manifest.txt"

failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        failures.append(name)
        print(f"  FAIL {name}" + (f"  — {detail}" if detail else ""))


def run(*args):
    return subprocess.run(["bash", str(STAGER), *args], capture_output=True, text=True)


def manifest_entries():
    entries = []
    for line in MANIFEST.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        entries.append((parts[0], parts[1] if len(parts) > 1 else ""))
    return entries


def main():
    print("stage_plugin_payload tests")

    entries = manifest_entries()
    check("dist_manifest.txt parses to a non-empty allowlist", bool(entries))
    for path, tag in entries:
        check(f"manifest entry {path!r} exists in the repo", (REPO / path).exists())
        check(f"manifest entry {path!r} tag is empty or zip-only",
              tag in ("", "zip-only"), f"got {tag!r}")

    build_sh = (REPO / "build.sh").read_text()
    check("build.sh reads the shared manifest (no fork of the allowlist)",
          "dist_manifest.txt" in build_sh and not re.search(r'INCLUDE=\(\s*"', build_sh))

    with tempfile.TemporaryDirectory() as td:
        dest = Path(td) / "payload"

        r = run(str(dest))
        check("fresh stage exits 0", r.returncode == 0, (r.stdout + r.stderr).strip()[:300])

        expected = {p for p, tag in entries if tag != "zip-only"}
        staged_top = {p.name for p in dest.iterdir()}
        check("staged top level == manifest minus zip-only",
              staged_top == expected,
              f"missing={sorted(expected - staged_top)} extra={sorted(staged_top - expected)}")

        for banned, why in [
            ("graphics", "zip-only"), ("examples", "zip-only"), ("tests", "never shipped"),
        ]:
            check(f"no {banned}/ in payload ({why})", not (dest / banned).exists())
        check("legacy marketplace mirror removed",
              not (dest / ".claude-plugin" / "marketplace.json").exists())
        check("no bytecode/cruft in payload",
              not any(dest.rglob("__pycache__")) and not any(dest.rglob("*.pyc"))
              and not any(dest.rglob(".DS_Store")))
        check("no symlinks in payload (catalog validator rejects them)",
              not any(p.is_symlink() for p in dest.rglob("*")))

        # Runtime shape: the two out-of-skill lookups the engine actually makes.
        skill = dest / "skills" / "behavior-verifier" / "SKILL.md"
        check("skill present", skill.is_file())
        check("../../WORKER_REMIT_template.md resolves from the skill",
              (skill.parent / ".." / ".." / "WORKER_REMIT_template.md").resolve().is_file())
        check("../../.claude-plugin/plugin.json resolves from the skill",
              (skill.parent / ".." / ".." / ".claude-plugin" / "plugin.json").resolve().is_file())

        pj = json.loads((dest / ".claude-plugin" / "plugin.json").read_text())
        xj = json.loads((dest / ".codex-plugin" / "plugin.json").read_text())
        check("payload manifests agree on name and version",
              pj.get("name") == xj.get("name") and pj.get("version") == xj.get("version"),
              f"claude={pj.get('name')}@{pj.get('version')} codex={xj.get('name')}@{xj.get('version')}")
        check("payload version is semver (prerelease allowed)",
              bool(re.match(r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?$", pj.get("version") or "")))

        r = run("--check", str(dest))
        check("--check passes against a fresh stage", r.returncode == 0,
              (r.stdout + r.stderr).strip()[:300])

        r = run(str(dest))
        check("re-stage into non-empty dest refuses without --force", r.returncode != 0)

        (dest / "skills" / "behavior-verifier" / "SKILL.md").write_text("drifted")
        r = run("--check", str(dest))
        check("--check fails once a payload byte drifts", r.returncode != 0)

        r = run("--force", str(dest))
        check("--force restage exits 0", r.returncode == 0)
        check("--force restage heals the drift",
              (dest / "skills" / "behavior-verifier" / "SKILL.md").read_text() != "drifted")

    print()
    if failures:
        print(f"{len(failures)} FAILED")
        return 1
    print("all passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
