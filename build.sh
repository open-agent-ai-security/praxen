#!/usr/bin/env bash
#
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
#
# build.sh — package the Praxen distributable zip.
#
# Produces: dist/praxen-<version>.zip
#
# The distribution contains only the files an operator needs to run an analysis.
# Internal docs, deferred specs, build scripts, examples source files, and git
# metadata are excluded. The examples/ directory IS included because it is the
# primary "what does this produce?" artifact for new operators.

set -euo pipefail

# Read version from PRAXEN_SPEC.md (line: "**Version:** X.Y.Z")
VERSION="$(grep -m1 -E '^\*\*Version:\*\*' PRAXEN_SPEC.md | sed -E 's/.*\*\*Version:\*\*[[:space:]]*//; s/[[:space:]]*$//')"

if [[ -z "$VERSION" ]]; then
  echo "error: could not read version from PRAXEN_SPEC.md" >&2
  exit 1
fi

# Sanity-check: PRAXEN_SPEC.md, .claude-plugin/plugin.json, and
# .claude-plugin/marketplace.json must agree on the version. `manifest_to_findings.py`
# reads praxen_version from plugin.json at runtime, so a drift between these
# files silently produces reports stamped with the wrong version.
PLUGIN_VERSION="$(python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['version'])")"
if [[ "$VERSION" != "$PLUGIN_VERSION" ]]; then
  echo "error: version mismatch — PRAXEN_SPEC.md says $VERSION, plugin.json says $PLUGIN_VERSION" >&2
  exit 1
fi
MARKET_VERSION="$(python3 -c "import json; m=json.load(open('.claude-plugin/marketplace.json')); print(m['plugins'][0]['version'])")"
if [[ "$VERSION" != "$MARKET_VERSION" ]]; then
  echo "error: version mismatch — PRAXEN_SPEC.md says $VERSION, marketplace.json praxen entry says $MARKET_VERSION" >&2
  exit 1
fi

# Freshness backstop: rebuild the GitHub Pages docs (guide/) from docs/*.md.
# These pages are NOT packaged — Pages serves them from the repo — but rebuilding
# here catches docs/ edits (or shared-theme changes) that weren't regenerated
# before a tagged release. Requires the build-only `markdown` dependency
# (requirements-dev.txt); skipped with a notice when absent so the stdlib-only CI
# build stays green. The release workflow installs the dep, so a tagged release
# always enforces this check.
if python3 -c "import markdown" >/dev/null 2>&1; then
  echo "Rebuilding docs site (guide/) from docs/*.md…"
  python3 docs_build.py >/dev/null
  if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    if [[ -n "$(git status --porcelain -- guide/)" ]]; then
      echo "error: guide/ is out of date with docs/*.md (or the shared theme)." >&2
      echo "       run 'python3 docs_build.py' and commit the updated guide/*.html." >&2
      git status --porcelain -- guide/ >&2
      exit 1
    fi
  fi
else
  echo "note: 'markdown' not installed — skipping docs (guide/) rebuild + freshness check." >&2
  echo "      run 'pip install -r requirements-dev.txt' to enable (the release workflow does this)." >&2
fi

DIST_DIR="dist"
STAGE_DIR="$DIST_DIR/praxen-$VERSION"
ZIP_PATH="$DIST_DIR/praxen-$VERSION.zip"

echo "Building Praxen v$VERSION"

# Clean any prior stage / output for this version
rm -rf "$STAGE_DIR" "$ZIP_PATH"
mkdir -p "$STAGE_DIR"

# Files and directories that ship in the distribution.
# Add here if a new distributable artifact is introduced.
INCLUDE=(
  ".claude-plugin"
  "README.md"
  "PRAXEN_SPEC.md"
  "LICENSE"
  "NOTICE"
  "CHANGELOG.md"
  "CONTRIBUTING.md"
  "WORKER_REMIT_template.md"
  "skills"
  "docs"
  "examples"
  "graphics"
)

# Note: tests/ is in the source repository but intentionally NOT included in the
# distribution zip. Tests are for contributors; users of the shipped scanner
# don't need the regression harness.

# Copy each item; skip missing optional ones (e.g., LICENSE not yet added)
for item in "${INCLUDE[@]}"; do
  if [[ -e "$item" ]]; then
    cp -R "$item" "$STAGE_DIR/"
  else
    echo "  skip (missing): $item"
  fi
done

# Strip macOS cruft and any .DS_Store that slipped in
find "$STAGE_DIR" -name '.DS_Store' -delete
find "$STAGE_DIR" -name '__MACOSX' -type d -exec rm -rf {} +

# Strip Python bytecode caches — these appear in skills/ once the test suite
# has run on the build machine, and have no business in a source distribution.
find "$STAGE_DIR" -name '__pycache__' -type d -prune -exec rm -rf {} +
find "$STAGE_DIR" -name '*.pyc' -delete

# Strip any local/ directory that might have been inadvertently copied
rm -rf "$STAGE_DIR/local"

# Produce the zip
(cd "$DIST_DIR" && zip -rq "praxen-$VERSION.zip" "praxen-$VERSION")

# Clean up stage
rm -rf "$STAGE_DIR"

SIZE=$(du -h "$ZIP_PATH" | awk '{print $1}')
echo "  → $ZIP_PATH ($SIZE)"

# Summarize contents for sanity
echo ""
echo "Contents:"
unzip -l "$ZIP_PATH" | awk 'NR>3 && $4!="" {print "  " $4}' | head -40
echo ""
echo "Done."
