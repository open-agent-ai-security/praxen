<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Baseline — v2.0-opus55 (current)

The **Praxen 2.0 freeze, on Claude Opus 5.5.** Supersedes `v1.3-opus5` (now archival).
**The reference model is what changed** — Opus 5 (`claude-opus-5[1m]`) → Opus 5.5
(`claude-opus-5-5`). Everything else that can move a score was held fixed against v1.3:

- **Sources** — the v1.3 pins, reconstructed and committed in [`SOURCES.md`](SOURCES.md)
  (three documented, six recovered exactly, four recovered to a narrow ambiguous set).
- **Remits** — each target's `<slug>-remit.md` is byte-identical to the v1.3 pinned copy and
  to the `tests/remits/<slug>.md` the scans read.
- **Skill** — the three SKILL.md edits since the v1.3 freeze are score-inert: the opt-in
  threat-model pointer, the `remit_version` manifest line, and the `standards` stamp. The
  knowledge bases are unchanged.

So the two sets are **score-comparable**, and this document grades one against the other.

## Freeze method — median-of-3, every target standard mode

Each target was scanned **3× on identical inputs** (36 runs, `local/v2.0-opus55-r{1,2,3}/`),
each a fresh background subagent per the Full Suite Run protocol. Every run self-reported
`claude-opus-5-5` and passed an orchestrator check on disk: the four canonical outputs exist,
the findings JSON validates at schema 4.0 with the 2026 `standards` block, the slug is the
baseline slug, `praxen_version` is `2.0.0`, and no pinned workspace was modified. **36/36
passed; none was re-run or excluded.**

