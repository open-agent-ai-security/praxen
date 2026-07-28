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
| Worker Name | uAgents Framework Runtime |
| Agent Key / ID | fetchai/uagents (Python `uagents` + `uagents-core`) |
| Owner / Operator | Fetch.ai (framework author); the developer deploying an agent is the runtime operator |
| Deployment Environment | Self-hosted Python process; registers on the Fetch.ai Almanac smart contract; optional Agentverse mailbox/proxy |
| Primary Model | N/A — the framework is model-agnostic plumbing; LLM use is left to the agent developer |
| Secondary Models | N/A |
| Remit Version | 1.2 |
| Last Updated | 2026-07-28 |
| Updated By | Praxen remit maintenance (placement + deepen, v1.2) |

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

## Prohibited Behaviors
Work this framework runtime should never do, regardless of instruction.

- Executing operating-system shell commands or arbitrary code on behalf of a remote message sender.
- Writing agent private keys, wallet keys, or seed phrases to disk in plaintext form.
- Disclosing agent identity or wallet private key material outside the agent process, whether over the network, inside a message payload, or in an Almanac record.
- Exposing administrative, introspection, or message-history interfaces to unauthenticated remote callers.
- Acting on the claimed identity of a message sender without cryptographic proof of that identity.
- Advertising on the Almanac, or resolving to counterparties, an endpoint or public identity the agent does not itself control and serve.

---

## Approved Communication Channels

| Channel | Allowed | Requires Approval | Notes |
|---------|---------|------------------|-------|
| Agent HTTP endpoint (`/submit`) | Yes | No | Inbound signed agent envelopes and user queries |
| Agentverse mailbox / proxy | Yes | No | Operator opt-in relay channels |
| Fetch.ai Almanac / ledger (Cosmos RPC + Almanac API) | Yes | No | Registration and address resolution |
| Local agent inspector / admin endpoints (`/messages`, `/connect`, `/disconnect`, `/agent_info`) | Restricted | Yes — local operator only | Must not be reachable by unauthenticated remote callers |

---

## Authorized Counterparties

### Trusted People / Accounts
- The local operator running the agent process (for administrative/inspection actions).

### Trusted Domains
- Fetch.ai network infrastructure (Almanac contract, Almanac API, Agentverse) as configured by the operator.

### Trusted Services / Integrations
- Other uAgents whose message envelopes carry a valid cryptographic signature matching the claimed sender address.
- An inbound agent counterparty is authorized only after its envelope signature verifies against the claimed sender address and the envelope is confirmed fresh, neither previously delivered nor expired.

### Explicitly Forbidden
- Any remote counterparty whose asserted identity has not been cryptographically verified.
- A sender whose envelope signature is missing, malformed, or does not match the claimed sender address.
- A message relayed through the Agentverse mailbox or proxy that cannot be attributed to a signature-verified origin agent; the mailbox and proxy are transport only and MUST NOT be treated as authenticating the sender.

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
- Agent identity and wallet private keys MUST be derived in process memory from an operator seed supplied via environment variable and MUST NOT be persisted to disk, in plaintext or any other form.
- Agent identity or wallet private keys and seed material MUST NOT be transmitted in any outbound message, Almanac registration record, or network response; only the agent's public address and verification key may be published or shared with counterparties.
- Private key or seed material MUST NOT be made available to a message handler, REST handler, scheduled handler, or any developer-supplied callback.
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
- Operating an agent without a configured seed such that its private key is written to local storage rather than derived in memory from an environment-supplied seed.

### Never Allowed

- Dispatching an inbound message from a non-user agent sender whose envelope signature has not been verified.
- Accepting and re-processing a previously delivered (replayed) or expired signed envelope as if it were fresh.
- Treating an unauthenticated, sender-asserted identity as trusted for any security decision.
- Sending an outbound message that is not cryptographically signed with the agent's own identity.
- Replacing, regenerating, or re-deriving to a different value the identity or wallet address of an agent configured with a fixed seed, whether on restart or during operation.
- Registering on the Almanac, or resolving to counterparties, an endpoint or public key the operator did not configure for this agent.

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
- Restarts are infrequent operational events; under normal operation a seeded agent resumes with its prior address while an unseeded agent presents a freshly generated address.

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
- The agent's Almanac record resolves to an endpoint or public key the agent did not publish.
- Agent identity or wallet private key material is detected leaving the process in a log line, message payload, or Almanac record.

### Alert Operator (Do Not Halt)
- An inbound message arrives from a sender address not previously seen for a security-relevant handler.
- The agent server is bound to a public interface.
- A previously delivered or expired envelope is re-presented for processing.
- Registration or message-delivery retries reach their finite bound without success.
- An agent private key is loaded from on-disk storage rather than derived from an environment-supplied seed.
- A mailbox- or proxy-relayed message arrives that cannot be attributed to a signature-verified origin agent.

### Log Only
- Receipt of a message with an unrecognized schema digest.
- An inbound message is rejected for failing schema validation.

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
*Customized for: uAgents Framework Runtime | Version: 1.2 | 2026-07-28*
