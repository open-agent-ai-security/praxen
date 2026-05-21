<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Installation

Praxen ships as a Claude Code plugin. You can install it through the plugin marketplace mechanism or run it directly from an unzipped release — both paths work and produce identical analyses.

---

## Prerequisites

- **A coding agent** capable of tool use and multi-step instruction-following. Praxen is tested against [Claude Code](https://docs.claude.com/en/docs/claude-code/overview); other coding agents that can read a skill markdown file and call tools (Read, Grep, Glob, Bash, Write) should also work.
- **Python 3.9 or newer on the PATH.** Praxen's report renderer (`render.py`, bundled with the skill) is plain Python 3 — standard library only, nothing to `pip install`. 3.9 is the macOS Command Line Tools system Python (Ventura / Sonoma / Sequoia), so on macOS there's typically nothing to install. On Windows, `py -3` works. If `python3` isn't found, the renderer step falls back to `python`. (3.8 was supported up to v0.2.0 and dropped at v0.3.0 — EOL since 2024-10-07.)
- **Network access for your coding agent's LLM provider** during analysis. Praxen itself does not phone home, but the LLM calls your coding agent makes during analysis follow whatever provider configuration the agent uses.

That's the entire dependency surface.

---

## Option A — Install via Claude Code plugin marketplace

This is the recommended path for Claude Code users. From your terminal:

```bash
claude plugin marketplace add open-ai-security/praxen
claude plugin install praxen@open-ai-security
claude plugin list      # confirm: praxen@open-ai-security, enabled, v0.7.0+
```

The skill registers as `behavior-verifier`. The in-session equivalents — `/plugin marketplace add …`, `/plugin install …`, `/plugin list` — do exactly the same thing; if you install from within a Claude Code session, run `/reload-plugins` (or restart) to activate the skill. Prefer the terminal form when scripting: `claude plugin …` is argument-driven and runs the same way on every interface, whereas in-session slash commands occasionally fall through and get sent as ordinary chat messages.

---

## Option B — Use directly from an unzipped release

If you can't or don't want to use the plugin marketplace flow, unzip the release archive somewhere your coding agent can see it. There's no install step.

```bash
curl -L -o praxen-0.7.0.zip <release-URL>
unzip praxen-0.7.0.zip
cd praxen-0.7.0
```

Then point your coding agent at `skills/behavior-verifier/SKILL.md` when running an analysis. See [Usage](usage.md).

---

## Verifying the install

Run:

```bash
claude plugin list
```

If `praxen@open-ai-security` appears at `v0.7.0` or later with `enabled`, the marketplace install is working. From within a Claude Code session, the same plugin shows up under `/plugin list`, and the skill is invocable as `behavior-verifier`.

For an end-to-end first run that actually exercises the analysis pipeline — Worker Remit + agent source → HTML / JSON / TXT report — see [Quickstart](quickstart.md). It walks through scanning the bundled `finbot` example in about five minutes.

---

## Updating

**Plugin marketplace install:**

```bash
claude plugin marketplace update open-ai-security
claude plugin update praxen@open-ai-security
```

Restart Claude Code to apply. (In-session equivalents are the same commands as `/plugin …`.)

**Unzipped release:** download the new release zip and replace the unzipped directory. There is no migration step — Praxen is stateless across analyses.

---

## Uninstalling

**Plugin marketplace install:**

```bash
claude plugin uninstall praxen@open-ai-security
claude plugin marketplace remove open-ai-security
```

The marketplace is removed by its registered name (`open-ai-security`, from `.claude-plugin/marketplace.json`) — which here matches the repo owner used to add it.

**Unzipped release:** delete the directory. No system state is left behind.

---

## Next steps

- [Quickstart](quickstart.md) — first end-to-end report against the bundled `finbot` example
- [Writing Worker Remits](writing-remits.md) — authoring the policy document Praxen verifies against
- [Usage](usage.md) — the full running-an-analysis reference
