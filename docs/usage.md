<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Usage

Running a Praxen analysis takes two inputs: a **Worker Remit** (the agent's declared policy) and **evidence** (whatever the agent's code, deployment state, behavioral records, or development/governance docs can provide). Praxen produces three output files in `./reports/`.

This page covers the end-to-end run. For installing Praxen, see [Installation](installation.md). For authoring the Worker Remit, see [Writing Worker Remits](writing-remits.md).

---

## The two inputs

### Worker Remit

A markdown policy document describing what the agent is authorized to do — its mission, tools, channels, counterparties, forbidden actions, and approval requirements. One Worker Remit per agent. Save it as `WORKER_REMIT.md` (or `WORKER_REMIT_<agent>.md`) anywhere your coding agent can read it.

If you don't have one, your coding agent can help draft one before the analysis starts. See [Writing Worker Remits](writing-remits.md) for the authoring guide.

### Evidence

Praxen accepts four input shapes — used individually or in combination:

| Shape | What you point Praxen at |
|---|---|
| **Source repository** | A directory containing the agent's code, configs, skill files, dependencies, prompts. Most common for repo-based agents. |
| **Running deployment** | A directory containing live memory files (`MEMORY.md`, `SOUL.md`), operational logs (action reports, session JSONL, audit trails, escalation logs), and live config files. Pulled from a deployed instance of the agent — typically an exported workspace directory that holds the agent's identity files, the code and prompt artifacts that make up its skillset, and its accumulated memory and logs. |
| **Behavioral artifacts** | A chat transcript, email history, decision record, or any conversation log that captures how the agent has actually behaved. |
| **Governance & methodology docs** | RAISE scores *maturity*, not just behavior — so development and operational practice documents count as evidence too. A red-team plan or its results, threat models, security review records, SDLC/runbook docs, incident retrospectives, dependency-management policy, monitoring/alerting design. These feed the maturity-oriented RAISE categories (**Build an AI Red Team**, **Monitor Continuously**, **Manage Your Supply Chain**) that source code alone can't speak to. |

You can provide more than one shape in the same analysis — for example, source code plus a recent action log plus the team's red-team report. Coverage and confidence increase with each additional input shape.

---

## Running an analysis

From a Claude Code session (or any coding agent capable of running the skill):

```
Please run the behavior-verifier skill to analyze [path to evidence]. Use the Worker Remit at [path to remit].
```

Praxen reads the evidence, evaluates it against the RAISE framework and the Worker Remit, and writes three files to `./reports/`:

| File | Purpose |
|---|---|
| `<agent-slug>-analysis-<timestamp>.html` | Self-contained human-readable report. Open in a browser; no server needed. |
| `<agent-slug>-findings-<date>.json` | Machine-readable findings. Use for automation, ticketing, dashboards, diffing across runs. |
| `<agent-slug>-analysis-<timestamp>.txt` | Plain-text summary suitable for terminal output, email body, or Slack message. |

The `.txt` summary is also printed to stdout during the analysis, so you can read it as the run completes.

---

## Where outputs land

By default, Praxen writes to `./reports/` relative to the directory you started the coding agent in. If the directory doesn't exist, Praxen creates it.

If you want outputs elsewhere, change directory before running, or instruct your coding agent to write to a specific path. The skill follows your instruction.

---

## Re-running after changes

Praxen is stateless across analyses. Each run is independent. To re-analyze after the agent changes — or after you tighten the Worker Remit — invoke the skill again:

```
Please re-run the behavior-verifier skill against the same workspace and remit.
```

A new pair of timestamped files is written. Prior reports are not overwritten — you can compare runs by diffing the `findings-<date>.json` files or by opening multiple HTML reports side by side.

---

## Results tuning

Praxen only scores what it can see. If you disagree with a finding — especially a RAISE category score that feels lower than reality — the usual cause is that the evidence you handed it didn't *show* a control that's actually in place: a review process, a deployment-time limit, an external guardrail, a monitoring pipeline, a red-team cadence. Praxen won't assume those exist; it scores absence of evidence as absence of control (see the calibration anchors — present-but-undocumented and present-but-defeated both land low).

The fix is to give it more evidence and re-run. Add whatever artifact demonstrates the control — a runbook, a CI config, a policy doc, a red-team report, a ticket history, an exported dashboard config, even a written description of the process — and ask Praxen to factor it in:

