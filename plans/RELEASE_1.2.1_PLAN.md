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

### C · Optional / needs a call

- **#227 — report tag chips link the unstyled Jekyll `/docs/` render** instead of
  the styled `/guide/` pages. Score-inert, but fixing it regenerates **85
  committed HTML renders** (baselines, examples, the golden fixture) because the
  byte-render gate requires committed renders to reproduce exactly. Every diff
  should be *only* the URL substitution — mechanically verifiable.
  **Do not "fix" this with `.nojekyll`**: that turns `/praxen/docs/` into a 404
  and breaks every report users have already generated and shared at 1.0/1.1/1.2,
  which we cannot reach. Include only if the 85-file diff is acceptable in a
  patch; otherwise 1.3.
- **#216 — `SKILL.md` §9.2's worked example describes FinBot verbatim**, including
  a real finding on a roster/demo target. The fix is prose-only, but it is prose
  the scanning model reads while authoring `agent_structure_summary`, so it is
  the one item here with a non-zero (small) chance of nudging output style.
  If included, pair it with a single spot-check scan before merge.
- **#151 — Google Antigravity (`agy`) harness**: packaging and docs only, engine
  unchanged; an external contact is waiting and the 1.3 plan already notes there
  is no engineering reason to hold it. Additive, but it does open a new support
  surface — a scope call, not a technical risk.
- **#106 — clarify Out-of-Scope remit coverage** as boundary-rule checks.
  Authoring-side guidance; no scan-behavior change against committed remits.

## Explicitly NOT in 1.2.1

Each of these moves a number, changes the schema contract, or is a feature —
all belong to 1.3 (`RELEASE_1.3_PLAN.md`):

| Item | Why not |
|---|---|
| #48 scoring rework | The 1.3 headline; re-baseline by definition |
| #198 / #200 / #201 remit work | Remit changes move scores; needs a re-freeze |
| #195 band anchors · #196 decomposition rule | Scoring/variance surface |
| #173 / #174 tagging calibration | Changes frozen tags |
| #41 · #104 detection additions | New findings |
| #70 roster gap | New target = re-baseline |
| #176 suite_health full 0–5 scale | Explicitly gated on the next re-baseline |
| #113 `<code>` wrapping in prose fields | **Model-output change** — moves every committed render and is a prose-behavior change |
| #27 finding collapse/expand | Report UX feature, not a patch fix |
| #197 Thinking Modes | User-facing feature |
| #117 / #118 operator override + revision records | Schema-contract change |
| #217 manifest-authoring fragility | Architectural; needs design |
| #90 design system · #135 docs simplicity pass | Larger efforts |

## Success criteria

- Suite stays **245 / 0**; `./build.sh` green; mirror check in sync.
- `tests/baselines/` byte-identical **unless C/#227 is included**, in which case
  every changed file's diff is the URL substitution and nothing else.
- No `schema_version` change; `CURRENT` still `v1.2-opus5`.
- A fresh marketplace install of 1.2.1 scans one baseline target and lands
  within band — the same check that validated 1.2.0.

## Sequencing

A and B are independent and can land in one PR each. Decide C before starting:
if #227 is in, land it **last and alone**, so the 85-file regeneration is
reviewable on its own rather than mixed with prose edits.

Version bump is `1.2.0 → 1.2.1` by hand across `PRAXEN_SPEC.md`,
`.claude-plugin/plugin.json`, the praxen entry in
`.claude-plugin/marketplace.json`, and `.codex-plugin/plugin.json` — praxen has
no bump script; `build.sh`'s four-way guard is what enforces agreement (it now
looks the marketplace entry up **by name**, so the mirror's extra entries are
safe). Then the CHANGELOG entry, the usual `dev` → `main` merge-commit
promotion, fast-forward `dev`, and tag.

**Remember what "released" means now:** the community catalog pins praxen's
`main`, so **merging the promotion is what ships to users** — the tag only cuts
the zip and the GitHub release. Sequence any announcement accordingly.
