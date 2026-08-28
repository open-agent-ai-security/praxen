#!/usr/bin/env bash
#
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
#
# stage_plugin_payload.sh — build the vendored plugin payload for the
# community catalog (open-agent-ai-security/plugins).
#
# The catalog installs Praxen from a directory vendored INTO the plugins
# repo ("source": "./<dir>"), so users pull ~1 MB of skill instead of the
# whole product repo. This script is the release step that produces that
# directory: the shared distribution allowlist
# (scripts/release/dist_manifest.txt) minus its `zip-only` entries, minus
# the repo's legacy marketplace mirror, with the same cruft-stripping as
# the zip build. Run it from any branch — it stages whatever that branch's
# manifests declare (praxen on v2/main, praxen-beta on v2-beta).
#
# Usage:
#   scripts/release/stage_plugin_payload.sh <dest-dir>            stage into empty/new dest
#   scripts/release/stage_plugin_payload.sh --force <dest-dir>    replace dest's contents
#   scripts/release/stage_plugin_payload.sh --check <dest-dir>    no writes; diff staged
#                                                                 tree vs dest, exit 1 on drift
#
# A release cut is: bump_version.py, docs_build.py, commit, then this script
# pointed at the plugins repo's vendored directory (e.g. ../plugins/praxen-beta)
# and a PR there. --check answers "is the vendored copy current?" without
# touching anything.

set -euo pipefail

MODE="stage"
DEST=""
for arg in "$@"; do
  case "$arg" in
    --force) MODE="force" ;;
    --check) MODE="check" ;;
    -h|--help) sed -n '5,29p' "$0"; exit 0 ;;
    -*) echo "error: unknown flag $arg" >&2; exit 2 ;;
    *) if [[ -n "$DEST" ]]; then echo "error: exactly one dest-dir, got '$DEST' and '$arg'" >&2; exit 2; fi
       DEST="$arg" ;;
  esac
done
if [[ -z "$DEST" ]]; then
  echo "usage: $0 [--force|--check] <dest-dir>" >&2
  exit 2
fi

# Repo root = two levels up from this script, so it runs from anywhere.
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

DIST_MANIFEST="scripts/release/dist_manifest.txt"
if [[ ! -f "$DIST_MANIFEST" ]]; then
  echo "error: $DIST_MANIFEST not found — the distribution allowlist is gone" >&2
  exit 1
fi

# The payload's identity comes from the branch's own manifests. Guard the
# same invariant build.sh guards: the two plugin manifests must agree —
# manifest_to_findings.py stamps reports from the Claude one, and a Codex
# drift ships a different version under the same catalog entry.
NAME="$(python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['name'])")"
VERSION="$(python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['version'])")"
CODEX_VERSION="$(python3 -c "import json; print(json.load(open('.codex-plugin/plugin.json'))['version'])")"
CODEX_NAME="$(python3 -c "import json; print(json.load(open('.codex-plugin/plugin.json'))['name'])")"
if [[ "$VERSION" != "$CODEX_VERSION" || "$NAME" != "$CODEX_NAME" ]]; then
  echo "error: plugin manifests disagree — claude says $NAME@$VERSION, codex says $CODEX_NAME@$CODEX_VERSION" >&2
  exit 1
fi

# Stage into a temp dir first; nothing touches DEST until the tree is
# complete and has passed the assertions below.
STAGE="$(mktemp -d "${TMPDIR:-/tmp}/praxen-payload.XXXXXX")"
trap 'rm -rf "$STAGE"' EXIT

while read -r item tag _; do
  case "$item" in ''|'#'*) continue ;; esac
  if [[ "${tag:-}" == "zip-only" ]]; then continue; fi
  if [[ -e "$item" ]]; then
    cp -R "$item" "$STAGE/"
  else
    echo "  skip (missing): $item"
  fi
done < "$DIST_MANIFEST"

# The legacy marketplace mirror is catalog metadata for installs added from
# the product repo itself — it is not part of a plugin and confuses a
# vendored payload (a marketplace inside a marketplace).
rm -f "$STAGE/.claude-plugin/marketplace.json"

# Same strips as the zip build.
find "$STAGE" -name '.DS_Store' -delete
find "$STAGE" -name '__MACOSX' -type d -exec rm -rf {} +
find "$STAGE" -name '__pycache__' -type d -prune -exec rm -rf {} +
find "$STAGE" -name '*.pyc' -delete
rm -rf "$STAGE/local"

# Assertions: the payload must be installable and catalog-clean before it
# replaces anything. These encode the skill's real runtime shape — SKILL.md
# reads ../../WORKER_REMIT_template.md and manifest_to_findings.py reads
# ../../.claude-plugin/plugin.json — plus the catalog validator's symlink ban.
fail=0
must_exist=(
  ".claude-plugin/plugin.json"
  ".codex-plugin/plugin.json"
  "skills/behavior-verifier/SKILL.md"
  "WORKER_REMIT_template.md"
  "LICENSE"
  "NOTICE"
)
for f in "${must_exist[@]}"; do
  if [[ ! -f "$STAGE/$f" ]]; then echo "error: staged payload is missing $f" >&2; fail=1; fi
done
if [[ -e "$STAGE/.claude-plugin/marketplace.json" ]]; then
  echo "error: staged payload still contains .claude-plugin/marketplace.json" >&2; fail=1
fi
for banned in graphics examples tests; do
  if [[ -e "$STAGE/$banned" ]]; then
    echo "error: staged payload contains $banned/ — zip-only/non-distribution content" >&2; fail=1
  fi
done
SYMLINKS="$(find "$STAGE" -type l)"
if [[ -n "$SYMLINKS" ]]; then
  echo "error: staged payload contains symlinks (the catalog validator rejects them):" >&2
  echo "$SYMLINKS" >&2
  fail=1
fi
if [[ "$fail" -ne 0 ]]; then exit 1; fi

COUNT="$(find "$STAGE" -type f | wc -l | tr -d ' ')"
SIZE="$(du -sh "$STAGE" | awk '{print $1}')"

if [[ "$MODE" == "check" ]]; then
  if [[ ! -d "$DEST" ]]; then
    echo "check: dest $DEST does not exist (staged $NAME@$VERSION would create it)" >&2
    exit 1
  fi
  if diff -r "$STAGE" "$DEST" >/dev/null 2>&1; then
    echo "check OK — $DEST matches a fresh stage of $NAME@$VERSION ($COUNT files, $SIZE)"
    exit 0
  fi
  echo "check FAILED — $DEST drifts from a fresh stage of $NAME@$VERSION:" >&2
  diff -rq "$STAGE" "$DEST" >&2 || true
  exit 1
fi

if [[ -d "$DEST" && -n "$(ls -A "$DEST" 2>/dev/null)" ]]; then
  if [[ "$MODE" != "force" ]]; then
    echo "error: $DEST exists and is not empty — pass --force to replace its contents" >&2
    exit 1
  fi
  # Replace contents, keep the directory (its git history lives in the
  # destination repo). Dotfiles included.
  find "$DEST" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
fi
mkdir -p "$DEST"
cp -R "$STAGE"/. "$DEST"/

echo "staged $NAME@$VERSION → $DEST ($COUNT files, $SIZE)"
echo "next: commit/PR in the destination repo, then verify with:"
echo "  $0 --check $DEST"
