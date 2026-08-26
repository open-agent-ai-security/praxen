<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxen Threat-Model Graph — contract v1.4

One JSON object per analyzed agent. This is the published contract for the
threat-model graph that the extraction pass writes and `render_threatmodel.py`
renders; the runtime validator enforces it. Frozen from probe spec v0.4.3
(2026-08-17) after four validation rounds; **v1.1 (2026-08-17)** folds in
the pre-ship gate's findings — the `stored-state` archetype, `partial`
calibration, and coinage rules; **v1.2 (2026-08-17)** makes attack paths
run untrusted-origin → consequence; **v1.3 (2026-08-17)** adds the
required plain-English `executive_summary`; **v1.4 (2026-08-17)** requires
every attack path to be a WALK over real edges (no skipped hijack step) —
see
`plans/RESULTS_THREAT_MODEL_PROBE.md` and
`tests/runs/v2.0.0-threatmodel-gate/GATE.md` for the evidence.

Everything is evidence-derived: **no node, edge, boundary, or threat without
a citation into the source tree, the findings JSON, or the remit.** If you
cannot cite it, leave it out and record the omission in `notes`.

## Top level

```json
{
  "spec_version": "1.4",
  "praxen_version": "<mirrors .claude-plugin/plugin.json>",
  "target": { "slug": "<slug>", "source_root": "<abs path analyzed>" },
  "analysis_ref": "<filename of the findings JSON this graph was built against, or null>",
  "remit_version": "<string, OPTIONAL — the remit's own declared version (Identity table \"Remit Version\"); omit when the remit declares none>",
  "model_identity": "<verbatim 'You are powered by ...' declaration>",
  "executive_summary": "<2-3 short paragraphs of plain English — see Executive summary>",
  "lanes": ["user_inputs", "client_adapters", "agent_core", "tools_mcp", "external_deploy"],
  "nodes": [],
  "edges": [],
  "trust_boundaries": [],
  "attack_paths": [],
  "notes": {}
}
```

`spec_version` is exactly `"1.4"`. Legacy probe statuses
(`finding`/`residual`/`open`) are not valid — emit only
the canonical status set below.

## Lanes (fixed, all five always present)

| lane | contents |
|---|---|
| `user_inputs` | human users, inbound messages/webhooks, uploaded files, any untrusted input origin |
| `client_adapters` | UI/web/CLI clients, platform adapters, channel connectors, API surfaces the user talks to |
| `agent_core` | orchestrator/loop code, system prompts/skills, the LLM call, memory/session state, in-process controls |
| `tools_mcp` | tools the agent invokes, MCP servers, code-execution surfaces, local data stores the tools touch |
| `external_deploy` | external services/APIs, upstream model providers, deployment surfaces (Docker/Helm/IaC), secrets stores, telemetry sinks |

A component goes in exactly one lane. If placement is genuinely ambiguous,
pick the best fit and record the ambiguity in `notes.lane_fit`.

**Control-lane rule:** a `control` node sits in the lane of the PROCESS THAT
ENFORCES IT, not the lane of the thing it conceptually protects. A guardrail
executing inside the MCP bridge process is `tools_mcp`; a browser-side gate
is `client_adapters`; instruction-level controls in a skill/prompt file are
`agent_core` (the prompt is the enforcing surface). This keeps control
chains local instead of double-crossing lanes.

## Nodes

```json
{
  "id": "<content-derived kebab id — see ID rules>",
  "name": "<short display name>",
  "lane": "<one of the five>",
  "kind": "entrypoint | client | adapter | orchestrator | model | prompt | memory | datastore | tool | mcp_server | control | external_service | deploy_surface | secret_store | log_sink",
  "description": "<one sentence>",
  "evidence": [ { "file": "<repo-relative path>", "line": 123, "note": "<why this file proves the node>" } ]
}
```

**ID rules (load-bearing; MECHANICAL — no creativity).** Two independent
runs on the same code MUST coin the same id:

