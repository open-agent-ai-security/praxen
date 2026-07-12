#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Praxen OWASP coverage report — primary + secondary classification per category.

Walks a baseline set and, for each finding, records its PRIMARY OWASP classification
(the dominant `owasp_llm` / `owasp_agentic` value) plus any co-applicable SECONDARY
codes noted alongside it. Renders an HTML page with a compressed bar per category —
a solid primary segment plus a hatched secondary extension — hover tooltips listing
the findings behind each, per-target cards linking source repos and per-target
analysis reports, and links to the companion RAISE and Suite Health views.

Reads either a baseline set (`<slug>/<slug>-findings-*.json`, with an optional
`<slug>/<slug>-analysis-*.html` alongside for the per-target report link) or a flat
directory of findings files (`<slug>.json`). `--compare-dir` optionally draws a
reference tick at each category's primary count in another set.

Usage:
    python3 tests/baselines/owasp_coverage.py [--baseline-dir DIR] [--compare-dir DIR] [--out FILE]

Defaults: reads the baseline named in `CURRENT` (else the newest `v*` dir); writes
`owasp-coverage-report.html` alongside this script.
"""
import argparse
import html
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from theme_utils import load_theme_css, DOCS_BASE, masthead

THIS_DIR = Path(__file__).resolve().parent
CODE_RE = re.compile(r"(LLM\d{2}|ASI\d{2})")
SEV_COLOR = {"Critical": "#e5484d", "High": "#f76b15", "Medium": "#d9a400",
             "Low": "#4c8dff", "Informational": "#8a94a4"}
esc = html.escape


def _baseline_sort_key(p: Path):
    """Version-aware sort key for `v*` baseline dirs (v0.7.10 sorts above v0.7.9)."""
    version = p.name[1:].split("-", 1)[0]
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
    ("openai-customer-service", "OpenAI Customer Service",      "https://github.com/openai/openai-agents-python",
     "OpenAI Agents SDK example"),
    ("autogen-code-executor",   "AutoGen Code Executor",        "https://github.com/microsoft/autogen",
     "Microsoft AutoGen code-executor family"),
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
    ("craftbot",                "CraftBot",                     "https://github.com/CraftOS-dev/CraftBot",
     "Self-hosted general-purpose agent that builds and operates its own SaaS tools"),
    ("uagents",                 "uAgents",                      "https://github.com/fetchai/uAgents",
     "Fetch.ai decorator-based autonomous multi-agent framework runtime"),
    ("salesforce-help-agent-accelerator", "Agentforce Help Agent", "https://github.com/salesforce/help-agent-accelerator",
     "Salesforce Agentforce customer-service agent (Knowledge-article RAG)"),
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

# Card / chrome components (shared with the report's target cards). The bar
# components are defined in OWASP_V2_CSS below; base elements, hero, sections and
# footer come from the shared theme (assets/praxen-theme.css), inlined ahead of these.
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
"""

