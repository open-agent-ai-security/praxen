<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxen 1.3 — Detection Coverage, Output Quality & Reach

> Drafted 2026-07-15 alongside the revised `RELEASE_1.2_PLAN.md`. This holds
> everything deliberately cut from 1.2 when it was re-scoped to harness
> reliability + scoring stability. Deliberately lower-fidelity than the 1.2
> plan — it will be re-triaged when 1.2 freezes, against whatever 1.2's
> stage gates actually showed. Branches from `1.2` once frozen.

## Objective

With scans reliable and scores stable (1.2), widen what Praxen *finds* and
polish what it *emits*. Detection additions move numbers → 1.3 re-freezes
`v1.3-claude48`, graded vs `v1.2-claude48`. That freeze is why the detection
items travel together here rather than dribbling in: one release, one freeze.

## Buckets

### A · Detection additions *(the re-baseline justification — land all before the freeze)*

- **#65 item 4** — IaC/deployment artifacts as first-class Step-4 discovery
  surfaces (Helm values, K8s manifests, Terraform, docker-compose). The
  uAgents committed-Helm-seed Critical was found by manual luck; this makes it
  systematic. Cheap, high-yield.
- **#41** — named detection pattern: external API response → filesystem write
  (path-traversal class; the missed Hermes CVE-2026-7396 is the proof case).
- **#104** — entropy-based secret detection in `render.py`'s redaction
  backstop (catch high-entropy credentials the pattern list doesn't know).

### B · Coverage & roster

- **#70 (retitled in 1.1.1)** — replace the retired DB/NL-to-SQL archetype
  with a live SQL-agent target, or explicitly accept the gap and close. The
  only roster archetype dropped un-replaced in 1.0.2.
- **LLM05 specialist target** — downgraded from "known gap" to nice-to-have
  after 1.1 recovered LLM05 on existing targets (4P/6S); add only if a strong
  live candidate appears.
- **`scan_type: framework` (#65 item 5)** — `deployed_agent | framework | sdk`
  in the remit identity table; report framing + scoring guidance acknowledge
  operator-configurable defaults. **Gated on the O5 decision**
  (`PHASE1_OPEN_ISSUES.md`): confirm the uAgents framework-posture framing
  first — one operator paragraph, needed regardless.
- **Directional-lean correction** — only if 1.2's anchored check dispositioned
  it as structural-but-uncorrected; otherwise strike.

### C · Output quality & report UX *(no scan-behavior change)*

- **#113** — wrap technical tokens in `<code>` consistently across prose
  fields *(model-output change — schedule before the freeze, with bucket A)*.
- **#27** — finding default-state (collapsed/expanded) + expand/collapse-all.
- **#6 remainder** — render polish: finding-card confidence, Medium/Low badge.
- **#25** — split output-authoring conventions out of `SKILL.md`
  (rendering/MVC split). Refactor only; no output change.

### D · Harness reach & docs *(no baseline impact — may ship earlier as 1.2.x satellites)*

- **#151** — Google Antigravity (`agy` CLI) harness: packaging + docs only,
  engine unchanged. An external contact is waiting; there is no engineering
  reason this must wait for 1.3 — pull forward whenever convenient.
- **#65 items 6–8** — remit-authoring guidance: code-first warning block,
  mechanism-vs-property rule note in the remit template, absence-of-evidence
  confidence calibration in `KB_RAISE_SCANNING.md`. *(Item 6–8 wording changes
  what remit authors write, not what the scanner scores against committed
  remits — safe outside the freeze.)*
- **#117** — challenging-findings.md additions (gated on #118; collapses to a
  one-paragraph note if #118 isn't adopted) · **#118** operator override +
  finding-revision records (schema-contract change — if adopted, it must ride
  a re-baseline release, this one or later) · **#135** docs simplicity pass ·
  **#4** SKILL authoring aids · **#90** shared org design system · **#2**
  standing config *(still explicitly deferred)*.

## Sequencing

A + #113 (everything that changes findings or model prose) → C/D in any order
→ **one re-freeze `v1.3-claude48`, last.** Same discipline as 1.2: nothing
that moves numbers lands after the freeze; a stressed schedule drops whole
buckets by dated plan amendment, not by silent descope.

## Success metric (first cut — re-triage at 1.2 freeze)

- **Detection:** each bucket-A pattern demonstrated on its proof case (Helm
  seed class, path-traversal class, entropy-caught secret) in the frozen set
  or a fixture.
- **Coverage:** the #70 decision executed (target added and characterized
  median-of-3, or gap formally accepted); coverage pages regenerated with no
  undocumented zero columns (P+S counting, per the 1.2 rule).
- **Stability holds:** the 1.2 gates re-pass on the 1.3 stack — zero watchdog
  deaths on the freeze runs; calibration-target |drift| ≤ 0.2 vs
  `v1.2-claude48`. New detection must not cost the reliability and scoring
  stability 1.2 just bought.
