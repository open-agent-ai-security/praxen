#!/usr/bin/env python3
"""Phase-0 stability comparator: two graph.json runs -> agreement report.

Usage: python3 compare_runs.py <r1/graph.json> <r2/graph.json>

Measures what the probe actually asks: do two independent runs coin the same
structure? IDs are content-derived by spec, so raw id-set Jaccard is the
headline; a fuzzy name-match pass separates "different component" from
"same component, different id coinage" (the failure mode that matters for
the id rule specifically).
"""
import json, sys, difflib

def load(p): return json.load(open(p))

def jaccard(a, b):
    a, b = set(a), set(b)
    return (len(a & b) / len(a | b)) if (a | b) else 1.0, sorted(a - b), sorted(b - a)

def fuzzy_pairs(only1, only2, names1, names2, cutoff=0.6):
    """Greedy fuzzy match of unmatched ids by display name similarity."""
    pairs, used = [], set()
    for i1 in only1:
        best, score = None, cutoff
        for i2 in only2:
            if i2 in used: continue
            r = difflib.SequenceMatcher(None, names1.get(i1, i1), names2.get(i2, i2)).ratio()
            r2 = difflib.SequenceMatcher(None, i1, i2).ratio()
            r = max(r, r2)
            if r > score: best, score = i2, r
        if best: pairs.append((i1, best, round(score, 2))); used.add(best)
    return pairs

def section(title): print(f"\n=== {title} ===")

def main(p1, p2):
    g1, g2 = load(p1), load(p2)
    print(f"r1: {p1}\nr2: {p2}")
    print(f"model r1: {g1.get('model_identity','?')[:80]}")
    print(f"model r2: {g2.get('model_identity','?')[:80]}")

    for kind, key in [("NODES", "nodes"), ("EDGES", "edges")]:
        ids1 = [x["id"] for x in g1[key]]; ids2 = [x["id"] for x in g2[key]]
        j, only1, only2 = jaccard(ids1, ids2)
        section(f"{kind}: {len(ids1)} vs {len(ids2)}, id-Jaccard {j:.2f}")
        if kind == "NODES":
            n1 = {x["id"]: x["name"] for x in g1[key]}; n2 = {x["id"]: x["name"] for x in g2[key]}
            fp = fuzzy_pairs(only1, only2, n1, n2)
            matched1 = {a for a, _, _ in fp}; matched2 = {b for _, b, _ in fp}
            for a, b, s in fp: print(f"  ~ same component, different id: '{a}' vs '{b}' ({s})")
            for x in only1:
                if x not in matched1: print(f"  - only r1: {x}")
            for x in only2:
                if x not in matched2: print(f"  - only r2: {x}")
            union = len(set(ids1) | set(ids2))
            eff = (len(set(ids1) & set(ids2)) + len(fp)) / (union - len(fp)) if union else 1.0
            print(f"  component-level agreement (id-match + fuzzy): {eff:.2f}")
        else:
            for x in only1[:12]: print(f"  - only r1: {x}")
            for x in only2[:12]: print(f"  - only r2: {x}")

    b1 = {b["id"]: b for b in g1.get("trust_boundaries", [])}
    b2 = {b["id"]: b for b in g2.get("trust_boundaries", [])}
    j, only1, only2 = jaccard(b1.keys(), b2.keys())
    section(f"BOUNDARIES: {len(b1)} vs {len(b2)}, id-Jaccard {j:.2f}")
    for x in only1: print(f"  - only r1: {x} ({b1[x]['name']})")
    for x in only2: print(f"  - only r2: {x} ({b2[x]['name']})")

    t1 = [(t.get("owasp") or "none", t.get("stride"), t.get("status")) for b in b1.values() for t in b.get("threats", [])]
    t2 = [(t.get("owasp") or "none", t.get("stride"), t.get("status")) for b in b2.values() for t in b.get("threats", [])]
    section(f"THREATS: {len(t1)} vs {len(t2)}")
    from collections import Counter
    c1, c2 = Counter(x[0] for x in t1), Counter(x[0] for x in t2)
    for code in sorted(set(c1) | set(c2)):
        mark = "" if c1[code] == c2[code] else "  <-- differs"
        print(f"  {code}: r1={c1[code]} r2={c2[code]}{mark}")
    s1, s2 = Counter(x[2] for x in t1), Counter(x[2] for x in t2)
    print(f"  status r1: {dict(s1)}  |  r2: {dict(s2)}")

    a1 = [p.get("name") for p in g1.get("attack_paths", [])]
    a2 = [p.get("name") for p in g2.get("attack_paths", [])]
    section(f"ATTACK PATHS: {len(a1)} vs {len(a2)}")
    for x in a1: print(f"  r1: {x}")
    for x in a2: print(f"  r2: {x}")

    section("LANE FIT NOTES")
    print(f"  r1: {g1.get('notes', {}).get('lane_fit', '')}")
    print(f"  r2: {g2.get('notes', {}).get('lane_fit', '')}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