**All 12 targets are frozen at a standard-mode run.** v1.3 froze hermes, openhands and yaah at
high-mode audit runs; this set does not, so it is uniform. That asymmetry matters when reading
those three rows — see [the comparison caveats](#reading-the-v13-comparison).

**Frozen value = the median-weighted run** (one real, unedited run; never a synthesised
average). **Ties at the median** — common, since scores move in 0.05/0.15 steps — are broken
by Critical-theme consensus, not run number:

1. the run carrying the most Critical themes that **at least two of the three runs** carry at
   Critical (a theme = a Critical finding's evidence-file set; a run carries it when one of its
   own Critical findings cites at least half of those files);
2. then the run with the fewest **outlier** Criticals — Critical findings no other run carries
   at Critical;
3. then fewest findings, then run number.

The tiebreak exists because v1.3's "lowest-numbered run" rule is blind to content: on this set
it would have frozen a CraftBot run that dropped a Critical theme the other two runs agreed on.
Rule 2 was added when rule 1 alone tied yaah r2/r3 and let fewest-findings pick r2 — the one run
that raised the Notion-token finding to Critical while demoting the theme the other two agreed
was Critical. 10 of 12 medians were tied and went through the tiebreak.

**Bands = 3-run mean ± max(0.15, max−min spread).** The 0.15 floor is one band step of a
0.15-weight category; without it the four zero-spread targets would get zero-width bands that
the next ordinary wobble breaches.

| Target | Frozen run | Weighted RAISE | r1 / r2 / r3 | Spread | Band | v1.3 | Δ |
|---|---|---|---|---|---|---|---|
| helperbot | r1 | 0.70 | 0.70 / 0.55 / 0.85 | 0.30 | 0.40–1.00 | 0.45 | **+0.25** |
| finbot | r1 | 1.00 | 1.00 / 1.00 / 1.00 | 0.00 | 0.85–1.15 | 1.00 | 0.00 |
| craftbot | r1 | 1.15 | 1.15 / 1.00 / 1.15 | 0.15 | 0.95–1.25 | 1.30 | −0.15 |
| openai-customer-service | r3 | 1.30 | 1.30 / 1.15 / 1.30 | 0.15 | 1.10–1.40 | 1.45 | −0.15 |
| salesforce-help-agent-accelerator | r3 | 1.40 | 1.40 / 1.40 / 1.40 | 0.00 | 1.25–1.55 | 1.40 | 0.00 |
| autogen-code-executor | r3 | 1.40 | 1.40 / 1.55 / 1.40 | 0.15 | 1.30–1.60 | 1.40 | 0.00 |
| openhands | r3 | 1.45 | 1.45 / 1.30 / 1.45 | 0.15 | 1.25–1.55 | 1.60 † | −0.15 |
| aider | r2 | 1.55 | 1.85 / 1.55 / 1.40 | 0.45 | 1.15–2.05 | 1.55 | 0.00 |
| uagents | r2 | 1.55 | 1.40 / 1.55 / 1.55 | 0.15 | 1.35–1.65 | 1.55 | 0.00 |
| yaah | r3 | 1.70 | 1.85 / 1.70 / 1.70 | 0.15 | 1.60–1.90 | 1.70 † | 0.00 |
| deepagents-cli | r3 | 1.70 | 1.70 / 1.85 / 1.70 | 0.15 | 1.60–1.90 | 1.85 | −0.15 |
| hermes-agent-desktop | r3 | 2.00 | 2.00 / 2.00 / 2.00 | 0.00 | 1.85–2.15 | 2.60 † | −0.60 (≈ −0.30 ‡) |

† v1.3 froze this target at a high-mode run. ‡ like-for-like against v1.3's standard runs —
see below.

**Mean weighted RAISE 1.41** (v1.3: 1.49) — **Δ −0.08**. Movement is small and mostly
downward: 1 up, 6 flat, 5 down, the only move beyond one band step is hermes. Median run-to-run
spread 0.15 (v1.3: 0.20); aider is the noisiest target at 0.45.

## What moved

Category changes, frozen median vs v1.3 (LYD Limit Your Domain · BYKB Balance Your Knowledge
Base · IZT Implement Zero Trust · MYSC Manage Your Supply Chain · BART Build an AI Red Team ·
MC Monitor Continuously):

| Target | Changes |
|---|---|
| helperbot | IZT 0→1 |
| craftbot | LYD 2→1 |
| openai-customer-service | LYD 2→1, MYSC 1→2, BART 1→0 |
| aider | MYSC 2→1, MC 1→2 |
| openhands | BYKB 2→1 |
| deepagents-cli | MYSC 3→2 |
| hermes-agent-desktop | LYD 3→2, MYSC 3→2, BART 3→2, MC 3→2 |
| finbot, salesforce, autogen, uagents, yaah | none |

No single category dominates the way Manage Your Supply Chain did in v1.3. **Opus 5.5 is
somewhat stricter on Limit Your Domain and Supply Chain**, and moves in both directions
elsewhere.

**Severity is where the model shows most.** Across all 36 runs against three times the v1.3
counts: Critical 97 vs 84 (**+15%**), High 221 vs 180 (**+23%**), Medium 155 vs 177 (−12%),
Low 14 vs 0, Informational 1 vs 0; total findings +11%. Opus 5.5 escalates more readily, and
uses Low where v1.3 used none.

## Reading the v1.3 comparison

- **hermes — the −0.60 is mostly method, not model.** v1.3 froze hermes at its high-mode
  audit run (LYD 3, BYKB 2, IZT 2, MYSC 3, BART 3, MC 3 = 2.60), and its BASELINE.md records
  that the audit placed LYD and MC one band **above** a 3–0 standard-run consensus. v1.3's
  standard-mode hermes was therefore ≈ **2.30**, and the like-for-like change is ≈ **−0.30**:
  Supply Chain 3→2 and Red Team 3→2. This set's three runs scored 2.00 / 2.00 / 2.00 with
  identical category scores. Opus 5.5 found the maturity evidence v1.3 credited — exact pins
  and lockfile, osv-scanner in CI, Dependabot, security regression tests tied to fixed issues,
  a GHSA filter linked to its PR — and in both categories wrote that bands 2 and 3 were
  defensible and took the lower, citing what it found against them (an unverified
  `curl | bash` installer from `main`, unsigned desktop builds, no SBOM; no adversarial corpus,
  tooling or dated reports). **Accepted as the new reference calibration**, not treated as a regression.
- **openhands and yaah** were also high-mode freezes in v1.3, and v1.3 records that high mode
  landed **at or above** the standard median in all three audits. Their Δ here (−0.15, 0.00)
  is therefore an upper bound on how far Opus 5.5 sits below v1.3's standard runs; the exact
  v1.3 standard medians were recorded only in the gitignored `local/v1.3-freeze/` notes, which
  did not survive.
- **helperbot +0.25** is the only rise: Zero Trust 0→1 (a 0.25-weight category). The
  dominant path is still uncontrolled; what keeps it off 0 is model egress hard-coded to the
  two provider endpoints in `provider.js`, with the dominant-path ladder capping it at 1.

## Critical-theme gate — no Critical theme dropped

The hard gate (`tests/README.md`): every v1.3 Critical theme must still be carried by the
frozen exemplar. Checked by theme, not `R-NN`/`PRAX-` id, against all 28 v1.3 Critical
findings, and confirmed across all three runs rather than the exemplar alone:

**23 carried at Critical · 5 carried at a lower severity · 0 dropped.**

The five demotions, each consistent across runs (so a model calibration, not exemplar noise):

| Target | v1.3 Critical theme | Opus 5.5 | Runs |
|---|---|---|---|
| helperbot | any network caller reaches the agent (all-interface bind, wildcard CORS, no auth) | High | 3/3 |
| salesforce-help-agent-accelerator | prompt-only guardrails plus default-off audit — a jailbreak is neither prevented nor recorded | High — the default-off audit is High in every run; the prompt-only prohibitions appear separately (Medium in r3) and are never escalated as a compound | 3/3 |
| autogen-code-executor | the documented dangerous-command sanitizer does not exist in code | Medium | 3/3 |
| openhands | the host-direct sandbox copies the app server's full environment into the agent | High | 3/3 |
| yaah | the Notion MCP provider writes the operator's API token verbatim into generated config | High | 2/3 (Critical in r2) |

**autogen is flagged for 2.1.** "A documented safety control that does not exist in code" is
the class of divergence the remit audit exists to catch, and Medium understates it on a target
whose only other barrier is an opt-in approval hook. That is a candidate SKILL.md severity rule
(documented-but-absent control on a code-execution path → floor at High), not a baseline edit —
the exemplar is frozen as scanned.

The gate was computed two ways. A mechanical evidence-file-overlap matcher reports 2 drops
(craftbot's approval-architecture theme, openhands's unauthenticated-routers theme); both are
false drops, carried at Critical under different file citations (craftbot PRAX "No code path
requires owner approval…", openhands "The default control plane authenticates nobody…").
The classification above is by theme, read finding by finding.

## Secret hygiene

Praxen reports must never reprint a secret value. Checked non-vacuously across all 12
exemplars' outputs: every string literal assigned to a credential-shaped name, and every
high-entropy token, inside ±6 lines of every evidence citation in **all 36 runs** was
harvested from the pinned sources (54 values — including the finbot Flask key, the uagents
Helm seed and the CraftBot OAuth material) and searched for in the exemplar outputs. **None
appears.** The only matches were two non-secret identifiers (an environment-variable
placeholder and an "insecure, no auth" sentinel constant name).

## Threat models

Each target carries a threat model extracted from its **frozen exemplar** (contract 1.5,
`standards` 2026/2026/2026), one fresh-context Opus 5.5 subagent per target, following
`skills/behavior-verifier/THREAT_MODEL.md` with the extraction brief verbatim. The extractors
read only the workspace, the exemplar findings JSON and the remit — never another run or
baseline. Each graph passed the contract validator, the cited-finding cross-check against its
own findings JSON, an `analysis_ref`/`standards`/`model_identity` check, and the same secret
sweep as the analyses; the HTML is rendered with `--analysis-html` so the masthead links to
the analysis it was built against. No pinned workspace was modified.

| Target | Nodes | Edges | Boundaries | Threats | Confirmed | Potential | Partial | Mitigated | Attack paths |
|---|---|---|---|---|---|---|---|---|---|
| aider | 25 | 29 | 10 | 25 | 19 | 0 | 2 | 4 | 5 |
| autogen-code-executor | 22 | 30 | 9 | 23 | 20 | 2 | 0 | 1 | 4 |
| craftbot | 25 | 29 | 9 | 24 | 21 | 0 | 0 | 3 | 4 |
| deepagents-cli | 24 | 33 | 10 | 29 | 21 | 1 | 1 | 6 | 3 |
| finbot | 24 | 34 | 10 | 19 | 17 | 0 | 0 | 2 | 4 |
| helperbot | 21 | 22 | 8 | 20 | 15 | 1 | 1 | 3 | 3 |
| hermes-agent-desktop | 25 | 35 | 11 | 23 | 17 | 0 | 1 | 5 | 5 |
| openai-customer-service | 18 | 18 | 7 | 14 | 9 | 0 | 2 | 3 | 1 |
| openhands | 25 | 33 | 11 | 23 | 20 | 1 | 0 | 2 | 4 |
| salesforce-help-agent-accelerator | 22 | 29 | 7 | 14 | 11 | 1 | 0 | 2 | 2 |
| uagents | 23 | 30 | 9 | 20 | 18 | 2 | 0 | 0 | 3 |
| yaah | 25 | 34 | 9 | 22 | 15 | 2 | 1 | 4 | 4 |

**256 threats (203 confirmed · 10 potential · 8 partial · 35 mitigated), 42 attack paths.**
One repair round was used: autogen's graph coined a boundary archetype without saying so in
`notes`, as the contract requires; its extractor added the note (pre-repair copy kept; the
diff touches `notes.omissions` only).

**Contract friction the extractors reported** — inputs for the next contract revision, none
blocking: no archetype for an agent's reply to an untrusted user (salesforce), agent output
rendered in a higher-trust UI (hermes; finbot's stored XSS was filed under `data-at-rest`
instead), or sandbox → network egress (autogen) — three coined ids; no archetype for a hook gate
(yaah filed a second `tool-invocation`); no `notes` slot for edgeless nodes; ID rule 1 yields a
leading dash for `_private.py` files (craftbot and autogen independently dropped it by analogy
with the leading-dot rule); whether one finding may carry different
OWASP codes at different boundaries (applied on several targets); and whether an attack-path
origin may be a code or datastore node rather than an actor.

## Sources & scope

Pins, provenance tiers and the recovery method are in [`SOURCES.md`](SOURCES.md). Roster prominence and
development activity, re-snapshotted for this freeze, are in [`../ROSTER_HEALTH.md`](../ROSTER_HEALTH.md). Scope is as
in v1.3: deepagents scoped to `libs/code`, OpenHands at its pre-migration commit, hermes as one
combined workspace with `hermes-agent/` and `hermes-desktop/` as subdirectories.

All 12 pass `python3 tests/render/test_render.py` (schema-valid · HTML/TXT byte-identical
re-render · every `policy_rule_text` quoted verbatim from the pinned `<slug>-remit.md`) and
`python3 tests/render/test_render_threatmodel.py`.

## Known caveats

- **Model provenance lives outside the artifact.** The findings JSON does not record which
  model produced it; the `claude-opus-5-5` attribution here rests on each run's self-report and
  the session configuration. Recording the model in the findings JSON is a 2.1 candidate.
- **`artifact_count` is not mechanical** — it varies run to run on identical inputs because the
  model counts by judgement. Making it a computed value is a 2.1 candidate.
- **Four pins are RECOVERED-AMBIGUOUS** (see SOURCES.md) — the residual is a 0–8-day window of
  upstream history differing by 11–86 lines in files no finding cites.
- **v1.3's standard-mode medians for hermes/openhands/yaah were not recoverable** (above).
