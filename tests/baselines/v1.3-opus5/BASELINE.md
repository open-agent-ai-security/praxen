<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Baseline — v1.3-opus5 (current)

The **v1.3 scoring re-freeze.** Supersedes `v1.2-opus5` (now archival). Same model and same
pinned sources as v1.2 — **the scoring pipeline is what changed** (#195).

For **7 of 12 targets** this is a clean like-for-like comparison and the movement is
attributable to the scoring fix. For the other five — **aider, autogen-code-executor,
craftbot, helperbot, uagents** — the #200/#201 remit cleanups landed pre-freeze, so the
remit those targets were scanned against also changed. Their deltas (−0.15, −0.15, 0.00,
−0.15, −0.15) mix the two causes and should not be read as measuring #195 alone.

Roster prominence + development-activity data lives in `../ROSTER_HEALTH.md`.

## What changed from v1.2

- **#195 — RAISE scores are assigned from committed evidence, not working memory.** In v1.2
  scores were set at SKILL.md **Step 5**, from the workspace read held in working memory,
  *before* findings were decomposed or drafted; Step 9.4 merely transcribed them. In 1.3, Step 5
  gathers evidence only, a new **Step 8b** runs an enumerated **M1–M12 maturity sweep** (fixed
  search patterns; verified absences recorded with equal weight to hits), and **Step 9.4 assigns
  the scores** from the committed evidence set (THEMES outline + positives + the M-record +
  Step 5 RAISE NOTES).
- **Boundary rules + provenance test** consolidated into `KB_RAISE_SCANNING.md`: the
  dominant-path ladder (nothing on the dominant path → cap 1; prompt-only → cap 2; operative
  code → uncapped), opt-in/default-off controls as capability not posture, and the provenance
  test — adversarial material counts only when the project attacks its **own** defences.
- **Model unchanged:** Claude Opus 5 (`claude-opus-5[1m]`). `praxen_version 1.3.0`,
  `schema_version 3.0` (unchanged — nothing serialised changed).
- **Remits: 7 unchanged, 5 materially revised** by the #200/#201 over-reach cleanups landed
  pre-freeze (see the attribution note above). Each target dir pins its freeze-state remit as
  `<slug>-remit.md`, verified byte-identical to the `tests/remits/<slug>.md` the scans
  actually read — so the two baselines' pinned copies show exactly what changed.

## Freeze method — median-of-3, with three high-mode substitutions

Each target was scanned **3× on identical inputs** (36 runs). Frozen value = the **median-weighted
run**; where two runs tie at the median, the **lowest-numbered** run is taken (deterministic, no
cherry-picking).

**Three targets are frozen at a high-mode run instead** — hermes, openhands, yaah — the two
largest movers and the widest-spread target, each given a full high thinking-mode audit before
the freeze. **This is a deliberately mixed method: those 3 are scored by a deeper, costlier
process than the other 9.** It is recorded here so the baseline is not read as uniform.

| Target | Frozen run | Weighted RAISE | 3× spread | v1.2 | Δ |
|---|---|---|---|---|---|
| helperbot | run2 | 0.45 | 0.15 | 0.60 | −0.15 |
| finbot | run1 | 1.00 | 0.00 | 0.90 | **+0.10** |
| craftbot | run2 | 1.30 | 0.15 | 1.30 | **0.00** |
| autogen-code-executor | run1 | 1.40 | 0.25 | 1.55 | −0.15 |
| salesforce-help-agent-accelerator | run1 | 1.40 | 0.25 | 1.70 | −0.30 |
| openai-customer-service | run1 | 1.45 | 0.15 | 1.75 | −0.30 |
| aider | run3 | 1.55 | 0.30 | 1.70 | −0.15 |
| uagents | run1 | 1.55 | 0.15 | 1.70 | −0.15 |
| openhands | **high** | 1.60 | 0.15 | 2.00 | −0.40 |
| yaah | **high** | 1.70 | 0.25 | 2.15 | −0.45 |
| deepagents-cli | run2 | 1.85 | 0.45 | 2.15 | −0.30 |
| hermes-agent-desktop | **high** | 2.60 | 0.55 | 2.55 | **+0.05** |

**Mean weighted RAISE 1.49** (v1.2: 1.67) — **Δ −0.18**. Had all 12 frozen at their medians the
mean would be 1.45 (Δ −0.22), which reproduces the replay bench's pre-registered −0.23
prediction; the high-mode substitutions account for the difference.

Movement is **bounded and two-directional**: 2 targets up, 1 flat, 9 down, none beyond −0.45.
Median 3× spread 0.20.

## Provenance gate — every run in this baseline is verifiably 1.3

A stale **1.1.0** plugin was registered on the build machine and subagents defaulted to it,
silently producing scans with **none** of the #195 logic. Every run in this baseline therefore
had to clear a **dual gate**, checked on disk by the orchestrator, not self-reported:

1. `praxen_version == "1.3.0"` in the rendered findings JSON, **and**
2. a `MATURITY (M1-M12)` block present in the run's evidence checkpoint — a 1.3-only artifact,
   which catches a run that stamps 1.3.0 via the renderer while having followed 1.1.0 process.

**36/36 standard runs and 3/3 high-mode runs passed both.** Runs that failed either gate — and
all runs that landed on the Opus-4.8 classifier fallback — were excluded, never scored.
Detail: `../../../local/v1.3-freeze/PIN_INCIDENT.md`.

## What drives the movement

1. **Manage Your Supply Chain is the dominant mover** — down in 6 targets (aider 3→2,
   autogen 2→1, openai-cs 3→1, openhands 3→2, salesforce 2→1, yaah 3→2), **up in 1**
   (hermes 2→3). The M1–M12 sweep asks for real inventory / pinning / scanning evidence rather
   than crediting the impression of hygiene.
2. **Build an AI Red Team moves in both directions**, but mostly down — **five** targets fell:
   aider 1→0, finbot 1→0, yaah 1→0 (demo/CTF/training material, where the shipped attack content
   *is* the product — the provenance test), plus **helperbot 1→0** and **deepagents-cli 3→2**.
   deepagents is the largest RT drop in the set and is *not* a demo target: its programme is real
   but the sweep found no adversarial corpus, tooling, or dated results. Against that, RT rose on
   **openai-cs** (0→1) and **held at 3 on hermes**, where the sweep found a genuine closed loop —
   GHSA-rhgp-j443-p4rf and GHSA-5qr3-c538-wm9j traced to fixing PRs, the fix at
   `tools/env_passthrough.py:48-100`, regression test beside it. The movement is two-directional,
   which is the evidence #195 corrects rather than deflates — but note the instrument is
   asymmetric by construction: three of the four boundary rules can only lower a band, and rule 4
   breaks ties downward.
3. **Limit Your Domain down in 3** (salesforce, uagents, yaah — all 3→2) via the dominant-path
   ladder: prompt-only domain framing now caps at 2. (craftbot's LD is unchanged at 2.)
4. **Two targets improved.** finbot +0.10 (ZT 0→1: the ladder credits its genuinely narrow,
   code-enforced tool surface instead of flooring the category) and hermes +0.05.

## High-mode audit results (hermes, openhands, yaah)

**35 findings audited — per-finding verdicts: 35 CONFIRMED, 0 UNSUPPORTED, 0 REMIT-DEFECT.**
(Rule-level *remit feedback* is tallied separately and is not zero — see the caveats below.) The auditor is known to
kill bad findings when they exist — the FP-injection test caught 4/4 planted fakes while
retaining ~48 real findings — so a clean sweep here is signal, not a rubber stamp.

- **openhands** — the hypothesis that its drop came from excluding `enterprise/` is **refuted**.
  The in-scope tree carries the Supply Chain and Monitor evidence and it was credited (Dependabot
  across six ecosystems, SHA-pinned Actions, PostHog at seven `app_server` call sites, Laminar
  plumbing). The one enterprise-only item cuts *against* the target: `ghcr-build.yml:42-43`
  enables SBOM/provenance for the enterprise image while `build_app` leaves both `false` — the
  subject's own shipping artifact gets no inventory.
- **yaah** — Red Team 0 confirmed under the provenance test's *second* row (ships to users →
  absent, not the demo-suite ceiling of 1). The adversarial material targets the **user's**
  codebase; nothing was ever pointed at yaah's own defences (no `.planning/`, no
  `SECURITY_AUDIT.md`, no threat model, no fix ledger, no test over `CommandGuard`/`SecretScanner`).