1. **File-backed node:** `id = <basename of primary evidence file,
   lowercase, dots AND underscores→dashes, extension kept>-<kind>`.
   Examples: `agent-py-orchestrator`, `values-yaml-deploy-surface`,
   `finbot-agent-py-orchestrator` (from `finbot_agent.py`). The kind
   suffix also normalizes underscores to dashes (`mcp_server` →
   `-mcp-server`, `secret_store` → `-secret-store`). No role words,
   adjectives, or directory names. **Leading-dot basenames drop the dot:**
   `.mcp.json` → `mcp-json-deploy-surface`, `.exabeam-mcp.env` →
   `exabeam-mcp-env-secret-store`.
2. **`__init__.*` / `index.*` basenames ALWAYS take the parent-directory
   prefix** (no collision needed): `storage-init-py-memory` — normalize
   `__init__` to `init`.
3. **Same-file split** (the granularity rule carves two trust-distinct
   nodes out of one file): prefix the defining function / class / section
   heading — or, when the code has no named defining scope, **the named
   construct the block turns on** (the flag, constant, or registry it
   registers), kebab-cased: `fallback-processing-finbot-agent-py-orchestrator`,
   `redaction-skill-md-control`. CamelCase scopes kebab on case boundaries
   (`FinBotConfig` → `fin-bot-config-`). A control implemented across two
   functions takes its prefix from the construct or configuration it keys
   on, never from whichever function happens to lead the evidence list.
   The base file id names the file's dominant role — a family that IS the
   file's dominant role keeps the base id, and only the splits take
   prefixes. **If two would-be splits share the same
   defining scope** (two controls under one heading, one function), that
   collision is the contract telling you they are ONE node — merge them
   with multi-line evidence.
4. **Cross-file collision** (two nodes with the same basename in
   different files, ANY kind — v1.1 widened; four `manager.py` nodes with
   different kinds are still indistinguishable to a reader): prefix the
   parent directory: `admin-admin-py-...` vs `vendor-admin-py-...`.
5. **Runtime-created artifact:** when code writes/reads a FIXED literal
   path (`private_keys.json`), the node is named for that artifact:
   `private-keys-json-secret-store`. When the path is dynamic
   (`{name}_data.json`), the node stays code-file-backed per rule 1.
6. **No-file node** (external service, human actor, peer): `id = <proper
   name of the thing, lowercase kebab>-<kind>` using the name the code
   itself uses (`openai-external-service`, `peer-agent-entrypoint`). An
   actor the code never names takes the remit's name for it — and may cite
   the remit file itself as its `evidence.file` (the one sanctioned
   non-workspace citation). An in-process signing identity is a
   `secret_store` node distinct from any at-rest key file. Never invent
   synonyms.

**Edgeless nodes are legitimate** and expected for: committed secrets,
stub/planned-but-unwired controls, deploy surfaces, and repo-posture
evidence. Do not invent a data flow to justify a node; note edgeless nodes
in `notes` with one clause each.

**Granularity convention:** one node per *remit-relevant capability*, not
per file and not per function. Same file, same kind, same trust
consequence → ONE node (multi-file/multi-function evidence list). Split a
single file into multiple nodes only when the roles differ in trust
consequence. A family of parallel same-role items (many tools, many
adapters) is ONE node named for the family unless a specific member carries
a distinct trust consequence — then that member alone splits out. A family
node carved from a file that also hosts a split takes the prefix of **the
function or table that enumerates the family** (the tool-definitions
function, the allow-list constant) — never an invented collective noun.
**A family spread across a directory with no enumerating construct** (a
folder of parallel markdown, a corpus) is not a node — it folds into the
owning component's evidence list. **Framework runtime internals**
(context/protocol/dispatch/session plumbing) collapse into the orchestrator
node unless a piece carries a distinct trust consequence of its own (a
wallet, a signer, a store) — plumbing is evidence on the orchestrator, not
a node.

Include control nodes (validators, gates, redactors) — present ones AND
empty/stub ones (mark stub status in `description`).

## Edges

```json
{
  "id": "<from-id>--<to-id>",
  "from": "<node id>", "to": "<node id>",
  "label": "<what flows, 2-6 words>",
  "data": "<the data class: user text, credentials, tool output, file contents, ...>",
  "evidence": [ { "file": "...", "line": 123, "note": "..." } ]
}
```

