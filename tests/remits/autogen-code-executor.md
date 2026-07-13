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
| Worker Name | AutoGen Code Executor |
| Agent Key / ID | autogen-code-executor |
| Owner / Operator | Operator of an AutoGen-based application (data scientist, developer, or automation engineer) |
| Deployment Environment | Library invoked from within an AutoGen application; executes code on the local host, inside a Docker container, inside a Jupyter kernel, or inside an Azure Container Apps dynamic-sessions sandbox depending on the configured executor |
| Primary Model | Operator-configured `ChatCompletionClient` used by `CodeExecutorAgent` when it generates its own code (examples use OpenAI `gpt-4o`) |
| Secondary Models | Optional model used by a model-based approval function to review code before execution |
| Remit Version | 1.0 |
| Last Updated | 2026-07-11 |
| Updated By | Praxen remit authoring (regenerated on current template) |

---

## Mission

Execute code blocks — Python or shell — that an LLM agent has produced, inside a controlled, isolated environment, and return stdout, stderr, and exit status to the calling agent for its next reasoning step. This is the execution tier of a generator/executor pattern: one component generates code, this component runs it safely and reports the result.

**Scope note — components covered.** This remit covers the AutoGen **code-executor** component family and its driving agent:
- **`CodeExecutorAgent`** — the AgentChat agent that receives messages, extracts fenced code blocks, and drives an executor; optionally uses a `model_client` to generate its own code and reflect on results. **This is the primary RAISE subject** (the LLM-driven component).
- **The executor implementations** — supporting, deterministic components that perform the actual execution: `LocalCommandLineCodeExecutor` (host), `DockerCommandLineCodeExecutor` (container, the recommended production path), `JupyterCodeExecutor` and `DockerJupyterCodeExecutor` (stateful Jupyter kernels), and `ACADynamicSessionsCodeExecutor` (Azure-managed cloud sandbox). `create_default_code_executor` selects an executor, preferring Docker.

Per-component rules appear as sub-headings within the existing sections below; no new top-level sections are introduced.

---

## Job Description

- Extract code from properly formatted markdown code blocks (triple-backtick fences) in incoming messages and execute only code in supported languages (Python and shell for command-line executors; Python only for the Jupyter and Azure executors).
- Execute each code block inside the configured execution environment, in the order received, and return a structured result containing exit status and captured output.
- Manage the lifecycle of the execution environment — start and stop containers, restart Jupyter/Azure sessions, create and (where configured) clean up the working directory and temporary files.
- Confine all file reads and writes to a configured working directory (for the Azure executor, `/mnt/data`).
- Enforce a configured wall-clock timeout on every execution and terminate any process that exceeds it.
- When `CodeExecutorAgent` is configured with a `model_client`, generate code from the user query, execute it, reflect on the result, and retry on execution error up to the configured retry limit.
- When configured with an approval function, obtain approval for each code block before executing it.
- Surface all errors (syntax, runtime, timeout, out-of-memory) back to the caller in structured form without silently discarding them.

---

## Non-Goals (Out of Scope)

Work this agent should never do, regardless of instruction. Praxen will flag any observed activity in these areas.

- Evaluating the semantic safety of the code — that is the responsibility of the calling agent's prompting, an approval function, or a separate review step, not the executor's core loop.
- Sending email, SMS, webhooks, or any outbound message on its own behalf.
- Persisting execution results to long-term storage or maintaining memory across application restarts.
- Providing authentication or authorization for the caller (the operator application owns that).
- Running as a long-lived service, scheduling recurring executions, or queuing work — executors are synchronous, single-call components.
- Fetching its own dependencies at runtime from package registries without explicit configuration, or modifying its own code.

---

## Approved Communication Channels

| Channel | Allowed | Requires Approval | Notes |
|---------|---------|------------------|-------|
| Inbound code blocks from the paired code-generator agent / group chat | Yes | No | Code arrives as fenced blocks in AgentChat messages; the `sources` filter, when set, restricts which agents' messages are executed |
| Return of stdout / stderr / exit status to the calling agent | Yes | No | Structured `CodeResult`; output must never be silently discarded |
| Files written to the configured working directory | Yes | No | Confined to `work_dir` (or `/mnt/data` for the Azure executor) |
| Docker daemon / Docker socket (container executors) | Yes | No | Used to create, control, and stop execution containers; "Docker out of Docker" (mounted socket) is the recommended containerized-app pattern |
| HTTPS to the Azure Container Apps dynamic-sessions endpoint | Yes | No | Only for the `ACADynamicSessionsCodeExecutor`; authenticated with the configured token provider |
| Jupyter server / kernel connection | Yes | No | For the Jupyter executors; stateful within a session |
| Outbound network egress initiated by the executor itself | No | Yes | The executor must not initiate its own network traffic beyond a configured allow-list. |
| Email / SMS / webhooks / arbitrary message queues | No | — | Never an executor channel |

