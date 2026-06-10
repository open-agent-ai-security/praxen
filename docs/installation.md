<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Installation

Praxen ships as a portable **agent skill**, packaged for both **Claude Code** and **OpenAI Codex**. Both platforms load the same `skills/behavior-verifier` engine and produce identical analyses — only the install/packaging differs. Claude Code is the most common path; Codex is supported as a first-class agent-skills platform.

---

## Prerequisites

- **A coding agent** capable of tool use and multi-step instruction-following. Praxen is tested against [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) and [OpenAI Codex](https://developers.openai.com/codex/skills); other coding agents that can read a skill markdown file and call tools (Read, Grep, Glob, Bash, Write) should also work.
- **Python 3.9 or newer on the PATH.** Praxen's report renderer (`render.py`, bundled with the skill) is plain Python 3 — standard library only, nothing to `pip install`. 3.9 is the macOS Command Line Tools system Python (Ventura / Sonoma / Sequoia), so on macOS there's typically nothing to install. On Windows, `py -3` works. If `python3` isn't found, the renderer step falls back to `python`.
- **Network access for your coding agent's LLM provider** during analysis. Praxen itself does not phone home, but the LLM calls your coding agent makes during analysis follow whatever provider configuration the agent uses.
- **Workspace write permission for the agent.** Praxen writes its report files to a `./reports/` directory and runs two bundled Python scripts during a scan, so the agent must be allowed to write within the working directory (the default in Claude Code; on Codex, run with a workspace-write sandbox — see below).

That's the entire dependency surface.

---

## Option A — Claude Code (plugin marketplace)

The recommended path for Claude Code users. From your terminal:

```bash
claude plugin marketplace add open-agent-ai-security/praxen
claude plugin install praxen@open-agent-ai-security
claude plugin list      # confirm: praxen@open-agent-ai-security, enabled, v0.7.8+
```

The skill registers as `behavior-verifier`. The in-session equivalents — `/plugin marketplace add …`, `/plugin install …`, `/plugin list` — do exactly the same thing; if you install from within a Claude Code session, run `/reload-plugins` (or restart) to activate the skill. Prefer the terminal form when scripting: `claude plugin …` is argument-driven and runs the same way on every interface, whereas in-session slash commands occasionally fall through and get sent as ordinary chat messages.

---

## Option B — OpenAI Codex (agent skill)

Codex reads skills from `.agents/skills/` (in the repo/working directory) and from `~/.codex/skills/` (user-wide). From a repo checkout or an unzipped release (see Option C), make the bundled skill discoverable:

```bash
# repo-local (this project only):
mkdir -p .agents/skills
ln -s "$(pwd)/skills/behavior-verifier" .agents/skills/behavior-verifier

# …or user-wide (every Codex session):
mkdir -p "$HOME/.codex/skills"
ln -s "$(pwd)/skills/behavior-verifier" "$HOME/.codex/skills/behavior-verifier"
```

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

> **Codex plugin packaging.** Praxen ships a `.codex-plugin/plugin.json` (pointing Codex at the same `./skills/`), so it also installs through Codex's `codex plugin marketplace add …` / `codex plugin add praxen@…` flow from a local plugin source. A published Codex marketplace entry for a one-line public install is in progress; until then, the skill-folder path above is the supported install.

---

## Option C — Run from an unzipped release (either agent)

If you can't or don't want to use a marketplace flow, unzip the release archive somewhere your coding agent can see it. There's no install step — the archive carries both the `.claude-plugin/` and `.codex-plugin/` manifests plus the shared `skills/` engine.

```bash
# Replace VERSION with the release tag and RELEASE_URL with the .zip asset URL
curl -L -o praxen-VERSION.zip RELEASE_URL
unzip praxen-VERSION.zip
cd praxen-VERSION
```

Then point your coding agent at `skills/behavior-verifier/SKILL.md` (Claude Code), or link it into `.agents/skills/` and invoke `$praxen:behavior-verifier` (Codex, per Option B). See [Usage](usage.md).

---

## Verifying the install

**Claude Code:**

```bash
claude plugin list
```

If `praxen@open-agent-ai-security` appears at `v0.7.8` or later with `enabled`, the marketplace install is working. From within a session the same plugin shows under `/plugin list`, and the skill is invocable as `behavior-verifier`.

**Codex:** confirm the skill is visible to the model (it appears in Codex's skill list as `praxen:behavior-verifier`), then run a scoped scan and check that JSON / HTML / TXT land under `./reports/`.

For an end-to-end first run that actually exercises the analysis pipeline — Worker Remit + agent source → HTML / JSON / TXT report — see [Quickstart](quickstart.md). It walks through scanning the bundled `finbot` example in about five minutes.

---

## Updating

**Claude Code (plugin marketplace):**

```bash
claude plugin marketplace update open-agent-ai-security
claude plugin update praxen@open-agent-ai-security
```

Restart Claude Code to apply. (In-session equivalents are the same commands as `/plugin …`.)

**OpenAI Codex / unzipped release:** pull the latest checkout or download the new release zip and replace it — a symlinked skill folder picks up the new version automatically. There is no migration step; Praxen is stateless across analyses.

---

## Uninstalling

**Claude Code (plugin marketplace):**

```bash
claude plugin uninstall praxen@open-agent-ai-security
claude plugin marketplace remove open-agent-ai-security
```

The marketplace is removed by its registered name (`open-agent-ai-security`, from `.claude-plugin/marketplace.json`) — which here matches the repo owner used to add it.

**OpenAI Codex:** remove the skill link (`rm .agents/skills/behavior-verifier` or `rm ~/.codex/skills/behavior-verifier`); if you installed it as a Codex plugin, `codex plugin remove praxen@…`.

**Unzipped release:** delete the directory. No system state is left behind.

---

## Next steps

- [Quickstart](quickstart.md) — first end-to-end report against the bundled `finbot` example
- [Writing Worker Remits](writing-remits.md) — authoring the policy document Praxen verifies against
- [Usage](usage.md) — the full running-an-analysis reference
