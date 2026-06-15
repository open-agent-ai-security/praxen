<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxen Docs — Authoring & Build Guide

How the `docs/` directory works: what gets shipped, how the styled website is generated, the
style conventions to follow, and the non-obvious assumptions (dividers, diagrams) that are easy
to rediscover the hard way. **This file is for contributors — it is not a website page** (the
build intentionally skips it).

## Two artifacts from one source

Everything authored here lives as plain Markdown in `docs/*.md`. That Markdown is the source of
truth, and it is shipped two ways:

1. **Raw Markdown** — `docs/*.md` ships verbatim in the plugin distributable. This is what a user
   reads on GitHub or in their unzipped copy. No build step; no dependencies.
2. **Styled HTML site** — `guide/*.html` is a generated, on-brand clone for the public GitHub
   Pages site, built from the same Markdown by [`../docs_build.py`](../docs_build.py). It is
   **build-only**: the `markdown` dependency is never shipped, and `guide/` is a build product, not
   hand-edited.

> **Never hand-edit `guide/*.html`.** It is overwritten on every build. Edit the Markdown and
> regenerate.

## Build & preview

```bash
pip install -r ../requirements-dev.txt   # one-time: installs Python-Markdown (build-only dep)
python3 ../docs_build.py                  # regenerates all of guide/*.html
```

Each page is self-contained: the shared design system (`../assets/praxen-theme.css`) is inlined
into every HTML file, so a page needs no external CSS.

**Previewing:** most pages open fine straight from disk (`file://…/guide/foo.html`). The
exception is **pages with Mermaid diagrams** (see below) — those need an `http(s)://` origin to
render, so preview them through a local web server:

```bash
# from the repo root, so ../graphics and the Home link resolve
python3 -m http.server 8000
# then open http://localhost:8000/guide/index.html
```

## Adding or editing a page

- **Register it in the nav.** Add a `("filename.md", "Nav Label")` entry to the `PAGES` list in
  [`../docs_build.py`](../docs_build.py). Order in that list **is** the left-nav order. A
  `docs/*.md` file that isn't in `PAGES` is skipped (the build prints a note) — so a new page
  with no `PAGES` entry silently won't appear on the site.
- **The page title comes from the first `# H1`**, not from the nav label — they can differ.
- **Start every file with the license header comment** (copy the one at the top of this file).
  The build strips that leading `<!-- … -->` before rendering.
- The left-nav auto-expands the current page into its `##` section TOC; you don't manage that by
  hand.

## Style conventions

Match the existing docs — the cheapest way is to skim a sibling page before writing.

