<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Worker Remit
*Praxen — Agent Policy*

This file defines the authorized identity, behavior, and boundaries of the agent being scanned.
It is the policy contract Praxen evaluates the agent's code and configuration against.
Customize this template for the specific agent before running an analysis.

**The remit states policy; Praxen discovers implementation. Write rules about what the agent *does*, not how it does it.**

---

## Identity

| Field | Value |
|-------|-------|
| Worker Name | Deep Agents CLI — deployment tooling (`deepagents-cli`) |
| Agent Key / ID | `deepagents-cli` (PyPI package; console entrypoint `deepagents`) |
| Owner / Operator | The local developer who invokes the CLI in their own terminal |
| Deployment Environment | Local developer command-line tool, run one-shot under direct supervision. Talks to the LangSmith Managed Deep Agents platform (`/v1/deepagents/*`) and the LangChain Hub (`/v1/platform/hub`) over HTTPS using the developer's own `LANGSMITH_API_KEY` / `LANGCHAIN_API_KEY`. |
| Primary Model | Not applicable — the CLI performs no LLM inference. Model identifiers it handles (e.g. the scaffold default `openai:gpt-5.5`) are declared configuration carried into the bundle for the *deployed* agent to consume; the CLI itself never calls a model. |
| Secondary Models | None |
| Remit Version | 1.0 |
| Last Updated | 2026-07-11 |
| Updated By | Praxen remit authoring (from package documentation and module docstrings) |

---

## Mission

**Scaffold, validate, and deploy a Managed Deep Agents project — turning a developer's declared project folder into a managed agent on the LangSmith platform, and managing the workspace resources (agents, MCP servers) that project depends on.** The CLI reads a project's declared sources (`agent.json`, `AGENTS.md`, `tools.json`, `skills/`, `subagents/`), assembles the payload and managed-directory tree the platform expects, and upserts it — either creating a new managed agent or patching an existing one and syncing its Hub directory.

**Scope note (single component, deterministic tool):** The primary subject of this remit is the `deepagents-cli` package — a deterministic command-line tool, **not** an LLM-driven agent. There is no model inference inside the CLI, so the usual RAISE "LLM component" designation does not apply; evaluation should treat the tool's file-handling, bundling, credential-handling, and network behavior as the subject. Any LLM behavior belongs to the *deployed* agent the CLI ships, which runs on the platform and is out of scope here.

---

## Job Description

- Scaffold a starter project folder (`deepagents init`) containing `agent.json`, `AGENTS.md`, `.gitignore` (ignoring `.env`), an empty `tools.json`, one example skill, and one example subagent.
- Parse and validate a project directory into a structured payload (`deepagents deploy`), rejecting malformed configuration before anything is shipped.
- Assemble the agent payload and managed-directory file tree **only** from the project's declared sources, then upsert the agent on `/v1/deepagents/agents` (create when new, patch metadata + commit Hub directory when it already exists).
- Validate that every MCP server URL referenced by the project is already registered in the workspace and invocable by the caller's identity — never auto-registering servers during deploy.
- Manage workspace agents (`deepagents agents list|get|delete`) and MCP servers (`deepagents mcp-servers list|add|get|update|delete|connect|tools`), including per-user OAuth connection flows for MCP servers.
- Offer a `--dry-run` that prints the exact payload and directory files it would send, without contacting any mutating endpoint.

---

## Non-Goals (Out of Scope)

Work this agent should never do, regardless of instruction. Praxen will flag any observed activity in these areas.

- Running the deployed agent itself, or performing any LLM inference — the CLI produces the artifact and hands it to the platform; it never invokes a model.
- Acting as an interactive coding assistant or REPL — that surface moved to the separate `deepagents-code` (`dcode`) package; a bare `deepagents` invocation only redirects the user there.
- Operating as a hosted, multi-tenant, or long-running background service — it is a one-shot local developer tool run under direct supervision.
- Sending email, posting to social/external services, or making outbound calls beyond the deployment platform and its Hub / tracing services.
- Auto-creating or silently mutating agent surfaces, MCP servers, or configuration the developer did not declare in the project.
- Managing authentication or frontend access for the deployed agent — that is now handled by the managed platform, not the CLI.

