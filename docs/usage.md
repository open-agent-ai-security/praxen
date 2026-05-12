<!--
  Copyright © 2026 Exabeam, Inc. All Rights Reserved.
  Confidential and Proprietary. Do not distribute. Use by permission only.
-->

# Usage

Running a Praxa analysis takes two inputs: a **Worker Remit** (the agent's declared policy) and **evidence** (whatever the agent's code, deployment state, behavioral records, or development/governance docs can provide). Praxa produces three output files in `./reports/`.

This page covers the end-to-end run. For installing Praxa, see [Installation](installation.md). For authoring the Worker Remit, see [Writing Worker Remits](writing-remits.md).

---

## The two inputs

### Worker Remit

A markdown policy document describing what the agent is authorized to do — its mission, tools, channels, counterparties, forbidden actions, and approval requirements. One Worker Remit per agent. Save it as `WORKER_REMIT.md` (or `WORKER_REMIT_<agent>.md`) anywhere your coding agent can read it.

If you don't have one, your coding agent can help draft one before the analysis starts. See [Writing Worker Remits](writing-remits.md) for the authoring guide.

### Evidence

Praxa accepts four input shapes — used individually or in combination:

| Shape | What you point Praxa at |
|---|---|
| **Source repository** | A directory containing the agent's code, configs, skill files, dependencies, prompts. Most common for repo-based agents. |
| **Running deployment** | A directory containing live memory files (`MEMORY.md`, `SOUL.md`), operational logs (action reports, session JSONL, audit trails, escalation logs), and live config files. Pulled from a deployed instance of the agent — for example, point Praxa at an OpenClaw worker's `Workspace/` folder, which holds the `SOUL.md` and the other code and prompt artifacts that make up the agent's skillset, alongside its accumulated memory and logs. |
| **Behavioral artifacts** | A chat transcript, email history, decision record, or any conversation log that captures how the agent has actually behaved. |
| **Governance & methodology docs** | RAISE scores *maturity*, not just behavior — so development and operational practice documents count as evidence too. A red-team plan or its results, threat models, security review records, SDLC/runbook docs, incident retrospectives, dependency-management policy, monitoring/alerting design. These feed the maturity-oriented RAISE categories (**Build an AI Red Team**, **Monitor Continuously**, **Manage Your Supply Chain**) that source code alone can't speak to. |

You can provide more than one shape in the same analysis — for example, source code plus a recent action log plus the team's red-team report. Coverage and confidence increase with each additional input shape.

---

## Running an analysis

From a Claude Code session (or any coding agent capable of running the skill):

```
Please run the behavior-verifier skill to analyze [path to evidence]. Use the Worker Remit at [path to remit].
```

Praxa reads the evidence, evaluates it against the RAISE framework and the Worker Remit, and writes three files to `./reports/`:

| File | Purpose |
|---|---|
| `<agent-slug>-analysis-<timestamp>.html` | Self-contained human-readable report. Open in a browser; no server needed. |
| `<agent-slug>-findings-<date>.json` | Machine-readable findings. Use for automation, ticketing, dashboards, diffing across runs. |
| `<agent-slug>-analysis-<timestamp>.txt` | Plain-text summary suitable for terminal output, email body, or Slack message. |

The `.txt` summary is also printed to stdout during the analysis, so you can read it as the run completes.

---

## Where outputs land

By default, Praxa writes to `./reports/` relative to the directory you started the coding agent in. If the directory doesn't exist, Praxa creates it.

If you want outputs elsewhere, change directory before running, or instruct your coding agent to write to a specific path. The skill follows your instruction.

---

## Re-running after changes

Praxa is stateless across analyses. Each run is independent. To re-analyze after the agent changes — or after you tighten the Worker Remit — invoke the skill again:

```
Please re-run the behavior-verifier skill against the same workspace and remit.
```

A new pair of timestamped files is written. Prior reports are not overwritten — you can compare runs by diffing the `findings-<date>.json` files or by opening multiple HTML reports side by side.

---

## Results tuning

Praxa only scores what it can see. If you disagree with a finding — especially a RAISE category score that feels lower than reality — the usual cause is that the evidence you handed it didn't *show* a control that's actually in place: a review process, a deployment-time limit, an external guardrail, a monitoring pipeline, a red-team cadence. Praxa won't assume those exist; it scores absence of evidence as absence of control (see the calibration anchors — present-but-undocumented and present-but-defeated both land low).

The fix is to give it more evidence and re-run. Add whatever artifact demonstrates the control — in whatever (text) format you have it: a runbook, a CI config, a policy doc, a red-team report, a ticket history, an exported dashboard config, even a written description of the process — and ask Praxa to factor it in:

```
Here's our red-team report and the production alerting config. Please re-run the
behavior-verifier skill against the same workspace and remit, and factor these in.
```

Praxa will re-evaluate with the added context. This is the intended workflow: the first run tells you what the evidence supports; subsequent runs let you close the gap between *what's true* and *what's demonstrable*. If a score is still low after you've supplied the evidence, that gap is itself the finding — the control may be real but unverifiable to anyone who wasn't told, which is its own maturity problem.

For the fuller treatment — including when a finding means "fix the remit" or "fix the agent" rather than "add evidence", and how to record an accepted risk — see [Challenging and Revising Findings](challenging-findings.md).

---

## Automating analyses

Praxa does not include a scheduler. If you want recurring analyses, wrap the coding agent invocation in whatever scheduler your environment already uses:

- **CI hook** — run on every pull request that touches the agent's code.
- **Cron / launchd** — run nightly against a deployed agent's exported state.
- **GitHub Action** — run on a schedule and post the `.txt` summary as a comment.

Because Praxa is stateless and produces deterministic outputs (modulo timestamp), CI integration is straightforward. The JSON output is the right format for automated downstream consumers.

---

## Tips for large workspaces

Praxa's analysis is read-heavy on the workspace. Two practical tips for large targets:

1. **Scope the input.** Point Praxa at the agent's *core* directory (often `src/` or the agent code subtree), not the whole repository. Tests, build artifacts, and vendor directories are noise. The Worker Remit defines what's in scope; the input path should match.
2. **Watch for context-window pressure.** Very large workspaces (50+ artifacts, multi-megabyte configs) can stress the coding agent's context window mid-analysis. Praxa is designed to degrade gracefully — an interim scorecard is printed before the heavy output steps, and the final summary is also written to a `.txt` file so it survives session compression. If a large analysis truncates, the `.txt` and JSON outputs land regardless.

---

## Next steps

- [Writing Worker Remits](writing-remits.md) — the authoring guide for the policy document
- [Interpreting Reports](interpreting-reports.md) — how to read what Praxa produces
- [Challenging and Revising Findings](challenging-findings.md) — what to do when you disagree with the analysis
