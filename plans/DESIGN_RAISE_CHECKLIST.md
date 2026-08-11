<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Design — RAISE checklist scoring (#195)

> **STATUS: DRAFT — 2026-08-11.** A structural alternative to the anchor-sharpening
> approach #195 originally proposed. Replaces six holistic 0–5 maturity judgments
> with a decomposed, evidence-anchored checklist aggregated arithmetically.
> Not scheduled; a schema-and-template change, so it rides a re-baseline (1.4+).
> Eval results against real targets: `RESULTS_CHECKLIST_EVAL.md`.

---

## 1. Why the current model wobbles

#195 diagnosed band-edge ambiguity and proposed sharper prose anchors. The
1.3 x-high validation localised the residual variance precisely: across two
targets × two adjudicated super-runs, **five of six categories agreed exactly**,
and the entire pair delta was one category moving one notch. Finding-level
adjudication did not help, because the variance is not in the findings.

Three structural causes, none of which prose anchoring touches:

**a. The scale is not being used as a scale.** Category scores across the
12-target v1.2-opus5 baseline:

```
target                           LYD BKB  ZT MSC  RT  MC   wtd
aider                              2   1   2   3   1   1  1.70
autogen-code-executor              2   1   2   2   1   1  1.55
craftbot                           2   1   1   1   0   3  1.30
deepagents-cli                     2   2   2   3   3   1  2.15
finbot                             2   1   0   1   1   1  0.90
helperbot                          0   1   0   1   1   1  0.60
hermes-agent-desktop               3   2   3   2   3   2  2.55
openai-customer-service            2   2   1   3   0   3  1.75
openhands                          2   2   2   3   1   2  2.00
salesforce-help-agent-accelerator  3   2   2   2   0   1  1.70
uagents                            3   2   2   1   1   1  1.70
yaah                               3   2   2   3   1   2  2.15
```

No category scored **4 or 5 anywhere** — 72 cells, top third of the scale
unused. Each category empirically uses ~3 of 6 bands, and the values are
non-contiguous (LYD skips 1; RT skips 2), which is the signature of a coarse
classifier wearing numeric labels rather than an ordinal scale.

**BKB uses exactly two values, 1 and 2, across all twelve targets.** A category
with no headroom is permanently at a band edge: every BKB call *is* the 1↔2
coin flip. BKB is a flipper on both wide-variance targets. This is a complete
mechanical explanation, and no anchor rewording can fix it.

**b. Quantization amplifies.** `weighted_overall` is six integers × fixed
weights, so the minimum possible move is one band × one weight — 0.25 for Zero
Trust, 0.15 for the rest. There is no way to express "slightly worse." A single
judgment change is always a visible headline change.

**c. The maturity labels are imported and unobservable.** *Absent / Ad hoc /
Partial / Established / Strong / Exemplary* is CMM-flavoured **organizational
process** maturity, appraised by interviewing an organization. Praxen assesses
an artifact snapshot. "Documented controls consistently applied" (3) and
"automated, continuously tested" (5) describe a company, not a repository —
which is why the corpus never reaches them.

## 2. What the source material actually says

Re-read of *The Developer's Playbook for LLM Security*, Ch. 12 (pp. 157–173),
the origin of RAISE:

- RAISE is a **six-step process framework plus a 17-item binary checklist**.
- There is **no 0–5 scale, no maturity labels, no weights, and no weighted
  decimal** anywhere in the source. All of that is Praxen-original (the KB
  footer credits the earlier RUBRIC.md, not the book).
- The book's own decomposition: LYD 2 items, BKB 2, ZT 3, MSC 5, RT 2, MC 3.

**We replaced the author's checklist with a holistic judgment, then spent
months trying to stabilise the aggregate we had replaced it with.** Restoring
the checklist shape is simultaneously the variance fix and a fidelity fix.

Two fidelity gaps found in the same pass, both in flipping categories:

- **BKB** — the book frames it as a *balance*, naming under-provisioning
  (too little grounded data → hallucination) as one of two failure modes. The
  KB's BKB signal table is entirely about too-much / unvalidated data. Half
  the construct is unoperationalised, which is consistent with BKB having no
  usable range.
- **BKB, second gap (found 2026-08-11 in eval §2.5)** — neither the KB signal
  table nor the first draft of this checklist named **tool results and
  execution output** as untrusted content entering context. The KB lists
  "external content (email, web, user uploads)" only. For agentic targets this
  is the dominant channel. Item BKB-5 corrected; the shipping KB has the same
  gap and needs its own fix.
- **MSC** — the book's items are training-data oriented (dataset provenance,
  poisoning, bias); the KB's are dependency/plugin/credential oriented. Sound
  adaptation for agent repos, but "account for bias in training data" has no
  representation at all, and "credentials in workspace files → Critical" is
  filed under supply chain when it is secrets hygiene.

