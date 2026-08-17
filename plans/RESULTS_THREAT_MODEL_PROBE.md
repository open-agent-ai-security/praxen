<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Results — Threat-Model Phase-0 Probe

> **STATUS: PROBE CLOSED — PHASE 1 GO (Steve, 2026-08-17).** Four spec
> rounds plus a full design-review cycle on the renderer (brand
> alignment, print-first statics, icons + 6-family colors, status set
> confirmed/potential/partial/mitigated with blue off-ladder potential,
> interaction discipline). Steve approved the v4 socxen render as the
> 2.0 visual reference: "Good enough to move us to the next phase."
> Spec v0.4.3 is the freeze candidate; everything from here is the
> Phase-1 port per `RELEASE_2.0_PLAN.md`.
> Design under test: `DESIGN_THREAT_MODEL.md`. Artifacts (graph JSONs,
> comparison outputs, spec, prompt, probe scripts) are checked in at
> `plans/threat-model-probe/`; rendered HTML is generated output —
> rebuild with `render_probe.py` (see its README). Verdict:
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
governing remit rules. *(The probe first rendered that as "candidate for
#198" — wrong framing, corrected per Steve 2026-08-16: a remit is a job
description, not a security model, so an untouched boundary is normal and
its threats stand on the RAISE/OWASP calibration alone. The renderer now
says so neutrally; see the design doc's corrected §5.)*

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
output with zero layout intervention, remit attachment works, and the
instability that exists is (a) id coinage — mitigated by the
same diff-by-content rule we already use for remits, (b) granularity —
mitigated by a spec convention, (c) ASI forcing — a spec bug, not a model
limitation. Semantic convergence on boundaries (the security-meaningful
layer) was 6/7 and ~5/5; attack paths 2/3 and 3/3.

Before Phase 1: re-run one pair on the scan model (Opus 5) with spec v0.2
to confirm the readout transfers; then freeze the graph spec.

---

# Round 2 — spec v0.2, Opus 5, + socxen (2026-08-16)

Steve asked for a spec update, a re-run, and a **real, well-understood
target**: socxen (SOC investigator — skill + Exabeam MCP connector, i.e. a
prompt-shaped agent, the shape most Praxen targets will have). Inputs:
`socxen-rev2/socxen-src` @ e913025 with its coherent same-day (2026-07-03)
schema-2.0 findings JSON and 15-rule remit. Spec v0.2 changes: nullable
`owasp` (ASI | LLM | null), mechanical ID formula, 11-entry boundary
archetype menu, granularity convention, edgeless nodes blessed, input
tolerance (old schema / drifted lines), prompt-shaped-target section.
All six runs pinned `model: opus` — **all six self-reported Opus 5**.

## Stability, v1 → v2 (same-target pairs)

| target | node id-Jaccard | boundary id-Jaccard | edge id-Jaccard |
|---|---|---|---|
| finbot | 0.00 → **0.79** | 0.00 → **0.82** | 0.00 → 0.55 |
| uagents | 0.07 → **0.59** | 0.00 → **0.73** | 0.02 → 0.28 |
| socxen | — → 0.54 (0.72 fuzzy) | — → **1.00** | — → 0.22 |

The mechanical formulas work: raw-id convergence went from ~zero to
strong, and **socxen's boundary set converged perfectly (8/8)** — the
archetype menu is the single most effective v0.2 change. The nullable
`owasp` also behaved: no forced tags, and matching codes now largely agree
across runs (finbot: ASI01 2=2, LLM02 4=4; ~10 threats/run honestly null).

Remaining variance is precisely located, and **every major class was
self-reported by the agents as a spec gap before comparison**:

1. **Same-file splits** (headline v0.3 fix, hit on all 3 targets): the ID
   collision rule only covers different files, so a file holding multiple
   trust-distinct roles (finbot's fallback engine + approve tool in the
   orchestrator module; socxen's 3–4 instruction-level controls in
   SKILL.md) either collapses or forces invented prefixes — runs resolved
   it differently. Fix: bless a `<function-or-section>-` prefix.
2. **`__init__.py` basenames** degrade ids (uagents, both runs predicted
   it, resolved it two ways). Fix: mandate parent-dir prefix for
   `__init__.*`/`index.*`; also state underscore→dash and the
   runtime-created-artifact naming rule (`private_keys.json`).
3. **Edgeless boundaries** (`secret-material`, `supply-chain` are repo
   posture with no runtime flow): one run emits `crossing_edges: []`,
   another attaches a nearby edge. Fix: bless `[]`.
4. **Edge topology on hub components** stays the loosest layer (0.22–0.55):
   granularity of framework internals (uagents context/protocol split vs
   one hub) and hub routing choices dominate. Conclusion unchanged —
   product comparisons and baselines should anchor on boundaries + threat
   content, treating edges as illustrative, not contractual.

## Socxen — the "real target" readout

The prompt-shaped section worked. Both runs modeled instruction-level
controls as `control` nodes with markdown evidence, put the executing
orchestrator question in the right place (the hosted model executes; the
skill is the policy surface), and produced SOC-native attack paths — both
runs' top path is the same one: **planted benign content in adversary
sighted logs manufactures the analyst's yes / a production suppression**
(r1 also surfaced unattended-run suppression and the defanging gap).
Boundary set: 8/8 identical archetypes. Remit attachment: 14–15 of 15
rules landed on boundaries; three boundaries (secret-material,
supply-chain, telemetry-egress) attached none — which is the *expected*
shape, not a gap: the remit is a job description, and those surfaces are
governed by the RAISE/OWASP calibration, not by declared intent (framing
corrected per Steve, 2026-08-16).
Both runs correctly resolved the **2025→2026 OWASP renumbering** skew
between the old findings JSON and current KBs, tagging per current KB and
logging the divergence.

## Emergent capabilities observed (unprompted)

- **Residual-threat surfacing works**: uagents r1 modeled the in-scope
  experimental `chat_agent` LLM tool loop (inbound chat →
  `tool_choice="required"` → any handler, ToolContext inheriting ledger +
  storage) which carries **zero baseline findings** — flagged as the most
  notable unscanned surface. §2.3 of the design doc, demonstrated.
- **Baseline auditing for free — with a false-positive lesson.** Verified
  by hand before acting (per standing practice), agent claims about our
  baselines went 2-for-3:
  - CONFIRMED, filed as **praxen#253**: uagents -002 overstates the Helm
    Secret wiring — `secrets.yaml` renders `UAGENT_SEED` but
    `deployment.yaml` has no env/envFrom/secret volume, so nothing
    delivers it to the pod (the committed seed default itself stays
    Critical).
  - CONFIRMED, filed as **praxen#254**: uagents -013 carries ASI08 against
    the KB's own arbitration (pure alerting gap → RAISE-only; missing halt
    is an explicitly non-tag-earning predisposing artifact). Both v2 runs
    independently applied the KB correctly and diverged from the baseline.
  - REFUTED: finbot "~35-line evidence drift" — the baseline cites
    behavior lines (807–820 IS the threshold-expedite logic, 841–850 IS
    the `contains_injection` approve branch); the extraction agent misread
    body-line citations as function-def citations. Baseline accurate.
  Net: extraction doubles as a light audit of finding wiring-claims and
  tags, but its audit claims need the same adversarial verification as
  anything else.

