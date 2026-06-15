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

Codex discovers skills from a `.agents/skills/` directory. The first-class path is a **user-wide skill link** — set it up once and every Codex session can invoke Praxen, from any directory:

```bash
cd /path/to/praxen          # your checkout or unzipped release (Option C)
mkdir -p "$HOME/.agents/skills"
ln -sfn "$PWD/skills/behavior-verifier" "$HOME/.agents/skills/behavior-verifier"
```

Codex surfaces the skill as **`praxen:behavior-verifier`**. Invoke it by name and point it at a target. Praxen needs workspace writes (it creates `./reports/` and runs two bundled Python scripts), so run `codex exec` with a workspace-write sandbox:

```bash
codex exec --sandbox workspace-write -C /path/to/scan-dir \
  'Use $praxen:behavior-verifier. Run a Praxen behavior analysis against ./target. Use the Worker Remit at ./WORKER_REMIT.md. Write outputs to ./reports/.'
```

That's the whole happy path. For an end-to-end first run, see [Quickstart](quickstart.md). A public Codex *marketplace* install mirroring Option A is [tracked as a future enhancement](https://github.com/open-agent-ai-security/praxen/issues/102), not yet available.

### Codex — discovery, sandbox & trusted-directory details

You can skip this on a first read; the user-wide link above is all most setups need.

- **Repo-local link (project-only alternative).** To scope the skill to one project instead of user-wide, link it inside that repo: `mkdir -p .agents/skills && ln -sfn "$PWD/skills/behavior-verifier" .agents/skills/behavior-verifier`. Codex walks **up** from the session's directory to find `.agents/skills/`, so a repo-root link is visible from the repo root and any subdirectory (including a nested `local/<target>_scan/`). A scan directory **outside the repo tree** won't see it — which is exactly the case the user-wide link avoids.
- **Workspace-write sandbox.** In an interactive session, approve workspace writes when prompted (or start with a workspace-write posture). Praxen's reads, the two Python scripts, and the `./reports/` writes all run under that one sandbox — no other approval needed.
- **Trusted-directory check.** `codex exec -C <dir>` refuses to run in a directory that isn't inside a trusted git repo (`Not inside a trusted directory and --skip-git-repo-check was not specified`). Run from a scan directory inside a git checkout, or add `--skip-git-repo-check` (the unzipped-release smoke test below does exactly this).
- **Skill name.** Codex shows the skill as the plugin-qualified `praxen:behavior-verifier` — invoke it as `$praxen:behavior-verifier`, not `$behavior-verifier`.
- **Benign loader warnings.** During discovery Codex may print warnings unrelated to Praxen — about *other* installed plugins, plugin-asset icon-path (`..`) notices, or a telemetry metric-tag warning that the colon-qualified id "contains invalid characters." None block discovery or execution; the skill still loads and runs. The telemetry constraint is a Codex-side limit on the plugin-qualified id, not a Praxen error.

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

**Codex:** confirm the skill appears to the model as `praxen:behavior-verifier` in Codex's skill list. That's the parity check — it confirms discovery, the same way `claude plugin list` does for Claude Code.

For the first **end-to-end run** on either platform — Worker Remit + agent source → HTML / JSON / TXT report — see [Quickstart](quickstart.md). It walks through scanning the FinBot agent (source cloned from upstream) against the bundled remit in about five minutes, with the exact Claude Code and Codex commands.

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