## 3. Design

### 3.1 Principles

1. **Grade the practice, not the org chart.** The book's items encode
   builder-self-assessment assumptions ("use a human-led team"). Every item is
   restated as an observable practice.
2. **Every item names its satisfying evidence classes.** Calibration lives at
   item granularity, where it is concrete, rather than at band granularity,
   where it is adjectives.
3. **Evidence classes are drawn from real repositories**, never invented — see
   §5 and the eval doc. **A count of files matching a naming pattern is a place
   to start looking, never a finding**; the first eval published such counts and
   two of four were false (eval §2.0).
4. **Absence of evidence still scores as absence** (existing KB principle), but
   is *reported* distinctly, with the artifact that would change it.
5. **Aggregation is arithmetic**, performed in code, not by the model.

### 3.2 Division of labour — what the model does, what code does

**The model answers every item. Code does nothing but arithmetic.** This is not
a mechanization proposal, and the checklist is not a grep list.

| | Who | Why |
|---|---|---|
| *"Is this file adversarial security testing, or adversarial content that is part of the product?"* | **Model** | Requires reading the code and understanding intent. Pattern matching cannot do it — see the eval's false positives, where a deliberately-vulnerable app, a skill *about* red-teaming, and an input sanitiser all matched the same patterns. |
| *"Does this evidence make the item MET, PARTIAL, or NOT MET?"* | **Model** | A judgment about evidence sufficiency. |
| *"What number does that add up to?"* | **Code** | Arithmetic. There is no judgment here and the model should not be near it. |

Evidence classes in §4 are **guidance for a reader**, not patterns to match.
They tell the model what would satisfy an item; they do not tell it where to
`grep`.

#### Why this reduces variance even though the model answers everything

The fix does not come from determinism in observation. It comes from three
places:

1. **The scale mapping leaves the model entirely.** Today the model must answer
   two questions at once: *how good is this?* and *what integer on a 6-point
   CMM scale represents that?* The second has no ground truth — it is an
   arbitrary mapping — and that is where the coin flip lives. Under the
   checklist the model only ever answers questions about evidence.
2. **Each question is narrower and better posed**, so per-judgment error is
   lower than for one unconstrained holistic call.
3. **Errors become partially independent** across 39 items and partially
   cancel, instead of quantizing into one visible band jump.

**The RT eval is direct evidence for (1).** The model had no difficulty seeing
that aider, finbot, uagents and yaah contain no adversarial testing — the
*observation* was never in doubt. What wobbled was whether "no adversarial
testing" maps to 0 or to 1: seven targets got 1, three got 0, on identical
emptiness. Observation was fine; the mapping was the coin flip. Removing the
mapping from the model's job is the fix, and it survives every item being
LLM-answered.

### 3.3 Answer values

| Value | Meaning | Points |
|---|---|---|
| **MET** | Evidence shows the control exists and is enforced | 1.0 |
| **PARTIAL** | Exists but soft, incomplete, or unenforced (e.g. prompt-only) | 0.5 |
| **NOT MET** | Looked where it would be; it is not there | 0.0 |
| **NOT EVIDENCED** | Nothing in scope could decide it | 0.0 |
| **N/A** | Item does not apply to this architecture | excluded |

**NOT EVIDENCED scores identically to NOT MET, and reports differently.**
Charity credit for missing evidence would let an empty repository score well.
But the report names the artifact that would settle it — *"not evidenced;
supply your CI configuration, red-team reports, or log-shipping manifests and
rescan."* That converts the epistemic limit into the product's feedback loop:
**don't like your score in a category? Provide more evidence.**

**N/A must be justified from the target's architecture** and is listed in the
report with its justification. Unjustified N/A is the obvious gaming vector.

### 3.4 Aggregation

```
category_score (0–5) = 5 × (points_earned / points_applicable)      # 1 decimal
weighted_overall     = Σ (category_score × category_weight)          # weights unchanged
evidence_coverage    = decided_on_direct_evidence / applicable_items
```

