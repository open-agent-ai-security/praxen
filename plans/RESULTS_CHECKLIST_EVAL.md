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
> **The current RT band is a floor artifact, not a measurement.** **Ten** of
> twelve baseline targets contain *zero* adversarial security testing — and the
> holistic scorer gave those ten identical-evidence targets **seven 1s and
> three 0s**. Same evidence, different score, no discernible reason. The
> checklist puts all ten on a stable 0.0 with nothing left to flip.
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
| openhands | NOT MET | NOT MET | NOT MET | NOT EVID | NOT MET | NOT MET | **0.0** | 1 | −1.0 |
| openai-customer-service | NOT MET | NOT MET | NOT MET | NOT EVID | NOT MET | NOT MET | **0.0** | 0 | 0 |
| aider | NOT MET | NOT MET | NOT MET | NOT EVID | NOT MET | NOT MET | **0.0** | 1 | −1.0 |
| autogen-code-executor | NOT MET | NOT MET | NOT MET | NOT EVID | NOT MET | NOT MET | **0.0** | 1 | −1.0 |
| craftbot | NOT MET | NOT MET | NOT MET | NOT EVID | NOT MET | NOT MET | **0.0** | 0 | 0 |
| finbot | NOT MET | NOT MET | NOT MET | NOT EVID | NOT MET | NOT MET | **0.0** | 1 | −1.0 |
| helperbot | NOT MET | NOT MET | NOT MET | NOT EVID | NOT MET | NOT MET | **0.0** | 1 | −1.0 |
| salesforce-help-agent | NOT MET | NOT MET | NOT MET | NOT EVID | NOT MET | NOT MET | **0.0** | 0 | 0 |
| uagents | NOT MET | NOT MET | NOT MET | NOT EVID | NOT MET | NOT MET | **0.0** | 1 | −1.0 |
| yaah | NOT MET | NOT MET | NOT MET | NOT EVID | NOT MET | NOT MET | **0.0** | 1 | −1.0 |

### 2.0 Correction — file counts are not evidence (2026-08-11)

An earlier revision of this document reported "security-control test file"
counts (hermes 38, deepagents 16, openhands 11, openai-cs 9) as supporting
evidence, derived from **filename patterns without reading the files**. Steve
challenged the openai-cs call. On inspection, **two of the four non-zero rows
were false**:

| Target | Claimed | What the tests actually do |
|---|---|---|
| hermes | 38 | **Verified real.** `_resolve_trust_level("official/attacker-skill") == "community"`, sibling-prefix spoofing, skills.sh typo-squatting, cross-profile write/patch bypass, tirith block-on-terminal-injection. Adversarial inputs throughout. |
| deepagents | 16 | **Verified real.** Genuine bypass attempts against a shell allow-list — `;`, pipes, `&&`, quoting, malformed input. |
| openhands | 11 | **False.** Docker/remote *sandbox provisioning service* lifecycle tests, plus React route guards (`permission-guard.test.ts` checks UI redirects). Matched on the words "sandbox" and "guard". |
| openai-cs | 9 | **False.** Guardrail *plumbing*: a stub guardrail returns `tripwire_triggered=True` and the test asserts the framework stops. No attack appears anywhere; the tripwire is written by the test. |

**This document's §3 argues that pattern matching cannot distinguish
adversarial testing from adversarial content — and its own evidence table was
built by pattern matching.** String right, meaning wrong, in the section
warning about exactly that. Recorded rather than quietly fixed: it is the
strongest available argument for keeping observation with the model, and for
the rule that a count of matching filenames is a place to start looking, never
a finding.

The distinction that survives, and that generalises: **does the test contain an
adversarial input, or does it verify that machinery fires when told to?**
Nothing to do with whether the control is a shipped product feature — the
original stated reason for discounting openai-cs, which was wrong.

### 2.1 The floor artifact

**Ten of twelve targets contain no adversarial security testing whatsoever**
(all but hermes and deepagents). The holistic scorer gave those ten:

- **RT = 1** — aider, autogen, finbot, helperbot, openhands, uagents, yaah
- **RT = 0** — craftbot, openai-customer-service, salesforce