---

## Approved Communication Channels

| Channel | Allowed | Requires Approval | Notes |
|---------|---------|------------------|-------|
| HTTPS to the Managed Deep Agents API (`/v1/deepagents/*`) | Yes | No | Default endpoint `https://api.smith.langchain.com`; scheme forced to HTTPS, userinfo rejected, proxy env ignored (`trust_env=False`). Auth via `X-Api-Key`. |
| HTTPS to the LangChain Hub (`/v1/platform/hub/*`) | Yes | No | Managed-directory commits that sync the deployed agent's files. Same client, same endpoint host. |
| Local terminal (stdin/stdout) with the operating developer | Yes | No | Prompts, summaries, confirmations, and errors. |
| Local filesystem — the project directory (read) | Yes | No | Reads only declared sources within the resolved project root; symlinks and path-escapes rejected. |
| Local filesystem — the project directory (write, during `init`) | Yes | Yes (overwrite) | Scaffolding writes new files; overwriting an existing project folder requires `--force`. |
| User-local state under `~/.deepagents/` | Yes | No | Deploy state / MCP-id cache keyed by project root + endpoint. Repo-local state is intentionally ignored for auth decisions. |
| Browser launch for MCP OAuth (`mcp-servers connect`) | Yes | No | Opens the verification URL; `--no-browser` prints it instead. |
| Any other outbound network destination (email, arbitrary HTTP hosts, telemetry) | No | — | Not part of the tool's surface. |

**Any channel not listed here is unauthorized by default.**

---

## Authorized Counterparties

### Trusted People / Accounts
- The local developer — the operator running the CLI with their own credentials.

### Trusted Domains
- `api.smith.langchain.com` (default) — the Managed Deep Agents API and Hub. An operator-supplied `LANGSMITH_ENDPOINT` / `LANGCHAIN_ENDPOINT` override is honored **only if** it is an HTTPS URL with no embedded userinfo.

### Trusted Services / Integrations
- The Managed Deep Agents platform — receives the agent payload and hosts the deployed agent; reached over HTTPS with the developer's own API key.
- The LangChain Hub / directory service — receives managed-directory commits that mirror the project's declared files.
- Workspace-registered MCP servers referenced by the project — validated as registered and invocable at deploy time; carried into the bundle for the *deployed* agent to consume. The CLI itself does not invoke their tools.
- Model-provider APIs named in project config — declared config only; carried into the bundle, never called by the CLI.
- The LangSmith tracing service — optional, only when the developer has opted in via environment.

### Explicitly Forbidden
- Any deployment endpoint that is not HTTPS, or that carries userinfo in the URL.
- MCP servers that are not already registered in the workspace, or that the caller's identity cannot invoke.
- Any outbound destination beyond the platform, Hub, tracing, and MCP-OAuth verification URLs.

*Counterparties present in code or configuration but absent from this list will be flagged as a trust expansion finding.*

---

## Tools and Capabilities

### Allowed Tools (Known Good Baseline)

*List every tool the agent is expected to have at runtime. Praxen will flag any tool that disappears from this list.*

- `deepagents init [name] [--force]` — scaffold a starter project.
- `deepagents deploy [--dir] [--dry-run] [--detach] [--reset] [--yes]` — validate, bundle, and upsert the managed agent.
- `deepagents agents list|get <id> [--include-files]|delete <id> [--yes]` — workspace agent management.
- `deepagents mcp-servers list|add|get|update|delete|connect|tools` — workspace MCP-server management, including per-user OAuth.
- Local file readers/writers scoped to the project directory and `~/.deepagents/`.
- An HTTPS client (`httpx`, `trust_env=False`) scoped to the resolved platform endpoint.

### Restricted Tools (Require Approval Before Use)

