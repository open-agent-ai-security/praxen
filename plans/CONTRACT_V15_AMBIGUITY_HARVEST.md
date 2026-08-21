<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Contract v1.5 ambiguity harvest — 12-target baseline sweep (2026-08-21)

Source: the twelve contract-v1.4 extractions that produced the baseline
threat models (run stamp `2026-08-21-143615`, one fresh-context Opus 5
extraction per target, shipped `THREAT_MODEL.md` brief verbatim). Every
item below was reported by the extraction run itself in its final
message and/or recorded in its graph's `notes.omissions`; nothing here
blocked a run — all twelve graphs were first-pass valid. Grouped by how
many targets hit the same seam independently. Candidate batch for a
v1.5 contract amendment in 2.1.

## Recurring (the v1.5 core)

### 1. Same-file split (rule 3) vs. merge clause vs. the 12–25 node budget — 5 targets

The contract's three granularity pressures pull against each other and
different runs resolve the tension differently:

- **openai-customer-service** — prompt-shaped controls each live inside
  the same `Agent(...)` scope as the agent node; rule 3's collision
  clause says merge, the prompt-shaped-targets section says model them
  as `control` nodes. Run applied the merge.
- **finbot** — `FinBotConfig` hosts a `memory` (goals row re-entering
  prompts) and a `control` (unread `confidence_threshold`) in one
  defining scope: merge clause says one node, but kinds and trust
  consequences differ and merging erases a phantom control. Run split,
  reading the gate as a cross-file control.
- **openhands** — rule 3 wants the CORS gate and rate limiter split
  (different findings, different consequences); the node budget pushed
  the other way. Run merged into one `middleware-py-control`.
- **deepagents-cli** — mandatory control nodes (present *and* stub)
  plus five populated lanes forced the graph to 26; staying ≤25 meant
  dropping a real component carrying a confirmed finding (PyPI
  auto-update egress), carried as a threat + omission note instead.
- **hermes-agent-desktop** — a four-file adapter family with one
  trust-divergent member: rule 3's split-prefix guidance is written for
  one file and doesn't say how a cross-file family splits.

**v1.5 fix shape:** a precedence clause (trust-consequence divergence
beats the merge clause; the budget yields last and requires an
`notes.omissions` entry when it forces a drop), plus a cross-file
family split rule.

### 2. Single `owasp` field vs. KB primary + co-tag — 5 targets

The threat schema holds one code; findings carry primary + co-tags and
the KB assigns co-tags of its own.

- **openai-customer-service** — took KB-arbitrated primary per threat
  statement; a finding's co-tag became the primary of a separate
  disclosure threat.
- **hermes-agent-desktop** — co-tags unrepresentable (ASI05 riding the
  LLM03 smart-approval threat); primaries only.
- **craftbot** — one finding backing threats at two boundaries got
  different primaries per boundary under the KB's evidence-class rule.
- **openhands** — ASI03's artifact list literally names the surface but
  the mechanism is disclosure; "an ASI code when an agentic primary
  honestly applies" left it borderline (tagged LLM02 by mechanism).
- **yaah** — schema 3.0 stores `owasp_llm`/`owasp_agentic` as separate
  scalars with no explicit primary; run read the `tags` array order as
  the stored primary, which varies by finding.

**v1.5 fix shape:** either an optional `owasp_co` field or a codified
rule: threat-level primary is chosen by the KB for the mechanism the
threat names, co-tags dropped, and the stored primary is defined as
`tags[0]` — pick one and say it.

### 3. Untrusted-origin naming and lane — 6 targets (incl. one direct contradiction)

Where untrusted *content* enters, rule 6 assumes the origin has a name
the code uses and the lane table claims it twice:

- **aider vs. craftbot — direct contradiction.** A fetched web page is
  "any untrusted input origin" (`user_inputs`) and an external service
  (`external_deploy`). aider filed it `external_deploy`; craftbot filed
  it `user_inputs` "so attack paths start in the lane the contract
  designates for origins". Same surface, opposite calls, both defensible
  under the current text.
- **hermes-agent-desktop** — code names fetched content only as "an
  external source"; run coined `web-content-entrypoint` and flagged that
  a second run could coin differently.
- **uagents** — the origin is any remote/cross-origin HTTP caller,
  named only `scope["client"]`; rule 6 has no coinage path for an
  unnamed actor; run coined `remote-caller-entrypoint`.
- **deepagents-cli** — "whatever repository the agent was pointed at":
  rules 5 and 6 both partly apply, neither names the family; run keyed
  `makefile-datastore` off the one fixed literal path, an id narrower
  than its evidence.
- **yaah** — the host coding agent is model-generated input whose
  injection source is out of tree; run treated it as an external
  untrusted caller (the "internal mechanism" prohibition reads as
  written for in-tree agents).

