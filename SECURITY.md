<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Security Policy

Praxen is a security tool. We take vulnerabilities in Praxen itself seriously. This document describes how to report one privately, what is in scope, and what to expect after you report.

## Scope

**In scope** — vulnerabilities in Praxen itself:

- The `behavior-verifier` skill (the prompt and step graph in `skills/behavior-verifier/SKILL.md`).
- The deterministic renderer (`skills/behavior-verifier/render.py`) and report template (`report_template.html`).
- The findings-JSON schema validator (`skills/behavior-verifier/schema.py`, `findings.schema.json`).
- The plugin manifest (`.claude-plugin/plugin.json`, `marketplace.json`).
- The build (`build.sh`) and release (`.github/workflows/release.yml`) pipelines, and the published `praxen-X.Y.Z.zip` artifacts.

Examples of in-scope issues: an injection in a finding's `evidence.snippet` that escapes the HTML escaper and executes script in the rendered report; a path-traversal in `render.py` that lets a crafted findings JSON write outside the output directory; a tampered release artifact.

**Out of scope** — findings *about* the agents Praxen analyses. If you run Praxen against an AI agent and Praxen reports a finding against that agent, that is normal output of the tool, not a vulnerability in Praxen. Please report those to the agent's own maintainer, not here.

## Reporting a vulnerability

**Do not file a public GitHub issue for a security vulnerability.** Public issues are indexed and broadcast immediately; that is the wrong channel for an unpatched defect.

Use GitHub's private security advisory:

1. Go to the [Security tab](https://github.com/open-agent-ai-security/praxen/security) on this repository.
2. Click **Report a vulnerability**.
3. Fill in the form. Include enough detail to reproduce — a minimal Praxen input, the observed output, and what you expected to differ. Attach the crafted findings JSON, remit, or repro script if applicable.

GitHub will create a private advisory thread between you and the project maintainers. We will respond there.

If GitHub Security Advisories are unavailable to you for any reason, email **open-agent-ai-security@exabeam.com** with the subject line **`Praxen security report`** and the same level of detail.

## What to expect

- **Initial acknowledgement:** within 3 business days of your report.
- **First substantive reply** (we understand the issue, we agree on scope and severity, here is the plan): within 10 business days.
- **Fix timeline:** depends on severity and complexity. Critical issues are prioritised; expect a fix in an immediate patch release, rather than waiting for the next scheduled minor release.
- **Coordinated disclosure:** we prefer to ship the fix in a tagged release, publish a [GitHub Security Advisory](https://github.com/open-agent-ai-security/praxen/security/advisories) (with credit to you unless you ask otherwise), and request a CVE if the issue warrants one. We will coordinate the public-disclosure timing with you.

If you do not hear back from us within the windows above, please nudge the thread or escalate via the email address above.

## Supported versions

Security fixes ship in the **latest** released `0.x` line. Praxen is pre-`1.0` and there is no LTS branch; please upgrade to the latest tagged release before reporting.

| Version | Receiving security fixes |
|---|---|
| `0.7.x` | ✓ Yes — current release line |
| `0.6.x` and earlier (under the former name `Praxa`, at `Exabeam/deckard`) | No — superseded by the rename, not maintained |
