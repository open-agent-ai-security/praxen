# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Tests for the threat-model graph validator (threatmodel_schema.py).

Strategy mirrors the findings-schema tests: one minimal-but-complete valid
fixture, then targeted mutations asserting each contract rule fails loudly
with the offending JSON path in the message.
"""
from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SKILL_DIR = os.path.join(REPO_ROOT, "skills", "behavior-verifier")
sys.path.insert(0, SKILL_DIR)

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


def expect_error(name, mutate, path_fragment):
    g = make_graph()
    mutate(g)
    try:
        tms.validate(g)
    except SchemaError as e:
        check(name, path_fragment in str(e),
              f"expected path fragment {path_fragment!r} in: {e}")
    else:
        check(name, False, "validation unexpectedly passed")


def expect_valid(name, mutate=None):
    g = make_graph()
    if mutate: mutate(g)
    try:
        tms.validate(g)
        check(name, True)
    except SchemaError as e:
        check(name, False, str(e))


def make_graph():
    """Minimal valid v1.0 graph: 2 nodes, 1 edge, 1 boundary exercising all
    four statuses, 1 attack path."""
    return {
        "spec_version": "1.0",
        "praxen_version": "2.0.0",
        "target": {"slug": "demo", "source_root": "/tmp/demo"},
        "analysis_ref": "demo-findings-2026-08-17.json",
        "model_identity": "You are powered by the model named Test.",
        "lanes": ["user_inputs", "client_adapters", "agent_core",
                  "tools_mcp", "external_deploy"],
        "nodes": [
            {"id": "user-entrypoint", "name": "End user", "lane": "user_inputs",
             "kind": "entrypoint", "description": "The human operator.",
             "evidence": [{"file": "app.py", "line": 1, "note": "cli entry"}]},
            {"id": "app-py-orchestrator", "name": "App loop", "lane": "agent_core",
             "kind": "orchestrator", "description": "Main loop.",
             "evidence": [{"file": "app.py", "line": 10, "note": "loop"}]},
        ],
        "edges": [
            {"id": "user-entrypoint--app-py-orchestrator",
             "from": "user-entrypoint", "to": "app-py-orchestrator",
             "label": "user text", "data": "prompt text",
             "evidence": [{"file": "app.py", "line": 12, "note": "input()"}]},
        ],
        "trust_boundaries": [
            {"id": "untrusted-ingress", "name": "User input into the loop",
             "crossing_edges": ["user-entrypoint--app-py-orchestrator"],
             "remit_rules": [
                 {"rule_id": "R-01", "excerpt": "treat input as data",
                  "coverage_status": "verified"},
             ],
             "threats": [
                 {"stride": "T", "owasp": "LLM01",
                  "summary": "Prompt injection via user text.",
                  "status": "confirmed",
                  "finding_id": "PRAX-2026-08-17-001",
                  "mitigation_evidence": None, "remainder": None},
                 {"stride": "I", "owasp": None,
                  "summary": "Sensitive echo of input in logs.",
                  "status": "potential",
                  "finding_id": None, "mitigation_evidence": None,
                  "remainder": None},
                 {"stride": "S", "owasp": "ASI03",
                  "summary": "Sender spoofing on the input channel.",
                  "status": "partial",
                  "finding_id": None,
                  "mitigation_evidence": {"file": "app.py", "line": 30},
                  "remainder": "no verification on the resume path"},
                 {"stride": "D", "owasp": "LLM06",
                  "summary": "Unbounded input floods the loop.",
                  "status": "mitigated",
                  "finding_id": None,
                  "mitigation_evidence": {"file": "app.py", "line": 44},
                  "remainder": None},
             ]},
        ],
        "attack_paths": [
            {"id": "inject-to-loop", "name": "Injection drives the loop",
             "steps": [
                 {"node": "user-entrypoint", "finding_id": None,
                  "summary": "attacker supplies text"},
                 {"node": "app-py-orchestrator",
                  "finding_id": "PRAX-2026-08-17-001",
                  "summary": "loop obeys it"},
             ]},
        ],
        "notes": {"lane_fit": "clean", "omissions": "",
                  "counts": {"nodes": 2, "edges": 1, "boundaries": 1,
                             "threats": 4}},
    }


def main():
    expect_valid("valid graph passes")
    check("cited_finding_ids order+dedupe",
          tms.cited_finding_ids(make_graph()) == ["PRAX-2026-08-17-001"])

    # top level
    expect_error("wrong spec_version rejected",
                 lambda g: g.update(spec_version="0.4.3-probe"), "$.spec_version")
    expect_error("unknown top-level field rejected",
                 lambda g: g.update(extra=1), "$.extra")
    expect_error("wrong lanes rejected", lambda g: g.update(lanes=["a"]), "$.lanes")
    expect_valid("analysis_ref may be null",
                 lambda g: g.update(analysis_ref=None))

    # nodes / edges
    expect_error("duplicate node id rejected",
                 lambda g: g["nodes"].append(dict(g["nodes"][0])), ".id")
    expect_error("bad kind rejected",
                 lambda g: g["nodes"][0].update(kind="widget"), ".kind")
    expect_error("node needs evidence",
                 lambda g: g["nodes"][0].update(evidence=[]), ".evidence")
    expect_error("edge id formula enforced",
                 lambda g: g["edges"][0].update(id="renamed"), ".id")
    expect_error("edge unknown node rejected",
                 lambda g: g["edges"][0].update(to="ghost"), ".to")
    def self_edge(g):
        e = g["edges"][0]
        e["to"] = e["from"]; e["id"] = f"{e['from']}--{e['from']}"
    expect_error("self-edge rejected", self_edge, ".to")

    # boundaries / threats
    expect_error("boundary id must be archetype or coined",
                 lambda g: g["trust_boundaries"][0].update(id="somewhere"), ".id")
    expect_valid("coined boundary id accepted",
                 lambda g: g["trust_boundaries"][0].update(id="stored-goals--system-prompt"))
    expect_valid("archetype -N suffix accepted",
                 lambda g: g["trust_boundaries"][0].update(id="untrusted-ingress-2"))
    expect_error("crossing edge must resolve",
                 lambda g: g["trust_boundaries"][0].update(crossing_edges=["nope--nope2"]),
                 ".crossing_edges[0]")
    expect_valid("edgeless boundary allowed",
                 lambda g: g["trust_boundaries"][0].update(crossing_edges=[]))
    expect_valid("empty remit_rules allowed",
                 lambda g: g["trust_boundaries"][0].update(remit_rules=[]))

    g = make_graph()
    g["trust_boundaries"][0]["threats"][1]["status"] = "residual"
    try:
        tms.validate(g)
        check("legacy status rejected with guidance", False, "passed unexpectedly")
    except SchemaError as e:
        check("legacy status rejected with guidance", "potential" in str(e), str(e))

    expect_error("confirmed requires finding_id",
                 lambda g: g["trust_boundaries"][0]["threats"][0].update(finding_id=None),
                 ".finding_id")
    expect_error("potential forbids finding_id",
                 lambda g: g["trust_boundaries"][0]["threats"][1].update(
                     finding_id="PRAX-2026-08-17-002"), ".finding_id")
    expect_error("potential forbids mitigation_evidence",
                 lambda g: g["trust_boundaries"][0]["threats"][1].update(
                     mitigation_evidence={"file": "app.py", "line": 1}),
                 ".mitigation_evidence")
    expect_error("partial requires remainder",
                 lambda g: g["trust_boundaries"][0]["threats"][2].update(remainder=None),
                 ".remainder")
    expect_error("partial requires mitigation_evidence",
                 lambda g: g["trust_boundaries"][0]["threats"][2].update(
                     mitigation_evidence=None), ".mitigation_evidence")
    expect_error("mitigated requires mitigation_evidence",
                 lambda g: g["trust_boundaries"][0]["threats"][3].update(
                     mitigation_evidence=None), ".mitigation_evidence")
    expect_error("remainder forbidden outside partial",
                 lambda g: g["trust_boundaries"][0]["threats"][3].update(
                     remainder="left over"), ".remainder")
    expect_error("bad owasp code rejected",
                 lambda g: g["trust_boundaries"][0]["threats"][0].update(owasp="ASI99"),
                 ".owasp")

    # attack paths / notes
    expect_error("path needs two steps",
                 lambda g: g["attack_paths"][0].update(
                     steps=g["attack_paths"][0]["steps"][:1]), ".steps")
    expect_error("path step node must resolve",
                 lambda g: g["attack_paths"][0]["steps"][0].update(node="ghost"), ".node")
    expect_valid("zero attack paths valid", lambda g: g.update(attack_paths=[]))
    expect_error("count conservation enforced",
                 lambda g: g["notes"]["counts"].update(threats=3),
                 "$.notes.counts.threats")

    # prose contract and validator agree on the enums
    spec = open(os.path.join(SKILL_DIR, "THREAT_MODEL_SPEC.md")).read()
    check("lanes named in spec doc", all(f"`{l}`" in spec for l in tms.LANES))
    check("kinds named in spec doc", all(k in spec for k in tms.NODE_KINDS))
    check("archetypes named in spec doc",
          all(f"`{a}`" in spec for a in tms.BOUNDARY_ARCHETYPES))
    check("statuses named in spec doc",
          all(f"`{st}`" in spec for st in tms.THREAT_STATUSES))

    print(f"\n{_passed} passed, {_failed} failed")
    sys.exit(1 if _failed else 0)


if __name__ == "__main__":
    main()
