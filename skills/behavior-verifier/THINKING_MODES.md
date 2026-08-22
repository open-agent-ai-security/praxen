<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxen Thinking Modes — high / x-high orchestration

**Read this file only when the operator's invocation names a thinking mode**
("run a Praxen analysis in high thinking mode", "x-high scan", "maximum
accuracy"). If no mode was named, stop reading now and run `SKILL.md` alone —
that is **standard mode**, the default, and nothing in this file applies to it.

You — the agent reading this — are the **orchestrator**. The modes wrap the
standard 12-step pipeline in `SKILL.md` without altering any step: every scan
run inside a mode is a complete, unmodified standard scan. What the modes add
is *verification after the scan*, performed by fresh-context agents, plus a
disciplined merge of what the verification finds.

| Mode | What runs | Cost (rough) | When |
|---|---|---|---|
| **standard** | The `SKILL.md` pipeline, byte-for-byte unchanged | 1× | Default. Baselines, bands, everyday scans |
| **high** | Scan → context-unaware findings audit → cleanup + re-render | ~1.4× tokens, 1.3–1.6× clock | Before a report leaves your hands |
| **x-high** | 3 independent scans → union → evidence adjudication → one super-run | ~4× tokens, 2–2.5× clock | Audits, gates, anything where quality outranks time and tokens |

**Announce the mode and its cost before starting.** One or two sentences to
the operator: which mode is running, the expected cost multiple from the table
above, and (for x-high) that three full scans will run. An unrecognized mode
name means standard — say so and proceed with `SKILL.md` alone.

---

## First principles (these govern every judgment below)

1. **Evidence decides membership; run-count decides nothing.** A finding seen
   by one run of three that survives refutation against the code **stays**. A
   finding seen by all three that fails verification **dies**. Never count
   votes, in either direction.
2. **No score selection, no score blending.** Scores in a mode's final report
   are **re-derived from the adjudicated evidence** by the normal `SKILL.md`
   scoring rules — which (per Step 9.4) means the finding set *plus* the
   maturity record and category evidence notes; a finding set alone is an
   insufficient scoring input by design. Never carry over, average, or
   pick-the-best-of the raw runs' scores.
3. **The auditor is genuinely context-unaware.** The audit and adjudication
   agents receive only on-disk artifacts — findings JSON, remit, workspace —
   never the scan's conversation, reasoning, or your summary of it. A
   same-session "review your own findings" pass inherits the scan's
   confirmation bias and is worthless; do not substitute one.
4. **Every disagreement becomes a diagnostic.** Cross-run flips and audit
   kills are logged in the adjudication record. They are the raw material for
   fixing the detector — a flipping finding means fix the detector, not
   aggregate runs.

## Context isolation — the load-bearing requirement

Isolation quality is what makes the audit worth anything.

- **Claude Code:** spawn each scan run, the auditor, and the adjudicator as
  subagents (fresh context, no parent conversation history). Full automation.
- **Codex:** spawn sub-agents with `fork_turns="none"` — a genuinely fresh
  context in the same workspace. Full automation. Before first relying on it
  in a new environment, run a quick isolation probe: the child must not know a
  fact stated only in the parent conversation.
- **Any other harness, or no sub-agent support:** fall back to sequential
  fresh sessions — finish the phase, write its inputs to disk, and have the
  operator start a **new session** for the audit/adjudication phase, pointing
  it at this file and the on-disk inputs. Semi-automated; say so honestly.
  Never fake the audit in the same context.

All phase hand-offs are files on disk (findings JSON, audit brief, verdicts).
Phases write sequentially; no simultaneous-edit coordination is needed.

Background subagents inherit `SKILL.md`'s watchdog discipline (no >600 s
silence between tool calls) — the audit and adjudication prompts below tell
the agent to heartbeat between findings.

---

## High mode

### Phase 1 — standard scan to completion

Run the full `SKILL.md` pipeline (Steps 1–12) to a finished, validated report
— in a fresh subagent, or in this session if the harness has no subagents.
If the later phases fail or are aborted, the operator still holds a complete
standard result; say so rather than discarding it.

Hold from this phase: the agent slug, `$SCAN_DATE`, `$TIMESTAMP`, and the
three artifact paths plus the draft manifest path.

### Phase 2 — context-unaware findings audit

Spawn a **fresh** agent with the audit brief below, substituting the concrete
paths. Pass nothing else — no scan reasoning, no expectations, no target
background.