**v1.5 fix shape:** one lane rule for untrusted content origins (the
probe-era boundary-agreement risk lives here — this is the
coinage-divergence class the stored-state archetype fixed for
boundaries), plus a rule-6 coinage recipe for unnamed actors/content
(suggested: `<content-kind>-entrypoint`).

### 4. Egress-side gaps in the archetype menu — 4 targets

- **helperbot, salesforce-help-agent-accelerator** — disclosure exits
  on the channel it entered; no outbound/response-egress archetype.
  Both filed the threats on `untrusted-ingress` with the reply edge
  listed as a crossing.
- **craftbot** — a listener the agent itself starts, network-exposed
  (0.0.0.0 binds, published container port): no archetype fits;
  `control-plane-exposure` would mislabel it; run used
  `untrusted-ingress-2` with empty `crossing_edges` since no caller
  node exists.
- **autogen-code-executor** — executed code reaching network/host from
  inside the container fits none of the twelve; coined
  `container-sandbox--external-network` via the escape hatch.

**v1.5 fix shape:** decide whether response-egress and
exposed-listener/sandbox-egress earn archetype rows (the stored-state
precedent: a menu row ended the coinage divergence) or whether the
"file on the ingress boundary, list the reply crossing" pattern gets
written down as the rule.

## Hit twice

### 5. ID rule 1 — leading-underscore basenames (autogen-code-executor, craftbot)

`_docker_code_executor.py` / `_routing.py` → "underscores→dashes"
yields a leading-dash id. Both runs dropped the leading separator by
analogy with the leading-dot clause. Codify that analogy.

### 6. Walk rule — node revisits (helperbot, yaah)

Origin→consequence chains that land back where they began (request in,
disclosure/execution out) must revisit the adapter/caller node — the
only real edges. Both runs revisited; the contract permits it
implicitly but doesn't say revisits are intended. Say so.

### 7. Prefix composition and stuttering ids (finbot, salesforce)

- **finbot** — a node subject to both rule 3 (scope prefix) and rule 4
  (directory prefix) has no stated composition order.
- **salesforce** — rule 4 applied where the parent directory equals the
  basename stem stutters:
  `haainlineenhancedchat-haainlineenhancedchat-js-client`; and rule 5
  vs. rule 1 for `{orgId}_CWC_WEB_STORAGE` (fixed suffix, dynamic
  prefix) produced a triple-prefixed memory id.

Fix: composition order + a de-duplication clause for repeated tokens.

### 8. STRIDE has no honest letter for some threat classes (deepagents-cli, uagents)

Observability gaps / stale-threat-model posture (deepagents used `R` as
"closest fit rather than a good one") and message replay (uagents:
between S and T; tagged T for envelope replay, S for the prefix
bypass). Either give the mapping or allow a null.

### 9. Scope boundary vs. graph completeness (helperbot, openhands)

Both targets' scan instructions exclude the surface where an attack
path completes (shared dashboard server; agent-server/SDK). Both runs
included a node built from in-scope evidence rather than truncating —
consistent with "an internal read is not yet a path" — and recorded the
scope treatment. Write the rule down: consequence nodes may be modeled
from in-scope evidence when scope excludes their code.

## Singles (bank, don't necessarily fix)

- **openai-customer-service** — `state-commit` where the write is
  non-durable (in-process context dying with the loop): fits neither
  `state-commit`'s durable-write reading nor `stored-state`; filed as
  `state-commit` with non-durability stated. / Evidence citation for a
  negative posture finding ("no credential material") has no natural
  file:line; cited the enforcing artifact (`.gitignore` exclusion).
- **autogen-code-executor** — shared runtime artifact (work dir written
  by five backends) has a dynamic path and no owning file; keyed on the
  `work_dir` construct while the sharpest evidence lives elsewhere. /
  Documented-but-absent sanitizer is a docstring claim with no named
  construct for rule 3 to name; fell back to class scope.
- **aider** — arbitration precedence when a threat cites a *subset* of
  a chain-shaped finding's evidence (is that "the same evidence"?). /
  Whether two distinct origins reaching the same consequence class earn
  two attack paths (run emitted both).
- **yaah** — attack-path walk semantics for a tool with no LLM of its
  own (host agent as origin and consequence).

## Disposition

Not a 2.0 blocker — all twelve ships were first-pass valid under v1.4.
Items 1–4 are the v1.5 batch proper (each hit ≥4 targets and item 3
contains a live two-run contradiction, the class the stability gate
measures as boundary/component agreement). Items 5–9 are cheap
clarifier lines that ride along. Singles stay banked here until a
second run hits the same seam.