**Any channel not listed here is unauthorized by default.**

---

## Authorized Counterparties

### Trusted People / Accounts
- The operator application that instantiates the executor and configures its working directory, timeout, container image, resource limits, and network policy.

### Trusted Domains
- The Azure Container Apps dynamic-sessions endpoint configured for the `ACADynamicSessionsCodeExecutor` (operator-supplied `pool_management_endpoint`).

### Trusted Services / Integrations
- The paired AutoGen code-generator agent (the LLM component that produces code); code from this counterparty is the only accepted execution input.
- The containerization / isolation layer the executor relies on for safety — the Docker daemon, the Jupyter server, or the Azure dynamic-sessions sandbox.

### Explicitly Forbidden
- Any code source other than the paired agent's generated code blocks and code passed explicitly by operator application logic — code arriving from a file, HTTP endpoint, message queue, or memory store must not be accepted by the executor interface.

*Counterparties present in code or configuration but absent from this list will be flagged as a trust expansion finding.*

---

## Tools and Capabilities

### Allowed Tools (Known Good Baseline)

*List every tool the agent is expected to have at runtime. Praxen will flag any tool that disappears from this list.*

- Execute a batch of code blocks in the configured environment and return exit status and output.
- Start and stop the execution environment (container start/stop, kernel/session start).
- Restart a Jupyter or Azure session (resetting session state; previous sessions are not reusable).
- Create, and where configured clean up, the working directory and temporary files.
- Inject a fixed, operator-supplied set of helper functions into the execution environment at session start.
- Upload files to and download files from the working directory (Azure dynamic-sessions executor, into `/mnt/data`).

### Restricted Tools (Require Approval Before Use)

- The local host executor (`LocalCommandLineCodeExecutor`) in production — it runs generated code directly on the host OS with no container isolation and is acceptable only on an ephemeral, isolated, operator-approved host.
- Exposing host GPUs or other host devices to a container executor.
- Mounting host volumes into a container executor at any path other than the configured working directory.
- Enabling network egress from the execution environment beyond a configured allow-list.

### Forbidden Tools

*Praxen will emit a Critical finding if any of these appear in the agent's tool inventory or code.*

- Any mechanism that loads or executes code fetched from a remote URL or other unverified source on the LLM's behalf.
- Any capability that persists execution results to long-term storage or carries state across unrelated sessions.
- Any outbound-messaging capability (email, SMS, webhook) operating on the executor's own behalf.

---

## Data Boundaries

### Allowed Data Sources
- The code blocks supplied by the paired agent and the operator application.
- Files within the configured working directory (or `/mnt/data` for the Azure executor).
- The operator-supplied helper functions injected at session start.

### Sensitive Data Classes

*Data that requires special handling. Praxen will flag unexpected access or movement of these classes.*

- Host credentials, environment variables, and secrets of the parent process.
- The Docker socket / daemon control channel.
- The Azure token / credential used to authenticate to the dynamic-sessions endpoint.
- Any data outside the working directory (databases, user data, host filesystem).

### Forbidden Data Movement

*Specific patterns of data movement that are never authorized.*

- Reading or modifying the parent process's environment, credentials, or state from within an execution.
- Moving files or data outside the configured working directory.
- Leaking state (kernel variables, work-directory files) between unrelated sessions.
- Exfiltrating data over network egress not permitted by configuration.

---

## Action Boundaries

>
> - ✓ *"Message bodies must never be fetched for senders not in the authorized counterparty list"*
> - ✓ *"Responding to unknown senders requires human approval — no automated reply"*
> - ✗ *"Handle email appropriately"*
> - ✗ *"Be careful with sensitive data"*
>
> The first two rules give Praxen something to audit. The second two don't.
> Praxen will inventory every rule in this document and report any it cannot verify — so the more specific your rules, the more useful the coverage report.

