#!/usr/bin/env bash
#
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
#
# build.sh — package the Praxa distributable zip.
#
# Produces: dist/praxa-<version>.zip
#
# The distribution contains only the files an operator needs to run an analysis.
# Internal docs, deferred specs, build scripts, examples source files, and git
# metadata are excluded. The examples/ directory IS included because it is the
# primary "what does this produce?" artifact for new operators.

set -euo pipefail

# Read version from PRAXA_SPEC.md (line: "**Version:** X.Y.Z")
VERSION="$(grep -m1 -E '^\*\*Version:\*\*' PRAXA_SPEC.md | sed -E 's/.*\*\*Version:\*\*[[:space:]]*//; s/[[:space:]]*$//')"

if [[ -z "$VERSION" ]]; then
  echo "error: could not read version from PRAXA_SPEC.md" >&2
  exit 1
fi

DIST_DIR="dist"
STAGE_DIR="$DIST_DIR/praxa-$VERSION"
ZIP_PATH="$DIST_DIR/praxa-$VERSION.zip"

echo "Building Praxa v$VERSION"

# Clean any prior stage / output for this version
rm -rf "$STAGE_DIR" "$ZIP_PATH"
mkdir -p "$STAGE_DIR"

# Files and directories that ship in the distribution.
# Add here if a new distributable artifact is introduced.
INCLUDE=(
  ".claude-plugin"
  "README.md"
  "PRAXA_SPEC.md"
  "LICENSE"
  "NOTICE"
  "CHANGELOG.md"
  "CONTRIBUTING.md"
  "WORKER_REMIT_template.md"
  "skills"
  "docs"
  "examples"
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

# Strip any local/ directory that might have been inadvertently copied
rm -rf "$STAGE_DIR/local"

# Produce the zip
(cd "$DIST_DIR" && zip -rq "praxa-$VERSION.zip" "praxa-$VERSION")

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
