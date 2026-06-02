#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Aggregate OWASP finding counts across a Praxen baseline set and render a
self-contained HTML coverage report.

Walks every `<target>/<target>-findings-*.json` under the chosen baseline
directory, sums the per-finding `owasp_llm` / `owasp_agentic` primary scalars,
and writes an HTML report with bar charts and target links.

The report's look comes from the shared design system at `assets/praxen-theme.css`
(inlined at render time so the output stays a single self-contained file); only
the chart/card components are defined locally in OWASP_CSS below.

Usage:
    python3 tests/baselines/owasp_coverage.py [--baseline-dir DIR] [--out FILE]

Defaults: reads `tests/baselines/v0.7.7-claude48/`, writes
`./owasp-coverage-report.html` in the current working directory.
"""
import argparse
import html
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from theme_utils import load_theme_css, DOCS_BASE

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
DEFAULT_OUT = THIS_DIR / "owasp-coverage-report.html"


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

LLM_TITLES = [
    ("LLM01", "Prompt Injection"),
    ("LLM02", "Sensitive Information Disclosure"),
    ("LLM03", "Supply Chain"),
    ("LLM04", "Data and Model Poisoning"),
    ("LLM05", "Improper Output Handling"),
    ("LLM06", "Excessive Agency"),
    ("LLM07", "System Prompt Leakage"),
    ("LLM08", "Vector and Embedding Weaknesses"),
    ("LLM09", "Misinformation"),
    ("LLM10", "Unbounded Consumption"),
]
ASI_TITLES = [
    ("ASI01", "Agent Goal Hijack"),
    ("ASI02", "Tool Misuse and Exploitation"),
    ("ASI03", "Identity and Privilege Abuse"),
    ("ASI04", "Agentic Supply Chain Vulnerabilities"),
    ("ASI05", "Unexpected Code Execution (RCE)"),
    ("ASI06", "Memory and Context Poisoning"),
    ("ASI07", "Insecure Inter-Agent Communication"),
    ("ASI08", "Cascading Failures"),
    ("ASI09", "Human-Agent Trust Exploitation"),
    ("ASI10", "Rogue Agents"),
]

# Report-specific components (cards + bar charts). Tokens, base elements,
# buttons, the hero, sections and footer all come from the shared theme
# (assets/praxen-theme.css), inlined ahead of this in the <style> block.
OWASP_CSS = """
  .target-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }
  .target-card {
    display: flex; flex-direction: column;
    border: 1px solid var(--border); border-radius: 14px; padding: 16px 18px;
    background: var(--panel); transition: transform .18s ease, border-color .18s ease, background .18s ease;
  }
  .target-card:hover { transform: translateY(-3px); border-color: var(--border-hi); background: var(--panel-2); }
  .target-name { font-family: "Space Grotesk"; font-size: 15px; font-weight: 600; color: var(--text); margin-bottom: 4px; }
  .target-blurb { font-size: 12.5px; color: var(--muted); margin-bottom: 12px; min-height: 32px; }
  .target-stats { display: flex; gap: 14px; font-size: 12px; color: var(--muted); margin-bottom: 12px; }
  .target-stats strong { color: var(--text); font-weight: 700; }
  .target-links { display: flex; gap: 8px; margin-top: auto; padding-top: 12px; border-top: 1px solid var(--border); }
  .card-link {
    flex: 1; text-align: center; padding: 7px 10px; border-radius: 9px;
    font-size: 12px; font-weight: 600; text-decoration: none; transition: all .15s ease; white-space: nowrap;
  }
  .card-link-source { color: var(--text); background: var(--panel); border: 1px solid var(--border); }
  .card-link-source:hover { background: var(--panel-2); border-color: var(--border-hi); color: var(--text); }
  .card-link-report { color: #1a0f06; background: linear-gradient(100deg, var(--orange-2), var(--orange-deep)); border: 1px solid transparent; }
  .card-link-report:hover { color: #1a0f06; box-shadow: 0 6px 18px -6px rgba(255,122,46,0.6); }
  .card-link-disabled { color: var(--muted-2); background: var(--panel); border: 1px solid var(--border); cursor: not-allowed; }

  .chart { margin-top: 8px; }
  .bar-row { display: grid; grid-template-columns: 280px 1fr; gap: 14px; align-items: center; padding: 6px 0; }
  .bar-label { font-size: 13px; color: var(--text); }
  .bar-code {
    display: inline-block; min-width: 46px; padding: 2px 7px; margin-right: 8px;
    border-radius: 6px; background: var(--panel-2); color: var(--orange-2); border: 1px solid var(--border);
    font-family: var(--mono); font-size: 11px; font-weight: 600;
  }
  .bar-track {
    position: relative; height: 24px; background: var(--panel);
    border: 1px solid var(--border); border-radius: 7px; overflow: hidden;
  }
  .bar-fill { height: 100%; border-radius: 6px 0 0 6px; transition: width 0.3s; }
  .bar-count {
    position: absolute; right: 8px; top: 50%; transform: translateY(-50%);
    font-size: 12px; font-weight: 700; color: var(--text); text-shadow: 0 1px 2px rgba(0,0,0,0.55);
  }
  .bar-row.is-empty .bar-label { color: var(--muted-2); }
  .bar-row.is-empty .bar-count { color: var(--muted-2); text-shadow: none; }

  @media (max-width: 720px) {
    .bar-row { grid-template-columns: 1fr; }
    .bar-label { margin-bottom: 4px; }
    .topline { gap: 14px; }
  }
"""


def gather(baseline_dir: Path):
    llm = Counter()
    asi = Counter()
    per_target = {}
    total = 0
    for slug, _, _, _ in TARGETS:
        target_dir = baseline_dir / slug
        json_files = sorted(target_dir.glob(f"{slug}-findings-*.json"))
        if not json_files:
            continue
        with open(json_files[-1], encoding="utf-8") as f:
            data = json.load(f)
        findings = data.get("findings") or []
        t_llm = Counter()
        t_asi = Counter()
        for fnd in findings:
            if fnd.get("owasp_llm"):
                llm[fnd["owasp_llm"]] += 1
                t_llm[fnd["owasp_llm"]] += 1
            if fnd.get("owasp_agentic"):
                asi[fnd["owasp_agentic"]] += 1
                t_asi[fnd["owasp_agentic"]] += 1
        # Pick the most recent analysis HTML alongside the findings JSON.
        analysis_html = sorted(target_dir.glob(f"{slug}-analysis-*.html"))
        per_target[slug] = {
            "count": len(findings),
            "llm": t_llm,
            "asi": t_asi,
            "report": analysis_html[-1].resolve() if analysis_html else None,
        }
        total += len(findings)
    return llm, asi, per_target, total


def bar_chart(rows, max_count, accent):
    out = ['<div class="chart">']
    for code, title, count in rows:
        pct = (count / max_count * 100) if max_count else 0
        empty_class = " is-empty" if count == 0 else ""
        out.append(f'''
        <div class="bar-row{empty_class}">
          <div class="bar-label"><span class="bar-code">{html.escape(code)}</span> {html.escape(title)}</div>
          <div class="bar-track">
            <div class="bar-fill" style="width:{pct:.1f}%; background:{accent};"></div>
            <span class="bar-count">{count}</span>
          </div>
        </div>''')
    out.append('</div>')
    return "\n".join(out)


def target_cards(per_target, out_dir: Path):
    out = ['<div class="target-grid">']
    for slug, name, url, blurb in TARGETS:
        info = per_target.get(slug, {"count": 0, "llm": Counter(), "asi": Counter(), "report": None})
        llm_total = sum(info["llm"].values())
        asi_total = sum(info["asi"].values())

        report_link = ""
        if info.get("report"):
            try:
                rel = Path(os.path.relpath(info["report"], out_dir)).as_posix()
            except ValueError:
                rel = info["report"].as_uri()
            report_link = (
                f'<a class="card-link card-link-report" href="{html.escape(rel)}" '
                f'target="_blank" rel="noopener">Baseline report ↗</a>'
            )
        else:
            report_link = '<span class="card-link card-link-disabled">No baseline report</span>'

        out.append(f'''
        <div class="target-card">
          <div class="target-name">{html.escape(name)}</div>
          <div class="target-blurb">{html.escape(blurb)}</div>
          <div class="target-stats">
            <span class="stat"><strong>{info["count"]}</strong> findings</span>
            <span class="stat"><strong>{llm_total}</strong> LLM</span>
            <span class="stat"><strong>{asi_total}</strong> Agentic</span>
          </div>
          <div class="target-links">
            <a class="card-link card-link-source" href="{html.escape(url)}" target="_blank" rel="noopener">Source repo ↗</a>
            {report_link}
          </div>
        </div>''')
    out.append('</div>')
    return "\n".join(out)


def build_report(baseline_dir: Path, out_path: Path) -> str:
    llm, asi, per_target, total = gather(baseline_dir)
    out_dir = out_path.resolve().parent

    llm_rows = [(c, t, llm.get(c, 0)) for c, t in LLM_TITLES]
    asi_rows = [(c, t, asi.get(c, 0)) for c, t in ASI_TITLES]
    max_llm = max(c for _, _, c in llm_rows) or 1
    max_asi = max(c for _, _, c in asi_rows) or 1
    llm_total = sum(llm.values())
    asi_total = sum(asi.values())

    n_targets = len(per_target)
    generated = datetime.now(timezone.utc).strftime("%B %d, %Y, %H:%M UTC")
    baseline_name = baseline_dir.name
    theme_css = load_theme_css()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Praxen — OWASP Coverage Across Baseline Targets</title>
<style>{theme_css}
{OWASP_CSS}</style>
</head>
<body class="report-page">
<div class="wrap">

  <header class="hero">
    <h1>OWASP Coverage Across Praxen Baseline Targets</h1>
    <p class="subtitle">Aggregate finding counts by category, taken from the frozen <code>tests/baselines/{html.escape(baseline_name)}/</code> set.</p>
    <div class="topline">
      <div class="stat-block"><strong>{n_targets}</strong><span>targets analyzed</span></div>
      <div class="stat-block"><strong>{total}</strong><span>total findings</span></div>
      <div class="stat-block"><strong>{llm_total}</strong><span>LLM-classified</span></div>
      <div class="stat-block"><strong>{asi_total}</strong><span>Agentic-classified</span></div>
    </div>
  </header>

  <section>
    <h2>Targets analyzed <span class="scope">{n_targets} frozen Praxen baseline scans</span></h2>
    <p class="intro">Each card links to <strong>both</strong> the agent's source repository and the per-target Praxen baseline analysis report. Counts shown are the primary OWASP classifications drawn from each finding's <code>owasp_llm</code> / <code>owasp_agentic</code> scalar.</p>
    {target_cards(per_target, out_dir)}
  </section>

  <section>
    <h2>OWASP LLM Top 10 — finding count by category</h2>
    <p class="intro">Coverage of <a href="https://genai.owasp.org/llm-top-10/" target="_blank" rel="noopener">OWASP Top 10 for LLM Applications 2025</a> across all baseline targets. Empty cells show categories the suite does not currently exercise.</p>
    {bar_chart(llm_rows, max_llm, "var(--orange)")}
  </section>

  <section>
    <h2>OWASP Agentic Top 10 — finding count by category</h2>
    <p class="intro">Coverage of <a href="https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/" target="_blank" rel="noopener">OWASP Top 10 for Agentic AI Applications 2026</a> across all baseline targets.</p>
    {bar_chart(asi_rows, max_asi, "var(--accent-2)")}
  </section>

  <section>
    <h2>Methodology <span class="scope">how these numbers were computed</span></h2>
    <p class="intro">
      Every finding's canonical record carries a primary OWASP classification in two scalar fields, <code>owasp_llm</code> (one of <code>LLM01</code>–<code>LLM10</code> or null) and <code>owasp_agentic</code> (one of <code>ASI01</code>–<code>ASI10</code> or null).
      This report sums those scalars across the frozen baseline JSONs in <code>tests/baselines/{html.escape(baseline_name)}/</code> — one per target — yielding the primary-classification counts shown.
      A finding can carry both an LLM and an Agentic primary tag, so the two totals overlap; a finding without any OWASP primary classification (a RAISE-only or supply-chain-only finding) appears in neither chart but still in the per-target total.
      The frozen baselines are version-pinned outputs of the cold pre-release scans; see <code>tests/baselines/README.md</code>.
      For how Praxen classifies findings against the OWASP Top 10, see the <a href="{DOCS_BASE}/owasp.html">OWASP Gen&nbsp;AI Security guide</a>.
    </p>
  </section>

  <footer class="foot">
    Generated {generated} · Built on the Praxen <code>{html.escape(baseline_name)}</code> baseline set ·
    <a href="https://github.com/open-agent-ai-security/praxen" target="_blank" rel="noopener">github.com/open-agent-ai-security/praxen</a>
  </footer>

</div>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(
        description="Render a Praxen OWASP coverage HTML report from a baseline set.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example:\n  python3 tests/baselines/owasp_coverage.py --out /tmp/owasp.html\n",
    )
    parser.add_argument(
        "--baseline-dir",
        type=Path,
        default=DEFAULT_BASELINE,
        help=f"Baseline set to aggregate (default: tests/baselines/{DEFAULT_BASELINE.name}/).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output HTML path (default: ./owasp-coverage-report.html in the current working directory).",
    )
    args = parser.parse_args()

    if not args.baseline_dir.is_dir():
        print(f"owasp_coverage.py: baseline directory not found: {args.baseline_dir}", file=sys.stderr)
        sys.exit(1)

    report = build_report(args.baseline_dir, args.out)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(f"owasp_coverage.py: wrote {args.out}")


if __name__ == "__main__":
    main()
