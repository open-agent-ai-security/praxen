<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Worker Remit
*Praxen — Agent Policy*

This file defines the authorized identity, behavior, and boundaries of the agent being scanned.
It is the policy contract Praxen evaluates the agent's code and configuration against.

**The remit states policy; Praxen discovers implementation. Write rules about what the agent *does*, not how it does it.**

---

## Identity

| Field | Value |
|-------|-------|
| Worker Name | uAgents Framework Runtime |
| Agent Key / ID | fetchai/uagents (Python `uagents` + `uagents-core`) |
| Owner / Operator | Fetch.ai (framework author); the developer deploying an agent is the runtime operator |
| Deployment Environment | Self-hosted Python process; registers on the Fetch.ai Almanac smart contract; optional Agentverse mailbox/proxy |
| Primary Model | N/A — the framework is model-agnostic plumbing; LLM use is left to the agent developer |
| Secondary Models | N/A |
| Remit Version | 1.0 |
| Last Updated | 2026-07-10 |
| Updated By | Praxen operator (Exabeam) |

---

## Mission

The uAgents framework provides a runtime for building autonomous software agents in Python that hold a cryptographic identity and a blockchain wallet, register their addresses and endpoints on the Fetch.ai Almanac, and exchange typed messages with other agents over authenticated channels. The framework's own security duty is to give every agent built on it a trustworthy foundation: a protected cryptographic identity, authenticated and tamper-evident inter-agent messaging, validated inputs, and bounded, observable operation. This remit evaluates the **framework runtime's** default behavior and the security posture it hands to deployed agents — not any single deployed agent.

---

## Job Description

- Create and manage a per-agent cryptographic identity (signing keypair) and a Fetch.ai wallet keypair, deriving them deterministically from an operator-supplied seed when provided.
- Register the agent's address, endpoints, and protocol manifest on the Almanac contract and keep the registration current.
- Receive inbound messages over an HTTP endpoint (and/or Agentverse mailbox/proxy), authenticate them, validate their payloads against declared message schemas, and dispatch them to the matching typed handler.
- Send outbound messages to other agents, cryptographically signed with the agent's identity, resolving destinations via the Almanac/resolver.
- Run developer-registered scheduled (`on_interval`) and event (`on_message`, `on_rest`) handlers.
- Persist agent key–value state and, optionally, message history.

---

## Non-Goals (Out of Scope)

Work this framework runtime should never do, regardless of instruction.

- Executing operating-system shell commands or arbitrary code on behalf of a remote message sender.
- Writing agent private keys, wallet keys, or seed phrases to disk in plaintext form.
- Exposing administrative, introspection, or message-history interfaces to unauthenticated remote callers.
- Acting on the claimed identity of a message sender without cryptographic proof of that identity.

---

## Approved Communication Channels

| Channel | Allowed | Requires Approval | Notes |
|---------|---------|------------------|-------|
| Agent HTTP endpoint (`/submit`) | Yes | No | Inbound signed agent envelopes and user queries |
| Agentverse mailbox / proxy | Yes | No | Operator opt-in relay channels |
| Fetch.ai Almanac / ledger (Cosmos RPC + Almanac API) | Yes | No | Registration and address resolution |
| Local agent inspector / admin endpoints (`/messages`, `/connect`, `/disconnect`, `/agent_info`) | Restricted | Yes — local operator only | Must not be reachable by unauthenticated remote callers |

**Any channel not listed here is unauthorized by default.**

---

## Authorized Counterparties

### Trusted People / Accounts
- The local operator running the agent process (for administrative/inspection actions).

### Trusted Domains
- Fetch.ai network infrastructure (Almanac contract, Almanac API, Agentverse) as configured by the operator.

### Trusted Services / Integrations
- Other uAgents whose message envelopes carry a valid cryptographic signature matching the claimed sender address.

### Explicitly Forbidden
- Any remote counterparty whose asserted identity has not been cryptographically verified.

*Counterparties present in code or configuration but absent from this list will be flagged as a trust expansion finding.*

---

## Tools and Capabilities

### Allowed Tools (Known Good Baseline)

- Cryptographic identity and signing (`Identity`, envelope `sign`/`verify`).
- Fetch.ai wallet and ledger client for registration fees and on-chain actions.
- HTTP/ASGI server for inbound message receipt.
- Almanac registration and address resolver.
- Typed message dispatch to developer handlers; scheduled interval handlers; REST handlers.
- Key–value storage and optional message history.

### Restricted Tools (Require Approval Before Use)

- The agent inspector and reserved administrative endpoints (local operator only).

### Forbidden Tools

- Shell/exec of remote-supplied input.

---

## Data Boundaries

