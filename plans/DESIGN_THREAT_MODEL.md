<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Design — Praxen Threat Modeling (visual, evidence-derived)

> **STATUS: EXPLORATORY DESIGN — not scheduled, not public.** Drafted
> 2026-08-16 on a quiet side branch while 1.3 is in release mechanics. No
> issue number yet; nothing here is committed scope for 1.4 (which remains
> the detection-coverage release). Earliest realistic slot: **1.5**, with a
> zero-code Phase 0 probe possible any time after the 1.3 tag.

## 1. Purpose

Extend Praxen beyond findings-shaped output (SAST-adjacent: "here is what is
wrong, at file:line") to an **architecture-level threat model**: a visual
data-flow diagram of the agent with trust boundaries, threat enumeration per
boundary, and the scan's existing evidence pinned onto the structure.

The opportunity is structural. Every incumbent threat-modeling tool
(Microsoft TMT, OWASP Threat Dragon, IriusRisk, pytm) shares one bottleneck:
**a human draws the DFD**, and it is stale the day after. The LLM entrants
(STRIDE-GPT and kin) generate models from a *prose description* of the
system — unverified by construction. Praxen's Step 4 already discovers,
reads, and cites the real artifacts — entry points, orchestrator prompts,
tools, MCP servers, memory files, data stores, IaC/deployment surfaces,
logs — and then throws the structure away, keeping only a prose
`agent_structure_summary`. The capability is largely **persisting a
structure the scan already derives, then reasoning over it**. This is the
same move #195 made for scoring: capture the evidence as an artifact first,
derive the output from the artifact.

**Positioning in one line: a threat model with receipts.** Every node,
boundary, and threat annotation carries file:line evidence, because the
model is derived from the workspace, not from a description of it.

## 2. What makes it more than a diagram

Three capabilities, in descending order of differentiation:

### 2.1 Remit-annotated trust boundaries (unique to Praxen)

Praxen holds a document no other threat modeler has: **declared intent**.
Overlay each trust boundary with the remit rules that govern it, colored by
their existing `remit_coverage` status — verified / partial / **gap** /
vague. A boundary whose declared controls are unverified is visually hot.
This is the intent-vs-implementation thesis made visual, and it is not
replicable without the remit concept.

### 2.2 Findings pinned to structure + attack paths

Schema 3.0 findings already carry `related_findings` and `escalation`;
KB_AGENTIC_TOP10 has an "Agentic Attack Chain Patterns" section; Step 7
(compound signal reasoning) already chains signals in prose. Render
escalation chains as **attack paths across the diagram** — e.g. *committed
Helm seed (ASI04) → wallet key access → unbounded tool loop (ASI05)*. The
strongest demo material in the whole idea, and it is a rendering of data the
scan already emits.

### 2.3 Residual-threat matrix (honest coverage)

For each boundary crossing, enumerate expected threats mechanically
(STRIDE × ASI), subtract what findings and positives addressed. What remains
splits into **examined-and-clean** vs **never-examined**. This turns the
scan's silent non-coverage into a visible artifact — the claims-ledger
"no silent caps" discipline applied to the scan itself.

## 3. Framework choice

Survey basis: Microsoft's agent reference data flows / threat models
(learn.microsoft.com/en-us/agents/architecture/threat-models) and the
2026 framework comparison at trent.ai (STRIDE, ATT&CK, ATLAS, MAESTRO,
SAILORS, PHANTOM-B, AGENTIC). The comparison's core finding — *no single
framework covers even two-thirds of the threat domains; layering is
mandatory* — maps cleanly onto Praxen:

| Layer | Framework | Why |
|---|---|---|
| Threat taxonomy (spine) | **OWASP Agentic Top 10 (ASI01–10)** + LLM Top 10 | Already our KB, already the tags on every finding. The threat model speaks the same vocabulary the findings do — zero new taxonomy, existing arbitration rules apply. |
| Per-boundary method | **STRIDE** | 25 years of reviewer muscle memory; mechanical and promptable as "STRIDE × ASI per crossing". |
| Multi-agent lens | **MAESTRO (optional)** | Its 7 layers structure the inventory for multi-agent targets (uagents, autogen). Specialist-grade per the comparison — an opt-in lens, never the default. |
| Detection mapping | ATT&CK / ATLAS | Later export, not v1. |

## 4. The visual: deterministic SVG, not mermaid

Key observation (Microsoft's reference data flow confirms it): **agent
architectures have a canonical macro shape.** Nearly every target we scan
fits fixed lanes:

```
[ User / Inputs ] │ [ Client / Adapters ] │ [ Agent core: prompts · model · memory ] │ [ Tools / MCP ] │ [ External / Deployment ]
```

So we do not need general graph layout. The division of labor mirrors the
rest of Praxen — **model does judgment, python does mechanics**:

- The scan emits a **structured graph JSON**: nodes (with lane assignment +
  evidence citations), edges (data flows), trust boundaries, and
  annotations (threats, remit rules, finding IDs).
- `render.py` (or a sibling `render_threatmodel.py`) computes a
  deterministic lane layout and emits **inline SVG** into a self-contained
  HTML page. Testable, byte-stable, no vendored JS, consistent with the
  report's no-external-assets philosophy.

Rejected default: embedding mermaid (~1.3 MB of JS per report,
nondeterministic layout, breaks byte-gate testing). Acceptable as a debug
side-format at most (the graph JSON trivially transcodes to mermaid source
for quick looks during development).

**Identity lesson carried in from R-NN:** node IDs must be
**content-derived** (path-based), never enumeration-order, or baseline
diffing of threat models breaks the same way diffing remit rules by R-ID
would.

## 5. Product shape

- **Score-inert, opt-in pass.** A third axis alongside thinking modes (or a
  `--threat-model` addendum). It must not touch the score:
  one-scan-one-score stays intact ([[feedback-multirun-measures-not-solves]]
  discipline), and the claims ledger stays clean.
- **Runs from a completed scan's artifacts** — evidence checkpoint +
  findings JSON + source tree. Consequences: composes with thinking modes,
  retro-fittable onto frozen baselines (v1.3-opus5 targets become the test
  corpus for free), and cheap to iterate on because discovery isn't re-run.
- **Artifacts:** `<slug>-threatmodel.json` + rendered page as a **sidecar**
  — no change to the canonical findings schema for v1. Folding a
  `threat_model` block into the canonical JSON rides #118 (the same
  deferred-schema-change bus as `scan_mode`).
- **Feeds #198 (remit generator, 1.4's opener):** boundaries with no
  governing remit rule are exactly what the generator should propose rules
  for. The threat model becomes the generator's skeleton — a clean 1.4→1.5
  arc if the probe pans out.

## 6. Risks

- **Graph wobble across runs.** Discovery recall is our strong suit
  (x-high validation: Critical recall 100%), and structure is more
  discoverable than severity — but measure before promising anything.
  Score-inertness contains the blast radius; the claims ledger gets no
  threat-model row until a stability test exists.
- **Cost.** As a reuse-the-checkpoint pass, expected well under high-mode's
  ~1.4×; as a fresh full pass, more. Measure in Phase 0/1.
- **The layout engine is the biggest code item.** Bounded by the lane
  constraint (no general graph layout), but real work: lane placement,
  orthogonal edge routing, boundary bands, annotation callouts, overflow
  behavior on big targets (openhands-scale).
- **Multi-agent targets stress the lane model.** uagents/autogen have
  agent↔agent flows that don't fit five lanes cleanly; MAESTRO lens or a
  repeated-core-lane convention. Defer past v1 if needed — but pick the
  node-ID scheme so it won't need breaking later.

## 7. Phasing

1. **Phase 0 — prompt-only probe (zero product code, ~a day).** Draft the
   graph-JSON spec. Hand a fresh agent 2–3 baseline targets (finbot +
   uagents + one boring one), generate graphs ×2 runs each. Questions:
   does the graph match reality? does it hold stable across runs? do remit
   rules attach to boundaries cleanly? does the lane model survive a
   multi-agent target?
2. **Phase 1 — sidecar ship.** Graph spec frozen; `THREAT_MODEL.md`
   instruction file (the THINKING_MODES.md pattern — SKILL.md gets one
   pointer, standard path untouched); lane-layout SVG renderer + tests;
   standalone HTML page; docs. No schema, score, or baseline impact.
3. **Phase 2 — integration.** Report section (rides #118), residual-threat
   matrix, attack-path rendering from `escalation` chains, MAESTRO lens,
   #198 hookup, ATT&CK/ATLAS export.

## 8. Non-goals (v1)

No score movement, no schema change, no template change to the existing
report, no mermaid/JS dependency, no live/runtime threat modeling (source
and deployment-state evidence only, same as scans), no auto-generated
mitigations beyond the existing `recommended_actions` conventions.

## References

- Microsoft, *Reference data flows and threat models for security
  evaluations* — learn.microsoft.com/en-us/agents/architecture/threat-models
- trent.ai, *AI Threat Modeling Frameworks Compared* (2026) — STRIDE /
  ATT&CK / ATLAS / MAESTRO / SAILORS / PHANTOM-B / AGENTIC comparison;
  "layering is mandatory, not optional."
- OWASP Top 10 for Agentic Applications 2026 (already distilled in
  `skills/behavior-verifier/knowledge/KB_AGENTIC_TOP10.md`).
