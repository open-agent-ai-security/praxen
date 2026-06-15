<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Installation

Praxen ships as a portable **agent skill**, packaged for both **Claude Code** and **OpenAI Codex**. Both platforms load the same `skills/behavior-verifier` engine and produce the same JSON / HTML / TXT report format — only the install/packaging differs. On the same inputs, findings should cover the same major themes, but exact counts, grouping, and RAISE maturity scores can vary by model and context (see [Understanding Run-to-Run Variability](understanding-variability.md)). Claude Code is the most common path; Codex is supported as a first-class agent-skills platform.

## Prerequisites

- **A coding agent** capable of tool use and multi-step instruction-following. Praxen is tested against [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) and [OpenAI Codex](https://developers.openai.com/codex/skills); other coding agents that can read a skill markdown file and call tools (Read, Grep, Glob, Bash, Write) should also work.
- **Python 3.9 or newer on the PATH.** Praxen's report renderer (`render.py`, bundled with the skill) is plain Python 3 — standard library only, nothing to `pip install`. 3.9 is the macOS Command Line Tools system Python (Ventura / Sonoma / Sequoia), so on macOS there's typically nothing to install. On Windows, `py -3` works. If `python3` isn't found, the renderer step falls back to `python`.
- **Network access for your coding agent's LLM provider** during analysis. Praxen itself does not phone home, but the LLM calls your coding agent makes during analysis follow whatever provider configuration the agent uses.
- **Workspace write permission for the agent.** Praxen writes its report files to a `./reports/` directory and runs two bundled Python scripts during a scan, so the agent must be allowed to write within the working directory (the default in Claude Code; on Codex, run with a workspace-write sandbox — see below).

That's the entire dependency surface.

## Option A — Claude Code (plugin marketplace)

The recommended path for Claude Code users. From your terminal:

```bash
claude plugin marketplace add open-agent-ai-security/praxen
claude plugin install praxen@open-agent-ai-security
claude plugin list      # confirm: praxen@open-agent-ai-security, enabled, v0.8.0+
```

The skill registers as `behavior-verifier`. The in-session equivalents — `/plugin marketplace add …`, `/plugin install …`, `/plugin list` — do exactly the same thing; if you install from within a Claude Code session, run `/reload-plugins` (or restart) to activate the skill. Prefer the terminal form when scripting: `claude plugin …` is argument-driven and runs the same way on every interface, whereas in-session slash commands occasionally fall through and get sent as ordinary chat messages.

## Option B — OpenAI Codex (agent skill)

Codex discovers skills from a `.agents/skills/` directory — both repo-local (in the working directory of the session) and user-wide (`~/.agents/skills/`). The current first-class Codex path is to **link the bundled skill** from a repo checkout or an unzipped release (Option C); a public Codex *marketplace* install (`codex plugin marketplace add …`, mirroring Option A) is [tracked as a future enhancement](https://github.com/open-agent-ai-security/praxen/issues/102), not yet available.

Pick the link scope that matches how you'll run Praxen:

```bash
# B1 — repo-local: this project's directory only
mkdir -p .agents/skills
ln -sf "$(pwd)/skills/behavior-verifier" .agents/skills/behavior-verifier

# B2 — user-wide: every Codex session, any directory
mkdir -p "$HOME/.agents/skills"
ln -sf "$(pwd)/skills/behavior-verifier" "$HOME/.agents/skills/behavior-verifier"
```

> **Working-directory scope — the common gotcha.** Codex walks **up** from the session's directory looking for `.agents/skills/`, so a repo-local link is visible from the repo root *and any subdirectory* — a scan directory nested inside the repo (e.g. `local/<target>_scan/`, as in the smoke test below) does find a repo-root link. What won't find it is a scan directory **outside the repo tree**, with no ancestor holding the link. For that out-of-tree shape, either link the skill into the **scan directory's** own `.agents/skills/`, or link it **user-wide** (B2).

Codex surfaces the skill as **`praxen:behavior-verifier`**. Invoke it by name and point it at a target:

```text
Use $praxen:behavior-verifier. Run a Praxen behavior analysis against ./target.
Use the Worker Remit at ./WORKER_REMIT.md. Write outputs to ./reports/.
```

**Permissions.** Praxen needs to create `./reports/` and run two bundled Python scripts, so Codex must allow workspace writes. With `codex exec`, pass a workspace-write sandbox:

```bash
codex exec --sandbox workspace-write -C /path/to/working-dir \
  'Use $praxen:behavior-verifier. Run a Praxen behavior analysis against ./target. Use the Worker Remit at ./WORKER_REMIT.md. Write outputs to ./reports/.'
```

In an interactive Codex session, approve workspace writes when prompted (or start the session with a workspace-write posture). No special approval is needed beyond that — Praxen's reads, the two Python scripts, and the `./reports/` writes all run under a workspace-write sandbox.

> **Scan directory outside a git repo?** `codex exec -C <dir>` refuses to run in a directory that isn't inside a trusted git repo (`Not inside a trusted directory and --skip-git-repo-check was not specified`). Either add `--skip-git-repo-check` to the command, or — preferred — use a trusted **repo-local** scan directory such as `local/<target>_scan/` (the `local/` convention this repo already gitignores) instead of `/tmp`.

> **Codex skill name.** Codex shows the skill to the model as `praxen:behavior-verifier` (plugin-qualified) — invoke it as `$praxen:behavior-verifier`, not `$behavior-verifier`.

> **Benign Codex loader warnings.** During skill discovery Codex may print warnings unrelated to Praxen — about *other* installed plugins, repeated plugin-asset icon-path (`..`) notices, or a telemetry metric-tag warning that the colon-qualified id `praxen:behavior-verifier` "contains invalid characters." None of these block discovery or execution; the skill still loads and runs. The telemetry metric-tag constraint is a Codex-side limitation on the plugin-qualified id, not a Praxen error.

## Option C — Run from an unzipped release (either agent)

If you can't or don't want to use a marketplace flow, unzip the release archive somewhere your coding agent can see it. There's no install step — the archive carries both the `.claude-plugin/` and `.codex-plugin/` manifests plus the shared `skills/` engine.

```bash
# Replace VERSION with the release tag and RELEASE_URL with the .zip asset URL
curl -L -o praxen-VERSION.zip RELEASE_URL
unzip praxen-VERSION.zip
cd praxen-VERSION
```

Then point your coding agent at `skills/behavior-verifier/SKILL.md` (Claude Code), or link it into `.agents/skills/` and invoke `$praxen:behavior-verifier` (Codex, per Option B). See [Usage](usage.md).

## Verifying the install

**Claude Code:**

```bash
claude plugin list
```

If `praxen@open-agent-ai-security` appears at `v0.8.0` or later with `enabled`, the marketplace install is working. From within a session the same plugin shows under `/plugin list`, and the skill is invocable as `behavior-verifier`.

**Codex:** confirm the skill appears to the model as `praxen:behavior-verifier` (e.g. it shows in Codex's skill list), then run a scoped scan and check that JSON / HTML / TXT land under `./reports/`. A copy-paste FinBot smoke test (one real single-target scan — enough to validate Codex skill loading):

```bash
PRAXEN_ROOT=/path/to/praxen          # your checkout or unzipped release
cd "$PRAXEN_ROOT"                     # so local/ lands under the repo (gitignored + trusted in a checkout)
mkdir -p local/finbot_scan/reports
cd local/finbot_scan

# the agent to scan = the REAL upstream source, never examples/
# (clone into ./finbot so the report slug — derived from the workspace dir name — is "finbot-…")
git clone https://github.com/OWASP-ASI/finbot-ctf-demo finbot

# the policy baseline = the FinBot remit. examples/ ships in the release zip; tests/ does not,
# so this line works from both a checkout and an unzipped release.
cp "$PRAXEN_ROOT/examples/finbot/WORKER_REMIT.md" ./WORKER_REMIT.md

codex exec --sandbox workspace-write -C "$(pwd)" \
  'Use $praxen:behavior-verifier. Run a Praxen behavior analysis against ./finbot. Use the Worker Remit at ./WORKER_REMIT.md. Write outputs to ./reports/.'
```

Expect four files under `reports/`: a `finbot-draft-*.md` checkpoint plus `finbot-findings-*.json`, `finbot-analysis-*.html`, and `finbot-analysis-*.txt`. (From an **unzipped release** rather than a git checkout, `local/` isn't inside a git repo — add `--skip-git-repo-check` to the `codex exec`, per the note in Option B. For a Codex *platform* check, one FinBot or HelperBot scan is enough; the full 12-target suite is the release gate for Praxen changes — see [tests/README.md](../tests/README.md).)

For a guided end-to-end first run that exercises the analysis pipeline — Worker Remit + agent source → HTML / JSON / TXT report — see [Quickstart](quickstart.md). It walks through scanning the FinBot agent (source cloned from upstream) against the bundled remit in about five minutes.

## Updating

**Claude Code (plugin marketplace):**

```bash
claude plugin marketplace update open-agent-ai-security
claude plugin update praxen@open-agent-ai-security
```

Restart Claude Code to apply. (In-session equivalents are the same commands as `/plugin …`.)

**OpenAI Codex / unzipped release:** pull the latest checkout or download the new release zip and replace it — a symlinked skill folder picks up the new version automatically. There is no migration step; Praxen is stateless across analyses.

## Uninstalling

**Claude Code (plugin marketplace):**

```bash
claude plugin uninstall praxen@open-agent-ai-security
claude plugin marketplace remove open-agent-ai-security
```

The marketplace is removed by its registered name (`open-agent-ai-security`, from `.claude-plugin/marketplace.json`) — which here matches the repo owner used to add it.

**OpenAI Codex:** remove the skill link — `rm .agents/skills/behavior-verifier` (or `rm ~/.agents/skills/behavior-verifier`).

**Unzipped release:** delete the directory. No system state is left behind.

## Next steps

- [Quickstart](quickstart.md) — first end-to-end report: scan the FinBot agent (source cloned from upstream) against the bundled remit
- [Writing Worker Remits](writing-remits.md) — authoring the policy document Praxen verifies against
- [Usage](usage.md) — the full running-an-analysis reference
