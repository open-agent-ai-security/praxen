<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Test plan — auditor FP-injection (booby-trapped baselines)

> **STATUS: ACTIVE — 2026-08-11**, part of the 1.3 Thinking Modes validation
> (#197). Complements acceptance §9.1: the aider/craftbot/uagents dry-runs test
> whether the auditor catches *remit* defects; this test measures whether it
> catches *finding* defects — the UNSUPPORTED verdict, which no organic run has
> exercised (FinBot and aider audits confirmed everything, correctly). Devised
> by Steve, 2026-08-11: *"Take all of the 'baseline' results. Copy them. Insert
> a 'plausible, but fake' finding. Then run the auditor against the booby
> trapped findings… Do we find the FPs?"*

## What is being measured

The high-mode auditor's two error rates, on ground truth we control:

- **FP recall** — given a findings set containing exactly one injected
  plausible-but-fake finding, does the audit kill it (UNSUPPORTED) with the
  required contradicting citation? Missing it = a false positive survives
  high mode, the failure the mode exists to prevent.
- **TP retention** — does the audit confirm every *real* finding? The frozen
  baseline findings are prior ground truth (median-of-3 freeze + the 1.2
  human FP sweep found zero detector FPs). Any real finding killed =
  auditor over-zealousness, the failure §9.1 calls worse than no auditor.

No scans run. The scanner is not under test.

## Inputs

- **Findings (primary run, per Steve 2026-08-11): the scan sets produced
  during the 1.3 dry-runs** — finbot high, a finbot x-high raw run, the
  finbot x-high super-run, aider high, craftbot high, uagents high — copied,
  never mutated in place. Their workspaces are already on disk in the exact
  scanned state, so evidence line references are current by construction.
- **Extension (optional, documented for later):** the 12 frozen
  `tests/baselines/v1.2-opus5/<target>/` findings JSONs against sources
  cloned at the **pinned baseline SHAs** in
  `local/v1.2-owasp2026-baseline/SOURCES.md`. The pin is load-bearing:
  auditing July's findings against today's upstream HEAD would produce
  stale-line kills that are version drift, not auditor skill. (OpenHands
  uses the documented pre-migration re-pin; Hermes stages both pinned
  roots.)
- **Remits:** the staged `WORKER_REMIT.md` each scan actually used
  (`tests/remits/<target>.md`). Scope notes transcribed from
  `tests/scan_instructions/<target>.md` where one exists.

## The injected fake — authoring rules

One fake finding per target, handcrafted by the orchestrator (never by the
auditor's model lineage-with-hints; the injector script only does mechanical
insertion + validation):

1. **Plausible in situ.** Severity Medium or High (never a headline
   Critical), realistic summary/description in the target's own idiom,
   OWASP/RAISE tags consistent with the claim, `policy_rule_ids` either
   `null` or a genuinely related existing `R-NN`.
2. **Cites only real files** — paths that exist at the pinned SHA (reuse
   files already cited by neighboring real findings), with line numbers in
   range. The fake must be refutable only by *reading the code*, never by
   spotting a nonexistent path.
3. **False in substance.** Rotate four fake classes across the suite so one
   refutation style can't carry the test:
   - **A — inverted control:** claims a guard/validation is absent at a
     location where it demonstrably exists.
   - **B — fabricated mechanism:** claims a config key / flag / endpoint /
     code path that does not exist anywhere in the tree.
   - **C — misattributed evidence:** claims file X does Y (plausible for its
     name) when it does Z.
   - **D — over-claim:** takes a real weak signal and asserts a stronger
     consequence the code does not support.
4. **Mechanically clean:** inserted in canonical severity order with an
   unused sequential-style ID, `footer.severity_counts` re-derived, the
   result validated by `schema.py` before use. A fake that fails validation
   is a harness bug, not a test datum.

Injection position and ID give no signal (no always-last, no odd ID shape).

## Protocol

1. Stage per-target dirs (scratchpad, outside the repo): booby-trapped JSON
   copy, remit, pinned workspace clone.
2. Launch the **standard high-mode audit brief, verbatim** (current v3 text
   from `THINKING_MODES.md`) against each — the auditor is told nothing
   about injection, sees no pristine copy, and each target gets a fresh
   agent. Model: the pinned Opus 5 scanner agent, self-report required.
3. Grade each adjudication file:
   - fake verdict = UNSUPPORTED **and** the cited contradicting evidence is
     correct → catch;
   - fake CONFIRMED (or killed for a wrong reason) → miss (record the
     auditor's stated rationale);
   - every real finding CONFIRMED → retention pass; any real kill →
     investigate individually (drift at the pin? auditor error? or a genuine
     latent baseline defect — each disposition recorded).
4. Report: per-target catch/miss + class, suite FP-recall n/12, TP-retention
   count, and any remit-feedback entries (observed but not graded — the
   remits here are the known #200/#201 state).

## Pass expectations

- **FP recall:** every injected fake killed. A miss on class B (fabricated
  mechanism) is the most alarming (pure grep refutes it); misses on class D
  (over-claim) are the most informative about verdict-boundary calibration.
- **TP retention:** zero unexplained real kills across ~150 real findings.
- Verdict-quality guardrail holds: every kill carries a concrete
  contradicting citation (no citation-less kills anywhere).

## Cost / mechanics

12 audit agents (~100k tokens, ~5–10 min each; run 4–6 concurrent), 13
pinned clones (~15 min, OpenHands largest). Harness: a small stdlib injector
script (session scratchpad; formalize into `tests/` only if this becomes a
standing regression — decide at 1.3 close). Artifacts are dry-run working
files; the durable outputs are the graded results table (reported on #197)
and any brief changes they force.

## Addendum — Phase 3 cleanup test (2026-08-11)

The injection test above proves **detection**. It does not exercise **removal**:
its audits stop at verdicts. And because all four organic high-mode runs
confirmed everything, high mode's Phase 3 cleanup path (preserve `-raw`, edit
the audited manifest, re-convert, re-render) had **never executed** — an
untested path in shipping instructions. Closed with this end-to-end test:

1. Injected the class-A fake into the **draft manifest** (not just the JSON),
   proving a fake is manifest-representable; converted → 14 findings, valid.
2. Rendered that as the simulated Phase-1 output; applied the existing audit
   verdict (fake = UNSUPPORTED, 13 others CONFIRMED).
3. Executed Phase 3 verbatim: renamed the three artifacts with `-raw`, wrote
   `<slug>-draft-<TS>-audited.md` with the fake's block removed, re-ran
   `manifest_to_findings.py` then `render.py` at a fresh timestamp.

**Result — every checkpoint passed:**

| Check | Outcome |
|---|---|
| Fake in raw / absent from final | ✅ / ✅ |
| Finding IDs never reused or renumbered | ✅ 001–013, no 014 — the gap is provenance |
| Dangling references to the removed id | ✅ none |
| `footer.severity_counts` re-derived | ✅ medium 5 → 4 |
| Category scores re-derived only if load-bearing | ✅ unchanged (the fake was not load-bearing in any rationale) |
| Raw artifacts preserved alongside final | ✅ `-raw` html/txt/json |
| **Cleaned final vs. the never-injected original** | ✅ **finding-for-finding identical, and the rendered HTML/TXT are byte-identical** |

That last row is the strongest statement available: inject a false positive →
the audit detects it → cleanup removes it → **the result is byte-for-byte what
the scan would have produced had the false positive never existed.** Detection
and removal are both now demonstrated end-to-end.

Residual gap: every fake carried `policy_rule_ids: null` by design, so the
**rule re-status path** (an UNSUPPORTED kill forcing a linked rule from `gap`
back to `verified`/`partial`) is still unexercised. Worth one targeted fake
carrying a real rule link before ship.

## Known limits

- Tests the auditor's *refutation* skill on single fakes, not saturation
  (one fake per set mirrors the realistic "rare FP" regime; a multi-fake
  variant is a possible follow-up).
- The 1.2 human sweep is the warrant that baseline findings are all-true; if
  a "real" finding falls to a *correct* refutation here, that is a baseline
  correction, not a test failure — dispositioned explicitly, never silently.
- Fakes are orchestrator-authored and may share authorship tells; rotating
  the four classes and grounding every fake in real files mitigates but
  cannot eliminate this.