OWASP_V2_CSS = """
  .v2-legend { display:flex; flex-wrap:wrap; gap:18px; align-items:center;
    margin:0 0 18px; padding:11px 16px; background:var(--panel); border:1px solid var(--border);
    border-radius:11px; font-size:12.5px; color:var(--muted); }
  .v2-legend .sw { display:inline-flex; align-items:center; gap:7px; }
  .v2-box { width:26px; height:12px; border-radius:3px; display:inline-block; }
  .v2-box.p { background:var(--accent-2); }
  .v2-box.s { background:color-mix(in srgb, var(--accent-2) 42%, transparent);
    background-image:repeating-linear-gradient(45deg, transparent 0 3px, rgba(0,0,0,.22) 3px 5px); }
  .v2-box.tick { width:3px; height:15px; background:var(--muted); }

  .v2-chart { margin-top:4px; }
  .v2-row { display:grid; grid-template-columns:250px 1fr; gap:14px; align-items:center; padding:5px 0; }
  .v2-label { font-size:13px; color:var(--text); }
  .v2-count { position:absolute; right:8px; top:50%; transform:translateY(-50%); font-size:12px; font-weight:700;
    color:var(--text); text-shadow:0 1px 2px rgba(0,0,0,0.55); pointer-events:none; z-index:3; font-variant-numeric:tabular-nums; }
  .v2-code { display:inline-block; min-width:46px; padding:2px 7px; margin-right:8px; border-radius:6px;
    background:var(--panel-2); color:var(--orange-2); border:1px solid var(--border);
    font-family:var(--mono); font-size:11px; font-weight:600; }
  .v2-flag { font-family:var(--mono); font-size:10px; padding:1px 6px; border-radius:20px; margin-left:6px; }
  .v2-flag.up { color:#1f9d6b; border:1px solid color-mix(in srgb,#1f9d6b 45%,transparent); }
  .v2-flag.sec { color:var(--muted-2); border:1px solid var(--border); }

  .v2-track { position:relative; height:22px; background:var(--panel); border:1px solid var(--border);
    border-radius:7px; }
  .v2-seg { position:absolute; top:0; height:100%; cursor:default; }
  .v2-seg.p { left:0; background:var(--seg-accent); border-radius:6px 0 0 6px; }
  .v2-seg.s { background:color-mix(in srgb, var(--seg-accent) 42%, transparent);
    background-image:repeating-linear-gradient(45deg, transparent 0 3px, rgba(0,0,0,.20) 3px 5px);
    border-radius:0 6px 6px 0; }
  .v2-seg.p.solo { border-radius:6px; }
  .v2-seg.s.solo { border-radius:6px; }
  .v2-fz { position:absolute; top:-3px; height:28px; width:3px; background:var(--muted);
    border-radius:1px; opacity:.9; z-index:2; pointer-events:none; }
  .v2-row.is-empty .v2-label { color:var(--muted-2); }
  .v2-row.is-empty .v2-count { color:var(--muted-2); text-shadow:none; }

  /* hover tooltip */
  .v2-tip { position:absolute; left:0; top:132%; z-index:9; min-width:230px; max-width:340px;
    background:color-mix(in srgb, var(--panel) 93%, transparent);
    backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px);
    border:1px solid var(--border-hi); border-radius:9px;
    padding:9px 11px; box-shadow:0 12px 30px -8px rgba(0,0,0,.6);
    opacity:0; visibility:hidden; transform:translateY(-3px); transition:opacity .12s, transform .12s; }
  .v2-seg:hover .v2-tip { opacity:1; visibility:visible; transform:translateY(0); }
  .v2-tip b { color:var(--text); font-size:12px; }
  .v2-tip ul { list-style:none; margin:7px 0 0; padding:0; }
  .v2-tip li { display:flex; gap:7px; align-items:flex-start; font-size:11.5px; color:var(--muted);
    padding:2px 0; line-height:1.35; }
  .v2-tip .dot { flex:0 0 auto; width:8px; height:8px; border-radius:50%; margin-top:4px; }
  .v2-tip .ag { color:var(--text); font-weight:600; white-space:nowrap; }
  .v2-tip li.more { color:var(--muted-2); font-style:italic; }

  @media (max-width:720px){ .v2-row{ grid-template-columns:1fr; } .v2-label{ margin-bottom:4px; } }
"""

OWASP_HEAT_CSS = """
  .heat-wrap { overflow:visible; margin-top:6px; }
  .heat-grid { display:grid; grid-template-columns:auto repeat(var(--n), minmax(30px,1fr)); gap:3px; }
  .heat-corner { font-size:10px; color:var(--muted-2); align-self:end; padding:0 8px 3px 0; white-space:nowrap; line-height:1.2; }
  .heat-colh { text-align:center; font-family:var(--mono); font-size:11px; color:var(--muted); padding-bottom:3px; }
  .heat-rowh { font-family:var(--mono); font-size:11px; color:var(--muted); display:flex; align-items:center;
    justify-content:flex-end; padding-right:8px; white-space:nowrap; }
  .heat-rowh .heat-code { color:var(--text); }
  .heat-cell { position:relative; aspect-ratio:1/1; min-height:32px; border-radius:5px; display:flex;
    align-items:center; justify-content:center; font-size:12.5px; font-weight:700;
    font-variant-numeric:tabular-nums; cursor:default; }
  .heat-cell.heat-empty { background:var(--panel); box-shadow:inset 0 0 0 1px var(--border); }
  .heat-cell:not(.heat-empty) { box-shadow:0 1px 2px rgba(0,0,0,.30); }
  .heat-cell:not(.heat-empty):hover { outline:2px solid var(--text); outline-offset:1px; z-index:8; }
  .heat-n { pointer-events:none; }
  .heat-cell:hover .v2-tip { opacity:1; visibility:visible; transform:translateY(0); }

  .heat-legend { display:flex; align-items:center; gap:14px; flex-wrap:wrap; margin-top:16px;
    font-size:12.5px; color:var(--muted); }
  .heat-legend .lg { display:inline-flex; align-items:center; gap:7px; }
  .heat-empty-sw { width:15px; height:15px; border-radius:4px; background:var(--panel);
    box-shadow:inset 0 0 0 1px var(--border); }
  .heat-bar { width:170px; height:13px; border-radius:7px; }
  .heat-ends { display:inline-flex; gap:9px; align-items:center; font-variant-numeric:tabular-nums; }
  .heat-ends .mut { color:var(--muted-2); }

  @media (max-width:640px){ .heat-wrap { overflow-x:auto; } .heat-grid { min-width:520px; } }
"""


