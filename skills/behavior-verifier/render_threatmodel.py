#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Render a Praxen threat-model graph JSON to a self-contained HTML report.

Stage 2 of the threat-model pipeline: the extraction pass emits a graph
conforming to ``THREAT_MODEL_SPEC.md`` (validated here via
``threatmodel_schema.py``); this module renders the deterministic lane-layout
diagram plus the static companions (legend, boundary key, attack paths,
boundary detail, component inventory).

Design contract (RELEASE_2.0_PLAN.md item 4):

* **Visual alignment, single-source.** The report must read as the same
  product as the analysis report. Brand chrome is EXTRACTED from
  ``report_template.html`` at render time — the ``:root`` token block and the
  masthead/footer logo lockups — never copied into this file. A template
  restyle flows through automatically; if the template's anchors move, this
  renderer fails loudly rather than shipping an off-brand report. The few
  literal colors this module carries (the lightened-on-navy masthead
  variants) are asserted against the template text by the test suite.
* **Static-completeness.** The page reads complete on paper: printed legend,
  boundary key table, kind icons, numbered attack-path badges, component
  inventory with citations, print CSS. Hover behaviors (highlighting, fan
  labels, disciplined tooltips) are an enhancement layer only.
* **Determinism.** Same graph + same template -> byte-identical output.

Python 3.9+ stdlib only.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys

import threatmodel_schema as tms
from schema import SchemaError

# ── layout constants ─────────────────────────────────────────────────────────
LANE_TITLES = {
    "user_inputs": "User / Inputs",
    "client_adapters": "Client / Adapters",
    "agent_core": "Agent Core",
    "tools_mcp": "Tools / MCP",
    "external_deploy": "External / Deploy",
}
COL_W, COL_GAP, MARGIN_X, TOP_Y = 250, 110, 30, 158
BAND_TOP, BAND_ROW = 16, 26   # boundary badges live in a reserved strip
NODE_GAP = 22

# ── color semantics (token NAMES — resolved from the template's :root) ───────
# Color carries FAMILY (6, trackable); the icon carries the exact KIND.
KIND_TOKEN = {
    "entrypoint": "--purple",
    "client": "--blue", "adapter": "--blue",
    "orchestrator": "--blue-dark", "model": "--blue-dark",
    "prompt": "--blue-dark", "memory": "--blue-dark",
    "tool": "--green", "mcp_server": "--green", "datastore": "--green",
    "control": "--sev-medium",
    "external_service": "--sev-low", "deploy_surface": "--sev-low",
    "secret_store": "--sev-low", "log_sink": "--sev-low",
}
FAMILIES = [
    ("actors & inputs", "--purple"), ("client / adapters", "--blue"),
    ("agent core", "--blue-dark"), ("tools & data", "--green"),
    ("controls", "--sev-medium"), ("external & deploy", "--sev-low"),
]
# confirmed = red (a finding proves it) / potential = blue, deliberately OFF
# the red/yellow/green assessment ladder (not yet judged) / partial = gold /
# mitigated = green. Ladder for boundary coloring, worst first.
STATUS_TOKEN = {"confirmed": "--sev-critical", "potential": "--blue",
                "partial": "--sev-medium", "mitigated": "--green"}
STATUS_RANK = {"mitigated": 0, "partial": 1, "potential": 2, "confirmed": 3}
COVERAGE_TOKEN = {"verified": "--green", "partial": "--sev-medium",
                  "gap": "--sev-critical", "vague": "--sev-low", "enp": "--sev-low"}
# Lightened-on-navy masthead variants — literals mirrored from
# report_template.html's .mh-metric rules; test_render_threatmodel.py asserts
# each appears in the template so drift is caught.
MH_CONFIRMED, MH_POTENTIAL, MH_PARTIAL, MH_MITIGATED = (
    "#FF7A6B", "#27B2FF", "#F2CD5A", "#4CDB00")

# 24x24 stroke glyphs; a tool looks like a tool.
ICONS = {
    "entrypoint": '<path d="M13 4h6v16h-6M3 12h11M10 8l4 4-4 4"/>',
    "client": '<rect x="3" y="5" width="18" height="12" rx="1.5"/><path d="M9 21h6M12 17v4"/>',
    "adapter": '<path d="M9 3v5M15 3v5M7 8h10v4a5 5 0 0 1-10 0zM12 17v4"/>',
    "orchestrator": '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>',
    "model": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8zM19 16l.9 2.1L22 19l-2.1.9L19 22l-.9-2.1L16 19l2.1-.9z"/>',
    "prompt": '<path d="M6 3h9l4 4v14H6zM15 3v4h4M9 11h7M9 15h7"/>',
    "memory": '<rect x="6" y="6" width="12" height="12" rx="1.5"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
    "datastore": '<ellipse cx="12" cy="5.5" rx="8" ry="3"/><path d="M4 5.5V18c0 1.7 3.6 3 8 3s8-1.3 8-3V5.5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    "tool": '<path d="M14.5 6.5a4.5 4.5 0 0 0-6 5.6L3 17.6V21h3.4l5.5-5.5a4.5 4.5 0 0 0 5.6-6L14 13l-3-3z"/>',
    "mcp_server": '<rect x="3" y="4" width="18" height="7" rx="1.5"/><rect x="3" y="13" width="18" height="7" rx="1.5"/><circle cx="7" cy="7.5" r="0.8"/><circle cx="7" cy="16.5" r="0.8"/>',
    "control": '<path d="M12 3l8 3v6c0 4.5-3.2 7.6-8 9-4.8-1.4-8-4.5-8-9V6zM8.8 12l2.2 2.2 4.2-4.2"/>',
    "external_service": '<path d="M7 18a4.5 4.5 0 1 1 .8-8.9A6 6 0 0 1 19 11a3.5 3.5 0 0 1-1 7z"/>',
    "deploy_surface": '<path d="M12 2l8 4.5v11L12 22l-8-4.5v-11zM12 2v9M4 6.5l8 4.5 8-4.5M12 22V11"/>',
    "secret_store": '<circle cx="8" cy="8" r="5"/><path d="M11.5 11.5L21 21M17 17l2-2M14 14l2-2"/>',
    "log_sink": '<path d="M4 5h2M9 5h11M4 12h2M9 12h11M4 19h2M9 19h11"/>',
}


