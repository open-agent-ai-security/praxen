#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Semantic comparator for Praxen threat-model graphs (test tooling).

Measures run-to-run agreement between two independent extractions of the
same target, on the yardstick settled during the Phase-0 probe
(plans/RESULTS_THREAT_MODEL_PROBE.md): the product gates are
**boundary-set agreement**, **matched-threat status agreement**, and
**component fuzzy agreement** — explicitly NOT raw node-id or edge-topology
match, which the probe proved are the wrong yardsticks.

Matching is content-based (global greedy on a similarity matrix — the
probe's row-greedy matcher mispaired and under-matched). Legacy probe
statuses (finding/residual/open) are normalized so probe-era graphs remain
comparable.

Usage:
  python3 threatmodel_compare.py A/graph.json B/graph.json [--json]

``--json`` prints a machine-readable summary (the pre-ship gate consumes
it); otherwise a human-readable report. Not shipped in the plugin.
"""
from __future__ import annotations

import argparse
import json
import sys

_STOP = set("the a an of to in on for with and or is are that this into from "
            "by as no not its it every any via one two".split())
_LEGACY = {"finding": "confirmed", "residual": "potential", "open": "potential"}


def _norm_status(st):
    return _LEGACY.get(st, st)


def _tokens(*texts):
    out = set()
    for t in texts:
        for w in t.lower().replace("-", " ").replace("_", " ").split():
            w = w.strip(".,()`'\"“”:;")
            if w and w not in _STOP:
                out.add(w)
    return out


def _sim(ta, tb):
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _global_greedy(items_a, items_b, score_fn, cutoff):
    """Best-first global matching: score every pair, take non-conflicting
    pairs by descending score above the cutoff."""
    scored = []
    for i, a in enumerate(items_a):
        for j, b in enumerate(items_b):
            s = score_fn(a, b)
            if s >= cutoff:
                scored.append((s, i, j))
    scored.sort(key=lambda x: (-x[0], x[1], x[2]))
    used_a, used_b, pairs = set(), set(), []
    for s, i, j in scored:
        if i in used_a or j in used_b:
            continue
        used_a.add(i); used_b.add(j)
        pairs.append((i, j, s))
    return pairs


# ── the three gate measures ──────────────────────────────────────────────────
def match_boundaries(ga, gb):
    """Boundaries match on identical id (archetypes converge — the probe's
    strongest result); leftovers match on name-token similarity."""
    ba, bb = ga["trust_boundaries"], gb["trust_boundaries"]
    ids_a = {b["id"]: b for b in ba}
    ids_b = {b["id"]: b for b in bb}
    pairs = [(ids_a[i], ids_b[i], 1.0) for i in ids_a if i in ids_b]
    rest_a = [b for b in ba if b["id"] not in ids_b]
    rest_b = [b for b in bb if b["id"] not in ids_a]
    fuzzy = _global_greedy(
        rest_a, rest_b,
        lambda a, b: _sim(_tokens(a["id"], a["name"]), _tokens(b["id"], b["name"])),
        cutoff=0.30)
    pairs += [(rest_a[i], rest_b[j], s) for i, j, s in fuzzy]
    union = len(ba) + len(bb) - len(pairs)
    return pairs, (len(pairs) / union if union else 1.0), rest_a, rest_b, fuzzy


def match_threats(pairs):
    """Within matched boundaries, pair threats on summary-token similarity
    with a bonus for agreeing STRIDE letter / OWASP code; report status
    agreement over the matched pairs."""
    matched = agree = 0
    disagreements = []
    total_a = total_b = 0
    for ba, bb, _s in pairs:
        ta, tb = ba["threats"], bb["threats"]
        total_a += len(ta); total_b += len(tb)

        def score(a, b):
            s = _sim(_tokens(a["summary"]), _tokens(b["summary"]))
            if a.get("stride") == b.get("stride"):
                s += 0.10
            if (a.get("owasp") or None) == (b.get("owasp") or None):
                s += 0.10
            return s

        for i, j, s in _global_greedy(ta, tb, score, cutoff=0.30):
            matched += 1
            sa, sb = _norm_status(ta[i]["status"]), _norm_status(tb[j]["status"])
            if sa == sb:
                agree += 1
            else:
                disagreements.append((ba["id"], sa, sb,
                                      ta[i]["summary"][:70], tb[j]["summary"][:70]))
    return matched, agree, disagreements, total_a, total_b


def match_components(ga, gb):
    """Nodes match on exact id, then on same-kind + name/id token similarity."""
    na, nb = ga["nodes"], gb["nodes"]
    ids_b = {n["id"]: n for n in nb}
    exact = [n["id"] for n in na if n["id"] in ids_b]
    rest_a = [n for n in na if n["id"] not in ids_b]
    rest_b = [n for n in nb if n["id"] not in {n["id"] for n in na}]

    def score(a, b):
        # kind disagreement halves the score rather than barring the match:
        # two runs judging one file a datastore vs a log_sink are still
        # describing the same component (the probe yardstick, which the gate
        # thresholds were calibrated on, matched on name similarity alone).
        s = _sim(_tokens(a["id"], a["name"]), _tokens(b["id"], b["name"]))
        return s if a["kind"] == b["kind"] else s * 0.5

    fuzzy = _global_greedy(rest_a, rest_b, score, cutoff=0.30)
    matched = len(exact) + len(fuzzy)
    union = len(na) + len(nb) - matched
    return (matched / union if union else 1.0), exact, fuzzy, rest_a, rest_b


def compare(ga, gb):
    bpairs, b_agree, only_a, only_b, bfuzzy = match_boundaries(ga, gb)
    t_matched, t_agree, t_dis, ta, tb = match_threats(bpairs)
    c_agree, c_exact, c_fuzzy, c_only_a, c_only_b = match_components(ga, gb)
    return {
        "boundary_agreement": round(b_agree, 3),
        "boundaries": {"a": len(ga["trust_boundaries"]),
                       "b": len(gb["trust_boundaries"]),
                       "matched": len(bpairs),
                       "only_a": [x["id"] for x in only_a
                                  if x["id"] not in {p[0]["id"] for p in bpairs}],
                       "only_b": [x["id"] for x in only_b
                                  if x["id"] not in {p[1]["id"] for p in bpairs}]},
        "threat_status_agreement": round(t_agree / t_matched, 3) if t_matched else None,
        "threats": {"a": ta, "b": tb, "matched": t_matched, "agreed": t_agree,
                    "disagreements": [
                        {"boundary": d[0], "a": d[1], "b": d[2],
                         "summary_a": d[3], "summary_b": d[4]} for d in t_dis]},
        "component_agreement": round(c_agree, 3),
        "components": {"a": len(ga["nodes"]), "b": len(gb["nodes"]),
                       "exact_id": len(c_exact), "fuzzy": len(c_fuzzy)},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Compare two threat-model graphs semantically.")
    ap.add_argument("graph_a"); ap.add_argument("graph_b")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)
    ga = json.load(open(args.graph_a, encoding="utf-8"))
    gb = json.load(open(args.graph_b, encoding="utf-8"))
    r = compare(ga, gb)
    if args.json:
        print(json.dumps(r, indent=1))
        return 0
    print(f"A: {args.graph_a}\nB: {args.graph_b}\n")
    print(f"boundary-set agreement:      {r['boundary_agreement']:.2f}  "
          f"({r['boundaries']['matched']} matched of "
          f"{r['boundaries']['a']} vs {r['boundaries']['b']})")
    for side in ("only_a", "only_b"):
        for x in r["boundaries"][side]:
            print(f"  {side}: {x}")
    tsa = r["threat_status_agreement"]
    print(f"threat status agreement:     "
          f"{('%.2f' % tsa) if tsa is not None else 'n/a'}  "
          f"({r['threats']['agreed']}/{r['threats']['matched']} matched pairs; "
          f"{r['threats']['a']} vs {r['threats']['b']} threats)")
    for d in r["threats"]["disagreements"]:
        print(f"  {d['boundary']}: {d['a']} vs {d['b']} | {d['summary_a']}")
    print(f"component fuzzy agreement:   {r['component_agreement']:.2f}  "
          f"({r['components']['exact_id']} exact + {r['components']['fuzzy']} fuzzy of "
          f"{r['components']['a']} vs {r['components']['b']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
