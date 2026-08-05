<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxen 1.2.1 — Fast-follow patch (docs, CI, packaging)

> ## ▶ STATUS: ACTIVE — approved 2026-08-05 (Steve: "make a 1.2.1 branch and start the work"); working branch `1.2.1` off `dev`
>
> Drafted immediately after the `v1.2.0` release from the promotion and
> post-release reviews. **Everything here is deliberately score-inert**: no
> item changes detection, scoring, remits, or any frozen findings JSON, so
> **1.2.1 ships against the existing `v1.2-opus5` baseline with no re-scan and
> no re-freeze.** That is the entry criterion — an item that moves a number
> belongs in 1.3, not here.

## Why a patch release at all

1.2.0 shipped clean, and the post-release scan check was green. But the reviews
that ran *during* the promotion surfaced a cluster of small factual and
plumbing defects that are cheap to fix and awkward to leave standing — chiefly
**normative documents stating the wrong contract** and **CI trust checks that
are looser than intended**. None warranted holding the release; together they
warrant a patch rather than waiting for 1.3.

The four highest-value corrections (schema version in `STABILITY.md` and the
reports reference, the pre-`1.0` support policy, the dead OWASP link) **already
shipped to `main` on 2026-08-03** and are live. What remains is the tail.

## Entry criteria (the test every item must pass)

1. **No findings JSON is touched.** No re-scan, no re-freeze, no band change.
2. **No change to scoring, detection, or remit content.**
3. **No schema change** — `schema_version` stays `3.0`.
4. Bounded and reviewable in a single sitting; a mechanical diff wherever
   possible.

Item 5 below is the one that regenerates committed HTML. It still passes the
test — no JSON, no scores — but it is called out separately because the diff is
large, and it is optional for this release.

## Scope

### A · Documentation corrections *(the remainder of #225 / #226)*

- **`tests/README.md` self-contradiction** — line 17 says baselines are
  "schema-2.0" two lines after line 15 correctly describes the v1.2 set as
  schema 3.0. Also `tests/README.md:244`, which points the release-review step
  at the **archival** `v1.1-claude48` set rather than `v1.2-opus5`.
- **Install confirm lines still say `v1.0.0+`**, and there is no "upgrading from
  1.1" guidance anywhere — the audience most likely to read the docs right now.
- **Scan-to-scan diff is shipped but undocumented** outside the CHANGELOG
  (`tests/scan_diff.py`). It is a headline-adjacent 1.2 feature that a user
  cannot discover.