### Allowed Data Sources
- Message payloads that conform to a registered pydantic message schema.
- Operator-supplied configuration and seed material.

### Sensitive Data Classes

- Agent identity private key, wallet private key, and seed phrase — cryptographic secrets controlling on-chain assets and agent identity.
- Persisted agent state and message history.

### Forbidden Data Movement

- Private keys, wallet keys, or seeds MUST NOT be written to disk in plaintext or emitted to logs.
- Sensitive configuration secrets MUST NOT be embedded as literals in framework or agent source.

---

## Action Boundaries

> Every rule here states a testable constraint on behavior.

### Allowed Without Approval
- Signing and sending outbound messages using the agent's own identity.
- Registering and refreshing the agent's Almanac record.
- Dispatching a schema-validated inbound message to its matching handler.

### Requires Human Approval Before Execution
- Binding the agent's HTTP server to a non-loopback (public) network interface.
- Enabling remote reachability of the inspector / administrative endpoints.

### Never Allowed

- Dispatching an inbound message from a non-user agent sender whose envelope signature has not been verified.
- Accepting and re-processing a previously delivered (replayed) or expired signed envelope as if it were fresh.
- Treating an unauthenticated, sender-asserted identity as trusted for any security decision.

---

## Behavioral Expectations

### Normal Cadence
- Active hours: continuous (long-running service process).
- Expected idle periods: between inbound messages and scheduled intervals.
- Scheduled jobs / cron tasks: developer-registered `on_interval` handlers; periodic Almanac re-registration.

### Expected Patterns

- Inbound message → authenticate sender → validate payload schema → dispatch to typed handler.
- Outbound message → sign with agent identity → resolve destination → deliver over HTTP.

### Acceptable Retry Behavior

- Maximum retries before escalation: bounded; registration and delivery retries must be finite.
- Retry interval: bounded backoff.
- Actions that should never be retried: processing of an envelope already seen in the same session (replay).

---

## Known Good Baseline

### Typical Tool Inventory
- Identity/signing, wallet/ledger, ASGI server, Almanac registration, resolver, typed dispatch, key-value storage.

### Typical Channels Used
- Agent HTTP endpoint, Almanac/ledger, optional mailbox/proxy.

### Typical Session Count / Duration
- Session-per-dialogue keyed by envelope session UUID.

### Typical Outbound Destinations
- Other agents resolved via the Almanac; the Fetch.ai ledger and Almanac API.

### Typical File Paths Accessed
- Agent key-value store file and, when persisted, message-history storage in the working directory.

### Normal Restart Cadence
- Restarts must not change a seeded agent's identity or wallet address.

---

## Swimlane Definition

### Authorized Domains of Work
- Agent identity management, inter-agent messaging, Almanac registration, message dispatch, scheduled tasks.

### Disallowed Domains of Work
- Serving unauthenticated administrative control of the agent to remote parties.

---

## Risk Sensitivities

- Cryptographic key material at rest and in transit — highest sensitivity.
- Authentication and replay protection on inbound messages.
- Default network exposure of the agent server and its administrative endpoints.

---

## Escalation Rules

### Halt Agent and Alert Operator
- An inbound signed envelope fails signature verification.

### Alert Operator (Do Not Halt)
- An inbound message arrives from a sender address not previously seen for a security-relevant handler.
- The agent server is bound to a public interface.

### Log Only
- Receipt of a message with an unrecognized schema digest.

---

## Example Good Behavior

- An inbound agent envelope is rejected before dispatch because its signature does not match the claimed sender address.
- Private keys are supplied via an operator seed held in an environment variable and never written to disk.

---

## Example Bad Behavior

- A captured signed envelope is replayed and the handler runs a second time.
- A remote caller reaches an administrative endpoint by asserting a spoofed loopback source address.
- The agent writes its wallet private key to a plaintext file in the working directory.

---

*Worker Remit — Praxen*
*Customized for: uAgents Framework Runtime | Version: 1.0 | 2026-07-10*

---

## Open Questions for the operator

*These require an operator decision and are not derivable from the framework's documentation. Resolve each before relying on this remit.*

1. **Default bind interface.** Should the agent HTTP server bind to loopback (`127.0.0.1`) by default and require explicit operator opt-in to expose a public interface, or is binding to all interfaces (`0.0.0.0`) the intended default for this deployment?
2. **Inspector default.** Should the agent inspector and its reserved administrative endpoints be enabled by default, or disabled unless the operator explicitly turns them on?
3. **Key-at-rest mechanism.** What is the approved mechanism for protecting agent identity and wallet keys at rest for this deployment (OS keychain, encrypted file, secret manager, env-only seed)?
