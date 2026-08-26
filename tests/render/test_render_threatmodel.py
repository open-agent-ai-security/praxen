# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Tests for render_threatmodel.py (threat-model report renderer).

Covers: golden byte-comparison, determinism, masthead status-conservation
(the counts a reader sees must equal the graph's contents — a vocabulary
change once silently zeroed a metric in the probe), the brand single-source
contract (extraction anchors + the few mirrored literals must exist in
report_template.html), and fails-loudly behavior on bad input.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SKILL_DIR = os.path.join(REPO_ROOT, "skills", "behavior-verifier")
FIXTURES = os.path.join(REPO_ROOT, "tests", "fixtures")
GRAPH = os.path.join(FIXTURES, "threatmodel-demo.graph.json")
GOLDEN = os.path.join(FIXTURES, "threatmodel-demo.golden.html")
TEMPLATE = os.path.join(SKILL_DIR, "report_template.html")
sys.path.insert(0, SKILL_DIR)

import render_threatmodel as rtm  # noqa: E402
import threatmodel_schema as tms  # noqa: E402
from schema import SchemaError  # noqa: E402

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
    graph = json.load(open(GRAPH, encoding="utf-8"))
    template = open(TEMPLATE, encoding="utf-8").read()

    check("fixture validates against the v1.0 contract",
          tms.validate(json.load(open(GRAPH, encoding="utf-8"))) is not None)

    out1 = rtm.render(json.load(open(GRAPH, encoding="utf-8")), template)
    out2 = rtm.render(json.load(open(GRAPH, encoding="utf-8")), template)
    check("render is deterministic", out1 == out2)

    # analysis cross-link: opt-in via analysis_html, absent by default
    linked = rtm.render(json.load(open(GRAPH, encoding="utf-8")), template,
                        analysis_html="demo-analysis.html")
    aref = json.load(open(GRAPH, encoding="utf-8"))["analysis_ref"]
    check("analysis_html links the built-against reference",
          f'built against <a href="demo-analysis.html"><b>' in linked)
    check("default render carries no built-against link",
          'built against <a href=' not in out1
          and f"built against <b>" in out1)

    # optional remit_version: masthead suffix present iff the graph carries it
    gv = json.load(open(GRAPH, encoding="utf-8"))
    gv["remit_version"] = "9.9-test"
    check("remit_version validates as optional", tms.validate(dict(gv)) is not None)
    out_rv = rtm.render(gv, template)
    check("remit_version shows in the masthead", "remit v9.9-test" in out_rv)
    check("no remit_version, no masthead suffix", "remit v" not in out1)

    golden = open(GOLDEN, encoding="utf-8").read()
    check("render matches the committed golden output", out1 == golden,
          "regenerate with: python3 skills/behavior-verifier/render_threatmodel.py "
          "--graph tests/fixtures/threatmodel-demo.graph.json "
          "--template skills/behavior-verifier/report_template.html "
          "--out-html tests/fixtures/threatmodel-demo.golden.html "
          "(only when the change is intentional)")

    # status conservation: masthead numbers == recomputed from the graph
    want = {st: sum(1 for b in graph["trust_boundaries"] for t in b["threats"]
                    if t["status"] == st) for st in tms.THREAT_STATUSES}
    got = {}
    for cls, st in (("mh-con", "confirmed"), ("mh-pot", "potential"),
                    ("mh-par", "partial"), ("mh-mit", "mitigated")):
        m = re.search(rf'class="mh-metric {cls}"><b>(\d+)</b>', out1)
        got[st] = int(m.group(1)) if m else -1
    check("masthead status counts conserve the graph", got == want,
          f"masthead {got} vs graph {want}")
    check("statuses sum to total threats",
          sum(want.values()) == graph["notes"]["counts"]["threats"])

    # brand single-source: extraction anchors present, mirrored literals exist
    tokens, root_css, mh, ft = rtm.extract_brand(template)
    check("template :root tokens extracted", "--navy" in tokens and "--orange" in tokens)
    check("masthead/footer lockups extracted",
          mh.startswith('<div class="masthead-logo">') and "</svg></div>" in ft)
    for lit in (rtm.MH_CONFIRMED, rtm.MH_POTENTIAL, rtm.MH_PARTIAL, rtm.MH_MITIGATED):
        check(f"mirrored masthead literal {lit} still in template", lit in template,
              "update render_threatmodel.MH_* when the template restyles")
    for name in set(rtm.KIND_TOKEN.values()) | set(rtm.STATUS_TOKEN.values()) \
            | set(rtm.COVERAGE_TOKEN.values()):
        check(f"token {name} resolvable from template", name in tokens)

    # fails loudly
    try:
        rtm.extract_brand("<html>no tokens here</html>")
        check("missing :root fails loudly", False, "no error raised")
    except rtm.RenderError:
        check("missing :root fails loudly", True)
    bad = json.load(open(GRAPH, encoding="utf-8"))
    bad["trust_boundaries"][0]["threats"][0]["status"] = "residual"
    try:
        rtm.render(bad, template)
        check("invalid graph fails loudly", False, "no error raised")
    except SchemaError:
        check("invalid graph fails loudly", True)

    # CLI end-to-end
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        out_path = os.path.join(td, "out.html")
        r = subprocess.run([sys.executable,
                            os.path.join(SKILL_DIR, "render_threatmodel.py"),
                            "--graph", GRAPH, "--template", TEMPLATE,
                            "--out-html", out_path],
                           capture_output=True, text=True)
        check("CLI renders end-to-end", r.returncode == 0, r.stderr)
        check("CLI output matches golden",
              open(out_path, encoding="utf-8").read() == golden)

    print(f"\n{_passed} passed, {_failed} failed")
    sys.exit(1 if _failed else 0)


if __name__ == "__main__":
    main()