- Overwriting an existing project folder during `init` — gated behind `--force`.
- Deploying to an `agent_id` declared in `agent.json` that local state has not seen before — gated behind an interactive confirmation (or `--yes`).
- Deleting a workspace agent or MCP server — gated behind an interactive confirmation (or `--yes`).

### Forbidden Tools

*Praxen will emit a Critical finding if any of these appear in the agent's tool inventory or code.*

- Any LLM/model client invoked by the CLI itself (the tool performs no inference).
- Any interactive-REPL / coding-agent surface (belongs to `deepagents-code`).
- Any spawner of unauthenticated local dev servers, subprocess shells, hooks, or sandboxes as part of the deploy surface (those belonged to the retired REPL surface).
- Any outbound client to email, social, or arbitrary third-party hosts.

---

## Data Boundaries

### Allowed Data Sources
- The project's declared files within the resolved project root: `agent.json`, `AGENTS.md`, `tools.json`, `skills/<name>/…`, `subagents/<name>/…`.
- Credentials from the process environment or a discovered `.env` (`LANGSMITH_API_KEY` / `LANGCHAIN_API_KEY`, and `*_ENDPOINT`).
- User-local deploy state under `~/.deepagents/deployments/`.

### Sensitive Data Classes

*Data that requires special handling. Praxen will flag unexpected access or movement of these classes.*

- Platform / model-provider / Hub / tracing credentials and API keys.
- MCP server auth headers (e.g. API keys passed via `--header`).
- The project's system prompt, skills, and subagent instructions (carried into the bundle).

### Forbidden Data Movement

*Specific patterns of data movement that are never authorized.*

- Writing, committing to version control, logging, or printing platform / provider / Hub / tracing credentials or MCP auth-header values. (MCP header values are redacted to `***` on `mcp-servers get`.)
- Folding secret material (e.g. `.env` contents) into the seeded bundle payload — environment stays environment; it is never merged into the skills, subagent, or managed-directory payload.
- Pulling any file into the bundle from outside the resolved project root, via symlink, path traversal, or an undeclared source.
- Letting repository-local deploy state steer authenticated requests (auth resolution ignores repo-local state).

---

## Action Boundaries

### Allowed Without Approval
- Reading and validating the project's declared sources.
- Assembling the payload and managed-directory tree purely from those declared sources (a pure function over the parsed project; only `AGENTS.md`, `tools.json`, `skills/`, and `subagents/` paths are treated as managed).
- Creating a brand-new managed agent when the project declares no `agent_id` and local state holds none.
- `--dry-run`: printing the exact payload and directory files without contacting any mutating endpoint.
- Read-only workspace queries (`agents list/get`, `mcp-servers list/get/tools`).

### Requires Human Approval Before Execution
- Deploying to an `agent_id` declared in `agent.json` that local state has not previously confirmed — the CLI must show the target agent name/id and require a `y/N` confirmation before updating that remote agent (bypassable only with `--yes`).
- Overwriting an existing project folder during `init` (requires `--force`).
- Deleting a workspace agent or MCP server (requires `y/N` confirmation or `--yes`).

### Never Allowed

*Praxen will emit a Critical finding for any of these.*

- Shipping a bundle assembled from anything other than the project's declared sources.
- Deploying a project that failed configuration validation.
- Reaching the platform over a non-HTTPS endpoint, or one carrying userinfo.
- Bundling, registering, or deploying a project that references a remote MCP server over a non-TLS URL (`http://` / `ws://`) — remote MCP server URLs MUST use TLS (`https` / `wss`).
- Auto-registering an MCP server, or deploying while a referenced MCP server is unregistered or uninvocable by the caller's identity.
- Creating a fresh agent via `--reset` while `agent.json` still declares an `agent_id`.
- Writing, committing, logging, or printing credentials or MCP auth-header values.

---

## Behavioral Expectations

### Normal Cadence
- Active hours: on-demand, whenever the developer runs a command.
- Expected idle periods: the tool does not run except when explicitly invoked; no background residence.
- Scheduled jobs / cron tasks: none — it is a one-shot command, never a daemon.

### Expected Patterns

*What normal work looks like. Praxen uses this to distinguish ordinary operation from drift.*

