<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Quickstart — your first Praxen report in 5 minutes

This walks you from "Praxen is installed" to "I have a real report" against one of the bundled examples — `finbot`, a deliberately vulnerable financial assistant from the OWASP Agentic AI CTF. No editing your own agent required.

If you haven't installed yet, do [Installation](installation.md) first (one command from the marketplace).

---

## 1. Get a copy of the example workspace

If you don't have a local copy of the Praxen repository yet, clone it (or unzip a release):

```bash
git clone https://github.com/open-ai-security/praxen.git
cd praxen
```

The pieces you'll point Praxen at are already inside `examples/finbot/`:

```
examples/finbot/
  WORKER_REMIT.md          ← the policy doc you'll verify against
  finbot-analysis.html     ← the committed report (what your run should approximately produce)
  finbot-findings.json     ← the same content as canonical JSON
```

A real first scan would use *your* agent's source plus a remit you wrote. We're using the pre-staged ones so the first run has no moving parts.

## 2. Get the FinBot source

The example was developed against the **CineFlow Productions finbot** from the OWASP Agentic AI CTF (see [`examples/README.md`](../examples/README.md) for the full provenance). Clone the source so Praxen has a real workspace to read:

```bash
git clone https://github.com/OWASP-ASI/finbot-ctf-demo.git ../finbot-src
```

(Any directory will do — `../finbot-src` keeps the clone outside the Praxen tree and works the same on macOS, Linux, and Windows.)

## 3. Run the analysis

From a Claude Code session in the `praxen` repo directory, ask the agent:

```
Please run the behavior-verifier skill against ../finbot-src.
Use the Worker Remit at examples/finbot/WORKER_REMIT.md. Write outputs
to ./reports/finbot-quickstart/.
```

That's the whole prompt. Praxen will:

1. Read the Worker Remit
2. Sweep the workspace at `../finbot-src`
3. Score the six RAISE categories
4. Audit every remit rule
5. Surface compound attack chains
6. Write three files to `./reports/finbot-quickstart/`

The skill prints an interim overview to stdout while it works. When it finishes you'll have:

```
./reports/finbot-quickstart/
  finbot-findings-YYYY-MM-DD.json     ← canonical record
  finbot-analysis-YYYY-MM-DD-HHMMSS.html  ← human-readable report
  finbot-analysis-YYYY-MM-DD-HHMMSS.txt   ← plain-text summary
```

## 4. Open the report

```bash
open ./reports/finbot-quickstart/finbot-analysis-*.html
```

(`open` is macOS; on Linux use `xdg-open`, on Windows the file works in any browser.)

What you should see, top to bottom:

- A red **CRITICAL** status badge — FinBot is deliberately broken
- An **Agent Remit** panel restating what the remit says, alongside an **Agent Structure** panel summarising what Praxen found in the workspace
- A **Behavior Summary** — the dominant pattern (typically something like *"framework offers safe primitives, code uses none of them"*)
- A **Remit Coverage** table listing every rule with status (`Verified` / `Gap` / `Partial` / `Vague` / `ENP`)
- A **Findings Register** — Critical first, then High, Medium, Low, Informational, each with evidence and a recommended action
- A **RAISE Maturity Posture** wrap-up — a 0–5 weighted score across six categories

You can compare your fresh report against the committed [`examples/finbot/finbot-analysis.html`](../examples/finbot/finbot-analysis.html). It won't be byte-identical (LLM analyses have run-to-run variance) but the dominant Critical themes, the broad RAISE shape, and the remit-coverage counts should be close. See [tests/README.md](../tests/README.md) for what "close" actually means for this target.

## 5. Now try your own agent

The pattern is identical with a real target:

1. [Write a Worker Remit](writing-remits.md) for the agent
2. Point Praxen at whatever evidence you have — source, deployment files, behavioral logs, governance docs
3. Read the report; [iterate](challenging-findings.md) on the remit and the agent as needed

See [Usage](usage.md) for the full set of input shapes and the running-an-analysis details.

---

## If something went wrong

See the [Troubleshooting](usage.md#troubleshooting) section in `usage.md`. The most common first-run snags:

- **"behavior-verifier skill not found"** — restart Claude Code or run `/reload-plugins`
- **`render.py` errored at the end** — the LLM produced a malformed findings JSON; re-run with more context window or a more focused workspace path
- **Context window auto-compacted during the run** — Praxen wrote a draft manifest in `./reports/<agent>-draft-<timestamp>.md`; tell the agent to read it and finish from there. See [Usage § Large workspaces and context sizing](usage.md#large-workspaces-and-context-sizing).