---

# Round 3 — full regeneration under corrected assumptions + review (2026-08-16)

Steve: *"Regen all with these new assumptions. Then review."* Spec v0.3 =
the remit-is-a-job-description semantics made binding (attach only genuine
governance; empty `remit_rules` is normal and must not be remarked on) +
the round-2 mechanical fixes (six-rule ID formula with same-file split
prefixes, `__init__` dir-prefix, runtime-artifact naming, edgeless
boundaries, framework-internals collapse, `spec_version` literal). Six
fresh Opus-5 runs (two were sleep-killed mid-run and rerun under
`caffeinate`; the originals in fact survived and their duplicates were
stopped — all six final graphs validated).

## Review

**1. Mechanical — PASS.** 6/6 graphs: `0.3-probe` stamp, Opus 5 identity,
0 renderer warnings (all refs resolve, every node cited). finbot and
uagents place all 14 baseline findings in both runs; none invented.

**2. Stability (v1 → v2 → v3, node/boundary raw id-Jaccard):**

| target | nodes | boundaries |
|---|---|---|
| finbot | 0.00 → 0.79 → 0.58 | 0.00 → 0.82 → **0.90** |
| uagents | 0.07 → 0.59 → **0.72** (0.85 fuzzy) | 0.00 → 0.73 → **1.00** (11/11) |
| socxen | — → 0.54 → 0.44 | — → 1.00 → **1.00** (8/8) |

