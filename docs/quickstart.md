<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Quickstart — your first Praxen report in about 15 minutes

A complete Praxen run, end to end: you'll have Claude **author a security policy** for a real agent, **verify the agent's code against it**, and read the report — all from plain-English instructions. The target is **FinBot**, a deliberately vulnerable invoice-processing agent from the OWASP Agentic AI CTF, so the divergences are dramatic and easy to learn from.

This walkthrough uses **Claude Code**; **OpenAI Codex** works the same way — wherever it says `claude` or "ask Claude," substitute your Codex invocation, and the steps are identical.

You do very little here — a few short instructions; Claude does the work: fetching docs, writing the policy, cloning the code, running the analysis, and rendering the report. Budget about 15 minutes for your first report, most of it Claude thinking while you watch. (The optional **Bonus** at the end — fix a finding and re-scan — adds a few more.)

> Not installed yet? Do [Installation](installation.md) first — one marketplace command on Claude Code or Codex. There's nothing else to clone or download; Claude pulls what it needs.

## Set up

Start a Claude Code session in a fresh, empty folder — that's where the remit and the `reports/` will land:

```bash
mkdir finbot-quickstart && cd finbot-quickstart
claude
```

As you go, Claude will ask permission to do things like clone the repo, write the remit, and run the renderer — approve them.

## 1. Have Claude author the Worker Remit

A Praxen scan checks an agent against a **Worker Remit** — a plain-language policy of what the agent is *supposed* to do. Rather than hand-write one, have Claude do it:

> *Author a Worker Remit for this agent from its repo docs. It's an intentionally vulnerable bot, so build the remit from the **intended** ("desired") behavior in the docs — don't read the implementation code: https://github.com/OWASP-ASI/finbot-ctf-demo*

**What Claude does:** loads the Praxen skill, reads the repo's README and design/walkthrough docs (not the code), and — because FinBot's docs are an *attack* walkthrough — inverts each documented exploit into the secure behavior it violates. It writes `WORKER_REMIT.md` and appends a short **Open Questions** list for what it can't infer (the real approval thresholds, whether vendors are allowlisted, whether MFA is required). A couple of minutes.

**Why "don't read the code" matters:** the remit is the standard the scan judges the code against. If you author it *from* the implementation, it just mirrors what the code already does — and the scan finds nothing. Building it from stated intent is what gives the scan something real to measure against. (This discipline is built into the skill; see [Writing Worker Remits](writing-remits.md).) Skim `WORKER_REMIT.md` — it's your policy, and you can tighten it or answer the Open Questions before scanning if you want a sharper result.

## 2. Have Claude run the scan

Now point Praxen at the agent's actual code, using the remit it just wrote:

> *Run the scan now, using the remit you built.*