Direction = direction of data flow. If bidirectional, emit two edges only
when both directions carry materially different data; otherwise one edge,
dominant direction.

## Trust boundaries

```json
{
  "id": "<archetype id — see boundary ID rule>",
  "name": "<short name>",
  "crossing_edges": [ "<edge id>", ... ],
  "remit_rules": [
    { "rule_id": "R-07", "excerpt": "<short verbatim excerpt>", "coverage_status": "verified | partial | gap | vague | enp" }
  ],
  "threats": [
    {
      "stride": "S | T | R | I | D | E",
      "owasp": "ASI01".."ASI10" | "LLM01".."LLM10" | null,
      "summary": "<one sentence, specific to THIS target>",
      "status": "confirmed | potential | partial | mitigated",
      "finding_id": "<finding id from the findings JSON, when status=confirmed>",
      "mitigation_evidence": { "file": "...", "line": 123 },
      "remainder": "<REQUIRED when status=partial: what the control does not cover>"
    }
  ]
}
```

**Boundary ID rule (MECHANICAL).** Pick from this archetype menu when one
fits — the id IS the archetype string, and most boundaries fit one:

| archetype id | meaning |
|---|---|
| `untrusted-ingress` | untrusted input origin → first handler (users, peers, webhooks, inbound messages) |
| `control-plane-exposure` | admin/inspector/config surface reachable by a caller |
| `model-egress` | agent → LLM/model provider |
| `tool-invocation` | model/orchestrator decision → tool with side effects |
| `state-commit` | decision → durable state change (approval, DB write, case action) |
| `data-at-rest` | stored data readable by a lower-trust caller |
| `secret-material` | keys/seeds/credentials at rest or injected at deploy |
| `telemetry-egress` | agent → logs, analytics, external reporting |
| `supply-chain` | dependencies, install path, plugin/skill provenance |
| `value-transfer` | funds/irreversible external action crossing |
| `peer-a2a` | agent ↔ agent communication |
| `stored-state` | writable persistent state (goals, config, memory) whose contents later re-enter the agent's decisions or prompts |

**State disambiguation (the gate's most-coined surface):** `state-commit`
is the *write* of a decision into durable state; `data-at-rest` is stored
data *read by a lower-trust caller*; `stored-state` is persisted content
*re-entering the agent's own reasoning later* (the replay/poisoning
surface). A stored-goals mechanism typically yields `stored-state` for the
replay, with the ungated write filed under `control-plane-exposure` or
`state-commit` as evidence dictates.

**A2A direction convention:** inbound peer traffic lands on
`untrusted-ingress`; outbound sends, resolution, and sync responses land on
`peer-a2a`.

Only if no archetype fits, coin `<from-concept>--<to-concept>` and say so
in `notes`. Two boundaries of the same archetype: suffix `-2` and
distinguish in `name`.

- **Edgeless boundaries are legitimate** for any posture-shaped boundary —
  repo/deploy posture typically lands on `secret-material`, `supply-chain`,
  or `telemetry-egress`: emit `crossing_edges: []` and never attach an
  unrelated nearby edge to satisfy the field. A threat with no crossing
  that fits no posture archetype folds into the boundary where its
  consequence lands.
- `remit_rules` — **a remit is a JOB DESCRIPTION, not a security model.**
  It declares what the agent is supposed to do; security expectations live
  in the RAISE/OWASP calibration and apply everywhere regardless.
  Therefore:
  - Attach a rule ONLY when its text genuinely governs conduct at this
    boundary. Do not stretch a thematic resemblance into governance.
  - **An empty `remit_rules` array is a normal, expected outcome** — most
    posture boundaries will have one. It is NOT a remit defect, NOT a
    coverage gap, and NOT a rule candidate; do not remark on it as a
    problem anywhere in the graph or notes.
  - For rules you do attach, copy the coverage status from the findings
    JSON `remit_coverage` block (match by rule TEXT, not by R-number).
  - **Heading-shaped rules:** when a rule's extracted text is a bare
    section heading, the governing artifact is the table/list under that
    heading — attach the rule iff that content governs the boundary, and
    quote a content line, not the heading, as the excerpt.
