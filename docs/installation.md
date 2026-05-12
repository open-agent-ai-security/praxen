<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Installation

Praxa ships as a Claude Code plugin. You can install it through the plugin marketplace mechanism or run it directly from an unzipped release — both paths work and produce identical analyses.

---

## Prerequisites

- **A coding agent** capable of tool use and multi-step instruction-following. Praxa is tested against [Claude Code](https://docs.claude.com/en/docs/claude-code/overview); other coding agents that can read a skill markdown file and call tools (Read, Grep, Glob, Bash, Write) should also work.
- **Python 3.9 or newer on the PATH.** Praxa's report renderer (`render.py`, bundled with the skill) is plain Python 3 — standard library only, nothing to `pip install`. 3.9 is the macOS Command Line Tools system Python (Ventura / Sonoma / Sequoia), so on macOS there's typically nothing to install. On Windows, `py -3` works. If `python3` isn't found, the renderer step falls back to `python`. (3.8 was supported up to v0.2.0 and dropped at v0.3.0 — EOL since 2024-10-07.)
- **Network access for your coding agent's LLM provider** during analysis. Praxa itself does not phone home, but the LLM calls your coding agent makes during analysis follow whatever provider configuration the agent uses.

That's the entire dependency surface.

---

## Option A — Install via Claude Code plugin marketplace

This is the recommended path for Claude Code users. From within a Claude Code session:

```
/plugin marketplace add Exabeam/deckard
/plugin install praxa@exabeam
```

The skill registers as `behavior-verifier`. Confirm it's available:

```
/plugin list
```

You should see `praxa` (with version `0.6.1` or later).

> **Note:** the GitHub repository is currently named `Exabeam/deckard`. The repository rename to match the project name is a separate administrative task. Use the URL above as-is.

---

## Option B — Use directly from an unzipped release

If you can't or don't want to use the plugin marketplace flow, unzip the release archive somewhere your coding agent can see it. There's no install step.

```bash
curl -L -o praxa-0.6.1.zip <release-URL>
unzip praxa-0.6.1.zip
cd praxa-0.6.1
```

Then point your coding agent at `skills/behavior-verifier/SKILL.md` when running an analysis. See [Usage](usage.md).

---

## Verifying the install

Run an analysis against one of the bundled examples. The `examples/` directory contains pre-staged Worker Remits for FinBot and HelperBot — both deliberately vulnerable agents. From a Claude Code session:

```
Please run the behavior-verifier skill against examples/finbot/. Use the Worker Remit at examples/finbot/WORKER_REMIT.md. Write outputs to a temporary reports directory.
```

A successful analysis produces three files in the reports directory:

- `finbot-findings-<date>.json` — the canonical record (written by the skill)
- `finbot-analysis-<timestamp>.html` — the report (rendered from the JSON by `render.py`)
- `finbot-analysis-<timestamp>.txt` — a plain-text summary (also from `render.py`)

If the renderer step printed `render.py: wrote .../finbot-analysis-...html` and exited cleanly, the JSON passed schema validation and the HTML is marker-free. Open the HTML in a browser: if it renders with the Praxa header, six RAISE category cards, and a Findings Register populated with cited evidence, the install is working.

---

## Updating

### Plugin marketplace install

```
/plugin update praxa@exabeam
```

### Unzipped release

Download the new release zip and replace the unzipped directory. There is no migration step — Praxa is stateless across analyses.

---

## Uninstalling

### Plugin marketplace install

```
/plugin uninstall praxa@exabeam
/plugin marketplace remove Exabeam/deckard
```

### Unzipped release

Delete the directory. No system state is left behind.

---

## Next steps

- [Usage](usage.md) — running your first analysis
- [Writing Worker Remits](writing-remits.md) — authoring the policy document Praxa verifies against
