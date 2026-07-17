#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Scan-vs-scan diff for Praxen findings JSON (schema 3.0).

Joins two runs of the *same target* mechanically and reports what held, what
dropped, and what is new — the regression check the 1.2 "comparability" work
exists to make automatic (the 2026-07-12 clean run needed hand-matching).

**Why this needs schema 3.0.** Finding ids (`PRAX-…`) and remit rule ids
(`R-NN`) are re-enumerated every scan, so neither is a stable join key (see
tests/baselines/README.md and the run-local-rule-id note). What *is* stable is
the exact remit **rule text** a finding quotes — fixed by the remit. Schema 3.0
carries that as an array (`policy_rule_text`), so a finding's rule-citation set
is a clean set-membership key instead of a ' / '-joined string to re-split.

Join strategy. There is no single stable key — finding ids and R-NN ids
re-enumerate per scan, and the model even cites *different remit rules* for the
same finding run to run (so rule-text sets only partially overlap). The
robustly stable signals are the **evidence file set** (the same issue cites the
same code locations) and the **RAISE category**; rule-text and summary tokens
are weaker corroborators. Similarity is a weighted blend of all four, with a
severity-distance penalty so a Critical and a Medium at the same location don't
collapse together. Schema 3.0's array `policy_rule_text` is what lets the
rule-text signal be a clean set instead of a re-split ' / ' string.

Greedy best-first matching; each finding matches at most once. Output is a
human-readable report (default) or `--json`. Exit is always 0 — this is a
diff, not a gate; callers decide what a drop means.

Usage:
    python3 tests/scan_diff.py RUN_A.json RUN_B.json [--threshold 0.5] [--json]
