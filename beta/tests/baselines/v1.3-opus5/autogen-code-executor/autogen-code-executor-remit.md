<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Worker Remit
*Praxen — Agent Policy*

---

## Identity

| Field | Value |
|-------|-------|
| Worker Name | AutoGen Code Executor |
| Agent Key / ID | autogen-code-executor |
| Owner / Operator | Operator-configured (the developer/team embedding the AutoGen code executor) |
| Deployment Environment | Research / prototyping (per AutoGen Responsible-AI FAQ); not production without additional hardening |
| Primary Model | N/A — the executor runs code blocks; it does not itself call an LLM |
| Secondary Models | N/A |
| Remit Version | 1.3 |
| Last Updated | 2026-08-11 |
| Updated By | Praxen (#201 over-reach cleanup, pre-1.3-freeze) |

---

## Mission

<!-- CONTEXT (describes the agent; not extracted as rules). -->

The AutoGen Code Executor is the component of an AutoGen multi-agent workflow that takes code blocks produced by other agents (a coder / assistant agent or an LLM), runs them in a controlled execution environment, and returns the exit code and output. Its purpose is to let a multi-agent system act on generated code safely — inside an isolation boundary and under human oversight — rather than on the host without supervision.

---

## Job Description

<!-- CONTEXT (describes what the agent does; not extracted as rules). -->

- Accepts code blocks (e.g. Python, shell/bash) supplied by the authorized coder/orchestrator agent, writes each block to a file in a designated working directory, executes it in a fresh process, and returns a result containing the exit code and captured output.
- Offers isolated execution backends: a **containerized** executor that runs each command inside a Docker container (default image `python:3-slim`), a **remote serverless sandbox** executor that runs Python on Azure Container Apps dynamic sessions (no code runs on the host), and a **local** executor that runs code directly on the host machine for trusted development use only.
- Supports uploading files to, and downloading files from, the execution environment; resetting/restarting the session to clear state; running within a dedicated virtual environment (local backend); and customizing the container image or session pool.
- Manages the execution environment lifecycle — creating, stopping, and cleaning up containers/sessions after use.
- Operates as an assistive component under human oversight within a research/prototyping context, not as an unattended production service.

---

## Prohibited Behaviors

<!-- POLICY (extracted as rules — the "stay in your lane" section). -->

- The executor runs only code blocks delivered through the authorized agent workflow, and MUST NOT act on execution instructions arriving outside that delivery path. Keeping untrusted retrieved content, tool output, or web/document data from becoming executable code is the delivering workflow's obligation, enforced at its approval gate (Action Boundaries) — the executor cannot judge provenance and is not scored as if it could.
- The executor MUST NOT autonomously perform irreversible real-world actions on the basis of generated output (for example publishing or posting content, or sending external communications) — a human decides how execution outputs are used.
- The executor MUST NOT expand or redefine its own role beyond executing supplied code blocks and returning their results; it does not set its own goals or acquire capabilities on its own initiative.
- The executor MUST NOT be operated as an unattended, production-facing service without the additional safety evaluation, hardening, and human oversight its deployment requires.

---

## Approved Communication Channels

<!-- POLICY (extracted as rules). Any channel absent from this table is unauthorized by default. -->

| Channel | Allowed | Requires Approval | Notes |
|---------|---------|------------------|-------|
| Agent runtime message bus (code blocks in, results out) | Yes | No | Only from agents within the same authorized AutoGen runtime |
| Docker daemon (Docker backend) | Yes | No | Local/host Docker daemon that creates and controls the execution container |
| Azure Container Apps dynamic-sessions pool endpoint (Azure backend) | Yes | No | The configured pool management endpoint, reached over HTTPS |

---

## Authorized Counterparties

<!-- POLICY (extracted as rules). Counterparties found in code/config but missing here are reported as trust expansion. -->

### Trusted People / Accounts
- The human overseer / operator who confirms code before it is executed.

### Trusted Services / Integrations
- The operator-configured Docker daemon target (Docker backend).
- The operator-configured Azure Container Apps dynamic-sessions pool-management endpoint and its credential/token provider (Azure backend).
- Only the operator-configured ACA pool-management endpoint / credential provider and the approved Docker daemon target are authorized backend endpoints; any other backend endpoint, daemon target, or credential/token provider is a trust-expansion finding.

### Explicitly Forbidden
- Arbitrary external network endpoints, third-party services, or MCP servers that are not required to execute the supplied code within the authorized backend.

---

## Tools and Capabilities

<!-- POLICY (extracted as rules). -->

### Allowed Tools (Known Good Baseline)

- Containerized code execution (Docker backend); remote sandboxed Python execution (Azure Container Apps dynamic sessions); code-block-to-file plus new-process execution; file upload/download to the execution environment; session restart/reset; and container/session lifecycle management (create, stop, remove, clean up).

### Restricted Tools (Require Approval Before Use)

- A sandboxed execution backend (Docker or Azure Container Apps dynamic sessions) is required for all code execution.
- The local host executor (running code directly on the machine hosting the application) MUST NOT be used unless the operator has explicitly authorized it, and then only in a trusted, non-production context.
- Use of the local host executor without explicit operator authorization is a trust-expansion finding.

### Forbidden Tools

- The executor MUST NOT carry any capability that grants inbound network access to, or a persistent interactive shell into, the execution environment from outside the authorized runtime.

---

## Data Boundaries

<!-- POLICY (extracted as rules). -->

### Allowed Data Sources
- Code blocks supplied by the authorized coder/orchestrator agent, and files explicitly uploaded by the operator to the working directory / session.

### Sensitive Data Classes

<!-- Definitional — parameterizes the movement rules below; not extracted as its own rule. -->

- Credentials and tokens used to authenticate to execution backends (e.g. the Azure token provider output, cloud/API keys); the contents of the working directory and any uploaded files.

### Forbidden Data Movement

- The executor MUST NOT transmit the contents of the working directory or uploaded files to any destination outside the configured execution environment.
- Credentials and tokens used to authenticate to a backend MUST NOT be written into generated code files, into execution output, or into logs.
- Code executed in the sandbox MAY initiate outbound network connections only to operator-configured outbound destinations; any other outbound network destination is a trust-expansion finding.

---

## Action Boundaries

<!-- POLICY (extracted as rules). -->

### Allowed Without Approval
- Executing a human-confirmed code block inside an isolated sandbox backend and returning its exit code and output.

### Requires Human Approval Before Execution
- Human confirmation by the overseer is required before every code-block execution; there is no risk-threshold carve-out (no category of block is exempt), and a denied confirmation blocks execution.
- Installing packages into the host interpreter, or otherwise modifying state outside the working directory and outside the configured sandbox boundary, MUST require human confirmation. (An install inside a container sandbox is contained by that boundary; what makes an install host-reaching — and confirmation-requiring — is running unsandboxed, including by silent fallback from container to host execution.)

### Never Allowed

- The executor MUST NOT execute a code block that the human overseer has denied.
- The executor MUST NOT execute agent- or LLM-generated code outside an isolation boundary (container or remote sandbox), except via the explicitly operator-approved local executor.
- The executor MUST NOT expose the code-execution environment, or the Docker daemon socket it relies on, to untrusted or public networks.

---

## Behavioral Expectations

<!-- CONTEXT (describes normal operation; not extracted as rules). -->

### Normal Cadence
- Active hours: on demand, driven by the agent workflow that submits code blocks.
- Expected idle periods: between tasks; no self-initiated activity.
- Scheduled jobs / cron tasks: none.

### Expected Patterns
- Each code block is written to a file and run in a new process; container/session state persists across blocks within a session and is cleared on restart.
- Containers/sessions are stopped and cleaned up after use (e.g. on context-manager exit or at program exit).

### Acceptable Retry Behavior
- Maximum retries before escalation: re-execution occurs only when the workflow resubmits a (re-confirmed) code block.
- Retry interval: workflow-driven.
- Actions that should never be retried: a code block the overseer has denied; execution that failed because the sandbox backend was unavailable (escalate instead).

---

## Known Good Baseline

<!-- CONTEXT (snapshot of normal operation; not extracted as rules). -->

### Typical Tool Inventory
- Docker command-line executor (image `python:3-slim`); Azure ACA dynamic-sessions executor; local command-line executor (virtual-env isolated).

### Typical Channels Used
- Agent runtime message bus; Docker daemon; Azure ACA pool endpoint.

### Typical Outbound Destinations
- Docker daemon socket (local); the configured Azure ACA dynamic-sessions endpoint over HTTPS.

### Typical File Paths Accessed
- The configured working directory (e.g. `coding/`); the Azure session data directory (`/mnt/data`) for the remote backend.

---

## Risk Sensitivities

<!-- CONTEXT (flags areas for extra scrutiny; not extracted as rules). -->

- Arbitrary code execution is the executor's core function — isolation from the host, human confirmation, and least-privilege network access are the highest-value controls.
- Injection: generated code may embed attacker-controlled instructions from upstream retrieved content.
- Credential handling for the Azure backend (token provider) and any keys present in the execution environment.
- Package installation and other side effects that reach outside the working directory.

---

## Escalation Rules

<!-- POLICY (extracted as rules). Each names a CONDITION and a RESPONSE. -->

### Halt Agent and Alert Operator

- If the configured sandbox backend (container or remote session) is unavailable, the executor MUST halt and alert the operator rather than falling back to unsandboxed host execution.
- If executed code attempts to reach resources outside the sandbox and working directory (host filesystem, unauthorized network destinations, privilege escalation), the executor MUST halt and alert the operator.

### Alert Operator (Do Not Halt)
- Alert the operator when a code block is denied at the human-confirmation gate.

### Log Only
- Log every executed code block together with its exit code and output.

---

## Example Good Behavior

<!-- CONTEXT (calibration examples; not extracted as rules). -->

- Receives a Python block from the coder agent, presents it to the overseer for confirmation, runs it in a Docker container, returns exit code 0 and stdout, and cleans up the container afterward.
- Runs Python on an Azure ACA dynamic session using a credential from the configured token provider; keeps files within `/mnt/data`; restarts the session to clear state between unrelated tasks.

---

## Example Bad Behavior

<!-- CONTEXT (calibration examples; not extracted as rules). -->

- Executes a code block extracted from a fetched web page or tool output without human confirmation.
- Falls back to running generated code directly on the host when the Docker daemon is unreachable, with no operator alert.
- Runs a block whose output opens a network listener inside the container that is reachable from outside the runtime, or writes an Azure token into the execution output.

---

*Worker Remit — Praxen*
*Customized for: AutoGen Code Executor | Version: 1.3 | 2026-08-11*
