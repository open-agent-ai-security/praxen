# Praxa Render Pipeline — Design Note

**Status:** design proposal, not yet implemented
**Author:** internal
**Date:** 2026-05-02 (initial), revised 2026-05-03 after first-survey discovery

---

## 1. Problem

Today the Praxa skill produces three artifacts at the end of an analysis:

- `<agent>-findings-<date>.json`
- `<agent>-analysis-<timestamp>.html`
- `<agent>-analysis-<timestamp>.txt`

In the current implementation, **all three are produced by the LLM agent itself**, including the HTML. The agent reads the canonical template (`report_template.html`, ~824 lines) and substitutes:

- ~30 scalar `{{PLACEHOLDER}}` tokens
- 4–6 `REPEAT:` blocks (findings, remit rules, RAISE cards, log files, positives)
- 2–3 `PICK:` blocks (variant selection by condition)

Today's full-suite regression run exposed two systemic problems:

| Problem | Evidence |
|---|---|
| **Slow.** A typical render involves 30+ Edit tool calls to substitute placeholders one at a time, plus generating each REPEAT block manually. End-to-end: 8–12 minutes per render. | Suite run: 9 targets in parallel; 5 of 9 hit the 24-minute stream-idle watchdog mid-render. |
| **Unreliable.** Random subset of agents stalls partway through, leaving HTML files with unfilled `{{}}` markers, missing TXT, or bare templates copied without substitution. | FinBot, Sweep, Aider, OpenHands, LangChain SQL — same skill, same template, same workspace size class — non-deterministic outcomes. |
| **Wasteful.** The substitution work is mechanical. There is no judgment call between "JSON entry says severity = Critical" and "card gets `class='severity-critical'`". Spending LLM tokens on this is paying for the wrong thing. | Skill currently spends ~60% of its tokens on rendering. Increases context-window pressure and timeout risk on legitimately complex analyses. |

The right boundary is: **LLM does judgment; code does mechanical transformation.** Findings JSON → HTML should be a deterministic mapping; the LLM should not be in that loop.

## 2. Discovery during initial survey (2026-05-03)

Surveying the 9 fresh JSONs from the v0.1.0 suite run revealed **two issues that the original design did not anticipate.**

### 2.1 The JSON is incomplete

The original design assumed the findings JSON contains everything the HTML renders. It doesn't. About half of what appears in the HTML is prose **synthesized by the LLM at render time** and never captured in JSON:

| HTML section | Source today | In JSON? |
|---|---|---|
| Title, header brand, footer brand | Hardcoded in template | n/a |
| Header status badge (CRITICAL/HIGH/ADVISORY/CLEAN) | Inferred at render time from severity counts | ❌ |
| Intro band: Agent Remit (as declared) — 2-4 sentences | LLM synthesis | ❌ |
| Intro band: Agent Structure (as observed) — 2-4 sentences | LLM synthesis | ❌ |
| Behavior Summary | LLM synthesis | ✅ as `posture.scan_summary` |
| Remit Coverage stat-pill counts (verified/gap/partial/...) | LLM synthesis | ❌ |
| Remit Coverage table (17 rows: rule ID, section, quoted text, status, finding anchor) | LLM synthesis | ❌ |
| Findings Register (cards) | Read directly from findings array | ✅ |
| What's Working Well — positive cards (title, description, evidence path) | LLM synthesis | ❌ |
| Discovered Log Files — table (path, source, content type, purpose, mtime, status) | LLM synthesis | ❌ |
| Logs-empty fallback note | LLM synthesis | ❌ |
| RAISE hero band weighted score | ✅ `posture.posture_score.weighted_overall` |
| RAISE hero band rationale (prose explaining the weighted overall) | LLM synthesis | ❌ |
| RAISE per-category cards: scores | ✅ `posture.posture_score.categories.*.score` |
| RAISE per-category cards: confidence, weight | ✅ |
| RAISE per-category cards: rationale (1-2 sentence prose per category) | LLM synthesis | ❌ |
| Maturity rubric table | Hardcoded in template | n/a |
| Footer: severity counts | LLM-derived from findings array | ❌ |
| Footer: artifact count | LLM-derived from workspace | ❌ |
| Footer: praxa version | Substituted from `--version` arg | n/a |

