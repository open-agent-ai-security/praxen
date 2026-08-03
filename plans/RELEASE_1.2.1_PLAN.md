<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxen 1.2.1 — Fast-follow patch (docs, CI, packaging)

> ## ▶ STATUS: DRAFT — proposed 2026-08-03, not yet approved
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
- **`scripts/bump_version.py`** *(new — Steve, 2026-08-03)*. Praxen keeps the
  version in **five** places and edits every one of them by hand:

  | Surface | Guarded by |
  |---|---|
  | `PRAXEN_SPEC.md` (`**Version:**`) | `build.sh` (the authority the tag is checked against) |
  | `.claude-plugin/plugin.json` | `build.sh` + `test_plugin_manifests.py` |
  | `.claude-plugin/marketplace.json` (praxen entry, **by name**) | as above |
  | `.codex-plugin/plugin.json` | as above |
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
- **#27 — finding default-state (collapsed/expanded) + expand/collapse-all.**
  A report-UX change, so ordinarily 1.3 — but it lands in `render.py` /
  `report_template.html` and therefore regenerates exactly the same 85 renders
  #227 already forces. **If #227 is in, doing #27 in the same pass is nearly
  free**; doing them in separate releases means paying the regeneration twice.
  Score-inert either way. Include only if the UX decision (which state is
  default) is settled — otherwise it is a design question wearing a cleanup's
  clothes.
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
| #176 suite_health full 0–5 scale | Gated on the next re-baseline by its own title. *Worth re-examining* — it looks like presentation over frozen data, so the gate may be conservative; decide deliberately rather than by inheritance |
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

Four PRs, in this order:

1. **A (docs)** and **B (CI + bump script)** — independent, one PR each. Land the
   bump script first and use it to cut this release's own version bump.
2. **The SKILL prose pair — #216 + #4 — together**, gated by a single spot-check
   scan of one baseline target. One scan covers both; if it lands outside band,
   drop the pair rather than debugging prose in a patch.
3. **The render regeneration — #227 + #27 + #6 — last, and alone.** All three
   touch `render.py` / `report_template.html` and force the same 85-file
   regeneration, so they cost one regeneration together and three separately.
   Landing them alone keeps that large diff reviewable instead of buried under
   prose edits.

**Verify the regeneration rather than trusting it:** for #227 every changed file's
diff must be *only* the URL substitution. #27 and #6 legitimately change more, so
review those diffs on their merits — and confirm no findings JSON moved, which is
the actual invariant.

Version bump is `1.2.0 → 1.2.1` across the five surfaces listed in **B**.
`build.sh`'s four-way guard enforces agreement on all but the README badge (it
now looks the marketplace entry up **by name**, so the mirror's extra entries
are safe); `test_plugin_manifests.py` covers the badge.

**Land `scripts/bump_version.py` early in the release, then use it to cut this
release's own bump** — that is both the fastest way to validate it and the most
honest test. Then the CHANGELOG entry, the usual `dev` → `main` merge-commit
promotion, fast-forward `dev`, and tag.

**Remember what "released" means now:** the community catalog pins praxen's
`main`, so **merging the promotion is what ships to users** — the tag only cuts
the zip and the GitHub release. Sequence any announcement accordingly.
