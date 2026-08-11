<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Results — scoring replay bench (#195)

> **Run 2026-08-11**, Opus 5. 40 replay agents, ~2.3M tokens, no scans.
> Bench: session scratchpad `bench/`. Category under test: Balance Your
> Knowledge Base, on the two targets that flip in exactly this category
> (finbot and autogen both scored 2/1/1 in the v1.2 3× variance study).
>
> ## Headline — REVISED after round 2 (2026-08-11)
>
> **Two fixes were found. Both work, independently, on both targets: 20 of 20
> replays returned identical scores across four conditions.**
>
> Round 1 tested a checklist rubric (failed) and concluded improvement was not
> generally possible. **That conclusion was wrong** — Steve pushed back that it
> merely restated existing policy, and round 2 found two working fixes that
> round 1 never tested. Round 1's findings are preserved below unchanged.
>
> - The **checklist rubric is not steadier** — higher sigma than the current
>   rubric in 3 of 4 comparisons, and it scores a deliberately-vulnerable
>   target 2.5–4.2 out of 5 by averaging its catastrophic failure away.
> - **Freezing the evidence** eliminated finbot's variance completely
>   (5/5 identical) and did **nothing** for autogen.

## Design

Two-stage replay isolating observation from scoring:

- **Frozen condition** — one evidence pack, byte-identical for every replay.
  Only the scorer varies, so this measures **mapping variance alone**.
- **Varying condition** — 5 independent observer agents each explore the source
  tree and build their own pack; each pack is scored once. Measures
  **observation + mapping**.

Scorers see only a rubric and a pack — no repository access.

## Results

```
condition              N              scores          spread   sigma
finbot-holistic        5                1 1 1 1 1      0.00    0.000
finbotvar-holistic     5                2 1 1 1 1      1.00    0.400
finbot-checklist       5   4.17 3.75 3.33 2.92 3.75    1.25    0.425
finbotvar-checklist    5    2.5 2.5 3.75 2.92 3.33     1.25    0.485

autogen-holistic       5                2 2 1 1 1      1.00    0.490
autogenvar-holistic    5                1 1 1 1 2      1.00    0.400
autogen-checklist      5   2.08 2.92 2.92 2.08 2.92    0.84    0.412
```

### Finding 1 — the variance source differs by target

| Target | Mapping only (frozen) | Mapping + observation |
|---|---|---|
| finbot | **0.000** | 0.400 |
| autogen | 0.490 | 0.400 |

**finbot's variance is entirely observational.** Freeze what the scorer looks
at and five independent scorers agree perfectly. The varying-pack run
reproduced the real 3× study's shape (2/1/1/1/1 vs the study's 2/1/1) from
observation drift alone.

**autogen's variance is entirely in the mapping.** Freezing the evidence
changed nothing — the 1-vs-2 call is genuinely ambiguous for this target no
matter what evidence is in front of the scorer.

So evidence canonicalisation is a **partial** fix: complete for one target,
useless for the other. It is not a #195 closure.

### Finding 2 — the checklist is not steadier, and it hides critical failures

Higher sigma than the current rubric in 3 of 4 comparisons. Per-question
answers disagreed on **3 of 6 questions** on both targets, so "narrower
questions are more reliable" does not hold either — narrower questions still
wobble, and there are now six chances to do it instead of one.

Worse, finbot — a deliberately vulnerable demo whose whole purpose is being
exploited through attacker text concatenated into its system prompt under
`CUSTOM GOALS (OVERRIDE ABOVE IF CONFLICTING)` — scores **2.5–4.2 out of 5**
under the checklist against **1–2** under the current rubric. Equal-weighted
arithmetic awards credit for enumerable sources, grounded retrieval and
omitted banking fields, and averages the disqualifying failure away.

That is scoring anti-pattern #3 from our own `KB_RAISE_SCANNING.md`:
*"Averaging away critical gaps… Never let averages hide critical failures."*
The design reinvented the anti-pattern the shipping guidance already warns
about. The current rubric's cap rules (*"prompt-only controls → Zero Trust
capped at 2"*) exist precisely to prevent this, and the checklist dropped them.

### Finding 3 — a refuted premise