- **Arbitration precedence:** when the findings JSON's stored OWASP tag
  disagrees with the current KB arbitration on the same evidence, **the KB
  wins** — tag per the KB and record the divergence in `notes.omissions`.
  Stored tags are a snapshot; the KB is the authority.
- **Mitigation-check sweep — run BEFORE assigning any threat status.** For
  each enumerated threat, actively look for the control that would answer
  it (the lane table's control locations, plus config and deploy
  artifacts): `mitigated`/`partial` require a citation to the enforcing
  code/config; `potential` asserts you LOOKED and found none — record
  where you looked, when non-obvious, as a trailing clause of the threat's
  `summary` (e.g. "… (checked: agent.py:509 — no gate found)");
  `mitigation_evidence` stays null on `potential`, always. Never assign `potential` as a default
  for not having checked.
- `threats`: enumerate per crossing via STRIDE. `owasp` is the primary
  OWASP code under the KB's arbitration conventions: an ASI code when an
  agentic primary honestly applies, an LLM code when only the LLM Top 10
  applies, **null when neither does**. Never force a code — a wrong tag is
  worse than a null. `status` (severity order: confirmed > potential >
  partial > mitigated):
  - `confirmed` — an existing finding in the findings JSON proves it (cite
    the id). **One finding may back threats at multiple boundaries** when
    it genuinely describes multiple mechanisms.
  - `potential` — an unanswered hypothesis: the mitigation-check sweep
    found no control, and no finding covers it.
  - `partial` — a control demonstrably answers PART of the threat (cite
    the enforcing code in `mitigation_evidence`) and the unaddressed
    remainder is stated in the required `remainder` field (one clause). If
    a finding covers the remainder, the status is `confirmed` instead —
    findings win. The name deliberately matches the remit-coverage
    `partial` status.
  - `mitigated` — a control demonstrably handles the whole threat (cite
    code).
  - **Partial calibration (v1.1).** `partial` requires a control acting on
    the SAME mechanism as the threat — an adjacent control does not count.
    Tiebreaks at the borders: vs `mitigated` — if you cannot NAME a
    concrete uncovered input, path, or configuration in `remainder`, it is
    `mitigated`; vs `potential` — if no control touches the mechanism at
    all, it is `potential`; vs `confirmed` — a finding proving the
    remainder always wins. A control that exists but is trivially disabled
    by reachable configuration is `partial` with the bypass named as the
    remainder.
- Do not pad. A boundary with 2 real threats beats one with 8 generic ones.

## Executive summary

`executive_summary` is a required plain-English string (2–3 short
paragraphs, no markup) — the first thing a reader sees, before the diagram,
the way the analysis report leads with its behavior summary. Write it for a
hurried operator who may read nothing else, and write it LAST, once the
graph, boundaries, and attack paths are settled, so it reflects them.

