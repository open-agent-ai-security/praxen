<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Installation

> **🧪 You are on the Praxen 2.0 beta channel.** These instructions install
> the `praxen-beta` marketplace entry, which tracks the pre-release 2.0 beta
> (threat modeling). It installs under its own plugin key, side by side with
> a production `praxen` install — but run one at a time: if you have
> production Praxen installed, disable it while testing
> (`claude plugin disable praxen@open-agent-ai-security`) so both plugins
> don't answer a "run a Praxen analysis" request, and re-enable it when
> you're done. Report anything odd on
> [GitHub issues](https://github.com/open-agent-ai-security/praxen/issues).

Praxen ships as a portable **agent skill**, packaged for both **Claude Code** and **OpenAI Codex**. Both platforms load the same `skills/behavior-verifier` engine and produce the same JSON / HTML / TXT report format — only the install/packaging differs. On the same inputs, findings should cover the same major themes, but exact counts, grouping, and RAISE maturity scores can vary by model and context (see [Understanding Run-to-Run Variability](understanding-variability.md)). Claude Code is the most common path; Codex is supported as a first-class agent-skills platform.

## Prerequisites

- **A coding agent** capable of tool use and multi-step instruction-following. Praxen is tested against [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) and [OpenAI Codex](https://developers.openai.com/codex/skills); other coding agents that can read a skill markdown file and call tools (Read, Grep, Glob, Bash, Write) should also work.
- **Python 3.9 or newer on the PATH** — for the bundled report renderer (`render.py`), which is standard-library only (nothing to `pip install`). You almost certainly already have it: 3.9 ships as the macOS Command Line Tools system Python, and on Windows `py -3` works. (If `python3` isn't found, the renderer falls back to `python`.)
- **Network access for your coding agent's LLM provider** during analysis. Praxen itself does not phone home, but the LLM calls your coding agent makes during analysis follow whatever provider configuration the agent uses.
- **Workspace write permission for the agent.** Praxen writes its report files to a `./reports/` directory and runs two bundled Python scripts during a scan, so the agent must be allowed to write within the working directory. Claude Code allows this by default; agents that sandbox file writes need that permission granted (per your agent's own docs).

That's the entire dependency surface.

## Claude Code

Install from the community plugin marketplace ([open-agent-ai-security/plugins](https://github.com/open-agent-ai-security/plugins) — one `marketplace add` covers every Open Agent AI Security plugin). From your terminal:

```bash
claude plugin marketplace add open-agent-ai-security/plugins
claude plugin install praxen-beta@open-agent-ai-security
claude plugin list      # confirm: praxen-beta@open-agent-ai-security, enabled, v2.0.0-beta.1
```

> **Added the marketplace from `open-agent-ai-security/praxen` previously?** That path still
> works — this repo carries a synced mirror of the community index — but the community
> marketplace is the canonical source, and the `praxen-beta` entry only exists there. Run the
> add + install commands above; your existing production install and its
> `praxen@open-agent-ai-security` key are untouched — the beta lands under its own
> `praxen-beta@open-agent-ai-security` key (see the disable note at the top).

The skill registers as `behavior-verifier`. The in-session equivalents — `/plugin marketplace add …`, `/plugin install …`, `/plugin list` — do exactly the same thing; if you install from within a Claude Code session, run `/reload-plugins` (or restart) to activate the skill. (When scripting, prefer the terminal form — it behaves identically everywhere.)

## OpenAI Codex

Codex has its own plugin marketplace, and Praxen installs from the **same community marketplace** as the Claude Code path (Codex reads the same catalog manifest and honors its `main`-branch pins). From your terminal:

```bash
codex plugin marketplace add open-agent-ai-security/plugins
codex plugin add praxen-beta@open-agent-ai-security
codex plugin list      # confirm: praxen-beta@open-agent-ai-security, installed, enabled, v2.0.0-beta.1
```

This installs and enables the plugin in Codex's local config; the bundled `behavior-verifier` skill is then available to every Codex session. Running an analysis is the same as on any agent — see [Usage](usage.md).

> **Already added the Codex marketplace from `open-agent-ai-security/praxen`?** Run the `marketplace add` above — it registers under the same marketplace name, and the `praxen-beta` entry only exists in the community catalog. Your production `praxen@open-agent-ai-security` install is untouched; the beta lands under its own `praxen-beta@open-agent-ai-security` key (disable production Praxen while testing, per the note at the top).

## Any other agent

No marketplace, no download step — Praxen is just a skill folder in a public repo, so any capable coding agent can fetch and run it from a plain-English instruction. (This also works on Claude Code or Codex if you'd rather skip the marketplace.) In your agent session, say something like:

> Clone `https://github.com/open-agent-ai-security/praxen` and follow its `behavior-verifier` skill to run a Praxen behavior analysis on [your target]. Use the Worker Remit at [path].

The agent brings down its own copy and runs the skill from `skills/behavior-verifier/`. Offline? Download the release `.zip` from the [releases page](https://github.com/open-agent-ai-security/praxen/releases) and point your agent at the unzipped folder instead. See [Usage](usage.md) for the analysis instructions.

## Updating

Every release bumps the version, so a refresh always picks up the latest. Check what you have with `claude plugin list`.

**Claude Code** — refresh the catalog, update, then restart (`/reload-plugins` or relaunch):

```bash
claude plugin marketplace update open-agent-ai-security   # refresh the catalog
claude plugin update praxen-beta@open-agent-ai-security         # install the latest
```

Both steps matter: without the first, `plugin update` only sees your local (possibly stale) catalog cache.

**OpenAI Codex** — the same two-step shape:

```bash
codex plugin marketplace upgrade open-agent-ai-security
codex plugin add praxen-beta@open-agent-ai-security
```

**Any other agent** — `git pull` the clone (or re-clone), or download a newer release `.zip`. Praxen is stateless across analyses, so there's no migration step.

> **Upgrading from 1.1?** The update commands above are the whole procedure — nothing to migrate. What you'll notice after the jump: findings JSON is now **schema 3.0** (findings carry `policy_rule_ids` / `policy_rule_text` *arrays* — anything parsing the old single-value fields needs updating; see the [reports reference](interpreting-reports.md) and the [schema stability policy](https://github.com/open-agent-ai-security/praxen/blob/main/STABILITY.md)), risk tags use the **2026 OWASP** LLM and Agentic Top 10 names, and scores are **not directly comparable** to 1.1 reports (the reference model, knowledge bases, and remit guidance all moved — see the [CHANGELOG](https://github.com/open-agent-ai-security/praxen/blob/main/CHANGELOG.md)). If you originally added the marketplace from `open-agent-ai-security/praxen`, see the migration note in the install section above — the legacy path still updates, but the community catalog is canonical.

> Praxen is a security tool — staying current matters. Update on a regular cadence, or turn on auto-update (below).

### Auto-update and fleet config (Claude Code)

Auto-update is **per-marketplace and off by default** for third-party marketplaces, and Claude Code won't notify you when a new version exists. To enable it interactively: `/plugin` → **Marketplaces** → select `open-agent-ai-security` → **enable auto-update** (it then checks at startup). Admins can set it fleet-wide in managed `settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "open-agent-ai-security": {
      "source": { "source": "github", "repo": "open-agent-ai-security/plugins" },
      "autoUpdate": true
    }
  }
}
```

(`DISABLE_AUTOUPDATER=1` turns off Claude Code's auto-updates globally; see Claude Code's settings docs for its exact scope.)

## Uninstalling

**Claude Code (plugin marketplace):**

```bash
claude plugin uninstall praxen-beta@open-agent-ai-security
claude plugin marketplace remove open-agent-ai-security
```

The marketplace is removed by its registered name (`open-agent-ai-security`, from `.claude-plugin/marketplace.json`) — which here matches the repo owner used to add it.

**OpenAI Codex (marketplace):**

```bash
codex plugin remove praxen-beta@open-agent-ai-security
codex plugin marketplace remove open-agent-ai-security
```

**Any other agent:** delete the cloned (or unzipped) folder. No system state is left behind.

## Next steps

- [Quickstart](quickstart.md) — first end-to-end report: have Claude author a remit for the FinBot demo agent, scan it, and read the report
- [Writing Worker Remits](writing-remits.md) — authoring the policy document Praxen verifies against
- [Usage](usage.md) — the full running-an-analysis reference