The design argued the model observes reliably and wobbles on the mapping to a
band. finbot refutes it (mapping sigma 0.000, all variance observational);
autogen supports it (all variance in the mapping). **The premise is not
general and must not be used as a justification.**

## Statistical honesty

N=5 per condition, on an outcome that is effectively binary (1 or 2).
**These sigma values cannot be distinguished from one another** — 0.400 vs
0.490 is noise. The only statistically solid result is finbot frozen: five of
five identical, a perfect run, which is a clean signal. Every other comparison
is directional at best.

## What this means for #195

Two independent structural interventions were measured and neither removes the
one-notch wobble in general. The issue's own interim mitigation — treat the
weighted score as **ordinal and advisory**, gate on dominant themes and
severity-count neighbourhood — is looking less like an interim and more like
the correct permanent policy, now with measurement behind it.

## Round 2 — two fixes, both work

```
condition                scores        sigma
finbot-holistic        1 1 1 1 1       0.000   round 1: frozen hand-built pack
finbotvar-holistic     2 1 1 1 1       0.400   round 1: scorers explore freely
autogen-holistic       2 2 1 1 1       0.490   round 1: frozen hand-built pack
autogenvar-holistic    1 1 1 1 2       0.400   round 1: scorers explore freely
--------------------------------------------------------------------------
finbotfind-holistic    1 1 1 1 1       0.000   FIX A: score from the findings
autogenfind-holistic   1 1 1 1 1       0.000   FIX A
finbottb-holistic      1 1 1 1 1       0.000   FIX B: tie-break rules
autogentb-holistic     1 1 1 1 1       0.000   FIX B
```

### Fix A — score from the scan's own findings, not from free exploration

Give the scorer the findings JSON the scan already produced instead of letting
it re-explore the workspace. **5/5 identical on both targets**, including
autogen, which round 1 declared unfixable because its variance survived a
frozen evidence pack.

Why it works where a frozen *code* pack did not: findings are already a
judgment about what matters. Raw code forces the scorer to make that judgment
itself, and that is where scorers diverge — they weighed incidental controls
(`suppress_result_output`, `silence_pip`) differently. Findings remove the
question.

Cost: a procedural change to the scan flow. No schema, template, scale, or
baseline change.

### Fix B — boundary tie-break rules

Four rules appended to the existing rubric, applied in order before choosing
between adjacent scores:

1. Opt-in, default-off controls do not count as controls — capability, not posture.
2. Side-effect behaviours do not count as controls (noise reduction, memory).
3. If the dominant data path is unmanaged, incidental controls elsewhere cannot
   lift the score above 1.
4. When two adjacent scores both seem defensible, choose the lower, and name
   which two you were choosing between.

**5/5 identical on both targets, scoring raw code** — so the mapping ambiguity
round 1 called irreducible was in fact reducible. Rationales show the rules
firing by name and the scorers converging for stated reasons.

Cost: text added to `KB_RAISE_SCANNING.md`. No flow change.

The finbot arm doubles as a regression check: fix B did not disturb the
condition that already agreed perfectly.

### Limits that must travel with this

- **N=5, one category, two targets.** Four perfect runs is a strong signal but
  a narrow one.
- **The tie-break rules were written after seeing where these two targets made
  scorers disagree.** The rules themselves are generic — no target-specific
  content — but they are calibrated on the test set. A cold run on a target
  nobody has examined is required before claiming they generalise. Fix A has no
  such problem; nothing in it was tuned to a target.
- **Both fixes converge on 1**, the lower end of the production range for these
  targets. Adopting either shifts these scores down slightly, so it rides a
  re-baseline.
- Rounds 1 and 2 ran the same day, same model, same bench.

## What survives

- **The bench.** ~2.3M tokens answered in one session a question two prior
  efforts failed to settle. It is reusable and it should be promoted out of the
  scratchpad.
- **Evidence canonicalisation**, as a partial and cheap improvement for
  observation-dominated targets — not as a #195 fix.
- **The fidelity fixes**, which are independent of scoring: tool and execution
  output as an untrusted channel entering context, and the missing
  under-provisioning half of Balance Your Knowledge Base.