**Implication:** A renderer reading the current JSON has nothing to put in roughly half the report. The "JSON is the data, HTML is presentation" architecture only works if we **expand the JSON schema** to capture every prose field the HTML displays.

### 2.2 The JSON shape is inconsistent across runs

Of the 9 fresh suite JSONs, 8 are bare lists (`[posture, finding-1, finding-2, ...]`) and 1 (HelperBot) is a top-level object (`{scan: {...}, findings: [...]}`). Different blind runs of the same skill emitted two different shapes. The schema isn't actually nailed down — it has been LLM-improvised per run.

This is fine while the LLM is also doing the rendering (it can adapt to its own output). It is **fatal** to a code renderer.

## 3. Proposed Architecture (revised)

The original two-stage split is still right, but Stage 1 has to do more work than the original design specified:

```
                ┌──────────────────────────────────────┐
   workspace ──▶│   STAGE 1 — Analyze + Synthesize    │──▶ findings.json
                │   (LLM, behavior-verifier skill)    │     (CANONICAL,
   remit ─────▶ │   Step 9 expanded to populate ALL   │      COMPLETE)
                │   prose fields, not just scan_summary│
                └──────────────────────────────────────┘
                                                       │
                                                       ▼
                                          ┌──────────────────────────┐
                                          │   STAGE 2 — Render       │──▶ analysis.html
                                          │   (Python script,        │──▶ analysis.txt
                                          │   purely deterministic)  │
                                          └──────────────────────────┘
```

The skill performs more synthesis up-front (every prose snippet the report displays). The renderer becomes pure substitution — no judgment, no inference, no "if missing, generate something reasonable."

### 3.1 Why this revised split

- **Stronger contract.** The JSON becomes the complete behavioral record, not an analytical subset. Customers who consume only the JSON (dashboards, ticketing, compliance) get the same content humans see in HTML.
- **Renderer stays trivial.** No conditional prose generation, no fallback logic. If a field is missing, fail loudly — that's a skill bug, not a render bug.
- **Diff-friendly.** Two analyses of the same agent become a clean JSON diff, including prose fields.
- **Synthesis cost is paid once.** Today the LLM synthesizes prose during HTML render. Moving it to analysis stage costs the same tokens but they go into the JSON record where they're reusable.

## 4. Canonical JSON Schema

The renaming/expansion of the JSON is the core architectural change. Proposed shape:

```json
{
  "schema_version": "1.0",
  "praxa_version": "0.1.0",
  "scan": {
    "agent": "HelperBot",
    "agent_slug": "helperbot",
    "scan_date": "2026-05-03",
    "scan_timestamp": "2026-05-03T04:12:49Z",
    "workspace": "/tmp/praxa_helperbot/workspace",
    "artifact_count": 5
  },
  "header": {
    "overall_status": "critical"
  },
  "intro_band": {
    "agent_remit_summary": "<2-4 sentences, may include <code> tags>",
    "agent_structure_summary": "<2-4 sentences, may include <code> tags>"
  },
  "behavior_summary": "<2-4 sentence dominant-pattern narrative>",
  "remit_coverage": {
    "stat_counts": {
      "verified": 0, "gap": 15, "partial": 1, "vague": 0, "enp": 1, "total": 17
    },
    "rules": [
      {
        "rule_id": "R-01",
        "section": "Behavioral Constraints",
        "rule_text": "<exact quoted text from remit>",
        "status": "gap",
        "finding_id": "PRAX-2026-05-03-001"
      }
      // ... 17 rows
    ]
  },
  "findings": [
    {
      "id": "PRAX-2026-05-03-001",
      "severity": "Critical",
      "summary": "...",
      "tags": [
        {"kind": "raise", "label": "Implement Zero Trust"},
        {"kind": "owasp_llm", "label": "LLM01 — Prompt Injection"},
        {"kind": "owasp_agentic", "label": "ASI01 — Agent Goal Hijack"}
      ],
      "policy_rule_ids": "R-03, R-04",
      "policy_rule_text": "<quoted text from remit>",
      "evidence": "<multiline string with file:line references>",
      "recommended_action": "<actionable text>",
      "raise_category": "implement_zero_trust",
      "owasp_llm": "LLM01",
      "owasp_agentic": "ASI01",
      "confidence": "High",
      "related_findings": ["PRAX-2026-05-03-002"],
      "escalation": "alert"
    }
  ],
  "positives": [
    {"title": "...", "description": "...", "evidence_path": "..."}
  ],
  "log_files": {
    "present": false,
    "no_logs_note": "No log files found in the workspace. The absence is itself evidence — see PRAX-2026-05-03-004.",
    "rows": []
  },
  "raise_posture": {
    "weighted_overall": 0.45,
    "weighted_rationale": "<prose explaining the overall>",
    "categories": [
      {
        "key": "limit_your_domain",
        "name": "Limit Your Domain",
        "score": 0,
        "confidence": "High",
        "weight": 0.15,
        "rationale": "<1-2 sentence prose>"
      }
      // ... 6 categories in fixed order
    ]
  },
  "footer": {
    "severity_counts": {
      "critical": 5, "high": 9, "medium": 2, "low": 0, "info": 0
    }
  }
}
```

Key principles:

- **Every placeholder in the template has a corresponding JSON path.** No render-time inference.
- **JSON holds semantic data, not presentation.** Severity is `"Critical"`, not `"sev-critical"`; status is `"gap"`, not `"pill-gap"`. The renderer maps semantic values → CSS classes. Skill stays out of presentation concerns.
- **Pre-computed values that are derived from other fields stay out.** No `score_pct` (renderer multiplies score × 20); no `weight_pct` (renderer × 100); no `weighted_contribution` (renderer multiplies). The JSON minimizes redundancy; the renderer composes presentation values.
- **Fixed enumerations.** RAISE categories appear in fixed order; remit rules are pre-numbered; severity ordering is fixed.
- **Backward-incompatible.** This is a new schema. The existing skill's bare-list output is **legacy**. We don't try to render legacy JSONs.

## 5. Component Design

### 5.1 `render.py` — input contract

```
python render.py \
  --findings <path>/findings.json \
  --template <path>/report_template.html \
  --out-html <path>/analysis.html \
  --out-txt  <path>/analysis.txt
```

The Praxa version comes from the JSON's `praxa_version` field, not a CLI arg (single source of truth).

All paths absolute. Exit code 0 on success; non-zero with diagnostic on any error.

### 5.2 Output guarantees

The renderer guarantees:

- 0 unsubstituted `{{...}}` tokens in the output HTML
- 0 unresolved `<!-- REPEAT:name -->` / `<!-- END:name -->` / `<!-- PICK:name -->` / `<!-- Variant A: -->` / `<!-- Variant B: -->` markers
- Footer counts match the Findings Register (renderer derives both from `findings[]` and asserts equality with `footer.severity_counts`)
- Remit stat-pill counts match the actual status grouping in `remit_coverage.rules[]` (renderer asserts equality with `remit_coverage.stat_counts`)
- Anchors in the Remit Coverage table resolve to existing finding IDs
- Categories appear in the fixed RAISE order regardless of input dict order
- Severity ordering (Critical → High → Medium → Low → Informational) enforced
- Output is byte-deterministic: same JSON → same HTML, every run

These were validation steps in the current Step 11; they become hard assertions in code. See §5.8 for the consistency assertion rules.

### 5.3 Schema validation

On entry, the renderer validates the JSON against the schema. Failures produce specific errors:

