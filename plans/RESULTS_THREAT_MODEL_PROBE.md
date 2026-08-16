<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Results — Threat-Model Phase-0 Probe

> **STATUS: PROBE COMPLETE 2026-08-16 — quiet branch, local artifacts.**
> Design under test: `DESIGN_THREAT_MODEL.md`. Artifacts (graph JSONs,
> rendered diagrams, comparison outputs, spec, prompt) live in gitignored
> `local/threat-model-probe/` — open `index.html` there. Verdict:
> **PASS with spec revisions** — the concept works end-to-end; two spec
> defects and one measurement lesson found, all fixable.

## Setup

- 2 targets × 2 independent runs: **finbot** (simple, LLM-in-the-loop) and
  **uagents** (multi-agent framework, no LLM in the scanned subject —
  deliberately stresses the lane model).
- Inputs per run: pinned v1.3-freeze source clone + frozen `v1.3-opus5`
  findings JSON + pinned remit + `KB_AGENTIC_TOP10` arbitration. Identical
  prompts within a pair; graph shape per `GRAPH_SPEC.md` v0.1 (5 fixed
  lanes, content-derived ids, mandatory evidence citations, STRIDE×ASI per
  boundary, finding/mitigated/residual status).
- Renderer: throwaway `render_probe.py` — deterministic lane layout →
  inline SVG, self-contained HTML, plus threat/remit tables and validation
  diagnostics. Comparator: `compare_runs.py` (id-Jaccard + fuzzy
  name-match + ASI/status distributions).
- **Model caveat:** all four extraction agents self-reported **Fable 5**,
  not Opus 5 (general-purpose subagents did not inherit the session model).
  Pairs are internally consistent (same model both sides), so stability
  reads are valid; absolute quality should be re-checked on the scan model
  before product decisions.
- Cost: ~93–119k tokens per extraction (~mean 105k ≈ **0.4–0.5× of a
  standard scan**, without evidence-checkpoint reuse), ~10 min wall each,
  run concurrently.

## Results against the four probe questions

### 1. Does the graph match reality? — YES

All 4 graphs rendered with **zero validation warnings**: every edge/boundary
/path reference resolves, every node cites evidence, every `finding_id`
exists in the findings JSON. Spot checks against known ground truth hold:
finbot's three attack paths are the known critical chains (anonymous goal
override → decision hijack; injected description past the fallback;
unauthenticated vendor bank-detail harvest); uagents surfaced the known-seed
Helm deploy surface, ungated wallet, and inspector control plane.

Emergent bonus: **orphan control nodes carry signal.** uagents'
QuotaProtocol renders as a deliberately edgeless control — shipped but
wired to nothing, which is itself the finding, visible on the diagram for
free. Same for finbot's absent-control strain (the auth gap reads as a
missing control node in the client lane).

### 2. Does it hold stable across runs? — SEMANTICALLY YES, BY ID NO

| Measure | finbot | uagents |
|---|---|---|
| Node count | 19 vs 18 | 24 vs 22 |
| Raw node id-Jaccard | **0.00** | **0.07** |
| Component agreement (fuzzy) | 0.48† | 0.70 |
| Boundaries, semantic match | ~4–5 of 5 | **6 of 7** |
| Attack paths, semantic match | **3 of 3** | 2 of 3 |
| Threat status mix | close | close (14/2/1 vs 15/3/1) |

† understated — the greedy fuzzy matcher mispaired the orchestrator nodes
and misses same-component pairs with divergent names (e.g. r1's three
separate decision-tool nodes vs r2's single `invoice-decision-tools`);
eyeball agreement is ~0.7 both targets.

Three distinct phenomena, in decreasing severity:

1. **ID coinage does not converge** (`helm-values-deploy` vs
   `values-yaml-helm-deploy`; boundary ids 0.00 overlap on both targets
   while the *named concepts* match nearly 1:1). The spec's "content-derived
   id" rule as written is insufficient — **the R-NN lesson repeats exactly**.
   Consequence for product: diff threat models by CONTENT (semantic match),
   never by id, same rule we already live by for remit rules; and/or tighten
   coinage to "primary evidence path only, no role words".
2. **Granularity variance** — one run splits what the other merges (three
   tool nodes vs one; two input nodes vs a portal node). The real
   structural wobble, and it is modest; a spec granularity convention
   ("one node per remit-relevant capability") would shrink it.
3. **ASI-tag wobble** (finbot ASI06 5 vs 2, ASI01 1 vs 4) — largely
   *caused* by spec defect #1 below: where no honest ASI exists, forced
   fits scatter.

### 3. Do remit rules attach to boundaries cleanly? — YES

Coverage statuses copied by rule-text match without incident on both
targets. uagents' supply-chain boundary legitimately attached **zero**
governing remit rules — rendered as "candidate for #198", which is exactly
the remit-generator feed the design hoped for.

### 4. Does the 5-lane model survive? — YES, WITH KNOWN STRAINS

All four runs report "mostly clean" with honest, *converging* strain
reports:

- **No peer lane**: uagents' "other agents" split across `user_inputs`
  (inbound untrusted) and `external_deploy` (outbound resolved) — both runs
  hit it. A multi-agent variant needs a peer/A2A convention (design doc §6
  predicted this).
- **Dual-role components**: finbot's single SQLite store splits across
  lanes by role (goals-as-memory vs rows-as-datastore); `approve_invoice`
  is both tool and enforcement point. Verdict: acceptable — the split *by
  role* is arguably the more truthful security view.
- **No-LLM targets**: agent_core with no model/prompt node renders fine.

## Spec defects found (fix in v0.2)

1. **`asi` must be nullable** (allow LLM codes or `none`). All four runs
   independently hit it: RAISE-only (observability), LLM-only (LLM02/03/06),
   and browser-layer findings have no honest Agentic primary under the KB's
   own arbitration; forcing a code manufactures both wrong tags and
   run-to-run wobble.
2. **Bless evidence-only / edgeless nodes** (committed secrets, stub
   controls, deploy surfaces). Agents did the right thing and documented
   around the spec; the spec should say it.
3. **ID rule needs teeth or abandonment**: either canonical coinage
   ("primary evidence path, verbatim, role words banned") or declare ids
   run-local and require content-based diffing. Recommend both: tighten
   coinage AND diff by content.
4. Product comparator must be semantic (the probe's greedy fuzzy matcher
   mispairs); boundary/path matching by name+member similarity.

## Verdict

**Phase 0 PASSES.** The deliverable exists (4 rendered, evidence-cited,
self-contained diagrams), the deterministic lane renderer works on real
output with zero layout intervention, remit attachment and the #198 feed
work, and the instability that exists is (a) id coinage — mitigated by the
same diff-by-content rule we already use for remits, (b) granularity —
mitigated by a spec convention, (c) ASI forcing — a spec bug, not a model
limitation. Semantic convergence on boundaries (the security-meaningful
layer) was 6/7 and ~5/5; attack paths 2/3 and 3/3.

Before Phase 1: re-run one pair on the scan model (Opus 5) with spec v0.2
to confirm the readout transfers; then freeze the graph spec.
