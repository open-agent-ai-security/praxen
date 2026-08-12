#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
render_all_remits.py — regenerate (or verify) every committed pretty-remit HTML.

Two sets of remit HTMLs live in the repo, each co-located with the analysis
report it accompanies:

  * examples/<name>/WORKER_REMIT.html      ← examples/<name>/WORKER_REMIT.md
  * tests/baselines/<CURRENT>/<slug>/<slug>-remit.html
                                           ← tests/remits/<slug>.md

Both are deterministic renders (see skills/behavior-verifier/render_remit.py), so
"in sync with the remit" means: re-rendering the source Markdown reproduces the
committed HTML byte-for-byte. This script is the one command that regenerates
them all — the easy fix when a remit changes — and, with --check, the freshness
gate used by tests/render/test_render.py and build.sh.

Usage:
    python3 tests/render/render_all_remits.py            # (re)write all HTMLs
    python3 tests/render/render_all_remits.py --check     # verify in-sync; exit 1 on drift
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO / "skills" / "behavior-verifier"
sys.path.insert(0, str(SKILL_DIR))
import render_remit  # noqa: E402

TEMPLATE = SKILL_DIR / "report_template.html"


def _current_baseline():
    return (REPO / "tests" / "baselines" / "CURRENT").read_text(encoding="utf-8").strip()


def discover():
    """Return [(source_md, dest_html)] for every pretty-remit we maintain."""
    targets = []
    # Showcase examples — each carries its own WORKER_REMIT.md copy.
    ex_dir = REPO / "examples"
    if ex_dir.is_dir():
        for d in sorted(p for p in ex_dir.iterdir() if p.is_dir()):
            md = d / "WORKER_REMIT.md"
            if md.is_file():
                targets.append((md, d / "WORKER_REMIT.html"))
    # Frozen baseline targets — remit source is the freeze-pinned copy in the
    # baseline dir (<slug>-remit.md), so pre-freeze evolution of the live
    # tests/remits/<slug>.md cannot rewrite a frozen artifact. Fall back to the
    # live remit only when no pinned copy exists (pre-1.3 layout).
    base = REPO / "tests" / "baselines" / _current_baseline()
    remits = REPO / "tests" / "remits"
    if base.is_dir():
        for d in sorted(p for p in base.iterdir() if p.is_dir()):
            slug = d.name
            if not list(d.glob(f"{slug}-findings-*.json")):
                continue  # not a scanned target dir
            md = d / f"{slug}-remit.md"
            if not md.is_file():
                md = remits / f"{slug}.md"
            if md.is_file():
                targets.append((md, d / f"{slug}-remit.html"))
    return targets


def _render(md_path, template_text, version):
    return render_remit.render_remit(md_path.read_text(encoding="utf-8"),
                                     template_text, version)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Regenerate or verify all pretty-remit HTMLs.")
    ap.add_argument("--check", action="store_true",
                    help="verify each HTML is in sync with its remit; exit 1 on any drift")
    args = ap.parse_args(argv)

    template_text = TEMPLATE.read_text(encoding="utf-8")
    version = render_remit._praxen_version(None, [SKILL_DIR, REPO])
    targets = discover()
    if not targets:
        print("render_all_remits.py: no remits discovered", file=sys.stderr)
        return 1

    drift, wrote = [], 0
    for md, dest in targets:
        rendered = _render(md, template_text, version)
        if args.check:
            current = dest.read_text(encoding="utf-8") if dest.is_file() else None
            if current != rendered:
                drift.append((md, dest, "missing" if current is None else "out of sync"))
        else:
            dest.write_text(rendered, encoding="utf-8")
            wrote += 1

    if args.check:
        # Orphan sweep: a committed remit HTML whose SOURCE dropped out of
        # discovery (remit md deleted/renamed, findings file renamed off the
        # glob) would otherwise ship stale forever while --check stays green
        # (#208). Any on-disk remit HTML must be a discovered dest.
        dests = {dest.resolve() for _md, dest in targets}
        on_disk = list((REPO / "examples").glob("*/WORKER_REMIT.html")) + \
                  list((REPO / "tests" / "baselines" / _current_baseline()).glob("*/*-remit.html"))
        orphans = [p for p in on_disk if p.resolve() not in dests]
        for p in orphans:
            drift.append((None, p, "orphaned (no discovered source)"))
        if drift:
            print("render_all_remits.py: pretty-remit HTML is out of sync with its remit:",
                  file=sys.stderr)
            for md, dest, why in drift:
                src = f"  (source: {md.relative_to(REPO)})" if md else ""
                print(f"  {why}: {dest.relative_to(REPO)}{src}", file=sys.stderr)
            print("  fix: python3 tests/render/render_all_remits.py", file=sys.stderr)
            return 1
        print(f"render_all_remits.py: all {len(targets)} pretty-remit HTMLs in sync")
        return 0

    print(f"render_all_remits.py: wrote {wrote} pretty-remit HTMLs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
