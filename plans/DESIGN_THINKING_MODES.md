<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Design — Praxen Thinking Modes (#197)

> **STATUS: DESIGN — approved 2026-08-10; ships as release 1.3** (the accuracy
> release — see `RELEASE_1.3_PLAN.md`), deliberately **ahead of** the
> detection/re-baseline release, which renumbered to 1.4. Ordering rationale in
> the 1.3 plan. Freeze-independent by construction (see §8).

## 1. Purpose

Operationalize our proven manual best practices for the "fuzzy" parts of a
scan, as opt-in accuracy tiers — the way LLMs expose effort levels. Two facts
motivate this:

- The 1.2 post-freeze **FP scrub** (one independent, context-unaware reviewer
  per target) worked: zero detector false positives confirmed, and a recurring
  remit over-reach class surfaced that nothing else had caught.
- The **median-of-3** baseline discipline works, but as used today it only
  *measures* variance; the discovery half (what runs find that other runs
  miss) is thrown away.

Thinking modes automate both. They are **complementary to, not a substitute
for, single-run accuracy work** (#48, #195, #196, #198 — prompt engineering,
python translation of judgment-free steps, rubric sharpening). Those shrink
variance at the source; as long as an LLM is in the loop, residual variance
remains — the modes damp what remains.

## 2. The modes

| Mode | What runs | Cost (rough) | When |
|---|---|---|---|
| **standard** | Today's scan, byte-for-byte unchanged | 1× | Default. Baselines, bands, everyday scans |
| **high** | Scan → context-unaware findings audit → cleanup + re-render | ~2× | Before a report leaves your hands |
| **x-high** | 3 independent scans → union → evidence adjudication → one super-run | ~4–5× | Audits, gates, anything where quality outranks time/tokens |

Selected per-invocation in natural language ("run a Praxen analysis in high
thinking mode"). No config file, no standing state (consistent with #2's
deferral). Unrecognized/absent mode ⇒ standard.

**Measured cost (Opus 5, 2026-08-11 dry-runs; the "Cost (rough)" column is a
token estimate — actual numbers below).** Wall-clock expansion runs *lower*
than the token multiple, because the audit is a finding-bounded re-read (not a
second discovery pass) and x-high's three scans run concurrently:

| Mode | Tokens (measured) | Wall-clock (measured) | Absolute (Opus 5) |
|---|---|---|---|
| **standard** | 1× | 1× | ~215k–265k tok, ~14–19 min |
| **high** | ~1.4–1.5× | **~1.3–1.6×** (scan + a few min audit) | ~305k–395k tok, ~17–28 min |
| **x-high** | **~4.0×** | ~2.0–2.5× (parallel scans + one adjudication) | ~0.9M tok, ~30–35 min |

Per-target: high FinBot 1.41×tok/1.27×wc, Aider 1.40/1.52, CraftBot 1.52/1.57,
uAgents 1.42/—; x-high FinBot 4.06×tok/~2.25×wc.

**Token burn and wall-clock diverge, and the divergence is the budgeting
point.** Parallelism cuts x-high's *wall-clock* (three scans overlap at ~15
min) but not its *token bill* — three full scans' tokens are spent regardless
of concurrency, plus a scan-sized adjudication pass (the adjudicator re-runs
Steps 5–12 on the union), so ~3× + ~1× ≈ 4× tokens at ~2.25× wall-clock. High
mode's audit is a finding-bounded re-read: ~90k–135k tokens / ~4–10 min on top
of the scan (scales with finding count × evidence density — subtle production
agents audit slower than dense demo apps). The docs keep the round multiples
(~2× / ~4–5×) as conservative planning ceilings; operator guidance carries both
measured axes and says to budget by tokens, not the clock
(`docs/thinking-modes.md`).

## 3. First principles

