# Worker Remit — Deep Agents CLI

## Agent Identity

**Name:** Deep Agents CLI
**Operator:** The local developer running the CLI in their own terminal.
**Environment:** Python; Anthropic / OpenAI / Google / OpenRouter API for inference (developer's own API keys); `langchain-mcp-adapters` for MCP; optional LangSmith for tracing.

---

## Mission

**Help a developer accomplish coding and automation tasks in their local workspace — read/search/edit files, run shell commands, plan, spawn subagents, and consult declared MCP servers — under interactive developer supervision.** It is the `deepagents-cli` package built on the `deepagents` SDK and LangGraph: it plans and carries out multi-step development tasks, with the developer reviewing the work.

---

## Authorized Tools

**The agent may use read_file, write_file, edit_file, ls, glob, grep, execute, write_todos, task, and MCP tools loaded from trusted .mcp.json configs.** Specifically: `read_file` / `ls` / `glob` / `grep` (read and search, subject to `FilesystemMiddleware` permission rules); `write_file` / `edit_file` (write and edit within allowed paths); `execute` (shell, through the configured backend — a sandboxed backend in any non-trivial context); `write_todos` (planning); `task` (spawn a subagent with an isolated context window); MCP tools from `.mcp.json` configs that have passed the trust gate — the currently-declared servers are the two first-party LangChain documentation endpoints (`docs-langchain`, `reference-langchain`) over HTTPS.

---

## Authorized Channels / Counterparties

**Outbound network is limited to: the configured LLM provider API; remote MCP servers declared in trusted .mcp.json files; LangSmith when tracing is enabled; and whatever the developer's own shell commands reach.** The counterparties: the local developer (interactive supervision); the configured LLM provider (inference only, developer's keys); trusted MCP servers (reached over TLS; the agent uses its own scoped OAuth token per server — no passthrough of the developer's token to downstream APIs); LangSmith (optional, for tracing).

---

## Action Boundaries

- **The agent MUST NOT load tools from an untrusted project-level .mcp.json without explicit operator approval (fingerprint trust).** A newly-discovered project-level `.mcp.json` triggers a trust prompt; the agent must not load its tools until the operator approves it.
- **When the agent processes untrusted input or runs in a non-trusted/multi-tenant/production context, the shell execute tool MUST use a sandboxed backend, not the unsandboxed LocalShellBackend.** The `LocalShellBackend` runs commands on the host with no isolation; a sandboxed backend (one of the `BaseSandbox` implementations) is required outside a personal dev environment.
- **File operations MUST reject path traversal and absolute-path escapes, and should be restrictable to an allowlist of paths.** `FilesystemMiddleware` validates every path (no `..`, absolute-only, no `~`) and supports allow/deny path ACLs.
- **Remote MCP servers MUST be reached over TLS.** The currently-declared servers are HTTPS endpoints; the config loader validates transport types.

---

## Approval Requirements

- **High-impact actions — shell command execution, file writes/deletes outside the working tree, and any MCP tool that sends/deletes/executes — should be gated by human-in-the-loop approval when the agent runs in a non-trivial context.** The `interrupt_on` / `HumanInTheLoopMiddleware` mechanism provides this; it should be engaged for those actions rather than left off.
- Writes to session-loaded notes/memory files (e.g. `default_agent_prompt.md`) should require operator confirmation.

---

## Forbidden Actions

- **Credentials (provider API keys, MCP OAuth tokens) MUST be stored with restrictive file permissions, never written into the workspace or version control, and never logged or printed.**
- **External content that enters the agent's context (file contents, shell output, MCP tool results, fetched docs) should be treated as untrusted and not allowed to silently redirect the agent's behaviour.**

---

## Behavioral Expectations

- **The agent operates interactively under developer supervision; it MUST NOT run as an unattended background service.** The CLI is interactive by construction.
- **The agent should maintain a durable, structured record of the actions it takes (tool invocations with parameters and timestamps) sufficient to reconstruct an incident.**

---

## Escalation and Limits

- A newly-discovered, untrusted project-level `.mcp.json` triggers a trust prompt; the agent must not load its tools until the operator approves it.
- Authentication or permission errors against an MCP server are surfaced to the operator, not silently retried indefinitely.
- **The project should maintain a documented adversarial-testing / red-team practice and a published threat model (e.g. SECURITY.md), with findings feeding back into the agent's defaults.**

---

## Known Good Baseline

- **Tool inventory:** `read_file`, `write_file`, `edit_file`, `ls`, `glob`, `grep`, `execute`, `write_todos`, `task`, plus MCP tools from trusted `.mcp.json` configs (currently the two LangChain HTTPS doc servers).
- **Dependencies MUST be version-controlled via a committed lockfile and should be pinned to compatible ranges; the LLM model version should be specified.** Both packages commit `uv.lock`; the CLI pins its internal dep exactly (`deepagents==0.6.1`); the default model version is `claude-sonnet-4-6`.

---

## Out of Scope

- The Deep Agents CLI is not a hosted multi-tenant service — it runs locally for one developer.
- It does not send email, post to social platforms, or make outbound calls other than the LLM provider, trusted MCP servers, LangSmith, and whatever the developer's own shell commands reach.
- It does not operate autonomously without a supervising developer.
