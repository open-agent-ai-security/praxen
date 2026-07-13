<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxen 1.2 — Engine reliability, schema evolution, output quality & coverage

## Objective

The **broad functional line** that 1.1 deliberately left out. Where 1.1 tightens the
scoring/tagging *judgment* metadata against a stable engine, 1.2 is the larger, higher-blast-
radius work: schema evolution (which forces a re-baseline), the render/output-quality
overhaul, engine reliability, and new detection surface. Sequenced **after** 1.1 is frozen, so
each of these lands against a metadata layer that's already been made consistent.

## Prerequisite
Fold **1.1** in first. 1.2 branches from `1.1`. Because #7 (schema arrays) forces a
re-baseline, 1.2 re-freezes `v1.2-claude48` at release.

## Buckets (re-triaged out of the old #168)

### A · Schema evolution *(forces a re-baseline)*
- **#7** — structure `policy_rule_text` / `policy_rule_ids` as arrays; fold into the render-
  pipeline refactor. **Largest single change** — moves the byte-render gate, `schema_version`
  bump, full re-baseline. The reason 1.1 was kept schema-neutral.
- **#5** — `schema.py` validator round 2: `policy_rule_ids` ↔ remit-rule cross-check.

### B · Skill-flow & output quality
- **#33** interleave finding emission with analysis (kill the Step-9.9 synthesis burst / stream-stall)
- **#29** Step-8.5 finding-themes outline first (decomposition primer)
- **#113** wrap technical tokens in `<code>` consistently across prose fields
- **#27** report finding default-state (collapsed/expanded) + expand/collapse-all
- **#25** split output-authoring conventions out of `SKILL.md` (rendering/MVC split)
- **#6** `render.py` polish (confidence, Medium/Low badge)

### C · Engine reliability
- **#65** — framework scanning, manifest resilience, discovery gaps (from the uAgents scan).
  Distinct from the scoring/tagging *judgment* work — this is about scans not stalling/dying
  and handling framework targets robustly.

### D · Detection additions *(may add findings — intended)*
- **#104** entropy-based secret detection in `render.py`'s redaction backstop
- **#41** new named detection pattern: external API response → filesystem write (path-traversal class)
- **Full OWASP category coverage (LLM01–10 + ASI01–10).** Goal: every category exercised by at
  least one baseline target. 1.1's tagging work (#169) is the *first* remedy — it recovers the
  categories that zeroed as **tagging artifacts** (ASI08/ASI10 — behaviors are still found, just
  mis-/under-tagged). What tagging **cannot** recover is a category lost to **target retirement**:
  **LLM05 (Improper Output Handling)** zeroed because we retired the output-handling specialist
  targets. **Contingency (owner of finding #3):** if the 1.1 scoring/tagging tweaks don't restore
  a category, **add new baseline app(s)** here in 1.2 to cover it — LLM05/output-handling is the
  known one to backfill. Measured against the `owasp_coverage.py` matrix (no zero columns).

### G · Scoring rigour (#48) — *explicitly deferred from 1.1*
- **#48** — RAISE scoring-guidance rigour. **Pushed out of 1.1 into 1.2 on purpose:** 1.1 held
  scoring constant (tagging-only) precisely so `v1.1-claude48` is the clean, scoring-unchanged
  *"before"* this work is graded against. 1.2 owns tightening the RAISE rubric — **severity
  anchoring** (decidable Critical-vs-High / Medium-vs-Low criteria) and category-score guidance —
  to shrink run-to-run score variance. Pairs with the **directional-lean** correction in
  "Carried-forward watch-items" below (both need a **human-anchored reference**). Measure
  **median-of-3 on both sides**, graded vs `v1.1-claude48`. Same over-steer/contamination
  discipline the 1.1 tagging work hard-won applies here, amplified — scoring is even more
  seductive to steer than tagging.

### E · Harness support
- **#151** — Google Antigravity (`agy` CLI) as a supported harness.

### F · Docs / low / defer
- **#117** — `challenging-findings.md`: *damage-model-wrong* resolution path + category-score
  *independence* guidance. **Moved here from 1.1** (human-challenge-workflow axis, not automated
  run-to-run variance) and **gated on #118**: if we adopt curated outputs, #117 is the docs half
  of that work; if not, it collapses to a ~1-paragraph note ("challenges resolve by re-analysis;
  category scores are independent") that lands opportunistically.
- **#135** docs simplicity pass (Tier 3) · **#4** SKILL authoring aids · **#118** operator
  override + finding-revision records (provenance; schema-contract change) · **#90** shared org
  brand/design system · **#2** durable version-independent standing config *(explicitly deferred)*.

## Carried-forward watch-items (from 1.1)
- **Scoring directional *lean* (RAISE credit bias).** 1.1 tightens scoring *scatter* (σ) but
  deliberately does **not** gate on directional *bias* — the old→new lean (Zero Trust up,
  Limit-Your-Domain stricter) — because measuring bias needs a **human-anchored reference** we
  don't have. 1.1 only carries a lightweight non-gating check (does the ZT / Limit-Your-Domain
  category-mean drift the *same* direction again vs v1.0.2?). If that check shows the lean is
  structural, **1.2 owns the correction**: pair it with #48's rubric work + a human-anchored
  reference so the scoring center — not just its spread — can be validated.

## Not in 1.2 — pull independently
- **#120** — replace the retired Gemini review gate. **Time-sensitive: Gemini Code Assist
  sunsets 2026-07-17.** Pull **now / independently** of both 1.1 and 1.2; it belongs to no
  theme and cannot wait for either release train.
- **#127** — gate `examples/` in `test_render.py` — **planned for 1.0.2** (PR #160 open, targets
  `dev`; not yet merged). Tracking moves #168 Bucket F → #167 on merge.

