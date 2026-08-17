#!/usr/bin/env python3
"""Phase-0 probe renderer: threat-model graph JSON -> self-contained HTML/SVG.

Throwaway code — proves the deterministic lane-layout bet, nothing more.
Usage: python3 render_probe.py <graph.json> <out.html>
"""
import json, sys, html

LANES = ["user_inputs", "client_adapters", "agent_core", "tools_mcp", "external_deploy"]
LANE_TITLES = {
    "user_inputs": "User / Inputs",
    "client_adapters": "Client / Adapters",
    "agent_core": "Agent Core",
    "tools_mcp": "Tools / MCP",
    "external_deploy": "External / Deploy",
}
# Praxen report brand palette (mirrors report_template.html :root).
# Orange is chrome-only (masthead/footer rules), never data — same rule as
# the analysis report. Severity semantics: residual=red, finding=amber,
# mitigated=green.
# Color carries FAMILY (6, trackable); the icon carries the exact KIND.
KIND_COLOR = {
    "entrypoint": "#8D00FF",
    "client": "#006BFF", "adapter": "#006BFF",
    "orchestrator": "#003FCC", "model": "#003FCC", "prompt": "#003FCC", "memory": "#003FCC",
    "tool": "#009D00", "mcp_server": "#009D00", "datastore": "#009D00",
    "control": "#D4A017",
    "external_service": "#6C757D", "deploy_surface": "#6C757D",
    "secret_store": "#6C757D", "log_sink": "#6C757D",
}
FAMILIES = [("actors & inputs", "#8D00FF"), ("client / adapters", "#006BFF"),
            ("agent core", "#003FCC"), ("tools & data", "#009D00"),
            ("controls", "#D4A017"), ("external & deploy", "#6C757D")]
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
def icon_svg(kind, color, size=18):
    p = ICONS.get(kind, "")
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" '
            f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{p}</svg>')
STATUS_COLOR = {"finding": "#E67E00", "mitigated": "#009D00", "residual": "#C0392B"}
COVERAGE_COLOR = {"verified": "#009D00", "partial": "#D4A017", "gap": "#C0392B",
                  "vague": "#6C757D", "enp": "#6C757D"}

COL_W, COL_GAP, MARGIN_X, TOP_Y = 250, 110, 30, 70
NODE_GAP = 22

def wrap(text, width=30):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur: lines.append(cur)
    return lines[:3]

def esc(s): return html.escape(str(s), quote=True)

def load_brand():
    """Extract the masthead/footer logo lockups from the shipping report
    template so the threat model wears the same chrome. Falls back to a text
    wordmark when the template isn't found (standalone use)."""
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    for up in ("../..", "../../..", "."):
        p = os.path.join(here, up, "skills/behavior-verifier/report_template.html")
        if os.path.exists(p):
            t = open(p).read()
            def block(start):
                i = t.find(start)
                if i < 0: return None
                j = t.find("</svg></div>", i)
                return t[i:j + len("</svg></div>")] if j > 0 else None
            mh = block('<div class="masthead-logo">')
            ft = block('<div class="footer-logo">')
            if mh and ft: return mh, ft
    w = '<div class="masthead-logo" style="color:#fff;font-weight:800;font-size:26px">PRAXEN</div>'
    return w, w.replace("masthead-logo", "footer-logo")

