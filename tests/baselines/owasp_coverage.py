#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Aggregate OWASP finding counts across a Praxen baseline set and render a
self-contained HTML coverage report.

Walks every `<target>/<target>-findings-*.json` under the chosen baseline
directory, sums the per-finding `owasp_llm` / `owasp_agentic` primary scalars,
and writes an HTML report with bar charts and target links.

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

THIS_DIR = Path(__file__).resolve().parent
DEFAULT_BASELINE = THIS_DIR / "v0.7.7-claude48"
DEFAULT_OUT = Path.cwd() / "owasp-coverage-report.html"

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

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Praxen — OWASP Coverage Across Baseline Targets</title>
<style>
  :root {{
    --navy:        #0D1B2A;
    --blue:        #006BFF;
    --blue-lt:     #27B2FF;
    --blue-dark:   #003FCC;
    --purple:      #8D00FF;
    --text:        #0D1B2A;
    --text-muted:  #3A4A6B;
    --bg:          #FFFFFF;
    --surface:     #F5F7FA;
    --surface-alt: #F0F4FF;
    --border:      #E1E4E8;
    --border-alt:  #C8D4F0;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--surface);
    color: var(--text);
    line-height: 1.5;
  }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 32px 24px 64px; }}
  header.hero {{
    background: var(--navy);
    color: white;
    padding: 36px 32px;
    border-radius: 8px;
    margin-bottom: 28px;
  }}
  header.hero h1 {{ margin: 0 0 6px; font-size: 28px; font-weight: 600; }}
  header.hero .subtitle {{ color: #B8C5DB; margin: 0 0 18px; }}
  .topline {{
    display: flex; gap: 28px; flex-wrap: wrap; padding-top: 16px;
    border-top: 1px solid #1F2D44;
  }}
  .topline .stat-block {{ color: white; }}
  .topline .stat-block strong {{
    display: block; font-size: 24px; font-weight: 700; color: var(--blue-lt);
  }}
  .topline .stat-block span {{ font-size: 13px; color: #B8C5DB; }}

  section {{ background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 24px; margin-bottom: 24px; }}
  section h2 {{
    margin: 0 0 4px; font-size: 18px; font-weight: 600; color: var(--navy);
    padding-bottom: 12px; border-bottom: 2px solid var(--border-alt);
  }}
  section h2 .scope {{ font-size: 13px; color: var(--text-muted); font-weight: 400; margin-left: 8px; }}
  section .intro {{ color: var(--text-muted); margin: 12px 0 20px; font-size: 14px; }}

  .target-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }}
  .target-card {{
    display: flex; flex-direction: column;
    border: 1px solid var(--border); border-radius: 6px; padding: 14px 16px;
    background: var(--surface-alt); transition: border-color 0.1s, box-shadow 0.1s;
  }}
  .target-card:hover {{ border-color: var(--blue); box-shadow: 0 2px 8px rgba(0,107,255,0.12); }}
  .target-name {{ font-size: 15px; font-weight: 600; color: var(--navy); margin-bottom: 4px; }}
  .target-blurb {{ font-size: 12.5px; color: var(--text-muted); margin-bottom: 10px; min-height: 32px; }}
  .target-stats {{ display: flex; gap: 14px; font-size: 12px; color: var(--text-muted); margin-bottom: 12px; }}
  .target-stats strong {{ color: var(--navy); font-weight: 700; }}
  .target-links {{
    display: flex; gap: 8px; margin-top: auto;
    padding-top: 10px; border-top: 1px solid var(--border-alt);
  }}
  .card-link {{
    flex: 1; text-align: center; padding: 6px 10px; border-radius: 4px;
    font-size: 12px; font-weight: 600; text-decoration: none; transition: all 0.1s;
    white-space: nowrap;
  }}
  .card-link-source {{
    color: var(--blue-dark); background: var(--bg); border: 1px solid var(--border-alt);
  }}
  .card-link-source:hover {{ background: var(--surface-alt); border-color: var(--blue); }}
  .card-link-report {{
    color: white; background: var(--blue); border: 1px solid var(--blue);
  }}
  .card-link-report:hover {{ background: var(--blue-dark); border-color: var(--blue-dark); }}
  .card-link-disabled {{
    color: var(--text-muted); background: var(--surface); border: 1px solid var(--border);
    cursor: not-allowed;
  }}

  .chart {{ margin-top: 8px; }}
  .bar-row {{ display: grid; grid-template-columns: 280px 1fr; gap: 14px; align-items: center; padding: 6px 0; }}
  .bar-label {{ font-size: 13px; color: var(--text); }}
  .bar-code {{
    display: inline-block; min-width: 44px; padding: 2px 6px; margin-right: 8px;
    border-radius: 3px; background: var(--navy); color: white;
    font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: 11px; font-weight: 600;
  }}
  .bar-track {{
    position: relative; height: 24px; background: var(--surface);
    border: 1px solid var(--border); border-radius: 4px; overflow: hidden;
  }}
  .bar-fill {{ height: 100%; border-radius: 3px 0 0 3px; transition: width 0.3s; }}
  .bar-count {{
    position: absolute; right: 8px; top: 50%; transform: translateY(-50%);
    font-size: 12px; font-weight: 600; color: var(--navy);
    background: rgba(255,255,255,0.85); padding: 0 6px; border-radius: 3px;
  }}
  .bar-row.is-empty .bar-label {{ color: var(--text-muted); }}
  .bar-row.is-empty .bar-count {{ color: var(--text-muted); }}

  footer.foot {{
    margin-top: 32px; padding: 18px 0 0; border-top: 1px solid var(--border);
    font-size: 12px; color: var(--text-muted); text-align: center;
  }}
  footer.foot a {{ color: var(--blue-dark); text-decoration: none; }}
  footer.foot a:hover {{ text-decoration: underline; }}

  @media (max-width: 720px) {{
    .bar-row {{ grid-template-columns: 1fr; }}
    .bar-label {{ margin-bottom: 4px; }}
    .topline {{ gap: 14px; }}
  }}
</style>
</head>
<body>
<div class="wrap">

  <header class="hero">
    <h1>OWASP Coverage Across Praxen Baseline Targets</h1>
    <p class="subtitle">Aggregate finding counts by category, taken from the frozen <code style="background:#1F2D44;padding:2px 6px;border-radius:3px;color:#B8C5DB;font-size:12px;">tests/baselines/{html.escape(baseline_name)}/</code> set.</p>
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
    <p class="intro">Coverage of <a href="https://genai.owasp.org/llm-top-10/" target="_blank" rel="noopener" style="color:var(--blue-dark);">OWASP Top 10 for LLM Applications 2025</a> across all baseline targets. Empty cells show categories the suite does not currently exercise.</p>
    {bar_chart(llm_rows, max_llm, "var(--blue)")}
  </section>

  <section>
    <h2>OWASP Agentic Top 10 — finding count by category</h2>
    <p class="intro">Coverage of <a href="https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/" target="_blank" rel="noopener" style="color:var(--blue-dark);">OWASP Top 10 for Agentic AI Applications 2026</a> across all baseline targets.</p>
    {bar_chart(asi_rows, max_asi, "var(--purple)")}
  </section>

  <section>
    <h2>Methodology <span class="scope">how these numbers were computed</span></h2>
    <p class="intro">
      Every finding's canonical record carries a primary OWASP classification in two scalar fields, <code>owasp_llm</code> (one of <code>LLM01</code>–<code>LLM10</code> or null) and <code>owasp_agentic</code> (one of <code>ASI01</code>–<code>ASI10</code> or null).
      This report sums those scalars across the frozen baseline JSONs in <code>tests/baselines/{html.escape(baseline_name)}/</code> — one per target — yielding the primary-classification counts shown.
      A finding can carry both an LLM and an Agentic primary tag, so the two totals overlap; a finding without any OWASP primary classification (a RAISE-only or supply-chain-only finding) appears in neither chart but still in the per-target total.
      The frozen baselines are version-pinned outputs of the cold pre-release scans; see <code>tests/baselines/README.md</code>.
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
