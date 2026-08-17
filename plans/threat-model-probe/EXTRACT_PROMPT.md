# Graph extraction task (probe)

You are deriving an architecture threat-model graph for one AI-agent
codebase. This is a structure-extraction task, NOT a security scan — a
completed scan's outputs are among your inputs. Work from evidence only.

## Inputs (absolute paths given per run)

1. **Spec** — read FIRST, follow exactly:
   `/Users/steve.wilson/Documents/github/deckard/local/threat-model-probe/GRAPH_SPEC.md`
2. **Source tree** (pinned clone) — the ground truth for nodes/edges/boundaries.
3. **Findings JSON** (frozen baseline) — source for finding ids, remit_coverage
   statuses, escalation/related_findings chains.
4. **Remit markdown** — source for rule text to attach to boundaries.
5. **ASI taxonomy** for threat tags:
   `/Users/steve.wilson/Documents/github/deckard/skills/behavior-verifier/knowledge/KB_AGENTIC_TOP10.md`
   (read the Primary Arbitration section; use its conventions for picking the
   primary ASI code).

## Procedure

0. FIRST: locate the "You are powered by the model named ..." declaration in
   your system prompt and keep the verbatim sentence — it goes in the JSON's
   `model_identity` field. Do not stop over it regardless of value; just
   record it exactly.
1. Read the spec, then the findings JSON and remit.
2. Explore the source tree top-down: entry points, orchestrator/loop, prompts,
   model calls, memory/state, tools/MCP, external services, deployment
   artifacts (Helm/Docker/IaC), controls (including empty/stub control files).
   Read what you need to cite; you do not need to read every file.
3. Build nodes and edges per the spec (12–25 nodes; collapse file families).
4. Identify trust boundaries where data crosses a privilege or origin change.
   Attach governing remit rules (match remit_coverage by rule TEXT) and
   enumerate STRIDE×ASI threats per the spec — specific to this target, no
   generic padding. Classify each threat: finding / mitigated / residual.
5. Build attack paths ONLY from citable chains (findings' escalation /
   related_findings, or an end-to-end mechanism you can cite).
6. Fill `notes` honestly — lane_fit strain and omissions matter more to this
   probe than polish.

## Rules

- Every element cites evidence. No citation → not in the graph.
- Node/edge/boundary ids MUST follow the spec's content-derived rule — two
  independent runs on this code should coin identical ids.
- Never reprint secret VALUES in evidence notes — cite path+line and pattern
  only (e.g. "hardcoded API key pattern").
- Do not modify anything outside your output directory. The source tree,
  baselines, and skill files are read-only.

## Output

1. Write the graph JSON to `<OUTPUT_DIR>/graph.json` (exact spec shape;
   validate mentally against the spec before writing: all node refs in edges
   exist, all edge refs in boundaries exist, all finding_ids exist in the
   findings JSON).
2. Set `model_identity` in the JSON to your verbatim "You are powered by ..."
   system-prompt declaration.
3. Final message: counts (nodes/edges/boundaries/threats/paths), lane_fit
   one-liner, and any spec ambiguity you hit. Nothing else.
