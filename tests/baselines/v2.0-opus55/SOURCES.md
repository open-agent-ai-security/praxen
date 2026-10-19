<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Sources — v2.0-opus55

The exact upstream commit every target was scanned at. **Clone each target at
this SHA, never at HEAD** — upstream moves, and a re-run against drifted source
measures the drift, not the change under test.

This file is committed on purpose. The previous freeze recorded its pins in
`local/v1.3-freeze/CLONE_SHAS.txt` — a **gitignored** path — and they were lost
with the machine that held them. Only three survived, by accident, in prose
elsewhere. Pins are now part of the baseline they belong to.

## Pins

| Target | Upstream | Commit | Committed | Provenance |
|---|---|---|---|---|
| `helperbot` | [opena2a-org/damn-vulnerable-ai-agent](https://github.com/opena2a-org/damn-vulnerable-ai-agent) | `fd8fd185bf46b94df58398922a5842de6244361b` | 2026-07-16 | **RECOVERED-EXACT** |
| `finbot` | [OWASP-ASI/finbot-ctf-demo](https://github.com/OWASP-ASI/finbot-ctf-demo) | `3bdeca0aa6ab8961d3bca09cfd8a3358e346c8e7` | 2026-01-20 | **RECOVERED-EXACT** |
| `craftbot` | [CraftOS-dev/CraftBot](https://github.com/CraftOS-dev/CraftBot) | `2391f9c0267af57371e63dd9437dff47c4e544ec` | 2026-07-03 | **RECOVERED-AMBIGUOUS** |
| `openai-customer-service` | [openai/openai-agents-python](https://github.com/openai/openai-agents-python) | `5804bd039f2c92c9b93b3b8e8037c9e8ef9906eb` | 2026-07-28 | **RECOVERED-AMBIGUOUS** |
| `salesforce-help-agent-accelerator` | [salesforce/help-agent-accelerator](https://github.com/salesforce/help-agent-accelerator) | `304de841be3a67fdf5a1487533fc00b1398a80f3` | 2026-06-02 | **RECOVERED-AMBIGUOUS** |
| `aider` | [Aider-AI/aider](https://github.com/Aider-AI/aider) | `5dc9490bb35f9729ef2c95d00a19ccd30c26339c` | 2026-05-22 | **RECOVERED-EXACT** |
| `autogen-code-executor` | [microsoft/autogen](https://github.com/microsoft/autogen) | `027ecf0a379bcc1d09956d46d12d44a3ad9cee14` | 2026-04-06 | **RECOVERED-EXACT** |
| `uagents` | [fetchai/uAgents](https://github.com/fetchai/uAgents) | `7870048f0e80ed3c48f83556511169ecf671df5b` | 2026-07-23 | **RECOVERED-EXACT** |
| `yaah` | [dirien/yet-another-agent-harness](https://github.com/dirien/yet-another-agent-harness) | `5bc3b04124d4d8d7f80cc6974a665b2a47e53639` | 2026-05-31 | **RECOVERED-EXACT** |
| `openhands` | [All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands) | `652503005093d18d1b2f48816c91d62e93f45970` | 2026-07-24 | **DOCUMENTED** |
| `deepagents-cli` | [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) | `44910bc2ef3f70975533e4a2ce38ee0e2d0624b6` | 2026-07-27 | **RECOVERED-AMBIGUOUS** |
| `hermes-agent` | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | `b1a25404b638bfbd79ce4d08b49afc0ee1361528` | 2026-05-30 | **DOCUMENTED** |
| `hermes-desktop` | [fathah/hermes-desktop](https://github.com/fathah/hermes-desktop) | `4e8388a7ec26ce80c76fcdb5976920c453abb550` | 2026-05-25 | **DOCUMENTED** |

`hermes-agent-desktop` is one combined workspace with both repositories as
subdirectories — `hermes-agent/` and `hermes-desktop/` — matching how v1.3
scanned it, so cited paths line up.

## Provenance tiers

These pins are the v1.3 freeze's own pins, reconstructed — so that this freeze
changes **only the model** relative to `v1.3-opus5`. Sources pinned, remits
byte-identical to the v1.3 copies, and the 2.0 skill verified score-inert
against v1.3 leave the reference model as the single variable.

- **DOCUMENTED** (3) — the pin survived in committed text: OpenHands in
  `tests/baselines/v1.3-opus5/BASELINE.md` (the deliberate pre-migration
  commit), both Hermes repos in `tests/README.md`.
- **RECOVERED-EXACT** (6) — reconstructed forensically and resolved to a single
  tree for every cited file. All six also have HEAD-at-cutoff in the winning
  set: the cited code was stable up to the v1.2 scan date.
- **RECOVERED-AMBIGUOUS** (4) — reconstructed, but the evidence admits a small
  set of trees that differ in regions no citation constrains. The residual is
  narrow: each tie spans 0-1 day of upstream history (salesforce: 8 days) and
  differs by 11-86 lines across the cited files, against the ~2.5 months of
  drift a fresh HEAD clone would have introduced.

## How the pins were recovered

`local/v2.0-opus55/recover_pins2.py` (kept outside the repo; reproducible from
any clone). For each target it scores candidate commits against the v1.3
evidence — the findings' `file:line` citations **plus** the threat-model
graph's, which cite every node, edge, boundary and threat and give 5-6x the
signal. A commit scores on whether the snippet's code identifiers sit inside
the exact line range the snippet names ("lines 125-148"), with a looser
+/-25-line window as the tiebreak. Candidates are the commits that changed a
cited file before the first v1.2 scan (`2026-07-28T22:25:47Z`): between two
such commits every cited file is identical, so nothing in between needs
scoring.

**Calibrated before use.** The method had to place all three DOCUMENTED pins in
its winning set before it was trusted for the other ten. It did — and getting
there took two corrections, both found by calibration rather than assumed:

1. Candidates were first capped by count (the 600 most recent). hermes-agent's
   true pin sits 8,818 commits back and was never searched; the method settled
   for a worse local maximum. Now bounded by date.
2. The loose window was ranked first. hermes-agent's true pin then lost
   (0.919 loose / 0.759 tight) to a later commit (0.928 / 0.728) — the loose
   window rewards later code for drifting *nearby*, while the cited range is an
   exact fact about the scanned file. Tight is now primary.

OpenHands landed exactly on its documented commit.

## Scope

Each target's scan scope is its `tests/scan_instructions/<target>.md`, copied to
`SCAN_INSTRUCTIONS.md` in the run directory. `finbot` and `craftbot` have none
and scan the whole workspace.