def _load_findings(base: Path, slug: str):
    """Return (findings, agent_name) for a slug, from a nested baseline file
    (`<slug>/<slug>-findings-*.json`) or a flat `<slug>.json`. ([], slug) if none."""
    nested = sorted((base / slug).glob(f"{slug}-findings-*.json"))
    if nested:
        data = json.loads(nested[-1].read_text(encoding="utf-8"))
        return data.get("findings") or [], (data.get("scan", {}) or {}).get("agent") or slug
    flat = base / f"{slug}.json"
    if flat.is_file():
        data = json.loads(flat.read_text(encoding="utf-8"))
        return data.get("findings") or [], (data.get("scan", {}) or {}).get("agent") or slug
    return [], slug


def _prim_codes(f):
    return [str(f[k])[:5] for k in ("owasp_llm", "owasp_agentic") if f.get(k)]


def _sec_codes(f, prim):
    out = []
    for t in (f.get("tags") or []):
        s = t.get("label", "") if isinstance(t, dict) else str(t)
        m = CODE_RE.search(s)
        if m and m.group(1) not in prim and m.group(1) not in out:
            out.append(m.group(1))
    return out


def gather(base: Path):
    """cat[code] -> {prim, sec, pf:[(sev,agent,summary)], sf:[...]}; plus per_target, total."""
    cat = {c: {"prim": 0, "sec": 0, "pf": [], "sf": []} for c, _ in (LLM_TITLES + ASI_TITLES)}
    per_target, total = {}, 0
    for slug, name, _, _ in TARGETS:
        findings, agent = _load_findings(base, slug)
        if not findings:
            continue
        t_llm, t_asi = Counter(), Counter()
        for f in findings:
            sev = f.get("severity", "Informational")
            summ = (f.get("summary") or "").strip()
            prim = _prim_codes(f)
            for c in prim:
                if c not in cat:
                    continue
                cat[c]["prim"] += 1
                cat[c]["pf"].append((sev, agent, summ))
                (t_llm if c.startswith("LLM") else t_asi)[c] += 1
            for c in _sec_codes(f, prim):
                if c in cat:
                    cat[c]["sec"] += 1
                    cat[c]["sf"].append((sev, agent, summ))
        report = sorted((base / slug).glob(f"{slug}-analysis-*.html"))
        per_target[slug] = {"count": len(findings), "llm": t_llm, "asi": t_asi,
                            "report": report[-1].resolve() if report else None}
        total += len(findings)
    return cat, per_target, total


def compare_primary(base: Path):
    c = Counter()
    if not base:
        return c
    for slug, _, _, _ in TARGETS:
        findings, _ = _load_findings(base, slug)
        for f in findings:
            for code in _prim_codes(f):
                c[code] += 1
    return c


def _tip(label, n, findings):
    items = []
    for sev, agent, summ in findings[:7]:
        dot = SEV_COLOR.get(sev, "#8a94a4")
        items.append(f'<li><span class="dot" style="background:{dot}"></span>'
                     f'<span><span class="ag">{esc(agent)}</span> — {esc(summ[:82])}</span></li>')
    if len(findings) > 7:
        items.append(f'<li class="more">+{len(findings) - 7} more</li>')
    return (f'<span class="v2-tip"><b>{label} — {n} finding{"s" if n != 1 else ""}</b>'
            f'<ul>{"".join(items)}</ul></span>')