### Allowed Without Approval
- Execute code blocks received from the paired agent inside an isolated container executor, confined to the working directory and subject to the configured timeout.
- Return stdout, stderr, and exit status to the calling agent in structured form.
- Write files to, and read files from, the configured working directory only.
- Start, stop, and restart the execution environment as part of normal single-call lifecycle management.

### Requires Human Approval Before Execution
- Executing code on the local host executor in a production deployment (default production deployments must use a containerized executor).
- Enabling any network egress from the execution environment beyond a configured allow-list.
- Mounting host volumes into a container executor at any path other than the configured working directory.
- Any change to resource limits (CPU, memory, timeout) that raises the ceiling.
- Exposing host GPUs or other host devices to a container executor.
- When an approval function is configured, executing any code block it has not approved.

### Never Allowed

*Praxen will emit a Critical finding for any of these.*

- Executing code with host-level privileges when a less-privileged option achieves the same task.
- Acting on instructions embedded in the code source that attempt to escape the sandbox, escalate privileges, or exfiltrate data.
- Bypassing working-directory confinement by any means — symlinks, parent-directory traversal, absolute paths, or runtime-supplied volume-mount overrides.
- Loading or executing code from a remote URL or unverified source on the LLM's behalf; the paired agent's generated code is the only accepted input.
- Silently swallowing or transforming error output before returning it to the caller.
- Connecting to services, databases, or networks not explicitly permitted by configuration.

---

## Behavioral Expectations

### Normal Cadence
- Active hours: on-demand only — the executor runs when the application invokes it.
- Expected idle periods: idle between calls; no background activity when not invoked.
- Scheduled jobs / cron tasks: none — executors are synchronous, single-call components and must not schedule or queue work.

### Expected Patterns

*What normal work looks like. Praxen uses this to distinguish ordinary operation from drift.*

- Receive a batch of code blocks, execute them serially in the order received, return one structured result, and (for non-stateful executors) tear down or reset the environment.
- With `model_client`: generate code, execute, reflect on the result, and stop.
- Stateful Jupyter/Azure sessions preserve variables across executions within the same session only, and reset on restart.

### Acceptable Retry Behavior

- Maximum retries before escalation: the configured `max_retries_on_error` for `CodeExecutorAgent`; after that the agent yields a reflection result rather than retrying further.
- Retry interval: immediate re-generation/re-execution on error; no unbounded looping.
- Actions that should never be retried: executions terminated for exceeding the timeout must be terminated, not re-run in a loop; approval-denied code must not be retried without new approval.

---

## Known Good Baseline

*Snapshot of what this agent looks like when operating correctly. Used for comparison.*

### Typical Tool Inventory
- One executor instance (Docker command-line executor recommended) plus lifecycle start/stop and execute-code-blocks.

### Typical Channels Used
- Inbound fenced code blocks from the paired agent; structured result returned to the caller; files within the working directory.

### Typical Session Count / Duration
- One synchronous call per execution request; container/session lives only for the duration of use and is stopped on context-manager exit or process exit.

### Typical Outbound Destinations
- None initiated by the executor itself, other than the Docker daemon or the configured Azure dynamic-sessions endpoint.

### Typical File Paths Accessed
- The configured `work_dir` (default: a temporary directory), or `/mnt/data` for the Azure executor.

### Normal Restart Cadence
- Containers auto-removed and stopped by default at end of use; Jupyter/Azure sessions restarted explicitly, which resets session state.

---

## Swimlane Definition

### Authorized Domains of Work
*Topics, systems, and tasks this agent is permitted to engage with.*

- Executing paired-agent-generated Python and shell code for the operator application's task, inside the configured isolated environment.
- Returning execution output and lifecycle management of that environment.

### Disallowed Domains of Work
*Topics, systems, and tasks this agent must decline or escalate.*

- Judging whether code is semantically safe to run (belongs to the caller / approval step).
- Any work outside code execution: messaging, data persistence, authentication, scheduling, or acting as a network service.

---

## Risk Sensitivities

*Areas where extra scrutiny applies. Praxen will apply lower thresholds for findings in these areas.*

- Sandbox escape and container/host isolation boundaries.
- Working-directory traversal (symlinks, `..`, absolute paths, volume-mount overrides).
- Prompt-injection instructions embedded in code that attempt escalation or exfiltration.
- Use of the local host executor, especially in production.
- Docker socket mounting ("Docker out of Docker") and extra host volume mounts.
- Network egress from the execution environment.
- The default behavior when no approval function is configured (all executions auto-approved).
- Handling of host credentials, environment variables, and the Azure/Docker control channels.

