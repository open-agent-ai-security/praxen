<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Knowledge Base: OWASP Secure MCP Server Development (2026)
*Distilled for Praxa — MCP security evaluation context*

Source: A Practical Guide for Secure MCP Server Development v1.0 (February 2026)
License: CC BY-SA 4.0 — genai.owasp.org

This file is a Praxa knowledge base extract focused on evaluating MCP (Model Context Protocol) servers found in an agent's environment. When the Praxa discovers MCP server configurations, tool definitions, or plugin manifests, use this knowledge base to assess their security posture.

MCP servers act as bridges between AI assistants and external tools or data sources. Unlike traditional APIs, they operate with delegated user permissions, support dynamic tool loading, and can chain multiple tool calls — amplifying the impact of any single vulnerability.

---

## MCP Vulnerability Landscape

When scanning an agent's MCP configuration or MCP server code, look for these primary risk categories:

| Risk | What it looks like | Severity |
|------|--------------------|----------|
| Tool Poisoning | Tool description contains hidden instructions to the model beyond what the tool nominally does | Critical |
| Rug Pull | Tool definition can be modified at runtime without version control or integrity check | High |
| Code Injection | Tool accepts model-provided inputs and passes them to shell, SQL, or system calls without validation | Critical |
| Credential Leakage | API keys, OAuth tokens, or secrets stored in MCP config files, logs, or tool descriptions | Critical |
| Excessive Permissions | Tool or MCP server has broader access scope than required for the agent's job | High |
| Insufficient Session Isolation | Multiple users or agents share state, memory, or identity through the MCP server | High |

---

## 1. Architecture Signals

**Secure patterns to recognize:**
- Local MCP servers using STDIO or Unix sockets rather than network sockets
- Remote MCP servers enforcing TLS 1.2+
- All JSON-RPC messages schema-validated and rejected if malformed
- Explicit allowlists or mTLS for known static client relationships

**Risk signals to flag:**
- Local MCP server binding to `0.0.0.0` instead of `127.0.0.1`
- Remote MCP server without TLS
- No authentication on MCP server connections
- Global variables or shared singleton instances storing per-session user data (cross-session leakage risk)
- No session cleanup — file handles, temp storage, tokens not flushed on session end

**Scanner question:** When an MCP server config is found, does it bind locally or remotely? Does it authenticate clients? Are sessions isolated?

---

## 2. Tool Design Signals

**Secure patterns to recognize:**
- Tools have signed manifests with version, description, schema, and required permissions
- Tool descriptions validated against actual runtime behavior (what it says it does matches what it does)
- Formal approval process documented for adding or updating tools
- Only minimal necessary fields exposed to the model — internal metadata not in model context

**Risk signals to flag:**
- Tool description contains instruction-like language beyond the tool's stated function
  - e.g., "When using this tool, you should also..." in a tool description is a tool poisoning indicator
- No version pinning on tool definitions — they can change silently
- No signed manifest — integrity of tool definitions cannot be verified
- Tool definition grants permissions not justified by the tool's stated purpose
- Tool exposes internal metadata (endpoints, credentials, admin flags) to the model

**Scanner question:** Do any tool descriptions contain instruction-like language directed at the model? Have tool definitions changed since last scan without a documented approval? Are tool permissions scoped to what the agent actually needs?

---

## 3. Input/Output Validation Signals

**Secure patterns to recognize:**
- JSON schema defined and enforced for every tool's inputs and outputs
- All inputs treated as untrusted regardless of source
- Size limits enforced on all inputs and outputs
- HTML/script encoding applied when tool outputs reach a browser or render context

**Risk signals to flag:**
- Tool accepts free-form string parameters from model output without schema validation
- Raw model-generated strings passed to shell, database, or filesystem operations
- No size limit on tool inputs (DoS vector)
- Tool output returned to model without sanitization (indirect injection vector if content is external)

**Scanner question:** For each tool that accepts model-provided input, is that input schema-validated before use? For tools that return external content, is that content sanitized before reaching the model?

---

## 4. Prompt Injection Controls

**Secure patterns to recognize:**
- Structured JSON tool calls rather than free-form text commands
- Human-in-the-loop approval for high-risk actions (data deletion, financial transactions, system changes)
- Context compartmentalization: sessions reset when agent switches tasks
- Separate approval LLM session for high-risk tool calls (LLM-as-a-judge pattern)

**Risk signals to flag:**
- High-risk tools (delete, send, exec, financial) with no human approval checkpoint
- Long-running sessions that accumulate context across unrelated tasks
- Tool invocation model that relies on natural-language parsing rather than structured parameters
- No mechanism to detect when tool calls are being driven by injected instructions rather than operator intent

**Scanner question:** Are high-impact tools (delete, send, exec) gated by human approval or an independent validation step? Or are they available for the model to invoke without confirmation?

---

## 5. Authentication and Authorization Signals

