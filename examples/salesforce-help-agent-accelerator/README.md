# Salesforce Help Agent Accelerator

## Overview

This agent is available from [Salesforce](https://www.salesforce.com) as an
open source project hosted on a Salesforce [public Github repository](https://github.com/salesforce/help-agent-accelerator).

**Note**: the scan was NOT run against any actual deployed agent, or even an actual configuration with a valid Salesforce org. It was run against the exact codebase in the source repository, as-is.

## Worker Remit Generation

The `WORKER_REMIT.md` for this agent was authored by the Praxen behavior-verifier
skill as a **blind, documentation-only draft** — generated from the agent's public
docs without reading its implementation — and then refined to remove authoring
over-reach. It is the remit frozen in the Praxen v1.2 baseline.

## Report Generation

The report was produced by the Praxen behavior-verifier skill (v1.2) running on
`Claude Opus 5`, scanning the source repository **as-is** at pinned commit
`304de841`. It is the frozen v1.2 baseline run for this target (weighted RAISE
1.70; the median of three identical-input runs).