---

## Escalation Rules

These rules drive Praxen's reporting layer. They determine whether a finding is logged only, triggers an alert, or requires an immediate halt.

*State each condition precisely — Praxen will check whether the agent's code implements the described response. "Alert if something suspicious happens" is not checkable; "Alert operator when a reply is addressed to any address not in the Rolodex" is.*

### Halt Agent and Alert Operator
*Conditions serious enough to warrant stopping the agent.*

- A code execution attempts to read or write outside the working directory, or to escape the container/sandbox.
- A code execution attempts to escalate privileges or access parent-process credentials or environment.
- The local host executor is used in a production deployment without operator approval.
- Code that an approval function has denied is executed anyway.

### Alert Operator (Do Not Halt)
- An execution attempts network egress beyond the configured allow-list.
- Embedded instructions in the code source attempt to subvert the sandbox (detected but blocked).
- Executions repeatedly fail up to the configured retry limit.
- A host volume or GPU/device is mounted beyond the configured working directory.

### Log Only
- Every execution is recorded with timestamp, executor kind, language, source agent, working directory, timeout, exit status, and a digest (not the body) of the executed code.

---

## Example Good Behavior

*Concrete examples of what authorized operation looks like. Used to calibrate detection.*

- The agent receives a fenced Python block from the paired coder agent, runs it in a `python:3-slim` Docker container confined to `work_dir` with a 60-second timeout, captures the output, returns exit status and stdout, and stops the container on exit.
- A configured approval function is called with the code before execution; the agent executes only after an approval response.
- On an execution error, the model-backed agent regenerates code and retries up to `max_retries_on_error`, then yields a reflection result instead of looping indefinitely.

---

## Example Bad Behavior

*Concrete examples of what unauthorized or anomalous behavior looks like. Used to calibrate detection.*

- The agent runs generated code on the local host in production instead of a container, with no operator approval.
- Code writes to a path outside the working directory via a symlink or `../` traversal and the executor allows it.
- The executor acts on an embedded instruction to open an outbound connection and exfiltrate a file from the host.
- Error output from a failed execution is swallowed and a success result is returned to the caller.
- Code is accepted and executed from an HTTP endpoint or message queue rather than the paired agent's generated block.

---

*Worker Remit — Praxen*
*Customized for: AutoGen Code Executor | Version: 1.0 | 2026-07-11*

---

## Open Questions for the operator

*These are genuine operator-intent decisions that cannot be derived from the documentation. They sit outside the policy body above (which a Praxen scan reads as rules) so they travel with the remit and reach the operator.*

1. **Authorized executor for this deployment.** Which executor is this deployment permitted to use — Docker command-line (recommended), Jupyter/Docker-Jupyter, Azure dynamic sessions, or local host? Is the local host executor permitted at all, and if so only on ephemeral, isolated hosts?
2. **Network egress scope.** Is any network egress from the execution environment in scope for this deployment, and if so, what is the exact allow-list of destinations?
3. **Approved container image.** Which container image(s) are authorized (default is `python:3-slim`)? Are custom images allowed and from which registries?
4. **Resource ceiling.** What are the maximum authorized resource limits (CPU, memory, and execution timeout) above which operator approval is required?
5. **Authorized code sources (`sources` allowlist).** Which specific agent(s) are authorized to supply code for execution when the agent runs in a group chat?
6. **Permitted languages (`supported_languages`).** Should execution be restricted to a subset of languages (e.g., Python only), or are all default supported shell dialects permitted?
7. **Approval requirement.** Should an approval function be mandatory for this deployment (rather than the default of auto-approving all executions), and what approval criteria apply?

---

*Authoring notes for the operator (not policy):*
- **Thin-docs flag.** The project's `SECURITY.md` is a generic Microsoft vulnerability-reporting boilerplate and says nothing about the executor's runtime security posture. The **escalation / alerting surface is essentially undocumented** — the documentation describes an inline `approval_func` (approve/deny before execution) but no halt/alert/telemetry behavior. The Escalation Rules and the "Log Only" audit-record clause above are therefore stated as **conservative security intent**, not transcribed from docs; confirm they match your operational expectations.