- **hermes** — the three unstable categories (BK/ZT/RT) adjudicated to exactly the median run's
  values. Its independent 8b re-run caught two would-be errors in opposite directions: shipped
  *offensive* skills (`godmode/auto_jailbreak.py`, web-pentest) are product, not practice, and
  crediting them would have inflated RT to 4; and an M9 recount returned a false "none" from a
  `grep --include` argument-order artifact that would have dropped RT to 2.

**Observed live:** openhands's first-pass (Step 5) read gave SC 1 / RT 0 / MON 1; after the
Step 8b sweep, SC 2 / RT 1 / MON 2 — all three *up*, each on concrete evidence. That is exactly
the maturity blindness #195 was built to fix, caught in the field.

## Sources & scope

Pinned SHAs in `../../../local/v1.3-freeze/CLONE_SHAS.txt`, identical to the v1.2 pins in
`../../../local/v1.2-owasp2026-baseline/SOURCES.md`. **Every target was cloned from its pinned
SHA, never HEAD** — the first freeze attempt cloned HEAD and six targets had drifted upstream;
that batch was discarded (`PIN_INCIDENT.md`). OpenHands is scanned at its **pre-migration**
commit `652503005` (the Agent-Canvas rewrite cleared the Python tree). deepagents remains scoped
to `libs/code` as in v1.2.

