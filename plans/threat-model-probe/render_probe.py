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
KIND_COLOR = {
    "entrypoint": "#7c5cbf", "client": "#4a7fb5", "adapter": "#4a7fb5",
    "orchestrator": "#2e6f6c", "model": "#2e6f6c", "prompt": "#8a6d3b",
    "memory": "#8a6d3b", "datastore": "#8a6d3b", "tool": "#3d7a46",
    "mcp_server": "#3d7a46", "control": "#b0762a", "external_service": "#6d6d6d",
    "deploy_surface": "#a04848", "secret_store": "#a04848", "log_sink": "#6d6d6d",
}
STATUS_COLOR = {"finding": "#c9542c", "mitigated": "#3d7a46", "residual": "#b03030"}
COVERAGE_COLOR = {"verified": "#3d7a46", "partial": "#b0762a", "gap": "#b03030",
                  "vague": "#8a6d3b", "enp": "#6d6d6d"}

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
        svg.append(f'<rect x="{x-10}" y="{TOP_Y-30}" width="{COL_W+20}" height="{total_h-TOP_Y+10}" rx="10" fill="#f2f0ec" stroke="#ddd8d0"/>')
        svg.append(f'<text x="{x+COL_W/2}" y="{TOP_Y-8}" text-anchor="middle" font-size="13" font-weight="700" fill="#555">{esc(LANE_TITLES[ln])}</text>')

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
    svg.append('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#7a756d"/></marker>'
               '<marker id="arr-hi" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#b03030"/></marker></defs>')
    loop_count = {}
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
            svg.append(f'<g class="edge" data-from="{esc(e["from"])}" data-to="{esc(e["to"])}" data-tip="{tip0}">')
            svg.append(f'<path class="hit" d="{d}" fill="none" stroke="transparent" stroke-width="14"/>')
            svg.append(f'<path class="vis" d="{d}" fill="none" stroke="#7a756d" stroke-width="1.4" marker-end="url(#arr)" opacity="0.55"/>')
            svg.append(f'<text class="elbl" x="{mx+6}" y="{(fy+ty)/2}" text-anchor="middle" font-size="10.5" font-weight="600" fill="#b03030" paint-order="stroke" stroke="#faf9f7" stroke-width="3.5">{lbl0}</text>')
            svg.append('</g>')
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
        dim = ' style="opacity:.35"' if span >= 2 else ''
        svg.append(f'<g class="edge" data-from="{esc(e["from"])}" data-to="{esc(e["to"])}" data-tip="{tip}">')
        svg.append(f'<path class="hit" d="{d}" fill="none" stroke="transparent" stroke-width="14"/>')
        svg.append(f'<path class="vis" d="{d}" fill="none" stroke="#7a756d" stroke-width="1.4" marker-end="url(#arr)" opacity="0.55"{dim}/>')
        # cross-lane labels rotate 90° to run along the (narrow) lane gap
        ly_mid = (fy + ty) / 2 + (55 * (span - 1) * (1 if (fy + ty) / 2 > (total_h + TOP_Y) / 2 else -1) * 0.75 if span >= 2 else 0)
        svg.append(f'<text class="elbl" x="{mx - 4}" y="{ly_mid}" text-anchor="middle" font-size="10.5" font-weight="600" fill="#b03030" paint-order="stroke" stroke="#faf9f7" stroke-width="3.5" transform="rotate(-90 {mx - 4} {ly_mid})">{lbl}</text>')
        svg.append('</g>')

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
        svg.append(f'<g class="node" data-id="{esc(n["id"])}" data-tip="{tip}">')
        svg.append(f'<rect x="{x}" y="{y}" width="{COL_W}" height="{h}" rx="8" fill="#fff" stroke="{c}" stroke-width="1.6"/>')
        svg.append(f'<rect x="{x}" y="{y}" width="5" height="{h}" rx="2.5" fill="{c}"/>')
        for li, line in enumerate(lines):
            svg.append(f'<text x="{x+14}" y="{y+20+14*li}" font-size="12" font-weight="600" fill="#2b2823">{esc(line)}</text>')
        svg.append(f'<text x="{x+14}" y="{y+h-8}" font-size="9.5" fill="{c}" font-weight="600">{esc(n.get("kind","?").upper())}</text>')
        if n["id"] in badge_at:
            svg.append(f'<circle cx="{x+COL_W-14}" cy="{y+14}" r="10" fill="#b03030"/>'
                       f'<text x="{x+COL_W-14}" y="{y+18}" text-anchor="middle" font-size="11" font-weight="700" fill="#fff">{badge_at[n["id"]]}</text>')
        svg.append('</g>')

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

    doc = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Threat model (probe) — {esc(g["target"]["slug"])}</title>
