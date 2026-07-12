#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Suite Health — popularity (GitHub stars) & development freshness of the Praxen baseline roster.

Companion to owasp_coverage.py / raise_coverage.py. Stdlib only; emits a self-contained
suite-health-report.html.

Two data sources:
  * **Popularity + freshness** — a manual snapshot (GitHub stars, commit cadence, and a
    0–5 freshness score) taken on SNAPSHOT_DATE. `gh api` is network + not stdlib, so the
    snapshot is embedded here and re-taken by hand at re-baseline time (see ROSTER_HEALTH.md).
  * **Maturity** — read live from the frozen baseline JSONs (`raise_posture.weighted_overall`),
    so the RAISE axis always matches the committed set.

Usage:
    python3 tests/baselines/suite_health.py [--baseline-dir DIR] [--out FILE]
"""
import argparse
import datetime
import html
import json
import math
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
from theme_utils import load_theme_css, masthead  # noqa: E402

DEFAULT_BASELINE = THIS_DIR / "v1.0.2-claude48"
DEFAULT_OUT = THIS_DIR / "suite-health-report.html"
SNAPSHOT_DATE = "2026-07-11"

# slug -> (display, repo (owner/name), stars, freshness 0-5, (c4wk, c12wk, c52wk), note)
# Snapshot per ROSTER_HEALTH.md. † = repo-level metric covers more than the scanned scope.
ROSTER = {
    "hermes-agent-desktop":            ("Hermes (Agent + Desktop)", "NousResearch/hermes-agent",         213129, 5.0, (3301, 10175, 15140), "Top-tier, intensely active"),
    "openhands":                       ("OpenHands",                "All-Hands-AI/OpenHands",             80454,  5.0, (171, 533, 2316),     "Live, heavy cadence"),
    "autogen-code-executor":           ("AutoGen Code Executor",    "microsoft/autogen",                 59656,  2.0, (0, 0, 77),           "Big but quiet ~3mo; successor framework"),
    "aider":                           ("Aider",                    "Aider-AI/aider",                    47288,  3.0, (0, 17, 196),         "Maintained, decelerating"),
    "openai-customer-service":         ("OpenAI Customer Service",  "openai/openai-agents-python",       27814,  5.0, (105, 363, 1227),     "SDK, live"),
    "deepagents-cli":                  ("Deep Agents CLI",          "langchain-ai/deepagents",           26095,  5.0, (478, 1170, 2681),    "Live, heavy cadence"),
    "uagents":                         ("uAgents",                  "fetchai/uAgents",                   1639,   3.5, (1, 23, 114),         "Recent touch, light cadence"),
    "craftbot":                        ("CraftBot",                 "CraftOS-dev/CraftBot",              373,    5.0, (107, 409, 1149),     "Small but very active"),
    "finbot":                          ("FinBot",                   "OWASP-ASI/finbot-ctf-demo",         65,     1.5, (0, 0, 73),           "CTF demo, static by design"),
    "helperbot":                       ("HelperBot",                "opena2a-org/damn-vulnerable-ai-agent", 57,  4.0, (13, 41, 132),        "Small, actively developed"),
    "yaah":                            ("yaah",                     "dirien/yet-another-agent-harness",  19,     2.0, (0, 3, 39),           "Personal harness, sporadic"),
    "salesforce-help-agent-accelerator": ("Agentforce Help Agent",  "salesforce/help-agent-accelerator", 14,     2.0, (0, 7, 14),           "Vendor sample, low by design"),
}


# Obvious corporate / institutional sponsor per target ("—" = genuinely independent).
SPONSOR = {
    "hermes-agent-desktop": "Nous Research", "openhands": "All Hands AI",
    "autogen-code-executor": "Microsoft", "aider": "Aider AI",
    "openai-customer-service": "OpenAI", "deepagents-cli": "LangChain",
    "uagents": "Fetch.ai", "craftbot": "CraftOS", "finbot": "OWASP",
    "helperbot": "OpenA2A", "yaah": "—", "salesforce-help-agent-accelerator": "Salesforce",
}
# Short label for the scatter (long slugs overflow the plot).
SHORT = {
    "hermes-agent-desktop": "hermes", "openhands": "openhands",
    "autogen-code-executor": "autogen", "aider": "aider",
    "openai-customer-service": "openai-cs", "deepagents-cli": "deepagents",
    "uagents": "uagents", "craftbot": "craftbot", "finbot": "finbot",
    "helperbot": "helperbot", "yaah": "yaah", "salesforce-help-agent-accelerator": "agentforce",
}


def maturity_label(w):
    return "Absent" if w < 1 else "Ad hoc" if w < 2 else "Partial" if w < 3 else "Established"


def read_maturity(baseline_dir: Path, slug: str):
    js = sorted((baseline_dir / slug).glob(f"{slug}-findings-*.json"))
    if not js:
        return None, None
    d = json.loads(js[-1].read_text(encoding="utf-8"))
    w = d.get("raise_posture", {}).get("weighted_overall")
    return (float(w), maturity_label(float(w))) if w is not None else (None, None)


def star_str(n):
    return f"{n/1000:.0f}k" if n >= 1000 else str(n)


def fresh_pill(f):
    cls = "fresh-hi" if f >= 4 else "fresh-mid" if f >= 2.5 else "fresh-lo"
    return f'<span class="pill {cls}">{f:.1f}</span>'


def mat_pill(label):
    cls = {"Absent": "mat-absent", "Ad hoc": "mat-adhoc", "Partial": "mat-partial", "Established": "mat-est"}.get(label, "")
    return f'<span class="pill {cls}">{html.escape(label)}</span>'


def rows_table(rows, out_dir: Path):
    body = []
    for slug, disp, repo, stars, fresh, cad, note, w, mat in rows:
        c4, c12, c52 = cad
        reports = sorted((DEFAULT_BASELINE / slug).glob(f"{slug}-analysis-*.html"))
        rep = ""
        if reports:
            try:
                rel = reports[-1].resolve().relative_to(out_dir.resolve())
                rep = f' · <a href="{html.escape(str(rel))}">report ↗</a>'
            except ValueError:
                pass
        body.append(f"""      <tr>
        <td class="t-name">{html.escape(disp)}<div class="t-repo"><a href="https://github.com/{html.escape(repo)}" target="_blank" rel="noopener">{html.escape(repo)}</a>{rep}</div></td>
        <td class="sponsor">{html.escape(SPONSOR.get(slug, "—"))}</td>
        <td class="num">{star_str(stars)}</td>
        <td>{fresh_pill(fresh)}</td>
        <td class="num cadence">{c4} / {c12} / {c52}</td>
        <td class="num">{w:.2f}</td>
        <td>{mat_pill(mat)}</td>
        <td class="note">{html.escape(note)}</td>
      </tr>""")
    return "\n".join(body)


def _y_pct(w):
    return 9.0 + min(w, 3.0) / 3.0 * 82.0  # inset 9%..91% so top/bottom dots aren't clipped


def _dot(slug, disp, stars, fresh, w, mat, x, radius):
    return (
        f'<div class="pt" style="left:{x:.1f}%; bottom:{_y_pct(w):.1f}%" '
        f'title="{html.escape(disp)} — ★{stars:,}, freshness {fresh:.1f}, RAISE {w:.2f} ({html.escape(mat)})">'
        f'<span class="dot" style="width:{2*radius:.0f}px;height:{2*radius:.0f}px"></span>'
        f'<span class="lbl">{html.escape(SHORT.get(slug, slug))}</span></div>'
    )


def dots_activity(rows):
    # x = development freshness (0-5), inset 7%..93%; dot size ∝ stars
    out = []
    for slug, disp, repo, stars, fresh, cad, note, w, mat in rows:
        x = 7.0 + min(fresh, 5.0) / 5.0 * 86.0
        r = 5.0 + min(stars, 220000) ** 0.5 / 100.0
        out.append(_dot(slug, disp, stars, fresh, w, mat, x, r))
    return "\n".join(out)


def dots_popularity(rows):
    # x = GitHub stars on a log10 scale (domain 10 .. ~316k), inset 7%..93%; dot size ∝ freshness
    out = []
    for slug, disp, repo, stars, fresh, cad, note, w, mat in rows:
        lx = (math.log10(max(stars, 10)) - 1.0) / 4.5
        x = 7.0 + max(0.0, min(1.0, lx)) * 86.0
        r = 5.0 + fresh * 1.9
        out.append(_dot(slug, disp, stars, fresh, w, mat, x, r))
    return "\n".join(out)


SUITE_CSS = """
  table.health { width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 13px; }
  table.health th, table.health td { text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }
  table.health thead th { font-family: var(--mono); font-size: 11px; text-transform: uppercase; letter-spacing: .05em; color: var(--muted); font-weight: 700; }
  table.health td.num { text-align: right; font-variant-numeric: tabular-nums; color: var(--text); font-weight: 600; }
  table.health td.cadence { color: var(--muted); font-weight: 500; font-family: var(--mono); font-size: 11.5px; }
  table.health tr:hover td { background: var(--panel-2); }
  .t-name { font-weight: 600; color: var(--text); }
  .t-repo { font-size: 11px; color: var(--muted); margin-top: 3px; }
  .t-repo a { color: var(--muted); text-decoration: none; }
  .t-repo a:hover { color: var(--orange-2); }
  table.health td.sponsor { color: var(--muted); font-size: 12.5px; white-space: nowrap; }
  .note { color: var(--muted); font-size: 12px; max-width: 220px; }

  .pill { display: inline-block; min-width: 30px; text-align: center; padding: 2px 9px; border-radius: 20px; font-size: 12px; font-weight: 700; font-variant-numeric: tabular-nums; border: 1px solid var(--border); }
  .fresh-hi { background: rgba(64,196,127,0.16); color: #46c47f; border-color: rgba(64,196,127,0.4); }
  .fresh-mid { background: rgba(255,176,64,0.14); color: var(--orange-2); border-color: rgba(255,176,64,0.4); }
  .fresh-lo { background: rgba(150,150,160,0.14); color: var(--muted); }
  .mat-absent { color: #e2686b; border-color: rgba(226,104,107,0.4); background: rgba(226,104,107,0.12); }
  .mat-adhoc { color: var(--orange-2); border-color: rgba(255,176,64,0.4); background: rgba(255,176,64,0.12); }
  .mat-partial { color: #46c47f; border-color: rgba(64,196,127,0.4); background: rgba(64,196,127,0.12); }
  .mat-est { color: #4aa3ff; border-color: rgba(74,163,255,0.4); background: rgba(74,163,255,0.12); }

  .plot-wrap { display: grid; grid-template-columns: 34px 1fr; grid-template-rows: 1fr 26px; gap: 6px; margin-top: 14px; }
  .y-axis { grid-row: 1; grid-column: 1; writing-mode: vertical-rl; transform: rotate(180deg); text-align: center; font-family: var(--mono); font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; }
  .x-axis { grid-row: 2; grid-column: 2; text-align: center; font-family: var(--mono); font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; }
  .plot { grid-row: 1; grid-column: 2; position: relative; height: 460px; border: 1px solid var(--border); border-radius: 12px; background: var(--panel); overflow: hidden; }
  .qline { position: absolute; background: var(--border); }
  .qline.v { width: 1px; top: 0; bottom: 0; }                   /* left set inline per plot */
  .qline.h { height: 1px; left: 0; right: 0; bottom: 63.7%; }   /* RAISE weighted = 2.0 */
  .qlabel { position: absolute; font-family: var(--mono); font-size: 10px; color: var(--muted-2); padding: 4px 6px; text-transform: uppercase; letter-spacing: .04em; }
  .pt { position: absolute; transform: translate(-50%, 50%); display: flex; flex-direction: column; align-items: center; }
  .pt .dot { border-radius: 50%; background: linear-gradient(135deg, var(--orange-2), var(--orange-deep)); border: 1px solid rgba(0,0,0,0.35); box-shadow: 0 2px 6px -1px rgba(0,0,0,0.5); }
  .pt .lbl { margin-top: 2px; font-size: 10px; color: var(--text); white-space: nowrap; text-shadow: 0 1px 2px var(--panel); }
  .companion { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; }
  .companion a { padding: 7px 13px; border-radius: 9px; font-size: 12.5px; font-weight: 600; text-decoration: none; border: 1px solid var(--border); background: var(--panel); color: var(--text); }
  .companion a:hover { border-color: var(--border-hi); background: var(--panel-2); color: var(--orange-2); }
  @media (max-width: 720px) { .note { max-width: none; } table.health td.cadence { display: none; } }
"""


def build_html(baseline_dir: Path, out_dir: Path):
    rows = []
    for slug, (disp, repo, stars, fresh, cad, note) in ROSTER.items():
        w, mat = read_maturity(baseline_dir, slug)
        if w is None:
            continue
        rows.append((slug, disp, repo, stars, fresh, cad, note, w, mat))
    rows.sort(key=lambda r: (-r[3]))  # by stars desc
    n = len(rows)
    total_stars = sum(r[3] for r in rows)
    live = sum(1 for r in rows if r[4] >= 3.0)
    theme_css = load_theme_css()
    generated = datetime.date.today().isoformat()
    baseline_name = baseline_dir.name
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Praxen — Baseline Agent Suite Health (Popularity &amp; Freshness)</title>
<style>{theme_css}
{SUITE_CSS}</style>
</head><body class="report-page">
<div class="wrap">
  {masthead()}
  <header class="hero">
    <h1>Baseline Agent Suite Health — Popularity &amp; Freshness</h1>
    <p class="subtitle">GitHub prominence and development activity of the {n} targets in the frozen <code>tests/baselines/{html.escape(baseline_name)}/</code> set — the "is this a live, mainstream agent?" companion to the OWASP and RAISE coverage.</p>
    <div class="topline">
      <div class="stat-block"><strong>{n}</strong><span>targets</span></div>
      <div class="stat-block"><strong>{star_str(total_stars)}</strong><span>combined stars</span></div>
      <div class="stat-block"><strong>{live}</strong><span>live (freshness ≥ 3)</span></div>
      <div class="stat-block"><strong>{SNAPSHOT_DATE}</strong><span>snapshot</span></div>
    </div>
    <div class="companion">
      <a href="owasp-coverage-report.html">← OWASP coverage</a>
      <a href="raise-coverage-report.html">← RAISE coverage</a>
    </div>
  </header>

  <section>
    <h2>Popularity &amp; freshness <span class="scope">by stars</span></h2>
    <p class="intro">Stars and commit cadence are a <strong>{SNAPSHOT_DATE}</strong> snapshot; the RAISE maturity is read live from the frozen baseline. Cadence = merged commits into the default branch over the trailing 4 / 12 / 52 weeks. Metrics are <strong>repo-level</strong> — for monorepo targets they cover more than the scanned component.</p>
    <div style="overflow-x:auto">
    <table class="health">
      <thead><tr><th>Target</th><th>Sponsor</th><th class="num">★ Stars</th><th>Fresh 0–5</th><th class="cadence">Commits 4/12/52wk</th><th class="num">RAISE</th><th>Maturity</th><th>Activity</th></tr></thead>
      <tbody>
{rows_table(rows, out_dir)}
      </tbody>
    </table>
    </div>
  </section>

  <section>
    <h2>Activity × maturity <span class="scope">freshness vs. RAISE posture</span></h2>
    <p class="intro">Each dot is a target (size ∝ stars). <strong>x = development freshness (0–5)</strong>, <strong>y = RAISE maturity (0–3)</strong>. Dividers: live/dormant at freshness 3, Partial+/weaker at RAISE 2. The high-value cell for a security suite is <em>bottom-right</em> — live but under-enforced.</p>
    <div class="plot-wrap">
      <div class="y-axis">RAISE maturity →</div>
      <div class="plot">
        <div class="qline v" style="left:58.6%"></div><div class="qline h"></div>
        <div class="qlabel" style="left:0; top:0">live · weaker</div>
        <div class="qlabel" style="right:0; top:0; text-align:right">live · stronger</div>
        <div class="qlabel" style="left:0; bottom:0">dormant · weaker</div>
        <div class="qlabel" style="right:0; bottom:0; text-align:right">dormant · stronger</div>
{dots_activity(rows)}
      </div>
      <div class="x-axis">development freshness →</div>
    </div>
  </section>

  <section>
    <h2>Popularity × maturity <span class="scope">stars (log) vs. RAISE posture</span></h2>
    <p class="intro">Each dot is a target (size ∝ freshness). <strong>x = GitHub stars, log scale</strong> (10 → ~300k), <strong>y = RAISE maturity (0–3)</strong>. Divider at 10k stars. As before, <em>bottom-right</em> — popular but weak — is the highest real-world blast radius.</p>
    <div class="plot-wrap">
      <div class="y-axis">RAISE maturity →</div>
      <div class="plot">
        <div class="qline v" style="left:64.3%"></div><div class="qline h"></div>
        <div class="qlabel" style="left:0; top:0">niche · stronger</div>
        <div class="qlabel" style="right:0; top:0; text-align:right">mainstream · stronger</div>
        <div class="qlabel" style="left:0; bottom:0">niche · weaker</div>
        <div class="qlabel" style="right:0; bottom:0; text-align:right">mainstream · weaker</div>
{dots_popularity(rows)}
      </div>
      <div class="x-axis">GitHub stars (log) →</div>
    </div>
  </section>

  <section>
    <h2>Methodology <span class="scope">how these are scored</span></h2>
    <p class="intro">
      <strong>Stars / cadence:</strong> <code>gh api repos/&lt;owner&gt;/&lt;repo&gt;</code> and <code>.../stats/participation</code>, snapshot {SNAPSHOT_DATE}.
      <strong>Freshness (0–5):</strong> blended from last-push recency and sustained cadence, capped for archived/dormant repos — <code>5</code> pushed ≤1wk with heavy cadence · <code>4</code> ≤1mo clearly active · <code>3</code> ≤2mo maintained · <code>2</code> ≤3–4mo or sporadic · <code>1</code> archived / &gt;4mo near-zero · <code>0.5</code> ~10mo+ abandoned.
      <strong>Maturity:</strong> the frozen median-of-3 <code>raise_posture.weighted_overall</code> from <code>tests/baselines/{html.escape(baseline_name)}/</code>.
      Full per-target rationale and the retired targets' record live in <code>tests/baselines/ROSTER_HEALTH.md</code>.
      For the security dimensions, see the <a href="owasp-coverage-report.html">OWASP</a> and <a href="raise-coverage-report.html">RAISE</a> coverage pages.
    </p>
  </section>

  <footer class="foot">
    Generated {generated} · Popularity/freshness snapshot {SNAPSHOT_DATE} · Maturity from the Praxen <code>{html.escape(baseline_name)}</code> baseline ·
    <a href="https://github.com/open-agent-ai-security/praxen" target="_blank" rel="noopener">github.com/open-agent-ai-security/praxen</a>
  </footer>
</div>
</body></html>
"""


def main():
    ap = argparse.ArgumentParser(description="Render the Praxen Suite Health (popularity + freshness) report.")
    ap.add_argument("--baseline-dir", type=Path, default=DEFAULT_BASELINE)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    out = args.out
    out.write_text(build_html(args.baseline_dir, out.resolve().parent), encoding="utf-8")
    print(f"suite_health.py: wrote {out}")


if __name__ == "__main__":
    main()
