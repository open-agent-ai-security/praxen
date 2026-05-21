<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Challenging and Revising Findings

Praxen is an LLM-driven analyzer working from the evidence you provide. It will sometimes produce findings that are wrong, miscalibrated, or inapplicable to your context. This page describes what to do when that happens — and how to tell whether the problem is the analysis, the remit, or the agent.

---

## When findings can be wrong

There are four kinds of wrong:

1. **The analysis missed context.** Praxen only sees the evidence you point it at. If the input doesn't include a security control that exists elsewhere — in a sibling repository, a runtime configuration injected at deploy time, a sidecar proxy — Praxen will report the gap honestly. The finding is technically correct given the input but not a real risk.

2. **The remit is vague.** A Praxen finding labeled "Vague Policy" means the rule isn't specific enough to verify. The fix is to tighten the rule, not to dispute the finding. See [Writing Worker Remits](writing-remits.md).

3. **The reasoning is incorrect.** Less common, but real. The LLM occasionally misreads code, conflates two similar patterns, or escalates a Medium-severity issue to High based on a chain that doesn't actually exist. These are bugs in the specific analysis, not in Praxen as a whole.

4. **You accept the risk.** The finding is correct, the rule is specific, the implementation gap is real — but you've decided the risk is acceptable for this agent in this deployment. That's a legitimate operator decision; it doesn't make the finding wrong.

Each of these has a different remediation path.

---

## Path 1 — The analysis missed context

If the finding is correct given the evidence Praxen saw but wrong because Praxen didn't see something it should have:

- **Add the missing evidence to the next analysis.** Point Praxen at the additional directory, log file, or transcript that contains the missing control. Re-run.
- **Don't loosen the remit just to silence the finding.** A finding that disappears because the remit was weakened is now a real gap that won't be caught next time.
- **Document the dependency.** If the missing control lives outside the agent's repository (a sidecar, an upstream gateway, a platform-enforced policy), record this in the remit's *Trusted Services / Integrations* section and explicitly note that the control is enforced externally. Praxen can then mark the rule as `Enforcement Not Possible` (in code) rather than as a Gap.

---

## Path 2 — The remit is vague

If a rule shows up as **Vague Policy** in the Remit Coverage section, or if findings on that rule have low severity-confidence calibration:

- **Rewrite the rule** to make it verifiable. See [Writing Worker Remits](writing-remits.md) for the specificity test.
- **Bump the remit version and date** in the Identity section so the change is tracked.
- **Re-run Praxen.** The new analysis will use the new rule.

A common pattern: an early-draft remit produces ten Vague Policy entries. After three iterations of tightening, the count drops to one or two — and the genuine implementation gaps become much sharper.

---

## Path 3 — The reasoning is incorrect

If the finding misreads the code, miscategorizes the issue, or asserts a chain that doesn't actually exist:

1. **Verify the cited evidence.** Open the file at the line numbers cited in the finding. If the code Praxen describes doesn't match what's actually there, the finding is wrong.

2. **Re-run the analysis.** LLM analyses are not perfectly deterministic. A second run with the same inputs will sometimes produce a corrected finding (or a different incorrect finding — both happen).

3. **Tighten the input.** If the evidence directory contains noise (test fixtures with deliberate vulnerabilities, archived old code, vendored dependencies), exclude it. Praxen will reason more sharply over a focused workspace.

4. **If the issue persists across runs**, the analysis methodology may have a calibration bug. File it through whatever channel the project's release notes name. Include the finding ID, the cited evidence, what's actually in the code, and what you believe the correct severity (or absence of finding) should be.

Do not edit the JSON or HTML output to "correct" the finding — those are the analysis artifacts and downstream consumers depend on them being unedited.

---

## Path 4 — You accept the risk

If the finding is correct but you've decided the risk is acceptable:

- **Record the acceptance outside the Praxen JSON.** The findings schema is closed by design — `additionalProperties: false`, validated by `schema.py` — so adding fields to a committed findings file would fail the next time anything re-validates it. Track risk acceptances in the consumer of choice: a sidecar `<agent>-risk-acceptances.md`, your ticketing system (Jira / Linear / GitHub issues with the `PRAX-…` finding ID in the title), or your governance / compliance register. Record who accepted, when, and why.
- **Update the Worker Remit** if the acceptance is permanent. For example, if you've decided that "no rate limiting" is acceptable for an internal-only deployment, the remit should reflect that scope (a public deployment of the same agent would need rate limiting, and a remit for that deployment would say so).
- **Record the decision in your change log.** Risk acceptances accumulate over time and become invisible if not tracked. The remit + change log together should explain *why* the agent looks the way it does.

---

## When findings improve over time

Praxen is calibrated to highlight real risk; the methodology continues to evolve. Across releases you may see:

- **Severity shifts** — what was a High in one release may be a Critical in a later release if the methodology determines the path is more directly exploitable. This is intentional sharpening, not an error in the prior release.
- **New finding categories** — Praxen adds named detectors as new attack patterns become well-understood. A previously-passed agent may surface a new finding when re-analyzed.
- **Calibration of the RAISE rubric** — the rubric itself is described in [`docs/RAISE.md`](RAISE.md). Updates to the rubric are noted in the project changelog and surface as score deltas across re-runs.

A regression in a re-run analysis (new findings appearing, scores moving) is not necessarily a regression in the agent. Compare against the changelog before assuming the agent got worse.

---

## What Praxen will not do

- **Argue with the operator.** Praxen reports what the evidence shows. If you disagree, the channels for disagreement are the remit and the input — not the report.
- **Self-correct mid-analysis.** Each run is independent. If you want a corrected analysis, fix the input or the remit and re-run.
- **Hide findings.** Even findings that are likely false positives are surfaced, with appropriate confidence. Suppression happens at the consumer (your ticketing pipeline, your risk register), not in Praxen itself.

---

## Next steps

- [Writing Worker Remits](writing-remits.md) — for "Vague Policy" findings
- [Interpreting Reports](interpreting-reports.md) — for understanding severities and confidence
- [The RAISE Framework](RAISE.md) — for understanding maturity-score deltas across runs