def v2_chart(rows, cat, max_cov, accent_var, froz):
    out = ['<div class="v2-chart">']
    for code, title in rows:
        d = cat[code]
        prim, sec = d["prim"], d["sec"]
        cover = prim + sec
        empty = " is-empty" if cover == 0 else ""
        pw = prim / max_cov * 100 if max_cov else 0
        sw = sec / max_cov * 100 if max_cov else 0
        fz = froz.get(code, 0)
        flag = ""
        if prim == 0 and sec > 0:
            flag = '<span class="v2-flag sec">secondary only</span>'
        segp = (f'<span class="v2-seg p{" solo" if sec == 0 else ""}" style="width:{pw:.1f}%">'
                f'{_tip("Primary", prim, d["pf"])}</span>') if prim > 0 else ""
        segs = (f'<span class="v2-seg s{" solo" if prim == 0 else ""}" '
                f'style="left:{pw:.1f}%;width:{sw:.1f}%">{_tip("Secondary", sec, d["sf"])}</span>') if sec > 0 else ""
        tick = f'<span class="v2-fz" style="left:{min(fz / max_cov * 100, 99.5):.1f}%"></span>' if (fz and max_cov) else ""
        out.append(f'''
        <div class="v2-row{empty}">
          <div class="v2-label"><span class="v2-code">{esc(code)}</span>{esc(title)}{flag}</div>
          <div class="v2-track" style="--seg-accent:{accent_var};">{segp}{segs}{tick}<span class="v2-count">{cover}</span></div>
        </div>''')
    out.append('</div>')
    return "\n".join(out)


def target_cards(per_target, out_dir: Path):
    out = ['<div class="target-grid">']
    for slug, name, url, blurb in TARGETS:
        info = per_target.get(slug, {"count": 0, "llm": Counter(), "asi": Counter(), "report": None})
        if info.get("report"):
            try:
                rel = Path(os.path.relpath(info["report"], out_dir)).as_posix()
            except ValueError:                       # Windows cross-drive relpath
                rel = Path(info["report"]).as_uri()
            report_link = (f'<a class="card-link card-link-report" href="{esc(rel)}" '
                           f'target="_blank" rel="noopener">Analysis report ↗</a>')
        else:
            report_link = '<span class="card-link card-link-disabled">No analysis report</span>'
        out.append(f'''
        <div class="target-card">
          <div class="target-name">{esc(name)}</div>
          <div class="target-blurb">{esc(blurb)}</div>
          <div class="target-stats">
            <span class="stat"><strong>{info["count"]}</strong> findings</span>
            <span class="stat"><strong>{sum(info["llm"].values())}</strong> LLM</span>
            <span class="stat"><strong>{sum(info["asi"].values())}</strong> Agentic</span>
          </div>
          <div class="target-links">
            <a class="card-link card-link-source" href="{esc(url)}" target="_blank" rel="noopener">Source repo ↗</a>
            {report_link}
          </div>
        </div>''')
    out.append('</div>')
    return "\n".join(out)


# cool -> hot sequential ramp (dark/cool for low counts, bright/warm for high).
HEAT_STOPS = [(0.00, (30, 43, 94)),     # deep navy — coolest
              (0.30, (63, 63, 160)),    # indigo
              (0.55, (139, 63, 160)),   # purple
              (0.78, (210, 75, 102)),   # rose
              (1.00, (246, 161, 60))]   # hot orange — hottest


def _heat(t):
    """Map t in [0,1] to (bg_hex, text_hex) along the cool->hot ramp."""
    t = max(0.0, min(1.0, t))
    rgb = HEAT_STOPS[-1][1]
    for (t0, c0), (t1, c1) in zip(HEAT_STOPS, HEAT_STOPS[1:]):
        if t <= t1:
            f = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            rgb = tuple(round(a + (b - a) * f) for a, b in zip(c0, c1))
            break
    lum = (0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]) / 255
    return "#%02x%02x%02x" % rgb, ("#17162b" if lum > 0.6 else "#ffffff")


def cooccurrence(base: Path):
    """mat[llm][asi] -> [(sev,agent,summary), ...] for findings carrying both
    that LLM and that Agentic code (primary OR secondary); plus max cell, n_both."""
    llm = [c for c, _ in LLM_TITLES]
    asi = [c for c, _ in ASI_TITLES]
    mat = {l: {a: [] for a in asi} for l in llm}
    n_both = 0
    for slug, name, _, _ in TARGETS:
        findings, agent = _load_findings(base, slug)
        for f in findings:
            prim = _prim_codes(f)
            codes = set(prim) | set(_sec_codes(f, prim))
            ls = [c for c in codes if c in mat]
            as_ = [c for c in codes if c in asi]
            if ls and as_:
                n_both += 1
            sev = f.get("severity", "Informational")
            summ = (f.get("summary") or "").strip()
            for l in ls:
                for a in as_:
                    mat[l][a].append((sev, agent, summ))
    maxv = max((len(mat[l][a]) for l in llm for a in asi), default=0)
    return mat, maxv, n_both


