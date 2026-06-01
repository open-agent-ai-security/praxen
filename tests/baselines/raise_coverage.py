#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Aggregate RAISE scores across a Praxen baseline set and render a
self-contained HTML coverage report.

Walks every `<target>/<target>-findings-*.json` under the chosen baseline
directory, extracts `raise_posture.weighted_overall` and the six per-category
scores, and writes an HTML report with a per-target score heatmap, per-category
score distributions, and a population weighted-overall histogram.

The report's look comes from the shared design system at `assets/praxen-theme.css`
(inlined at render time so the output stays a single self-contained file); only
the table/heatmap/distribution components are defined locally in RAISE_CSS below.

Usage:
    python3 raise_coverage.py [--baseline-dir DIR] [--out FILE]

Defaults: reads the most recent `tests/baselines/v*/` directory found alongside
this script (or alongside owasp_coverage.py if run from the praxen repo),
writes `./raise-coverage-report.html` in the current working directory.
"""
import argparse
import html
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, stdev

from theme_utils import load_theme_css

THIS_DIR = Path(__file__).resolve().parent

def _baseline_sort_key(p: Path):
    """Version-aware sort key for `v*` baseline dirs: compares the numeric
    version components, so v0.7.10 sorts above v0.7.9 (plain name sorting puts
    it below). Non-numeric parts and unparseable names fall back to 0."""
    version = p.name[1:].split("-", 1)[0]  # "0.7.10" from "v0.7.10-claude48"
    nums = [int(part) if part.isdigit() else 0 for part in version.split(".")]
    return (nums, p.name)


def _default_baseline() -> Path:
    """Return the canonical baseline named in CURRENT, falling back to the newest v* dir."""
    current_file = THIS_DIR / "CURRENT"
    if current_file.is_file():
        name = current_file.read_text(encoding="utf-8").strip()
        candidate = THIS_DIR / name
        if candidate.is_dir():
            return candidate
    candidates = sorted([p for p in THIS_DIR.glob("v*") if p.is_dir()],
                        key=_baseline_sort_key, reverse=True)
    return candidates[0] if candidates else THIS_DIR / "v0.7.7-claude48"

DEFAULT_BASELINE = _default_baseline()
DEFAULT_OUT = THIS_DIR / "raise-coverage-report.html"


TARGETS = [
    ("finbot",                  "FinBot",                       "https://github.com/OWASP-ASI/finbot-ctf-demo",
     "OWASP Agentic AI CTF — invoice processor"),
    ("helperbot",               "HelperBot",                    "https://github.com/opena2a-org/damn-vulnerable-ai-agent",
     "Damn Vulnerable AI Agent — training agent"),
    ("langchain-sql",           "LangChain SQL Agent",          "https://github.com/langchain-ai/langchain-community",
     "create_sql_agent toolkit"),
    ("openai-customer-service", "OpenAI Customer Service",      "https://github.com/openai/openai-agents-python",
     "OpenAI Agents SDK example"),
    ("autogen-code-executor",   "AutoGen Code Executor",        "https://github.com/microsoft/autogen",
     "Microsoft AutoGen code-executor family"),
    ("sweep",                   "Sweep",                        "https://github.com/sweepai/sweep",
     "GitHub issue-to-code agent"),
    ("devika",                  "Devika",                       "https://github.com/stitionai/devika",
     "Autonomous software engineer"),
    ("aider",                   "Aider",                        "https://github.com/Aider-AI/aider",
     "Interactive pair-programming agent"),
    ("openhands",               "OpenHands",                    "https://github.com/All-Hands-AI/OpenHands",
     "Autonomous software-engineering platform"),
    ("deepagents-cli",          "Deep Agents CLI",              "https://github.com/langchain-ai/deepagents",
     "LangChain agent harness (MCP coverage)"),
    ("yaah",                    "yaah",                         "https://github.com/dirien/yet-another-agent-harness",
     "Yet Another Agent Harness (MCP coverage)"),
    ("hermes-agent-desktop",    "Hermes (Agent + Desktop)",     "https://github.com/NousResearch/hermes-agent",
     "Multi-component LLM agent + desktop control layer"),
]

RAISE_CATEGORIES = [
    ("limit_your_domain",           "Limit Your Domain",            0.15),
    ("balance_your_knowledge_base", "Balance Your Knowledge Base",  0.15),
    ("implement_zero_trust",        "Implement Zero Trust",         0.25),
    ("manage_your_supply_chain",    "Manage Your Supply Chain",     0.15),
    ("build_an_ai_red_team",        "Build an AI Red Team",         0.15),
    ("monitor_continuously",        "Monitor Continuously",         0.15),
]

MATURITY = {0: "Absent", 1: "Ad hoc", 2: "Partial", 3: "Established", 4: "Strong", 5: "Exemplary"}

# Score colour scale: red → amber → yellow → lime → green → teal. These jewel
# tones read as a heatmap on the dark theme; kept as inline cell styles below.
SCORE_COLORS = {
    0: ("#6B1010", "#FFCCCC"),   # bg, text
    1: ("#7D3800", "#FFDDBB"),
    2: ("#7A5C00", "#FFF0B0"),
    3: ("#1E5C00", "#D6F5C0"),
    4: ("#0A4400", "#B0EFC0"),
    5: ("#003344", "#A0E8F0"),
}

# Report-specific components (heatmap table + distribution bars). Tokens, base
# elements, the hero, sections and footer all come from the shared theme
# (assets/praxen-theme.css), inlined ahead of this in the <style> block.
RAISE_CSS = """
  /* Score table */
  .table-scroll { overflow-x: auto; }
  .score-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .score-table th {
    background: var(--panel-2); color: var(--text); padding: 11px 12px;
    text-align: center; font-weight: 600; white-space: nowrap; border-bottom: 1px solid var(--border);
  }
  .score-table th.target-hdr { text-align: left; min-width: 220px; }
  .score-table th.overall-hdr { background: rgba(255,122,46,0.12); color: var(--orange-2); font-size: 12px; }
  .score-table th.cat-header { font-size: 12px; min-width: 72px; }
  .score-table tbody tr { border-bottom: 1px solid var(--border); }
  .score-table tbody tr:hover { background: var(--panel); }
  .score-cell {
    text-align: center; padding: 10px 8px; font-weight: 700;
    font-size: 14px; cursor: default; white-space: nowrap;
  }
  .score-cell.score-missing { color: var(--muted-2); background: transparent; }
  .score-cell.score-overall { font-size: 13px; font-weight: 700; min-width: 72px; }
  .score-sub { font-size: 10px; font-weight: 400; display: block; margin-top: 1px; opacity: 0.85; }
  .target-cell { padding: 10px 14px; vertical-align: top; min-width: 220px; }
  .tgt-name { font-family: "Space Grotesk"; font-weight: 600; font-size: 13px; color: var(--text); }
  .tgt-blurb { font-size: 11.5px; color: var(--muted); margin: 2px 0 6px; }
  .tgt-links { display: flex; gap: 8px; }
  .tbl-link {
    font-size: 11px; color: var(--orange-2); text-decoration: none;
    padding: 3px 8px; border: 1px solid var(--border); border-radius: 7px;
  }
  .tbl-link:hover { background: var(--panel-2); border-color: var(--border-hi); }
  .table-note { font-size: 12px; color: var(--muted); margin-top: 12px; }

  /* Distribution charts */
  .cat-block { margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid var(--border); }
  .cat-block:last-child { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }
  .cat-block-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; flex-wrap: wrap; gap: 4px; }
  .cat-block-name { font-family: "Space Grotesk"; font-weight: 600; font-size: 14px; color: var(--text); }
  .cat-block-meta { font-size: 12px; color: var(--muted); }
  .cat-dist { display: flex; flex-direction: column; gap: 5px; }
  .dist-row { display: grid; grid-template-columns: 200px 1fr; gap: 12px; align-items: center; }
  .dist-label { display: flex; align-items: center; gap: 8px; }
  .dist-score {
    display: inline-block; min-width: 24px; text-align: center;
    padding: 2px 6px; border-radius: 6px;
    font-weight: 700; font-size: 12px;
  }
  .dist-maturity { font-size: 12px; color: var(--muted); }
  .dist-track {
    position: relative; height: 22px; background: var(--panel);
    border: 1px solid var(--border); border-radius: 7px; overflow: hidden;
  }
  .dist-fill { height: 100%; border-radius: 6px 0 0 6px; transition: width 0.3s; min-width: 2px; opacity: 0.9; }
  .dist-count {
    position: absolute; right: 8px; top: 50%; transform: translateY(-50%);
    font-size: 11px; font-weight: 600; color: var(--text); text-shadow: 0 1px 2px rgba(0,0,0,0.5);
  }
  .overall-stats { font-size: 13px; color: var(--muted); margin-bottom: 14px; }
  .overall-stats strong { color: var(--text); }

  @media (max-width: 720px) {
    .dist-row { grid-template-columns: 160px 1fr; }
    .topline { gap: 14px; }
  }
