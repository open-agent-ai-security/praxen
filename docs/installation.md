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

- **Disable updates globally:** `DISABLE_AUTOUPDATER=1` turns off Claude Code's automatic updates. For Praxen specifically, the per-marketplace toggle above is the reliable control; for the exact scope of the env var, see Claude Code's own settings documentation.

> Because Praxen is a security tool, staying current matters — enabling auto-update (or updating on a regular cadence) is recommended.

### OpenAI Codex — marketplace

Refresh the catalog snapshot, then re-install — the same two-step shape as Claude Code:

```bash
codex plugin marketplace upgrade open-agent-ai-security   # refresh the snapshot from the repo
codex plugin add praxen@open-agent-ai-security             # install the refreshed version
```

### Any other agent

Tell the agent to `git pull` its clone (or re-clone), or download a newer release `.zip`. There's no migration step — Praxen is stateless across analyses.

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
