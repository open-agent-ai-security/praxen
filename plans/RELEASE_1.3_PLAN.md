<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxen 1.3 — Thinking Modes (the accuracy release)

> **STATUS: PLANNED — approved 2026-08-10** (Steve: numbering + ordering
> confirmed; "Modify the plans accordingly"). Branches from `dev` after the
> post-1.2.1 plans sync lands on `main`. **Ships before the detection /
> re-baseline release, which is now 1.4** (`RELEASE_1.4_PLAN.md` — formerly
> the 1.3 plan; renumbered when this feature was promoted from "1.2.x
> satellite" to its own minor release).
>
> The design is the contract: **`plans/DESIGN_THINKING_MODES.md`** (#197).
> This plan only adds release packaging around it.

## Objective

Ship opt-in accuracy tiers — **standard / high / x-high** — that
operationalize the proven manual practices for the fuzzy parts of a scan (the
1.2 FP scrub, the multi-run discipline), per the design's first principles:
evidence decides membership, run-count decides nothing; scores are re-derived
from the adjudicated finding set, never selected or blended; the auditor is
context-unaware; every disagreement becomes a variance diagnostic.

**Score-inert by construction.** Standard path stays byte-identical; no
schema change; no template change; no re-freeze. `v1.2-opus5` remains the
current baseline set, and 1.3 output is never graded against standard-mode
bands.

## Why before 1.4 (the ordering decision, 2026-08-10)

1.4 is the scan-heaviest, judgment-heaviest release planned — #48 before/after
grading, #200/#201 remit re-scrubs, detection proof cases, a full 12-target
re-freeze. Building the modes first means: high mode runs the re-scrubs the
humans ran in 1.2; x-high's variance diagnostics are the #48/#195/#196
feedstock, generated as a byproduct; freeze candidates get high-mode audits
before freezing (the freeze itself stays standard-mode median-of-3). Building
after would mean doing all of that by hand once more, then automating it.

## Contents

1. **#197 — Thinking Modes v1**, exactly per `DESIGN_THINKING_MODES.md`:
   `THINKING_MODES.md` mode instructions (separate file; SKILL.md gets only a
   gate-scanned pointer), high-mode pipeline (audit brief, three-way verdicts,
   cleanup + re-render), x-high pipeline (3× scan, union + matching with
   `scan_diff.py` assist, adjudication, super-run assembly), adjudication +
   variance artifacts, harness isolation docs (Claude Code subagents; Codex
   `fork_turns="none"` sub-agents — verify isolation empirically per design
   §7; fresh-session recipe for any other harness), user docs incl. the cost
   table.
2. **#226 leftovers** *(rider — docs-only)*: the verified list on the issue —
   quickstart `PRAX-005` fake ID, llms.txt Codex mention, spec "four files"
   undercount, duplicated "Working with Praxen", plus verify items 10/13
   either way.
3. **#151 Google Antigravity harness** *(optional rider — packaging/docs
   only, engine unchanged)*: pull in if convenient; an external contact is
   waiting. Dropping it to 1.4 needs no plan amendment.

Scope fence, restated from the design: **if this release grows a schema
field, a template change, or any standard-path behavior change, it is no
longer freeze-independent and loses its slot ahead of 1.4.** The `scan_mode`
provenance field is explicitly deferred to ride a re-baseline with #118.

## Gates

- **Standard-mode non-regression:** byte-identical renders (existing CI gate)
  + a blind standard-mode gate scan of a baseline target lands in-band (the
  #216 treatment, for the SKILL.md pointer line).
- **Design acceptance §9:** high mode independently reproduces the 1.2
  human-scrub catches (scrub reports are ground truth; hand spot-check every
  UNSUPPORTED verdict on first runs); an x-high super-run *pair* on a
  historically wide-band target (autogen or uAgents) holds finding sets
  near-identical with score delta well inside the historical single-run band;
  no unmatched duplicates in x-high output.

## Release mechanics

Standard flow (per `feedback_dev_main_branching` + the 1.2.1 record): work on
a feature branch → squash to `dev` → promotion PR (merge commit, FF `dev`) →
tag `v1.3.0` → post-tag sandboxed install smoke (must report 1.3.0) + a
fresh-agent scan check → blog post ("Praxen 1.3: Thinking Modes" — the
feature is the story). Bump reminders: `bump_version.py --dry-run` first;
re-run `tests/render/render_all_remits.py` after the bump (remits stamp the
version at render time — the de-facto seventh surface); ride the
`v1.2.1+` install-confirm floors forward.

## Non-goals

No detection changes, no scoring-rubric changes, no remit regeneration, no
roster changes, no re-freeze — all of that is 1.4. If a mode implementation
detail turns out to require a scoring or schema change, it stops, gets logged
on #197, and waits.