*(For this tutorial, scanning in the same session is fine. On your own targets you'll get a sharper scan from a fresh session — see [Usage § fresh context](usage.md#for-highest-scan-fidelity-run-in-a-fresh-context).)*

**What Claude does:** clones FinBot itself, sweeps the workspace, scores the agent across the six **RAISE** security-maturity categories (a 0–5 scale — see [RAISE](RAISE.md)), audits every remit rule, and renders the report. This is the longest step — a few minutes while Claude works.

**What you'll see:** FinBot lands at a RAISE posture of **"Absent"** — a near-floor score, expected for a deliberately-broken agent — with a dozen-plus findings, **Criticals first**. The headline is a compound chain: an unauthenticated admin plane → attacker text written into the agent's goals → no approval gate on payments → no audit log — the exact goal-hijack-to-autonomous-payment path the CTF is built around. It also notes what FinBot gets *right* (no code-execution capability, a bounded agent loop), so the report isn't only a list of failures.

*(Exact counts and the score shift from run to run — synthesis is an act of judgment, not a fixed function. The themes are the stable signal; see [Run-to-Run Variability](understanding-variability.md).)*

## 3. Read the report

> *Show me the report in the browser.*

Claude opens the self-contained HTML report. Read it top to bottom:

- **Behavior Summary + RAISE scorecard** — the one-line story (something like *"safe primitives offered, none used"*) and the 0–5 weighted maturity score across six categories, color-graded by score.
- **Findings register** — Critical first, then High → Informational. Each card carries its **`file:line` evidence** and the **remit rule(s) it violates**, plus a recommended action.
- **Remit Coverage table** — every rule you authored, marked `Verified` / `Gap` / `Partial` / `Vague` / `ENP` (Enforcement Not Possible). This is where you see how much of your policy the code actually honors.
- **OWASP heatmaps** + **Positives** — the findings mapped to the OWASP LLM and Agentic risk catalogs, and the controls that *are* present and working.

Ask Claude to walk through any finding — *"explain PRAX-005"*, *"why is this Critical?"* — and it re-examines the evidence with you. The analysis is conversational, so you can challenge or revise it; see [Challenging and Revising Findings](challenging-findings.md).

## Bonus — don't just measure, improve

At this point Praxen has done its core job: you have a report that tells you exactly where FinBot diverges from its remit. But a verifier that only measures is half a tool. A Praxen finding isn't just a label — it carries `file:line` evidence and a recommended action — so it's something you can act on. Close the loop.

Ask Claude to fix the worst one:

> *Find the most critical finding and create a fix.*

**What Claude does:** it identifies the highest-priority finding, targets a fix in the agent's code, verifies the change, and reports back what it changed and what's still open. Which finding it leads with and how it fixes it will vary — that's a judgment call on a live codebase — but the shape is consistent: one concrete, load-bearing fix, verified, not a vague to-do list.

*In one run, for example,* it targeted FinBot's missing payment-approval gate, added a deterministic check that routes high-value or manipulation-flagged invoices to human review before any payment, then verified it end-to-end — running a manipulated "CEO-approved, $25k, urgent" invoice through the real decision path and confirming it now stops at review while clean invoices still pass.

Now re-verify — run the same loop again:

> *Re-run the Praxen scan and show me what changed.*

The finding you fixed should resolve or downgrade, its remit rule should move toward `Verified`, and the RAISE posture should tick up. It won't jump to green — FinBot has plenty more deliberate holes, and the report now points you at the next one. That's the model: **measure → remediate → re-verify**, one link at a time, with the report as your worklist.

That loop — verify intent, fix the divergence, prove the fix landed — is the whole idea. Praxen doesn't just tell you an agent is unsafe; it hands you an actionable, re-checkable path to making it safe.

## Now point it at your own agent

Same moves, your target:

1. Ask Claude to **author a remit** from your agent's docs and intended behavior (or [write one yourself](writing-remits.md))
2. Ask it to **scan** your agent's evidence against it — source, deployment files, behavioral logs, governance docs
3. **Read** the report, then [iterate](challenging-findings.md) on the remit and the agent

See [Usage](usage.md) for the full set of input shapes and the running-an-analysis details.

> **Want a fixed, repeatable result** — a regression baseline rather than a tutorial? Use a pinned remit instead of authoring one each time. The bundled `examples/finbot/WORKER_REMIT.md` and its [reference report](https://open-agent-ai-security.github.io/praxen/examples/finbot/finbot-analysis.html) are exactly that; see [tests/README.md](../tests/README.md).

## If something went wrong

See the [Troubleshooting](usage.md#troubleshooting) section in `usage.md`. The most common first-run snags:

- **"behavior-verifier skill not found"** — restart Claude Code or run `/reload-plugins`
- **`render.py` errored at the end** — the model produced malformed findings JSON; ask Claude to re-render from the draft manifest it wrote, or re-run with a tighter workspace path
- **Context window auto-compacted during the run** — Praxen wrote a draft manifest at `./reports/<agent-slug>-draft-<timestamp>.md`; tell Claude to read it and finish the report from there. See [Usage § Large workspaces and context sizing](usage.md#large-workspaces-and-context-sizing).
