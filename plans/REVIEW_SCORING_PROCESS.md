# Code review — revised #195 scoring process (2026-08-11)

Requested by Steve after the #195 gates passed: a full Fable review of the
revised scoring process, review-only ("we don't necessarily modify things
based on the review"). Scope: `git diff 3b6884f^..HEAD -- skills/` — the
SKILL.md Step 5 / 8b / 9.4 restructure, the KB boundary rules + provenance
test, and three comment-only pointer fixes.

Method: five independent Fable reviewers with source access, one lens each —
process consistency, rule-system soundness, operational executability,
cross-file drift, regression risk. Every high/medium finding below was then
re-verified against the files by the orchestrator; two reviewer claims were
refuted in verification and are listed at the end.

## Verdict in one paragraph

The validated core held: nothing serialized changes, all 245 + 42 tests pass,
the 15 byte-gated artifacts re-render byte-identical, and the three code edits
are genuinely comment-only. The confirmed defects cluster in exactly two
places the #195 gates never exercised: (1) **persistence and handoff** of the
new evidence artifacts — the 8b record and Step 5 notes exist only in working
memory, which collides with the compaction-resume design the rest of SKILL.md
is built around; and (2) **the rule system's edges** — category coverage,
rule-ordering semantics, and the x-high thinking mode, whose adjudicator is
now instructed to do something the new Step 9.4 defines as impossible. None
of these were hit by Gate 1/2 or the sweep because all validation ran
standard-mode, single-context, on targets where the dominant-path calls were
clean.

## Confirmed HIGH

**H1. The Step 8b maturity record has no durable home, and 9.4 forbids the
only recovery path.** (Found independently by 4 of 5 reviewers.)
SKILL.md:620–622 declares the record "not serialized"; unlike Step 8.5
(SKILL.md:630, which appends THEMES to the Step 4 evidence checkpoint), 8b is
never directed to any file. But 9.4 (SKILL.md:714–719) makes the record item 3
of its fixed evidence set and forbids re-reading the workspace. A compaction
between 8b and 9.4 — the exact contingency the checkpoint design exists for —
forces a resumed run to either violate the no-re-read rule (reintroducing the
variance this revision kills) or score Red Team / Monitor from findings alone
(the maturity blindness SKILL.md:725 itself warns about). One-line fix exists:
append the M1–M12 block to the evidence checkpoint like 8.5 does.

**H2. The x-high adjudicator cannot execute the new Step 9.4.**
THINKING_MODES.md:313 has the adjudicator assemble the super-run "per SKILL.md
Steps 8.5–12" — a range that skips Step 8b — while 9.4 requires the 8b record
and Step 5 notes, which died with the raw runs' contexts (unserialized per
SKILL.md:620). Principle 2 (THINKING_MODES.md:38–41: scores "re-derived from
the adjudicated **finding set**") now contradicts SKILL.md:725 ("a category is
not scored on defects alone"). The adjudicator has workspace access, so the
fix is small (assembly range includes 8b; principle 2 names the full 9.4
evidence set), but as written x-high either scores maturity-blind or
improvises a forbidden workspace re-read. Related: the brief's read range
"Steps 5–12" (L277) vs assembly range "8.5–12" (L313) disagree on whether 8b
is in scope.

**H3. "Apply these in order, and the first that applies decides" is
incoherent for boundary rules 1–2.** (KB:94–95.) Rules 1 and 2 are evidence
filters — they discount an artifact, they don't pick a band — so when one
"applies", nothing is decided, and the text doesn't say whether processing
continues or what a discounted control means for rule 3's "unmanaged" test.
Worked failure: dominant path guarded only by an opt-in default-off code
sanitizer, lesser paths fully managed. Rule 1 fires and discounts the
sanitizer. Is the path now "unmanaged" (no *counting* control addresses it →
rule 3 → cap 1) or "managed but uncreditable" (not a prompt, so the carve-out
gives no routing → no cap → 3 from lesser paths)? Two defensible outcomes two
bands apart, produced by the section built to eliminate one-band spreads.

**H4. Rule 3's carve-out routes prompt-covered paths to a prompt-only cap
that exists for only two of six categories.** (KB:107–110.) Every stated
prompt-only cap is scoped to Zero Trust (KB:237, 412, 467) or Domain (KB:377).
For Balance, Supply Chain, Red Team, and Monitor, the carve-out disclaims
rule 3's jurisdiction and hands the call to a rule that does not exist. Worked
failure: an agent whose dominant untrusted channel is tool output (KB:383's
own words), covered only by a system-prompt instruction — Zero Trust caps it
at 2, Balance can be argued to 3 on identical posture.

## Confirmed MEDIUM

**M1. Step 5 still opens with the old imperative.** SKILL.md:358: "Score each
category 0–5 with a confidence level…" — retracted only at :386 ("Do not
commit scores here"). A top-down reader scores six categories in Step 5 and
9.4 degrades to transcription — the pre-revision behavior. (2 reviewers
independently.)

**M2. 9.4's evidence item 1 names an artifact that doesn't exist yet.**
"The committed `findings[]` and their severities" — `findings[]` is composed
at 9.9/10. What exists at 9.4 time is the Step 8.5 THEMES outline (which does
carry intended severities, categories, and evidence sites on disk — so this
was downgraded from a reviewer's HIGH). The item should name the THEMES
outline; severity shifts during 9.9 drafting are otherwise never seen by the
scores.

**M3. Step 8b's determinism has open seams.** (a) M2's trailing clause "and
any schema-validated attack fixture set" (SKILL.md:585) is an unscoped sweep
inside the enumerated lookup — the same mechanism that produced the 16/9/7
variance. (b) No M-question specifies its search root; on a scoped monorepo,
tree-wide vs subject-only reads give different answers, and Step 8b never
references SCAN_INSTRUCTIONS scoping (whose hygiene carve-out at :225 covers
only secrets/pinning). (c) M8's "stated pass bar" is a semantic property
dressed as a grep, and its mandated "none — searched <patterns>" answer has no
patterns to cite. (d) M6's second disjunct ("a test suite invocable by a
single documented command") is satisfied by `pytest` + README on nearly every
target, flipping the question's meaning. (e) M12's `vector` token is unbounded
on LLM-agent codebases, and "an observed telemetry connection" has no
observation procedure.

**M4. Ceiling-of-1 scope is ambiguous between the two files.** KB:144 "the
first case caps an otherwise-higher score at 1" reads category-level;
SKILL.md:364 reads artifact-level with a bar for 2+ ("evidence the team's own
adversarial testing changed the design"). Worked absurdity under the KB
reading: a target with an own demo suite (no fix) AND an independent exercise
that drove an architectural change scores 1 — and deleting the demo suite
would raise its score. Same class as the floor/ceiling conflict already fixed
once this session. Related hybrid gap: a CTF project whose shipped challenge
surfaced a bug the team then fixed matches both provenance rows (KB:127–129
vs KB:142) with no priority rule — scorers can land 0 or 2.

**M5. PRAXEN_SPEC.md is stale on scoring.** L138: "final scores are
re-derived from the audited finding set by the normal scoring rules" — the
finding set is now an insufficient scoring input by design; no mention of 8b
or the 9.4 relocation anywhere in the spec. The spec ships in the zip and
release tooling reads it. docs/thinking-modes.md:111–114 (and the generated
guide page) repeat the same finding-set-only model user-facing.

**M6. Rule 3's dominant-path selector is dual-keyed with no tiebreak.**
KB:104–105 "largest-volume **or** highest-risk" — co-dominant paths or a
volume/risk split make the cap's trigger arbitrary (cap 1 vs score 3 depending
on which path the scorer names dominant). Also rule 3 is written in data-path
terms that are undefined for Red Team and Supply Chain, though SKILL.md:723
invokes the boundary rules for all six categories.

**M7. Variance can relocate into what Step 5 happened to write down.**
9.4's evidence item 4 is the Step 5 notes — no required format, persistence
optional (:296 "if you wish"), living in working memory. Two runs with
identical 8b records can still diverge on a band call because one run's notes
captured a default-on detail the other's didn't. Additionally: 9.4's no-re-read
rule is honor-system (nothing audits it), there is no stated recourse when the
committed evidence can't decide a call (the KB choose-lower rule is the de
facto fallback but is never connected to "evidence insufficient"), and nothing
requires 9.4 rationales to cite M-lines — which would make 8b consultation
observable and anchoring detectable.

**M8. 8b's instructions mix "record what returned" with "open before
recording".** SKILL.md:580 vs the guardrail at :612–615 — one run records raw
paths, another records interpreted artifacts; and :606 ("do not judge it
here") sits next to the CI guardrail (:616–618) which weighs evidence
strength — judgment guidance inside the step that forbids judging. Answer
granularity is also uncapped (M7-the-question requires per-workflow records; a
20-workflow repo cannot answer in one line).

## Confirmed LOW

- SKILL.md:966 — Step 10 still says "a finding raised by RAISE-category
  scoring (Step 5)". Stale pointer to the old model.
- SKILL.md:710 — 9.4's heading is still "RAISE per-category rationale ×6";
  heading-navigation misses that it's now the scoring step.
- schema.py:489 ("KB Scoring Model B3") and tests/render/test_render.py:722
  ("KB Step B3") — two dangling references the comment sweep missed.
- KB:133 / SKILL.md:365 "score it as absent" — the one phrase that points at
  the N/A machinery for a category schema forbids from using it;
  mitigated (both files immediately say the category is 0, and the failure
  mode is a loud Step-11 validation abort, not a silent shift).
- M4's literal paths miss `.github/SECURITY.md`, GitHub's recommended
  location. M9 leaves git-history/GitHub-releases in or out unresolved.
- Rule 4 (KB:111–112) restates KB:58's choose-lower with a different trigger
  and obligation; and because the rule-3 carve-out only removes rule 3 without
  asserting the band, rule 4 can still pull a prompt-covered call to 1 when a
  scorer finds 1 "defensible" — outcome-indistinguishable from the
  pre-99f080e behavior it was fixed to prevent.
- 8b cost on a large target: realistic 50–100+ tool calls / 30–80k tokens,
  dominated by M7's read-every-workflow, guardrail-1's uncapped obligation to
  open every hit, and M12's `vector` grep. No cap stated ("open at most N hits
  per question" would bound it).

## Directional-bias probe (no defect filed)

Three of four boundary rules only lower scores and rule 4 ties down, but
deflation is guarded elsewhere in the evidence 9.4 must re-read: SKILL.md
calibration anchors read both directions (:368–372), :723's "don't drop a
category to 0 when the control underneath is real and running", KB anti-pattern
2, and the 22/24 adjudication found the winning side "never deflated a real
control". A one-line cross-reference from the KB boundary section to the SKILL
anchors would close the standalone-KB-reader risk.

## Refuted / corrected in verification

- One reviewer claimed the prompt-only cap-at-2 rule "is not defined anywhere
  in the KB or SKILL.md" — refuted by grep (KB:237, 377, 412, 467). The
  surviving, sharper version is H4: the caps exist but cover only two
  categories.
- One reviewer asserted "no Step B3 ghost reference remains anywhere in
  skills/ or docs/" — refuted (schema.py:489); another reviewer had already
  found it.
- The "9.4 scores from findings that don't exist" HIGH was downgraded to M2:
  the committed 8.5 THEMES outline does exist on disk with severities; the
  defect is the evidence item's name, not a missing input.

## Strengths (consolidated, all verified)

- The scoring relocation is advertised consistently at every summary surface —
  pipeline TL;DR, jump table, Step 5 closing, 9.4 opening.
- Mandatory all-twelve M-answers with "none — searched <patterns>" makes
  verified absence first-class and auditable; M3 and M11 are the fully
  deterministic model the other ten should converge toward.
- The KB↔SKILL provenance/ceiling table is mirrored with matching numbers,
  and the amended rule 3 creates a coherent three-tier ladder (nothing → ≤1,
  prompt-only → ≤2, operative code → uncapped) that composes with
  cross-category inference instead of fighting it.
- 8b's serialization wall (:620–622) pre-empts the schema-regression class
  entirely; all three comment fixes point at things that exist, with real
  commit provenance.
- Rule 1 (opt-in never counts) and SKILL.md:370 (inherited default-on
  framework controls do count) partition the defaults question in opposite
  directions — a two-sided guard, not a ratchet.

## Reviewer-effort note

Five reviewers, ~345k subagent tokens total. Convergence was the strongest
signal: H1 was found independently by four of five lenses; M1 and the
THINKING_MODES gap by two each. Findings above were individually re-verified;
line numbers are current as of commit 99f080e.

## Disposition (2026-08-11) — all confirmed findings fixed

Steve's call: "these are generally must-fix items." Every confirmed finding
above was fixed in the same session:

- **H1** — Step 8b now appends its `MATURITY (M1-M12)` block to the Step 4
  evidence checkpoint (as 8.5 does with `THEMES`), and Step 5 appends a
  mandatory `RAISE NOTES` section (also fixes M7's memory-only notes). 9.4
  names the checkpoint sections it reads; all scoring inputs now survive a
  compaction.
- **H2** — THINKING_MODES principle 2 and the x-high assembly brief now name
  9.4's full evidence set; the adjudicator runs Step 8b itself (mismatches vs
  the raw runs' persisted records are adjudication evidence); the high-mode
  re-derivation reads the scan's checkpoint sections; PRAXEN_SPEC.md and
  docs/thinking-modes.md (guide rebuilt) carry the same correction.
- **H3** — the boundary-rules preamble now distinguishes evidence filters
  (rules 1–2) from band deciders (rules 3–4), and rules 1–2 state their
  consequence for rule 3 explicitly: a path whose only controls were
  discounted is unmanaged in the shipped default.
- **H4** — rule 3 rewritten as the three-rung dominant-path ladder (nothing →
  cap 1; prompt-only → cap 2 in every applicable category; operative code →
  no cap), with the ZT/Domain prompt-only caps as named instances. Scoped to
  the four path-identifiable categories (also fixes M6's applicability gap);
  dominant path = highest-risk, volume breaks ties, co-dominant paths set the
  ladder by the worse-covered door (M6's selector fix).
- **M1–M8 and all lows** — Step 5 opener no longer says "score"; 9.4's
  evidence item names the 8.5 THEMES outline and adds the severity-shift and
  insufficient-evidence recourses; Red Team / Monitor rationales must cite
  M-lines; the M-table gained a fixed search-scope block, an enumerated
  replacement for M2's open clause, M8 grep tokens, M6's security-testing
  antecedent, M12 bounds, `.github/SECURITY.md`, M9 working-tree scoping, the
  five-hit open cap and tally format; the ceiling-of-1 is now explicitly
  artifact-level with the hybrid case resolved (both files); "score it as
  absent" became "treat it as absent (never `N/A`)"; rule 4 defines "both
  defensible"; the KB boundary section cross-references the SKILL anchors;
  the remaining B3 ghost comments (schema.py:489, its spliced fragment,
  test_render.py:722) are gone; Step 10's stale "(Step 5)" label and the 9.4
  heading are corrected.

**Verification after the fixes:** 245 + 42 tests green, byte-gated artifacts
unchanged, `claude plugin validate` clean, docs rebuilt. Replay sanity on the
rewritten rules, three blind scorers per condition, 12/12 unanimous with the
intended rule cited every time: salesforce full-facts 2,2,2 (adjudicated
answer preserved via the ladder's prompt-only rung); openhands 1,1,1 (via the
codified rule-1 discount); autogen 2,2,2 (fix-neutral, matches every prior
replay on that sheet); and the H3 worked example — opt-in code sanitizer on
the dominant path, lesser paths well-managed — which the old text left
ambiguous between 1 and 3, now 1,1,1 with identical traces.
