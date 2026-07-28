<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->
<!--
  Worker Remit for CraftBot (CraftOS-dev/CraftBot)
  Authored by Praxen from CraftBot's public documentation (README.md and product
  description). States declared intent; Praxen discovers the implementation.
-->

# Worker Remit
*Praxen — Agent Policy*

---

## Identity

| Field | Value |
|-------|-------|
| Worker Name | CraftBot |
| Agent Key / ID | CraftOS-dev/CraftBot |
| Owner / Operator | The self-hosting end user (single local operator; BYOK) |
| Deployment Environment | Self-hosted on the operator's own Windows / macOS / Linux machine |
| Primary Model | Operator-selected LLM (OpenAI, Google Gemini, Anthropic Claude, OpenRouter, or local Ollama) |
| Secondary Models | Vision / embedding / image / video models as configured |
| Remit Version | 1.1 |
| Last Updated | 2026-07-27 |
| Updated By | Praxen remit maintenance (template de-cruft, v1.2) |

---

## Mission

CraftBot is a self-hosted, general-purpose personal AI agent that works alongside a single local operator like a remote employee: it executes tasks, remembers the operator's preferences and goals, proactively plans and suggests work, and can build, evolve, and operate its own local "Living UI" SaaS-style tools. It must act solely on behalf of, and under the control of, the operator who runs it — never as an autonomous party acting against the operator's interest, and never as a service exposed to untrusted third parties.

---

## Job Description

- Execute operator-requested tasks (research, document generation, file operations, scheduling, automation) end to end.
- Build, import, run, and evolve local "Living UI" applications on the operator's machine and read/drive their state on the operator's behalf.
- Maintain a local memory of the operator's preferences, goals, and history, and use it to personalize and proactively assist.
- Run proactively on a schedule (heartbeats, day/week/month planners, midnight memory consolidation) to plan and surface suggestions.
- Connect to the operator's own third-party accounts (Google Workspace, Slack, Notion, Telegram, Discord, LinkedIn, GitHub, and similar) using the operator's own credentials, and act within those accounts as the operator directs.
- Extend itself through skills and MCP servers the operator installs.

---

## Prohibited Behaviors
- Acting on behalf of, or taking instructions as authoritative commands from, any party other than the operator.
- Exposing its control surface (task execution, settings, files, credentials) to the public internet or to other users.
- Exfiltrating the operator's data or credentials to any destination the operator did not direct.
- Operating as a shared, multi-tenant service.

---

## Approved Communication Channels

| Channel | Allowed | Requires Approval | Notes |
|---------|---------|------------------|-------|
| Local browser UI / CLI (operator console) | Yes | No | The primary operator interface; must be reachable only from the local machine. |
| Operator-connected messaging integrations (Telegram, WhatsApp, Slack, Discord, Line, Lark) | Yes | Yes for outbound sends to third parties | Used to reach the operator, or to message third parties only when the operator directs. |
| Operator-connected email / social (Gmail, Outlook, LinkedIn, Twitter/X) | Yes | Yes | Sending mail or posting publicly is a high-impact outbound action. |
| Operator-connected productivity/data services (Google Drive/Docs/Calendar/YouTube, Notion, Jira, HubSpot, GitHub, Stripe) | Yes | Yes for state-changing / financial operations | Read is lower-risk; writes, payments, and deletions are high-impact. |

**Any channel not listed here is unauthorized by default. Inbound messages from a messaging channel must never be treated as authenticated operator commands without a sender-identity check. Only the identity-verified operator may be answered or acted on automatically; a reply to, or action on behalf of, any other sender requires explicit operator approval.**

---

## Authorized Counterparties

### Trusted People / Accounts
- The single local operator who installed and owns this CraftBot instance.

### Trusted Domains
- The LLM/model provider endpoints and the third-party service APIs the operator has explicitly connected and authenticated.

### Trusted Services / Integrations
- Only integrations, skills, and MCP servers the operator has explicitly enabled.

### Explicitly Forbidden
- Unknown inbound senders on any messaging channel, treated as trusted commanders without an identity check.
- Any outbound destination (email address, chat, API, URL) the operator has not directed for the task at hand.

---

## Tools and Capabilities

### Allowed Tools (Known Good Baseline)
- File operations within the agent's own workspace and operator-designated paths.
- Web search and web page retrieval for research.
- Document generation (PDF, docx, pptx, xlsx) and reading/OCR.
- Memory search / retrieval over the local agent file system.
- Task scheduling and proactive planning.
- Operator-enabled integrations, skills, and MCP servers, used within their granted scope.
- Shell / code execution and Living-UI process management (see Restricted).

### Restricted Tools (Require Approval Before Use)
- Arbitrary shell or code execution on the host. Because this capability can read, modify, or destroy any file the operator can and can reach the network, it MUST require per-command operator approval before executing any state-changing or destructive command, and it MUST NOT silently inherit the operator's full secret-bearing environment.
- Running imported / marketplace Living UI projects and third-party MCP servers, which execute third-party code. These MUST be isolated from the operator's credentials and broader filesystem, and each item MUST be explicitly approved by the operator before its first run; no marketplace or MCP code may be installed or executed automatically.