```
Here's our red-team report and the production alerting config. Please re-run the
behavior-verifier skill against the same workspace and remit, and factor these in.
```

Text artifacts are the most reliable channel and the only thing Praxen's automatic workspace sweep looks for. Image evidence (a screenshot of a dashboard or an alerting rule) works too **if your coding agent's `Read` tool is multimodal — Claude Code's is** — but the sweep won't go hunting for image files, so name the file explicitly when you ask for the re-run ("…and factor in `alerting-dashboard.png`"). If you're unsure, a written description of what the screenshot shows is always safe.

Praxen will re-evaluate with the added context. This is the intended workflow: the first run tells you what the evidence supports; subsequent runs let you close the gap between *what's true* and *what's demonstrable*. If a score is still low after you've supplied the evidence, that gap is itself the finding — the control may be real but unverifiable to anyone who wasn't told, which is its own maturity problem.

For the fuller treatment — including when a finding means "fix the remit" or "fix the agent" rather than "add evidence", and how to record an accepted risk — see [Challenging and Revising Findings](challenging-findings.md).

---

## Automating analyses

Praxen does not include a scheduler. If you want recurring analyses, wrap the coding agent invocation in whatever scheduler your environment already uses:

- **CI hook** — run on every pull request that touches the agent's code.
- **Cron / launchd** — run nightly against a deployed agent's exported state.
- **GitHub Action** — run on a schedule and post the `.txt` summary as a comment.

Because Praxen is stateless and produces deterministic outputs (modulo timestamp), CI integration is straightforward. The JSON output is the right format for automated downstream consumers.

---

## Large workspaces and context sizing

A Praxen analysis is read-heavy: it loads the skill procedure, the knowledge bases, and every artifact in the workspace, holds the findings in working memory, and writes the report in a single synthesis pass. On a large target this can exceed the coding agent's context window, and the session **auto-compacts mid-analysis**. That failure is silent — you still get a report, but findings gathered early in the run can be lost or over-summarized by the compaction before the report is written. The goal is to keep the whole scan inside one context window.

**To keep a scan inside the window:**

1. **Use the largest context window available.** This is the biggest lever. In Claude Code, run the analysis in the largest-context session you have access to — a 1M-context (Opus) session if you have one. A 200k-class window can compact partway through a non-trivial agent scan once the procedure, knowledge bases, file reads, and synthesis are all resident at once.
2. **Start a fresh session for the scan.** Don't run Praxen at the tail of a long conversation that has already consumed most of the window — give the analysis the full budget.
3. **Scope the input to the agent, not the whole repo.** Point Praxen at the agent's core surface — its prompts, skill files, code, config, and the Worker Remit — and leave out what isn't the agent: `node_modules` and vendored dependencies, `.git`, `dist` / `build` output, large data and log files, test fixtures. The Worker Remit defines what's in scope; the input path should match. (Praxen already samples large logs and lockfiles rather than reading them whole — but the cleanest fix is to not hand it the bulk in the first place.)

**If a run compacts anyway:** Praxen checkpoints itself. Just before it writes the report, it saves a **draft manifest** to `./reports/<agent-slug>-draft-<timestamp>.md` — a complete record of the analysis (every finding, the RAISE scores, the remit audit). So if you see the auto-compaction notice during a run, or the final report looks thinner than the interim overview Praxen prints to stdout, you have two recovery options:

- **Recover from the manifest.** Tell the agent: *"the session compacted — read `./reports/<agent-slug>-draft-<timestamp>.md` and finish the report from it."* It rebuilds the findings JSON and re-renders from the checkpoint, without re-analyzing the workspace.
- **Re-run** the analysis with a tighter scope or a larger context window.

A report produced *through* a mid-synthesis compaction should be treated as possibly incomplete until you've done one of those — not authoritative.

This is guidance, not a guarantee — a genuinely large workspace can still compact even when scoped well. Scoping tighter and giving the run a fresh, large context window is the most reliable thing you can do today; the draft manifest is the safety net for when it compacts regardless.

---

## Next steps

- [Writing Worker Remits](writing-remits.md) — the authoring guide for the policy document
- [Interpreting Reports](interpreting-reports.md) — how to read what Praxen produces
- [Challenging and Revising Findings](challenging-findings.md) — what to do when you disagree with the analysis
