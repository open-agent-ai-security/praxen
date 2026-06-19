#!/usr/bin/env bash
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
#
# Post-tag plugin install smoke for Praxen releases.
#
# This is the PRIMARY release-verification check for the two real install
# journeys (clean install + upgrade). The equivalent hand-run `claude plugin …`
# commands in CONTRIBUTING.md ("Releasing and rolling back") are the fallback if
# this script can't run. It is intentionally NOT wired into CI: the `claude` CLI
# is not run in GitHub Actions, so this stays a maintainer-run step.
#
# Both journeys run against isolated, throwaway $CLAUDE_CONFIG_DIR scratch dirs,
# so your live Claude Code install is never touched.
#
#   scripts/release/plugin-smoke.sh [TARGET] [PRIOR_TAG]
#
#   TARGET     version or tag to verify   (default: the PRAXEN_SPEC.md version)
#   PRIOR_TAG  tag to seed the upgrade from (default: most recently created other tag)
#
# Journeys:
#   1. Clean install — add the GitHub marketplace + install; assert TARGET.
#      Exercises the REAL published state (marketplace serves main@HEAD), so run
#      this AFTER the dev→main promotion and the v<TARGET> tag are pushed.
#   2. Upgrade       — seed PRIOR_TAG via a local git worktree, install it, then
#      `marketplace update` + `plugin update`; assert it moves to TARGET.
#
# Requires: claude CLI, git, and network access (journey 1 clones the marketplace).
# Exits non-zero on the first failed assertion.
set -euo pipefail

MARKET="open-agent-ai-security"        # marketplace name (from .claude-plugin/marketplace.json)
PLUGIN="praxen@${MARKET}"
REPO_SLUG="open-agent-ai-security/praxen"

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

fail() { echo "  ✗ $*" >&2; exit 1; }
command -v claude >/dev/null 2>&1 || fail "claude CLI not found on PATH"

# --- resolve TARGET (strip a leading v) ---
TARGET="${1:-}"
[ -n "$TARGET" ] || TARGET="$(grep -m1 -E '^\*\*Version:\*\*' PRAXEN_SPEC.md \
  | sed -E 's/.*\*\*Version:\*\*[[:space:]]*//; s/[[:space:]]*$//')"
TARGET="${TARGET#v}"
TARGET_TAG="v${TARGET}"

# make sure release tags are present locally for the worktree checkout
git fetch --tags --quiet origin 2>/dev/null || true
git rev-parse -q --verify "refs/tags/${TARGET_TAG}" >/dev/null \
  || fail "tag ${TARGET_TAG} not found — run this after pushing the release tag"

# --- resolve PRIOR_TAG for the upgrade leg (most recent OTHER tag) ---
PRIOR_TAG="${2:-}"
[ -n "$PRIOR_TAG" ] || PRIOR_TAG="$(git tag --sort=-creatordate | grep -vxF "$TARGET_TAG" | head -1 || true)"

# cleanup state
SCRATCH=()
WORKTREE=""
cleanup() {
  [ -n "$WORKTREE" ] && git worktree remove --force "$WORKTREE" >/dev/null 2>&1 || true
  local d; for d in "${SCRATCH[@]:-}"; do [ -n "$d" ] && rm -rf "$d"; done
}
trap cleanup EXIT

# read praxen's installed version from the current $CLAUDE_CONFIG_DIR
installed_version() { claude plugin list 2>/dev/null | awk '/praxen@/{f=1} f&&/Version:/{print $2; exit}'; }
assert_version() {
  local want="$1" got; got="$(installed_version)"
  [ "$got" = "$want" ] || fail "expected version '$want', got '${got:-<none>}'"
  echo "  ✓ reports $got"
}

echo "=== Praxen plugin install smoke — target ${TARGET_TAG} ==="

# ---------- Journey 1: clean install (new-user, real marketplace) ----------
echo "[1/2] clean install from the GitHub marketplace (${REPO_SLUG})"
CONFIG1="$(mktemp -d)"; SCRATCH+=("$CONFIG1")
(
  export CLAUDE_CONFIG_DIR="$CONFIG1"
  claude plugin marketplace add "$REPO_SLUG" >/dev/null
  claude plugin install "$PLUGIN" >/dev/null
)
CLAUDE_CONFIG_DIR="$CONFIG1" assert_version "$TARGET"

# ---------- Journey 2: upgrade (prior tag -> target) ----------
if [ -z "$PRIOR_TAG" ]; then
  echo "[2/2] upgrade — SKIPPED (no prior tag found; first release?)"
else
  PRIOR_VER="${PRIOR_TAG#v}"
  echo "[2/2] upgrade ${PRIOR_TAG} -> ${TARGET_TAG} (seeded via local worktree)"
  CONFIG2="$(mktemp -d)"; SCRATCH+=("$CONFIG2")
  WT_PARENT="$(mktemp -d)"; SCRATCH+=("$WT_PARENT")
  WORKTREE="$WT_PARENT/praxen-prior"
  git worktree add -q "$WORKTREE" "$PRIOR_TAG"
  (
    export CLAUDE_CONFIG_DIR="$CONFIG2"
    claude plugin marketplace add "$WORKTREE" >/dev/null   # local marketplace @ PRIOR_TAG
    claude plugin install "$PLUGIN" >/dev/null
  )
  CLAUDE_CONFIG_DIR="$CONFIG2" assert_version "$PRIOR_VER"
  git -C "$WORKTREE" checkout -q "$TARGET_TAG"             # bump the marketplace source to GA
  (
    export CLAUDE_CONFIG_DIR="$CONFIG2"
    claude plugin marketplace update "$MARKET" >/dev/null
    claude plugin update "$PLUGIN" >/dev/null
  )
  CLAUDE_CONFIG_DIR="$CONFIG2" assert_version "$TARGET"
fi

echo "=== PASS — ${TARGET_TAG} installs clean and upgrades from ${PRIOR_TAG:-<none>} ==="