Weights are **deliberately unchanged** (ZT 25%, others 15%). The checklist
makes the weighting question explicit and re-openable — the source's only
quantitative signal, item counts, would make MSC heaviest, not ZT — but
changing weights is a separate decision, not a side effect of this one.

**Resolution improves ~3×.** Minimum move today is one band × weight: **0.25**
(ZT) or **0.15** (others). Under the checklist, minimum move is a half-credit
step on one item:

| Category | Items | Min step (today → checklist) |
|---|---|---|
| Zero Trust | 8 | 0.25 → **0.078** |
| Manage Supply Chain | 7 | 0.15 → **0.054** |
| Limit Domain / BKB / Red Team / Monitor | 6 | 0.15 → **0.063** |

Beyond finer granularity, the errors become **independent**: 39 narrow
judgments whose disagreements partially cancel, versus 6 judgments where one
disagreement *is* the delta. That is the variance hypothesis (mechanism in §3.2) — it is a
hypothesis, and the replay bench (§6) is how it gets measured, not asserted.

### 3.5 Evidence coverage as a second axis

Today "we looked and it is bad" and "we could not see much" produce
indistinguishable reports. Publishing evidence coverage alongside the score
separates them, and is a more useful honesty signal than the current
per-category confidence prose.

---

## 4. The checklist

39 items. Item text is the *question*; evidence classes are what satisfies it.

### LYD — Limit Your Domain (6)

| ID | Item | Evidence that satisfies | PARTIAL when |
|---|---|---|---|
| LYD-1 | The intended use case is explicitly bounded | Scope statement in system prompt; supported-use-case list in README/AGENTS.md; policy or remit document | Scope stated but broad or aspirational |
| LYD-2 | Scope is enforced outside the prompt | Code-level intent/topic gate; per-role tool allow-list; router with a rejection path; refusal tests | Prompt instruction plus a weak or bypassable code check |
| LYD-3 | Model selection matches the domain | Domain-tuned or deliberately smaller model; fine-tune config; documented model choice rationale | General-purpose model with a strong scope prompt |
| LYD-4 | The tool/capability surface is enumerated and minimal | Explicit tool registry; per-tool scoping; no dynamic or `eval`-loaded tools | Registry exists but includes unused broad-capability tools |
| LYD-5 | Scope is bounded by allow-list, not deny-list | Allow-list in code or config | Deny-list present and maintained, no allow-list |
| LYD-6 | Out-of-scope input has a defined failure mode | Explicit refusal path; escalation to human; typed "unsupported" outcome | Behaviour described in prose but not implemented |

### BKB — Balance Your Knowledge Base (6)

