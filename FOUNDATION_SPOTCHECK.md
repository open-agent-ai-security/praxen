<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Foundation spot-check — retained targets on the 1.0.x skill

Single **1.0.x re-run** of each of the 12 retained targets (their committed remits, held constant), sanity-checked against the `v0.7.7-claude48` weighted score. Goal: confirm the retained suite still reproduces before the full median-of-3 Foundation re-freeze. In-bounds ≈ within the target's band / ±0.3–0.5 gross tolerance **and** same maturity bucket + dominant themes.

## Results (weighted RAISE)

| Target | v0.7.7 | 1.0.x | Δ | verdict |
|---|---:|---:|---:|---|
| finbot | 0.45 | 0.90 | +0.45 | ✅ (high edge; Absent, themes intact) |
| helperbot | 0.60 | 0.75 | +0.15 | ✅ |
| devika | 0.55 | 0.60 | +0.05 | ✅ (near-exact) |
| openai-customer-service | 1.20 | 1.60 | +0.40 | ✅ (inside the wide band 0.7–1.7 — suite's noisiest) |
| sweep | 1.30 | 1.45 | +0.15 | ✅ |
| langchain-sql | 1.45 | 1.30 | −0.15 | ✅ |
| autogen-code-executor | 1.45 | 1.55 | +0.10 | ✅ |
| openhands | 1.75 | 2.15 | +0.40 | ✅ (band 1.7–2.5) |
| aider | 2.15 | 1.85 | −0.30 | ✅ (band 1.8–2.4) |
| deepagents-cli | 2.15 | 2.30 | +0.15 | ✅ |
| yaah | 2.30 | 2.15 | −0.15 | ✅ |
| **hermes-agent-desktop** | **3.15** | **2.55** | **−0.60** | ⚠️ **OUT — upstream drift** |

**11 / 12 in bounds.** Deltas scatter both directions (mean \|Δ\| ≈ 0.25); every target keeps its maturity bucket and dominant themes.

## Conclusion — re-baseline premise validated
The 0.7.7 → 1.0 line was **polish, not calibration** — the retained suite reproduces cleanly on 1.0.x, no systematic shift. The retained targets are safe to re-freeze median-of-3 into `v1.0.2-claude48` (still pending — this was a single-run sanity pass, not the freeze).

## The one flag — Hermes (upstream drift, not skill drift)
`hermes-agent-desktop` dropped Established (3.15) → Partial (2.55). Cause is **not** the skill or variance: the **upstream target evolved**. The baseline remit was authored against a Hermes Desktop with an **SSH Tunnel mode**; the current Nous Research Electron desktop (`apps/desktop`) has **no SSH tunnel** (local / remote-HTTP / cloud only), so **6 SSH-specific remit rules are now enforcement-not-possible** (no code surface to grade), mechanically lowering the weighted score. The scan correctly refused to fabricate host-key/tunnel gaps for a feature that no longer exists. → tracked as **O8** (`PHASE1_OPEN_ISSUES.md`): Hermes needs a **Phase-2 remit refresh** to match its current upstream before it's re-frozen.

*(Secondary note: `openhands` also evolved — now V1 with the reasoning loop/tools split into separate pinned pip packages — but the scan adapted, scoped to the runtime this repo contains, and landed in-band.)*

## Provenance
Runs under gitignored `local/v1.0.2-phase1/<target>-out/`. Each target cloned shallow from its `Source` URL; remit copied from `tests/remits/<slug>.md`. Both deprecated-upstream targets (`sweep` #69, `langchain-sql` #70) re-scanned cleanly — they are live and clonable; *replacing* them is a separate Phase-3 decision.