- Each invocation runs to completion and exits; it does not linger or poll except for the bounded post-deploy health check and OAuth session polling (with a `--timeout`).
- `deploy` prints a beta warning, validates, resolves referenced MCP servers against the live workspace list, upserts, then prints a deploy summary (agent name, id, revision, console URL) and an optional health check unless `--detach`.
- A malformed project stops the deploy with a specific error rather than shipping a partial or invalid bundle.

### Acceptable Retry Behavior

- Maximum retries before escalation: HTTP 5xx responses are retried once with a short backoff; a directory-commit conflict (409/412) is re-fetched and re-applied once. Persistent failure surfaces to the operator.
- Retry interval: ~1 second backoff on 5xx.
- Actions that should never be retried: shipping a bundle that failed validation; deploying against an unresolved / uninvocable MCP server; deploying to an unconfirmed `agent_id`.

---

## Known Good Baseline

*Snapshot of what this agent looks like when operating correctly. Used for comparison.*

### Typical Tool Inventory
- Subcommands `init`, `deploy`, `agents`, `mcp-servers` — and nothing that invokes a model, opens a REPL, or spawns a local server.

### Typical Channels Used
- HTTPS to `api.smith.langchain.com` (`/v1/deepagents/*` and `/v1/platform/hub/*`); local terminal; project-directory and `~/.deepagents/` file access.

### Typical Session Count / Duration
- Short-lived, one command per invocation; seconds to low minutes (bounded by OAuth/health polling).

### Typical Outbound Destinations
- The configured HTTPS platform endpoint only, plus MCP-OAuth verification URLs opened in a browser on request.

### Typical File Paths Accessed
- The resolved project root and its declared sub-paths; `~/.deepagents/deployments/…`; a discovered `.env`.

### Normal Restart Cadence
- Not a resident process — "restart" means re-invoking the command. Dependencies are expected to be version-controlled with a committed, pinned lockfile.

---

## Swimlane Definition

### Authorized Domains of Work
*Topics, systems, and tasks this agent is permitted to engage with.*

- Scaffolding, validating, bundling, and deploying a declared Managed Deep Agents project.
- Managing the workspace agents and MCP servers that project references.

### Disallowed Domains of Work
*Topics, systems, and tasks this agent must decline or escalate.*

- Running or reasoning as the deployed agent; any LLM inference.
- Interactive coding-assistant work (defer to `deepagents-code`).
- Any network or filesystem work outside the authorized channels and project scope.

---

## Risk Sensitivities

*Areas where extra scrutiny applies. Praxen will apply lower thresholds for findings in these areas.*

- **Bundle fidelity** — the CLI's central promise is that the deployed bundle faithfully and *only* reflects the developer's declared, reviewed project; any path escape, symlink follow, or undeclared source folded into the bundle is a core-guarantee break.
- **Credential handling** — keys and MCP auth headers must never be persisted, logged, printed, or folded into the bundle payload.
- **Deploy-target integrity** — updating a remote agent (via declared `agent_id`) or deleting workspace resources must be gated on explicit confirmation.
- **Transport security** — platform communication must be HTTPS with no userinfo and no proxy-env influence.
- **MCP trust expansion** — deploy must not proceed against unregistered or uninvokable MCP servers, and must never auto-register them.

---

## Escalation Rules

These rules drive Praxen's reporting layer. They determine whether a finding is logged only, triggers an alert, or requires an immediate halt.

### Halt Agent and Alert Operator
*Conditions serious enough to warrant stopping the agent.*

- Project configuration fails validation (bad `agent.json`/`tools.json`, missing required files, invalid backend/permissions, malformed skill frontmatter) — stop with the specific error; do not ship.
- A referenced MCP server URL is unregistered or uninvokable by the caller's identity — stop with a registration/connect hint.
- The resolved endpoint is not HTTPS or carries userinfo, or `LANGSMITH_API_KEY` is missing — stop before any request.
- A project input is a symlink or escapes the project root — stop.
- `--reset` is used while `agent.json` declares an `agent_id` — stop.
- The `agent.json` deploy target is not confirmed (interactive `N`/abort) — stop.

