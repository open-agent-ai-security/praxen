<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Results — RAISE checklist first eval (#195)

> **Run 2026-08-11** against the 12 pinned v1.2-opus5 baseline source trees
> (`local/v1.2-owasp2026-baseline/src/`, SHAs in `SOURCES.md`) plus
> `open-agent-ai-security/socxen`. Checklist draft:
> `DESIGN_RAISE_CHECKLIST.md`. **No scans run** — this evaluates the *rubric*
> against source evidence, which is the whole point of the replay approach.
> Cost: ~0 scan tokens; a mechanical sweep plus hand adjudication.
>
> ## Headline
>
> **The current RT band is a floor artifact, not a measurement.** Seven of
> twelve baseline targets scored exactly RAISE `RT = 1` while containing *zero*
> observable adversarial-testing evidence — and two targets that do have real
> security testing scored *lower* than targets that have none. The checklist
> reorders them correctly using evidence anyone can re-check.
>
> **Agreement holds where the holistic score is trustworthy:** socxen scores
> **4.6** against a prior holistic **4**; hermes **2.9** against **3**.

---

## 1. What was measured

Two passes:

1. **Mechanical sweep** (`checklist_sweep.py`, session scratchpad) — artifact
   presence for 14 of the 39 items across all 13 trees.
2. **Hand adjudication** of the full RT category (6 items) for all 13, using
   the sweep plus targeted inspection.

RT was chosen as the deep-dive because it is the category the 0–5 scale
collapses hardest: 7 of 12 targets sit at exactly 1.

## 2. RT results — hand-adjudicated

`score = 5 × (points earned / 6 applicable)`, MET 1.0 / PARTIAL 0.5 / NOT MET 0.

| Target | RT-1 corpus | RT-2 runner | RT-3 ongoing | RT-4 feedback | RT-5 gate | RT-6 surface | **Checklist** | Baseline RT | Δ |
|---|---|---|---|---|---|---|---|---|---|
| **socxen** | MET | MET | PARTIAL | MET | MET | MET | **4.6** | *4 (prior)* | +0.6 |
| **hermes-agent-desktop** | MET | MET | PARTIAL | NOT EVID | PARTIAL | PARTIAL | **2.9** | 3 | −0.1 |
| deepagents-cli | PARTIAL | MET | PARTIAL | NOT EVID | NOT MET | NOT MET | **1.7** | 3 | −1.3 |
| openhands | PARTIAL | MET | PARTIAL | NOT EVID | NOT MET | NOT MET | **1.7** | 1 | +0.7 |
| openai-customer-service | PARTIAL | MET | PARTIAL | NOT EVID | NOT MET | NOT MET | **1.7** | 0 | **+1.7** |
| aider | NOT MET | NOT MET | NOT MET | NOT EVID | NOT MET | NOT MET | **0.0** | 1 | −1.0 |
| autogen-code-executor | NOT MET | NOT MET | NOT MET | NOT EVID | NOT MET | NOT MET | **0.0** | 1 | −1.0 |
| craftbot | NOT MET | NOT MET | NOT MET | NOT EVID | NOT MET | NOT MET | **0.0** | 0 | 0 |
| finbot | NOT MET | NOT MET | NOT MET | NOT EVID | NOT MET | NOT MET | **0.0** | 1 | −1.0 |
| helperbot | NOT MET | NOT MET | NOT MET | NOT EVID | NOT MET | NOT MET | **0.0** | 1 | −1.0 |
| salesforce-help-agent | NOT MET | NOT MET | NOT MET | NOT EVID | NOT MET | NOT MET | **0.0** | 0 | 0 |
| uagents | NOT MET | NOT MET | NOT MET | NOT EVID | NOT MET | NOT MET | **0.0** | 1 | −1.0 |
| yaah | NOT MET | NOT MET | NOT MET | NOT EVID | NOT MET | NOT MET | **0.0** | 1 | −1.0 |

Supporting evidence counts (security-control test files; security CI workflows):

```
hermes-agent   38 / 1      deepagents  16 / 0      openhands    11 / 0
openai-cs       9 / 0      autogen      0 / 1      all others    0 / 0
```

### 2.1 The floor artifact

Seven targets — aider, autogen, finbot, helperbot, uagents, yaah, and
(baseline) openhands — scored **RT = 1** with no adversarial testing, no
security-control tests, and no security CI. Meanwhile craftbot, salesforce and
openai-cs scored **RT = 0** on the same emptiness. **Identical evidence
produced different scores**, which is the #195 mechanism caught in the act,
directly rather than through score spread.

Worse, it inverts: **openai-customer-service has 9 security-control test files
and scored 0; uagents has none and scored 1.**

Under the checklist all seven no-evidence targets land on a stable **0.0** with
every item NOT MET. There is nothing left to flip.

### 2.2 Where the holistic score was right

socxen and hermes — the two targets with genuine practice — land within 0.6 and
0.1 of their holistic scores. The checklist is not simply harsher; it agrees
where there is something real to see and diverges where the holistic judgment
was filling a vacuum.

### 2.3 Where it disagrees, and why

- **deepagents 3 → 1.7.** 16 security-control test files (a thorough shell
  allow-list suite covering pipes, `;`, `&&`/`||`, quoting, case, malformed
  input) but no threat model, no red-team corpus, no release gate, and nothing
  testing the LLM loop against untrusted input. Good control unit-testing is
  not adversarial testing of an agent. **Needs Steve's adjudication** — this is
  the sharpest ground-truth question the eval produced.
- **openai-cs 0 → 1.7.** Nine guardrail tests. Note these largely test the
  project's *own shipped guardrail feature* — product QA, which is why RT-1 is
  PARTIAL rather than MET. Still strictly more than the zero its 0 implied.

## 3. What is mechanically decidable — measured, not assumed

Of 14 probed items, the sweep produced **usable determinism on 8** (MSC-1, -2,
-4, -6, -7; RT-2, RT-3; ZT-8) and **failed on the rest**, in two distinct ways:

**Precision failures (false positives).** Filename matching cannot tell
adversarial testing from adversarial *content*:

| Target | Spurious hit | Why it is wrong |
|---|---|---|
| helperbot | `scenarios/*-injection`, `test/attack-log-*.test.js` | A deliberately-vulnerable app: the attacks are the product |
| yaah | `.claude/skills/the-fool/references/red-team-adversarial.md` | A skill *about* red-teaming, not evidence of red-teaming |
| craftbot | `skills/differential-review/adversarial.md`, `memory/injector.py` | Product content; and a memory injector is not prompt injection |
| craftbot | `app/security/prompt_sanitizer.py` | A **control** (ZT-1), not a test — right category, wrong one |
| autogen | `SECURITY.md:BLOCK` | Matched `<!-- BEGIN MICROSOFT SECURITY.MD V0.0.9 BLOCK -->` |

**Recall failure (the important one).** The first sweep **missed hermes
entirely** — the second-strongest RT practice in the corpus — because its 38
security tests are named `test_skills_guard.py`, `test_command_guards.py`,
`test_cross_profile_guard.py`, and no filename contains "redteam" or
"adversarial". A second pass keyed on control-guard naming found them, along
with deepagents' 16, openhands' 11 and openai-cs' 9. **Every non-zero RT score
in this eval except socxen came from the corrected pass**, so the naive sweep
would have reported a corpus in which only socxen tests anything.

**Conclusion:** artifact presence is a *screening* layer, not the answer.
RT-2/RT-3 (does a runner exist, is there a dated series) are reliably
mechanical. RT-1/RT-6 (is this adversarial testing, does it cover the real
attack surface) require judgment and must stay model-answered with the
evidence classes as guidance.

## 4. Corrections this eval forced on the draft

1. **RT-2 item text** — originally "wired into CI." Socxen's runner is
   deliberately *not* CI (a pre-release live model sweep), so the wording would
   have scored the stronger practice lower. Now: "an automated, repeatable
   runner exists," CI sufficient but not necessary.
2. **RT-5 detector** — the same CI-centric bias reappeared in the *code* after
   being fixed in the *item text*: the probe read only workflow files, so
   socxen's stated 🔴 BLOCK release bar (`security/redteam/HISTORY.md`) went
   undetected. The bias is sticky; every item needs the check applied twice.
3. **RT-1 needs conjunction, not any single artifact.** A red-team directory
   only counts when it also holds a runner or dated results. Tiered to
   STRONG / WEAK(judgment) / none.
4. **Scope question raised, unresolved.** Scan instructions scope the subject
   (e.g. AutoGen's executors, not the monorepo) while hygiene sweeps run
   tree-wide. RT/MSC/MC are project-practice items and read naturally
   tree-wide; LYD/BKB/ZT are subject-scoped. The checklist must state which
   scope each item uses. **Not yet specified in the design.**
5. **Multi-tree targets.** hermes-agent-desktop spans two source trees; the
   first sweep covered one. Item evaluation must enumerate all trees in a
   target.

## 5. What this does and does not show

**Shows:**

- The RT band carries a floor artifact that the checklist removes, and the
  removal is verifiable from evidence rather than from judgment.
- The checklist reproduces the holistic score where the practice is real
  (socxen 4.6 vs 4; hermes 2.9 vs 3).
- Roughly half the probed items are mechanically screenable; the other half
  are not, and the failure modes are now characterised rather than guessed.

**Does not show:**

- **Any variance reduction.** Nothing here was replayed. The §3.3 independence
  hypothesis remains untested and unclaimed — that needs the bench (design
  §6.1), N ≥ 10 replays with the unchanged rubric as same-day control.
- **Anything about the other five categories.** Only RT was hand-adjudicated.
  BKB — the other collapsed category, stuck at {1,2} across all 12 — has not
  been evaluated at all.
- **Correctness of the checklist's own calls.** Scored by one operator
  (Claude), unreviewed. deepagents 3 → 1.7 in particular is a judgment call
  about whether control unit tests count as adversarial testing.

## 6. Next

1. **Steve adjudicates the disagreement cases** — deepagents (3 → 1.7) and
   openai-cs (0 → 1.7). These become ground-truth anchors.
2. **Repeat the exercise for BKB**, the other collapsed category, where the
   design predicts the restored under-provisioning items (BKB-3, BKB-4) create
   the missing range.
3. **Then the bench.** Variance is the claim that matters and it is still
   entirely unmeasured.