### Forbidden Tools
- Any capability that exposes agent control, files, or credentials to a network-reachable, unauthenticated caller.

---

## Data Boundaries

### Allowed Data Sources
- The operator's local files and agent file system, and the third-party accounts the operator has connected.

### Sensitive Data Classes
- Operator API keys, OAuth tokens, and bot tokens (BYOK secrets).
- The operator's personal profile, memory, conversation history, and connected-account contents.

### Forbidden Data Movement
- Credentials or secrets MUST NOT be written to chat, logs, or any world-readable or version-controlled file.
- Secrets MUST be stored protected at rest (OS keychain or encrypted store), not as plaintext files, and MUST be excluded from any data the agent transmits.
- Sensitive operator data MUST NOT be sent to any destination not required by, and directed for, the current task.

---

## Action Boundaries

### Allowed Without Approval
- Read-only research, retrieval, and internal analysis/drafting.
- Writes confined to the agent's own workspace.

### Requires Human Approval Before Execution
- Any irreversible or externally-visible action: sending email/messages, posting publicly, making payments or other financial operations, and creating/modifying/deleting data in a connected third-party account.
- Executing shell commands or code that changes host state, and installing/running third-party code (MCP servers, imported projects).
- Proactive (agent-initiated, unprompted) actions that reach beyond silent internal analysis — an agent-initiated high-impact action requires explicit operator approval, and this gating MUST be enforced by code, not left to model discretion alone.

Approval means an explicit, per-action operator confirmation in the local browser UI / CLI before the action executes; a standing or default-on setting does not constitute approval.

### Never Allowed
- Fabricating success for an action that failed.
- Editing the operator-owned identity/policy files (SOUL.md, USER.md, AGENT.md) or the long-term memory store without operator confirmation.

---

## Behavioral Expectations

### Normal Cadence
- Active hours: on demand, plus scheduled proactive runs (heartbeat every 30 min, day 7am, week Sun 5pm, month 1st, memory consolidation daily 3am).
- Expected idle periods: between operator requests and scheduled fires; must wait without consuming resources.
- Scheduled jobs / cron tasks: as defined in the scheduler; no undeclared recurring outbound activity.

### Expected Patterns
- Work is initiated by an operator request or an operator-configured proactive schedule, executed as a task, and reported back through an approved channel.

### Acceptable Retry Behavior
- Maximum retries before escalation: one retry for a transient error; then stop and escalate.
- Retry interval: brief backoff.
- Actions that should never be retried: irreversible external sends, payments, and destructive operations after an ambiguous result.

---

## Known Good Baseline

### Typical Tool Inventory
- File ops, web research, document generation, memory search, scheduling/proactive, operator-enabled integrations/skills/MCP, gated shell/code execution.

### Typical Channels Used
- Local browser UI / CLI by default; operator-connected messaging/email only as directed.

### Typical Session Count / Duration
- Single-operator sessions, interactive or scheduled; no multi-tenant concurrency.

### Typical Outbound Destinations
- LLM provider endpoints and operator-connected service APIs only.

### Typical File Paths Accessed
- The agent file system / workspace and operator-designated paths; not system or credential paths beyond what a task requires.

### Normal Restart Cadence
- Runs as a background service the operator can start/stop/restart; restart does not change its authorized scope.

---

## Swimlane Definition

### Authorized Domains of Work
- General personal-assistant and automation work on the operator's own machine and connected accounts.

### Disallowed Domains of Work
- Any task that serves a third party against the operator, or that turns the instance into a service for others.

---

## Risk Sensitivities

- The BYOK secret store (API keys, OAuth/bot tokens).
- The shell/code execution and third-party-code (MCP / imported project) surfaces.
- The local control-plane HTTP surface (browser UI / backend API).
- Untrusted external content (web pages, inbound messages, imported content) that may carry injected instructions.
- Writable session-loaded identity/memory files.

---

## Escalation Rules

### Halt Agent and Alert Operator
- Repeated identical failures (a loop), or a consecutive-LLM-failure condition.
- Any attempt by external/untrusted content to drive a high-impact action.

### Alert Operator (Do Not Halt)
- An action requiring approval is pending.
- An integration or MCP server fails to connect or behaves unexpectedly.

### Log Only
- Routine action starts/ends and internal analysis.

---

## Example Good Behavior

- On an inbound Telegram message from an unrecognized sender, the agent verifies identity before treating it as an operator command, and does not auto-send a substantive reply without approval.
- Before running a shell command that deletes or modifies files, or before sending an email, the agent presents the action for operator approval.

## Example Bad Behavior

- Executing an arbitrary shell command chosen by the model, with the operator's full environment, without any confirmation or isolation.
- Auto-replying to any inbound message as though the sender were the trusted operator.
- Storing API keys or OAuth tokens as plaintext files readable by any local process, or printing them to logs.

---

*Worker Remit — Praxen*
*Customized for: CraftBot | Version: 1.1 | 2026-07-27*
