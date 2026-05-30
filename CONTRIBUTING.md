<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Contributing to Praxen

Thanks for your interest in improving Praxen. Contributions are welcome via pull
request.

## License

Praxen is licensed under the [Apache License, Version 2.0](LICENSE). By
contributing, you agree that your contributions will be licensed under the same
terms.

## Developer Certificate of Origin (DCO)

We use the [Developer Certificate of Origin](https://developercertificate.org/)
instead of a Contributor License Agreement. It's a lightweight way for you to
certify that you wrote the contribution, or otherwise have the right to submit it
under the project's license.

To certify, add a `Signed-off-by` line to every commit:

```
Signed-off-by: Your Name <your.email@example.com>
```

Git adds it for you with the `-s` flag:

```
git commit -s -m "Your commit message"
```

The name and email must match a real identity (no anonymous or pseudonymous
contributions). A CI check (`.github/workflows/dco.yml`) verifies every non-merge
commit in a pull request carries a `Signed-off-by` line matching the author or
committer; PRs that don't pass will be asked to amend before merge.

The full text of the DCO:

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.

Everyone is permitted to copy and distribute verbatim copies of this license
document, but changing it is not allowed.


Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I have the right
    to submit it under the open source license indicated in the file; or

(b) The contribution is based upon previous work that, to the best of my
    knowledge, is covered under an appropriate open source license and I have
    the right under that license to submit that work with modifications, whether
    created in whole or in part by me, under the same open source license
    (unless I am permitted to submit under a different license), as indicated in
    the file; or

(c) The contribution was provided directly to me by some other person who
    certified (a), (b) or (c) and I have not modified it.

(d) I understand and agree that this project and the contribution are public and
    that a record of the contribution (including all personal information I
    submit with it, including my sign-off) is maintained indefinitely and may be
    redistributed consistent with this project or the open source license(s)
    involved.
```

## Branching

Branch from and target **`dev`**, not `main`. `main` is the release branch that
downstream teams install via the Claude Code plugin marketplace — a fresh
`/plugin marketplace add` pulls `main` at HEAD — so it only receives release PRs
at version-bump time. Everyday work lands on `dev` first and reaches `main` as
part of a deliberate, re-verified release.

When you open a PR, GitHub pre-selects the base branch as the repository default
(`main`); switch it to `dev` unless you are specifically cutting a release.

### Keeping `dev` in sync with `main`

`main` and `dev` **diverge by construction**: a release is squash-merged from a
`release/x.y` branch into `main`, which creates a new commit `dev` doesn't share.
If release-only content — the version bump, the `CHANGELOG` entry, the frozen
baseline, the spec edits — is authored on the release branch and never returns,
`dev` silently falls *behind* `main`, and every release widens the gap. (This is
how `dev` ended up two releases behind through 0.7.7.)

The standing rule (maintainers — `dev` is unprotected):

- **Realign `dev` to `main` immediately after every release (and any hotfix).** As
  soon as the release squash lands on `main` and the `vX.Y.Z` tag is cut, run —
  **before any new feature work** —
  ```
  git fetch origin && git checkout dev && git reset --hard origin/main && git push --force-with-lease origin dev
  ```
  `dev` restarts cleanly from the released commit, so it can never sit behind
  `main`. This step has existed since 0.7.2; skipping it after 0.7.5 is how `dev`
  ended up two releases behind through 0.7.7.
- **If `dev` has *already* diverged with unreleased work** (so a hard reset would
  discard it), don't reset — recover with a `chore/sync-dev-with-main` PR instead:
  `git merge origin/main` into `dev`, resolving squash conflicts in favour of
  `main` (the content-newer side). This is how the 0.7.7 gap was reconciled.
- **Optionally, finalize releases *through* `dev`** (author the version bump,
  `CHANGELOG`, and baseline freeze as PRs into `dev`, or merge the `release/x.y`
  branch back into `dev`) so `main` never holds content that isn't already on
  `dev` — which makes the realign a clean no-op.

A scheduled CI check (`.github/workflows/branch-drift.yml`) fails if `dev` is ever
on an older release than `main`, so a skipped realign is caught the next day
instead of accumulating across releases.

## Before you open a PR

- Run the test suite: `python3 tests/render/test_render.py` — it should report all checks passing.
- If you changed `skills/behavior-verifier/render.py` or `report_template.html`, regenerate the golden fixtures (see the header comment in `tests/render/test_render.py`) and include them in your PR.
- Keep changes scoped; one logical change per PR.