def heatmap_html(base: Path):
    mat, maxv, n_both = cooccurrence(base)
    used = sum(1 for l, _ in LLM_TITLES for a, _ in ASI_TITLES if mat[l][a])
    out = [f'<div class="heat-wrap"><div class="heat-grid" style="--n:{len(ASI_TITLES)}">']
    out.append('<div class="heat-corner">LLM&nbsp;↓<br>ASI&nbsp;→</div>')
    for a, title in ASI_TITLES:
        out.append(f'<div class="heat-colh" title="{esc(a)} — {esc(title)}">{esc(a[3:])}</div>')
    for l, ltitle in LLM_TITLES:
        out.append(f'<div class="heat-rowh" title="{esc(l)} — {esc(ltitle)}">'
                   f'<span class="heat-code">{esc(l)}</span></div>')
        for a, atitle in ASI_TITLES:
            fl = mat[l][a]
            n = len(fl)
            if not n:
                out.append('<div class="heat-cell heat-empty"></div>')
                continue
            t = (n - 1) / (maxv - 1) if maxv > 1 else 1.0
            bg, txt = _heat(t)
            tip = _tip(f"{l} × {a}", n, fl)
            out.append(f'<div class="heat-cell" style="background:{bg};color:{txt}">'
                       f'<span class="heat-n">{n}</span>{tip}</div>')
    out.append('</div></div>')
    grad = ", ".join(_heat(i / 8)[0] for i in range(9))
    out.append(f'''
    <div class="heat-legend">
      <span class="lg"><span class="heat-empty-sw"></span> no co-occurrence</span>
      <span class="lg"><span class="heat-bar" style="background:linear-gradient(90deg,{grad})"></span></span>
      <span class="lg heat-ends"><span>1</span><span class="mut">cooler → hotter</span><span>{maxv}</span></span>
      <span class="lg" style="margin-left:auto; color:var(--muted-2)">hover a cell for the findings behind it</span>
    </div>''')
    return "\n".join(out), n_both, used, maxv


