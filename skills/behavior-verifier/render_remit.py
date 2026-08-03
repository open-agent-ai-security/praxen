#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
render_remit.py — render a naked Worker Remit (Markdown) into a styled,
shareable HTML page that matches the Praxen analysis report's look.

A Worker Remit is authored and co-edited as plain Markdown (great for hand /
agent editing, poor for display and review). This is a *mechanical* translator:
Markdown in, one self-contained HTML file out. It reads no code and makes no
judgments — it only re-skins the remit you already have.

Brand chrome (the :root palette, the Praxen wordmark, the page footer) is
extracted at render time from the report template (`report_template.html`) so
the remit page and the analysis report share one source of styling. The remit
body and masthead are rendered by this script.

The output is deterministic: it carries the remit's own `Remit Version` /
`Last Updated` fields, never a wall-clock generation time, so re-rendering an
unchanged remit produces byte-identical HTML (and clean diffs / stable tests).

Usage:
    python render_remit.py REMIT.md [--out REMIT.html]
                                    [--template report_template.html]
                                    [--praxen-version X.Y.Z]

Defaults: --out is REMIT.md with a .html suffix; --template is the sibling
report_template.html; --praxen-version is read from .claude-plugin/plugin.json
(walked up from this script, then the cwd) when not given.
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path


class RemitRenderError(Exception):
    """Raised when the remit or the template cannot be rendered cleanly."""


# ── brand-chrome extraction (shared with the report template) ─────────────────
def _extract_between(text, open_pat, close, *, what):
    """Return the substring from the first `open_pat` match to the next `close`."""
    m = re.search(open_pat, text)
    if not m:
        raise RemitRenderError(f"template is missing {what} (no {open_pat!r})")
    idx = text.find(close, m.end())
    if idx == -1:
        raise RemitRenderError(f"template is missing the {close!r} that closes {what}")
    return text[m.start():idx + len(close)]


def extract_chrome(template_html):
    """Pull (brand <style>, wordmark <svg>, footer <div>) out of the report template."""
    # The head's brand stylesheet: the FIRST <style> block. SVG-local <style>
    # blocks live later in <body>, so the first open/close pair is the brand CSS.
    style = _extract_between(template_html, r"<style>", "</style>",
                             what="the brand <style> block")
    # The Praxen wordmark: the <svg> inside the masthead logo div. The SVG holds
    # no <div>, so a non-greedy match to the next </div> captures exactly it.
    logo_div = _extract_between(template_html, r'<div class="masthead-logo">', "</div>",
                                what="the masthead logo")
    logo_svg = logo_div[len('<div class="masthead-logo">'):-len("</div>")]
    # The page footer: <div class="footer"> … its last </div> BEFORE </body>.
    # Bounding the search to </body> keeps the greedy close from over-capturing an
    # element added after the footer; a missing marker raises rather than emits garbage.
    fstart = template_html.find('<div class="footer">')
    if fstart == -1:
        raise RemitRenderError('template is missing the footer (no <div class="footer">)')
    bend = template_html.find("</body>", fstart)
    if bend == -1:
        raise RemitRenderError("template is missing the </body> that bounds the footer")
    fclose = template_html.rfind("</div>", fstart, bend)
    if fclose == -1:
        raise RemitRenderError("template is missing the </div> that closes the footer")
    footer = template_html[fstart:fclose + len("</div>")]
    return style, logo_svg, footer


def _praxen_version(explicit, start_paths):
    if explicit:
        return explicit
    for start in start_paths:
        for base in [start, *start.parents]:
            cand = base / ".claude-plugin" / "plugin.json"
            if cand.is_file():
                try:
                    return json.loads(cand.read_text(encoding="utf-8"))["version"]
                except (ValueError, KeyError):
                    pass
    return ""


# ── inline Markdown → HTML ────────────────────────────────────────────────────
_CODE_RE = re.compile(r"`([^`]+)`")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_ITAL_RE = re.compile(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])")


def inline(text):
    """Escape HTML, then apply `code`, **bold**, *italic* (code taken first)."""
    out, last = [], 0
    for m in _CODE_RE.finditer(text):
        out.append(_emphasis(html.escape(text[last:m.start()])))
        out.append("<code>" + html.escape(m.group(1)) + "</code>")
        last = m.end()
    out.append(_emphasis(html.escape(text[last:])))
    return "".join(out)


def _emphasis(escaped):
    escaped = _BOLD_RE.sub(r"<strong>\1</strong>", escaped)
    escaped = _ITAL_RE.sub(r"<em>\1</em>", escaped)
    return escaped


# ── block parsing ─────────────────────────────────────────────────────────────
COMMENT_RE = re.compile(r"<!--\s*(.*?)\s*-->", re.DOTALL)
BADGE_RE = re.compile(r"^(POLICY|CONTEXT)\b\s*(.*)$", re.DOTALL)


