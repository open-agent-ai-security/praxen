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

Codex surfaces the skill as **`praxen:behavior-verifier`** — invoke it by that plugin-qualified name (`$praxen:behavior-verifier`, not `$behavior-verifier`) and point it at a target. Praxen needs workspace writes (it creates `./reports/` and runs two bundled Python scripts), so run `codex exec` with a workspace-write sandbox:

```bash
codex exec --sandbox workspace-write -C /path/to/scan-dir \
  'Use $praxen:behavior-verifier. Run a Praxen behavior analysis against ./target. Use the Worker Remit at ./WORKER_REMIT.md. Write outputs to ./reports/.'
```

That's the whole happy path; for an end-to-end first run, see [Quickstart](quickstart.md). (To scope the skill to a single project instead of user-wide, link it into that repo's own `.agents/skills/`. A public Codex *marketplace* install mirroring Option A is [tracked as a future enhancement](https://github.com/open-agent-ai-security/praxen/issues/102), not yet available.)

> **Two Codex gotchas.** `codex exec -C <dir>` refuses to run outside a trusted git repo (`Not inside a trusted directory…`) — run from a git checkout, or add `--skip-git-repo-check`. And on load Codex may print warnings about *other* installed plugins or a telemetry metric-tag on the `praxen:behavior-verifier` id; those are Codex-side and don't affect the scan.

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

Every Praxen release bumps the version string, so a new version is always picked up once you refresh — the only question is whether you refresh by hand or let Claude Code do it for you. Check what you currently have with:

```bash
claude plugin list      # shows praxen@open-agent-ai-security and its installed version
```

### Claude Code — manual update

Two steps (the catalog refresh and the install are independent), then restart:

```bash
claude plugin marketplace update open-agent-ai-security   # refresh the catalog from the repo
claude plugin update praxen@open-agent-ai-security         # install the latest version
```

Restart Claude Code (or run `/reload-plugins`) to apply. **Don't skip the first command** — on its own, `plugin update` only moves you to the newest version in your *local* catalog cache, which may be stale. The in-session `/plugin marketplace update …` and `/plugin update …` do exactly the same thing.

### Claude Code — auto-update (opt-in)

Auto-update is a **per-marketplace** setting, and for third-party marketplaces like Praxen's it is **off by default** — so out of the box you're on manual updates, and **Claude Code does not notify you** when a newer version exists. To turn it on:

- **Interactively:** `/plugin` → **Marketplaces** tab → select `open-agent-ai-security` → **enable auto-update**. Claude Code then checks for a newer version **at startup** (not on a schedule) and updates automatically.
- **Fleet-wide (admins)** — in managed `settings.json`:

  ```json
  {
    "extraKnownMarketplaces": {
      "open-agent-ai-security": {
        "source": { "source": "github", "repo": "open-agent-ai-security/praxen" },
        "autoUpdate": true
      }
    }
  }
  ```

- **Global override (env vars):** `DISABLE_AUTOUPDATER=1` turns off *all* auto-updates; add `FORCE_AUTOUPDATE_PLUGINS=1` alongside it to keep plugin auto-updates while disabling Claude Code's own self-update.

> Because Praxen is a security tool, staying current matters — enabling auto-update (or updating on a regular cadence) is recommended.

### OpenAI Codex / unzipped release

There's no marketplace, so updating is manual: `git pull` the checkout (a symlinked skill folder picks up the new version automatically), or download the new release zip and replace it. There's no migration step; Praxen is stateless across analyses.

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