**Identical evidence, two different scores, seven-to-three.** This is the #195
mechanism caught directly rather than inferred from score spread, and the
correction in §2.0 *strengthened* it: verifying the file counts moved openhands
and openai-cs into the no-evidence group, taking it from 7-of-12 to 10-of-12.

Under the checklist all ten land on a stable **0.0**, every item NOT MET.
Nothing left to flip.

**Note on item conditionality (design gap found here).** The first pass gave
openhands and openai-cs `MET` on "an automated runner exists" and `PARTIAL` on
"testing is ongoing" purely for having pytest and CI — 1.5 free points in the
red-team category for owning a normal test suite. Items 2–6 **qualify the
adversarial testing found in item 1**; where item 1 is NOT MET there is nothing
to qualify and they are NOT MET, not NOT EVIDENCED. Now applied above.

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
- **openai-cs 0 → 0.0** *(revised from 1.7 — see §2.0)*. Its guardrail tests
  contain no adversarial input; they verify the tripwire mechanism fires when a
  stub guardrail says to. The baseline's 0 was right.
- **openhands 1 → 0.0** *(revised from 1.7 — see §2.0)*. Sandbox provisioning
  lifecycle tests and frontend route guards. No adversarial testing.

## 2.5 Balance Your Knowledge Base — second category pass (2026-08-11)

The other collapsed category: **BKB scored 1 or 2 on all twelve targets**, never
0, never 3+. Hypothesis from the design: the missing under-provisioning items
would create range.

**Scored only what was read.** Three targets read properly, one partially. The
remaining eight are deliberately unscored — the RT pass established that
unverified counts are worthless.

| Target | Sources enumerated | Minimised | Grounded knowledge | Hallucination controls | Untrusted marked as data | Sensitive data out | **Checklist** | Baseline |
|---|---|---|---|---|---|---|---|---|
| salesforce-help-agent | MET | PARTIAL | MET | PARTIAL | NOT EVID | PARTIAL | **2.9** | 2 |
| finbot | PARTIAL | PARTIAL | MET | NOT MET | NOT MET | NOT MET | **1.7** | 1 |
| autogen-code-executor | MET | PARTIAL | **N/A** | **N/A** | NOT MET | NOT MET | **1.9** *(4 applicable)* | 1 |
| *aider (partial read)* | *PARTIAL* | *MET* | *MET* | *NOT MET* | *NOT MET* | *unread* | *provisional* | *1* |

Range across three fully-read targets: **1.7 – 2.9** (plus autogen at 1.9),
against `{1, 2}` for all twelve under the holistic scorer. Real range, but
narrower than the first revision claimed — see the retraction below.

### Retracted — the "category does not apply" mechanism (2026-08-11)

**An earlier revision claimed AutoGen's code executors "have no knowledge base,
no retrieval, no context assembly" and scored four of six items N/A, giving
0.0. That was wrong, and it was reasoned from the component's *name*.** Steve
asked whether it was overly simplistic. Reading the executors:

- **`work_dir`** — an explicit working directory the executed code reads and
  writes.
- **`extra_volumes`** — arbitrary host paths mountable into the container. The
  documented example is `{'/home/user1/': {'bind': '/mnt/vol2', 'mode': 'rw'}}`.
- **`bind_dir`** — host directory bound to the container work dir, hardcoded
  `{"bind": str(work_dir), "mode": "rw"}` in `_jupyter_server.py:360`.
- **Execution output returns into the model's context** —
  `CommandLineCodeResult(output="".join(outputs))`
  (`_docker_code_executor.py:376`), container logs decoded and returned (429,
  564). Whatever executed code prints — including the contents of any file it
  read from a mounted volume — reaches the next turn unmarked and untruncated.

That is a substantial information surface. **Two items are genuinely N/A**
(grounded domain knowledge, hallucination controls — the executor answers no
questions), not four. Re-scored at **1.9 against the baseline's 1** — close
agreement, not the dramatic divergence claimed.

**So there is no verified case of a "category does not apply" collapse.** The
mechanism may exist; it has not been demonstrated, and the flagship example
does not hold. The denominator concern below is correspondingly milder: four
applicable items give 1.25-point granularity, not 2.5.

### The recurring error, recorded

Three times in this workstream a conclusion was drawn from a **name** rather
than from the code:

