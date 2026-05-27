#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Self-contained smoke tests for the Praxen Step 9.9 → Step 10 converter
(`manifest_to_findings.py` + `schema.py`).

No pytest dependency — run directly:

    python3 tests/render/test_manifest_to_findings.py

Covers:
  * happy-path round-trip: helperbot manifest fixture → byte-identical golden JSON
  * parser output is deterministic across reruns
  * parser output passes schema.validate
  * parser output renders cleanly through render.py
  * negative cases: missing section, bad format version, heading/id disagreement,
    malformed evidence item, unknown field, missing required field
  * value coercion: null for nullable fields, (none)/(empty) markers, booleans, ints
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SKILL_DIR = os.path.join(REPO_ROOT, "skills", "behavior-verifier")
CONVERTER = os.path.join(SKILL_DIR, "manifest_to_findings.py")
RENDER_PY = os.path.join(SKILL_DIR, "render.py")
TEMPLATE = os.path.join(SKILL_DIR, "report_template.html")
FIXTURE_DIR = os.path.join(REPO_ROOT, "tests", "fixtures")
MANIFEST = os.path.join(FIXTURE_DIR, "helperbot.manifest.md")
GOLDEN_JSON = os.path.join(FIXTURE_DIR, "helperbot.from_manifest.json")

sys.path.insert(0, SKILL_DIR)
import schema  # noqa: E402
import manifest_to_findings as m2f  # noqa: E402

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


def run_converter(manifest_path, out_path):
    return subprocess.run(
        [sys.executable, CONVERTER, "--manifest", manifest_path, "--out", out_path],
        capture_output=True, text=True)


def read_text(path):
    return Path(path).read_text(encoding="utf-8")


def read_bytes(path):
    return Path(path).read_bytes()


def assert_parse_error(label, manifest_text, expected_substring):
    """Run the parser on `manifest_text`; check that it raises ManifestError
    whose message contains `expected_substring`."""
    try:
        m2f.parse_manifest(manifest_text)
    except m2f.ManifestError as e:
        ok = expected_substring in str(e)
        check(label, ok, f"got {e!r}, expected substring {expected_substring!r}")
        return
    except Exception as e:
        check(label, False, f"raised wrong exception: {e!r}")
        return
    check(label, False, "no exception raised")


# ── 1. Happy path: golden round-trip ────────────────────────────────────────
print("1. Happy path: golden round-trip")
with tempfile.TemporaryDirectory() as td:
    out = os.path.join(td, "out.json")
    res = run_converter(MANIFEST, out)
    check("converter exits 0", res.returncode == 0, res.stderr or res.stdout)
    actual_bytes = read_bytes(out)
    golden_bytes = read_bytes(GOLDEN_JSON)
    check("output bytes match golden", actual_bytes == golden_bytes,
          f"actual_len={len(actual_bytes)} golden_len={len(golden_bytes)}")

# ── 2. Determinism: rerun produces identical output ─────────────────────────
print("\n2. Determinism")
with tempfile.TemporaryDirectory() as td:
    a = os.path.join(td, "a.json")
    b = os.path.join(td, "b.json")
    run_converter(MANIFEST, a)
    run_converter(MANIFEST, b)
    check("two consecutive runs are byte-identical",
          read_bytes(a) == read_bytes(b))

# ── 3. Parser output validates against schema.py ────────────────────────────
print("\n3. Schema validation")
data = json.loads(read_text(GOLDEN_JSON))
try:
    schema.validate(data)
    check("golden JSON passes schema.validate", True)
except schema.SchemaError as e:
    check("golden JSON passes schema.validate", False, str(e))

# Cross-checks against the golden's known shape (helperbot has 10 findings, 13 rules).
check("golden has 10 findings", len(data["findings"]) == 10,
      f"got {len(data['findings'])}")
check("golden has 13 rules", len(data["remit_coverage"]["rules"]) == 13,
      f"got {len(data['remit_coverage']['rules'])}")
check("golden has all six RAISE categories",
      len(data["raise_posture"]["categories"]) == 6)

# ── 4. Parser output renders cleanly through render.py ──────────────────────
print("\n4. Render integration")
with tempfile.TemporaryDirectory() as td:
    out_html = os.path.join(td, "out.html")
    out_txt = os.path.join(td, "out.txt")
    res = subprocess.run(
        [sys.executable, RENDER_PY,
         "--findings", GOLDEN_JSON,
         "--template", TEMPLATE,
         "--out-html", out_html,
         "--out-txt", out_txt],
        capture_output=True, text=True)
    check("render.py exits 0", res.returncode == 0, res.stderr or res.stdout)
    if res.returncode == 0:
        html_out = read_text(out_html)
        txt_out = read_text(out_txt)
        check("HTML has no unsubstituted placeholders", "{{" not in html_out,
              "found '{{' in HTML")
        check("HTML mentions agent name", "HelperBot" in html_out)
        check("TXT mentions agent name", "HelperBot" in txt_out)


# ── 5. Value coercion ───────────────────────────────────────────────────────
print("\n5. Value coercion")
# Verify by inspecting the golden directly.
rule_with_null = next(r for r in data["remit_coverage"]["rules"]
                      if r["rule_id"] == "R-08")
check("null finding_id parses to JSON null",
      rule_with_null["finding_id"] is None,
      f"got {rule_with_null['finding_id']!r}")

# artifact_count is an int.
check("artifact_count coerced to int",
      isinstance(data["scan"]["artifact_count"], int))
# weighted_overall is a float.
check("weighted_overall coerced to float",
      isinstance(data["raise_posture"]["weighted_overall"], float))
# log_files.present is a bool (helperbot has present=false).
check("log_files.present coerced to bool",
      isinstance(data["log_files"]["present"], bool))
