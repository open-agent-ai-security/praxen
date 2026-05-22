<!--
  Thanks for sending a PR to Praxen.

  Base branch: target `dev`, not `main`. `main` is the release branch and only
  receives release PRs. If GitHub defaulted the base to `main`, switch it to
  `dev` (unless you are specifically cutting a release).

  Please fill in the sections below. If a section truly does not apply
  (e.g. a docs-only change has no functional testing), say so explicitly
  rather than deleting the heading — it signals to reviewers that you
  considered it.

  By opening this pull request you confirm that your contribution is
  signed off under the Developer Certificate of Origin (`git commit -s`).
  CI enforces this; unsigned commits will fail.
-->

## Summary

<!-- What does this PR change? One or two sentences for the change, plus a
sentence on *why* it's needed (motivating problem, linked issue/RFE, field
report, etc.). Link related issues with `Closes #N` / `Refs #N`. -->

## Testing

<!-- How did you verify the change?
  - `python3 tests/render/test_render.py` should be green; paste the
    one-line summary (`N passed, 0 failed`).
  - For changes to the SKILL prompt, the renderer, the schema, or the
    JSON template, describe any baselines or fixtures you re-rendered
    and how you confirmed they are correct.
  - For docs-only changes, "n/a — docs only; rendered locally" is fine. -->

## Notes for reviewers

<!-- Anything reviewers should look at first, design choices worth
flagging, follow-up work intentionally deferred. Optional. -->
