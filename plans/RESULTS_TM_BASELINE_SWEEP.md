<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Results — 12-target baseline threat-model sweep (2026-08-21)

One contract-v1.4 extraction per baseline target via the shipped
`THREAT_MODEL.md` brief verbatim: fresh-context Opus 5 subagents
(model_identity verified in every graph), frozen `v1.3-freeze` sources,
the target's baseline findings JSON + remit as inputs, freeze-run
scan-instructions scope applied where one existed. Run stamp
`2026-08-21-143615`; artifacts committed under
`tests/baselines/v1.3-opus5/<slug>/`. **All 12 graphs were first-pass
valid — zero repair rounds — and every cited finding_id resolved.**
Ambiguities the runs reported are consolidated in
`CONTRACT_V15_AMBIGUITY_HARVEST.md`.

## Cost measurements

Tokens are harness-reported subagent totals; wall-clock is the
subagent's run duration. The sweep ran 4–8 extractions concurrently, so
the longest clocks (openhands, salesforce) include concurrency stretch —
the same effect the thinking-modes cost guidance documents.

| target | tokens | ×260k scan | wall-clock |
|---|---|---|---|
| openai-customer-service | 127,858 | 0.49 | 9.9 min |
| helperbot | 138,157 | 0.53 | 10.9 min |
| finbot | 187,112 | 0.72 | 18.1 min |
| autogen-code-executor | 196,982 | 0.76 | 15.7 min |
| deepagents-cli | 198,936 | 0.77 | 16.3 min |
| hermes-agent-desktop | 201,714 | 0.78 | 15.9 min |
| uagents | 204,351 | 0.79 | 16.2 min |
| salesforce-help-agent-accelerator | 210,423 | 0.81 | 46.6 min† |
| aider | 225,271 | 0.87 | 17.3 min |
| openhands | 228,089 | 0.88 | 32.6 min† |
| craftbot | 230,726 | 0.89 | 18.6 min |
| yaah | 250,724 | 0.96 | 16.0 min |
| **mean** | **~200k** | **0.77** | — |

† concurrency-stretched (ran alongside 4–7 other extractions).

Denominator: the ~260k-token standard scan implied by the gate record's
own ratios (`tests/runs/v2.0.0-threatmodel-gate/GATE.md`: 145–220k ≈
0.55–0.85×). Accounting caveat: gate tokens were the gate's own
measurements, sweep tokens are harness-reported subagent totals — the
two paths are close but not proven identical, which is one reason the
published range is stated wide.

## The published number (Steve-approved wording, 2026-08-21)

Combined evidence — 8 gate extractions (145–220k, mean ~184k) + 12
sweep extractions (128–251k, mean ~200k) = 20 measured product-brief
extractions:

> in our testing, roughly **0.5–1× the tokens of a standard scan,
> typically ~0.75×**

with duration framed separately (one fresh-context pass, ~10–20 minutes
solo; wall-clock stretches under concurrency). This supersedes the
probe-era 0.4–0.5× (smaller targets, thinner brief) wherever it
appears; the gate's 0.55–0.85× remains correct for its own 8-run
record.