- `KeyError: behavior_summary` — skill didn't populate this required field
- `ValueError: raise_posture.categories must contain exactly 6 entries (got 5)` — skill missed one
- `ValueError: schema_version 0.x not supported by renderer 1.x` — version mismatch

A small `schema.py` module owns the validation rules. Schema and renderer ship together.

### 5.4 Template syntax — keep, don't replace

The existing template syntax stays. The actual marker forms in `report_template.html` are HTML comments:

| Marker | Form in template |
|---|---|
| Scalar | `{{PLACEHOLDER}}` |
| Repeat begin | `<!-- REPEAT:name -->` |
| Repeat end | `<!-- END:name -->` |
| Pick begin | `<!-- PICK:name -->` |
| Pick variant A | `<!-- Variant A: <hint> -->` |
| Pick variant B | `<!-- Variant B: <hint> -->` |
| Pick end | `<!-- END:name -->` (same as REPEAT end) |

The renderer matches these forms verbatim. Custom mini-engine, ~430 LOC (revised from initial ~150 estimate after gap analysis).

### 5.5 Marker resolution rules

- **`{{SCALAR}}`** — JSON-path lookup via a placeholder→path table held in the renderer. Example mappings:
  - `{{AGENT_NAME}}` → `scan.agent`
  - `{{SCAN_DATE}}` → `scan.scan_date`
  - `{{SCAN_TIMESTAMP}}` → `scan.scan_timestamp`
  - `{{PRAXA_VERSION}}` → `praxa_version`
  - `{{ARTIFACT_COUNT}}` → `scan.artifact_count`
  - `{{AGENT_REMIT_SUMMARY}}` → `intro_band.agent_remit_summary`
  - `{{AGENT_STRUCTURE_SUMMARY}}` → `intro_band.agent_structure_summary`
  - `{{SCAN_SUMMARY_NARRATIVE}}` → `behavior_summary`
  - `{{N_VERIFIED}}` → `remit_coverage.stat_counts.verified` (and similar for gap/partial/vague/enp/total)
  - `{{N_CRITICAL}}`, `{{N_HIGH}}`, … → `footer.severity_counts.*`
  - `{{WEIGHTED_SCORE}}` → `raise_posture.weighted_overall` (formatted to 2 decimals)
  - `{{WEIGHTED_RATIONALE}}` → `raise_posture.weighted_rationale`
  - `{{MATURITY_LABEL}}` — derived (see §5.7)
  - `{{OVERALL_STATUS_CLASS}}`, `{{OVERALL_STATUS_LABEL}}` — derived (see §5.7)
- **`REPEAT:remit_row`** — iterate `remit_coverage.rules[]` in input order. Per-row scalars: `{{RULE_ID}}` `{{REMIT_SECTION}}` `{{RULE_TEXT}}` `{{STATUS_PILL_CLASS}}` (derived) `{{STATUS_LABEL}}` (derived) `{{FINDING_ANCHOR}}` `{{FINDING_ID}}`. Empty finding cell when `rule.finding_id` is null/missing.
- **`REPEAT:finding`** — iterate `findings[]` in severity order (Critical→High→Medium→Low→Informational; ties broken by JSON input order). Per-card scalars: `{{FINDING_ANCHOR}}` (= id) `{{SEVERITY_CLASS}}` (derived) `{{SEVERITY_LABEL}}` (derived) `{{FINDING_ID}}` `{{FINDING_SUMMARY}}` `{{RULE_IDS}}` `{{QUOTED_RULE_TEXT}}` `{{EVIDENCE}}` (joined; see §5.5.1) `{{RECOMMENDED_ACTION}}`.
  - **Nested `REPEAT:finding_tag`** lives inside each finding card. Per-tag scalars: `{{TAG_CLASS}}` (derived from `tag.kind`) `{{TAG_LABEL}}` (= `tag.label`). Renderer handles nesting by resolving the inner REPEAT first per finding instance, then expanding the outer.