1. **Evidence decides membership; run-count decides nothing.** A finding seen
   by one run of three that survives refutation against the code **stays**. A
   finding seen by all three that fails verification **dies**. Vote counting —
   in either direction — is consensus-by-the-back-door and is banned.
2. **No score selection, no score blending.** The x-high score is **re-derived
   from the adjudicated finding set** by the normal SKILL scoring rules — a
   real single scan's score computed on better-vetted inputs. This keeps the
   standing rule intact: the product is one scan → one score; we never
   union/median/average scores as a user-facing deliverable.
3. **The auditor is genuinely context-unaware.** A fresh agent that receives
   only: the findings JSON, the remit, and the workspace — with an explicit
   refutation mandate. A same-session "review your own findings" pass inherits
   the scan's confirmation bias and is worthless; this is what made the manual
   scrubs work.
4. **Every disagreement becomes a diagnostic.** Cross-run flips and audit
   kills are logged as a variance artifact. "Found once, refuted" = detector
   wobble (feeds #48/#195/#196). "Found by all three, refuted" = systematic
   error, likely remit-defect class (feeds #198). The mode both improves the
   run *and* generates the raw material for fixing the detector — honoring
   "a flipping finding = fix the detector, not aggregate runs."

## 4. High mode — pipeline

**Phase 1 — standard scan to completion.** Full pipeline through validated
canonical JSON + rendered report. If later phases fail or are aborted, the
operator still holds a complete standard result (graceful degradation).

**Phase 2 — findings audit.** Fresh context-unaware agent (subagent where the
harness supports it; see §7). Inputs: findings JSON, remit, workspace path,
and a written audit brief. Mandate: for **each** finding, re-read every cited
artifact and attempt refutation. Verdict per finding — three-way, because the
1.2 scrub proved the binary version discards the most valuable signal:

- **CONFIRMED** — evidence holds as cited.
- **UNSUPPORTED** — the cited evidence does not support the claim (wrong
  reading, stale line, over-claim beyond what the code shows).
- **REMIT-DEFECT** — the evidence holds and the finding honestly violates the
  rule *as written*, but the rule itself is fabricated, over-reaching, or
  contradicts documented behavior (the #198/#200/#201 class).

Guardrails against an over-zealous auditor: a verdict of UNSUPPORTED requires
citing what the auditor actually read that contradicts the claim — "could not
verify quickly" is CONFIRMED-by-default territory, not a kill; severity
re-grading is out of scope (that's #48's axis); the auditor never proposes new
findings (discovery is x-high's job, via more runs — not the auditor's).

**Phase 3 — cleanup + re-render.** UNSUPPORTED findings are removed from the
findings JSON (original IDs are never reused; gaps are provenance).
REMIT-DEFECT findings are removed from the findings register and recorded as
**remit feedback** in the adjudication artifact — the remit owner's fix list,
not the agent's risk list. RAISE category scores are re-derived **only** where
a removed finding was load-bearing in that category's rationale. Pipeline
re-runs (manifest → findings → render) to produce the final report.

## 5. X-high mode — pipeline

**Phase 1 — three independent standard scans.** Fresh context each, zero
shared state, parallel subagents where the harness supports them (the
regression suite already runs 4–8 concurrent), sequential otherwise. Three
canonical findings JSONs.

**Phase 2 — union + matching.** Findings matched across runs by **rule text +
evidence overlap + claim semantics — never R-IDs** (rule IDs are run-local
enumerations). `tests/scan_diff.py` is the assist tool, with its known limit
treated as a rule: the 0.40 join threshold under-matches rewordings, so every
"unmatched" item is hand-verified by the adjudicator before being treated as
unique. Output: the deduplicated union, each entry carrying found-in-runs
provenance.

**Phase 3 — adjudication.** Fresh context-unaware adjudicator applies the
§4 audit (same three-way verdicts, same guardrails) to **every union member**
— principle 1 governs: membership is decided by evidence alone. For matched
duplicates, the canonical record is the instance whose evidence chain verified
most completely (selection over synthesis — verifiable provenance beats
blended prose); verified evidence citations from sibling instances may be
merged into its evidence list.

**Phase 4 — super-run assembly.** The adjudicated set gets fresh sequential
IDs (per-run IDs recorded in the adjudication artifact). Category scores and
all report prose are re-derived from the adjudicated set per normal scoring
rules. One canonical findings JSON, one report — plus:

- **Adjudication record** — per finding: found-in runs, verdict, evidence
  status, source instance, rationale.
- **Variance diagnostic** — the flip inventory (found-in-1 verified / refuted,
  found-in-3 refuted, score spread of the three raw runs vs the final derived
  score). This is the #48 feedstock and gets attached to any future
  re-baseline analysis.

## 6. Artifacts, schema, and what stays untouched

- **Canonical findings JSON: schema 3.0, no new fields, v1.** The mode and
  adjudication live in a separate artifact
  (`reports/<slug>-adjudication-<timestamp>.md`) plus naturally in the
  report's existing prose fields. A proper `scan_mode` / revision-provenance
  schema field is deliberately deferred to ride a re-baseline release together
  with #118 (operator overrides want the same provenance shape — design once).
- **`report_template.html` / `render.py`: untouched.** Standard-mode renders
  must remain byte-identical (the render gate enforces this); nothing in v1
  requires a template change.
- **Skill packaging:** mode instructions live in a **separate file**
  (`skills/behavior-verifier/THINKING_MODES.md`) loaded only when a
  non-standard mode is requested. SKILL.md gains only a short pointer. That
  pointer is a skill-prose change and gets the #216 treatment: a blind
  standard-mode gate scan of a baseline target must land in-band before ship.

## 7. Harness reality

- **Claude Code:** subagents give real context isolation for the auditor /
  the three scan runs / the adjudicator. Full automation.
- **Codex:** reports the same capability — sub-agents spawned with
  `fork_turns="none"` get a genuinely fresh context (no parent conversation
  history), async, same workspace. Full automation on both primary harnesses;
  **verify empirically at implementation time** (a quick isolation probe: the
  child must not know a fact only the parent context holds) before relying on
  it. Shared-workspace caveat: phases write to disk sequentially, so no
  simultaneous-edit coordination is needed.
- **Any other harness:** fallback is sequential phases where phase 1 writes
  the audit brief + inputs to disk and the operator starts a **fresh session**
  for the audit phase. Semi-automated, honestly documented as such. The
  artifacts themselves assume nothing harness-specific.
- Docs state plainly: isolation quality is what makes the audit worth
  anything; a harness that can't isolate gets the manual-fresh-session recipe,
  not a fake same-context "audit."

## 8. Baselines, bands, and release packaging

- Frozen baselines and per-target bands are **standard-mode artifacts**.
  Thinking-mode outputs are never graded against standard bands, and no
  baseline is ever frozen in a thinking mode. Docs state cross-mode scores are
  not comparable-by-band.
- **Corrected 2026-08-11 by the §9.2/§9.5 validation** (`RESULTS_XHIGH_VALIDATION.md`):
  the original "expected direction: equal or cleaner" is **wrong in
  direction**, and the claim that x-high "damps score variance" is **not
  supported by the data**. Measured: adjudication *adds* verified findings
  (12 single-run rescues across 4 super-runs, ~1 kill total), so super-run
  scores trend **lower** than the raw runs (uAgents −0.125, AutoGen −0.017 vs
  raw means). And two independent super-runs differed by exactly the raw
  6-run range on both targets (0.15 / 0.25) — with **five of six categories
  agreeing exactly** and the entire delta coming from one band-edge category
  call. The honest statement, now in the docs: **x-high stabilises and expands
  the finding set; per-category anchoring (#195) is what still moves the
  score, and x-high inherits that rather than fixing it.**
- **Freeze-independent satellite.** Standard path unchanged (modulo the
  gate-scanned SKILL pointer), no schema change, no template change ⇒ this can
  ship as a 1.2.x satellite or alongside 1.3 without riding the v1.3-opus5
  freeze. If implementation slips into 1.3 proper, it still doesn't join the
  freeze-gated bucket.

## 9. Acceptance

1. **High-mode proof (regression against the human scrubs):** run high mode on
   the 1.2 FP-scrub targets; the audit must independently surface the same
   remit over-reach catches the human scrub logged (scrub reports exist as
   ground truth). Spot-check every UNSUPPORTED verdict by hand on the first
   runs — audit precision is the make-or-break metric; an auditor that kills
   true positives is worse than no auditor.
2. **X-high stability proof:** two full x-high super-runs on a historically
   wide-band target (autogen or uAgents). Success = super-run finding sets
   near-identical and score delta well inside the target's historical
   single-run band. A super-run *pair* that wobbles like single runs means the
   adjudication isn't doing its job.
3. **Standard-mode non-regression:** byte-identical renders (existing gate)
   plus the blind in-band gate scan for the SKILL pointer change.
4. **Duplicate audit:** the x-high output contains no unmatched duplicates
   (scan_diff assist + adjudicator hand-check is the mitigation; this test is
   the proof it worked).
5. **Discovery yield — does x-high catch verified findings a single run
   misses?** (Added 2026-08-11 at Steve's direction; the stability proof in
   §9.2 measures the *damping* half, this measures the *discovery* half, and
   it is why principle 1 bans vote-counting.) For every finding in the
   adjudicated super-run set, record how many of the three raw runs found it
   (`k` ∈ {1,2,3}); **expected single-run recall = Σ(k/3) / N**. The
   complement is the share of verified findings an ordinary single scan would
   have missed on average. Grade it **overall and by severity tier** — a
   missed Critical and a missed Medium are not the same result. Pass = the
   super-run demonstrably contains verified findings a single run would have
   missed, with the rescue rate stated, not asserted.

   *Prior data point (FinBot x-high, 2026-08-11):* 19 union entries — 11
   found-in-3, 4 found-in-2, 4 found-in-1 → **expected single-run recall
   78.9%**, i.e. an ordinary scan misses ~21% of the verified set. Severity
   split matters: **all 6 Criticals were unanimous** (found by all three
   runs), and every single-run rescue was Medium or Low. On this target the
   headline risks reproduced reliably and the discovery payoff sat entirely in
   the tail. Whether that holds on the wide-band targets — or whether
   Criticals themselves flip there — is the open question the §9.2 pairs on
   autogen/uagents answer.

## 10. Risks

| Risk | Mitigation |
|---|---|
| Over-zealous auditor kills true positives | Refutation requires cited contradicting evidence; CONFIRMED is the default when evidence holds; hand spot-check on first runs (§9.1) |
| Matching errors (dupes or false-uniques) in x-high | scan_diff assist + mandatory hand-verification of unmatched items; §9.4 |
| Adjudicator context pressure on large targets | Artifact-driven pipeline — all inputs on disk; adjudicate in finding-batches, never "hold everything in context" |
| Manifest fragility ×4 (#217) | Mid-draft `--validate-manifest` is already standard practice; x-high multiplies exposure, not failure modes |
| Codex isolation weaker | Fresh-session fallback documented as semi-automated; no pretend-isolation |
| Cost surprise | Mode table (§2) in docs; the skill states the expected multiple when a mode is invoked |

## 11. Issue map

#197 (this design) · consumes/feeds: #48, #195, #196 (variance diagnostics) ·
#198, #200, #201 (REMIT-DEFECT verdicts are the generator's fix list) · #118
(schema provenance — deferred, designed together later) · #217 (manifest
fragility, multiplied not changed) · #2 (no standing config — modes stay
per-invocation).
