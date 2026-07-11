<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxen 1.1 — Plan & Issue Triage

> **Branch:** `1.1` · **Type:** first functional line since 1.0 GA · **Grades against:** the `v1.0.2-claude48` baseline (see `RELEASE_1.0.2_BASELINE_REFRESH.md`, folded in first)

## Objective

1.1 is the first **functional** release since 1.0 GA: **scoring rigour**, **detection coverage**, **skill-flow & output quality**, and (deliberately) **schema evolution**. It is developed against the stable `v1.0.2-claude48` baseline so regressions are detectable and *intended* number movement is distinguishable from drift.

## Prerequisite — fold in 1.0.2 first

**Do not start 1.1 functional work until the `1.0.2` baseline + target-roster refresh is folded in.** Grading 1.1 changes against a 0.7.7-era exemplar would make intended calibration movement indistinguishable from noise. The 1.0.2 branch:
- re-freezes the suite on the stable 1.0.x skill, and
- refreshes the target roster (retires dead `sweep`/`langchain-sql`, adds CraftBot/uAgents/Agentforce).

Once `1.0.2` is green, merge it into `1.1`; `1.1` then carries `v1.0.2-claude48` (and the refreshed roster) as its reference.

## Regression discipline (important)

Several 1.1 items **intentionally move the numbers** — #48 (scoring rigour), #104 (new secret detection), #41 (new detection pattern), #7 (schema change), #111 (deterministic-layer normalization). The v1.0.2 baseline is the reference: grade every change against it, and for each moved number decide **intended vs regression** (`tests/README.md` › *What a release review looks like*). An intended calibration/detection/schema change is fine — note it, and **at 1.1 release re-freeze `v1.1-claude48`**. So 1.1 begins on a fresh baseline and ends with another.

## Issue triage (open issues → 1.1 buckets)

### A. Scoring rigour & consistency — the headline theme
- **#48** — RAISE scoring rigour: reduce per-category variance via a structured control-ledger + boundary decision rules. *Directly answers the "±0.3–0.5 variability / risk of being over-read as deterministic" critique from the project evaluation. Moves numbers — intended.*
- **#111** — normalize the OWASP tag-label separator in the deterministic layer (cross-model report consistency).
- **#117** — `challenging-findings.md`: add a 'damage model wrong' path + category-score cascade guidance.

### B. Detection coverage
- **#104** — entropy-based secret detection in `render.py`'s redaction backstop (catch unrecognized high-entropy credentials). *May add findings — intended.*
- **#41** — new named detection pattern: external API response → filesystem write (path-traversal class).
- **#65** — tool feedback from the uAgents scan: framework scanning, manifest resilience, discovery gaps.
- **#169** — **LLM08 (Vector & Embedding Weaknesses) systematically under-tagged** (1/15 despite ≥3 targets having in-scope vector stores). Root cause: co-applicable LLM08 starved by single-`owasp_llm`-scalar counting + a too-narrow `KB_LLM_TOP10` §LLM08. Fix = expand the LLM08 KB entry (+5 OWASP sub-risks; add a *detect vector store → audit* step), count secondary OWASP codes from `tags[]` in `owasp_coverage.py`, re-scan craftbot/sweep. **Schema-neutral — `schema_version` stays 2.0; NOT part of #7 / §D (schema evolution), and NOT an engine-reliability item (distinct from #65).** Surfaced by the 1.0.2 retirement-impact analysis (would falsely zero LLM08 on retiring devika).

### C. Skill-flow & output quality
- **#33** — interleave finding emission with analysis (eliminate the Step 9.9 synthesis burst / stream-stall).
- **#29** — Step 8.5: emit a finding-themes outline first (decomposition primer, stream-stall prevention).
- **#113** — wrap technical tokens in `<code>` consistently across ALL prose fields (SKILL).
- **#27** — report: finding default-state (collapsed vs expanded) + expand-all/collapse-all buttons.
- **#25** — split output-authoring conventions out of `SKILL.md` (rendering/MVC split).
- **#6** — `render.py` polish: finding-card confidence, Medium/Low badge. *(TXT High-findings shipped in 1.0.1 — confirm remaining scope.)*

### D. Schema evolution — careful: schema changes force a re-baseline
- **#7** — structure `policy_rule_text` / `policy_rule_ids` as arrays; fold into the render-pipeline refactor. *Largest blast radius: moves the byte-render gate and requires a re-baseline. Plan as one coherent migration or hold for 1.2 — see open questions.*
- **#5** — `schema.py` validator round 2: `policy_rule_ids` ↔ remit-rule cross-check.

### E. Harness support
- **#151** — add Google Antigravity (`agy` CLI) as a supported harness. *Functional (a new agent host, alongside Claude Code / Codex), distinct from a baseline target.*
- *(Baseline **target** roster — CraftBot #116, uAgents #64, dead-upstream swaps #69/#70, Agentforce — is handled in **1.0.2**, not here.)*

### F. CI / infra
- **#120** — replace the retired Gemini code-review gate. **Time-sensitive: Gemini Code Assist sunsets 2026-07-17 — pull this early**, independent of the rest of 1.1.
- **#127** — gate `examples/` in `test_render.py` (schema-validate + byte-render, like `tests/baselines/`).

### G. Docs / low / defer
- **#135** — docs simplicity pass (Tier 3): trim remaining over-complexity.
- **#4** — `SKILL.md` authoring aids & docs polish.
- **#118** — operator override + finding-revision records with provenance. *Explicitly post-1.0/1.x — 1.1 stretch or 1.2.*
- **#137** — chore: GA metadata in `PRAXEN_SPEC` + drop dangling `design/DEFERRED.md` ref. *Non-functional; verify/close — could ride 1.0.2.*
- **#90** — shared org-level brand/design system (Praxen side). *Cross-org coordination; not blocking.*
- **#2** — durable version-independent "standing config". *Explicitly deferred — not 1.1.*

## Proposed 1.1 shape (recommendation)

- **Must-have core:** **A** (scoring rigour #48/#111/#117) + **B** (detection #104/#41/#65), plus the time-sensitive **#120** (Gemini sunset). These deliver the eval-flagged improvements and keep CI healthy.
- **Strong candidates:** **C** (skill-flow / output quality #33/#29/#113/#27/#25/#6).
- **Decide deliberately:** **D** (schema #7) — the biggest single change; it forces a re-baseline. Either make it a 1.1 centerpiece or hold for 1.2. #5 can land regardless.
- **Opportunistic:** **E** (#151 harness), **F** (#127).
- **Defer:** **G** (except #120, and #137 which can ride 1.0.2).

## Open questions
1. **Schema change (#7) in 1.1 or 1.2?** Largest blast radius; gates the re-baseline strategy and the render-pipeline refactor.
2. **Reference model for the 1.1 re-baseline** — same Opus 4.8, or does 1.1 validate a new tier?
3. **How much of C** ships in 1.1 vs slips — the skill-flow items (#33/#29) touch the analysis path and could themselves move numbers.