- **`REPEAT:raise_card`** — iterate `raise_posture.categories[]` in input order. Skill is responsible for fixed RAISE order (renderer asserts the six known keys are present). Per-card scalars: `{{CATEGORY_NAME}}` `{{SCORE}}` `{{SCORE_PCT}}` (derived) `{{SCORE_CLASS}}` (derived) `{{CONFIDENCE}}` `{{WEIGHT_PCT}}` (derived) `{{WEIGHTED_CONTRIBUTION}}` (derived) `{{RATIONALE}}`.
- **`REPEAT:positive`** — iterate `positives[]`. If empty, the entire REPEAT block (including its delimiting comments) is replaced with `<div class="none-found">No confirmed positive controls were verified during this scan.</div>`. Per-card scalars: `{{POSITIVE_TITLE}}` `{{POSITIVE_DESCRIPTION}}` `{{POSITIVE_EVIDENCE_PATH}}`.
- **`REPEAT:log_row`** — iterate `log_files.rows[]`. Lives inside `PICK:logs_present` variant A. Per-row scalars: `{{LOG_PATH}}` `{{LOG_SOURCE}}` `{{LOG_CONTENT_TYPE}}` `{{LOG_PURPOSE}}` `{{LOG_MTIME}}` `{{LOG_STATUS_CLASS}}` (derived from `row.status` ∈ {active, new}) `{{LOG_STATUS_LABEL}}`.
- **`PICK:logs_present`** — Variant A if `log_files.present == true`. Variant B otherwise (renders `{{NO_LOGS_NOTE}}` from `log_files.no_logs_note`). Renderer resolves PICK first; the surviving block then participates in REPEAT processing.

Resolution order: **(1)** PICK blocks resolved (one variant survives, the other and the marker comments are stripped); **(2)** REPEAT blocks expanded outer-then-inner; **(3)** scalar substitutions applied.

#### 5.5.1 Evidence formatting

`finding.evidence` is `list[str]`. The renderer joins items with `\n` (newline), substitutes into the `<div class="evidence-block">` which has CSS `white-space: pre-wrap`, so newlines render as visible line breaks. Each item is HTML-escaped (see §5.6).

### 5.6 HTML escaping

All scalar substitutions are HTML-escaped by default using `html.escape(s, quote=True)`. Two exceptions are explicit allow-tag fields where the skill may emit `<code>` tags inline (per `SKILL.md` Step 11 rule 10):

| Field | Escape policy |
|---|---|
| `intro_band.agent_remit_summary` | Allow `<code>` only; escape everything else |
| `intro_band.agent_structure_summary` | Allow `<code>` only; escape everything else |
| `behavior_summary` | Allow `<p>` and `<code>` only |
| All other text fields | Full escape |

Allow-tag fields use a small allowlist sanitizer (~30 LOC): parse with stdlib `html.parser`, retain whitelisted tags + their inner text, escape everything else.

Strings inside HTML attribute values (e.g., `id="{{FINDING_ANCHOR}}"`, `style="width: {{SCORE_PCT}}%;"`) are HTML-escaped with `quote=True`. Numeric derived values like `SCORE_PCT` cannot contain dangerous characters but are still passed through `str(int(v))` to enforce type.

### 5.7 Derived-value tables

The renderer computes presentation-layer values from semantic JSON values:

#### Severity → CSS class and label

| `finding.severity` | `{{SEVERITY_CLASS}}` | `{{SEVERITY_LABEL}}` |
|---|---|---|
| Critical | `sev-critical` | `CRITICAL` |
| High | `sev-high` | `HIGH` |
| Medium | `sev-medium` | `MEDIUM` |
| Low | `sev-low` | `LOW` |
| Informational | `sev-info` | `INFO` |

#### Score → CSS class and percent

| `category.score` | `{{SCORE_CLASS}}` | `{{SCORE_PCT}}` |
|---|---|---|
| 0 | `score-0-1` | `0` |
| 1 | `score-0-1` | `20` |
| 2 | `score-2`   | `40` |
| 3 | `score-3`   | `60` |
| 4 | `score-4-5` | `80` |
| 5 | `score-4-5` | `100` |