class RenderError(ValueError):
    """Raised when the template lacks a brand anchor this renderer needs."""


def esc(s):
    return html.escape(str(s), quote=True)


# ── brand extraction (single source: report_template.html) ───────────────────
def extract_brand(template_text):
    """Extract the shared brand assets from the analysis-report template.

    Returns (tokens: dict name->value, root_css: str, masthead_logo: str,
    footer_logo: str). Fails loudly if any anchor is missing — an off-brand
    render is a bug, not a fallback.
    """
    m = re.search(r":root\s*\{(.*?)\}", template_text, re.S)
    if not m:
        raise RenderError("report_template.html: ':root {...}' token block not found")
    root_body = m.group(1)
    tokens = dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", root_body))
    if "--navy" not in tokens or "--orange" not in tokens:
        raise RenderError("report_template.html: :root block lacks expected brand tokens")

    def block(start_marker, what):
        i = template_text.find(start_marker)
        if i < 0:
            raise RenderError(f"report_template.html: {what} anchor "
                              f"({start_marker!r}) not found")
        j = template_text.find("</svg></div>", i)
        if j < 0:
            raise RenderError(f"report_template.html: {what} block is not closed")
        return template_text[i:j + len("</svg></div>")]

    masthead_logo = block('<div class="masthead-logo">', "masthead logo lockup")
    footer_logo = block('<div class="footer-logo">', "footer logo lockup")
    root_css = ":root {" + root_body + "}"
    return tokens, root_css, masthead_logo, footer_logo


def _resolve(tokens, name):
    val = tokens.get(name, "").strip()
    if not val:
        raise RenderError(f"report_template.html: token {name} missing from :root")
    return val


# ── text helpers ─────────────────────────────────────────────────────────────
def wrap(text, width=30):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines[:3]


def icon_svg(kind, color, size=16):
    p = ICONS.get(kind, "")
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" '
            f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{p}</svg>')


def worst_status(threats):
    worst = "mitigated"
    for t in threats:
        st = t["status"]
        if STATUS_RANK[st] > STATUS_RANK[worst]:
            worst = st
        if worst == "confirmed":
            break
    return worst