def main(graph_path, out_path):
    g = json.load(open(graph_path))
    nodes = {n["id"]: n for n in g["nodes"]}
    warnings = []

    # --- validation (probe diagnostics) ---
    for e in g["edges"]:
        for ref in (e["from"], e["to"]):
            if ref not in nodes:
                warnings.append(f"edge {e.get('id','?')} references unknown node '{ref}'")
    edge_ids = {e.get("id") for e in g["edges"]}
    for b in g.get("trust_boundaries", []):
        for ce in b.get("crossing_edges", []):
            if ce not in edge_ids:
                warnings.append(f"boundary {b['id']} references unknown edge '{ce}'")
    for n in g["nodes"]:
        if n.get("lane") not in LANES:
            warnings.append(f"node {n['id']} has unknown lane '{n.get('lane')}'")
        if not n.get("evidence"):
            warnings.append(f"node {n['id']} has NO evidence")

    # --- layout ---
    lane_x = {ln: MARGIN_X + i * (COL_W + COL_GAP) for i, ln in enumerate(LANES)}
    # barycenter ordering: sort each lane's nodes by mean neighbor position to
    # cut edge crossings; a few alternating sweeps is plenty at this scale.
    lane_of = {n["id"]: (n.get("lane") if n.get("lane") in LANES else "agent_core") for n in g["nodes"]}
    neigh = {n["id"]: [] for n in g["nodes"]}
    for e in g["edges"]:
        if e["from"] in neigh and e["to"] in neigh:
            neigh[e["from"]].append(e["to"]); neigh[e["to"]].append(e["from"])
    order = {ln: [n["id"] for n in g["nodes"] if lane_of[n["id"]] == ln] for ln in LANES}
    for _ in range(4):
        rank = {}
        for ln in LANES:
            for i, nid in enumerate(order[ln]): rank[nid] = i
        for ln in LANES:
            order[ln].sort(key=lambda nid: (sum(rank[m] for m in neigh[nid]) / len(neigh[nid])) if neigh[nid] else rank[nid])
    node_by_id = {n["id"]: n for n in g["nodes"]}
    pos, lane_y = {}, {ln: TOP_Y + 30 for ln in LANES}
    for ln in LANES:
        for nid in order[ln]:
            n = node_by_id[nid]
            lines = wrap(n["name"])
            h = 30 + 14 * len(lines) + 14  # name lines + kind chip
            pos[nid] = (lane_x[ln], lane_y[ln], h, lines)
            lane_y[ln] += h + NODE_GAP
    total_h = max(lane_y.values()) + 40
    total_w = MARGIN_X * 2 + 5 * COL_W + 4 * COL_GAP

    # --- edge ports: stagger attachment points down each node side so hub
    # nodes fan out instead of emitting overlapping curves from mid-height ---
    side_edges = {}  # (node id, 'L'|'R') -> [edge ids]
    def side_of(e, which):
        fl, tl = LANES.index(lane_of[e["from"]]), LANES.index(lane_of[e["to"]])
        if which == "from":
            return "R" if tl >= fl else "L"
        return "L" if tl >= fl else "R"
    for e in g["edges"]:
        if e["from"] not in pos or e["to"] not in pos: continue
        side_edges.setdefault((e["from"], side_of(e, "from")), []).append(e["id"])
        side_edges.setdefault((e["to"], side_of(e, "to")), []).append(e["id"])
    def other_y(e, nid):
        oid = e["to"] if e["from"] == nid else e["from"]
        return pos[oid][1]
    edge_by_id_tmp = {e["id"]: e for e in g["edges"]}
    port = {}  # (edge id, node id) -> y
    for (nid, sd), eids in side_edges.items():
        eids.sort(key=lambda eid: other_y(edge_by_id_tmp[eid], nid))
        x, y, h, _ = pos[nid]
        for i, eid in enumerate(eids):
            port[(eid, nid)] = y + h * (i + 1) / (len(eids) + 1)

    svg = []
    # lane backgrounds + titles
    for ln in LANES:
        x = lane_x[ln]
        svg.append(f'<rect x="{x-10}" y="{TOP_Y-30}" width="{COL_W+20}" height="{total_h-TOP_Y+10}" rx="10" fill="#FFFFFF" stroke="#E1E4E8"/>')
        svg.append(f'<text x="{x+COL_W/2}" y="{TOP_Y-8}" text-anchor="middle" font-size="13" font-weight="700" fill="#3A4A6B">{esc(LANE_TITLES[ln])}</text>')

    # boundary lines: place at the modal lane-gap crossed by its edges
    def gap_of_edge(e):
        f, t = pos.get(e["from"]), pos.get(e["to"])
        if not f or not t: return None
        fi = LANES.index(nodes[e["from"]].get("lane", "agent_core"))
        ti = LANES.index(nodes[e["to"]].get("lane", "agent_core"))
        lo, hi = sorted((fi, ti))
        return lo if hi > lo else None  # gap index to the right of lane lo
    edge_by_id = {e.get("id"): e for e in g["edges"]}
    bnd_at_gap = {}
    for b in g.get("trust_boundaries", []):
        gaps = [gap_of_edge(edge_by_id[c]) for c in b.get("crossing_edges", []) if c in edge_by_id]
        gaps = [x for x in gaps if x is not None]
        gap = max(set(gaps), key=gaps.count) if gaps else 1
        worst = "mitigated"
        for t in b.get("threats", []):
            if t.get("status") == "residual": worst = "residual"; break
            if t.get("status") == "finding": worst = "finding"
        bnd_at_gap.setdefault(gap, []).append((b, worst))
    bnd_num = {}  # boundary id -> B<n>, in declaration order
    for i, b in enumerate(g.get("trust_boundaries", []), 1):
        bnd_num[b["id"]] = f"B{i}"
    for gap, blist in bnd_at_gap.items():
        for j, (b, worst) in enumerate(blist):
            x = MARGIN_X + (gap + 1) * COL_W + gap * COL_GAP + COL_GAP / 2 + (j - (len(blist)-1)/2) * 16
            c = STATUS_COLOR[worst]
            num = bnd_num[b["id"]]
            # numbered badge at a staggered height instead of a text label:
            # full name lives in the tooltip and the B<n> panel below.
            by = TOP_Y - 22 + (j % 4) * 26
            btip = f'{num} — {b["name"]} · {len(b.get("threats",[]))} threats · {len(b.get("remit_rules",[]))} remit rules (details below)'
            svg.append(f'<g class="bnd" data-tip="{esc(btip)}">')
            svg.append(f'<line x1="{x}" y1="{TOP_Y-30}" x2="{x}" y2="{total_h-20}" stroke="{c}" stroke-width="2" stroke-dasharray="7 5" opacity="0.75"/>')
            svg.append(f'<circle cx="{x}" cy="{by}" r="11" fill="{c}"/>'
                       f'<text x="{x}" y="{by+4}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#fff">{esc(num)}</text>')
            svg.append('</g>')

    # edges — each in a <g class="edge">: invisible fat hit-path underneath for
    # easy hovering, visible path, and a label that appears only on hover.
    # Tooltip carries the full from -> to story. data-from/data-to feed the
    # node-hover highlighting script.
    svg.append('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#3A4A6B"/></marker>'
               '<marker id="arr-hi" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#006BFF"/></marker>'
               '<marker id="arr-path" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#C0392B"/></marker></defs>')
    loop_count = {}
    elbls = []   # edge labels render in a top layer AFTER nodes so boxes
    ei = 0       # never paint over them; linked to edges via data-ei
    edge_d = {}  # (from,to) -> path d, for the static attack-path overlay
    for e in g["edges"]:
        f, t = pos.get(e["from"]), pos.get(e["to"])
        if not f or not t: continue
        fy = port.get((e["id"], e["from"]), f[1] + f[2] / 2)
        ty = port.get((e["id"], e["to"]), t[1] + t[2] / 2)
        fx, tx = f[0], t[0]
        span = abs(LANES.index(lane_of[e["to"]]) - LANES.index(lane_of[e["from"]]))
        if fx < tx:   x1, x2 = fx + COL_W, tx
        elif fx > tx: x1, x2 = fx, tx + COL_W
        else:  # same lane: side loop, offset per loop so they don't stack
            x1 = x2 = fx + COL_W
            k = loop_count.get(e["from"], 0); loop_count[e["from"]] = k + 1
            mx = x1 + 36 + 20 * k
            d = f"M{x1} {fy} C {mx} {fy}, {mx} {ty}, {x2} {ty}"
            fnn = esc(nodes[e["from"]]["name"]); tnn = esc(nodes[e["to"]]["name"])
            lbl0 = esc(e.get("label", ""))
            tip0 = f'{fnn} → {tnn}: {lbl0}' + (f' [{esc(e["data"])}]' if e.get("data") else "")
            svg.append(f'<g class="edge" data-ei="{ei}" data-from="{esc(e["from"])}" data-to="{esc(e["to"])}" data-tip="{tip0}">')
            svg.append(f'<path class="hit" d="{d}" fill="none" stroke="transparent" stroke-width="9"/>')
            edge_d[(e["from"], e["to"])] = d
            svg.append(f'<path class="vis" d="{d}" fill="none" stroke="#3A4A6B" stroke-width="1.2" marker-end="url(#arr)" opacity="0.4"/>')
            svg.append('</g>')
            elbls.append(f'<text class="elbl" data-ei="{ei}" x="{mx+6}" y="{(fy+ty)/2}" text-anchor="middle" font-size="10.5" font-weight="600" fill="#003FCC" paint-order="stroke" stroke="#FFFFFF" stroke-width="3.5">{lbl0}</text>')
            ei += 1
            continue
        mx = (x1 + x2) / 2
        if span >= 2:
            # lane-skipper: bow the curve vertically so it arcs around the
            # intermediate columns instead of plowing through them.
            dip = 55 * (span - 1) * (1 if (fy + ty) / 2 > (total_h + TOP_Y) / 2 else -1)
            cy1, cy2 = fy + dip, ty + dip
            d = f"M{x1} {fy} C {x1 + 90} {cy1}, {x2 - 90} {cy2}, {x2} {ty}"
        else:
            d = f"M{x1} {fy} C {mx} {fy}, {mx} {ty}, {x2} {ty}"
        fn = esc(nodes[e["from"]]["name"]); tn = esc(nodes[e["to"]]["name"])
        lbl = esc(e.get("label", ""))
        tip = f'{fn} → {tn}: {lbl}' + (f' [{esc(e["data"])}]' if e.get("data") else "")
        dim = ' style="opacity:.22"' if span >= 2 else ''
        svg.append(f'<g class="edge" data-ei="{ei}" data-from="{esc(e["from"])}" data-to="{esc(e["to"])}" data-tip="{tip}">')
        svg.append(f'<path class="hit" d="{d}" fill="none" stroke="transparent" stroke-width="9"/>')
        edge_d[(e["from"], e["to"])] = d
        svg.append(f'<path class="vis" d="{d}" fill="none" stroke="#3A4A6B" stroke-width="1.2" marker-end="url(#arr)" opacity="0.4"{dim}/>')
        svg.append('</g>')
        # cross-lane labels rotate 90° to run along the (narrow) lane gap
        ly_mid = (fy + ty) / 2 + (55 * (span - 1) * (1 if (fy + ty) / 2 > (total_h + TOP_Y) / 2 else -1) * 0.75 if span >= 2 else 0)
        elbls.append(f'<text class="elbl" data-ei="{ei}" x="{mx - 4}" y="{ly_mid}" text-anchor="middle" font-size="10.5" font-weight="600" fill="#003FCC" paint-order="stroke" stroke="#FFFFFF" stroke-width="3.5" transform="rotate(-90 {mx - 4} {ly_mid})">{lbl}</text>')
        ei += 1

    # attack-path badges (first path only, numbered)
    ap = g.get("attack_paths", [])
    badge_at = {}
    if ap:
        for i, step in enumerate(ap[0].get("steps", []), 1):
            if step.get("node") in pos: badge_at[step["node"]] = i

    # nodes
    for n in g["nodes"]:
        x, y, h, lines = pos[n["id"]]
        c = KIND_COLOR.get(n.get("kind"), "#666")
        tip = esc(n.get("description", "")) + " | evidence: " + esc("; ".join(
            f"{ev.get('file')}:{ev.get('line','-')}" for ev in n.get("evidence", [])[:4]))
        if n["id"] in badge_at and ap:
            tip += esc(f' | ⚔ attack-path step {badge_at[n["id"]]} of {len(ap[0].get("steps",[]))}: “{ap[0].get("name","")}”')
        svg.append(f'<g class="node" data-id="{esc(n["id"])}" data-tip="{tip}">')
        svg.append(f'<rect x="{x}" y="{y}" width="{COL_W}" height="{h}" rx="8" fill="#fff" stroke="{c}" stroke-width="1.6"/>')
        svg.append(f'<rect x="{x}" y="{y}" width="5" height="{h}" rx="2.5" fill="{c}"/>')
        for li, line in enumerate(lines):
            svg.append(f'<text x="{x+14}" y="{y+20+14*li}" font-size="12" font-weight="600" fill="#0D1B2A">{esc(line)}</text>')
        svg.append(f'<text x="{x+14}" y="{y+h-8}" font-size="9.5" fill="{c}" font-weight="600">{esc(n.get("kind","?").upper())}</text>')
        ic = ICONS.get(n.get("kind"), "")
        if ic:
            svg.append(f'<g transform="translate({x+COL_W-26},{y+7}) scale(0.75)" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ic}</g>')
        if n["id"] in badge_at:
            svg.append(f'<circle cx="{x+COL_W-14}" cy="{y+h-13}" r="10" fill="#C0392B"/>'
                       f'<text x="{x+COL_W-14}" y="{y+h-9}" text-anchor="middle" font-size="11" font-weight="700" fill="#fff">{badge_at[n["id"]]}</text>')
        svg.append('</g>')
    # static overlay: the badged (first) attack path drawn as a bold route so
    # the meaningful connections read without any interaction; other edges
    # recede. Consecutive steps with no direct edge are left to the badges.
    if ap:
        adj = {}
        for (a0, b0) in edge_d:
            adj.setdefault(a0, set()).add(b0); adj.setdefault(b0, set()).add(a0)
        def route(a, b, cap=4):
            # BFS through the flow graph: consecutive attack-path steps often
            # connect via a hub (harness, bridge) rather than a direct edge.
            from collections import deque
            q, seen = deque([[a]]), {a}
            while q:
                path = q.popleft()
                if len(path) > cap: continue
                for nx in adj.get(path[-1], ()):
                    if nx == b: return path + [b]
                    if nx not in seen:
                        seen.add(nx); q.append(path + [nx])
            return None
        steps = [st.get("node") for st in ap[0].get("steps", []) if st.get("node") in pos]
        hop_pairs = set()
        for a, b in zip(steps, steps[1:]):
            r = route(a, b)
            if r:
                for h1, h2 in zip(r, r[1:]): hop_pairs.add((h1, h2))
        for (a, b) in hop_pairs:
            d_ab = edge_d.get((a, b)) or edge_d.get((b, a))
            if d_ab:
                svg.append(f'<path d="{d_ab}" fill="none" stroke="#C0392B" stroke-width="2.6" opacity="0.8" marker-end="url(#arr-path)"/>')
    svg.append('<g class="lblLayer">' + "".join(elbls) + '</g>')

    # --- HTML panels below the diagram ---
    def chip(text, color):
        return f'<span style="background:{color};color:#fff;border-radius:4px;padding:1px 7px;font-size:11px;font-weight:600">{esc(text)}</span>'

    panels = []
    for b in g.get("trust_boundaries", []):
        rows = []
        for t in b.get("threats", []):
            fid = t.get("finding_id") or ""
            rows.append(f'<tr><td>{esc(t.get("stride","?"))}</td><td>{esc(t.get("owasp") or "—")}</td>'
                        f'<td>{esc(t.get("summary",""))}</td>'
                        f'<td>{chip(t.get("status","?"), STATUS_COLOR.get(t.get("status"), "#666"))} {esc(fid)}</td></tr>')
        remits = " ".join(
            chip(f'{r.get("rule_id","R-?")} {r.get("coverage_status","?")}',
                 COVERAGE_COLOR.get(r.get("coverage_status"), "#666")) +
            f' <span class="rx">{esc(r.get("excerpt",""))}</span><br>'
            for r in b.get("remit_rules", []))
        panels.append(f"""<details open><summary><b>{bnd_num.get(b["id"],"")} — {esc(b["name"])}</b> — {len(b.get("threats",[]))} threats, {len(b.get("remit_rules",[]))} remit rules</summary>
<div class="remits">{remits or "<i>the remit does not touch this boundary — threats here are assessed against the RAISE/OWASP baseline alone (a remit is a job description, not a security model; silence here is normal)</i>"}</div>
<table><tr><th>STRIDE</th><th>OWASP</th><th>Threat</th><th>Status</th></tr>{"".join(rows)}</table></details>""")

    appanels = []
    for p in ap:
        steps = " → ".join(
            f'<b>{esc(nodes.get(s.get("node"), {}).get("name", s.get("node")))}</b>'
            + (f' <span class="fid">[{esc(s["finding_id"])}]</span>' if s.get("finding_id") else "")
            + f' <span class="rx">{esc(s.get("summary",""))}</span>'
            for s in p.get("steps", []))
        appanels.append(f'<div class="ap">⚔ <b>{esc(p.get("name",""))}</b>: {steps}</div>')

    notes = g.get("notes", {})
    warn_html = "".join(f"<li>{esc(w)}</li>" for w in warnings) or "<li>none — all refs resolve, all nodes cited</li>"

    kinds_present = []
    for n in g["nodes"]:
        k = n.get("kind")
        if k not in kinds_present: kinds_present.append(k)
    fam_present = set(KIND_COLOR.get(k, "#666") for k in kinds_present)
    row1 = "".join(f'<span class="lg"><i style="background:#fff;border:2px solid {c};border-left:5px solid {c}"></i>{esc(nm)}</span>'
                   for nm, c in FAMILIES if c in fam_present)
    row2 = "".join(f'<span class="lg">{icon_svg(k, KIND_COLOR.get(k, "#666"), 16)}{esc(k.replace("_", " "))}</span>'
                   for k in kinds_present)
    row3 = "".join([
        '<span class="lg"><i class="lg-dash" style="border-color:#C0392B"></i>boundary — worst threat residual</span>',
        '<span class="lg"><i class="lg-dash" style="border-color:#E67E00"></i>— finding</span>',
        '<span class="lg"><i class="lg-dash" style="border-color:#009D00"></i>— mitigated</span>',
        '<span class="lg"><i style="background:none;border-top:3px solid #C0392B;height:0;border-radius:0"></i>attack-path route</span>',
        '<span class="lg"><b class="lg-b" style="background:#C0392B">1</b>attack-path step</span>',
        '<span class="lg"><i class="lg-arc"></i>faint arc = flow spanning 2+ lanes</span>',
    ])
    legend_html = (f'<div class="lg-row"><span class="lg-cap">Families</span>{row1}</div>'
                   f'<div class="lg-row"><span class="lg-cap">Kinds</span>{row2}</div>'
                   f'<div class="lg-row"><span class="lg-cap">Marks</span>{row3}</div>')

    # static boundary key — the B-badges resolved on paper, no hover needed
    bnd_num_pre = {b["id"]: f"B{i}" for i, b in enumerate(g.get("trust_boundaries", []), 1)}
    bk_rows = []
    for b in g.get("trust_boundaries", []):
        worst = "mitigated"
        for t in b.get("threats", []):
            if t.get("status") == "residual": worst = "residual"; break
            if t.get("status") == "finding": worst = "finding"
        c = STATUS_COLOR[worst]
        bk_rows.append(f'<tr><td><b class="lg-b" style="background:{c}">{bnd_num_pre[b["id"]]}</b></td>'
                       f'<td><b>{esc(b["name"])}</b> <span class="rx">({esc(b["id"])})</span></td>'
                       f'<td>{len(b.get("threats", []))}</td><td>{len(b.get("remit_rules", []))}</td>'
                       f'<td style="color:{c};font-weight:700">{worst}</td></tr>')
    boundary_key_html = ('<table class="bk"><tr><th></th><th>Trust boundary</th><th>Threats</th>'
                         '<th>Remit rules</th><th>Worst status</th></tr>' + "".join(bk_rows) + '</table>')

    # component inventory appendix — node evidence on paper, not only in tooltips
    inv_rows = []
    for n in g["nodes"]:
        evs = "; ".join(f'{ev.get("file")}:{ev.get("line", "—")}' for ev in n.get("evidence", [])[:2])
        c = KIND_COLOR.get(n.get("kind"), "#666")
        inv_rows.append(f'<tr><td style="white-space:nowrap">{icon_svg(n.get("kind"), c, 14)} <b>{esc(n["name"])}</b></td>'
                        f'<td>{esc(n.get("kind", ""))}</td><td>{esc(n.get("lane", ""))}</td>'
                        f'<td>{esc(n.get("description", ""))}</td><td class="rx">{esc(evs)}</td></tr>')
    inventory_html = ('<table><tr><th>Component</th><th>Kind</th><th>Lane</th><th>Description</th>'
                      '<th>Evidence</th></tr>' + "".join(inv_rows) + '</table>')
    mh_logo, ft_logo = load_brand()
    n_res = sum(1 for b in g.get("trust_boundaries", []) for t in b.get("threats", []) if t.get("status") == "residual")
    n_fin = sum(1 for b in g.get("trust_boundaries", []) for t in b.get("threats", []) if t.get("status") == "finding")
    n_mit = sum(1 for b in g.get("trust_boundaries", []) for t in b.get("threats", []) if t.get("status") == "mitigated")
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Praxen Threat Model — {esc(g["target"]["slug"])}</title>
<style>
 :root {{ --orange:#FF7A2E; --orange-2:#FF9D4D; --navy:#0D1B2A; --text:#0D1B2A; --text-muted:#3A4A6B;
   --bg:#FFFFFF; --surface:#F5F7FA; --surface-alt:#F0F4FF; --border:#E1E4E8; --border-alt:#C8D4F0;
   --blue:#006BFF; --blue-dark:#003FCC; --green:#009D00;
   --sev-critical:#C0392B; --sev-high:#E67E00; --sev-medium:#D4A017; --sev-low:#6C757D; }}
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
 .mh-metric.mh-res > b {{ color:#FF7A6B; }} .mh-metric.mh-fin > b {{ color:#FFB066; }} .mh-metric.mh-mit > b {{ color:#4CDB00; }}
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
 .diag {{ font-size:12px; color:var(--text-muted); }} .diag ul {{ margin:6px 0 0 18px; }}
 .elbl {{ opacity:0; pointer-events:none; transition:opacity .1s; }}
 .elbl.show {{ opacity:1; }}
 .legend {{ font-size:11.5px; color:var(--text-muted); }}
 .legend .lg-row {{ display:flex; flex-wrap:wrap; gap:6px 16px; align-items:center; padding:3px 0; }}
 .legend .lg-cap {{ font-size:10px; font-weight:800; letter-spacing:0.1em; text-transform:uppercase; color:#8A97A8; width:58px; flex-shrink:0; }}
 .legend .lg svg {{ display:inline-block; vertical-align:middle; }}
 .bk {{ margin-top:14px; }} .bk td, .bk th {{ padding:4px 9px; }}
 @media print {{
   .elbl {{ opacity:1 !important; }}
   #tt {{ display:none; }}
   .svgwrap {{ overflow:visible; border:none; padding:0; }}
   .svgwrap svg {{ max-width:100%; height:auto; }}
   details {{ page-break-inside:avoid; }} details:not([open]) {{ display:block; }}
   .section {{ page-break-inside:avoid; }}
 }}
 .legend .lg {{ display:inline-flex; align-items:center; gap:6px; }}
 .legend .lg i {{ display:inline-block; width:20px; height:12px; border-radius:3px; }}
 .legend .lg i.lg-dash {{ width:22px; height:0; border-top:2px dashed; border-radius:0; background:none; }}
 .legend .lg i.lg-arc {{ width:22px; height:8px; border:1.5px solid #3A4A6B; border-bottom:none; border-radius:11px 11px 0 0; opacity:.4; background:none; }}
 b.lg-b {{ display:inline-flex; align-items:center; justify-content:center; min-width:20px; height:20px; padding:0 3px; border-radius:10px; background:#E67E00; color:#fff; font-size:10px; font-weight:700; }}
 .edge:hover .vis, .edge.hi .vis {{ stroke:var(--blue); stroke-width:2.6; opacity:1 !important; marker-end:url(#arr-hi); }}
 .node:hover rect:first-of-type {{ filter:drop-shadow(0 0 4px rgba(0,107,255,.55)); cursor:default; }}
 .bnd:hover line {{ opacity:1; stroke-width:3; }} .bnd {{ cursor:default; }}
 #tt {{ position:fixed; background:var(--navy); color:#F5F7FA; padding:7px 11px; border-radius:7px; font-size:12.5px; line-height:1.45; max-width:380px; pointer-events:none; opacity:0; z-index:10; box-shadow:0 3px 10px rgba(13,27,42,.35); transition:opacity .08s; }}
 .footer {{ background:var(--navy); border-top:4px solid var(--orange); margin-top:40px; padding:18px 32px; color:#8BAFC8; }}
 .footer .rf-row {{ display:flex; justify-content:space-between; align-items:center; gap:24px; flex-wrap:wrap; }}
 .footer .footer-logo svg {{ height:34px; width:auto; display:block; }}
 .footer .rf-gh {{ display:inline-flex; align-items:center; gap:8px; color:#CDD8E4; text-decoration:none; font-size:13.5px; font-weight:600; border:1px solid #2A3D57; border-radius:8px; padding:7px 13px; }}
 .footer .rf-gh:hover {{ border-color:var(--orange); color:#FFF; }}
 .footer .rf-legal {{ font-size:11.5px; color:#6E7F92; line-height:1.6; text-align:right; }}
</style></head><body>
<div class="masthead"><div class="masthead-main">
  <div>{mh_logo}
    <div class="masthead-agent">{esc(g["target"]["slug"])}</div>
    <div class="masthead-kind">Threat Model · probe</div>
    <div class="masthead-date">evidence-derived · spec {esc(g.get("spec_version","?"))}</div>
  </div>
  <div class="masthead-summary">
    <div class="masthead-metrics">
      <div class="mh-metric"><b>{len(g["nodes"])}</b><span>Components</span></div>
      <div class="mh-metric"><b>{len(g["edges"])}</b><span>Flows</span></div>
      <div class="mh-metric"><b>{len(g.get("trust_boundaries",[]))}</b><span>Boundaries</span></div>
      <div class="mh-metric mh-fin"><b>{n_fin}</b><span>Findings</span></div>
      <div class="mh-metric mh-res"><b>{n_res}</b><span>Residual</span></div>
      <div class="mh-metric mh-mit"><b>{n_mit}</b><span>Mitigated</span></div>
    </div>
  </div>
</div></div>
<div class="content">
<div class="section section-fullbleed">
<div class="section-title">Architecture &amp; Trust Boundaries</div>
<div class="section-desc" style="max-width:1100px;margin-left:auto;margin-right:auto">Every component, flow, and boundary cites evidence — hover nodes for citations, edges for what flows, and B-badges for boundary detail. Dimmed long arcs span multiple lanes. PROBE ARTIFACT, not a product report.</div>
<div class="svgwrap"><svg width="{total_w}" height="{total_h}" viewBox="0 0 {total_w} {total_h}" xmlns="http://www.w3.org/2000/svg">{"".join(svg)}</svg></div>
<div class="legend" style="max-width:1100px;margin:12px auto 0">{legend_html}</div>
<div style="max-width:1100px;margin:0 auto">{boundary_key_html}</div>
</div>
<div class="section"><div class="section-title">Attack Paths</div>{"".join(appanels) or "<div class='diag'>none grounded in findings</div>"}</div>
<div class="section"><div class="section-title">Trust Boundaries — Threats &amp; Governing Remit Rules</div>{"".join(panels)}</div>
<div class="section"><div class="section-title">Component Inventory</div>
<div class="section-desc">Every component with its kind, lane, and source evidence — the diagram's tooltips, on paper.</div>{inventory_html}</div>
<div class="section"><div class="section-title">Probe Diagnostics</div>
<div class="diag">lane_fit: {esc(notes.get("lane_fit",""))}<br>omissions: {esc(notes.get("omissions",""))}<br>model: {esc(g.get("model_identity",""))}<ul>{warn_html}</ul></div></div>
</div>
<div class="footer"><div class="rf-row">
  {ft_logo}
  <a class="rf-gh" href="https://github.com/open-agent-ai-security/praxen"><span>github.com/open-agent-ai-security/praxen</span></a>
  <div class="rf-legal">Praxen threat model — evidence-derived; every element cites source.<br>Probe renderer; not a released Praxen artifact.</div>
</div></div>
<div id="tt"></div>
<script>
const tt = document.getElementById('tt');
// Tooltip discipline: 250ms show-delay (deliberate dwell, not traversal),
// click anywhere dismisses (until you enter a different element), and a
// 6s dwell auto-fade so it never parks on screen indefinitely.
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
const lblOf = e => document.querySelector('.elbl[data-ei="' + e.dataset.ei + '"]');
// Single-edge hover: tooltip only (it carries the label + endpoints + data).
// On-canvas labels appear only on NODE hover, where they annotate the whole
// fan of connected flows at once — something the one-at-a-time tooltip can't.
document.querySelectorAll('.node').forEach(n => {{
  const id = n.dataset.id;
  const mine = [...document.querySelectorAll('.edge')].filter(e => e.dataset.from === id || e.dataset.to === id);
  n.addEventListener('mouseenter', () => mine.forEach(e => {{ e.classList.add('hi'); const l = lblOf(e); l && l.classList.add('show'); }}));
  n.addEventListener('mouseleave', () => mine.forEach(e => {{ e.classList.remove('hi'); const l = lblOf(e); l && l.classList.remove('show'); }}));
}});
</script>
</body></html>"""
    open(out_path, "w").write(doc)
    print(f"wrote {out_path}  ({len(g['nodes'])} nodes, {len(g['edges'])} edges, "
          f"{len(g.get('trust_boundaries',[]))} boundaries, {len(warnings)} warnings)")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