Formula: `score_pct = score * 20`. (Class names remain for semantic CSS hooks even though the styles are unified — the template explicitly retains them; see template lines 286-307.)

#### Status → pill class and label

| `rule.status` | `{{STATUS_PILL_CLASS}}` | `{{STATUS_LABEL}}` |
|---|---|---|
| verified | `pill-verified` | `Verified` |
| gap | `pill-gap` | `Gap` |
| partial | `pill-partial` | `Partial` |
| vague | `pill-vague` | `Vague Policy` |
| enp | `pill-enp` | `Enforcement Not Possible` |

#### Tag kind → CSS class

| `tag.kind` | `{{TAG_CLASS}}` |
|---|---|
| raise | `tag-raise` |
| owasp_llm | `tag-owasp` |
| owasp_agentic | `tag-agentic` |
| mcp | `tag-owasp` (same brand-blue as LLM tags) |

#### Log status → CSS class

| `row.status` | `{{LOG_STATUS_CLASS}}` |
|---|---|
| active | `log-status-active` |
| new | `log-status-new` |

#### Weighted overall → maturity label and overall status

| `floor(weighted_overall)` | `{{MATURITY_LABEL}}` |
|---|---|
| 0 | Absent |
| 1 | Ad hoc |
| 2 | Partial |
| 3 | Established |
| 4 | Strong |
| 5 | Exemplary |

`{{OVERALL_STATUS_CLASS}}` and `{{OVERALL_STATUS_LABEL}}` derive from the highest severity present in `findings[]`:

| Highest severity present | `{{OVERALL_STATUS_CLASS}}` | `{{OVERALL_STATUS_LABEL}}` |
|---|---|---|
| Critical | `critical` | `CRITICAL` |
| High | `high` | `HIGH` |
| Medium / Low | `advisory` | `ADVISORY` |
| (only Informational, or empty) | `clean` | `CLEAN` |

#### Weight → percent and weighted contribution

`weight_pct = round(weight * 100)` (e.g., 0.15 → 15, 0.25 → 25)
`weighted_contribution = f"{score * weight:.2f}"` (e.g., score 3 × weight 0.25 → "0.75")

`{{WEIGHTED_SCORE}}` is `f"{weighted_overall:.2f}"`.

### 5.8 Counter-consistency assertions

Before writing the HTML, the renderer recomputes derived counts from primitive JSON arrays and asserts equality with the JSON's stated counts:

1. **Severity counts.** `Counter(f.severity for f in findings) == footer.severity_counts` (after normalizing case and including zeros for absent severities).
2. **Remit stat counts.** `Counter(r.status for r in remit_coverage.rules) == remit_coverage.stat_counts` and `len(rules) == stat_counts.total`.
3. **Anchor resolution.** Every `rule.finding_id` (when non-null) must exist in the `findings[]` id set.
4. **RAISE category set.** `{c.key for c in raise_posture.categories} == {limit_your_domain, balance_your_knowledge_base, implement_zero_trust, manage_your_supply_chain, build_an_ai_red_team, monitor_continuously}` (exactly six, matching keys).
5. **Weighted-overall sanity.** `abs(weighted_overall - sum(c.score * c.weight for c in categories)) <= 0.01` (small tolerance for the displayed 2-decimal rounding; renderer does NOT recompute from scratch — that's the skill's job — but flags suspicious drift).

Failure → non-zero exit with a specific message (e.g., `Inconsistency: footer.severity_counts.critical=5 but findings[] contains 6 Critical findings`).

### 5.9 Determinism contract

- Same JSON input → byte-identical HTML output. No timestamps in output beyond what's in the JSON. No locale-dependent formatting (use `'.'` decimal separator regardless of system locale).
- Renderer iterates dicts and lists in the order they appear in the JSON. Python 3.7+ dict iteration order is insertion-order, so `json.load` preserves source order; renderer does not re-sort except where explicitly required (severity order, fixed RAISE order).
- Test enforces this: render twice, `cmp` the outputs.