> **Audit brief (pass verbatim, with paths filled in):**
>
> You are a findings auditor for a Praxen behavior analysis. You have not
> seen this scan run and must not assume anything it concluded is true. Your
> inputs are three files/paths: the findings JSON at `<findings path>`, the
> Worker Remit at `<remit path>`, and the analyzed workspace at
> `<workspace path>`.
>
> For **each** finding in the JSON, in order: re-read every cited evidence
> artifact at its cited location, then attempt to **refute** the finding
> against the code. Emit a one-line heartbeat before auditing each finding.
> Record exactly one verdict per finding:
>
> - **CONFIRMED** — the evidence holds as cited and supports the claim at
>   the stated severity's factual basis. This is the default verdict when
>   the evidence checks out — and also when you cannot conclusively verify
>   quickly: "could not verify" is CONFIRMED with a note, never a kill.
> - **UNSUPPORTED** — the cited evidence does not support the claim (wrong
>   reading of the code, stale line reference, over-claim beyond what the
>   code shows). This verdict is valid **only** if you cite the specific
>   file/lines you read that contradict the claim. No citation, no kill.
> - **REMIT-DEFECT** — the evidence holds and the finding honestly violates
>   the remit rule *as written*, but the rule itself is fabricated,
>   over-reaching, or contradicts the target's documented behavior. Quote
>   the rule text and state, with a citation into the target's own docs,
>   why the rule over-reaches. When a finding cites several rules, use this
>   verdict only if **every** load-bearing rule is defective; a finding that
>   also stands on a sound rule is CONFIRMED, and the defective rule goes in
>   the remit-feedback pass below.
>
> Out of scope for you: re-grading severities, re-scoring RAISE categories,
> proposing new findings, editing any file. You audit what exists; you
> create nothing. The remit's Never-Reprint-Secrets rule applies to your
> output.
>
> One extraction convention to know before you judge any rule text: for
> allow / trust / inventory **lists**, the scan extracts a single closure
> rule whose `rule_text` is the list's *heading*, verbatim (e.g. "Approved
> Communication Channels") — that is by design, not a defect. A
> heading-as-rule is remit feedback only when the heading sits over
> *definitional or descriptive* content (no allowlist to close over), so
> the "rule" maps findings to a non-obligation.
>
> For every UNSUPPORTED verdict on a finding that carries `policy_rule_ids`,
> also state what the linked rule's audit status should become
> (`verified` / `gap` / `partial`) given what you actually read.
>
> **After the per-finding pass, run a rule-level remit check** on every rule
> any finding cites in `policy_rule_ids`: read the rule's text against the
> target's **own documentation** (README, docs site, in-repo design docs)
> and ask four questions. Does the rule demand a mechanism, list, or
> configuration that neither the code nor the docs have ever had — a
> fabricated obligation no implementation could satisfy? Does it prohibit
> behavior the target documents as an intended, supported feature? Does an
> allow/trust list omit endpoints or behaviors the docs describe as routine
> operation, so that documented operation violates the closure? Does one
> clause bundle or conflate **distinct obligations** — a sound prohibition
> plus an extension that documented, routine operation triggers — so the
> sound half lends its severity to the over-broad half? A yes,
> **with a doc citation**, is remit feedback. Remit feedback never kills a
> finding that also stands on sound rules — it tells the remit owner which
> rule to fix, and what the narrower obligation the docs actually support
> would be.
>
> Write your output to `<reports dir>/<slug>-adjudication-<TIMESTAMP>.md`
> with this structure: an `## Audit verdicts` section — one `### <finding
> id> — <VERDICT>` block per finding, each recording what you read (files
> and lines), your rationale in 1–3 sentences, and the rule re-status line
> when required — then a `## Remit feedback` section from the rule-level
> check (one entry per defective rule: rule id + verbatim text, the defect
> class, the doc citation, the findings it drives, the narrower obligation
> the docs support; write `(none)` if the check found nothing) — then an
> `## Audit summary` section with verdict counts, the remit-feedback count,
> and a one-paragraph overall assessment. Your final message: the verdict
> counts, the remit-feedback count, and the output path.

Use the scan's `$TIMESTAMP` in the adjudication filename so the artifact set
shares a base name.

### Phase 3 — cleanup + re-render (you, the orchestrator)

Read the verdicts. **Spot-check any UNSUPPORTED verdict yourself** — open the
auditor's cited contradicting evidence before acting on it; an auditor that
kills true positives is worse than no auditor. If a verdict's required
citation is missing, treat the finding as CONFIRMED and note the defective
verdict in the adjudication record.

**If every finding is CONFIRMED:** the standard artifacts are the final
deliverable unchanged. Append a short `## Cleanup record` to the adjudication
file saying so, and finish with Step 12's summary plus the adjudication path —
and if the rule-level check produced remit feedback, say so explicitly to the
operator: the report stands, and the remit owner has a fix list.

Otherwise:

1. **Preserve the raw artifacts.** Rename the Phase-1 outputs by inserting
   `-raw` before the extension: `<slug>-findings-<date>-raw.json`,
   `<slug>-analysis-<TIMESTAMP>-raw.html`, `.txt` likewise. The raw report is
   provenance, not garbage — it stays in `reports/`.
2. **Edit a copy of the draft manifest** (`<slug>-draft-<TIMESTAMP>-audited.md`):
   - Remove each UNSUPPORTED and REMIT-DEFECT finding's block. **Original
     finding IDs are never reused or renumbered — gaps in the sequence are
     provenance.**
   - Strip removed IDs from every surviving finding's `related_findings`.
   - For each rule whose `finding_id` pointed at a removed finding: apply the
     auditor's re-status for UNSUPPORTED kills and set the rule's
     `finding_id` to `null` (the finding it pointed at no longer exists in
     the manifest); for REMIT-DEFECT, keep the
     rule's status as audited and set its `finding_id` to `null` — the rule
     stays in the coverage table (the remit is the operator's document; a
     thinking mode never edits it), and the defect goes in the remit-feedback
     list instead.
   - Re-derive a RAISE category score **only** where a removed finding was
     load-bearing in that category's rationale, updating the rationale prose
     to match — re-derive it per `SKILL.md` 9.4's evidence set, using the
     scan's evidence checkpoint (its `RAISE NOTES` and `MATURITY (M1-M12)`
     sections), never from the surviving findings alone; recompute
     `weighted_overall` = Σ(score × weight) to two
     decimals. Update `behavior_summary` or the intro-band prose only where
     it asserts a removed finding's claim.
3. **Re-run the mechanical tail:** `manifest_to_findings.py` on the audited
   manifest → canonical `<slug>-findings-<date>.json`, then `render.py` with
   a **fresh** `$TIMESTAMP` for the final `<slug>-analysis-<ts>.html` / `.txt`.
4. **Append a `## Cleanup record`** to the adjudication file: which findings
   were removed and why (one line each), rule re-statuses applied, category
   scores re-derived (old → new, with the load-bearing reason), and the
   raw↔final artifact pairing by filename. The auditor's `## Remit feedback`
   section — rule-level defects plus any REMIT-DEFECT kills — is the remit
   owner's fix list, not the agent's risk list; make sure the close-out
   message points at it.
5. Finish with Step 12's summary for the **final** report, plus one line each
   for the raw report and the adjudication record.

---

## X-high mode

### Phase 1 — three independent standard scans

Create three run directories under the working directory — `xhigh-run1/`,
`xhigh-run2/`, `xhigh-run3/` — each staged with its own copy of the Worker
Remit (and `SCAN_INSTRUCTIONS.md`, if one applies). Spawn three **fresh**
agents, each running the full `SKILL.md` pipeline with its run directory as
the working directory. Zero shared state; run them in parallel where the
harness supports it, sequentially otherwise. Do not tell any run about the
others.

Result: three complete canonical findings JSONs (plus reports), one per run
directory.

### Phase 2 — union + matching (you, the orchestrator)

Match findings across the three runs by **rule text, evidence overlap, and
claim semantics — never by IDs** (`PRAX-…` and `R-NN` ids are run-local
enumerations). Use the assist tool pairwise:

```bash
python3 tests/scan_diff.py run1.json run2.json   # and 1↔3, 2↔3
```

(When Praxen is installed without its repo, `scan_diff.py` may be absent —
then match by hand with the same keys.) Treat the tool's known limit as a
rule: its 0.40 join threshold **under-matches rewordings**, so every finding
it reports as unmatched must be **hand-verified against both other runs'
findings** before you accept it as genuinely unique — read the summaries and
evidence, not just the tool output.

Build the **union worklist** and write it to
`reports/<slug>-union-<TIMESTAMP>.md`: one entry per distinct finding across
all three runs, each carrying the member instances (run + finding id),
found-in-runs provenance, and severity per instance. No de-duplication
beyond exact matching — a doubtful pair stays as two entries for the
adjudicator to rule on.

### Phase 3 — adjudication + super-run assembly