def _strip_leading_license(lines):
    """Drop a leading HTML comment block (the SPDX license header)."""
    i = 0
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i < len(lines) and lines[i].lstrip().startswith("<!--"):
        while i < len(lines) and "-->" not in lines[i]:
            i += 1
        i += 1  # consume the closing line
    return lines[i:]


def _render_blocks(lines):
    """Render a section's body lines (no headings) into HTML."""
    html_parts, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if stripped == "" or stripped == "---":
            i += 1
            continue
        # HTML comment → muted annotation note.
        if stripped.startswith("<!--"):
            buf = [line]
            while "-->" not in buf[-1] and i + 1 < n:
                i += 1
                buf.append(lines[i])
            m = COMMENT_RE.search("\n".join(buf))
            note = m.group(1).strip() if m else ""
            if note:
                html_parts.append(f'<p class="remit-note">{inline(note)}</p>')
            i += 1
            continue
        # Sub-headings — ### (h3) and #### (h4, used for paired-component sections).
        hm = re.match(r"^(#{3,6})\s+(.*)$", stripped)
        if hm:
            lvl = min(len(hm.group(1)), 4)  # h3, or h4 for deeper levels
            html_parts.append(f"<h{lvl}>{inline(hm.group(2).strip())}</h{lvl}>")
            i += 1
            continue
        # Table (a run of pipe rows).
        if stripped.startswith("|"):
            tbl, start = [], i
            while i < n and lines[i].strip().startswith("|"):
                tbl.append(lines[i].strip())
                i += 1
            html_parts.append(_render_table(tbl))
            continue
        # Bullet list (supports one level of nesting by indentation).
        if re.match(r"^\s*-\s+", line):
            block, base = [], i
            while i < n and (re.match(r"^\s*-\s+", lines[i]) or
                             (lines[i].strip() and lines[i].startswith(("  ", "\t"))
                              and not lines[i].strip().startswith(("|", "#")))):
                block.append(lines[i])
                i += 1
            html_parts.append(_render_list(block))
            continue
        # Paragraph (gather consecutive plain lines). A line that reaches here but
        # matches a block marker no handler consumed (a bare '#', a stray '|' or
        # '-' fragment) must still advance i, or the loop spins.
        start_i = i
        para = []
        while i < n and lines[i].strip() and not re.match(
                r"^\s*(-\s+|#|\||<!--|---)", lines[i]):
            para.append(lines[i].strip())
            i += 1
        if para:
            html_parts.append(f"<p>{inline(' '.join(para))}</p>")
        elif i == start_i:
            html_parts.append(f"<p>{inline(lines[i].strip())}</p>")
            i += 1
    return "\n".join(html_parts)


def _render_list(block):
    """Render `- ` bullets with one optional level of indented sub-bullets."""
    out = ["<ul>"]
    open_sub = False
    for line in block:
        indent = len(line) - len(line.lstrip(" \t"))
        m = re.match(r"^\s*-\s+(.*)$", line)
        if not m:
            # continuation of the previous bullet
            if out:
                out[-1] = out[-1][:-5] + " " + inline(line.strip()) + "</li>"
            continue
        item = inline(m.group(1).strip())
        if indent >= 2:
            if not open_sub:
                out.append("<ul>")
                open_sub = True
            out.append(f"<li>{item}</li>")
        else:
            if open_sub:
                out.append("</ul>")
                open_sub = False
            out.append(f"<li>{item}</li>")
    if open_sub:
        out.append("</ul>")
    out.append("</ul>")
    return "\n".join(out)