### 5.10 TXT output

Generated from the same JSON by a separate ~80 LOC formatter. Template is not used for TXT — the format is closer to a stdout log than a templated document, and reusing the HTML template would be more code than just direct printf-style emission. The TXT format mirrors what the LLM currently emits to stdout: agent header, behavior summary, severity counts, RAISE category scores, weighted overall, and Critical findings with their recommended actions.

## 6. Skill Workflow Changes

`SKILL.md` gets two big edits, not one:

### 6.1 Step 9 expansion (NEW)

The current Step 9 is "synthesize the Behavior Summary narrative." It expands to "synthesize ALL the report prose":

- Behavior Summary (existing)
- Intro band: Agent Remit (as declared)
- Intro band: Agent Structure (as observed)
- Per-category RAISE rationales × 6
- Weighted overall rationale
- Remit Coverage rule audit (every rule classified Verified/Gap/Partial/Vague/ENP with status pill class and finding anchor)
- Positives — what's working well
- Log files inventory or empty-note

This is rewritten to walk the LLM through each synthesis explicitly, with examples, and it terminates with a single JSON write.

### 6.2 Step 10 — write canonical JSON

The skill writes the canonical schema (per §4), single file. Validates its own output before exiting Step 10 (count checks, required-field presence).

### 6.3 Step 11 — render outputs

Replaces ~700 lines of substitution rules with:

> **Step 11 — Render outputs.**
> Run: `python skills/behavior-verifier/render.py --findings <out>/findings.json --template skills/behavior-verifier/report_template.html --out-html <out>/analysis.html --out-txt <out>/analysis.txt`
>
> Verify exit code 0. The renderer guarantees 0 unsubstituted markers. If it fails, fix the JSON (typically a missing field; the error message names it) and re-run.

The Step 11 substitution rules and marker conventions move from `SKILL.md` into `render.py` as code comments and tests.

## 7. Distribution

- `skills/behavior-verifier/render.py` ships with the plugin.
- `skills/behavior-verifier/schema.py` ships with the plugin (validation).
- `build.sh` already includes the entire `skills/` tree.
- Python 3.8+ stdlib only. No third-party deps.
- Plugin manifest documents Python 3 as a runtime dependency.

## 8. Testing Strategy

- **Golden-file tests.** A handful of canonical JSONs (one per agent posture class — clean / partial / absent) check into `tests/fixtures/`. Render each. Diff against checked-in expected HTML. Drift = test failure.
- **Schema validation.** Required-field tests, type tests, enumeration tests, count tests.
- **Negative tests.** Malformed JSON, missing categories, mis-ordered severities — verify clear error messages.
- **Round-trip parity (during transition).** Generate HTML both ways on the same JSON; manual diff to confirm no semantic drift.
- **Suite re-run.** After cutover, run all 9 targets again. Confirm wall-clock time per render drops to <1s and zero stalls.

## 9. Phased Rollout (revised — 4 phases)

1. **Phase 1 — Schema + skill update.** Define `schema.py` with the canonical shape. Rewrite `SKILL.md` Steps 9–11 to produce the new JSON. Validate by running the skill against one target end-to-end and inspecting the JSON manually for completeness.
2. **Phase 2 — Renderer build.** Implement `render.py` against the schema. Test against the Phase 1 JSON. Iterate until the rendered HTML is byte-equivalent (or close enough for hand-diff approval) to a reference HTML produced the old way.
3. **Phase 3 — Suite validation.** Run all 9 targets with the new skill + renderer. Confirm baselines still hold (no calibration regression). Confirm wall-clock improvement.
4. **Phase 4 — Clean break.** Remove legacy substitution rules from `SKILL.md`. Update `PRAXA_SPEC.md` §6 with the new schema. Update `docs/interpreting-reports.md` to describe the JSON sections. Tag a v0.2.0 release.