## Regression discipline
1.2 also intentionally moves numbers (#7 schema shape, #104/#41 add findings) → re-freeze
`v1.2-claude48`, graded vs `v1.1-claude48`. Because #7 changes the schema contract, plan the
re-baseline + render-pipeline refactor as one coherent migration.

## Clean-run validation (2026-07-12) — empirical inputs for the buckets above
Before prod, all **12 baseline targets were re-scanned by fresh independent agents** (new
agents, source + remit only, no baseline peek) against `v1.1-claude48`. All 12 completed
schema-valid with **zero watchdog deaths**, and **detection reproduced** — the major vulns were
re-found on every target (verified by finding *content*; no genuine misses). The *divergences*
map onto this plan and should inform the work:

- **→ A (#5 / #7 stable rule IDs) — highest-value prod item.** `policy_rule_ids` (`R-NN`) are
  assigned **per-scan** and not tied to the remit, so baseline `R-15` ≠ fresh `R-15`; a
  scan-to-scan diff **can't join on them** (it took hand-matching finding content to confirm
  detection held). With more users you need *mechanical* scan-vs-scan regression detection — #5's
  remit cross-check + #7's arrays are exactly what makes that possible. The clean run is a live
  demonstration of the need.
- **→ B (#29 themes primer / #33 interleaved emission).** Finding *counts* varied widely at equal
  substance (hermes 11 vs 5, aider 11 vs 6) — a decomposition/splitting inconsistency #29/#33
  would stabilise; it also inflates apparent divergence and muddies score comparison.
- **→ C (#65 / #33 reliability).** 0 deaths this run, but several scans ran **13–14 min, right at
  the watchdog edge**; at prod scale (historical ~30% mortality) that's fragile — #65 resilience +
  #33 killing the Step-9.9 synthesis burst address it directly.
- **→ D (coverage) — UPDATE / likely strike.** **LLM05 is no longer a zero column:** 1.1's
  LLM05/LLM06 orthogonality fix recovered it to **4P / 6S** on the code-exec findings. Verify
  against the `owasp_coverage.py` matrix, then the "backfill output-handling targets for LLM05"
  contingency here can likely be **removed**.
- **→ G (#48 scoring) — empirical baseline.** RAISE-score reproducibility: **5/12 exact, mean
  |drift| 0.17 / 5.0, max 0.55**, and it is **entirely severity-calibration on borderline
  findings** (deepagents +0.55 and salesforce +0.45 lean *lenient* — a Critical scored as High).
  This pinpoints **severity anchoring** as #48's lever and names the two worst-offender targets to
  calibrate against. Caveat: single-pass fresh vs a median-of-3 baseline overstates true variance
  slightly — #48 must measure median-of-3 on both sides.

Bottom line for prod sequencing: the reliability wins here are **A (stable IDs, so regressions
are detectable at all)** and **C (engine resilience, so scans don't die at scale)** — ahead of
the output-polish items. 1.1 fixed the *visible* problem (tagging); this run says the
*prod-reliability* problem is schema-stable-IDs + engine-resilience, which is what 1.2 carries.
