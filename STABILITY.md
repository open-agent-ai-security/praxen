<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxen Stability Contract

From **1.0**, Praxen follows semantic versioning across two independently-versioned surfaces — the **product version** (`praxen_version`, e.g. `1.0.0`) and the **findings-schema version** (`schema_version`, currently `2.0`). This document defines what each major line guarantees. **Anything not listed as Stable is explicitly Evolving and may change in a minor release.**

## Semver / compatibility policy

Praxen is versioned `MAJOR.MINOR.PATCH`. The findings JSON schema carries its own `schema_version`; downstream tooling should **pin to a schema MAJOR and tolerate unknown fields and unknown enum values**, since both may be added in a schema MINOR. A **product MAJOR** bump is reserved for a breaking change to a Stable surface (below): the RAISE category set or weights, the skill's remit-discovery / workspace / `./reports/` output contract, the Worker Remit section structure, or the removal/renaming of any schema field or enum value. Everything else — new detection patterns, report styling, prose, scores, run-to-run wording, and *additive* schema/remit fields — may change in a MINOR. Security fixes ship in the latest released line as PATCH releases.

## Stable — guaranteed for the life of the 1.x line

A breaking change to any of these requires the next MAJOR.

### 1. Findings JSON schema (`schema.py` / `findings.schema.json`)

Within a given `schema_version` MAJOR, the published JSON is a stable contract for downstream consumers. Frozen:

- The **top-level object shape** — a JSON object, never a bare list.
- The **required sections**: `scan`, `intro_band`, `behavior_summary`, `remit_coverage`, `findings`, `positives`, `log_files`, `raise_posture`, `footer`.
- The **fixed enumerations**: `SEVERITIES`, `REMIT_STATUSES`, `CONFIDENCES`, `TAG_KINDS`, `ESCALATIONS`, and the finding-ID grammar `PRAX-YYYY-MM-DD-NNN`.

**Additive minors only.** A new *optional* field or a new enum *value* may ship in a schema MINOR (e.g. `2.1`); consumers must ignore unknown fields and unknown enum values. Removing a field, removing/renaming an enum value, or changing a field's type or required-ness is a schema-MAJOR (`3.0`) change. The validator's rule stands: a consumer accepts any matching MAJOR and a newer MINOR, and rejects a different MAJOR.

### 2. The RAISE six-category set and weights

The six categories (in canonical order), their display names, and their weights — **Implement Zero Trust 0.25; the other five 0.15 each**, summing to 1.0 — are stable, as is the weighted-overall formula `Σ(category_score × category_weight)` over the 0–5 integer scale and the 0–5 maturity labels (Absent … Exemplary). Re-ordering, renaming, re-weighting, or adding/removing a category is a **product-MAJOR** change, because it breaks score comparability across the installed base.

### 3. The skill invocation interface

Three behaviors downstream automation may rely on:

- **Remit discovery** finds `WORKER_REMIT.md` / `WORKER_REMIT_*.md` in the current directory (then the skill directory), preferring the file naming the scanned agent.
- A **workspace path** is accepted from the invocation message.
- **Output** is written to `./reports/` relative to the working directory, with the filename patterns `<agent-slug>-findings-<YYYY-MM-DD>.json`, `<agent-slug>-analysis-<TIMESTAMP>.html`, and `<agent-slug>-analysis-<TIMESTAMP>.txt`.

The output directory, the three output formats, and these filename *patterns* are stable — CI and pipelines glob on them, so treat them as API.

### 4. The Worker Remit section structure (`WORKER_REMIT_template.md`)

The named top-level sections of the template are stable: a remit authored against 1.0 must keep parsing for the life of the 1.x line. New **optional** sections may be added in a minor; existing section *names* are not renamed or removed within 1.x.

## Evolving — may change in any minor release

Do **not** build hard dependencies on these:

- **The exact set and names of detection / verification patterns.** The README's "What Praxen verifies" is illustrative, not exhaustive ("…and more"); new patterns are added routinely.
- **Per-scan remit-rule IDs (`R-NN`).** These are the model's per-scan enumeration, not stable identifiers — diff baselines by rule *text*, not ID.
- **The exact wording of `behavior_summary`, rationales, recommended actions, and the scores for a given target.** Output is model-generated and varies run to run (see [docs/understanding-variability.md](docs/understanding-variability.md)); reproducibility is not part of the contract. Absolute scores are calibrated per model tier and are not comparable across tiers.
- **The HTML report's visual design / CSS / template internals** (`report_template.html`). The HTML is a rendered artifact for humans; only the JSON is the machine contract.
- **Internal scoring guidance** (`knowledge/KB_*.md`) and the SKILL step graph.