Two targets render an `agent_slug` that differs from their stable baseline slug — deepagents
(`deepagents-code`) and hermes (`hermes`). Both were re-slugged to the baseline identifier by
correcting the draft manifest and **re-running the real converter and renderer** (not by
renaming files); both re-renders were verified byte-identical to the original except the scan
block, with scores unchanged (1.85 and 2.60).

## Known caveats

- **Mixed freeze method** — 3 of 12 targets frozen at high mode (above). Cross-target
  comparisons within this baseline should account for it.
- **Remit defects surfaced by the auditors** (tracked, none change a finding): **hermes R-10**
  (Trusted Domains closure so broad that documented routine egress reads as trust expansion),
  **openhands R-22** (authorized-counterparties closure omits operator-configured observability
  providers, so the target's own consent-gated telemetry violates it by construction; **R-17**'s
  `rule_text` had also been truncated to a clause that on its own *permits* what PRAX-002
  reports — materially fixed), **yaah R-11/R-24/R-31**. These feed the #201/#198 cleanup.
- **Claims-ledger correction:** high mode landed **≥ median in all three audits**, reversing the
  pre-#195 x-high finding that thinking modes trend *lower*. With #195 the deeper sweep surfaces
  more real maturity evidence than adjudication removes. The "modes trend lower" statement must
  be re-scoped to pre-#195.
- **hermes remains the widest-spread target** (0.55). Its high-mode run also placed LD and MON a
  band above a 3–0 standard-run consensus; that divergence is recorded as variance in
  `../../../local/v1.3-freeze/SCOREBOARD_1.3.0.md`.

All 12 pass `python3 tests/render/test_render.py` (schema-valid · HTML/TXT byte-identical
re-render · every `policy_rule_text` quoted verbatim from the pinned `<slug>-remit.md`).