The **boundary layer — the intended contract — has converged (0.90–1.00)**
and threat status mixes track closely. Node ids plateau: each mechanical
fix closed one wobble and opened a smaller one (family-node prefixes,
rule-5-vs-rule-1 datastore naming, unnamed-block prefixes — each
self-reported by the runs). Verdict: stop chasing raw-id 1.0; the product
contract is boundaries + threat content, node matching is content-based,
edges are rendering detail. This mirrors how we already treat remit rules.

**3. Semantics — PASS, with the best evidence being socxen.** All six runs
attach only genuinely governing rules, leave posture boundaries empty
without comment, and — the clincher — both socxen runs leave
`untrusted-ingress` remit-empty because **the remit genuinely has no
telemetry-as-data rule**: that control exists only in SKILL.md
(implementation), which the graphs correctly model as a control node.
v2 had stretched a thematic match there; v3 keeps declared-intent vs
implementation clean. Pair-consistent empty sets everywhere (finbot:
secret-material/supply-chain ×2; uagents: data-at-rest/supply-chain ×2).

**4. Substance — PASS.** Ground-truth chains present in both runs per
target (finbot: goal-override, fallback-manipulation, PII-harvest; uagents:
default-on inspector, replay→wallet; socxen: planted-benign-explanation →
suppression, export-injection). Third paths diverge per run — path
*selection* under a 2–3 cap varies even when underlying threats agree;
product answer: derive paths from the full threat set, cap at render time.

**5. Byproducts — verified 4, refuted 1, filed 3 more issues** (all
hand-verified before filing, continuing the 2-for-3 lesson):
- **praxen#255** — finbot console approve/reject buttons POST to routes
  that don't exist (`admin-dashboard.html:519,537` vs `admin.py:26`); the
  human-review UI 404s while the unauthenticated API works. Detection
  pattern candidate: client-side call sites vs declared routes.
- **praxen#256** — unauthenticated `/api/users` CRUD (`user.py:6-34`)
  uncovered by any baseline finding (-001 is admin-scoped).
- **praxen#257** — uagents -007 tags ASI02 on a missing approval gate;
  KB arbitration: LLM03 primary, "never ASI02 for the gate itself".
  Flagged independently by runs in both rounds.

## Run-to-run evaluation framework (the yardstick, settled with Steve 2026-08-16)

Consistency is layered — concentric rings, tightest to loosest:

1. **Verdict layer — effectively deterministic.** Boundary sets identical
   by archetype across all v3 pairs (8/8, 11/11, 9/10); every ground-truth
   critical chain in both runs; all baseline findings placed in both runs.
   Two readers of r1 and r2 write the same executive summary.
2. **Component inventory — same architecture, different box count.**
   0.70–0.85 fuzzy agreement; deltas are granularity calls at the margins,
   never a different system.
3. **Per-threat detail — visible wobble, near-zero contradiction.** Three
   wobble species, each with a known scan-variance analog: *enumeration
   depth* (4 vs 2 disclosure variants of one risk), *credit wobble*
   (mitigated vs residual = did the run go look for the control — the
   maturity-evidence wobble Step 8b fixed for scores), *adjacent-tag
   wobble* (LLM02 vs LLM04 — the severity-assignment analog). No run
   asserts a control the other denies; no inversions observed in any pair.

Same shape as the x-high scan validation (discovery stable, assignment
wobbles) → the same medicine applies if a canonical graph is ever needed:
union two runs, adjudicate credit/tag splits against evidence.