<style>
 body{{font-family:-apple-system,Segoe UI,sans-serif;background:#faf9f7;color:#2b2823;margin:24px;max-width:{total_w+40}px}}
 h1{{font-size:20px}} .sub{{color:#777;font-size:12.5px;margin-bottom:14px}}
 .svgwrap{{overflow-x:auto;border:1px solid #e2ddd5;border-radius:10px;background:#faf9f7;padding:8px}}
 details{{background:#fff;border:1px solid #e2ddd5;border-radius:8px;padding:10px 14px;margin:10px 0}}
 summary{{cursor:pointer}} table{{border-collapse:collapse;margin-top:8px;font-size:12.5px;width:100%}}
 th,td{{border:1px solid #e6e1d9;padding:4px 8px;text-align:left;vertical-align:top}}
 th{{background:#f2f0ec}} .remits{{margin:8px 0;font-size:12.5px;line-height:2}}
 .rx{{color:#6a655d;font-size:11.5px}} .fid{{color:#c9542c;font-weight:600;font-size:11.5px}}
 .ap{{background:#fff;border:1px solid #e2ddd5;border-left:4px solid #b03030;border-radius:8px;padding:10px 14px;margin:10px 0;font-size:13px}}
 .diag{{font-size:12px;color:#6a655d}} h2{{font-size:15px;margin-top:26px}}
 .edge .elbl{{opacity:0;pointer-events:none;transition:opacity .1s}}
 .edge:hover .elbl, .edge.hi .elbl{{opacity:1}}
 .edge:hover .vis, .edge.hi .vis{{stroke:#b03030;stroke-width:2.6;opacity:1 !important;marker-end:url(#arr-hi)}}
 .node:hover rect:first-of-type{{filter:drop-shadow(0 0 4px rgba(176,48,48,.5));cursor:default}}
 .bnd:hover line{{opacity:1;stroke-width:3}}
 #tt{{position:fixed;background:#2b2823;color:#faf9f7;padding:7px 11px;border-radius:7px;font-size:12.5px;line-height:1.45;max-width:380px;pointer-events:none;opacity:0;z-index:10;box-shadow:0 3px 10px rgba(0,0,0,.25);transition:opacity .08s}}
</style></head><body>
<h1>Threat model (probe v0.1) — {esc(g["target"]["slug"])}</h1>
<div class="sub">evidence-derived from {esc(g["target"].get("source_root",""))} · {len(g["nodes"])} components · {len(g["edges"])} flows · {len(g.get("trust_boundaries",[]))} trust boundaries · hover nodes for evidence citations · PROBE ARTIFACT, not a product report</div>
<div class="svgwrap"><svg width="{total_w}" height="{total_h}" viewBox="0 0 {total_w} {total_h}" xmlns="http://www.w3.org/2000/svg">{"".join(svg)}</svg></div>
<h2>Attack paths</h2>{"".join(appanels) or "<div class='diag'>none grounded in findings</div>"}
<h2>Trust boundaries — threats &amp; governing remit rules</h2>{"".join(panels)}
<h2>Probe diagnostics</h2>
<div class="diag">lane_fit: {esc(notes.get("lane_fit",""))}<br>omissions: {esc(notes.get("omissions",""))}<br>model: {esc(g.get("model_identity",""))}<ul>{warn_html}</ul></div>
<div id="tt"></div>
<script>
const tt = document.getElementById('tt');
document.querySelectorAll('[data-tip]').forEach(el => {{
  el.addEventListener('mousemove', ev => {{
    tt.textContent = el.dataset.tip;
    tt.style.opacity = 1;
    tt.style.left = Math.min(ev.clientX + 14, window.innerWidth - 400) + 'px';
    tt.style.top = (ev.clientY + 14) + 'px';
  }});
  el.addEventListener('mouseleave', () => tt.style.opacity = 0);
}});
document.querySelectorAll('.node').forEach(n => {{
  const id = n.dataset.id;
  const mine = [...document.querySelectorAll('.edge')].filter(e => e.dataset.from === id || e.dataset.to === id);
  n.addEventListener('mouseenter', () => mine.forEach(e => e.classList.add('hi')));
  n.addEventListener('mouseleave', () => mine.forEach(e => e.classList.remove('hi')));
}});
</script>
</body></html>"""
    open(out_path, "w").write(doc)
    print(f"wrote {out_path}  ({len(g['nodes'])} nodes, {len(g['edges'])} edges, "
          f"{len(g.get('trust_boundaries',[]))} boundaries, {len(warnings)} warnings)")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