check("log_files.rows empty when present=false",
      data["log_files"]["rows"] == [])
# helperbot has (none) for positives.
check("(none) positives -> empty array",
      data["positives"] == [])


# ── 5b. Sentinel-string normalization ───────────────────────────────────────
# The LLM might write `"null"` / `"none"` / empty string instead of the
# literal `null` for fields the schema permits to be null. The parser
# normalizes those to JSON null in `_populate_derived` so schema validation
# passes either way.
print("\n5b. Sentinel-string normalization")
manifest_text = read_text(MANIFEST)
# Replace several nullable-field values with sentinel strings.
mutated = (manifest_text
    # `- finding_id: null` → `- finding_id: none` (R-08 has a null finding_id)
    .replace("- finding_id: null", "- finding_id: none", 1)
    # Mutate PRAX-001's `related_findings: PRAX-2026-05-25-002` to `NONE`
    # (uppercase sentinel) — exercises the case where a worker wrote
    # a sentinel string where the schema expects an id list.
    .replace(
        "- related_findings: PRAX-2026-05-25-002",
        "- related_findings: NONE",
        1,
    )
)
with tempfile.TemporaryDirectory() as td:
    mpath = os.path.join(td, "mutated.md")
    Path(mpath).write_text(mutated, encoding="utf-8")
    out_path = os.path.join(td, "mutated.json")
    res = run_converter(mpath, out_path)
    check("mutated manifest with sentinel strings exits 0",
          res.returncode == 0, res.stderr or res.stdout)
    if res.returncode == 0:
        md = json.loads(read_text(out_path))
        # R-08's `finding_id: none` should normalize to JSON null.
        r08 = next(r for r in md["remit_coverage"]["rules"] if r["rule_id"] == "R-08")
        check("`finding_id: none` -> JSON null",
              r08["finding_id"] is None,
              f"got {r08['finding_id']!r}")
        # PRAX-001's `related_findings: NONE` should normalize to [].
        f1 = next(f for f in md["findings"] if f["id"] == "PRAX-2026-05-25-001")
        check("`related_findings: NONE` -> empty array",
              f1.get("related_findings") == [],
              f"got {f1.get('related_findings')!r}")


# ── 6. Negative cases ───────────────────────────────────────────────────────
print("\n6. Negative cases")

# (a) Missing required section.
truncated_manifest = "\n".join(read_text(MANIFEST).splitlines()[:50])
assert_parse_error(
    "missing required sections fails",
    truncated_manifest,
    "missing required sections",
)

# (b) Wrong manifest_format_version.
bad_version = read_text(MANIFEST).replace(
    "- manifest_format_version: 1",
    "- manifest_format_version: 99",
    1,
)
assert_parse_error(
    "wrong manifest_format_version fails",
    bad_version,
    "manifest_format_version",
)

# (c) Heading/id disagreement: bullet id doesn't match `### …` heading.
mismatch = read_text(MANIFEST).replace(
    "- id: PRAX-2026-05-25-001",
    "- id: PRAX-2026-05-25-999",
    1,
)
assert_parse_error(
    "heading/bullet id disagreement fails",
    mismatch,
    "disagrees with",
)

# (d) Heading/severity disagreement.
sev_mismatch = read_text(MANIFEST).replace(
    "### PRAX-2026-05-25-001 (Critical)",
    "### PRAX-2026-05-25-001 (Low)",
    1,
)
assert_parse_error(
    "heading/bullet severity disagreement fails",
    sev_mismatch,
    "disagrees with",
)

# (e) Unknown field in a section.
unknown_field = read_text(MANIFEST).replace(
    "- agent: HelperBot",
    "- agent: HelperBot\n- bogus_field: nope",
    1,
)
assert_parse_error(
    "unknown field in scan fails",
    unknown_field,
    "unknown field",
)

# (f) Malformed evidence — wrong field name in evidence item.
bad_evidence = read_text(MANIFEST).replace(
    "  - file: src/llm/prompts.js\n    line: 27\n    snippet:",
    "  - filename: src/llm/prompts.js\n    line: 27\n    snippet:",
    1,
)
assert_parse_error(
    "malformed evidence item (unknown field) fails",
    bad_evidence,
    "unknown field",
)

# (g) Missing required field in rule.
missing_rule_field = read_text(MANIFEST).replace(
    "#### R-08\n- section: Behavioral Constraints / What the agent must never do\n"
    "- rule_text: The agent MUST NOT execute shell commands or use any capability "
    "outside its authorized tool inventory.\n"
    "- status: verified\n"
    "- finding_id: null",
    "#### R-08\n- section: Behavioral Constraints / What the agent must never do\n"
    "- rule_text: The agent MUST NOT execute shell commands or use any capability "
    "outside its authorized tool inventory.\n"
    "- finding_id: null",
    1,
)
assert_parse_error(
    "rule with missing required field fails",
    missing_rule_field,
    "status",
)


# ── 7. JSON key order is canonical ──────────────────────────────────────────
print("\n7. Canonical JSON key order")
keys = list(data.keys())
expected_keys = [
    "schema_version", "praxen_version", "scan",
    "intro_band", "behavior_summary",
    "remit_coverage", "findings", "positives", "log_files",
    "raise_posture", "footer",
]
check("top-level keys are in canonical order", keys == expected_keys,
      f"got {keys}")


print(f"\n{_passed} passed, {_failed} failed")
# Guard the exit so `pytest <this-file>` doesn't fail collection with
# `INTERNALERROR: SystemExit`. The test is a standalone script (see header);
# pytest is not the supported runner, but the guard makes the wrong-runner
# case fall through to pytest's "no tests collected" message instead.
if __name__ == "__main__":
    sys.exit(0 if _failed == 0 else 1)
