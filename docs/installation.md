<!--
  Copyright © 2026 Exabeam, Inc. All Rights Reserved.
  Confidential and Proprietary. Do not distribute. Use by permission only.
-->

# Installation

Praxa ships as a Claude Code plugin. You can install it through the plugin marketplace mechanism or run it directly from an unzipped release — both paths work and produce identical analyses.

---

## Prerequisites

- **A coding agent** capable of tool use and multi-step instruction-following. Praxa is tested against [Claude Code](https://docs.claude.com/en/docs/claude-code/overview); other coding agents that can read a skill markdown file and call tools (Read, Grep, Glob, Bash, Write) should also work.
- **Network access for your coding agent's LLM provider** during analysis. Praxa itself does not phone home, but the LLM calls your coding agent makes during analysis will follow whatever provider configuration the agent uses.

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

You should see `praxa` (with version `0.1.0` or later).

> **Note:** the GitHub repository is currently named `Exabeam/deckard`. The repository rename to match the project name is a separate administrative task. Use the URL above as-is.

---

## Option B — Use directly from an unzipped release

If you can't or don't want to use the plugin marketplace flow, unzip the release archive somewhere your coding agent can see it. There's no install step.

```bash
curl -L -o praxa-0.1.0.zip <release-URL>
unzip praxa-0.1.0.zip
cd praxa-0.1.0
```

Then point your coding agent at `skills/behavior-verifier/SKILL.md` when running an analysis. See [Usage](usage.md).

---

## Verifying the install

Run an analysis against one of the bundled examples. The `examples/` directory contains pre-staged Worker Remits for FinBot and HelperBot — both deliberately vulnerable agents. From a Claude Code session:

```
Please run the behavior-verifier skill against examples/finbot/. Use the Worker Remit at examples/finbot/WORKER_REMIT.md. Write outputs to a temporary reports directory.
```

A successful analysis produces three files in the reports directory:

- `finbot-analysis-<timestamp>.html`
- `finbot-findings-<date>.json`
- `finbot-analysis-<timestamp>.txt`

Open the HTML in a browser. If the report renders with the Praxa header, six RAISE category cards, and a Findings Register populated with cited evidence, the install is working.

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