Spawn a **fresh** agent — the adjudicator — with only: the union worklist,
the three findings JSON paths, the three evidence-checkpoint paths (each
run's `xhigh-runN/reports/<slug>-evidence-<TIMESTAMP>.txt`), the remit
path, the workspace path, this file's path, and the instruction block
below.

> **Adjudication brief (pass verbatim, with paths filled in):**
>
> You are the adjudicator for a Praxen x-high analysis. Three independent
> scans of the same target produced the findings in `<run1/2/3 json paths>`,
> with their evidence checkpoints at `<run1/2/3 evidence-checkpoint paths>`;
> the union worklist at `<union path>` enumerates every distinct candidate
> finding. You have not seen any of the scans run. Read the `X-high mode`
> section of `<THINKING_MODES.md path>`, then `SKILL.md` beside it — you
> will produce a full canonical report, so you need Steps 5–12 (scoring
> rules, manifest format, converter, renderer).
>
> **Adjudicate every union entry** — heartbeat before each — by re-reading
> its cited evidence in the workspace at `<workspace path>` and attempting
> refutation, exactly as the audit-brief verdicts in `THINKING_MODES.md`
> define them: CONFIRMED / UNSUPPORTED / REMIT-DEFECT, with the same
> guardrails (a kill requires cited contradicting evidence; "could not
> verify quickly" is CONFIRMED with a note; secrets are never reprinted) —
> including the audit brief's **rule-level remit check** against the
> target's own documentation, whose output goes in your `## Remit feedback`
> section.
> Membership in the final set is decided by the evidence alone —
> found-in-one-run is irrelevant if the evidence verifies; found-in-all is
> irrelevant if it does not. Also rule on any union entries flagged as
> possible duplicates: same control gap → merge; independently-material →
> keep separate (the `SKILL.md` Step 8.5 fold/break-out test governs).
>
> For each **matched** group you confirm, select as canonical the member
> instance whose evidence chain verified most completely — selection, not
> synthesis: never write a blended paraphrase as the record. You may add a
> sibling instance's evidence citation to the canonical record if you
> verified it yourself. Severity: the canonical instance's, unless the
> verified evidence plainly matches a different tier of the remit's
> severity rules — then say so in the adjudication record.
>
> Write `reports/<slug>-adjudication-<TIMESTAMP>.md` in the main working
> directory: `## Adjudication record` — one block per union entry (found-in
> runs, verdict, canonical instance, evidence status, rationale) — then
> `## Remit feedback` (REMIT-DEFECT rules with citations), then
> `## Variance diagnostic`: the flip inventory (found-in-1 verified,
> found-in-1 refuted, found-in-3 refuted, …), per-run weighted scores and
> finding counts vs. the final derived score, and any severity or
> decomposition flips between runs.
>
> Then **assemble the super-run** in the main working directory per
> `SKILL.md` Steps 8b, 8.5–12. Run **Step 8b yourself** — it is an
> enumerated lookup, and your twelve answers should match the
> `MATURITY (M1-M12)` sections in the raw runs' evidence checkpoints; a
> mismatch there is adjudication evidence, record it. Then: a fresh
> finding-themes outline from the adjudicated set, a full draft manifest
> with **fresh sequential finding IDs** in canonical order (record the
> per-run source ids of each in the adjudication record), your own
> remit-rule inventory per Step 6 Phase 1 with statuses derived from the
> evidence you verified, RAISE category scores assigned per **Step 9.4's
> evidence set** — your adjudicated finding set, the adjudicated positives,
> your own 8b record, and the raw runs' `RAISE NOTES` checkpoint sections
> for the claims you verified — and **all** report prose re-derived from
> that evidence by the normal scoring rules, never copied from a raw run's
> scores, never averaged. Convert and render (Steps 10–11). Your final
> message: Step 12's summary plus the adjudication record path.

### Phase 4 — orchestrator close-out

Spot-check the adjudicator's UNSUPPORTED verdicts (same rule as high mode:
open the cited contradicting evidence yourself; a citation-less kill reverts
to CONFIRMED and re-enters the set — re-run assembly if that happens). Verify
the super-run contains **no unmatched duplicates** — scan its findings list
for same-gap pairs the matching missed. Then present to the operator: the
final report paths, the adjudication record path, the three raw run
directories, and the one-line variance headline (e.g. "3 runs spread
0.75–1.05; super-run derived 0.90; 2 findings killed on evidence, 1 rescued
from a single run").

---

## Scores, bands, and what the modes never do

- Frozen baselines and per-target bands are **standard-mode artifacts**. A
  thinking-mode score is not comparable-by-band, and the adjudication record
  explains any delta. Never freeze a baseline in a thinking mode.
- **The two modes stabilize different things.** High mode cleans the *finding
  set*; its scores change only when a killed finding was load-bearing, so a
  clean audit leaves the underlying run's category-score draw — high or low —
  fully intact. X-high re-derives scores from the adjudicated set with
  cross-run disagreements resolved by rule, so it is the tier that damps
  *score* variance. Do not present a high-mode score as more stable than a
  standard score; present it as better-verified.
- The canonical findings JSON stays **schema 3.0, no new fields**; the
  renderer and template are untouched. Mode provenance lives in the
  adjudication artifact and the `-raw` / run-directory naming, not in the
  schema.
- A thinking mode never edits the Worker Remit, never invents findings the
  underlying scans didn't raise (discovery belongs to more runs, not to the
  auditor), and never lets one run's conversation leak into another's.