"""


# ---------------------------------------------------------------------------
# Data gathering
# ---------------------------------------------------------------------------

def gather(baseline_dir: Path):
    """Return per-target RAISE data and aggregate counters."""
    per_target = {}
    all_weighted = []
    cat_scores = {key: [] for key, _, _ in RAISE_CATEGORIES}

    for slug, name, url, blurb in TARGETS:
        target_dir = baseline_dir / slug
        json_files = sorted(target_dir.glob(f"{slug}-findings-*.json"))
        if not json_files:
            continue
        try:
            with open(json_files[-1], encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"raise_coverage.py: warning: skipping {slug} — {e}", file=sys.stderr)
            continue

        rp = data.get("raise_posture") or {}
        weighted = rp.get("weighted_overall")
        cats_raw = rp.get("categories") or []
        cats = {c["key"]: c for c in cats_raw if "key" in c}

        analysis_html = sorted(target_dir.glob(f"{slug}-analysis-*.html"))
        per_target[slug] = {
            "name": name,
            "url": url,
            "blurb": blurb,
            "weighted": weighted,
            "categories": cats,
            "report": analysis_html[-1].resolve() if analysis_html else None,
            "n_findings": len(data.get("findings") or []),
        }
        if weighted is not None:
            all_weighted.append(weighted)
        for key, _, _ in RAISE_CATEGORIES:
            if key in cats and cats[key].get("score") is not None:
                cat_scores[key].append(cats[key]["score"])

    return per_target, all_weighted, cat_scores


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def score_cell(score, show_label=False):
    """Render one RAISE score as a coloured table cell."""
    if score is None:
        return '<td class="score-cell score-missing" title="Not available">—</td>'
    bg, fg = SCORE_COLORS.get(score, ("#999", "#000"))
    label = MATURITY.get(score, "")
    title = f"{score}/5 — {label}"
    content = str(score)
    if show_label:
        content = f"{score} <span class='score-sub'>{label}</span>"
    return (
        f'<td class="score-cell" style="background:{bg};color:{fg};" title="{html.escape(title)}">'
        f'{content}</td>'
    )


def weighted_cell(w):
    """Render the weighted-overall score as a coloured cell."""
    if w is None:
        return '<td class="score-cell score-missing">—</td>'
    floor_score = min(5, int(w))
    bg, fg = SCORE_COLORS.get(floor_score, ("#999", "#000"))
    label = MATURITY.get(floor_score, "")
    return (
        f'<td class="score-cell score-overall" style="background:{bg};color:{fg};" '
        f'title="{w:.2f}/5.0 — {label}">{w:.2f}</td>'
    )


def score_table(per_target, out_dir: Path):
    """Render the per-target heatmap table, sorted by weighted_overall desc."""
    order = sorted(
        [s for s in per_target if per_target[s].get("weighted") is not None],
        key=lambda s: per_target[s]["weighted"],
        reverse=True,
    )
    # Append any targets with missing data at the end
    order += [s for s in per_target if per_target[s].get("weighted") is None]

    cat_headers = "".join(
        f'<th class="cat-header" title="{html.escape(name)}">{html.escape(short)}</th>'
        for short, name in [
            ("Domain", "Limit Your Domain"),
            ("Knowledge", "Balance Your Knowledge Base"),
            ("Zero Trust", "Implement Zero Trust (×1.67)"),
            ("Supply Chain", "Manage Your Supply Chain"),
            ("Red Team", "Build an AI Red Team"),
            ("Monitor", "Monitor Continuously"),
        ]
    )

    rows = []
    for slug in order:
        info = per_target[slug]
        cats = info.get("categories") or {}
        name = html.escape(info["name"])
        url = html.escape(info["url"])
        blurb = html.escape(info["blurb"])

        report_link = ""
        if info.get("report"):
            try:
                rel = Path(os.path.relpath(info["report"], out_dir)).as_posix()
            except ValueError:
                rel = info["report"].as_uri()
            report_link = f'<a class="tbl-link" href="{rel}" target="_blank" rel="noopener">report ↗</a>'

        cat_cells = "".join(
            score_cell(cats.get(key, {}).get("score") if key in cats else None)
            for key, _, _ in RAISE_CATEGORIES
        )
        rows.append(f"""
        <tr>
          <td class="target-cell">
            <div class="tgt-name">{name}</div>
            <div class="tgt-blurb">{blurb}</div>
            <div class="tgt-links">
              <a class="tbl-link" href="{url}" target="_blank" rel="noopener">repo ↗</a>
              {report_link}
            </div>
          </td>
          {cat_cells}
          {weighted_cell(info.get("weighted"))}
        </tr>""")

    return f"""
    <div class="table-scroll">
    <table class="score-table">
      <thead>
        <tr>
          <th class="target-hdr">Agent / Target</th>
          {cat_headers}
          <th class="overall-hdr" title="Σ(score × weight); Zero Trust weight = 0.25, others 0.15">Weighted<br>Overall</th>
        </tr>
      </thead>
      <tbody>{"".join(rows)}</tbody>
    </table>
    </div>
    <p class="table-note">Sorted by weighted overall (highest first). Cell colour: <span style="background:#6B1010;color:#FFCCCC;padding:1px 6px;border-radius:3px;font-size:11px;">0 Absent</span> → <span style="background:#003344;color:#A0E8F0;padding:1px 6px;border-radius:3px;font-size:11px;">5 Exemplary</span>. Hover for maturity label.</p>
    """


def distribution_section(cat_scores, per_target):
    """Render per-category score distribution charts."""
    n = len([s for s in per_target if per_target[s].get("weighted") is not None])
    blocks = []
    for key, name, weight in RAISE_CATEGORIES:
        scores = cat_scores.get(key) or []
        counts = Counter(scores)
        avg = mean(scores) if scores else None
        sd = stdev(scores) if len(scores) > 1 else 0.0

        bars = []
        for s in range(6):
            c = counts.get(s, 0)
            pct = c / n * 100 if n else 0
            bg, fg = SCORE_COLORS[s]
            label = MATURITY[s]
            bar = f"""
            <div class="dist-row">
              <div class="dist-label">
                <span class="dist-score" style="background:{bg};color:{fg};">{s}</span>
                <span class="dist-maturity">{label}</span>
              </div>
              <div class="dist-track">
                <div class="dist-fill" style="width:{pct:.1f}%;background:{bg};"></div>
                <span class="dist-count">{c} of {n}</span>
              </div>
            </div>"""
            bars.append(bar)

        avg_str = f"{avg:.2f}" if avg is not None else "—"
        sd_str = f"±{sd:.2f}" if sd else ""
        weight_pct = int(weight * 100)
        blocks.append(f"""
        <div class="cat-block">
          <div class="cat-block-header">
            <span class="cat-block-name">{html.escape(name)}</span>
            <span class="cat-block-meta">weight {weight_pct}% &nbsp;·&nbsp; population avg {avg_str} {sd_str}</span>
          </div>
          <div class="cat-dist">{"".join(bars)}</div>
        </div>""")

    return "\n".join(blocks)


def overall_histogram(all_weighted):
    """Render a histogram of weighted-overall values across the population."""
    if not all_weighted:
        return "<p>No data.</p>"

    # Buckets: 0–<1, 1–<2, 2–<3, 3–<4, 4–<5, 5
    buckets = [[] for _ in range(6)]
    for w in all_weighted:
        buckets[max(0, min(5, int(w)))].append(w)

    n = len(all_weighted)
    pop_avg = mean(all_weighted)
    pop_max = max(all_weighted)
    pop_min = min(all_weighted)
    max_count = max(len(b) for b in buckets) or 1

    rows = []
    for i, bucket in enumerate(buckets):
        c = len(bucket)
        pct = c / max_count * 100
        bg, fg = SCORE_COLORS[i]
        label = MATURITY[i]
        range_str = f"{i}.0 – {i}.99" if i < 5 else "5.0"
        avg_str = f"(avg {mean(bucket):.2f})" if bucket else ""
        rows.append(f"""
        <div class="dist-row">
          <div class="dist-label">
            <span class="dist-score" style="background:{bg};color:{fg};">{label}</span>
            <span class="dist-maturity">{range_str}</span>
          </div>
          <div class="dist-track">
            <div class="dist-fill" style="width:{pct:.1f}%;background:{bg};"></div>
            <span class="dist-count">{c} of {n} {avg_str}</span>
          </div>
        </div>""")

    return f"""
    <div class="overall-stats">
      Population: <strong>{n}</strong> targets &nbsp;·&nbsp;
      Average: <strong>{pop_avg:.2f}</strong> &nbsp;·&nbsp;
      Range: <strong>{pop_min:.2f}</strong> – <strong>{pop_max:.2f}</strong>
    </div>
    <div class="cat-dist">{"".join(rows)}</div>
    """


# ---------------------------------------------------------------------------
# Main report builder
# ---------------------------------------------------------------------------

def build_report(baseline_dir: Path, out_path: Path) -> str:
    per_target, all_weighted, cat_scores = gather(baseline_dir)
    out_dir = out_path.resolve().parent

    n_targets = len(per_target)
    n_scored = len(all_weighted)
    pop_avg = f"{mean(all_weighted):.2f}" if all_weighted else "—"
    generated = datetime.now(timezone.utc).strftime("%B %d, %Y, %H:%M UTC")
    baseline_name = baseline_dir.name
    theme_css = load_theme_css()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Praxen — RAISE Score Distribution Across Baseline Targets</title>
<style>{theme_css}
{RAISE_CSS}</style>
</head>
<body class="report-page">
<div class="wrap">

  <header class="hero">
    <h1>RAISE Score Distribution Across Praxen Baseline Targets</h1>
    <p class="subtitle">Per-target scores and population distributions for all six RAISE categories,
    drawn from the frozen <code>tests/baselines/{html.escape(baseline_name)}/</code> baseline set.</p>
    <div class="topline">
      <div class="stat-block"><strong>{n_targets}</strong><span>targets analyzed</span></div>
      <div class="stat-block"><strong>{n_scored}</strong><span>with RAISE scores</span></div>
      <div class="stat-block"><strong>{pop_avg}</strong><span>population avg weighted overall</span></div>
    </div>
  </header>

  <section>
    <h2>Per-target RAISE scores <span class="scope">sorted by weighted overall, highest first</span></h2>
    <p class="intro">
      Each row shows all six RAISE category scores (0–5) and the weighted overall for one baseline target.
      <strong>Implement Zero Trust</strong> carries weight&nbsp;0.25; the other five carry 0.15 each.
      Hover any cell to see the maturity label.
    </p>
    {score_table(per_target, out_dir)}
  </section>

  <section>
    <h2>Score distribution by RAISE component <span class="scope">how many targets land at each maturity level</span></h2>
    <p class="intro">
      For each of the six RAISE categories, the bars show how many of the {n_scored} scored targets
      received each maturity level (0&nbsp;Absent through 5&nbsp;Exemplary).
      The population average and standard deviation are shown per category.
    </p>
    {distribution_section(cat_scores, per_target)}
  </section>

  <section>
    <h2>Population weighted-overall distribution <span class="scope">across all {n_scored} targets</span></h2>
    <p class="intro">
      Histogram of weighted-overall scores grouped by maturity band.
      Each band covers one integer step (0.0–0.99 = Ad hoc, etc.).
    </p>
    {overall_histogram(all_weighted)}
  </section>

  <section>
    <h2>Methodology <span class="scope">how scores were computed</span></h2>
    <p class="intro">
      RAISE scores are drawn from the <code>raise_posture.categories[].score</code> fields in each
      baseline findings JSON. The weighted overall is
      <code>raise_posture.weighted_overall</code> — Σ(score&nbsp;×&nbsp;weight) across the six
      categories, where Implement&nbsp;Zero&nbsp;Trust has weight&nbsp;0.25 and the other five
      have weight&nbsp;0.15. Scores are from static source scans run at the version pinned in the
      baseline directory name; they reflect the agent's posture at the time of the scan, not the
      current state of the target repositories.
      See <code>tests/baselines/README.md</code> for the full baseline methodology.
    </p>
  </section>

  <footer class="foot">
    Generated {generated}&nbsp;·&nbsp;Built on the Praxen <code>{html.escape(baseline_name)}</code> baseline set&nbsp;·&nbsp;
    <a href="https://github.com/open-agent-ai-security/praxen" target="_blank" rel="noopener">github.com/open-agent-ai-security/praxen</a>
  </footer>

</div>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Render a Praxen RAISE score distribution HTML report from a baseline set.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example:\n  python3 raise_coverage.py --out /tmp/raise.html\n",
    )
    parser.add_argument(
        "--baseline-dir",
        type=Path,
        default=DEFAULT_BASELINE,
        help=f"Baseline set to aggregate (default: {DEFAULT_BASELINE}).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output HTML path (default: ./raise-coverage-report.html).",
    )
    args = parser.parse_args()

    if not args.baseline_dir.is_dir():
        print(f"raise_coverage.py: baseline directory not found: {args.baseline_dir}", file=sys.stderr)
        sys.exit(1)

    report = build_report(args.baseline_dir, args.out)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(f"raise_coverage.py: wrote {args.out}")


if __name__ == "__main__":
    main()
