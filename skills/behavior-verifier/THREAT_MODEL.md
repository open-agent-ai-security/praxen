<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxen Threat Model — extraction orchestration

**Read this file only when the operator's invocation asks for a threat
model** ("run a Praxen threat model", "threat model this agent", "generate a
threat model", "Praxen analysis with a threat model"). If no threat model was
asked for, stop reading now — nothing in this file applies to a standard
analysis, and no step of `SKILL.md` changes.

You — the agent reading this — are the **orchestrator**. The threat model is
an **evidence-derived architecture view**: a data-flow graph with trust
boundaries, STRIDE×OWASP threat enumeration, remit-rule overlay, and attack
paths, where every element cites file:line evidence. It is produced by a
single extraction pass against on-disk artifacts, validated against the
published contract, and rendered to a self-contained HTML report. It is
**score-inert**: it never changes findings, scores, remit coverage, or any
analysis artifact.

**Announce the cost before starting.** One sentence: in our testing a
threat-model extraction costs roughly **0.5–1× the tokens of a standard
scan, typically ~0.75×** (one fresh-context pass, ~10–20 minutes) plus a
local validate-and-render step.

---

## Entry conditions — resolve the inputs first

The extraction consumes four on-disk inputs: the **workspace** (resolved
exactly as `SKILL.md` Step 1 resolves it, including `SCAN_INSTRUCTIONS.md`
scope when present), the **Worker Remit**, the **findings JSON** from a
completed analysis, and the contract + calibration files beside this one.

1. **Post-analysis (the default).** A completed analysis exists — use the
   most recent `<slug>-findings-*.json` in `./reports/` unless the operator
   names one. Use the same remit that analysis used. If the operator asked
   for a thinking mode on the analysis, the threat model consumes the
   **final** findings JSON (the mode's output), never a raw intermediate.
2. **Combined invocation** ("run a Praxen analysis with a threat model"):
   run the full `SKILL.md` pipeline first — standard or the named thinking
   mode, unchanged — then re-enter this file with its outputs.
3. **No findings JSON, threat-model-only ask:** tell the operator the model
   is materially stronger with an analysis behind it (`confirmed` statuses
   exist only when findings exist) and offer to run one first. Proceed
   without only on their explicit say-so: set `analysis_ref: null`; statuses
   are then limited to `mitigated` / `partial` / `potential`.

Also resolve, before spawning anything:

- **`PRAXEN_VERSION`** — the `version` field of the plugin manifest at
  `../../.claude-plugin/plugin.json` relative to this file (the same single
  source `manifest_to_findings.py` stamps into findings). Hard-stop if
  missing — a graph without provenance is a bug.
- **`TIMESTAMP`** — `YYYY-MM-DD-HHMMSS`, this run's own stamp.
- **Output paths** — `./reports/<slug>-threatmodel-<TIMESTAMP>.json` and
  `./reports/<slug>-threatmodel-<TIMESTAMP>.html`.

## Context isolation

The extraction runs with **on-disk inputs only** — the stability evidence
behind this feature was measured under exactly those conditions, and a
same-session extraction inherits whatever the conversation already believes
about the target.

- **Claude Code:** spawn the extraction as a subagent (fresh context, no
  parent conversation history).
- **Codex:** spawn with `fork_turns="none"`.
- **No sub-agent facility:** run the extraction inline as a last resort,
  reading only the listed inputs, and record `"extraction ran without
  context isolation"` in the graph's `notes.omissions`.

## The extraction brief (give this to the agent verbatim, placeholders filled)

> Derive a threat-model graph for one AI-agent codebase. This is
> structure-extraction against evidence, not a security scan — a completed
> scan's outputs are among your inputs. Work only from the inputs listed
> here; cite everything.
>
> Inputs:
> 1. **Contract — read FIRST and follow exactly:** `{SKILL_DIR}/THREAT_MODEL_SPEC.md`
> 2. **Workspace (the subject):** `{WORKSPACE}` — apply the scope in
>    `{SCAN_INSTRUCTIONS_OR_NONE}`.
> 3. **Findings JSON:** `{FINDINGS_JSON_OR_NONE}`
> 4. **Worker Remit:** `{REMIT_PATH}`
> 5. **Tag arbitration:** `{SKILL_DIR}/knowledge/KB_AGENTIC_TOP10.md`
>    (Primary Arbitration section) and `{SKILL_DIR}/knowledge/KB_LLM_TOP10.md`.
>    Where a stored finding tag disagrees with the KB on the same evidence,
>    the KB wins — record the divergence in `notes.omissions`.
>
> Procedure: read the contract, then the findings JSON and remit; explore
> the workspace top-down (entry points, orchestrator/prompts, model calls,
> memory/state, tools/MCP, external services, deploy artifacts, controls —
> including empty or stub controls); build nodes and edges per the
> contract's mechanical ID rules and granularity convention (12–25 nodes;
> collapse families; plumbing folds into the orchestrator); identify trust
> boundaries from the archetype menu; attach remit rules **only where their
> text genuinely governs conduct at that boundary** — a remit is a job
> description, not a security model, and empty `remit_rules` is a normal
> outcome never to be remarked on; run the mitigation-check sweep BEFORE
> assigning any threat status; write the required `executive_summary` LAST (2-3 plain-English paragraphs: para 1 = what the agent is and its key trust surfaces; para 2-3 = the threats to deal with first, led by the attack paths, in the operator's language, no IDs or paths in the prose); build attack paths that are a WALK over real edges (every consecutive step pair must be a real edge; never skip the orchestrator/hijack node between a gate/input and the dangerous call — validator-enforced) running from an untrusted ORIGIN (where attacker-influenceable content enters — NOT an internal tool or the loop acting under injected influence) to a CONSEQUENCE (host exec, data egress, state-commit, persistent poisoning), citing the finding at each link — see the contract's Attack paths section; a few complete origin→consequence chains beat many fragments.
>
> Rules: every element cites evidence — no citation, no element. Never
> reprint secret values (path + pattern only). Do not modify anything
> outside your output file; every input is read-only.
>
> Output: write the graph to `{OUTPUT_JSON}` with `"spec_version": "1.4"`,
> `"praxen_version": "{PRAXEN_VERSION}"`, `"analysis_ref":
> {ANALYSIS_REF_OR_NULL}`, `"remit_version"` set to the remit Identity
> table's "Remit Version" value (omit the field if the remit declares
> none), and your verbatim "You are powered by ..."
> declaration as `model_identity`. Before writing, self-check: all edge
> node-refs resolve, all boundary edge-refs resolve, every cited
> `finding_id` exists in the findings JSON, `notes.counts` match the
> document. Your final message: counts, lane_fit one-liner, and any
> contract ambiguity you hit — nothing else.

## Validate and render (orchestrator, after the extraction returns)

Run the renderer — it validates the graph against the contract before
producing HTML, and fails loudly with the offending JSON path:

```bash
python3 {SKILL_DIR}/render_threatmodel.py \
  --graph ./reports/<slug>-threatmodel-<TIMESTAMP>.json \
  --template {SKILL_DIR}/report_template.html \
  --out-html ./reports/<slug>-threatmodel-<TIMESTAMP>.html \
  --analysis-html <analysis-report-filename-or-omit>
```

Pass `--analysis-html` with the bare filename of the analysis HTML the
findings JSON came from (it sits in the same `./reports/` dir) so the
masthead's "built against" reference links to it; omit the flag for a
standalone extraction or when the analysis HTML is absent.

- **On a validation error:** first copy the failing graph aside
  (`<file>.prerepair`) so the repair's diff is auditable, then relay the
  exact error verbatim to the extraction agent to repair its own JSON —
  never hand-edit graph content yourself. At most two repair rounds; if it still fails, stop and report
  the error to the operator with the artifact paths.
- **Cross-check cited findings** (the validator cannot see the findings
  JSON): every ID from `threatmodel_schema.cited_finding_ids(graph)` must
  exist in the findings JSON's `findings[].id`. A miss is a repair-round
  error, same handling as above.

## Final summary (stdout, after the render succeeds)

Report to the operator, in this order: the two artifact paths; component /
flow / boundary counts; the four status counts (confirmed / potential /
partial / mitigated); the worst-status boundary by name; the first attack
path by name (or "none grounded in findings"). One short paragraph, no
reprinted findings.

## What the threat model never does

No score movement, no finding edits, no remit edits or remit commentary
beyond the rule overlay, no schema change to the findings JSON, no
multi-run aggregation — one extraction produces one graph. The standard
`SKILL.md` pipeline is untouched: if this file was read but no threat model
was requested, something has gone wrong — stop.
