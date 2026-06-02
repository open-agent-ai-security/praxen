#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Build the user-facing styled HTML docs site for GitHub Pages from docs/*.md.

This is a BUILD-ONLY tool — it is not part of the skill the user downloads and
is never shipped in the plugin zip. It requires Python-Markdown
(`pip install -r requirements-dev.txt`). The distributable keeps shipping the
raw `docs/*.md`; this generates a prettier, on-brand clone under `guide/` for
the public website only.

Each output page is self-contained: the shared design system
(assets/praxen-theme.css) is inlined, exactly like the coverage-report
generators. A left-nav lists every doc (the current one expanded into its
section TOC); cross-doc `*.md` links are rewritten to `*.html`, and links to
repo files (`../FOO.md`) are pointed at the GitHub blob view.

Edit the docs in markdown; regenerate at release time:

    python3 docs_build.py
"""
import html
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    import markdown
except ImportError:
    sys.exit("docs_build.py: Python-Markdown not installed. "
             "Run: pip install -r requirements-dev.txt")

ROOT = Path(__file__).resolve().parent
DOCS_DIR = ROOT / "docs"
OUT_DIR = ROOT / "guide"
THEME_CSS = ROOT / "assets" / "praxen-theme.css"
REPO = "https://github.com/open-agent-ai-security/praxen"

# Ordered table of contents for the left-nav: (source file, nav label).
PAGES = [
    ("index.md",                  "Overview"),
    ("installation.md",           "Installation"),
    ("quickstart.md",             "Quickstart"),
    ("usage.md",                  "Usage"),
    ("writing-remits.md",         "Writing Worker Remits"),
    ("interpreting-reports.md",   "Interpreting Reports"),
    ("challenging-findings.md",   "Challenging Findings"),
    ("understanding-variability.md", "Run-to-Run Variability"),
    ("owasp.md",                  "OWASP Gen AI Security"),
    ("RAISE.md",                  "The RAISE Framework"),
]

LEADING_COMMENT = re.compile(r"^\s*<!--.*?-->\s*", re.DOTALL)


def rewrite_links(body: str) -> str:
    """Rewrite href targets in the generated HTML for the site:
      - any URL with a scheme (http, https, mailto, ftp, …), a protocol-relative
        //host, or a pure #anchor: left untouched
      - ../repo/file: GitHub blob view (dev artifacts, not served on the site)
      - sibling docs foo.md[#frag]: foo.html[#frag]

    This runs on the rendered HTML, so it also rewrites links inside any raw-HTML
    passthrough blocks a doc may contain — correct for real navigation links. An
    author wanting to *show* a literal `.md` href as an example should put it in a
    fenced code block (Python-Markdown escapes the quotes there, so it never
    matches). Both double- and single-quoted href attributes are handled.
    """
    def repl(m):
        quote, href = m.group(1), m.group(2)
        if urlparse(href).scheme or href.startswith(("#", "//")):
            return m.group(0)
        if href.startswith("../"):
            # docs/ is one level below the repo root, so a legitimate cross-repo
            # link is a single `../`. Strip any leading `../` runs defensively so
            # a stray `../../x` still yields a repo-root path, not `./x`.
            new = f"{REPO}/blob/main/" + re.sub(r"^(?:\.\./)+", "", href)
        else:
            new = re.sub(r"\.md(#|$)", r".html\1", href)
        return f"href={quote}{new}{quote}"
    return re.sub(r"""href=(["'])(.*?)\1""", repl, body)


def onpage_toc(toc_tokens) -> str:
    """Build a flat 'sections' list from the page's H2 headings.

    toc_tokens is a hierarchical tree — H2s are nested under their H1 parent's
    'children' — so walk it recursively rather than scanning only the top level.
    """
    items = []

    def collect(tokens):
        for t in tokens:
            if t.get("level") == 2:
                items.append(t)
            collect(t.get("children") or [])

    collect(toc_tokens)
    if not items:
        return ""
    lis = "".join(
        f'<li><a href="#{t["id"]}">{html.escape(t["name"])}</a></li>' for t in items
    )
    return f'<ul class="docs-subnav">{lis}</ul>'


def left_nav(active_file: str, active_toc: str) -> str:
    out = ['<nav class="docs-nav"><div class="docs-nav-title">Documentation</div><ul>']
    for src, label in PAGES:
        target = src[:-3] + ".html"
        is_active = src == active_file
        cls = ' class="active"' if is_active else ""
        out.append(f'<li><a href="{target}"{cls}>{html.escape(label)}</a>')
        if is_active and active_toc:
            out.append(active_toc)
        out.append("</li>")
    out.append("</ul></nav>")
    return "".join(out)


def page_html(theme_css: str, title: str, nav: str, body: str, src: str) -> str:
    edit_url = f"{REPO}/blob/main/docs/{src}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · Praxen Docs</title>
<style>{theme_css}</style>
</head>
<body class="docs-page">
<header class="docs-top">
  <div class="docs-top-inner">
    <a class="docs-brand" href="../"><img src="../graphics/web/praxen-logo.png" alt="Praxen"></a>
    <div class="docs-top-links">
      <a href="../">Home</a>
      <a href="{REPO}" target="_blank" rel="noopener">GitHub ↗</a>
    </div>
  </div>
</header>
<div class="docs-shell">
  <aside class="docs-sidebar">{nav}</aside>
  <main class="docs-main">
    <article class="prose">{body}</article>
    <p class="docs-edit"><a href="{edit_url}" target="_blank" rel="noopener">Edit this page on GitHub ↗</a></p>
  </main>
</div>
</body>
</html>
"""


def build():
    if not THEME_CSS.is_file():
        sys.exit(f"docs_build.py: shared theme not found at {THEME_CSS}")
    theme_css = THEME_CSS.read_text(encoding="utf-8")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    known = {src for src, _ in PAGES}
    on_disk = {p.name for p in DOCS_DIR.glob("*.md")}
    missing = known - on_disk
    if missing:
        sys.exit(f"docs_build.py: PAGES lists files not in docs/: {sorted(missing)}")
    extra = on_disk - known
    if extra:
        print(f"docs_build.py: note: docs/*.md not in the nav (skipped): {sorted(extra)}",
              file=sys.stderr)

    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "toc", "sane_lists"],
        output_format="html5",
    )

    for src, label in PAGES:
        text = (DOCS_DIR / src).read_text(encoding="utf-8")
        text = LEADING_COMMENT.sub("", text, count=1)  # drop the license header comment
        md.reset()
        body = md.convert(text)
        body = rewrite_links(body)

        m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.DOTALL)
        # The H1 is already HTML-escaped; unescape before page_html re-escapes it.
        title = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else label

        nav = left_nav(src, onpage_toc(md.toc_tokens))
        out_path = OUT_DIR / (src[:-3] + ".html")
        out_path.write_text(page_html(theme_css, title, nav, body, src), encoding="utf-8")
        print(f"docs_build.py: wrote {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
