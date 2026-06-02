# Salesforce Help Agent Accelerator

## Overview

This agent is available from [Salesforce](https://www.salesforce.com) as an
open source project hosted on a Salesforce [public Github repository](https://github.com/salesforce/help-agent-accelerator).

**Note**: the scan was NOT run against any actual deployed agent, or even an actual configuration with a valid Salesforce org. It was run against the exact codebase in the source repository, as-is.

## Worker Remit Generation

The `WORKER_REMIT.md` for this agent was created using:

* the skill
* `Claude Sonnet 4.6` with medium effort, and
* the following prompt:
  ```text
  draft a worker remit for the agent source code at /Users/json/src/github/help-agent-accelerator
  ```

## Report Generation

The report was created using:

* the skill
* `Claude Sonnet 4.6` with medium effort, and
* the following prompt:
  ```text
  Please run the behavior-verifier skill against ../../github/help-agent-accelerator
  Use the Worker Remit at examples/salesforce-help-agent-accelerator/WORKER_REMIT.md. Write outputs
  to ./reports/salesforce-help-agent-accelerator/.
  ```