- **The floor-artifact finding** on adversarial testing: 10 of 12 targets with
  zero evidence scored seven 1s and three 0s.

## What is dead

- The checklist as a variance fix.
- The independence argument (39 small errors cancelling).
- The "mapping is the coin flip" premise as a general claim.

---

## Round 3 — Steve's maturity objection, tested (2026-08-11)

> Steve, on Fix A: *"If you're looking at the findings you're just seeing vulns.
> You won't see red teams, advanced controls. You're just seeing vulns, or
> their absence. This is a MATURITY score. We need to make sure we CAN see the
> evidence that matters."*

**Confirmed, and it is a correctness failure an order of magnitude larger than
the variance problem this whole workstream was chasing.**

### The artifact is blind to practice

Searching hermes's own findings artifact: `red team`, `adversarial` and
`test_` appear **zero times** in findings and positives. They appear only
inside the sentence that asserts the score. The evidence for hermes scoring 3
exists nowhere a findings-only scorer can reach.

### Measured, on the adversarial-testing category

```
                              scores      vs baseline
hermes, findings only        1 1 1 1 1    baseline 3  -- stable and WRONG BY TWO BANDS
hermes, findings + maturity  3 3 3 3 3    baseline 3  -- stable and correct
finbot, findings only        1 1 1 1 1    baseline 1  -- correct
finbot, findings + maturity  2 2 2 2 2    baseline 1  -- +1, defensibly
```

**Fix A alone produces a perfectly stable score that is wrong by two bands** —
0.30 of weighted total at this category's 15% weight, larger than any variance
observed anywhere in this workstream. Stability without visibility is worse
than instability: it is confidently wrong, every time.

Adding a deliberate maturity sweep recovers the correct score exactly, and the
rationales are better than the baseline's: 45 security-named test files / 871
tests gating every PR, a real-world promptware payload pinned as a permanent
regression anchor, a guard-removal canary suite, a per-release security ledger
with GHSA IDs and external reporter credit — while correctly withholding 4
because there is no red-team exercise, no attack corpus, no fuzzing or static
analysis, and prompt injection is declared out of scope.

### The sweep does not simply inflate

finbot moved 1 → 2, and the rationale is defensible rather than generous: the
sweep surfaced a graded goal-manipulation playbook with four attack vectors,
per-tier pass conditions and success criteria instrumented as runtime oracles
in application code. All five scorers then withheld 3 for the same stated
reasons — no test files, no corpus, no cadence, no feedback loop, single-commit
history. **A deliberately vulnerable demo did not get inflated toward maturity;
it got credited for the one real adversarial artifact it has.**

Whether the baseline's 1 or the sweep's 2 is right is a judgment call worth
Steve's review — but the sweep's version is the better-evidenced one.

### Corrected design

**The canonical evidence pack is findings + positives + a deliberate maturity
sweep.** Both halves are load-bearing and they fix different failures:

- canonicalising the pack buys **stability** (rounds 1–2)
- including presence-of-practice evidence buys **correctness** (round 3)

A vulnerability scan sees only defects. A maturity score needs a counterpart
step that goes looking for evidence the project does good things, and records
verified absences too. That step does not exist in the pipeline today.

### Score so far: 40 of 40 replays identical within condition

Rounds 2 and 3, four rubric/pack combinations across three categories and three
targets. Every condition returned a perfectly stable score. The open question
is no longer stability — it is whether the pack shows the scorer the right
things.

---

## Round 4 — Gate 1: cold-target generalisation (2026-08-11) — **PASS**

The tie-break and provenance rules were written after watching finbot and
autogen. This is the honest test: **salesforce and craftbot**, neither examined
while the rules were being written, scored with the proposed pack (findings +
positives + maturity sweep) and the proposed rubric.

```
                    scores        baseline   verdict
salesforce  RT      0 0 0 0 0        0       stable, exact match
craftbot    RT      0 0 0 0 0        0       stable, exact match
salesforce  KB      2 2 2 2 2        2       stable, exact match
craftbot    KB      1 1 1 1 1        1       stable, exact match
```

**20/20 identical, four for four against the frozen baseline.**

### The provenance rule generalised to two more artifact classes

The specific risk was inflation: the sweep hands the scorer 86–89 KB of "here
is what is good about this project," and both targets held at zero.