**Product-gate metrics, in order:** (1) boundary-set agreement (now
0.9–1.0 — gate-worthy), (2) threat-status agreement on matched threats
(~80% — the improvable one; credit wobble is the fix target), (3)
component fuzzy agreement (0.7–0.85 — acceptable). Explicitly NOT
yardsticks: raw node-id and edge-topology match. Reader-level summary:
either run correctly informs; both runs inform slightly better; neither
misleads.

## Round-3 verdict

The regeneration validates the corrected assumptions end-to-end: the
threat models are stable where the contract needs them stable, honest
about the remit's role, grounded in citations, and productive as a
baseline cross-check (five issues filed from three targets: #253–#257).
Spec learnings for a product freeze: bind arbitration explicitly (KB wins
over stored finding tags — already implicit, make it a line), rule-3
prefix for unnamed blocks ("or the named construct the block turns on"),
heading-shaped remit rules ruling, and the family-prefix tiebreak. Phase 1
remains a go on the design doc's shape.

## Round-2 verdict

Concept confirmed on the target shape that matters (prompt-shaped, real),
on the scan model, with converging ids and perfectly converging boundary
archetypes. Cost held at ~0.5× a scan (123–160k tokens/run). Phase-1
posture: fold the four v0.3 spec fixes in, then freeze the graph spec;
treat **boundaries + threats as the stable contract** and edges as
rendering detail. Next optional hardening before Phase 1: an x-high-style
adjudicated pair (union two runs, adjudicate splits) if we want a single
canonical graph per target rather than picking one run.

---

# Round 4 — spec v0.4 confirmation pair (2026-08-17): SPEC-FREEZE GATE PASS

Socxen ×2, Opus 5, spec v0.4 (control-lane rule, named-construct/family
prefixes, heading-shaped remit ruling, KB-over-stored-tags precedence,
mitigation-check sweep). Both runs `0.4-probe`-stamped, 0 validator
warnings, every `mitigated` threat citation-backed in both — the sweep is
enforced, not advisory.

**Against the three gate criteria (`RELEASE_2.0_PLAN.md`):**

1. **Boundary agreement ≥ 0.9 — PASS**: 8/8 identical archetypes, third
   consecutive perfect round on this target. The contract layer is stable.
2. **Same-file ID convergence — improved, plateau confirmed**: nodes 0.52
   raw / 0.73 fuzzy (v3: 0.44/0.70). The v0.4 prefix rules converge where
   they bind; both runs independently surfaced the same *new* margin
   cases (below). Confirms the standing conclusion: diff by content.
3. **Status agreement — measurably tightened**: mitigated-share gap
   between runs closed from 11 pts (v3: 36% vs 25%) to 3 pts (32% vs
   35%), with citation-backed credit now mandatory. On
   conservatively-matched threat pairs, status agreement is 100% (6/6;
   v3: 9/9) — the precise matched-pair ≥90% metric awaits the semantic
   comparator that is already 2.0 build scope (the probe's token matcher
   under-matches, as predicted in round 1).

**v0.4 rules observed working:** the dismiss/close gate decomposed across
its three enforcing surfaces exactly per the control-lane rule (harness
ask / in-prompt ask / write tools) — both runs, same decomposition; KB
precedence generated complete divergence logs against the 2025-numbered
stored tags (nearly the whole tag set on this older-schema input — a
known property of old inputs, not a defect).

**v1-contract polish items (documentation clarifications, no re-run
needed; both runs independently hit the same set):** leading-dot
basenames (drop the dot); two splits under one heading = one node;
directory-shaped families fold into the orchestrator's evidence;
one finding may back threats at multiple boundaries (bless explicitly);
edgeless-archetype list is guidance, fold-to-consequence otherwise.

**Verdict: freeze the spec as the 2.0 v1 contract** with the five polish
clarifications applied in the productized copy. Remaining measurement
(4-target pre-ship stability gate incl. one cold target) is 2.0 release
scope, not probe scope. Phase 0 closes here.
