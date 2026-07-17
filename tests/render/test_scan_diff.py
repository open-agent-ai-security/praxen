# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Self-contained tests for tests/scan_diff.py — the scan-vs-scan diff tool.

Run: python3 tests/render/test_scan_diff.py   (stdlib only; not a pytest module)

Covers the join contract: a run diffed against itself is a perfect match
(nothing dropped/new); removing a finding surfaces it as dropped; a severity
change on an otherwise-identical finding is reported; and the evidence-file /
category signals join two differently-worded descriptions of the same issue.
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "tests"))
import scan_diff  # noqa: E402

_passed = _failed = 0


def check(name, cond, detail=""):
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  ok   {name}")
    else:
        _failed += 1
        print(f"  FAIL {name}" + (f"  — {detail}" if detail else ""))


FIXTURE = os.path.join(REPO_ROOT, "tests", "fixtures", "finbot.canonical.json")
with open(FIXTURE, encoding="utf-8") as fh:
    RUN = json.load(fh)
N = len(RUN["findings"])

print("1. self-diff is a perfect match")
d = scan_diff.diff(RUN, RUN)
check("all findings matched", d["counts"]["matched"] == N, str(d["counts"]))
check("nothing dropped", d["counts"]["only_in_a_dropped"] == 0)
check("nothing new", d["counts"]["only_in_b_new"] == 0)
check("match rate 1.0", d["match_rate"] == 1.0, str(d["match_rate"]))
check("no severity changes", d["matched_with_severity_change"] == [])

print("\n2. removing a finding surfaces it as dropped")
b = copy.deepcopy(RUN)
removed = b["findings"].pop(0)
d = scan_diff.diff(RUN, b)
check("one finding dropped", d["counts"]["only_in_a_dropped"] == 1, str(d["counts"]))
check("dropped one is the removed finding",
      d["only_in_a_dropped"] and d["only_in_a_dropped"][0]["summary"] == removed["summary"])
check("nothing spuriously new", d["counts"]["only_in_b_new"] == 0)

print("\n3. a severity flip on a matched finding is reported")
b = copy.deepcopy(RUN)
i = next(k for k, f in enumerate(b["findings"]) if f["severity"] == "Critical")
b["findings"][i]["severity"] = "High"
d = scan_diff.diff(RUN, b)
check("severity change reported", len(d["matched_with_severity_change"]) == 1,
      str(d["matched_with_severity_change"]))
check("reported as Critical -> High",
      d["matched_with_severity_change"] and
      d["matched_with_severity_change"][0]["a"]["severity"] == "Critical" and
      d["matched_with_severity_change"][0]["b"]["severity"] == "High")
check("still counts as matched, not dropped/new",
      d["counts"]["only_in_a_dropped"] == 0 and d["counts"]["only_in_b_new"] == 0)

print("\n4. differently-worded same issue joins on evidence-file + category")
b = copy.deepcopy(RUN)
f0 = b["findings"][0]
f0["summary"] = "Completely reworded description of the same underlying issue at the same files."
# keep raise_category + evidence files identical → should still match
d = scan_diff.diff(RUN, b)
check("reworded finding still matched (not dropped)",
      d["counts"]["only_in_a_dropped"] == 0, str(d["counts"]))

print(f"\n{_passed} passed, {_failed} failed")
if __name__ == "__main__":
    sys.exit(0 if _failed == 0 else 1)