# ── render ───────────────────────────────────────────────────────────────────
def render(graph, template_text):
    """Render a validated graph to a self-contained HTML string."""
    g = tms.validate(graph)
    tokens, root_css, mh_logo, ft_logo = extract_brand(template_text)

    def tok(name):
        return _resolve(tokens, name)

    kind_color = {k: tok(v) for k, v in KIND_TOKEN.items()}
    status_color = {k: tok(v) for k, v in STATUS_TOKEN.items()}
    coverage_color = {k: tok(v) for k, v in COVERAGE_TOKEN.items()}

    nodes = {n["id"]: n for n in g["nodes"]}
    LANES = tms.LANES

    # -- barycenter ordering: cut crossings with a few alternating sweeps --
    lane_of = {n["id"]: n["lane"] for n in g["nodes"]}
    neigh = {n["id"]: [] for n in g["nodes"]}
    for e in g["edges"]:
        neigh[e["from"]].append(e["to"])
        neigh[e["to"]].append(e["from"])
    order = {ln: [n["id"] for n in g["nodes"] if n["lane"] == ln] for ln in LANES}
    for _ in range(4):
        rank = {}
        for ln in LANES:
            for i, nid in enumerate(order[ln]):
                rank[nid] = i
        for ln in LANES:
            order[ln].sort(key=lambda nid: (sum(rank[m] for m in neigh[nid]) / len(neigh[nid]))
                           if neigh[nid] else rank[nid])

    pos, lane_y = {}, {ln: TOP_Y + 30 for ln in LANES}
    lane_x = {ln: MARGIN_X + i * (COL_W + COL_GAP) for i, ln in enumerate(LANES)}
    for ln in LANES:
        for nid in order[ln]:
            lines = wrap(nodes[nid]["name"])
            h = 30 + 14 * len(lines) + 14
            pos[nid] = (lane_x[ln], lane_y[ln], h, lines)
            lane_y[ln] += h + NODE_GAP
    total_h = max(lane_y.values()) + 40
    total_w = MARGIN_X * 2 + 5 * COL_W + 4 * COL_GAP

    # -- edge ports: fan out along each node side, sorted by destination --
    side_edges = {}
    def side_of(e, which):
        fl, tl = LANES.index(lane_of[e["from"]]), LANES.index(lane_of[e["to"]])
        if which == "from":
            return "R" if tl >= fl else "L"
        return "L" if tl >= fl else "R"
    for e in g["edges"]:
        side_edges.setdefault((e["from"], side_of(e, "from")), []).append(e["id"])
        side_edges.setdefault((e["to"], side_of(e, "to")), []).append(e["id"])
    edge_by_id = {e["id"]: e for e in g["edges"]}
    port = {}
    for (nid, _sd), eids in side_edges.items():
        eids.sort(key=lambda eid: pos[edge_by_id[eid]["to"]
                                      if edge_by_id[eid]["from"] == nid
                                      else edge_by_id[eid]["from"]][1])
        x, y, h, _ = pos[nid]
        for i, eid in enumerate(eids):
            port[(eid, nid)] = y + h * (i + 1) / (len(eids) + 1)

    svg = []
    # lane backgrounds + titles
    for ln in LANES:
        x = lane_x[ln]
        svg.append(f'<rect x="{x-10}" y="{TOP_Y-30}" width="{COL_W+20}" '
                   f'height="{total_h-TOP_Y+10}" rx="10" fill="#FFFFFF" '
                   f'stroke="{tok("--border")}"/>')
        svg.append(f'<text x="{x+COL_W/2}" y="{TOP_Y-8}" text-anchor="middle" '
                   f'font-size="13" font-weight="700" fill="{tok("--text-muted")}">'
                   f'{esc(LANE_TITLES[ln])}</text>')

    # boundary badges (reserved band) + dashed lines at the modal crossed gap
    def gap_of_edge(e):
        fi = LANES.index(lane_of[e["from"]])
        ti = LANES.index(lane_of[e["to"]])
        lo, hi = sorted((fi, ti))
        return lo if hi > lo else None
    bnd_num = {b["id"]: f"B{i}" for i, b in enumerate(g["trust_boundaries"], 1)}
    bnd_at_gap = {}
    for b in g["trust_boundaries"]:
        gaps = [gap_of_edge(edge_by_id[c]) for c in b["crossing_edges"]]
        gaps = [x for x in gaps if x is not None]
        gap = max(set(gaps), key=gaps.count) if gaps else 1
        bnd_at_gap.setdefault(gap, []).append((b, worst_status(b["threats"])))
    for gap, blist in bnd_at_gap.items():
        for j, (b, worst) in enumerate(blist):
            x = MARGIN_X + (gap + 1) * COL_W + gap * COL_GAP + COL_GAP / 2 \
                + (j - (len(blist) - 1) / 2) * 16
            c = status_color[worst]
            by = BAND_TOP + (j % 4) * BAND_ROW + 11
            btip = (f'{bnd_num[b["id"]]} — {b["name"]} · {len(b["threats"])} threats · '
                    f'{len(b["remit_rules"])} remit rules (details below)')
            svg.append(f'<g class="bnd" data-tip="{esc(btip)}">')
            svg.append(f'<line x1="{x}" y1="{by+11}" x2="{x}" y2="{total_h-20}" '
                       f'stroke="{c}" stroke-width="2" stroke-dasharray="7 5" opacity="0.75"/>')
            svg.append(f'<circle cx="{x}" cy="{by}" r="11" fill="{c}"/>'
                       f'<text x="{x}" y="{by+4}" text-anchor="middle" font-size="10.5" '
                       f'font-weight="700" fill="#fff">{esc(bnd_num[b["id"]])}</text>')
            svg.append('</g>')

    # edges — hit path + visible path; labels render in a top layer
    arrow_grey, arrow_blue = tok("--text-muted"), tok("--blue")
    # Arrowheads anchor at their BACK edge (refX=0), so the marker sits with its
    # flat rear centered on the path's end and its tip extending ARROW_LEN px
    # forward along the tangent. The path is trimmed by ARROW_LEN so the tip
    # lands on the node edge and the visible line meets the center of that flat
    # back edge — not the target pixel under the head. On a sharply curved
    # bezier the trim follows the real end tangent (endpoint - last control
    # point), keeping the head square to the line instead of stabbing its side.
    ARROW_LEN = 7.0  # = markerWidth(7) * viewBox-span(10)/10

    def _trimmed(sx, sy, c1x, c1y, c2x, c2y, ex, ey):
        dx, dy = ex - c2x, ey - c2y
        L = (dx * dx + dy * dy) ** 0.5
        if L > 1e-6:
            ex -= ARROW_LEN * dx / L
            ey -= ARROW_LEN * dy / L
        return f"M{sx} {sy} C {c1x} {c1y}, {c2x} {c2y}, {ex} {ey}"

    # markerUnits="userSpaceOnUse" pins the head to a fixed ARROW_LEN px
    # regardless of stroke width. Without it markers default to scaling with
    # strokeWidth, so on highlight (stroke 1.2 -> 2.6) the head would balloon
    # and its tip would shoot ARROW_LEN*2+ px past the trim, deep into the box.
    # Both heads are ARROW_LEN long so the tip lands on the node edge in both
    # states; the highlight reads through the blue fill and thicker line, not a
    # bigger head.
    svg.append(f'<defs><marker id="arr" viewBox="0 0 10 10" refX="0" refY="5" '
               f'markerWidth="{ARROW_LEN}" markerHeight="{ARROW_LEN}" '
               f'markerUnits="userSpaceOnUse" orient="auto-start-reverse">'
               f'<path d="M0 0L10 5L0 10z" fill="{arrow_grey}"/></marker>'
               f'<marker id="arr-hi" viewBox="0 0 10 10" refX="0" refY="5" '
               f'markerWidth="{ARROW_LEN}" markerHeight="{ARROW_LEN}" '
               f'markerUnits="userSpaceOnUse" orient="auto-start-reverse">'
               f'<path d="M0 0L10 5L0 10z" fill="{arrow_blue}"/></marker></defs>')
    loop_count, elbls, ei = {}, [], 0
    for e in g["edges"]:
        f, t = pos[e["from"]], pos[e["to"]]
        fy = port[(e["id"], e["from"])]
        ty = port[(e["id"], e["to"])]
        fx, tx = f[0], t[0]
        span = abs(LANES.index(lane_of[e["to"]]) - LANES.index(lane_of[e["from"]]))
        tip = (f'{nodes[e["from"]]["name"]} → {nodes[e["to"]]["name"]}: '
               f'{e["label"]} [{e["data"]}]')
        if fx == tx:  # same lane: side loop, offset per loop
            x1 = x2 = fx + COL_W
            k = loop_count.get(e["from"], 0); loop_count[e["from"]] = k + 1
            mx = x1 + 36 + 20 * k
            d = _trimmed(x1, fy, mx, fy, mx, ty, x2, ty)
            lx, ly, rot = mx + 6, (fy + ty) / 2, ""
            dim = ""
        else:
            x1 = (fx + COL_W) if fx < tx else fx
            x2 = tx if fx < tx else (tx + COL_W)
            mx = (x1 + x2) / 2
            if span >= 2:
                # bow around intermediate columns, direction-aware, clamped
                # below the badge band.
                dirn = 1 if x2 >= x1 else -1
                dip = 55 * (span - 1) * (1 if (fy + ty) / 2 > (total_h + TOP_Y) / 2 else -1)
                floor_y = TOP_Y - 22
                cy1 = max(fy + dip, floor_y)
                cy2 = max(ty + dip, floor_y)
                d = _trimmed(x1, fy, x1 + 90 * dirn, cy1, x2 - 90 * dirn, cy2, x2, ty)
                ly = (fy + ty) / 2 + (cy1 - fy) * 0.75
            else:
                d = _trimmed(x1, fy, mx, fy, mx, ty, x2, ty)
                ly = (fy + ty) / 2
            lx = mx - 4
            rot = f' transform="rotate(-90 {lx} {ly})"'
            dim = ' style="opacity:.22"' if span >= 2 else ''
        svg.append(f'<g class="edge" data-ei="{ei}" data-from="{esc(e["from"])}" '
                   f'data-to="{esc(e["to"])}" data-tip="{esc(tip)}">')
        svg.append(f'<path class="hit" d="{d}" fill="none" stroke="transparent" stroke-width="9"/>')
        svg.append(f'<path class="vis" d="{d}" fill="none" stroke="{arrow_grey}" '
                   f'stroke-width="1.2" marker-end="url(#arr)" opacity="0.4"{dim}/>')
        svg.append('</g>')
        elbls.append(f'<text class="elbl" data-ei="{ei}" x="{lx}" y="{ly}" '
                     f'text-anchor="middle" font-size="10.5" font-weight="600" '
                     f'fill="{tok("--blue-dark")}" paint-order="stroke" stroke="#FFFFFF" '
                     f'stroke-width="3.5"{rot}>{esc(e["label"])}</text>')
        ei += 1

    # attack-path step badges (first path; sequence is the story — route ink
    # was tried twice in the probe and rejected: it sprays across the canvas)
    ap = g["attack_paths"]
    badge_at = {}
    if ap:
        for i, step in enumerate(ap[0]["steps"], 1):
            badge_at[step["node"]] = i

    for n in g["nodes"]:
        x, y, h, lines = pos[n["id"]]
        c = kind_color[n["kind"]]
        tip = n["description"] + " | evidence: " + "; ".join(
            f'{ev["file"]}:{ev.get("line") or "—"}' for ev in n["evidence"][:4])
        if n["id"] in badge_at and ap:
            tip += (f' | ⚔ attack-path step {badge_at[n["id"]]} of '
                    f'{len(ap[0]["steps"])}: “{ap[0]["name"]}”')
        svg.append(f'<g class="node" data-id="{esc(n["id"])}" data-tip="{esc(tip)}">')
        svg.append(f'<rect x="{x}" y="{y}" width="{COL_W}" height="{h}" rx="8" '
                   f'fill="#fff" stroke="{c}" stroke-width="1.6"/>')
        svg.append(f'<rect x="{x}" y="{y}" width="5" height="{h}" rx="2.5" fill="{c}"/>')
        for li, line in enumerate(lines):
            svg.append(f'<text x="{x+14}" y="{y+20+14*li}" font-size="12" '
                       f'font-weight="600" fill="{tok("--text")}">{esc(line)}</text>')
        svg.append(f'<text x="{x+14}" y="{y+h-8}" font-size="9.5" fill="{c}" '
                   f'font-weight="600">{esc(n["kind"].upper())}</text>')
        icp = ICONS.get(n["kind"], "")
        if icp:
            svg.append(f'<g transform="translate({x+COL_W-26},{y+7}) scale(0.75)" '
                       f'fill="none" stroke="{c}" stroke-width="1.8" '
                       f'stroke-linecap="round" stroke-linejoin="round">{icp}</g>')
        if n["id"] in badge_at:
            svg.append(f'<circle cx="{x+COL_W-14}" cy="{y+h-13}" r="10" '
                       f'fill="{tok("--sev-critical")}"/>'
                       f'<text x="{x+COL_W-14}" y="{y+h-9}" text-anchor="middle" '
                       f'font-size="11" font-weight="700" fill="#fff">{badge_at[n["id"]]}</text>')
        svg.append('</g>')
    svg.append('<g class="lblLayer">' + "".join(elbls) + '</g>')

    # -- static companions -----------------------------------------------------
    def chip(text, color):
        return (f'<span style="background:{color};color:#fff;border-radius:4px;'
                f'padding:1px 7px;font-size:11px;font-weight:600">{esc(text)}</span>')

    kinds_present = []
    for n in g["nodes"]:
        if n["kind"] not in kinds_present:
            kinds_present.append(n["kind"])
    fam_present = {kind_color[k] for k in kinds_present}
    row1 = "".join(
        f'<span class="lg"><i style="background:#fff;border:2px solid {tok(c)};'
        f'border-left:5px solid {tok(c)}"></i>{esc(nm)}</span>'
        for nm, c in FAMILIES if tok(c) in fam_present)
    row2 = "".join(f'<span class="lg">{icon_svg(k, kind_color[k])}'
                   f'{esc(k.replace("_", " "))}</span>' for k in kinds_present)
    row3 = "".join([
        f'<span class="lg"><i class="lg-dash" style="border-color:{status_color["confirmed"]}"></i>boundary — worst threat: confirmed</span>',
        f'<span class="lg"><i class="lg-dash" style="border-color:{status_color["potential"]}"></i>— potential (unanswered hypothesis)</span>',
        f'<span class="lg"><i class="lg-dash" style="border-color:{status_color["partial"]}"></i>— partial (control covers part; remainder stated)</span>',
        f'<span class="lg"><i class="lg-dash" style="border-color:{status_color["mitigated"]}"></i>— mitigated</span>',
        f'<span class="lg"><b class="lg-b" style="background:{status_color["confirmed"]}">1</b>attack-path step (follow 1→2→3…)</span>',
        '<span class="lg"><i class="lg-arc"></i>faint arc = flow spanning 2+ lanes</span>',
    ])
    legend_html = (f'<div class="lg-row"><span class="lg-cap">Families</span>{row1}</div>'
                   f'<div class="lg-row"><span class="lg-cap">Kinds</span>{row2}</div>'
                   f'<div class="lg-row"><span class="lg-cap">Marks</span>{row3}</div>')

    bk_rows = []
    for b in g["trust_boundaries"]:
        worst = worst_status(b["threats"])
        c = status_color[worst]
        bk_rows.append(
            f'<tr><td><b class="lg-b" style="background:{c}">{bnd_num[b["id"]]}</b></td>'
            f'<td><b>{esc(b["name"])}</b> <span class="rx">({esc(b["id"])})</span></td>'
            f'<td>{len(b["threats"])}</td><td>{len(b["remit_rules"])}</td>'
            f'<td style="color:{c};font-weight:700">{worst}</td></tr>')
    boundary_key_html = ('<table class="bk"><tr><th></th><th>Trust boundary</th>'
                         '<th>Threats</th><th>Remit rules</th><th>Worst status</th></tr>'
                         + "".join(bk_rows) + '</table>')

    appanels = []
    for p in ap:
        steps = " → ".join(
            f'<b>{esc(nodes[s["node"]]["name"])}</b>'
            + (f' <span class="fid">[{esc(s["finding_id"])}]</span>' if s.get("finding_id") else "")
            + f' <span class="rx">{esc(s["summary"])}</span>'
            for s in p["steps"])
        appanels.append(f'<div class="ap">⚔ <b>{esc(p["name"])}</b>: {steps}</div>')

    panels = []
    for b in g["trust_boundaries"]:
        rows = []
        for t in b["threats"]:
            extra = ""
            if t["status"] == "confirmed":
                extra = f' <span class="fid">{esc(t["finding_id"])}</span>'
            elif t["status"] in ("mitigated", "partial"):
                mev = t["mitigation_evidence"]
                extra = f' <span class="rx">{esc(mev["file"])}:{esc(mev.get("line") or "—")}</span>'
                if t["status"] == "partial":
                    extra += f'<br><span class="rx">remainder: {esc(t["remainder"])}</span>'
            rows.append(f'<tr><td>{esc(t["stride"])}</td><td>{esc(t["owasp"] or "—")}</td>'
                        f'<td>{esc(t["summary"])}</td>'
                        f'<td>{chip(t["status"], status_color[t["status"]])}{extra}</td></tr>')
        remits = " ".join(
            chip(f'{r["rule_id"]} {r["coverage_status"]}', coverage_color[r["coverage_status"]])
            + f' <span class="rx">{esc(r["excerpt"])}</span><br>'
            for r in b["remit_rules"])
        panels.append(
            f'<details open><summary><b>{bnd_num[b["id"]]} — {esc(b["name"])}</b> — '
            f'{len(b["threats"])} threats, {len(b["remit_rules"])} remit rules</summary>'
            f'<div class="remits">{remits or "<i>the remit does not touch this boundary — threats here are assessed against the RAISE/OWASP baseline alone (a remit is a job description, not a security model; silence here is normal)</i>"}</div>'
            f'<table><tr><th>STRIDE</th><th>OWASP</th><th>Threat</th><th>Status</th></tr>'
            + "".join(rows) + '</table></details>')

    inv_rows = []
    for n in g["nodes"]:
        evs = "; ".join(f'{ev["file"]}:{ev.get("line") or "—"}' for ev in n["evidence"][:2])
        inv_rows.append(
            f'<tr><td style="white-space:nowrap">{icon_svg(n["kind"], kind_color[n["kind"]], 14)} '
            f'<b>{esc(n["name"])}</b></td><td>{esc(n["kind"])}</td><td>{esc(n["lane"])}</td>'
            f'<td>{esc(n["description"])}</td><td class="rx">{esc(evs)}</td></tr>')
    inventory_html = ('<table><tr><th>Component</th><th>Kind</th><th>Lane</th>'
                      '<th>Description</th><th>Evidence</th></tr>'
                      + "".join(inv_rows) + '</table>')

    counts = {st: sum(1 for b in g["trust_boundaries"] for t in b["threats"]
                      if t["status"] == st) for st in tms.THREAT_STATUSES}
    notes = g["notes"]
    aref = g.get("analysis_ref")
    aref_html = (f' · built against <b>{esc(aref)}</b>' if aref
                 else ' · no analysis reference (standalone extraction)')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Praxen Threat Model — {esc(g["target"]["slug"])}</title>
