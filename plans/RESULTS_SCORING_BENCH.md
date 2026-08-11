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
> ## Headline
>
> **Both candidate fixes failed. The variance source is target-dependent, and
> neither intervention is general.**
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