1. Files matching `*guard*` counted as security tests (§2.0) — two of four rows
   false.
2. openai-agents-python discounted because "guardrails" is a shipped product
   feature — the real and better reason is that its tests contain no
   adversarial input.
3. A "code executor" assumed to have no knowledge surface — it has four.

Each was caught by Steve asking a question that required reading the code to
answer. This is the exact failure mode the checklist exists to prevent,
committed while designing the checklist, which is the strongest argument in
this document for why observation must stay with a model that reads and why
"evidence classes" must never degrade into name matching.

### Gap found in both the draft and the shipping knowledge base

The AutoGen re-read surfaced something worth more than the error that produced
it. **Execution and tool output flowing back into model context is an untrusted
-content channel that neither this draft nor `KB_RAISE_SCANNING.md` names.**
The shipping signal table lists "external content (email, web, user uploads) in
LLM context unvalidated" — tool results and execution stdout appear nowhere.

For agentic targets, tool output is the *dominant* untrusted channel: it is how
a poisoned file, a hostile web page, or an attacker-shaped API response reaches
the model. Draft item corrected below; the shipping-KB gap is independent of
this design work and worth its own issue.

### A defect the number was hiding

Salesforce's agent instruction says *"include sources in your response when
available from the knowledge articles."* Its configuration says
**`citations_enabled: False`** with an empty `citations_url`. The policy
requires citation; the implementation disables it. Two `filter_from_agent:
False` settings sit alongside it.

The holistic score for this was **2** — a number that surfaces none of it. The
checklist forces the question "are there hallucination controls?" to be
answered against configuration, and the answer names the exact line to fix.
This is the *"provide more evidence"* loop working in reverse: it tells the
owner what to *change*, not just what to send.

### New design problem this pass found

**N/A shrinks the denominator, which makes quantization worse, not better.**
With 4 applicable items each is worth 1.25 points on the 0–5 scale; at 2
applicable items it would be 2.5, coarser than today's 1-point bands. The
design's resolution argument (§3.4) silently assumed all items apply. Real but
milder than first reported.

Unresolved; the options are a minimum applicable-item count before a category
gets a number at all, reporting "insufficient applicable items" instead of a
score, or folding N/A-heavy categories out of the weighted average and
renormalising the weights. **This needs deciding before any of it is built.**

## 3. The mechanical sweep — a research instrument, and a cautionary one

**Correction (Steve, 2026-08-11): mechanization was never the goal, and this
section originally implied it was.** The checklist is model-answered
throughout; code does arithmetic only (design §3.2). The sweep existed to
survey 13 repositories cheaply for *this* eval, not as a proposed product
component.

It is reported here because it **under-performed**, and that failure is the
argument for keeping observation with the model. Of 14 probed items it screened
8 usably (MSC-1, -2, -4, -6, -7; RT-2, RT-3; ZT-8) and failed the rest in two
distinct ways:

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

**Conclusion:** *"is this adversarial security testing?"* is not a
pattern-matching question and never will be. Every false positive above is a
case where the string was right and the meaning was wrong; the recall failure
is a case where the meaning was right and the string was absent. Both are
category errors that only reading the code resolves.

The items stay model-answered. Where the eval's numbers came from mechanical
screening, they came with hand adjudication on top — and the screening layer
earned no place in the design.

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
- Pattern matching cannot answer the interesting items, with the failure modes
  now characterised rather than guessed.

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

1. ~~Steve adjudicates the disagreement cases~~ — **done 2026-08-11.**
   Bypass-shaped tests against your own control **partly count** (half credit),
   so deepagents settles at **1.7**. Whether an attack arrives through the real
   front door is judged as a **separate question** (attack-surface coverage),
   not folded into "do they test at all." openai-cs resolved itself once the
   tests were actually read (§2.0).
2. ~~Repeat the exercise for BKB~~ — **done, §2.5.** Range confirmed (0.0–2.9
   vs `{1,2}`), and a second, distinct collapse mechanism found: the category
   often does not apply and the scale cannot say so. **Open decision: how to
   score a category with few applicable items** — N/A currently makes
   quantization worse.
3. **Then the bench.** Variance is the claim that matters and it is still
   entirely unmeasured.