<style>
  {root_css}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:'Lausanne',Arial,'Helvetica Neue',Helvetica,sans-serif; background:var(--bg); color:var(--text); font-size:14px; line-height:1.5; }}
  .masthead {{ background:var(--navy); border-top:4px solid var(--orange); border-bottom:2px solid var(--border-alt); padding:18px 32px 22px; }}
  .masthead-logo svg {{ height:44px; width:auto; display:block; }}
  .masthead-main {{ display:flex; justify-content:space-between; align-items:flex-start; gap:24px; flex-wrap:wrap; }}
  .masthead-agent {{ color:#FFF; font-size:19px; font-weight:800; line-height:1.1; letter-spacing:0.01em; margin-top:18px; }}
  .masthead-kind {{ color:var(--orange-2); font-size:11px; font-weight:800; letter-spacing:0.14em; text-transform:uppercase; margin-top:8px; }}
  .masthead-date {{ color:#8BAFC8; font-size:13px; margin-top:6px; }}
  .masthead-metrics {{ display:flex; gap:24px; justify-content:flex-end; margin-top:6px; }}
  .mh-metric {{ text-align:center; }}
  .mh-metric > b {{ display:block; font-size:30px; font-weight:800; line-height:1; color:#FFF; }}
  .mh-metric > span {{ display:block; font-size:10px; letter-spacing:0.09em; text-transform:uppercase; color:#8BAFC8; margin-top:6px; }}
  .mh-metric.mh-con > b {{ color:{MH_CONFIRMED}; }} .mh-metric.mh-pot > b {{ color:{MH_POTENTIAL}; }}
  .mh-metric.mh-par > b {{ color:{MH_PARTIAL}; }} .mh-metric.mh-mit > b {{ color:{MH_MITIGATED}; }}
  .content {{ padding:28px 32px; max-width:1100px; margin:0 auto; }}
  .section {{ margin-bottom:40px; }}
  .section-title {{ font-size:13px; font-weight:800; color:var(--blue-dark); text-transform:uppercase; letter-spacing:0.08em; border-bottom:2px solid var(--border); padding-bottom:8px; margin-bottom:10px; }}
  .section-desc {{ color:#555; font-size:13px; margin:0 0 18px; line-height:1.6; }}
  .section-fullbleed {{ max-width:none; margin-left:calc(50% - 50vw); margin-right:calc(50% - 50vw); padding-left:32px; padding-right:32px; }}
  .svgwrap {{ overflow-x:auto; border:1px solid var(--border); border-radius:10px; background:var(--surface); padding:8px; }}
  details {{ background:#FFF; border:1px solid var(--border); border-radius:8px; padding:10px 14px; margin:10px 0; }}
  summary {{ cursor:pointer; }} summary b {{ color:var(--navy); }}
  table {{ border-collapse:collapse; margin-top:8px; font-size:12.5px; width:100%; }}
  th,td {{ border:1px solid var(--border); padding:5px 9px; text-align:left; vertical-align:top; }}
  th {{ background:var(--surface); font-size:11px; font-weight:800; letter-spacing:0.06em; text-transform:uppercase; color:var(--text-muted); }}
  .remits {{ margin:8px 0; font-size:12.5px; line-height:2; }}
  .rx {{ color:var(--text-muted); font-size:11.5px; }} .fid {{ color:var(--sev-high); font-weight:700; font-size:11.5px; }}
  .ap {{ background:var(--surface-alt); border:1px solid var(--border-alt); border-left:4px solid var(--sev-critical); border-radius:0 8px 8px 0; padding:12px 16px; margin:10px 0; font-size:13px; }}
  .notes {{ font-size:12px; color:var(--text-muted); }}
  .legend {{ font-size:11.5px; color:var(--text-muted); }}
  .legend .lg-row {{ display:flex; flex-wrap:wrap; gap:6px 16px; align-items:center; padding:3px 0; }}
  .legend .lg-cap {{ font-size:10px; font-weight:800; letter-spacing:0.1em; text-transform:uppercase; color:#8A97A8; width:58px; flex-shrink:0; }}
  .legend .lg {{ display:inline-flex; align-items:center; gap:6px; }}
  .legend .lg i {{ display:inline-block; width:20px; height:12px; border-radius:3px; }}
  .legend .lg i.lg-dash {{ width:22px; height:0; border-top:2px dashed; border-radius:0; background:none; }}
  .legend .lg i.lg-arc {{ width:22px; height:8px; border:1.5px solid var(--text-muted); border-bottom:none; border-radius:11px 11px 0 0; opacity:.4; background:none; }}
  .legend .lg svg {{ display:inline-block; vertical-align:middle; }}
  b.lg-b {{ display:inline-flex; align-items:center; justify-content:center; min-width:20px; height:20px; padding:0 3px; border-radius:10px; background:var(--sev-high); color:#fff; font-size:10px; font-weight:700; }}
  .bk {{ margin-top:14px; }} .bk td, .bk th {{ padding:4px 9px; }}
  .elbl {{ opacity:0; pointer-events:none; transition:opacity .1s; }}
  .elbl.show {{ opacity:1; }}
  .edge:hover .vis, .edge.hi .vis {{ stroke:var(--blue); stroke-width:2.6; opacity:1 !important; marker-end:url(#arr-hi); }}
  .node:hover rect:first-of-type {{ filter:drop-shadow(0 0 4px rgba(0,107,255,.55)); cursor:default; }}
  .bnd:hover line {{ opacity:1; stroke-width:3; }} .bnd {{ cursor:default; }}
  #tt {{ position:fixed; background:var(--navy); color:var(--surface); padding:7px 11px; border-radius:7px; font-size:12.5px; line-height:1.45; max-width:380px; pointer-events:none; opacity:0; z-index:10; box-shadow:0 3px 10px rgba(13,27,42,.35); transition:opacity .08s; }}
  .footer {{ background:var(--navy); border-top:4px solid var(--orange); margin-top:40px; padding:18px 32px; color:#8BAFC8; }}
  .footer .rf-row {{ display:flex; justify-content:space-between; align-items:center; gap:24px; flex-wrap:wrap; }}
  .footer .footer-logo svg {{ height:34px; width:auto; display:block; }}
  .footer .rf-gh {{ display:inline-flex; align-items:center; gap:8px; color:#CDD8E4; text-decoration:none; font-size:13.5px; font-weight:600; border:1px solid #2A3D57; border-radius:8px; padding:7px 13px; }}
  .footer .rf-gh:hover {{ border-color:var(--orange); color:#FFF; }}
  .footer .rf-legal {{ font-size:11.5px; color:#6E7F92; line-height:1.6; text-align:right; }}
  @media print {{
    .elbl {{ opacity:1 !important; }}
    #tt {{ display:none; }}
    .svgwrap {{ overflow:visible; border:none; padding:0; }}
    .svgwrap svg {{ max-width:100%; height:auto; }}
    details {{ page-break-inside:avoid; }}
    .section {{ page-break-inside:avoid; }}
  }}
</style></head><body>
<div class="masthead"><div class="masthead-main">
  <div>{mh_logo}
    <div class="masthead-agent">{esc(g["target"]["slug"])}</div>
    <div class="masthead-kind">Threat Model</div>
    <div class="masthead-date">evidence-derived · Praxen {esc(g["praxen_version"])} · graph contract {esc(g["spec_version"])}{aref_html}</div>
  </div>
  <div class="masthead-summary">
    <div class="masthead-metrics">
      <div class="mh-metric"><b>{len(g["nodes"])}</b><span>Components</span></div>
      <div class="mh-metric"><b>{len(g["edges"])}</b><span>Flows</span></div>
      <div class="mh-metric"><b>{len(g["trust_boundaries"])}</b><span>Boundaries</span></div>
      <div class="mh-metric mh-con"><b>{counts["confirmed"]}</b><span>Confirmed</span></div>
      <div class="mh-metric mh-pot"><b>{counts["potential"]}</b><span>Potential</span></div>
      <div class="mh-metric mh-par"><b>{counts["partial"]}</b><span>Partial</span></div>
      <div class="mh-metric mh-mit"><b>{counts["mitigated"]}</b><span>Mitigated</span></div>
    </div>
  </div>
</div></div>
<div class="content">
<div class="section section-fullbleed">
<div class="section-title">Architecture &amp; Trust Boundaries</div>
<div class="section-desc" style="max-width:1100px;margin-left:auto;margin-right:auto">Every component, flow, and boundary cites evidence. Hover nodes for citations, edges for what flows, and B-badges for boundary detail — or read it all statically: the key below resolves every mark, and the component inventory carries every citation.</div>
<div class="svgwrap"><svg width="{total_w}" height="{total_h}" viewBox="0 0 {total_w} {total_h}" xmlns="http://www.w3.org/2000/svg">{"".join(svg)}</svg></div>
<div class="legend" style="max-width:1100px;margin:12px auto 0">{legend_html}</div>
<div style="max-width:1100px;margin:0 auto">{boundary_key_html}</div>
</div>
<div class="section"><div class="section-title">Attack Paths</div>{"".join(appanels) or '<div class="notes">none grounded in findings</div>'}</div>
<div class="section"><div class="section-title">Trust Boundaries — Threats &amp; Governing Remit Rules</div>{"".join(panels)}</div>
<div class="section"><div class="section-title">Component Inventory</div>
<div class="section-desc">Every component with its kind, lane, and source evidence — the diagram's tooltips, on paper.</div>{inventory_html}</div>
<div class="section"><div class="section-title">Extraction Notes</div>
<div class="notes">lane_fit: {esc(notes["lane_fit"])}<br>omissions: {esc(notes["omissions"] or "none recorded")}<br>model: {esc(g["model_identity"])}</div></div>
</div>
<div class="footer"><div class="rf-row">
  {ft_logo}
  <a class="rf-gh" href="https://github.com/open-agent-ai-security/praxen"><span>github.com/open-agent-ai-security/praxen</span></a>
  <div class="rf-legal">Praxen threat model — evidence-derived; every element cites source.<br>Generated by Praxen {esc(g["praxen_version"])}.</div>
</div></div>
<div id="tt"></div>
<script>
const tt = document.getElementById('tt');
// Tooltip discipline: 250ms show-delay (deliberate dwell, not traversal),
// click or Esc dismisses (until a new element is entered), 6s dwell
// auto-fade so it never parks on screen.
let showTimer = null, fadeTimer = null, suppressed = false, mx = 0, my = 0;
const place = () => {{
  tt.style.left = Math.min(mx + 14, window.innerWidth - 400) + 'px';
  tt.style.top = (my + 14) + 'px';
}};
const hideTip = () => {{ clearTimeout(showTimer); clearTimeout(fadeTimer); tt.style.opacity = 0; }};
document.querySelectorAll('[data-tip]').forEach(el => {{
  el.addEventListener('mouseenter', ev => {{
    suppressed = false; mx = ev.clientX; my = ev.clientY;
    clearTimeout(showTimer);
    showTimer = setTimeout(() => {{
      if (suppressed) return;
      tt.textContent = el.dataset.tip; place(); tt.style.opacity = 1;
      clearTimeout(fadeTimer);
      fadeTimer = setTimeout(() => tt.style.opacity = 0, 6000);
    }}, 250);
  }});
  el.addEventListener('mousemove', ev => {{ mx = ev.clientX; my = ev.clientY; if (!suppressed && tt.style.opacity == 1) place(); }});
  el.addEventListener('mouseleave', hideTip);
}});
document.addEventListener('click', () => {{ suppressed = true; hideTip(); }});
document.addEventListener('keydown', ev => {{ if (ev.key === 'Escape') {{ suppressed = true; hideTip(); }} }});
// Single-edge hover: tooltip only. On-canvas labels appear on NODE hover,
// annotating the whole fan of connected flows at once.
const lblOf = e => document.querySelector('.elbl[data-ei="' + e.dataset.ei + '"]');
document.querySelectorAll('.node').forEach(n => {{
  const id = n.dataset.id;
  const mine = [...document.querySelectorAll('.edge')].filter(e => e.dataset.from === id || e.dataset.to === id);
  n.addEventListener('mouseenter', () => mine.forEach(e => {{ e.classList.add('hi'); const l = lblOf(e); l && l.classList.add('show'); }}));
  n.addEventListener('mouseleave', () => mine.forEach(e => {{ e.classList.remove('hi'); const l = lblOf(e); l && l.classList.remove('show'); }}));
}});
</script>
</body></html>"""


# ── CLI ──────────────────────────────────────────────────────────────────────
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Render a Praxen threat-model graph JSON to a self-contained HTML report.")
    ap.add_argument("--graph", required=True, metavar="PATH",
                    help="threat-model graph JSON (extraction output)")
    ap.add_argument("--template", required=True, metavar="PATH",
                    help="report_template.html (brand single-source)")
    ap.add_argument("--out-html", dest="out_html", required=True, metavar="PATH",
                    help="write the rendered HTML report here")
    args = ap.parse_args(argv)

    with open(args.graph, encoding="utf-8") as f:
        graph = json.load(f)
    with open(args.template, encoding="utf-8") as f:
        template_text = f.read()
    try:
        out = render(graph, template_text)
    except (SchemaError, RenderError) as e:
        print(f"render_threatmodel: {e}", file=sys.stderr)
        return 1
    with open(args.out_html, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"wrote {args.out_html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