Phase 1 gates Phase 2 — no point implementing the renderer until the schema is tested. Phase 2 gates Phase 3 — no point running the suite until the renderer works.

## 10. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| LLM doesn't reliably populate every prose field per the new Step 9. | Schema validation in `render.py` catches missing fields with specific error messages; skill iterates until clean. Add LLM-readable examples to SKILL.md for each new prose field. |
| New Step 9 is so heavy that the analysis stage now hits the same timeout the rendering stage hit before. | The synthesis was happening anyway, just at render time. Net token usage should be similar or lower (no Edit tool calls). Worst case: split Step 9 into two passes. |
| Renderer behind on a template change. | Template + renderer + schema ship together; CI runs golden-file tests; template edits without renderer updates fail tests. |
| Backward incompatibility with the v0.1.0 JSONs we just shipped in `examples/`. | Acceptable — `examples/` regenerates with the new pipeline. We're a 0.x project; schema break is allowed. Document in CHANGELOG. |
| JSON schema drift between skill versions over time. | `schema_version` field; renderer asserts compatibility; bumping major version requires explicit renderer support. |
| Python not on the operator's machine. | Python 3 is on every macOS/Linux dev box. Windows: document `py -3`. PyInstaller binary as Phase 5 if customers hit this. |
| Behavioral drift: Praxa user expects to hand-edit HTML. | The HTML was always generated; hand-editing was never supported. No-op risk. |
| Hand-diffing rendered HTML in Phase 2 is brittle. | Accept "semantically equivalent" parity, not byte-equivalent. Use HTML pretty-print + structural diff for the comparison. |

## 11. Effort Estimate (revised)

- `schema.py` (canonical schema definition + validators): ~150 LOC
- `render.py` core (template tokenizer + PICK + REPEAT + scalar substitution + HTML escape + derived-value tables + counter assertions + nested REPEAT): ~430 LOC
- TXT formatter: ~80 LOC
- Allow-tag sanitizer (for the three allow-tag prose fields): ~30 LOC
- `SKILL.md` Step 9–11 rewrite + new prose-synthesis examples (12+ new prose fields, each needs an LLM-readable example): ~2 days
- Test harness + 3 golden fixtures: ~half a day
- Skill ↔ renderer parity validation (Phase 2): ~half a day
- Suite re-run (Phase 3): ~1 hour wall-clock + ~half a day to review and update baselines
- Documentation (PRAXA_SPEC.md §6, RAISE.md, interpreting-reports.md): ~half a day

**Total: ~5–7 person-days.** Up from the revised 4-5 estimate after the gap analysis in §5.5–5.9. The win is unchanged on the runtime side (>10× faster, eliminates timeout-stall failure mode) and bigger on the architectural side: JSON consumers get the complete report content, not just the findings list.

## 12. Open Questions

1. Should `render.py` be invokable standalone? Recommend yes — operator hands a JSON to support engineer who regenerates HTML.
2. Should the renderer support a `--strict` vs. `--lenient` mode? Recommend strict-only. Lenient masks bugs.
3. Should the new schema be versioned in the file path (e.g., `findings-v1.json`)? Recommend no — `schema_version` field is sufficient.
4. Should we keep the "bare-list-of-findings" shape supported as a legacy ingest path for old JSONs? Recommend no — clean break, document in CHANGELOG.
5. Is there value in a TXT-only renderer mode? E.g., for headless CI summaries. Recommend yes — `--out-txt` alone (no `--out-html`) works.
6. Where does `header.overall_status_class` come from? **Decision:** the skill computes it during Step 9 synthesis (formulaically: highest severity present in `findings[]` → critical/high/advisory/clean).
7. Should `severity_class`, `score_class`, etc. be in the JSON, or computed by the renderer? **Decision:** computed by the renderer. The JSON should hold semantic data; CSS class names are presentation. Updated §4 accordingly.
8. The original Open Question about same-skill-directory vs sibling-skill stands: same directory, version-locked.