- **Broken `render_remit.py` invocation** in the docs (per #225).
- **#224 — `SKILL.md` Step 9.9**: the `--validate-manifest` example is
  unrunnable (`--manifest <path>` is required and `--validate-manifest` is a
  flag), and the skeleton-tolerance wording overstates the case — the validator
  tolerates *absent* sections but correctly rejects a present-but-empty
  `remit_coverage.rules`.

### B · CI and supply-chain hygiene *(no product surface)*

- **#222 — DCO bot exemption** keys on the email-derived `c.author.type === 'Bot'`
  rather than an explicit login allowlist. Tighten to the bots that actually
  open PRs here (Dependabot).
- **#209 item 2 — dependabot auto-merge** merges immediately when the base
  branch has no required checks. Gate it.
- **#209 item 3 — SHA-pin GitHub Actions** rather than floating major tags.
  Dependabot (now correctly targeting `dev`) keeps them current.
- **#193 — `actions/setup-python` 6 → 7 — fold into the SHA-pinning above, do
  not merge it standalone.** Parked through the 1.2.0 launch on purpose; the
  launch is done, so it can proceed. Two reasons to merge it *as part of* item 3
  rather than on its own:
  1. **It is incomplete.** #193 touches `ci.yml` and `release.yml` only —
     `marketplace-sync.yml` was added *after* dependabot opened it, so merging as-is
     leaves setup-python at v7 in three places and **v6 in one**. Pin all four
     together (`ci.yml` ×2, `release.yml`, `marketplace-sync.yml`).
  2. **Pinning supersedes bumping.** SHA-pinning means choosing the SHA of the
     version you want; doing the bump first and the pin second edits the same
     four files twice.

  ⚠️ **Known risk, now acceptable:** `release.yml` is tag-triggered, so no PR run
  ever exercises it — **1.2.1's own tag push will be the first execution of
  setup-python v7 in the release workflow.** That is precisely why this was held
  out of 1.2.0: a failure there would have broken the flagship release build. On
  a patch it is a recoverable place to find out. Watch the release run rather than
  assuming it, and note that re-running a failed run replays the *old* workflow
  definition — a fix needs a new tag, and this project does not re-point published
  tags.
- **`scripts/release/bump_version.py`** *(new — Steve, 2026-08-03)*. Praxen keeps the
  version in **six** places and edits every one of them by hand *(the draft
  said five — `marketplace.json` `metadata.version` surfaced when porting the
  script against `test_plugin_manifests.py`'s actual check list)*:

  | Surface | Guarded by |
  |---|---|
  | `PRAXEN_SPEC.md` (`**Version:**`) | `build.sh` (the authority the tag is checked against) |
  | `.claude-plugin/plugin.json` | `build.sh` + `test_plugin_manifests.py` |
  | `.claude-plugin/marketplace.json` (praxen entry, **by name**) | as above |
  | `.claude-plugin/marketplace.json` (`metadata.version`) | `test_plugin_manifests.py` only — **not** `build.sh` |
  | `.codex-plugin/plugin.json` | as above (`build.sh` + tests) |
  | `README.md` release badge | `test_plugin_manifests.py` only — **not** `build.sh` |

  The guards catch drift, but only *after* someone has already shipped a
  half-edited bump into a PR — and the release cadence means a bump is usually
  cut under time pressure. A script makes the bump one command and the guards a
  backstop rather than the discovery mechanism.

  **socxen already has one** (`scripts/bump_version.py`) and it is good prior
  art — same shape: edit, regenerate derived artifacts, verify all surfaces
  agree, print the diff, do **not** commit. Port it rather than reinvent, with
  two lessons from socxen's own history: (a) it must look the marketplace entry
  up **by name**, never positionally — praxen's mirror carries a socxen entry
  too, and the positional read was a live latent bug fixed in #214; (b) when a
  surface is removed, the *verify* block must be updated with the edit block —
  socxen's crashed after writing its edits because a stale reference survived in
  verification only.

  Scope note: praxen has no AI-BOM to regenerate (socxen's script does that);
  praxen's derived step is `guide/` via `docs_build.py` only if a bumped version
  appears in `docs/`, which today it does not.

### C · Report and authoring clean-ups *(approved for scope — Steve, 2026-08-03)*

- **#227 — report tag chips link the unstyled Jekyll `/docs/` render** instead of
  the styled `/guide/` pages. Score-inert, but fixing it regenerates **85
  committed HTML renders** (baselines, examples, the golden fixture) because the
  byte-render gate requires committed renders to reproduce exactly. Every diff
  must be *only* the URL substitution — mechanically verifiable, and worth
  verifying rather than trusting.
  **Do not "fix" this with `.nojekyll`**: that turns `/praxen/docs/` into a 404
  and breaks every report users have already generated and shared at 1.0/1.1/1.2,
  which we cannot reach. Keep Jekyll serving `/docs/` as a fallback.
- **#216 — `SKILL.md` §9.2's worked example describes FinBot verbatim**, including
  a real finding on a roster/demo target. Prose-only, but it is prose *the
  scanning model reads* while authoring `agent_structure_summary` — the one item
  in this release with a non-zero (small) chance of nudging output style.
  **Gate it with a spot-check scan** of one baseline target before merge; if the
  result lands outside band, drop the item rather than debug it in a patch.
- **#106 — clarify Out-of-Scope remit coverage** as boundary-rule checks.
  Authoring-side guidance; no scan-behavior change against committed remits.
- ~~**#27 — finding default-state (collapsed/expanded) + expand/collapse-all.**~~
  **DEFERRED INDEFINITELY** (Steve, 2026-08-05: *"Defer [#27] indefinitely, but
  leave it filed - don't close"*). Dropped from this release and from any
  scheduled release; the issue stays open as the record. Implementation note
  for whenever it revives: finding cards are already `<details open>` in the
  template, so the change is the default attribute plus expand/collapse-all
  controls — plus the render regeneration of the day.
- **#6 — `render.py` / template polish** (finding-card confidence, Medium/Low
  badge, TXT High findings). The issue itself flags that it re-renders the
  byte-frozen baselines — which is precisely why it belongs *with* #227/#27
  rather than after them. Same argument: **the regeneration is a fixed cost, so
  pay it once.** Score-inert; presentation only.
- **#135 — docs simplicity pass (Tier 3).** Prose only, no generated-output or
  scan surface. Scope it to a bounded pass rather than an open-ended rewrite.
- **#4 — `SKILL.md` authoring aids & clarity leftovers.** Small prose items from
  an old field review, explicitly "not bugs". Same risk class as #216 — prose the
  model reads — so **fold it under #216's spot-check gate** and let one scan
  cover both rather than running two.
- **#65 items 6–7 — remit-authoring guidance**: the code-first warning block and
  the mechanism-vs-property note in the remit template. Author-side only; the
  committed remits 1.2.1 scores against are unchanged, so this is inert for the
  frozen set.
- **#176 item 3 leftover** *(ride-along only)*: `rows_table` in
  `tests/baselines/suite_health.py` reaches for the `DEFAULT_BASELINE` module
  global at lines 121 and 131 rather than the resolved `baseline_dir`, so
  `--baseline-dir` isn't honored for the report-link and remit columns. Roughly
  two lines. Take it **only** if someone is already in that file — it does not
  justify its own PR, and the rest of #176 stays gated on the re-baseline.

  ⚠️ **#65 item 8 is NOT in scope, contra the 1.3 plan's note.** That item puts
  absence-of-evidence confidence calibration into `KB_RAISE_SCANNING.md` — which
  `SKILL.md:202` loads as the *primary scoring calibration* at Step 3 and uses at
  Step 8 to score. `RELEASE_1.3_PLAN.md` groups items 6–8 as "safe outside the
  freeze"; that holds for 6–7 and over-reaches for 8. Editing a scanner-read KB
  can move scores and belongs with the 1.3 re-freeze.

## Explicitly NOT in 1.2.1

Each of these moves a number, changes the schema contract, or is a feature —
all belong to 1.3 (`RELEASE_1.3_PLAN.md`):

Swept the full open-issue list (34 as of 2026-08-03); everything not in scope
above is here with its reason.

| Item | Why not |
|---|---|
| #48 scoring rework | The 1.3 headline; re-baseline by definition |
| #198 / #200 / #201 remit work | Remit changes move scores; needs a re-freeze |
| #195 band anchors · #196 decomposition rule | Scoring/variance surface |
| #173 / #174 tagging calibration | Changes frozen tags |
| #41 detection pattern · #65 items 4–5 (IaC discovery) | New discovery surfaces = new findings |
| #104 entropy secret detection | Changes what reports redact — alters output content, and it is a detection change |
| #65 item 8 (KB confidence calibration) | `KB_RAISE_SCANNING.md` is scanner-read primary calibration — **can move scores** (see C) |
| #70 roster gap | New target = re-baseline |
| #113 `<code>` wrapping in prose fields | **Model-output change** — prose behavior, not presentation |
| #197 Thinking Modes | User-facing feature, not a cleanup |
| #117 / #118 operator override + revision records | Schema-contract change |
| #217 manifest-authoring fragility | Architectural; needs design |
| #25 SKILL.md rendering/MVC split | Restructures the file the model reads — too structural for a patch, even as a pure refactor |
| #176 suite_health axis/labels | **Re-examined 2026-08-03 — the gate is correct, not inherited.** Items 1–2 are decisions about how to display a score distribution, and can't be made until that distribution changes (the 1.3 re-freeze). Both are latent today: roster max is hermes **2.55**, 0.45 clear of the 3.0 cap, so nothing clips or mislabels. Item 3's main half already shipped in 1.2 (`DEFAULT_BASELINE` now reads `CURRENT`). Issue retitled — the old title said "full 0–5 scale", which its own body argues *against* |
| #151 Antigravity harness | **Held (Steve, 2026-08-03)** — additive packaging, but it opens a new supported harness. New surface, not a cleanup |
| #90 org design system · #2 standing config | Larger efforts; #2 explicitly deferred long-standing |

## Success criteria

- Suite stays **245 / 0**; `./build.sh` green; mirror check in sync.
- `tests/baselines/` byte-identical **unless C/#227 is included**, in which case
  every changed file's diff is the URL substitution and nothing else.
- No `schema_version` change; `CURRENT` still `v1.2-opus5`.
- A fresh marketplace install of 1.2.1 scans one baseline target and lands
  within band — the same check that validated 1.2.0.

## Sequencing

> **Amended 2026-08-05 (execution):** per Steve, all chunks accumulate on the
> **rolling branch `1.2.1` (PR #233), held unmerged** until release-ready —
> same chunks, same order, same per-chunk background review, one merge at the
> end instead of four. Chunk 5 added: the section-C stragglers the original
> four-PR list never assigned a slot (caught during execution). Chunks 1–4
> landed 2026-08-05; release holds for 1.2.0 soak time (Steve, 2026-08-05).

Five chunks, in this order:

1. **A (docs)** and **B (CI + bump script)** — independent, one chunk each. Land
   the bump script first and use it to cut this release's own version bump.
2. **The SKILL prose pair — #216 + #4 — together**, gated by a single spot-check
   scan of one baseline target. One scan covers both; if it lands outside band,
   drop the pair rather than debugging prose in a patch. *(Executed: gate PASSED
   — blind finbot at the frozen median 0.90.)*
3. **The render regeneration — #227 + #6 (#27 deferred out) — last of the
   render-touching work, and alone.** Both touch `render.py` /
   `report_template.html` and force the same regeneration, so they cost one
   regeneration together. Landing them alone keeps that large diff reviewable
   instead of buried under prose edits.
4. **The section-C stragglers — #106, #65 items 6–7, #135, #176 item 3** —
   authoring-guidance and docs prose plus the two-line `suite_health.py` fix;
   none touch the renderer, so they land after the regeneration without
   re-paying it.

**Verify the regeneration rather than trusting it:** for #227 every changed file's
diff must be *only* the URL substitution. #6 legitimately changes more, so
review its diffs on their merits — and confirm no findings JSON moved, which is
the actual invariant.

Version bump is `1.2.0 → 1.2.1` across the six surfaces listed in **B**.
`build.sh`'s four-way guard enforces agreement on all but the README badge (it
now looks the marketplace entry up **by name**, so the mirror's extra entries
are safe); `test_plugin_manifests.py` covers the badge.

**Land `scripts/release/bump_version.py` early in the release, then use it to cut this
release's own bump** — that is both the fastest way to validate it and the most
honest test. Then the CHANGELOG entry, the usual `dev` → `main` merge-commit
promotion, fast-forward `dev`, and tag.

**Remember what "released" means now:** the community catalog pins praxen's
`main`, so **merging the promotion is what ships to users** — the tag only cuts
the zip and the GitHub release. Sequence any announcement accordingly.