- **Do NOT put a `---` horizontal rule before a heading.** The theme already draws a divider as
  the `border-top` on every `<h2>`. An explicit `---` renders a *second* `<hr>`, producing a
  doubled line. Section separation is automatic — just write the `## Heading`. (`---` mid-content
  for a genuine thematic break is fine; it's only the rule-before-a-heading that doubles up.)
- **Headings are sentence case** — `## Running an analysis`, not `## Running An Analysis`. The one
  exception is proper nouns (the RAISE category names like `### Limit Your Domain`). Keep each
  section substantial enough to earn its divider; avoid three-line sections that make the
  auto-dividers feel choppy. Don't title the *same* concept two ways across pages.
- **Lists** come in two shapes — don't mix them inside one list:
  - *Label list* — a bold label, an **em-dash**, then a fragment with **no** terminal period:
    `- **Escalation Rules** — what triggers halt, alert, log-only`. This is the house default
    (use the em-dash `—`, not a colon).
  - *Sentence list* — a bold lead-in that continues into a full sentence, **with** a period:
    `- **Vulnerability scanning** identifies secrets, vulnerable dependencies, and misconfigurations.`
- **Blockquote callouts** follow three roles:
  - *External resource* — `> **📊 See it live:** …` linking a live report or page.
  - *Note / tip* — `> **Short label.** …` (bold label, period, then the note).
  - *Conceptual quote* — a bold framing question or statement (`> **Is the agent within its role?**`).
    The italic product tagline on the Overview page is a deliberate one-off, not a pattern to copy.
- **Terminology** — capitalize the proper nouns consistently: `Praxen`, `Worker Remit` (lowercase
  bare "remit" is fine once introduced), `Agent Behavior Verification` / `ABV`, `Agent Behavior
  Analytics` / `ABA`, `RAISE`, the `behavior-verifier` skill. Use the **official** framework
  titles: `OWASP Top 10 for LLM Applications 2025`, `OWASP Top 10 for Agentic AI Applications
  2026`, and OWASP's `A Practical Guide for Secure MCP Server Development 2026` (not a paraphrase).
- **Voice & numbers** — address the reader as "you" (the operator) on procedural pages; spell out
  small numbers in prose ("five minutes", not "5 minutes"). Keep these consistent with siblings.
- **Cross-links** (handled automatically by the build's link rewriter):
  - Sibling docs — link with the `.md` path (`[Usage](usage.md)`); the build rewrites it to
    `.html` for the site while keeping it valid on GitHub.
  - Repo files outside `docs/` — link with a single leading `../` (`[`PRAXEN_SPEC.md`](../PRAXEN_SPEC.md)`);
    the build points these at the GitHub blob view (they aren't served on the site).
  - External URLs, `mailto:`, and pure `#anchors` are left untouched.
  - To show a *literal* `.md` link as an example (not a real link), put it in a fenced code block
    — the rewriter skips fenced code.
- **Tables, fenced code, and TOC anchors** work via the standard extensions (`tables`,
  `fenced_code`, `toc`, `sane_lists`). No GitHub-only Markdown.

## Mermaid diagrams

Author diagrams as a ` ```mermaid ` fenced block in Markdown — the build does the rest:

- The fence is converted to a `<pre class="mermaid">` element, and the **Mermaid runtime is
  injected only on pages that actually contain a diagram** (other pages stay clean).
- The runtime (Mermaid, MIT-licensed) loads from jsDelivr **pinned to an exact version with a
  Subresource Integrity (SRI) hash** (`MERMAID_VERSION` / `MERMAID_SRI` in `docs_build.py`), so the
  browser refuses any CDN bytes that don't match. It's initialized with a dark theme tuned to the
  navy palette; styling lives in `.prose pre.mermaid` / `themeVariables` — adjust there, not in the
  HTML. To bump Mermaid, change the version and regenerate the SRI hash (the one-liner is in the
  `docs_build.py` comment).

**Key assumption — preview diagrams over an HTTP(S) origin.** The runtime is a classic CDN script
loaded with Subresource Integrity and `crossorigin`, which needs a real origin: GitHub Pages or the
local `python3 -m http.server` above render correctly, while a diagram opened directly from a
`file://` page may fall back to showing its *source text* (browsers handle an integrity-checked
cross-origin fetch from a null `file://` origin inconsistently). This is a deliberate tradeoff:
`guide/` is the online website clone, so a pinned, integrity-checked CDN script is acceptable there.
If a fully offline-self-contained diagram is ever required, the alternative is to vendor the Mermaid
bundle locally or hand-build CSS box-and-arrow markup (no JS).

## Release / CI tie-in

- **`guide/` must be committed in sync with `docs/`.** After any `docs/*.md` or
  `assets/praxen-theme.css` change, run `python3 ../docs_build.py` and commit the updated
  `guide/*.html` in the **same** change. (`CONTRIBUTING.md` states this for contributors.)
- **`build.sh` enforces it.** At release it rebuilds `guide/` and fails if the working tree
  differs — a stale `guide/` blocks the tagged release. CI without the `markdown` dep skips the
  check (stdlib-only build stays green); the release workflow installs the dep, so a tag always
  enforces freshness.

## Quick gotcha list

- Hand-edited `guide/*.html` → overwritten on next build. Edit Markdown.
- New page not in `PAGES` → invisible on the site (build prints a skip note).
- `---` directly above a heading → doubled divider line.
- Mermaid diagram looks like raw code → you're viewing over `file://`; use a web server.
- Changed the shared theme (`assets/praxen-theme.css`) → every page changes; rebuild and commit
  all of `guide/`.