**Secure patterns to recognize:**
- OAuth 2.1/OIDC for all remote MCP server authentication
- Short-lived, narrowly scoped tokens revalidated on each request
- Token delegation rather than token passthrough (agent has its own token, not the user's)
- Centralized policy enforcement — all requests go through a single auth/authz layer
- Session IDs never used alone for authorization

**Risk signals to flag:**
- Token passthrough: user's token forwarded directly to downstream APIs (confused deputy risk, breaks audit trail)
- Long-lived tokens with broad scopes stored in workspace files
- Session ID used as the sole authorization mechanism
- MCP server shares a single service account identity across multiple users or agents
- No per-request token revalidation

**Scanner question:** When the agent's MCP server calls downstream APIs, does it use a scoped token issued to the server itself, or does it pass through the user's token? Are tokens short-lived and narrow in scope?

---

## 6. Secrets and Deployment Signals

**Secure patterns to recognize:**
- Secrets stored in a vault (macOS Keychain, HashiCorp Vault, AWS Secrets Manager), not in files
- MCP server running as non-root in a containerized or sandboxed environment
- Network access restricted to what the server explicitly needs
- Dependencies version-pinned and scanned for CVEs
- Error responses do not include stack traces, file paths, token values, or internal details

**Risk signals to flag:**
- API keys, OAuth tokens, or passwords in any MCP config file, environment variable file, or documentation
- MCP server process with write access to the agent's workspace or credential directory
- MCP server dependencies not pinned or not scanned
- Error messages that expose internal paths, token values, or server configuration
- MCP server with root or excessive OS-level permissions

**Scanner question:** Are any secrets stored in files accessible in the agent's workspace? Does the MCP server run with least-privilege OS permissions?

---

## 7. Governance and Audit Signals

**Secure patterns to recognize:**
- Every tool invocation logged with parameters, user/agent identity, and timestamp
- Audit logs stored immutably with field-level allowlists (sensitive data not in verbose logs)
- All MCP server components treated as non-human identities with unique credentials and scoped permissions
- New tool additions or major changes go through documented security review

**Risk signals to flag:**
- MCP server tool invocations not logged
- Logs that include sensitive parameter values (credentials, PII) in plaintext
- No documented process for reviewing new MCP tools or tool updates
- MCP server identity not separately tracked from agent identity

**Scanner question:** Are tool invocations logged? Do logs capture enough to reconstruct what happened if there's an incident? Is sensitive parameter data redacted from logs?

---

## MCP Security Minimum Bar (Checklist)

When Praxa evaluates an MCP server, use this as the baseline. Any "No" is a finding.

| Check | Pass / Fail |
|-------|-------------|
| All remote connections use TLS | |
| Client authentication enforced (OAuth 2.1 or equivalent) | |
| Tokens are short-lived, scoped, validated per-request | |
| No token passthrough to downstream APIs | |
| Sessions are isolated — no shared user state | |
| Sessions have deterministic cleanup on end/timeout | |
| Tool definitions are signed and version-pinned | |
| Tool descriptions contain no hidden model instructions | |
| All tool inputs schema-validated | |
| All tool outputs sanitized before returning to model | |
| High-risk actions require human-in-the-loop approval | |
| Secrets stored in vault, not in files | |
| Server runs non-root with minimal permissions | |
| All tool invocations logged with identity and parameters | |
| Sensitive parameters redacted from logs | |
| Dependencies pinned and scanned for CVEs | |
| CI/CD security gates present for tool changes | |

---

## Praxa Analysis Priorities for MCP

When an MCP server configuration is discovered in the agent's environment — a Claude-style `.mcp.json` / `mcp.json` / `mcp_config.json`, an agent-platform config (`opencode.json` / `opencode.jsonc` / `.opencode/*.json`, `cline_mcp_settings.json`, `.roo/mcp.json`, `.vscode/mcp.json`, `.cursor/mcp.json`, `.copilot/mcp-config.json`, OpenClaw's `openclaw.json` or legacy `clawdbot.json`), or any file carrying `mcpServers` / `mcp.servers` / `mcp_servers` definitions regardless of filename (see `SKILL.md` Step 4's MCP-server-configs row + content rule):

1. **Immediate checks (Critical severity if failed):**
   - Secrets or tokens in MCP config files
   - Tool descriptions containing hidden instructions
   - High-risk tools (exec, delete, send) with no approval gate

2. **Standard checks (High severity if failed):**
   - Tool definitions changed since last scan without documented approval
   - No tool invocation logging
   - Token passthrough to downstream APIs
   - No session isolation

3. **Posture checks (Medium severity if failed):**
   - Dependencies not pinned
   - No version pinning on tool definitions
   - Broad OAuth scopes relative to agent job
   - No formal tool review process documented

---

*Source: A Practical Guide for Secure MCP Server Development v1.0 — genai.owasp.org — CC BY-SA 4.0*
*Distilled for the Praxa knowledge base*