def _render_table(rows):
    def cells(r):
        return [c.strip() for c in r.strip().strip("|").split("|")]
    header = cells(rows[0])
    # rows[1] is the |---| separator when present (only |, :, -, spaces). Skip it
    # only if it really is one, so a table written without a separator row doesn't
    # silently drop its first data row.
    def _is_sep(r):
        s = r.strip()
        return bool(s) and set(s) <= set("|:- ")
    body = rows[2:] if len(rows) > 1 and _is_sep(rows[1]) else rows[1:]
    out = ['<table class="remit-table"><thead><tr>']
    out += [f"<th>{inline(h)}</th>" for h in header]
    out.append("</tr></thead><tbody>")
    for r in body:
        out.append("<tr>" + "".join(
            f"<td>{inline(c)}</td>" for c in cells(r)) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def _split_sections(lines):
    """Yield (heading, body_lines) per `## ` section."""
    sections, cur = [], None
    for line in lines:
        if line.startswith("## "):
            if cur:
                sections.append(cur)
            cur = [line[3:].strip(), []]
        elif cur is not None:
            cur[1].append(line)
        # lines before the first `## ` (title/subtitle) are handled by caller
    if cur:
        sections.append(cur)
    return sections


def _badge(body_lines):
    """Pull a leading POLICY/CONTEXT comment out of a section body → (kind, desc, rest)."""
    i = 0
    while i < len(body_lines) and body_lines[i].strip() == "":
        i += 1
    if i < len(body_lines) and body_lines[i].strip().startswith("<!--"):
        buf = []
        j = i
        while j < len(body_lines):
            buf.append(body_lines[j])
            if "-->" in body_lines[j]:
                break
            j += 1
        m = COMMENT_RE.search("\n".join(buf))
        inner = (m.group(1).strip() if m else "")
        bm = BADGE_RE.match(inner)
        if bm:
            desc = bm.group(2).strip().strip("().")
            return bm.group(1), desc, body_lines[j + 1:]
    return None, None, body_lines


# ── page assembly ─────────────────────────────────────────────────────────────
def _identity_meta(body_lines):
    """From the Identity table, return {field: value} for the masthead."""
    meta = {}
    for line in body_lines:
        s = line.strip()
        # >= 2 pipes: GFM makes the trailing pipe optional, so a two-column row
        # written `| Field | Value` (2 pipes) is valid and must still feed the
        # masthead (#210) — _render_table already accepts it in the body.
        if s.startswith("|") and s.count("|") >= 2:
            parts = [c.strip() for c in s.strip("|").split("|")]
            if len(parts) >= 2 and parts[0] not in ("Field", "") and set(parts[0]) != {"-"}:
                meta[parts[0]] = parts[1]
    return meta


def render_remit(md, template_html, praxen_version):
    style, logo_svg, footer = extract_chrome(template_html)

    lines = _strip_leading_license(md.splitlines())

    # Title + subtitle (the `# ...` and the following `*...*`), before section 1.
    title, subtitle = "Worker Remit", ""
    for idx, line in enumerate(lines):
        s = line.strip()
        if s.startswith("# ") and not s.startswith("## "):
            title = s[2:].strip()
        elif (s.startswith("*") and not s.startswith("**") and s.endswith("*")
              and len(s) > 2):
            subtitle = s.strip("*").strip()
            break
        elif s.startswith("## "):
            break

    sections = _split_sections(lines)

    agent_name, remit_version, last_updated = "", "", ""
    body_html = []
    for heading, body in sections:
        kind, desc, rest = _badge(body)
        if heading == "Identity":
            meta = _identity_meta(rest)
            agent_name = meta.get("Worker Name", "")
            remit_version = meta.get("Remit Version", "")
            last_updated = meta.get("Last Updated", "")
        badge_html = ""
        if kind:
            cls = "policy" if kind == "POLICY" else "context"
            badge_html = (f'<span class="remit-badge remit-badge-{cls}">{kind}</span>'
                          + (f'<span class="remit-badge-desc">{inline(desc)}</span>'
                             if desc else ""))
        # drop the footer signature block if it leaked into the last section
        rest = [l for l in rest if not l.strip().startswith("*Worker Remit")
                and not l.strip().startswith("*Customized for")]
        inner = _render_blocks(rest)
        anchor = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
        body_html.append(
            f'<section class="remit-card" id="{anchor}">\n'
            f'  <div class="remit-card-head"><h2>{inline(heading)}</h2>{badge_html}</div>\n'
            f'  <div class="remit-card-body">\n{inner}\n  </div>\n'
            f'</section>')

    masthead = (
        '<div class="remit-masthead">\n'
        '  <div class="remit-mh-row">\n'
        f'    <div class="masthead-logo">{logo_svg}</div>\n'
        '    <div class="remit-mh-id">\n'
        f'      <div class="remit-mh-kicker">{inline(subtitle or "Agent Policy")}</div>\n'
        f'      <div class="remit-mh-agent">{inline(agent_name or title)}</div>\n'
        f'      <div class="remit-mh-sub">{_mh_sub(remit_version, last_updated)}</div>\n'
        '    </div>\n'
        '  </div>\n'
        '</div>')

    footer = footer.replace("{{PRAXEN_VERSION}}", html.escape(praxen_version))

    return _PAGE.format(
        title=html.escape(f"Worker Remit — {agent_name or title}"),
        style=style,
        remit_css=_REMIT_CSS,
        masthead=masthead,
        body="\n".join(body_html),
        footer=footer,
    )


def _mh_sub(version, updated):
    bits = []
    if version:
        bits.append(f"Remit v{html.escape(version)}")
    if updated:
        bits.append(f"Updated {html.escape(updated)}")
    return " &nbsp;&middot;&nbsp; ".join(bits)


_REMIT_CSS = """
  .remit-masthead { background: var(--navy); border-top: 4px solid var(--orange);
    border-bottom: 2px solid var(--border-alt); padding: 20px 32px 24px; }
  .remit-mh-row { display: flex; align-items: flex-start; gap: 28px; flex-wrap: wrap; }
  .remit-mh-kicker { color: var(--orange-2); font-size: 11px; font-weight: 800;
    letter-spacing: 0.12em; text-transform: uppercase; }
  .remit-mh-agent { color: #FFFFFF; font-size: 22px; font-weight: 800; line-height: 1.15;
    margin-top: 6px; }
  .remit-mh-sub { color: #8BAFC8; font-size: 12.5px; margin-top: 8px; }
  .remit-wrap { max-width: 960px; margin: 0 auto; padding: 28px 32px 8px; }
  .remit-card { background: var(--bg); border: 1px solid var(--border);
    border-radius: 10px; padding: 20px 24px; margin-bottom: 18px;
    box-shadow: 0 1px 2px rgba(13,27,42,0.04); }
  .remit-card-head { display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap;
    border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 14px; }
  .remit-card-head h2 { font-size: 17px; font-weight: 800; color: var(--navy);
    letter-spacing: 0.01em; }
  .remit-badge { display: inline-block; font-size: 10px; font-weight: 800;
    letter-spacing: 0.09em; text-transform: uppercase; padding: 2px 9px; border-radius: 10px; }
  .remit-badge-policy { background: var(--orange); color: #FFFFFF; }
  .remit-badge-context { background: var(--surface); color: var(--text-muted);
    border: 1px solid var(--border); }
  .remit-badge-desc { font-size: 11.5px; color: var(--text-muted); font-style: italic; }
  .remit-card-body h3 { font-size: 13px; font-weight: 800; color: var(--text-muted);
    text-transform: uppercase; letter-spacing: 0.06em; margin: 16px 0 8px; }
  .remit-card-body h3:first-child { margin-top: 0; }
  .remit-card-body h4 { font-size: 13px; font-weight: 800; color: var(--navy);
    margin: 12px 0 6px; }
  .remit-card-body p { margin: 0 0 10px; }
  .remit-card-body ul { margin: 0 0 10px; padding-left: 22px; }
  .remit-card-body li { margin-bottom: 6px; }
  .remit-card-body ul ul { margin: 6px 0 6px; }
  .remit-note { font-size: 12px; color: var(--text-muted); font-style: italic;
    background: var(--surface); border-left: 3px solid var(--border-alt);
    padding: 6px 12px; border-radius: 0 6px 6px 0; }
  .remit-card-body code { font-family: 'SF Mono', ui-monospace, Menlo, Consolas, monospace;
    font-size: 12.5px; background: var(--surface-alt); border: 1px solid var(--border-alt);
    border-radius: 4px; padding: 1px 5px; }
  .remit-table { border-collapse: collapse; width: 100%; margin: 4px 0 12px; font-size: 13px; }
  .remit-table th { background: var(--navy); color: #FFFFFF; text-align: left;
    padding: 8px 12px; font-size: 11px; letter-spacing: 0.05em; text-transform: uppercase; }
  .remit-table td { border: 1px solid var(--border); padding: 8px 12px; vertical-align: top; }
  .remit-table tbody tr:nth-child(even) { background: var(--surface); }
  #identity .remit-table th:first-child, #identity .remit-table td:first-child {
    width: 30%; font-weight: 700; color: var(--text-muted); }
"""

_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
{style}
<style>{remit_css}</style>
</head>
<body>
{masthead}
<div class="remit-wrap">
{body}
</div>
{footer}
</body>
</html>
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render a Worker Remit (Markdown) to styled HTML.")
    ap.add_argument("remit", type=Path, help="path to the WORKER_REMIT.md")
    ap.add_argument("--out", type=Path, default=None, help="output HTML path (default: REMIT.html)")
    ap.add_argument("--template", type=Path, default=None,
                    help="report_template.html to borrow brand chrome from (default: sibling)")
    ap.add_argument("--praxen-version", default=None,
                    help="footer version string (default: read from .claude-plugin/plugin.json)")
    args = ap.parse_args(argv)

    if not args.remit.is_file():
        ap.error(f"remit not found: {args.remit}")
    template = args.template or (Path(__file__).resolve().parent / "report_template.html")
    if not template.is_file():
        ap.error(f"template not found: {template}")
    out = args.out or args.remit.with_suffix(".html")

    version = _praxen_version(args.praxen_version,
                              [Path(__file__).resolve().parent, Path.cwd(), args.remit.resolve().parent])
    try:
        page = render_remit(args.remit.read_text(encoding="utf-8"),
                            template.read_text(encoding="utf-8"), version)
    except RemitRenderError as e:
        print(f"render_remit.py: {e}", file=sys.stderr)
        return 1
    out.write_text(page, encoding="utf-8")
    print(f"render_remit.py: wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
