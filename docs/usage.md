<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Usage

Running a Praxen analysis takes two inputs: a **Worker Remit** (the agent's declared policy) and **evidence** (whatever the agent's code, deployment state, behavioral records, or development/governance docs can provide). Praxen produces three output files in `./reports/`.

**Praxen is a read-only observer.** It reads the artifacts you point it at and writes a report to `./reports/` — it never changes the agent it's analyzing or sits in its control path.

This page covers the end-to-end run. For installing Praxen, see [Installation](installation.md). For authoring the Worker Remit, see [Writing Worker Remits](writing-remits.md). For the verification model Praxen implements, see [Agent Behavior Verification](abv.md).

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

## Running an analysis

From inside your coding-agent session — Claude Code, Codex, or any agent that can run the skill — it's the same plain-English instruction:

```
Please run the behavior-verifier skill to analyze [path to evidence]. Use the Worker Remit at [path to remit].
```

### Invoking by evidence type

Concrete prompts you can copy and adapt — pick the shape that matches what you have, or combine.

**Source repository.**

```
Please run the behavior-verifier skill against ./my-agent-repo/.
Use the Worker Remit at ./WORKER_REMIT.md.
```

**Running deployment (exported workspace — memory files, action logs, live config).**

```
Please run the behavior-verifier skill against ./agent-workspace/.
Use the Worker Remit at ./WORKER_REMIT.md.
```

**Behavioral artifacts (chat transcript / email history / decision log).**

```
Please run the behavior-verifier skill against ./agent-session-2026-05-23.jsonl
(this is a chat transcript, not source code). Use the Worker Remit at
./WORKER_REMIT.md.
```

**Mixed evidence (the strongest case — combine multiple inputs in one run).**

```
Please run the behavior-verifier skill against ./my-agent-repo/ plus the
red-team report at ./redteam-q1.md and the session log at ./logs/session.jsonl.
Use the Worker Remit at ./WORKER_REMIT.md.
```