def build_report(base: Path, compare: Path, out_path: Path) -> str:
    cat, per_target, total = gather(base)
    out_dir = out_path.resolve().parent
    froz = compare_primary(compare)
    max_llm = max((cat[c]["prim"] + cat[c]["sec"] for c, _ in LLM_TITLES), default=1) or 1
    max_asi = max((cat[c]["prim"] + cat[c]["sec"] for c, _ in ASI_TITLES), default=1) or 1

    llm_prim = sum(cat[c]["prim"] for c, _ in LLM_TITLES)
    asi_prim = sum(cat[c]["prim"] for c, _ in ASI_TITLES)
    n_targets = len(per_target)
    generated = datetime.now(timezone.utc).strftime("%B %d, %Y, %H:%M UTC")
    theme_css = load_theme_css()
    heat_grid, heat_both, heat_used, heat_max = heatmap_html(base)

    legend = '''
    <div class="v2-legend">
      <span class="sw"><span class="v2-box p"></span> primary — the finding's main category</span>
      <span class="sw"><span class="v2-box s"></span> secondary — a category it also touches</span>
      <span style="margin-left:auto; color:var(--muted-2)">hover any bar to see the findings behind it</span>
    </div>'''

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Praxen — OWASP Coverage Across Baseline Targets</title>
<style>{theme_css}
{OWASP_CSS}
{OWASP_V2_CSS}
{OWASP_HEAT_CSS}</style>
</head>
<body class="report-page">
<div class="wrap">

  {masthead()}

  <header class="hero">
    <h1>OWASP Coverage Across Praxen Baseline Targets</h1>
    <p class="subtitle">How each OWASP category actually shows up across {n_targets} real-world AI agents — as a finding's <strong>primary</strong> risk (solid) or a <strong>secondary</strong>, co-occurring concern (hatched).</p>
    <div class="topline">
      <div class="stat-block"><strong>{n_targets}</strong><span>targets analyzed</span></div>
      <div class="stat-block"><strong>{total}</strong><span>total findings</span></div>
      <div class="stat-block"><strong>{llm_prim}</strong><span>LLM-classified</span></div>
      <div class="stat-block"><strong>{asi_prim}</strong><span>Agentic-classified</span></div>
    </div>
    <p class="intro" style="margin-top:16px">Companion views · <a href="raise-coverage-report.html">RAISE coverage</a> · <a href="suite-health-report.html">Suite Health — popularity &amp; freshness</a></p>
  </header>

  <section>
    <h2>Targets analyzed <span class="scope">{n_targets} Praxen scans</span></h2>
    <p class="intro">Each card links to the agent's source repository and its per-target Praxen analysis report. Counts show how many of that agent's findings fall primarily under an LLM or Agentic OWASP category.</p>
    {target_cards(per_target, out_dir)}
  </section>

  <section>
    <h2>OWASP LLM Top 10 — coverage by category</h2>
    <p class="intro">How the <a href="https://genai.owasp.org/llm-top-10/" target="_blank" rel="noopener">OWASP Top 10 for LLM Applications 2025</a> categories apply across these agents. Solid = the finding's primary category; hatched = a category it also touches. Empty rows are categories these apps don't exercise.</p>
    {legend}
    {v2_chart(LLM_TITLES, cat, max_llm, "var(--orange)", froz)}
  </section>

  <section>
    <h2>OWASP Agentic Top 10 — coverage by category</h2>
    <p class="intro">How the <a href="https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/" target="_blank" rel="noopener">OWASP Top 10 for Agentic AI Applications 2026</a> categories apply. Outcome categories — Cascading Failures, Rogue Agents — appear hatched-only: they're real concerns, but a more specific category is usually the primary one.</p>
    {v2_chart(ASI_TITLES, cat, max_asi, "var(--accent-2)", froz)}
  </section>

  <section>
    <h2>Where LLM and Agentic risks meet <span class="scope">co-occurrence heat map</span></h2>
    <p class="intro">Every square counts the findings tagged with <em>both</em> that LLM category (row) and that Agentic category (column) — primary or secondary. It shows how a model-layer weakness and an agent-layer weakness combine in the same finding: <strong>{heat_both}</strong> of {total} findings span both layers, lighting <strong>{heat_used}</strong> of 100 pairings. Blank squares are pairings that never co-occur; hotter squares occur more often (peak {heat_max}).</p>
    {heat_grid}
  </section>

  <section>
    <h2>How to read this <span class="scope">primary vs secondary</span></h2>
    <p class="intro">
      Every finding is classified against the OWASP Top 10 by its <strong>primary</strong> risk — the single category that best captures what an attacker could actually do — and may note <strong>secondary</strong> categories it also touches. The solid bar counts the primary classification; the hatched extension shows the secondary, co-occurring concerns, kept separate so a headline number reflects only where a category is genuinely the dominant risk, not merely implicated.
      Some real findings have <em>no</em> OWASP home at all — a missing audit trail, for instance, is something the Top 10 treats as a defensive gap to close rather than a vulnerability to classify. Those are left unclassified and appear in neither chart. Where the taxonomy reaches, and where it doesn't, is itself part of what this view measures.
      For how these categories are applied, see the <a href="{DOCS_BASE}/owasp.html">OWASP Gen&nbsp;AI Security guide</a>.
    </p>
  </section>

  <footer class="foot">
    Generated {generated} · Praxen — agent behavior verifier ·
    <a href="https://github.com/open-agent-ai-security/praxen" target="_blank" rel="noopener">github.com/open-agent-ai-security/praxen</a>
  </footer>

</div>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(
        description="Render the Praxen OWASP coverage report (primary + secondary classification).")
    ap.add_argument("--baseline-dir", type=Path, default=DEFAULT_BASELINE,
                    help=f"Baseline set to aggregate (default: {DEFAULT_BASELINE.name}/).")
    ap.add_argument("--compare-dir", type=Path, default=None,
                    help="Optional set to draw a primary-count reference tick from.")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT,
                    help="Output HTML path (default: owasp-coverage-report.html alongside this script).")
    args = ap.parse_args()
    if not args.baseline_dir.is_dir():
        print(f"owasp_coverage.py: baseline directory not found: {args.baseline_dir}", file=sys.stderr)
        sys.exit(1)
    report = build_report(args.baseline_dir, args.compare_dir, args.out)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(f"owasp_coverage.py: wrote {args.out}")


if __name__ == "__main__":
    main()
