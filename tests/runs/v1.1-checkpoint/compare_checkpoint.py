#!/usr/bin/env python3
"""Compare v1.1-checkpoint re-scans against the frozen v1.0.2-claude48 baseline.
Counts OWASP category coverage (scalar owasp_llm/owasp_agentic PLUS secondary
codes in tags[]), untagged rate, LLM08 recovery, and ASI10 (rogue/oversight) —
the metrics the #169 tagging sharpening is supposed to move."""
import json, glob, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
CK = os.path.join(HERE, "scans")
FROZEN = os.path.join(HERE, "..", "..", "baselines", "v1.0.2-claude48")
CODE_RE = re.compile(r"(LLM\d{2}|ASI\d{2})")

def codes_of(f):
    """All OWASP codes on a finding: the two scalars + any in tags[] (labels or bare)."""
    out = set()
    for k in ("owasp_llm", "owasp_agentic"):
        v = f.get(k)
        if v:
            m = CODE_RE.search(str(v));  out.add(m.group(1)) if m else None
    for t in (f.get("tags") or []):
        s = t.get("label", "") if isinstance(t, dict) else str(t)
        m = CODE_RE.search(s)
        if m and (not isinstance(t, dict) or t.get("kind", "").startswith("owasp")):
            out.add(m.group(1))
    return out

def scalar_untagged(f):
    return not f.get("owasp_llm") and not f.get("owasp_agentic")

def load_frozen(slug):
    g = glob.glob(f"{FROZEN}/{slug}/*-findings-*.json")
    return json.load(open(g[0]))["findings"] if g else None

def summarize(findings):
    cat = collections.Counter()
    untag = 0
    for f in findings:
        for c in codes_of(f):
            cat[c] += 1
        if scalar_untagged(f):
            untag += 1
    return len(findings), untag, cat

SLUGS = ["aider","autogen-code-executor","craftbot","deepagents-cli","finbot",
         "helperbot","hermes-agent-desktop","openai-customer-service","openhands",
         "salesforce-help-agent-accelerator","uagents","yaah"]

print(f"{'target':34} {'frozen(n/untag)':>16} {'new(n/untag)':>16}  LLM08 f→n  ASI10 f→n")
agg = {"fn":0,"fu":0,"nn":0,"nu":0}
fcat_tot, ncat_tot = collections.Counter(), collections.Counter()
done = []
for slug in SLUGS:
    ck = f"{CK}/{slug}.json"
    if not os.path.exists(ck):
        continue
    try:
        newf = json.load(open(ck))["findings"]
    except Exception as e:
        print(f"{slug:34}  [checkpoint JSON invalid: {e}]");  continue
    frf = load_frozen(slug)
    if frf is None:
        print(f"{slug:34}  [no frozen baseline]");  continue
    done.append(slug)
    fn, fu, fcat = summarize(frf)
    nn, nu, ncat = summarize(newf)
    agg["fn"]+=fn; agg["fu"]+=fu; agg["nn"]+=nn; agg["nu"]+=nu
    fcat_tot += fcat; ncat_tot += ncat
    print(f"{slug:34} {f'{fn}/{fu}':>16} {f'{nn}/{nu}':>16}  {fcat['LLM08']}→{ncat['LLM08']}      {fcat['ASI10']}→{ncat['ASI10']}")

print("-"*90)
if done:
    fpct = 100*agg['fu']//max(agg['fn'],1); npct = 100*agg['nu']//max(agg['nn'],1)
    tot_lbl = f"TOTAL ({len(done)} targets)"
    fcol = f"{agg['fn']}/{agg['fu']}"; ncol = f"{agg['nn']}/{agg['nu']}"
    print(f"{tot_lbl:34} {fcol:>16} {ncol:>16}")
    print(f"\nUntagged rate: frozen {fpct}%  →  new {npct}%")
    print("\nPer-category coverage (frozen → new), counting scalar + tags[]:")
    for fam in ("LLM","ASI"):
        for i in range(1,11):
            c=f"{fam}{i:02d}"
            if fcat_tot[c] or ncat_tot[c]:
                mark = "  <== zero→nonzero" if (fcat_tot[c]==0 and ncat_tot[c]>0) else ("  <== nonzero→zero" if (fcat_tot[c]>0 and ncat_tot[c]==0) else "")
                print(f"  {c}: {fcat_tot[c]:3} → {ncat_tot[c]:3}{mark}")
    print(f"\nCategories covered: frozen {sum(1 for c in fcat_tot if fcat_tot[c])}/20  →  new {sum(1 for c in ncat_tot if ncat_tot[c])}/20")
print(f"\n(checkpoint targets present: {len(done)}/12 — {', '.join(done) or 'none yet'})")