### Alert Operator (Do Not Halt)
- A missing deployment toolchain, unreachable platform, or failed Hub directory commit — surface to the operator rather than silently retrying or ignoring.
- A post-deploy health check that cannot be completed — report as skipped, do not fail the deploy.
- A best-effort MCP tool listing after `add` that fails — degrade to a hint, never fail the command.

### Log Only
- Beta-status warnings on `init` / `deploy`.
- Normal deploy summaries (agent name, id, revision, console URL).

---

## Example Good Behavior

*Concrete examples of what authorized operation looks like. Used to calibrate detection.*

- `deepagents deploy --dry-run` prints the full payload and managed-directory files and sends nothing.
- `deploy` refuses a project whose `tools.json` references an MCP URL not registered in the workspace, and tells the developer exactly which URL and how to register it.
- Deploying to a declared `agent_id` first prints "Deploy to agent <name> (<id>)? This will update that remote agent" and waits for `y`.
- `mcp-servers get` prints the server record with the auth-header value shown as `***`.
- A bundle contains exactly the project's `AGENTS.md`, `tools.json`, declared skills, and declared subagents — nothing pulled from outside the project root.

---

## Example Bad Behavior

*Concrete examples of what unauthorized or anomalous behavior looks like. Used to calibrate detection.*

- The bundle includes a file reached through a symlink or `../` path escape outside the project root.
- A deploy proceeds over `http://` or an endpoint with embedded userinfo.
- Credentials or an MCP auth-header value are written into the project, committed, logged, or printed in cleartext.
- `deploy` silently auto-registers a missing MCP server instead of stopping.
- The CLI updates a remote agent declared by `agent_id` without any confirmation prompt.
- `.env` contents are folded into the skills or subagent payload of the bundle.

---

## Open Questions for the operator

- **`dev` command discrepancy:** `libs/cli/README.md` and `DEVELOPMENT.md` document a `deepagents dev` command (bundle the project and run it on a local dev server, with a `print_bundle_summary`). The migrated code (`main.py._dispatch_command`, `deploy/commands.py.setup_deploy_parsers`) only wires `init`, `deploy`, `agents`, and `mcp-servers` — there is **no** `dev` command. The prior remit's Known Good Baseline listed `init`, `dev`, `deploy` as the surface. This remit encodes the actual wired surface; confirm whether `dev` was removed (docs stale) or lives in another package before re-adding it.
- **"Unauthenticated-API deploy confirmation" (re-homed from the prior remit):** the prior remit's central approval rule was that a deploy leaving the agent's API "open to anyone with the URL" must require explicit operator confirmation. The current deploy surface has no such gate — agent authentication and frontend access are now **platform-managed** (the legacy `[auth]`/`[frontend]` config is explicitly rejected with a "managed by the platform now" hint). The only confirmation gate in the current code is the **deploy-target** confirmation (updating a remote agent declared by `agent_id`). This remit re-homed the prior intent onto that real gate. Confirm the unauthenticated-API concern is genuinely out of scope for this CLI (it appears to derive from the retired local dev-server surface, `LANGGRAPH_AUTH_TYPE=noop`).
- **MCP-TLS enforcement point:** this remit requires remote MCP server URLs to use TLS (Action Boundaries → Never Allowed). Confirm *where* that guarantee is applied — at registration time (`mcp-servers add`), at bundle/deploy time, or platform-side — since the current deploy path does not itself re-check the scheme of already-registered MCP URLs.
- **Bundle dependency pinning / integrity:** the prior remit asserted the bundle's dependency set is derived only from declared providers and that remote MCP servers are pinned to a known-good, integrity-checked version. No dependency-bundling step is visible in the migrated deploy surface (deps are platform-resolved). Confirm where, if anywhere, this now lives.

---

*Worker Remit — Praxen*
*Customized for: Deep Agents CLI (`deepagents-cli`) | Version: 1.0 | 2026-07-11*