- **craftbot** — the sweep surfaced `skills/shannon`'s live pentester,
  `skills/differential-review/adversarial.md`, `skills/sharp-edges`, and a Kali
  MCP entry. All five scorers rejected the lot as shipped end-user capability
  aimed at the customer's systems, not craftbot testing itself. This is the
  exact artifact class that defeated the mechanical sweep in §3.
- **salesforce** — the scorers rejected its prompt-resident guardrail block as
  *"defensive content deployed into the customer's org… not the project
  attacking its own defences."* A subtler call than craftbot's, made
  consistently five times.

The rule now has four independent confirmations on three targets it was not
written from: hermes (a shipped jailbreak toolkit), craftbot (pentesting
skills), salesforce (a guardrail template).

### The tie-break rules resolve a real band edge

Salesforce is genuinely ambiguous — **every** scorer stated it was choosing
between 2 and 3, and rule 4 settled it identically five times. Craftbot's
scorers cited rule 3 (unmanaged dominant path caps at 1) by name. This is the
mechanism working as designed: the ambiguity is real and the rule makes it
deterministic, rather than leaving it to a per-run draw.

### The new signals earn their place

Craftbot's scorers independently identified **tool and MCP output** as the
dominant untrusted channel — the signal absent from the shipping knowledge base
— and surfaced that `PromptSanitizer` is 246 lines with zero call sites and
that `run_shell` hands `os.environ.copy()` to every command. Evidence the
current scan did not record.

**Running total: 80 of 80 replays identical within condition**, across four
categories and five targets, with the generalisation gate passed on cold ones.

**Next: Gate 2** — none of this has run inside a real scan.

---

## Round 5 — Gate 2: end-to-end scans (2026-08-11) — **FAIL**

Nine full Praxen scans (3 targets × 3) on the modified pipeline, Opus 5,
~2.3M tokens. First test of the change inside a real scan rather than an
isolated scoring step.

```
target      new runs           spread    v1.2 3x study       spread   criterion <=0.15
finbot      1.00 1.00 1.00      0.00     1.30 0.90 0.75       0.55    PASS
autogen     1.70 1.30 1.30      0.40     1.85 1.55 1.30       0.55    FAIL
hermes      3.00 2.60 2.30      0.70     2.30 2.60 2.70       0.40    FAIL (widened)
```

finbot's three runs produced **byte-identical category vectors** — `2 1 1 1 0 1`
three times, from a target whose prior spread was the joint-widest in the suite.

### Cause — the variance moved into the step I added

```
hermes run   maturity signals in the Step 8b record   weighted
  r1                      16                           3.00
  r2                       9                           2.60
  r3                       7                           2.30
```

Monotonic. **Step 8b is itself a free-exploration step**, so how much practice a
run happens to find varies, and the score tracks it. Fixing the scoring step's
dependence on a variable workspace read did not remove that dependence — it
relocated it one step upstream, into the new step.

The target pattern confirms the mechanism: the fix is perfect where there is
nothing for 8b to vary on (finbot, almost no practice → 0.00), degrades with a
little (autogen → 0.40), and is worse than the status quo with a lot (hermes →
0.70). That is exactly backwards, because maturity-rich targets are the ones
8b exists to serve.

### Disposition

**Not shipping**, per the kill criterion stated in the approved plan before the
result was known. 1.3 ships score-inert as originally scoped.

The SKILL/KB changes are committed at `3b6884f` and are **not reverted** — they
are correct in isolation, gate-tested, and cost nothing serialized. But they do
not deliver the outcome, so they are not a release claim.

### The identified next iteration, if anyone spends it

Step 8b needs the same treatment the scoring step got: a **bounded, enumerated
gathering task** — does a security-named test file exist, is there a CI
workflow, is there a finding→fix ledger, is log shipping configured — rather
than an open instruction to sweep for practice. Two runs answering a fixed list
gather the same evidence; two runs told to look for good things find different
amounts. Re-run the same three targets to test it; cost is roughly this round.

**Session totals: 80 bench replays + 9 full scans.** Three structural
interventions measured, two discarded on evidence, one diagnosed and stopped at
its gate.
