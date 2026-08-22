<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Threat Modeling

Praxen can produce a **threat model** of an analyzed agent: a visual
architecture view — components in five trust lanes, data flows, trust
boundaries, threat enumeration, and attack paths — where **every element
cites file:line evidence** from the agent's own workspace. It is derived
from what the code actually does, not drawn by a human or prompted from a
description of the system: a threat model with receipts.

> **📊 See it live:** every target in Praxen's public baseline suite ships a
> hosted threat model — browse [OpenHands](https://open-agent-ai-security.github.io/praxen/tests/baselines/v1.3-opus5/openhands/openhands-threatmodel-2026-08-21-143615.html),
> [Hermes desktop agent](https://open-agent-ai-security.github.io/praxen/tests/baselines/v1.3-opus5/hermes-agent-desktop/hermes-agent-desktop-threatmodel-2026-08-21-143615.html),
> or [FinBot](https://open-agent-ai-security.github.io/praxen/tests/baselines/v1.3-opus5/finbot/finbot-threatmodel-2026-08-21-143615.html), or any target from
> the [suite health page](https://open-agent-ai-security.github.io/praxen/tests/baselines/suite-health-report.html).

## Running one

Ask for it in natural language, the same way you invoke an analysis:

- *"Run a Praxen threat model"* — builds the model from the most recent
  analysis in `./reports/` (or name a findings JSON explicitly).
- *"Run a Praxen analysis with a threat model"* — runs the full analysis
  first, then the model against its results.

In our testing, a threat model costs roughly **0.5–1× the tokens of a
standard scan, typically ~0.75×** — one fresh-context extraction pass,
usually 10–20 minutes solo, stretching under concurrent runs — and never changes
the analysis: no finding, score, or report is touched. It works best *after*
an analysis (that is what makes `confirmed` statuses possible); running one
without an analysis is supported but the model can only report what it
verifies directly.

Outputs land beside the analysis artifacts:
`reports/<agent>-threatmodel-<timestamp>.json` (the graph, conforming to the
published contract) and `.html` (the report — self-contained, printable, and
styled like the analysis report).

## Reading the report

The diagram places every component in one of five lanes — **User / Inputs →
Client / Adapters → Agent Core → Tools / MCP → External / Deploy** — with an
icon carrying the component's kind (a tool looks like a tool) and color
carrying its family. Dashed vertical lines are **trust boundaries**, keyed by
`B1…Bn` badges to the boundary table below the diagram. Components on an
**attack path** carry a corner badge showing their role — purple where
untrusted content enters, amber for a control the path bypasses, red where
the damage lands — and the path itself is drawn in bold red; the Attack
Paths section below the diagram lists each path's steps in order. Everything the hover
interactions show — evidence citations, flow labels, boundary detail — is
also on the page statically: the legend, the boundary key, and the component
inventory make the report complete on paper.

Every threat at a boundary carries one of four statuses:

| status | meaning |
|---|---|
| **confirmed** | An analysis finding proves it — the finding ID is cited |
| **potential** | An unanswered hypothesis: no covering finding, and the sweep for a mitigating control found none |
| **partial** | A control demonstrably answers part of the threat (cited), and the uncovered remainder is stated |
| **mitigated** | A control demonstrably answers the whole threat (cited) |

`confirmed` (red) is the strongest signal — it is verified. `potential`
(blue, deliberately off the red/gold/green assessment scale) is where the
threat model adds the most beyond the analysis: plausible exposure on
surfaces nothing currently answers. Boundaries with **no attached remit
rules are normal** — a Worker Remit is a job description, not a security
model, and threats at such boundaries are assessed against the RAISE/OWASP
calibration alone.

## How it relates to the analysis

The analysis works bottom-up from evidence: read the code, find concrete
defects. The threat model works top-down from architecture: enumerate what
could go wrong at each trust crossing, then check each hypothesis against
the findings and the code. Where the two meet, a threat is `confirmed`;
where the top-down view finds surface the bottom-up pass never examined,
threats surface as `potential` — which is precisely the review list a
follow-up analysis should start from.

In our testing, independent extractions of the same target converged on
the same trust-boundary set and threat statuses, with variation confined
to enumeration depth and naming at the margins. Threat modeling follows the same rule as
everything else in Praxen: one run produces one artifact — multi-run
comparison is a diagnostic, not a deliverable.
