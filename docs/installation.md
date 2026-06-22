<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Installation

Praxen ships as a portable **agent skill**, packaged for both **Claude Code** and **OpenAI Codex**. Both platforms load the same `skills/behavior-verifier` engine and produce the same JSON / HTML / TXT report format — only the install/packaging differs. On the same inputs, findings should cover the same major themes, but exact counts, grouping, and RAISE maturity scores can vary by model and context (see [Understanding Run-to-Run Variability](understanding-variability.md)). Claude Code is the most common path; Codex is supported as a first-class agent-skills platform.

## Prerequisites

- **A coding agent** capable of tool use and multi-step instruction-following. Praxen is tested against [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) and [OpenAI Codex](https://developers.openai.com/codex/skills); other coding agents that can read a skill markdown file and call tools (Read, Grep, Glob, Bash, Write) should also work.
- **Python 3.9 or newer on the PATH** — for the bundled report renderer (`render.py`), which is standard-library only (nothing to `pip install`). You almost certainly already have it: 3.9 ships as the macOS Command Line Tools system Python, and on Windows `py -3` works. (If `python3` isn't found, the renderer falls back to `python`.)
- **Network access for your coding agent's LLM provider** during analysis. Praxen itself does not phone home, but the LLM calls your coding agent makes during analysis follow whatever provider configuration the agent uses.
- **Workspace write permission for the agent.** Praxen writes its report files to a `./reports/` directory and runs two bundled Python scripts during a scan, so the agent must be allowed to write within the working directory. Claude Code allows this by default; agents that sandbox file writes need that permission granted (per your agent's own docs).

That's the entire dependency surface.

## Claude Code

Install from the plugin marketplace. From your terminal:

```bash
claude plugin marketplace add open-agent-ai-security/praxen
claude plugin install praxen@open-agent-ai-security
claude plugin list      # confirm: praxen@open-agent-ai-security, enabled, v1.0.0+
```

The skill registers as `behavior-verifier`. The in-session equivalents — `/plugin marketplace add …`, `/plugin install …`, `/plugin list` — do exactly the same thing; if you install from within a Claude Code session, run `/reload-plugins` (or restart) to activate the skill. Prefer the terminal form when scripting: `claude plugin …` is argument-driven and runs the same way on every interface, whereas in-session slash commands occasionally fall through and get sent as ordinary chat messages.

## OpenAI Codex

Codex has its own plugin marketplace, and Praxen installs from the **same repo** as the Claude Code path. From your terminal:

```bash
codex plugin marketplace add open-agent-ai-security/praxen
codex plugin add praxen@open-agent-ai-security
codex plugin list      # confirm: praxen@open-agent-ai-security, installed, enabled, v1.0.0+
```

This installs and enables the plugin in Codex's local config; the bundled `behavior-verifier` skill is then available to every Codex session. Running an analysis is the same as on any agent — see [Usage](usage.md).

## Any other agent

No marketplace, no download step — Praxen is just a skill folder in a public repo, so any capable coding agent can fetch and run it from a plain-English instruction. (This also works on Claude Code or Codex if you'd rather skip the marketplace.) In your agent session, say something like:

> Clone `https://github.com/open-agent-ai-security/praxen` and follow its `behavior-verifier` skill to run a Praxen behavior analysis on [your target]. Use the Worker Remit at [path].

The agent brings down its own copy and runs the skill from `skills/behavior-verifier/`. Offline? Download the release `.zip` from the [releases page](https://github.com/open-agent-ai-security/praxen/releases) and point your agent at the unzipped folder instead. See [Usage](usage.md) for the analysis instructions.

## Updating

Every release bumps the version, so a refresh always picks up the latest. Check what you have with `claude plugin list`.

**Claude Code** — refresh the catalog, update, then restart (`/reload-plugins` or relaunch):

```bash
claude plugin marketplace update open-agent-ai-security   # refresh the catalog
claude plugin update praxen@open-agent-ai-security         # install the latest
```

Both steps matter: without the first, `plugin update` only sees your local (possibly stale) catalog cache.

**OpenAI Codex** — the same two-step shape:

```bash
codex plugin marketplace upgrade open-agent-ai-security
codex plugin add praxen@open-agent-ai-security
```

**Any other agent** — `git pull` the clone (or re-clone), or download a newer release `.zip`. Praxen is stateless across analyses, so there's no migration step.

> Praxen is a security tool — staying current matters. Update on a regular cadence, or turn on auto-update (below).

### Auto-update and fleet config (Claude Code)

Auto-update is **per-marketplace and off by default** for third-party marketplaces, and Claude Code won't notify you when a new version exists. To enable it interactively: `/plugin` → **Marketplaces** → select `open-agent-ai-security` → **enable auto-update** (it then checks at startup). Admins can set it fleet-wide in managed `settings.json`:

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

(`DISABLE_AUTOUPDATER=1` turns off Claude Code's auto-updates globally; see Claude Code's settings docs for its exact scope.)

## Uninstalling

**Claude Code (plugin marketplace):**

```bash
claude plugin uninstall praxen@open-agent-ai-security
claude plugin marketplace remove open-agent-ai-security
```

The marketplace is removed by its registered name (`open-agent-ai-security`, from `.claude-plugin/marketplace.json`) — which here matches the repo owner used to add it.

**OpenAI Codex (marketplace):**

```bash
codex plugin remove praxen@open-agent-ai-security
codex plugin marketplace remove open-agent-ai-security
```

**Any other agent:** delete the cloned (or unzipped) folder. No system state is left behind.

## Next steps

- [Quickstart](quickstart.md) — first end-to-end report: have Claude author a remit for the FinBot demo agent, scan it, and read the report
- [Writing Worker Remits](writing-remits.md) — authoring the policy document Praxen verifies against
- [Usage](usage.md) — the full running-an-analysis reference
