<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Release 1.1 — Retrospective Review

> Companion doc to `RELEASE_1.1_PLAN.md` and `RELEASE_1.2_PLAN_REVIEW.md`.
> Written 2026-07-15, reviewing the shipped `v1.1.0` (tagged 2026-07-12) plus the
> 1.0.1 / 1.0.2 releases that carried it, against the plan, the tracking issues
> (#167, #168, #169), the checkpoint data (`tests/runs/v1.1-checkpoint/`), and the
> shipped baseline (`tests/baselines/v1.1-claude48/`). All claims below were
> verified against the committed artifacts, not just the docs.

## Verdict in one paragraph

The 1.0.1 → 1.0.2 → 1.1.0 arc is a healthy, well-run release train with an
unusually strong measurement culture: every change was graded against a frozen
reference, over-steering was caught and pulled back, and the honest-caveats
habit (checkpoint caveat blocks, watch-items, the 5-lane re-review that filed
#173/#174) is a real asset. Three things need attention: **(1)** the shipped
v1.1 anchor contradicts the shipped KB on the exact proof case that motivated
the release's headline issue (#169's craftbot LLM08 — still untagged); **(2)**
the release's own success metric was redefined mid-flight without saying so in
one place, leaving `CHECKPOINT.md` and `BASELINE.md` telling contradictory
stories; **(3)** plan-doc and issue hygiene has drifted badly enough that the
repo's paper trail no longer matches what shipped.

---

## What was planned vs. what shipped

`RELEASE_1.1_PLAN.md` scoped 1.1 as **"Scoring & Tagging Rigour"** — three
items: **#48** (RAISE scoring control-ledger + boundary rules), **#169** (OWASP
distillation sharpening), **#111** (tag-label separator). What shipped in 1.1.0
is **tagging only**: #169's KB sharpening, the primary/secondary rendering
layer, #111's normalization, and a re-tagged (not re-scanned) baseline. #48 was
pushed to 1.2 mid-release (commit `8d047b3` on the `1.1` branch).

**The descope itself was the right call.** Bundling a scoring change into the
same release as the tagging change would have destroyed the ability to grade
either one — and `v1.1-claude48` as the pristine, scoring-unchanged "before"
for #48 is genuinely more valuable than shipping both at once. The 1.2 plan's
bucket G framing ("kept scoring constant *precisely so* v1.1 is the clean
before") reads slightly post-hoc — that argument was equally available for
v1.0.2 when the plan was written — but the engineering outcome is correct.

**The problem is the paper trail, not the decision:**

- `RELEASE_1.1_PLAN.md` on `main` still scopes #48 into 1.1, still carries an
  all-unchecked deliverables checklist, and still says "Closes: #48, #111, #169."
  None of those closed.
- Tracking issue #168 ("Scoring & Tagging Rigour") still describes the
  two-halves scope and remains open with no descope comment.
- The shipped release is therefore named and documented as something it isn't.
  A newcomer reading the plan doc would conclude 1.1 failed half its scope.

**Recommendation:** when a release descopes, annotate the plan doc at the
moment of the decision (a dated "Descoped" strike-through block, the way #169's
reframe was handled — that one was done right). Close or re-scope #168 with a
comment pointing at 1.2 bucket G.

## What shipped, graded

### The tagging work (#169) — mostly delivered, with one real hole

**Delivered and verifiable in the anchor:**

- **LLM05 genuinely recovered**: 4 primary / 6 secondary on the code-exec
  findings via the LLM05/LLM06 orthogonality rule. This also correctly
  downgraded the 1.2 plan's "backfill output-handling targets" contingency.
- **The secondary layer is real**: co-applicable chips went 3 → 28, and the
  primary distribution stayed stable across independent cold passes (LLM06
  robustly the largest at 23P). Primary/secondary rendering end-to-end is a
  genuine report-quality improvement.
- **The boundary rules read well**: ASI08/ASI10-as-outcomes, the
  gate-vs-validation LLM05/LLM06 split, and "logging is RAISE, not OWASP" are
  each defensible, clearly worded, and — critically — were arrived at by
  *correcting an over-steer* (see below), which is how you know they're
  calibrated rather than aspirational.

**The hole — the proof case regressed and nobody wrote it down:**

#169's entire evidentiary core is craftbot-005: a live ChromaDB store the agent
auto-writes from its own conversation — "textbook LLM08," per the issue, with a
smoking-gun table. The shipped KB (`KB_LLM_TOP10.md` §LLM08) now says, in bold:
*"When the agent can write to its own store from its own conversation, LLM08 is
the dominant frame, not a secondary tag."*

**The shipped v1.1 anchor contains zero LLM08 tags — primary or secondary —
anywhere in the corpus.** craftbot-005 ships as LLM01 + ASI06 (+ ASI10/ASI05
secondaries), exactly the pre-fix tagging the issue called out. The Phase-1
checkpoint run *had* recovered LLM08 (0 → 4: craftbot, salesforce, hermes,
aider); the final clean-pass re-tag lost it again, and `BASELINE.md` glosses
this as "LLM08 is not exercised as a primary in this corpus" — which is
technically true and materially misleading, since it isn't exercised as a
secondary either, and the KB says this exact finding should be dominant-LLM08.

So: guidance and anchor disagree on the release's own proof case, the
regression isn't tracked anywhere (#169 is open but doesn't note it), and both
LLM08 and ASI08 remain zero columns in the coverage matrix the 1.2 plan is
making decisions from.