"""
import argparse
import json
import re
import sys


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


_WORD = re.compile(r"[a-z0-9]+")


def _norm_tokens(text):
    # Lowercased word set minus very common filler, for summary-overlap fallback.
    stop = {"the", "a", "an", "of", "to", "and", "or", "is", "in", "on", "no",
            "not", "its", "it", "with", "for", "by", "as", "at", "any", "that"}
    return {w for w in _WORD.findall((text or "").lower()) if w not in stop}


def _evidence_files(f):
    """Set of evidence file paths (NOT file:line — line ranges drift run to
    run while the cited file is stable)."""
    return {e["file"] for e in f.get("evidence", []) if e.get("file")}


_SEV_RANK = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1, "Informational": 0}


def _rule_text_key(f):
    """Frozenset of the exact remit rule texts this finding cites, or empty."""
    return frozenset(t.strip() for t in (f.get("policy_rule_text") or []))


def _jaccard(a, b):
    if not a and not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _finding_view(f):
    return {
        "id": f.get("id"),
        "severity": f.get("severity"),
        "summary": f.get("summary"),
        "rules": sorted(_rule_text_key(f)),
    }


def _candidate_score(fa, fb):
    """Similarity in [0,1] between two findings, from four stable-to-weak
    signals: evidence-file overlap (strongest — same issue, same code sites),
    RAISE-category agreement, rule-text overlap, and summary-token overlap.
    A severity-distance factor keeps a Critical and a Medium at the same
    location from collapsing into one match."""
    ev = _jaccard(_evidence_files(fa), _evidence_files(fb))
    cat = 1.0 if fa.get("raise_category") == fb.get("raise_category") else 0.0
    rule = _jaccard(_rule_text_key(fa), _rule_text_key(fb))
    summ = _jaccard(_norm_tokens(fa.get("summary")), _norm_tokens(fb.get("summary")))
    base = 0.40 * ev + 0.20 * cat + 0.20 * rule + 0.20 * summ
    # Severity distance in rank units (0..4) → multiplicative damping: same
    # severity keeps the score, 1 tier off ×0.85, 2+ tiers ×0.6.
    dist = abs(_SEV_RANK.get(fa.get("severity"), 0) - _SEV_RANK.get(fb.get("severity"), 0))
    factor = {0: 1.0, 1: 0.85}.get(dist, 0.6)
    return base * factor


def diff(run_a, run_b, threshold=0.5):
    fa = run_a.get("findings", [])
    fb = run_b.get("findings", [])
    # Score all cross pairs, then greedily take the best unused pairs first.
    pairs = []
    for i, a in enumerate(fa):
        for j, b in enumerate(fb):
            s = _candidate_score(a, b)
            if s >= threshold:
                pairs.append((s, i, j))
    pairs.sort(reverse=True)
    used_a, used_b, matched = set(), set(), []
    for s, i, j in pairs:
        if i in used_a or j in used_b:
            continue
        used_a.add(i)
        used_b.add(j)
        matched.append((i, j, s))
    only_a = [i for i in range(len(fa)) if i not in used_a]
    only_b = [j for j in range(len(fb)) if j not in used_b]

    def sev_of(run, idx):
        return run["findings"][idx].get("severity")

    severity_changes = [
        {"a": _finding_view(fa[i]), "b": _finding_view(fb[j]), "score": round(s, 3)}
        for i, j, s in matched
        if sev_of(run_a, i) != sev_of(run_b, j)
    ]
    return {
        "counts": {
            "run_a": len(fa), "run_b": len(fb),
            "matched": len(matched),
            "only_in_a_dropped": len(only_a),
            "only_in_b_new": len(only_b),
        },
        "weighted_overall": {
            "a": run_a.get("raise_posture", {}).get("weighted_overall"),
            "b": run_b.get("raise_posture", {}).get("weighted_overall"),
        },
        "matched_with_severity_change": severity_changes,
        "only_in_a_dropped": [_finding_view(fa[i]) for i in only_a],
        "only_in_b_new": [_finding_view(fb[j]) for j in only_b],
        "match_rate": round(len(matched) / max(len(fa), len(fb), 1), 3),
    }


def _print_report(d, path_a, path_b):
    c = d["counts"]
    w = d["weighted_overall"]
    print(f"Scan diff — A={path_a}  B={path_b}")
    print(f"  findings: A={c['run_a']}  B={c['run_b']}  "
          f"matched={c['matched']}  (join rate {d['match_rate']:.0%})")
    print(f"  weighted_overall: A={w['a']}  B={w['b']}")
    if d["only_in_a_dropped"]:
        print(f"\n  DROPPED (in A, not B) — {c['only_in_a_dropped']}:")
        for f in d["only_in_a_dropped"]:
            print(f"    [{f['severity']}] {f['summary']}")
    if d["only_in_b_new"]:
        print(f"\n  NEW (in B, not A) — {c['only_in_b_new']}:")
        for f in d["only_in_b_new"]:
            print(f"    [{f['severity']}] {f['summary']}")
    if d["matched_with_severity_change"]:
        print("\n  SEVERITY CHANGED (matched, different severity):")
        for m in d["matched_with_severity_change"]:
            print(f"    {m['a']['severity']} -> {m['b']['severity']}  "
                  f"(join {m['score']:.0%})  {m['b']['summary']}")
    if not (d["only_in_a_dropped"] or d["only_in_b_new"]
            or d["matched_with_severity_change"]):
        print("\n  No dropped / new / severity-changed findings — runs agree.")


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="scan_diff.py",
        description="Mechanical scan-vs-scan diff for Praxen findings JSON (schema 3.0).")
    ap.add_argument("run_a", metavar="RUN_A.json")
    ap.add_argument("run_b", metavar="RUN_B.json")
    ap.add_argument("--threshold", type=float, default=0.40,
                    help="min similarity to call two findings the same (default 0.40, "
                         "tuned on real same-target run pairs)")
    ap.add_argument("--json", action="store_true", help="emit the diff as JSON")
    args = ap.parse_args(argv)

    a, b = _load(args.run_a), _load(args.run_b)
    d = diff(a, b, threshold=args.threshold)
    if args.json:
        json.dump(d, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        _print_report(d, args.run_a, args.run_b)
    return 0


if __name__ == "__main__":
    sys.exit(main())