| ID | Item | Evidence that satisfies | PARTIAL when |
|---|---|---|---|
| BKB-1 | Knowledge sources are enumerated | RAG/index configuration; documented corpora; declared data sources | Sources discoverable from code but undocumented |
| BKB-2 | Sources are minimised to the use case | Scoped index; per-role or per-tenant filtering; no blanket filesystem or web access | Scoping exists on some paths only |
| BKB-3 | The agent has sufficient grounded knowledge for its domain *(the book's under-provisioning half)* | Domain RAG or fine-tune; "answer only from provided context"; citation requirement | Grounding exists but domain coverage is thin |
| BKB-4 | Hallucination controls exist | Groundedness eval suite; citation enforcement; refuse-on-no-evidence; confidence thresholds | Instructional only ("do not speculate"), unmeasured |
| BKB-5 | Untrusted content in context is identified as data, not instruction | Provenance tagging; instruction/data channel separation; delimiters with canonicalisation. **Covers tool results and execution output, not only user uploads and retrieved documents** — for an agent, tool output is the dominant untrusted channel (an executor returning a mounted file's contents verbatim into the next turn is the same risk as an unvetted RAG document). | Separation by convention only; or applied to retrieval but not to tool output |
| BKB-6 | Sensitive data is kept out of context unless required | PII filtering before context assembly; field-level redaction; scoped credentials | Redaction on some sinks only |

### ZT — Implement Zero Trust (8)

| ID | Item | Evidence that satisfies | PARTIAL when |
|---|---|---|---|
| ZT-1 | Input to the model is screened | Input validation/sanitisation; canonicalisation; encoding normalisation; guardrail framework on input | Length/type checks only |
| ZT-2 | Retrieved and external content is screened before entering context | A distinct screening path for RAG/web/tool output | Same weak filter as user input, or partial coverage |
| ZT-3 | Model output is screened before use | Output filter; PII scan; structured-output validation against a schema | Schema validation without content screening |
| ZT-4 | Model output does not reach a consequential sink unvalidated | Parameterised queries; command allow-list; no `eval`/`exec` of model text | Validation on some sinks only |
| ZT-5 | High-impact actions are gated or structurally prevented | Non-bypassable confirmation; human-in-the-loop; capability denial; dry-run default | Gate exists but is bypassable by flag or config |
| ZT-6 | Controls are enforced in code, not only in the prompt | A code gate exists for each claimed control | Mixed: some code-enforced, some prompt-only |
| ZT-7 | Rate and resource limits exist | Rate limiter; loop/iteration caps; token or spend budget; timeouts | Limits on some paths; defaults unbounded |
| ZT-8 | Agency and credentials are bounded | Max iterations; tool-call caps; scoped per-action credentials; secrets in vault or env, **not in the workspace tree** | Scoping partial, or credentials present but non-production |

### MSC — Manage Your Supply Chain (7)

| ID | Item | Evidence that satisfies | PARTIAL when |
|---|---|---|---|
| MSC-1 | A component inventory exists | ML-BOM / AIBOM / SBOM (CycloneDX, SPDX); generated and drift-checked in CI | Inventory exists but is hand-maintained or stale |
| MSC-2 | Dependencies are pinned and verifiable | Lockfile; pinned versions; hashes | Pinned in some manifests only |
| MSC-3 | Model provenance is documented | Named model + version + provider; model card; weight integrity check for self-hosted | Model named but unversioned |
| MSC-4 | Third-party extensions are inventoried and vetted | Pinned MCP server list; plugin/skill allow-list; documented review step | Inventoried but unvetted |
| MSC-5 | Training/tuning data provenance is documented *(N/A for API-consuming agents)* | Dataset cards; sourcing documentation; poisoning and bias review | Sources named without review |
| MSC-6 | The build and deploy pipeline is secured | Pinned CI actions; least-privilege tokens; signed artifacts or releases; branch protection | Some hardening; unpinned actions |
| MSC-7 | A vulnerability response path exists | `SECURITY.md` with disclosure contact; dependency scanning (Dependabot/Renovate); documented patch cadence | Contact but no scanning, or scanning with no policy |

### RT — Adversarial Security Testing (6)

Renamed from "Build an AI Red Team": grade the practice, not the staffing.
Abbreviation stays **RT**.

**Items 2–6 qualify the testing found in item 1.** Where item 1 is NOT MET
there is nothing to qualify and items 2–6 are NOT MET, not NOT EVIDENCED.
Without this, any project with a CI-run pytest suite collects free points in
the red-team category — which is exactly what happened in the first eval.

| ID | Item | Evidence that satisfies | PARTIAL when |
|---|---|---|---|
| RT-1 | Adversarial testing exists, specific to this agent's threat model | Structured attack corpus; garak / promptfoo / PyRIT / Giskard configuration; jailbreak or injection test suite; checked-in red-team or pentest report; threat model with attached tests. **The test must contain an adversarial input** — a hostile string, a bypass attempt, a spoofed identifier. A test that verifies security *machinery fires when told to* (a stub tripwire returning true) is not adversarial testing, regardless of whether the control is a shipped feature. | Bypass-shaped tests against a control, without any test of the agent itself (Steve, 2026-08-11: *"partly counts"*) |
| RT-2 | An automated, repeatable runner exists | An executable runner; a command-invocable suite; a CI workflow. **CI is sufficient but not necessary** — a deliberate pre-release live exercise qualifies | Manual procedure documented but not executable |
| RT-3 | Testing is ongoing, not point-in-time | Dated report series; scheduled runs; documented per-release cadence; retests after fixes | One run, or cadence stated without history |
| RT-4 | Findings feed back into the system | Findings traceable to issues/PRs/commits; a ledger linking finding → fix; architectural change attributable to a finding | Findings recorded, remediation untraceable |
| RT-5 | Testing gates the release | Stated pass bar; a blocking verdict; a CI gate that can fail the build | Bar stated but advisory |
| RT-6 | Coverage spans the real attack surface | Attacks entering by the agent's actual untrusted channels (telemetry, email, RAG, tool output), tool misuse, and encoding variants — not direct jailbreak prompts alone. **This is where "did the attack come through the real front door" is judged** (Steve, 2026-08-11): a control tested only by calling its function directly loses this item, not RT-1. | Direct-prompt jailbreaks only, or control-level tests that never exercise the running agent |

### MC — Monitor Continuously (6)

| ID | Item | Evidence that satisfies | PARTIAL when |
|---|---|---|---|
| MC-1 | Agent activity is logged | Logging of prompts, responses, tool calls, decisions | Errors/lifecycle only |
| MC-2 | Log content is captured, not only metadata | Prompt and response bodies (redacted as needed); tool arguments | Truncated or tool names without arguments |
| MC-3 | Logs are structured for automated analysis | JSON or structured events; stable schema; correlation/trace IDs | Structured on some paths; free-form elsewhere |
| MC-4 | Logs reach a central system | OTel collector config; fluentbit/vector; Splunk/Datadog/Elastic exporter; cloud logging IAM; **or an observed connection on a deployed target**; deploy scripts wiring any of the above | Local files with rotation only |
| MC-5 | Detection content exists | Alert rules; anomaly detection configuration; dashboards-as-code; UEBA integration | Dashboards without alerting |
| MC-6 | High-impact actions are alerted on and auditable | Alerting on privileged actions; immutable audit trail; retention policy | Audit trail without alerting |

---

## 5. Calibration sources

Every evidence class above is present in a real repository we have scanned.
The RT column in particular was written against
`open-agent-ai-security/socxen`'s `security/redteam/` (schema-validated attack
corpus, `run.py` with deterministic + fresh-judge grading, `METHODOLOGY.md`,
dated `results/`, a 🔴 BLOCK release verdict, and a `HISTORY.md` ledger linking
finding → issue #30 → fix PR #36 → retest).

**Socxen also corrected the draft.** RT-2 was first written as "wired into
CI." Socxen's runner is explicitly *not* CI — it is a pre-release live model
sweep — so the original wording would have scored the stronger practice lower.
RT-2 now reads "an automated, repeatable runner exists," with CI as one
satisfying class. This is the argument for writing items against real repos:
the failure appeared on the first real example.

---

## 6. Validation plan

1. **Replay bench first.** Scoring is a pure function of (evidence + rubric +
   model). Frozen finding sets and pinned source trees already exist, so a
   scoring experiment needs no scan: ~15k tokens per sample instead of ~250k.
   N ≥ 10 replays per condition, with the unchanged rubric as same-day control.
   Without this, the #195 rat hole repeats with different adjectives.
2. **Discrimination check.** Does the checklist separate targets the 0–5 scale
   collapsed — specifically BKB (stuck at {1,2}) and RT (7 of 12 at exactly 1)?
3. **Agreement check.** Does the checklist reproduce holistic scores where the
   holistic score is trustworthy (socxen RT = 4)?
4. **Variance check.** Per-category band distribution over N replays, versus
   control. This is where the independence hypothesis in §3.3 is tested.
5. **Ground truth.** Hand-score the wide targets once, adjudicated by Steve, so
   the rubric is not optimised for self-consistency alone.

## 7. Cost and scope

- **39 evidence questions replace 6 holistic judgments.** More scanner steps,
  each much cheaper and most mechanically checkable. Net scan cost is expected
  to rise modestly; unmeasured, and the bench should measure it.
- **Schema + template change** (`raise_posture` gains per-item results,
  evidence coverage, and N/A justifications), so this rides a re-baseline —
  1.4 at the earliest, alongside the deferred `scan_mode` field.
- **Not backward-comparable.** Checklist-derived scores are a different
  instrument; the v1.2-opus5 bands do not carry over.

## 8. Item scope — repo-wide vs subject-scoped

Raised by the first eval, **unresolved**. Scan instructions scope the subject
(e.g. AutoGen's executors, not the monorepo) while hygiene sweeps run tree-wide.
RT, MSC and MC are project-practice items and read naturally tree-wide;
LYD, BKB and ZT are properties of the scanned subject. Each item must declare
its scope, and multi-tree targets (hermes-agent-desktop spans two) must
enumerate every tree.

## 9. Open questions

1. **Weights.** Left unchanged deliberately. The source's only quantitative
   signal (item counts) would make MSC heaviest. Separate decision.
2. **Per-category item counts** are unequal (6–8), so resolution differs by
   category. Acceptable, or normalise?
3. **Do category scores stay integers** in the report for continuity, or move
   to one decimal? Integers reintroduce exactly the quantization §1(b)
   identifies; decimals break visual comparability with published 1.2 scores.
4. **Should evidence coverage gate anything**, or remain advisory alongside the
   advisory score?