**Recommendation:** don't hand-edit the anchor (the discipline is right); do
file the regression on #169 explicitly, and fold a craftbot/salesforce/hermes/
aider re-tag pass into the next scheduled tagging run (the #173/#174 batch or
the v1.2 freeze). #169 must not close while its proof case is untagged.

### The metric that quietly changed

The plan gated tagging success on "untagged-rate down from 21% toward ~7%."
The checkpoint reported a triumphant 21% → 5%. The shipped anchor is **22%**
(25/114) — and `BASELINE.md` reframes that as "honest taxonomy reach"
(logging/observability/config findings are RAISE-only by design, so they
*should* be untagged).

The reframe is actually correct — the original ~7% goal counted findings that
the sharpened KB now deliberately excludes from OWASP, so the *metric* was
wrong, not the result. And the intermediate 5% was the product of the
over-steered pass (ASI10 0 → 27, LLM06 20 → 50) that the recalibration
correctly reverted — catching that over-steer before freeze is the single best
piece of judgment in the release.

But nothing in the repo says this in one place. `CHECKPOINT.md` (5%, ASI10=27,
"Phase 1 did what #169 promised") and `BASELINE.md` (22%, ASI10=5S) describe
two different tagging policies with no bridging note, and the CHANGELOG doesn't
mention that the release's stated success criterion was retired as
miscalibrated. A careful reader — or a future you grading #48 the same way —
gets whiplash.

**Recommendation:** add a superseded-by note to `CHECKPOINT.md` (it reflects
the pre-recalibration policy) and a line to the 1.1 CHANGELOG entry or
`BASELINE.md`: "the plan's ~7% untagged goal was retired — under the corrected
taxonomy, ~22% untagged is the honest floor." Lesson for 1.2: **when a success
metric turns out to be wrong, retiring it is fine; retiring it silently is
how metric-gaming habits start.**

### Release mechanics — one real wobble

The v1.1.0 release build failed at the docs-freshness backstop *after the tag
was cut*, forcing a fix-up commit, a dev↔main re-sync, and a **force-update of
the published v1.1.0 tag** (#177 → #178). Re-pointing a published tag is the
kind of thing that breaks downstream consumers (anyone who fetched between cut
and re-point has a divergent tag) and it will bite harder as install volume
grows.

**Recommendations:** (a) pull #178 (CI docs-freshness on PRs) immediately — it
is small, and it structurally blocks every future release the same way; (b)
adopt a "never re-point a published tag" rule — if the artifact is broken,
ship `X.Y.Z+1` (release-cadence memory notwithstanding; a broken release is the
exception that justifies a fast follow).

### Issue hygiene — a sweep is overdue

Shipped-but-still-open: **#137** (shipped in 1.0.1), **#64/#116** (targets added
in 1.0.2), **#69/#70** (retirements executed in 1.0.2 — #70's "replace, don't
drop" intent is the one live remnant; see the 1.2 review), **#111** (shipped in
1.1.0), **#167/#168** (both releases shipped). The CHANGELOG's "Closes #…"
lines never fired because merges land on `dev`, not the default branch. Ten
minutes of closing with pointer comments restores the signal value of the open
list — right now 9 of 35 open issues are already done.

## Direction of the project — commentary

**What the arc says, positively:** the project has developed a distinctive and
genuinely rare methodology — frozen median-of-3 anchors, graded releases,
"fix the input, never the output," adversarial self-review before freeze. The
1.0.2 remit-refresh work (measuring old-remit → new-remit on a fixed skill to
isolate the remit effect; the Hermes three-way remit investigation in O8) is
the kind of experimental hygiene most eval projects never reach. This is the
project's moat and it's compounding.

**Two strategic tensions worth naming:**

1. **The externally-cited #1 weakness keeps slipping.** The July Deep Research
   assessment (quoted on #48) names run-to-run RAISE variance as Praxen's
   single most substantive criticism. #48 was 1.1's bucket A; it is now 1.2's
   bucket G. Meanwhile three of the last five main-merges are news/SEO/site
   work. Adoption marketing is legitimate — but the thing reviewers say is
   wrong with the product has now been deferred through two releases while
   polish shipped. 1.2 must not repeat this (see the companion review).

2. **The review gate died with no replacement.** Gemini Code Assist sunsets
   **2026-07-17 — two days from this writing** — and #120 is still open. The
   per-PR background-review convention (per the working agreement) covers part
   of it, but the standing "automated second set of eyes on every PR" that
   caught real things (#176 exists because of a Gemini review) has no
   successor. This is now the most time-critical open item in the repo and it
   belongs to no release train. Pull it this week.

**Net:** direction is good — 1.1 shipped a real, verified improvement with the
right discipline. The gaps are all in the connective tissue: docs that lag
decisions, metrics that changed silently, issues that outlived their work, and
one contradiction between guidance and anchor that needs to be on the books
before #48 builds on top of it.