Coverage and confidence increase with each additional input shape — see the [Evidence](#evidence) table above for what each contributes.

### For highest scan fidelity: run in a fresh context

If the scan runs in a session that already explored the workspace (while authoring the remit or reading code), it tends to **skim** — recognizing what it's already seen instead of reading the workspace cold. A fresh, cold-context scan reads materially more, which can raise the RAISE scores. So for the most thorough result, give it a clean slate.

**The recommended approach for a high-confidence scan:** run it in a subagent or a fresh session that carries no prior context, and point it at the workspace:

```
Please spawn a subagent with no prior context to run the behavior-verifier skill
against ./my-agent-repo/. Worker Remit is at ./WORKER_REMIT.md. Output to
./reports/.
```

This is also the right pattern when the scan follows a remit-authoring session — if Praxen drafted the remit and then immediately scans, the same context holds everything it just read, and the artifact sweep will be shallow. Finish the remit, confirm it, then start a fresh scan session.

Praxen reads the evidence, evaluates it against the RAISE Framework and the Worker Remit, and writes three files to `./reports/`:

| File | Purpose |
|---|---|
| `<agent-slug>-analysis-<timestamp>.html` | Self-contained human-readable report. Open in a browser; no server needed. |
| `<agent-slug>-findings-<date>.json` | Machine-readable findings. Use for automation, ticketing, dashboards, diffing across runs. |
| `<agent-slug>-analysis-<timestamp>.txt` | Plain-text summary suitable for terminal output, email body, or Slack message. |

The findings JSON is keyed by **date** (`<YYYY-MM-DD>` — one per agent per day); the HTML and TXT carry a full **per-run timestamp** (`<YYYY-MM-DD-HHMMSS>`), so re-running the same day keeps each report distinct. Praxen also writes a working `<agent-slug>-draft-<timestamp>.md` checkpoint during the run — a recovery artifact, not a deliverable, and safe to delete.

The `.txt` summary is also printed to stdout during the analysis, so you can read it as the run completes.

## Where outputs land

By default, Praxen writes to `./reports/` relative to the directory you started the coding agent in. If the directory doesn't exist, Praxen creates it.

If you want outputs elsewhere, change directory before running, or instruct your coding agent to write to a specific path. The skill follows your instruction.

## Re-running after changes

Praxen is stateless across analyses. Each run is independent. To re-analyze after the agent changes — or after you tighten the Worker Remit — invoke the skill again:

```
Please re-run the behavior-verifier skill against the same workspace and remit.
```

Each run writes a fresh timestamped HTML and TXT, so prior reports stay on disk side by side. (The findings JSON is keyed by date — one per agent per day — so a second run on the *same day* replaces it: diff the JSON across days, or compare the timestamped HTML within a day.)

## Results tuning

Praxen only scores what it can see. If a finding — or a RAISE category score — feels lower than reality, the usual cause is simple: the evidence you handed it didn't *show* a control that's actually in place (a review process, a deployment-time limit, an external guardrail, a monitoring pipeline, a red-team cadence).

The fix is to show it — add whatever artifact demonstrates the control (a runbook, a CI config, a policy doc, a red-team report, a ticket history, an exported dashboard config, even a written description of the process) and ask Praxen to factor it in:

```
Here's our red-team report and the production alerting config. Please re-run the
behavior-verifier skill against the same workspace and remit, and factor these in.
```

Text artifacts are the most reliable channel and the only thing Praxen's automatic workspace sweep looks for. Image evidence (a screenshot of a dashboard or an alerting rule) works too **if your coding agent's `Read` tool is multimodal — Claude Code's is** — but the sweep won't go hunting for image files, so name the file explicitly when you ask for the re-run ("…and factor in `alerting-dashboard.png`"). If you're unsure, a written description of what the screenshot shows is always safe.

Praxen will re-evaluate with the added context. This is the intended workflow: the first run tells you what the evidence supports; subsequent runs let you close the gap between *what's true* and *what's demonstrable*. If a score is still low after you've supplied the evidence, that gap is itself the finding — the control may be real but unverifiable to anyone who wasn't told, which is its own maturity problem.

For the fuller treatment — including when a finding means "fix the remit" or "fix the agent" rather than "add evidence", and how to record an accepted risk — see [Challenging and Revising Findings](challenging-findings.md).

## Automating analyses

Praxen does not include a scheduler. If you want recurring analyses, wrap the coding agent invocation in whatever scheduler your environment already uses:

- **CI hook** — run on every pull request that touches the agent's code.
- **Cron / launchd** — run nightly against a deployed agent's exported state.
- **GitHub Action** — run on a schedule and post the `.txt` summary as a comment.

Because Praxen is stateless and emits machine-readable JSON, CI integration is straightforward. The JSON output is the right format for automated downstream consumers.

## Large workspaces and context sizing

A big scan reads a lot — the skill procedure, the knowledge bases, every artifact in the workspace, plus the findings it builds up. On a very large target this can exceed your agent's context window, and the session **auto-compacts mid-run**, thinning the findings before the report is written. That's recoverable (below), but cleaner to avoid:

1. **Give the scan room.** Run it in the largest-context session you have, and start it **fresh** — don't run Praxen at the tail of a long conversation that's already used up the window. (A fresh session also scans better: an agent that already explored the code tends to skim it the second time — see [For highest scan fidelity](#for-highest-scan-fidelity-run-in-a-fresh-context) above.)
2. **Scope to the agent, not the whole repo.** Point Praxen at the agent's own surface — prompts, skill files, code, config, and the Worker Remit — and leave out `node_modules`, vendored dependencies, `.git`, build output, and large data/log files. The Worker Remit defines what's in scope; the input path should match.

**If a run compacts anyway, you don't lose the work.** Just before rendering, Praxen saves a **draft manifest** to `./reports/<agent-slug>-draft-<timestamp>.md` — the complete analysis (every finding, the RAISE scores, the remit audit). Tell the agent *"the session compacted — read the draft manifest and finish the report from it,"* and it rebuilds the report from the checkpoint without re-scanning. (Or just re-run with a tighter scope.)

## Troubleshooting

A short list of first-run snags and how to clear them.

### "behavior-verifier skill not found" / the agent doesn't recognise the skill

The plugin is installed but the current session hasn't picked it up.

- From within Claude Code: run `/reload-plugins`, or restart Claude Code.
- From the terminal: `claude plugin list` should show `praxen@open-agent-ai-security`, `enabled`. If it doesn't, re-run the install (`claude plugin install praxen@open-agent-ai-security`); if it does and the in-session agent still can't find it, you're in a stale session — start a new one.
- Using an unzipped release directly (no marketplace): point the agent at `skills/behavior-verifier/SKILL.md` explicitly rather than naming the skill.

### `render.py` errored at the end of the run

The LLM wrote a `findings.json` that didn't pass schema validation, so the deterministic render step refused to produce an HTML report. The error message names the offending JSON path (e.g. `$.findings[3].evidence: expected array, got string`).

This is usually a context-pressure symptom — the analysis was synthesised under stress and the JSON came out malformed. Options:

- **Re-run** in a larger context window or with a tighter input scope. See *Large workspaces and context sizing* above.
- **Recover from the draft manifest** if Praxen wrote one (`./reports/<agent-slug>-draft-<timestamp>.md` — written just before the findings JSON). Tell the agent: *"the findings JSON failed validation — read the draft manifest and rebuild from it."*

If the same JSON-shape error reproduces on a fresh run with plenty of context, that's a Praxen bug — please [file it](https://github.com/open-agent-ai-security/praxen/issues/new/choose) with the schema error and the agent slug.

### "Worker Remit not found" / "no remit at that path"

The skill couldn't find the path you named. Most common causes:

- **Relative paths are relative to where the coding agent is running**, not to your terminal. From a Claude Code session, you can check with a quick `pwd` before the analysis.
- **A typo in the filename** — Praxen looks for the exact path you provide; it does not search.
- **The agent's working directory isn't where you think it is** — re-`cd` and start fresh, or pass an absolute path.

### Mid-analysis context auto-compaction (easy to miss)

A long scan can exceed the context window and **auto-compact mid-run** — the run still finishes, but findings gathered early can get summarised away before the report is written. It isn't loudly flagged, so it's easy to miss — but there are clear signs:

- The interim overview Praxen prints to stdout names findings the final HTML doesn't include.
- The HTML report looks suspiciously thin compared to the workspace's complexity.
- The agent suddenly switches to ad-hoc Python to "fix up" the JSON near the end of the run.

→ Prevention and recovery (a larger window, tighter scope, and the draft-manifest safety net) are covered in [Large workspaces and context sizing](#large-workspaces-and-context-sizing) above.

### Scan stopped emitting output for several minutes (streaming hiccup)

Praxen scans ran 3–10 minutes of wallclock across our test suite; larger codebases scoped to a subdirectory sit at the high end. Your mileage will vary — target size and scope, model tier, and provider capacity at the time all move the number. If a scan goes quiet for ~5 minutes with no progress messages or tool activity, you've likely hit a streaming hiccup — usually during the long-form drafting of the findings JSON. Symptoms:

- The agent emitted an analysis plan and started drafting findings, then went silent mid-document.
- No new files appear in the output directory; any partial JSON on disk is still valid but incomplete.
- The CLI shows the agent as still running but with no recent tool calls.

What to do: cancel the run and re-invoke against the same target. The skill writes its report incrementally, so the skeleton and early findings are already persisted on disk — you won't lose the analysis the agent built up, and a fresh invocation can resume cleanly. Most retries succeed on the first try.

### Scores look lower than reality

The most common operator surprise — *"my agent is more careful than this report suggests."* In nearly every case, the evidence you handed Praxen didn't *show* a control that's actually in place. See [Results tuning](#results-tuning) above for the additive-evidence workflow.

## Next steps

- [Writing Worker Remits](writing-remits.md) — the authoring guide for the policy document
- [Interpreting Reports](interpreting-reports.md) — how to read what Praxen produces
- [Challenging and Revising Findings](challenging-findings.md) — what to do when you disagree with the analysis
