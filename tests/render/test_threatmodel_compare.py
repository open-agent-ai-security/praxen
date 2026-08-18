# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Tests for the semantic threat-model comparator (threatmodel_compare.py)."""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FIXTURE = os.path.join(REPO_ROOT, "tests", "fixtures", "threatmodel-demo.graph.json")

import threatmodel_compare as cmp  # noqa: E402

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


def main():
    g = json.load(open(FIXTURE, encoding="utf-8"))

    # identical graphs → perfect agreement on all three gates
    r = cmp.compare(g, copy.deepcopy(g))
    check("identical graphs: boundary 1.0", r["boundary_agreement"] == 1.0)
    check("identical graphs: status 1.0", r["threat_status_agreement"] == 1.0)
    check("identical graphs: components 1.0", r["component_agreement"] == 1.0)

    # rename a node id (same name) → fuzzy match keeps component agreement 1.0
    b = copy.deepcopy(g)
    old = b["nodes"][0]["id"]
    new_id = old + "-renamed"
    b["nodes"][0]["id"] = new_id
    for e in b["edges"]:
        for k in ("from", "to"):
            if e[k] == old:
                e[k] = new_id
        e["id"] = f'{e["from"]}--{e["to"]}'
    for bd in b["trust_boundaries"]:
        bd["crossing_edges"] = [c.replace(old, new_id) for c in bd["crossing_edges"]]
    for ap in b["attack_paths"]:
        for st in ap["steps"]:
            if st["node"] == old:
                st["node"] = new_id
    r = cmp.compare(g, b)
    check("id rename: fuzzy component match holds", r["component_agreement"] == 1.0,
          str(r["components"]))

    # kind flip on the renamed node → still matched (penalty, not a bar)
    b2 = copy.deepcopy(b)
    b2["nodes"][0]["kind"] = "client" if b2["nodes"][0]["kind"] != "client" else "adapter"
    r = cmp.compare(g, b2)
    check("kind flip: still matched via penalty", r["component_agreement"] == 1.0,
          str(r["components"]))

    # kind flip WITH the kind embedded in the id (the uagents case:
    # resolver-py-adapter vs resolver-py-tool) → still matched
    bk = copy.deepcopy(b)
    n = bk["nodes"][0]
    old_id2 = n["id"]
    n["kind"] = "adapter" if n["kind"] != "adapter" else "tool"
    new_id2 = old_id2.rsplit("-renamed", 1)[0] + "-" + n["kind"]
    n["id"] = new_id2
    for e in bk["edges"]:
        for k in ("from", "to"):
            if e[k] == old_id2:
                e[k] = new_id2
        e["id"] = f'{e["from"]}--{e["to"]}'
    for bd in bk["trust_boundaries"]:
        bd["crossing_edges"] = [c.replace(old_id2, new_id2) for c in bd["crossing_edges"]]
    for ap2 in bk["attack_paths"]:
        for st in ap2["steps"]:
            if st["node"] == old_id2:
                st["node"] = new_id2
    r = cmp.compare(g, bk)
    check("kind-in-id flip: still matched", r["component_agreement"] == 1.0,
          str(r["components"]))

    # status flip on a matched threat → disagreement recorded
    b3 = copy.deepcopy(g)
    t = b3["trust_boundaries"][0]["threats"][1]
    orig_status = cmp._norm_status(t["status"])
    flipped = "mitigated" if orig_status != "mitigated" else "potential"
    t["status"] = flipped
    if flipped == "mitigated":
        t["mitigation_evidence"] = {"file": "x.py", "line": 1}
    else:
        t["mitigation_evidence"] = None
        t["finding_id"] = None
    r = cmp.compare(g, b3)
    check("status flip: agreement < 1.0", r["threat_status_agreement"] < 1.0)
    check("status flip: disagreement recorded",
          any(d["a"] == orig_status and d["b"] == flipped
              for d in r["threats"]["disagreements"]))

    # legacy statuses normalize before comparison
    b4 = copy.deepcopy(g)
    for bd in b4["trust_boundaries"]:
        for t in bd["threats"]:
            if t["status"] == "potential":
                t["status"] = "residual"
    r = cmp.compare(g, b4)
    check("legacy statuses normalize", r["threat_status_agreement"] == 1.0)

    # a boundary present on one side only → agreement < 1.0, listed
    b5 = copy.deepcopy(g)
    extra = copy.deepcopy(b5["trust_boundaries"][0])
    extra["id"] = "value-transfer"
    extra["name"] = "Funds leave the wallet"
    b5["trust_boundaries"].append(extra)
    r = cmp.compare(g, b5)
    check("extra boundary lowers agreement", r["boundary_agreement"] < 1.0)
    check("extra boundary listed", "value-transfer" in r["boundaries"]["only_b"])

    # CLI --json emits the three gate numbers
    p = subprocess.run([sys.executable, os.path.join(HERE, "threatmodel_compare.py"),
                        FIXTURE, FIXTURE, "--json"], capture_output=True, text=True)
    out = json.loads(p.stdout)
    check("CLI --json works", p.returncode == 0
          and {"boundary_agreement", "threat_status_agreement",
               "component_agreement"} <= set(out))

    print(f"\n{_passed} passed, {_failed} failed")
    sys.exit(1 if _failed else 0)


if __name__ == "__main__":
    main()