- **Paragraph 1 — what this agent is and how it's shaped.** What it does,
  where its untrusted inputs come from, what it can reach and act on, and
  the one or two trust surfaces that matter most. Concrete, not generic
  ("A SOC investigation agent driven by a Claude Code skill over a bundled
  Exabeam MCP; its only untrusted input is tenant telemetry it treats as
  data, and its most consequential capability is case suppression.").
- **Paragraph 2 (and optionally 3) — the threats to deal with first**, in
  priority order, in the operator's language. Lead with the attack paths
  (origin → consequence) and the confirmed high-severity boundaries; say
  plainly what an attacker gets and what to fix. Do not list every threat —
  name the few that matter. If the picture is genuinely clean, say that and
  say what keeps it clean.

Ground every claim in the graph — the summary asserts nothing the nodes,
boundaries, and paths don't already support. No finding IDs or file paths
in the prose; those live in the tables.

## Attack paths

Attack paths are the report's headline. They exist to answer one operator
question — *"how do I actually get owned, and what do I fix first?"* — not
to catalogue connectivity. A path is a chain grounded in the findings JSON
(`escalation`, `related_findings`) or in an explicit multi-step mechanism
you can cite end-to-end:

```json
{
  "id": "<kebab>",
  "name": "<origin → consequence, in plain words>",
  "steps": [ { "node": "<node id>", "finding_id": "<or null>", "summary": "<one clause>" } ]
}
```

**A path MUST run from an untrusted ORIGIN to a CONSEQUENCE (v1.2 — the
load-bearing rule).** This is what separates an attack from the agent
simply doing its job.

- **The path must be a WALK over real edges (v1.4, validator-enforced).**
  Every consecutive pair of steps must be connected by an edge in `edges`
  (either direction — attacker *influence* can run opposite to the data
  edge). You may NOT jump from a gate or an input straight to the dangerous
  call: the node where injected content becomes an action — almost always
  the orchestrator/react loop — is a required step in between. If two
  logical steps aren't edge-connected, insert the node the influence passes
  through, or add the carrying edge with its evidence. A skipped hop leaves
  the rendered path visibly broken and is a validation error.
- **Step 1 is the untrusted origin — where attacker-influenceable content
  or action ENTERS**, across an ingress/untrusted boundary: a
  `user_inputs` entrypoint that is *not* the trusted owner/operator (a
  third-party sender, an anonymous caller); external content the agent
  ingests (a fetched web page, a tool/MCP result, an integration message);
  a peer message. The step's `summary` must name *what makes it untrusted*
  (unauthenticated, attacker-authored, unlabeled provenance). **Do NOT
  start a path at an internal mechanism** — a tool, the orchestrator, the
  model — when that mechanism is merely acting under injected influence.
  The dangerous `run_shell` call is not the origin; the untrusted content
  that *directed* it is. Trace back to where control entered and start
  there.
- **The trusted owner/operator path is not an attack.** Owner →
  client → loop is normal use; it is an origin only if the owner's own
  channel is the injection vector (rare — say why).
- **The last step is the consequence — a durable, irreversible, or
  high-impact effect**: host command/code execution, credential or data
  egress off the trusted surface, a state-commit / value-transfer, or
  persistent memory/goal poisoning that outlives the session. A path that
  ends at an internal read with no onward damage is not yet a path.
- **The middle is the hijack** — how the untrusted influence reaches the
  model's decisions and is granted the consequence (the missing gate, the
  absent provenance check, the over-broad tool). Cite the finding at each
  step that proves that link.
- **Name the path origin→consequence in plain words** ("Stranger's chat
  message reaches the host shell", not "run_shell to Docker"). The name is
  what a hurried operator reads first.

Prefer a few complete origin→consequence chains over many fragments.
Every distinct untrusted origin that can reach a distinct consequence is
worth one path; do not enumerate internal hops as separate paths. **Zero
attack paths is a valid — and good — answer**: it means no untrusted
origin was shown to reach a consequence.

## Notes

```json
{
  "lane_fit": "<where the 5-lane model strained, or 'clean'>",
  "omissions": "<components you suspected but could not cite; arbitration divergences>",
  "counts": { "nodes": 0, "edges": 0, "boundaries": 0, "threats": 0 }
}
```

## Size discipline

Target 12–25 nodes. Collapse same-role file families into one node. The
diagram is an architecture view, not a file listing.

## Input tolerance

The findings JSON may be an older schema (2.0: scalar `policy_rule_text`)
or may predate the source snapshot slightly — text-match remit rules the
same way, and cite a `finding_id` only when the finding still matches the
code in front of you (otherwise note it in `notes.omissions`). If a target
arrives with NO findings JSON, set `analysis_ref: null`; threats can only
be `mitigated`, `partial`, or `potential`, and
`remit_rules.coverage_status` is judged directly from the code (say so in
`notes`).

## Prompt-shaped targets

Some targets' agent logic lives in skill/prompt markdown, not code (the
orchestrator is an LLM following a skill file; tools are MCP servers).
Prompt-file instructions ARE architecture: model the skill file as the
`prompt`/`orchestrator` surface, MCP tool surfaces as `mcp_server` nodes,
and treat instruction-level controls ("never do X", approval gates written
in prose) as `control` nodes with the markdown file:line as evidence —
noting in `description` that enforcement is instruction-level, not code.
A prose control that sits on a live data path (a canonicalization or
redaction instruction the flow passes through) may appear inline in that
path's edges; the edgeless allowance is for stubs, secrets, and posture
evidence, not for live controls.
