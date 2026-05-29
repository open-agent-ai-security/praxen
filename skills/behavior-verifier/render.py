#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Praxen report renderer — turns a canonical findings JSON into HTML and TXT.

Stage 2 of the Praxen pipeline. Deterministic: the same JSON in produces
byte-identical output every time. No judgment, no inference, no "if a field is
missing, generate something reasonable" — schema.py validates the input first
and fails loudly with the offending path; this module then performs a pure,
mechanical substitution.

Template syntax (in skills/behavior-verifier/report_template.html):

  {{PLACEHOLDER}}                       scalar substitution
  <!-- REPEAT:name -->...<!-- END:name -->     repeat the enclosed block per item
  <!-- PICK:name -->                            choose one of two variant blocks
    <!-- Variant A: ... -->...
    <!-- Variant B: ... -->...
  <!-- END:name -->

The JSON holds semantic data only (severity = "Critical", status = "gap"); this
renderer maps those to CSS classes and computes derived display values
(score percent, weighted contribution, maturity label, overall status badge).

Usage:
  python render.py --findings F.json --template T.html --out-html O.html --out-txt O.txt

--findings is required. At least one of --out-html / --out-txt is required.
--template is required whenever --out-html is given. All paths absolute.
Exit code 0 on success; non-zero with a diagnostic on any error.

Python 3.9+ stdlib only. No third-party dependencies.
"""
from __future__ import annotations

import argparse
import html
import json
import math
import os
import re
import sys
import textwrap
from datetime import datetime

# render.py and schema.py ship together in skills/behavior-verifier/.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schema  # noqa: E402
from schema import (  # noqa: E402
    RAISE_KEYS, RAISE_NAMES, SEVERITIES, SEVERITY_COUNT_KEYS,
    REMIT_STATUSES, SchemaError, maturity_label,
)


class RenderError(Exception):
    """Raised when the template cannot be rendered cleanly."""


# ── derived-value tables (semantic JSON value -> presentation) ───────────────
_SEV_CLASS = {"Critical": "sev-critical", "High": "sev-high", "Medium": "sev-medium",
              "Low": "sev-low", "Informational": "sev-info"}
_SEV_LABEL = {"Critical": "CRITICAL", "High": "HIGH", "Medium": "MEDIUM",
              "Low": "LOW", "Informational": "INFO"}
_SEV_RANK = {s: i for i, s in enumerate(SEVERITIES)}     # Critical first

_STATUS_PILL = {"verified": "pill-verified", "gap": "pill-gap", "partial": "pill-partial",
                "vague": "pill-vague", "enp": "pill-enp"}
_STATUS_LABEL = {"verified": "Verified", "gap": "Gap", "partial": "Partial",
                 "vague": "Vague Policy", "enp": "Enforcement Not Possible"}

_TAG_CLASS = {"raise": "tag-raise", "owasp_llm": "tag-owasp",
              "owasp_agentic": "tag-agentic", "mcp": "tag-owasp"}

_LOG_STATUS_CLASS = {"active": "log-status-active", "new": "log-status-new", "inferred": "log-status-inferred"}
_LOG_STATUS_LABEL = {"active": "Active", "new": "New", "inferred": "Inferred"}

_SCORE_CLASS = {0: "score-0-1", 1: "score-0-1", 2: "score-2",
                3: "score-3", 4: "score-4-5", 5: "score-4-5"}

# OWASP Top 10 coverage grid — canonical code order and titles. Titles are
# copied verbatim from the published OWASP entries (kept in sync with the
# `knowledge/KB_LLM_TOP10.md` and `knowledge/KB_AGENTIC_TOP10.md` headings).
_OWASP_LLM_CODES = ("LLM01", "LLM02", "LLM03", "LLM04", "LLM05",
                    "LLM06", "LLM07", "LLM08", "LLM09", "LLM10")
_OWASP_LLM_TITLES = {
    "LLM01": "Prompt Injection",
    "LLM02": "Sensitive Information Disclosure",
    "LLM03": "Supply Chain",
    "LLM04": "Data and Model Poisoning",
    "LLM05": "Improper Output Handling",
    "LLM06": "Excessive Agency",
    "LLM07": "System Prompt Leakage",
    "LLM08": "Vector and Embedding Weaknesses",
    "LLM09": "Misinformation",
    "LLM10": "Unbounded Consumption",
}
_OWASP_AGENTIC_CODES = ("ASI01", "ASI02", "ASI03", "ASI04", "ASI05",
                        "ASI06", "ASI07", "ASI08", "ASI09", "ASI10")
_OWASP_AGENTIC_TITLES = {
    "ASI01": "Agent Goal Hijack",
    "ASI02": "Tool Misuse and Exploitation",
    "ASI03": "Identity and Privilege Abuse",
    "ASI04": "Agentic Supply Chain Vulnerabilities",
    "ASI05": "Unexpected Code Execution (RCE)",
    "ASI06": "Memory and Context Poisoning",
    "ASI07": "Insecure Inter-Agent Communication",
    "ASI08": "Cascading Failures",
    "ASI09": "Human-Agent Trust Exploitation",
    "ASI10": "Rogue Agents",
}
# Highest severity present in a card's top-3 -> CSS class on the card. Empty
# cells use " empty" instead (handled below).
_WORST_SEV_CLASS = {"Critical": "worst-critical", "High": "worst-high",
                    "Medium": "worst-medium", "Low": "worst-low",
                    "Informational": "worst-info"}
# Per-card cap for the OWASP grid — chips beyond this are dropped from the
# card (the full set still appears in the Findings Register). Three keeps
# the cell compact and matches the published OWASP grid's visual density.
_OWASP_CHIPS_PER_CARD = 3

# Highest severity present in findings[] -> (badge class, badge label). Checked
# top-to-bottom; "Medium" and "Low" both map to advisory; only-Informational or
# no findings -> clean.
_OVERALL_STATUS_RULES = [
    ("Critical", "critical", "CRITICAL"),
    ("High", "high", "HIGH"),
    ("Medium", "advisory", "ADVISORY"),
    ("Low", "advisory", "ADVISORY"),
]

# Rich-text JSON fields that may contain a small set of inline HTML tags. Every
# other text field is fully escaped. (`<p>` only makes sense in the multi-
# paragraph behavior summary; `<code>`/`<strong>`/`<em>` are benign inline
# emphasis the synthesis step naturally reaches for.)
_RICH_FIELDS = {
    "agent_remit_summary": ("code", "strong", "em"),
    "agent_structure_summary": ("code", "strong", "em"),
    "behavior_summary": ("p", "code", "strong", "em"),
    "recommended_actions": ("code", "strong", "em"),
}


# ── escaping ─────────────────────────────────────────────────────────────────
def _neutralise_braces(s: str) -> str:
    """Turn literal ``{{`` / ``}}`` into numeric entities so a piece of code cited
    in a finding (a Jinja/Mustache/k8s/Compose template, ``{{DATABASE_URL}}`` and the
    like) can never collide with — or get mistaken for — a Praxen template placeholder.
    Renders identically to the literal braces in a browser."""
    return s.replace("{{", "&#123;&#123;").replace("}}", "&#125;&#125;")


def esc(value) -> str:
    """HTML-escape a value for either text content or an attribute value, and
    neutralise any literal ``{{...}}`` (see ``_neutralise_braces``).

    The value is HTML-*un*escaped first, so a string that already carries an HTML
    entity (``&mdash;``, ``&amp;``, ``&lt;NAME&gt;`` — easy to write into a prose
    field out of habit) renders as the character, not as the literal entity text.
    ``unescape`` then ``escape`` round-trips cleanly: a literal ``&`` and an
    ``&amp;`` both come out as ``&amp;`` (browser shows ``&``); ``&lt;`` and a
    literal ``<`` both come out as ``&lt;`` (browser shows ``<``)."""
    return _neutralise_braces(html.escape(html.unescape(str(value))))


def render_rich(text, allow=("code",)) -> str:
    """Escape ``text`` but preserve a small allowlist of inline tags.

    The Praxen skill emits these fields as plain prose plus, at most, the tags in
    ``allow`` (``<p>`` / ``<code>`` / ``<strong>`` / ``<em>``). We protect those
    exact tags, escape everything else, then restore them — so an unbalanced
    ``<`` in the prose is rendered as text, not as a stray tag, and a tag the
    skill reached for that is *not* in ``allow`` shows as escaped text rather
    than affecting layout. Literal ``{{...}}`` is neutralised too.

    The text is HTML-*un*escaped first (before tag protection), so an HTML
    entity written into a prose field — ``&mdash;``, ``&amp;``, ``&lt;NAME&gt;``,
    easy to do out of HTML habit — becomes the character it stands for instead of
    rendering double-escaped (``&amp;mdash;``) and showing the literal entity
    text. (The SKILL prompt asks for literal characters; this makes a slip
    harmless rather than visible in the report.)
    """
    text = html.unescape(str(text))
    if "\x00" in text:
        raise RenderError("rich-text field contains a NUL byte")
    tag_alt = "|".join(re.escape(t) for t in allow)
    saved: list[str] = []

    def _grab(m):
        saved.append(re.sub(r"\s+", "", m.group(0)).lower())   # normalise <CODE > -> <code>
        return f"\x00{len(saved) - 1}\x00"

    protected = re.sub(rf"</?(?:{tag_alt})\s*>", _grab, text, flags=re.IGNORECASE)
    escaped = _neutralise_braces(html.escape(protected))
    return re.sub(r"\x00(\d+)\x00", lambda m: saved[int(m.group(1))], escaped)


def strip_tags(text) -> str:
    """Flatten a rich-text field to plain text for the TXT summary: a ``</p>``
    paragraph break becomes a single space (so sentences don't run together),
    every other HTML-ish tag (``<p>``, ``<code>``, ``<strong>``, a stray
    ``<a ...>``, …) is dropped, and HTML entities (``&mdash;``, ``&amp;``,
    ``&lt;project&gt;`` …) are decoded to their characters — the prose fields
    legitimately carry entities for the HTML report, and the plain-text summary
    should show ``—`` / ``&`` / ``<project>`` rather than the raw entity text.
    A lone ``<`` that is not a tag is left alone."""
    t = re.sub(r"\s*</p\s*>\s*", " ", str(text), flags=re.IGNORECASE)
    t = re.sub(r"</?[a-zA-Z][^>]*>", "", t)
    return html.unescape(t)


# ── template engine ──────────────────────────────────────────────────────────
def _substitute_scalars(tpl: str, ctx: dict) -> str:
    """Replace ``{{NAME}}`` with ``ctx[NAME]``; leave unknown names untouched
    (a later pass — or the final assertion — will deal with them)."""
    return re.sub(r"\{\{([A-Z0-9_]+)\}\}",
                  lambda m: ctx[m.group(1)] if m.group(1) in ctx else m.group(0),
                  tpl)


def _find_block(tpl: str, kind: str, name: str):
    """Locate a REPEAT or PICK block by name. Returns (start, end, inner_text)."""
    pat = (rf"<!--\s*{kind}:{re.escape(name)}\b.*?-->"
           rf"(.*?)"
           rf"<!--\s*END:{re.escape(name)}\b\s*-->")
    matches = list(re.finditer(pat, tpl, flags=re.DOTALL))
    if not matches:
        raise RenderError(f"template is missing the {kind}:{name} block")
    if len(matches) > 1:
        raise RenderError(f"template has {len(matches)} {kind}:{name} blocks; expected exactly 1")
    m = matches[0]
    return m.start(), m.end(), m.group(1)


def expand_repeat(tpl: str, name: str, items, ctx_fn, *, empty_replacement="", inner=None) -> str:
    """Expand ``<!-- REPEAT:name -->...<!-- END:name -->`` once per item.

    ``ctx_fn(item, index) -> dict`` supplies the per-item scalar substitutions
    (values already escaped / stringified). ``inner(block, item) -> block``,
    if given, runs first to expand any nested REPEAT blocks for that item.
    If ``items`` is empty, the whole block (markers included) is replaced with
    ``empty_replacement``.
    """
    start, end, block = _find_block(tpl, "REPEAT", name)
    if not items:
        replacement = empty_replacement
    else:
        parts = []
        for idx, item in enumerate(items):
            instance = block
            if inner is not None:
                instance = inner(instance, item)
            instance = _substitute_scalars(instance, ctx_fn(item, idx))
            parts.append(instance)
        replacement = "".join(parts)
    return tpl[:start] + replacement + tpl[end:]


def resolve_pick(tpl: str, name: str, choose_a: bool) -> str:
    """Resolve ``<!-- PICK:name -->`` to its Variant A or Variant B block.

    The losing variant and all marker comments are removed. The surviving
    block's content is left intact for any later REPEAT / scalar processing.
    """
    start, end, body = _find_block(tpl, "PICK", name)
    parts = re.split(r"<!--\s*Variant\s+B\b.*?-->", body, maxsplit=1, flags=re.DOTALL)
    if len(parts) != 2:
        raise RenderError(f"PICK:{name} block is missing its Variant B marker")
    region_a, region_b = parts
    region_a = re.sub(r"^\s*<!--\s*Variant\s+A\b.*?-->\s*", "", region_a,
                      count=1, flags=re.DOTALL)
    chosen = region_a if choose_a else region_b
    return tpl[:start] + chosen + tpl[end:]


def strip_comments(tpl: str) -> str:
    """Remove every HTML comment from the rendered output.

    Template comments are authoring/structural notes plus the template's own
    license header — none of it belongs in a report. A rendered report is about
    the analyzed agent, not a copyrightable work of Exabeam's; the visible footer
    carries the Praxen attribution and the project-sponsor link.
    """
    return re.sub(r"<!--.*?-->", "", tpl, flags=re.DOTALL)


def assert_fully_rendered(tpl: str) -> None:
    leftovers = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", tpl)))
    if leftovers:
        raise RenderError(f"unsubstituted placeholders remain: {leftovers}")
    for marker in ("REPEAT:", "END:", "PICK:", "Variant A:", "Variant B:"):
        if re.search(rf"<!--\s*{re.escape(marker)}", tpl):
            raise RenderError(f"unresolved template marker remains: <!-- {marker} ...")


# ── timestamp formatting ─────────────────────────────────────────────────────
_MONTHS = ("January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December")


def _format_date(iso_date: str) -> str:
    """``2026-05-11`` -> ``May 11, 2026``. Fixed month names (not strftime ``%B``)
    so the renderer stays byte-deterministic regardless of the host locale."""
    try:
        y, m, d = (int(p) for p in iso_date.split("-"))
        return f"{_MONTHS[m - 1]} {d}, {y}"
    except (ValueError, IndexError) as e:
        raise RenderError(f"unparseable scan_date {iso_date!r}: {e}")


def _format_timestamp(iso_ts: str) -> str:
    """Display an ISO-8601 scan timestamp in the timezone the value itself carries.

    ``2026-05-11T22:49:16Z`` -> ``May 11, 2026, 22:49 UTC``; an offset-bearing
    value ``...T15:49:16-07:00`` -> ``May 11, 2026, 15:49 UTC-07:00``. The zone
    comes from the stored value, never from the host running render.py — using the
    render host's clock would be the wrong machine and would break byte-identical
    re-rendering. Seconds are dropped. Locale-independent for determinism.

    (Today the skill writes UTC ``Z``, so this shows UTC; once the skill records a
    local offset, the same code shows the scan's local time with no change here.)"""
    norm = iso_ts[:-1] + "+00:00" if iso_ts.endswith("Z") else iso_ts
    try:
        dt = datetime.fromisoformat(norm)
    except ValueError as e:
        raise RenderError(f"unparseable scan_timestamp {iso_ts!r}: {e}")
    base = f"{_MONTHS[dt.month - 1]} {dt.day}, {dt.year}, {dt.hour:02d}:{dt.minute:02d}"
    off = dt.utcoffset()
    if off is None or off.total_seconds() == 0:
        return f"{base} UTC"
    total = int(off.total_seconds())
    sign = "+" if total >= 0 else "-"
    hh, mm = divmod(abs(total) // 60, 60)
    return f"{base} UTC{sign}{hh:02d}:{mm:02d}"


# ── per-block contexts ───────────────────────────────────────────────────────
def _remit_row_ctx(rule, _idx):
    fid = rule.get("finding_id")
    link = f'<a href="#{esc(fid)}">{esc(fid)}</a>' if fid else "&mdash;"
    return {
        "RULE_ID": esc(rule["rule_id"]),
        "REMIT_SECTION": esc(rule["section"]),
        "RULE_TEXT": esc(rule["rule_text"]),
        "STATUS_PILL_CLASS": _STATUS_PILL[rule["status"]],
        "STATUS_LABEL": _STATUS_LABEL[rule["status"]],
        "FINDING_LINK": link,
    }


_DOCS_BASE = "https://open-agent-ai-security.github.io/praxen/docs/"
_MCP_ANCHOR = "a-practical-guide-for-secure-mcp-server-development-2026"


def _tag_href(tag) -> str:
    """Resolve a finding tag to the exact entry in Praxen's own framework docs
    on GitHub Pages — derived from the tag's kind + label, so no schema field is
    needed. OWASP LLM/Agentic tags lead with their code (``LLM02``/``ASI05``) →
    ``owasp.html#llm02``; MCP tags → the MCP-guide section (no per-entry granularity);
    RAISE tags carry the category name → its ``RAISE.html`` heading anchor."""
    kind, label = tag["kind"], tag["label"]
    if kind in ("owasp_llm", "owasp_agentic"):
        m = re.match(r"\s*([A-Za-z]+\d+)", label)
        return f"{_DOCS_BASE}owasp.html#{m.group(1).lower()}" if m else f"{_DOCS_BASE}owasp.html"
    if kind == "mcp":
        return f"{_DOCS_BASE}owasp.html#{_MCP_ANCHOR}"
    if kind == "raise":
        slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
        return f"{_DOCS_BASE}RAISE.html#{slug}"
    return _DOCS_BASE  # unreachable: kinds are schema-constrained


def _finding_tag_ctx(tag, _idx):
    return {"TAG_CLASS": _TAG_CLASS[tag["kind"]], "TAG_LABEL": esc(tag["label"]),
            "TAG_HREF": esc(_tag_href(tag))}


def _policy_ctx(finding, _idx):
    return {
        "RULE_IDS": esc(finding["policy_rule_ids"]),
        "QUOTED_RULE_TEXT": esc(finding["policy_rule_text"]),
    }


def _expand_finding_inner(block, finding):
    """Expand the nested REPEAT blocks of a finding card.

    `finding_tag` repeats once per tag. `finding_policy` is a 0-or-1 block: it
    survives for a finding that cites a remit rule and is dropped for one whose
    `policy_rule_ids` is null (a RAISE-category / detection-pattern finding)."""
    block = expand_repeat(block, "finding_tag", finding["tags"], _finding_tag_ctx)
    has_rule = finding["policy_rule_ids"] is not None
    block = expand_repeat(block, "finding_policy",
                          [finding] if has_rule else [], _policy_ctx)
    return block


def _finding_ctx(finding, _idx):
    return {
        "FINDING_ANCHOR": esc(finding["id"]),
        "SEVERITY_CLASS": _SEV_CLASS[finding["severity"]],
        "SEVERITY_LABEL": _SEV_LABEL[finding["severity"]],
        "FINDING_ID": esc(finding["id"]),
        "FINDING_SUMMARY": esc(finding["summary"]),
        "EVIDENCE": _format_evidence(finding["evidence"]),
        "RECOMMENDED_ACTION": _format_recommended_actions(finding["recommended_actions"]),
    }


def _format_evidence(items):
    """Render the structured-evidence array as a `\n`-joined block of
    `file:line — snippet` lines (or `file — snippet` for file-level evidence),
    each component HTML-escaped. The `<div class="evidence-block">` has
    `white-space: pre-wrap`, so the newlines render as visible line breaks."""
    lines = []
    for item in items:
        head = esc(item["file"])
        if item.get("line") is not None:
            head = f"{head}:{item['line']}"
        lines.append(f"{head} — {esc(item['snippet'])}")
    return "\n".join(lines)


def _format_recommended_actions(actions):
    """A single action renders as text (same as the v1.0 single-string field);
    multiple actions render as a `<ul>` of `<li>`s. Each entry goes through
    `render_rich` so `<code>`/`<strong>`/`<em>` survive inline."""
    allow = _RICH_FIELDS["recommended_actions"]
    if len(actions) == 1:
        return render_rich(actions[0], allow=allow)
    items = "".join(f"<li>{render_rich(a, allow=allow)}</li>" for a in actions)
    return f"<ul>{items}</ul>"


def _positive_ctx(p, _idx):
    return {
        "POSITIVE_TITLE": esc(p["title"]),
        "POSITIVE_DESCRIPTION": esc(p["description"]),
        "POSITIVE_EVIDENCE_PATH": esc(p["evidence_path"]),
    }


def _log_row_ctx(row, _idx):
    return {
        "LOG_PATH": esc(row["path"]),
        "LOG_SOURCE": esc(row["source"]),
        "LOG_CONTENT_TYPE": esc(row["content_type"]),
        "LOG_PURPOSE": esc(row["purpose"]),
        "LOG_MTIME": esc(row["mtime"]),
        "LOG_STATUS_CLASS": _LOG_STATUS_CLASS[row["status"]],
        "LOG_STATUS_LABEL": _LOG_STATUS_LABEL[row["status"]],
    }


def _raise_card_ctx(cat, _idx):
    score, weight = cat["score"], cat["weight"]
    return {
        "SCORE_CLASS": _SCORE_CLASS[score],
        "CATEGORY_NAME": esc(cat["name"]),
        "SCORE": str(score),
        "SCORE_PCT": str(score * 20),
        "CONFIDENCE": esc(cat["confidence"]),
        "WEIGHT_PCT": str(round(weight * 100)),
        "WEIGHTED_CONTRIBUTION": f"{score * weight:.2f}",
        "RATIONALE": esc(cat["rationale"]),
    }


# ── OWASP coverage grid ─────────────────────────────────────────────────────
def _owasp_cards(findings, key, codes, titles):
    """Group findings by their OWASP scalar (`owasp_llm` or `owasp_agentic`) and
    shape one card record per canonical code in `codes`. Each card carries the
    top-3 findings sorted by severity (Critical first), with finding-ID as the
    deterministic tiebreaker. Cards with no findings get an "empty" marker;
    populated cards get a "worst-<sev>" class derived from their highest-severity
    chip. Findings whose `key` field is null simply don't land in any card.
    """
    groups = {c: [] for c in codes}
    for f in findings:
        code = f.get(key)
        if code in groups:
            groups[code].append(f)
    cards = []
    for code in codes:
        bucket = sorted(groups[code],
                        key=lambda f: (_SEV_RANK[f["severity"]], f["id"]))
        chips = bucket[:_OWASP_CHIPS_PER_CARD]
        if chips:
            card_class = " " + _WORST_SEV_CLASS[chips[0]["severity"]]
        else:
            card_class = " empty"
        cards.append({"code": code, "title": titles[code],
                      "chips": chips, "card_class": card_class})
    return cards


def _owasp_chip_ctx(finding, _idx):
    return {
        "FINDING_ANCHOR": esc(finding["id"]),
        "SEVERITY_CLASS": _SEV_CLASS[finding["severity"]],
        "FINDING_SUMMARY": esc(finding["summary"]),
    }


def _owasp_card_ctx(card, _idx):
    return {
        "OWASP_CODE": esc(card["code"]),
        "OWASP_TITLE": esc(card["title"]),
        "OWASP_CARD_CLASS": card["card_class"],  # already includes leading space
    }


def _owasp_card_inner(chip_block_name):
    """Return an `inner` callback for `expand_repeat` that expands one of the
    two nested chip REPEATs (`owasp_llm_chip` or `owasp_agentic_chip`) inside a
    card. An empty chip list collapses the REPEAT block to the muted
    "No findings" note."""
    no_findings = '<div class="owasp-count">No findings</div>'

    def _inner(block, card):
        return expand_repeat(block, chip_block_name, card["chips"],
                             _owasp_chip_ctx, empty_replacement=no_findings)
    return _inner


_MH_SEV_TIERS = [("critical", "Critical", "mh-crit"), ("high", "High", "mh-high"),
                 ("medium", "Medium", "mh-med"), ("low", "Low", "mh-low"),
                 ("info", "Info", "mh-info")]


def _severity_blocks(sc, total):
    """Build the masthead metric strip: a ``Findings`` total followed by one block
    per non-zero severity tier — a big count over a small label, colored by tier.
    Zero-count tiers are omitted. Returns ready HTML (a run of ``mh-metric`` divs)."""
    noun = "Finding" if total == 1 else "Findings"
    blocks = [f'<div class="mh-metric"><b>{total}</b><span>{noun}</span></div>']
    for key, label, cls in _MH_SEV_TIERS:
        if sc[key] > 0:
            blocks.append(f'<div class="mh-metric {cls}"><b>{sc[key]}</b><span>{label}</span></div>')
    return "".join(blocks)


def _overall_status(findings):
    present = {f["severity"] for f in findings}
    for sev, cls, label in _OVERALL_STATUS_RULES:
        if sev in present:
            return cls, label
    return "clean", "CLEAN"


def _global_ctx(data):
    scan = data["scan"]
    rc = data["remit_coverage"]["stat_counts"]
    sc = data["footer"]["severity_counts"]
    posture = data["raise_posture"]
    wo = posture["weighted_overall"]
    lf = data["log_files"]
    status_cls, status_label = _overall_status(data["findings"])
    ib = data["intro_band"]
    return {
        "AGENT_NAME": esc(scan["agent"]),
        "SCAN_DATE": esc(_format_date(scan["scan_date"])),
        "SCAN_TIMESTAMP": esc(_format_timestamp(scan["scan_timestamp"])),
        "ARTIFACT_COUNT": str(scan["artifact_count"]),
        "PRAXEN_VERSION": esc(data["praxen_version"]),
        "OVERALL_STATUS_CLASS": status_cls,
        "OVERALL_STATUS_LABEL": status_label,
        "SEVERITY_BLOCKS": _severity_blocks(sc, len(data["findings"])),
        "AGENT_REMIT_SUMMARY": render_rich(ib["agent_remit_summary"],
                                           allow=_RICH_FIELDS["agent_remit_summary"]),
        "AGENT_STRUCTURE_SUMMARY": render_rich(ib["agent_structure_summary"],
                                               allow=_RICH_FIELDS["agent_structure_summary"]),
        "SCAN_SUMMARY_NARRATIVE": render_rich(data["behavior_summary"],
                                              allow=_RICH_FIELDS["behavior_summary"]),
        "N_VERIFIED": str(rc["verified"]),
        "N_GAP": str(rc["gap"]),
        "N_PARTIAL": str(rc["partial"]),
        "N_VAGUE": str(rc["vague"]),
        "N_ENP": str(rc["enp"]),
        "N_TOTAL_RULES": str(rc["total"]),
        "N_CRITICAL": str(sc["critical"]),
        "N_HIGH": str(sc["high"]),
        "N_MEDIUM": str(sc["medium"]),
        "N_LOW": str(sc["low"]),
        "N_INFO": str(sc["info"]),
        "WEIGHTED_SCORE": f"{wo:.2f}",
        "RAISE_PCT": str(round(wo / 5 * 100)),
        "MATURITY_LABEL": maturity_label(wo),
        "WEIGHTED_RATIONALE": esc(posture["weighted_rationale"]),
        "NO_LOGS_NOTE": esc(lf["no_logs_note"]) if not lf["present"] else "",
    }


# ── HTML assembly ────────────────────────────────────────────────────────────
def render_html(template: str, data: dict) -> str:
    tpl = template

    # 1. PICK blocks (one variant survives).
    logs_present = data["log_files"]["present"]
    tpl = resolve_pick(tpl, "logs_present", choose_a=logs_present)

    # 2. REPEAT blocks (outer-then-inner).
    if logs_present:
        tpl = expand_repeat(tpl, "log_row", data["log_files"]["rows"], _log_row_ctx)
    tpl = expand_repeat(tpl, "remit_row", data["remit_coverage"]["rules"], _remit_row_ctx)
    findings_sorted = sorted(data["findings"], key=lambda f: _SEV_RANK[f["severity"]])  # stable
    tpl = expand_repeat(tpl, "finding", findings_sorted, _finding_ctx, inner=_expand_finding_inner)
    tpl = expand_repeat(
        tpl, "positive", data["positives"], _positive_ctx,
        empty_replacement='<div class="none-found">No confirmed positive controls '
                          'were verified during this scan.</div>',
    )
    cats_sorted = sorted(data["raise_posture"]["categories"], key=lambda c: RAISE_KEYS.index(c["key"]))
    tpl = expand_repeat(tpl, "raise_card", cats_sorted, _raise_card_ctx)

    # OWASP coverage grids — 10 LLM cards + 10 Agentic cards, each with up to
    # three most-severe chips (or a "No findings" note). Driven by each
    # finding's scalar `owasp_llm` / `owasp_agentic`, not the tags[] array.
    llm_cards = _owasp_cards(data["findings"], "owasp_llm",
                             _OWASP_LLM_CODES, _OWASP_LLM_TITLES)
    tpl = expand_repeat(tpl, "owasp_llm_card", llm_cards, _owasp_card_ctx,
                        inner=_owasp_card_inner("owasp_llm_chip"))
    agentic_cards = _owasp_cards(data["findings"], "owasp_agentic",
                                 _OWASP_AGENTIC_CODES, _OWASP_AGENTIC_TITLES)
    tpl = expand_repeat(tpl, "owasp_agentic_card", agentic_cards, _owasp_card_ctx,
                        inner=_owasp_card_inner("owasp_agentic_chip"))

    # 3. Top-level scalars.
    tpl = _substitute_scalars(tpl, _global_ctx(data))

    # 4. Nothing may be left unresolved.
    assert_fully_rendered(tpl)

    # 5. Drop all template comments (authoring notes + license header), then
    #    trim whatever whitespace they leave behind so the document starts at <!DOCTYPE>.
    tpl = strip_comments(tpl).lstrip()
    return tpl


# ── TXT assembly ─────────────────────────────────────────────────────────────
_TXT_WIDTH = 78


def _wrap(text, *, indent="", subsequent=None):
    subsequent = indent if subsequent is None else subsequent
    return textwrap.wrap(text, width=_TXT_WIDTH,
                         initial_indent=indent, subsequent_indent=subsequent,
                         break_long_words=False, break_on_hyphens=False) or [indent.rstrip()]


def render_txt(data: dict) -> str:
    scan = data["scan"]
    posture = data["raise_posture"]
    sc = data["footer"]["severity_counts"]
    findings = data["findings"]
    bar = "=" * _TXT_WIDTH
    sub = "-" * _TXT_WIDTH
    out: list[str] = []

    out.append(bar)
    out.append("PRAXEN — AGENT BEHAVIOR VERIFIER")
    out.append(f"Agent:    {scan['agent']}")
    out.append(f"Analysis: {_format_timestamp(scan['scan_timestamp'])}")
    out.append(f"Praxen v{data['praxen_version']}")
    out.append(bar)
    out.append("")

    out.append("BEHAVIOR SUMMARY")
    out.append(sub)
    out.extend(_wrap(strip_tags(data["behavior_summary"])))
    out.append("")

    out.append("RAISE MATURITY POSTURE")
    out.append(sub)
    out.append(f"  Weighted overall:  {posture['weighted_overall']:.2f} / 5.0"
               f"   ({maturity_label(posture['weighted_overall'])})")
    for c in sorted(posture["categories"], key=lambda c: RAISE_KEYS.index(c["key"])):
        out.append(f"  {c['name']:<30} {c['score']}/5"
                   f"   (confidence: {c['confidence']}, weight: {round(c['weight'] * 100)}%)")
    out.append("")

    out.append("FINDINGS")
    out.append(sub)
    out.append(f"  Critical: {sc['critical']}   High: {sc['high']}   Medium: {sc['medium']}"
               f"   Low: {sc['low']}   Informational: {sc['info']}")
    out.append(f"  Total: {len(findings)}")
    out.append("")

    rc = data["remit_coverage"]["stat_counts"]
    out.append("REMIT COVERAGE")
    out.append(sub)
    out.append(f"  Verified: {rc['verified']}   Gap: {rc['gap']}   Partial: {rc['partial']}"
               f"   Vague: {rc['vague']}   Enforcement-not-possible: {rc['enp']}"
               f"   (of {rc['total']} rules)")
    out.append("")

    # OWASP coverage tables — full counts per category (not capped), em-dash
    # for empty cells. The HTML grid caps per-card chips at three; this is
    # the summary, so the number reflects all findings in each category.
    for heading, key, codes, titles in (
        ("OWASP LLM TOP 10 COVERAGE", "owasp_llm",
         _OWASP_LLM_CODES, _OWASP_LLM_TITLES),
        ("OWASP AGENTIC TOP 10 COVERAGE", "owasp_agentic",
         _OWASP_AGENTIC_CODES, _OWASP_AGENTIC_TITLES),
    ):
        counts = {c: 0 for c in codes}
        for f in findings:
            code = f.get(key)
            if code in counts:
                counts[code] += 1
        out.append(heading)
        out.append(sub)
        for code in codes:
            n = counts[code]
            tally = str(n) if n else "—"
            out.append(f"  {code}  {titles[code]:<50} {tally}")
        out.append("")

    crits = [f for f in findings if f["severity"] == "Critical"]
    if crits:
        out.append("CRITICAL FINDINGS")
        out.append(sub)
        for f in crits:
            out.extend(_wrap(f"{f['id']}  {f['summary']}", indent="  ", subsequent="            "))
            actions = f["recommended_actions"]
            for k, action in enumerate(actions):
                prefix = "Action: " if len(actions) == 1 else f"Action {k+1}: "
                lead = "      "
                out.extend(_wrap(prefix + strip_tags(action),
                                 indent=lead, subsequent=lead + " " * len(prefix)))
            out.append("")

    out.append(bar)
    out.append("Built on OWASP Top 10 for LLM Applications 2025  |  OWASP Top 10 for Agentic Applications 2026"
               "  |  RAISE Framework")
    out.append("Generated by Praxen  |  project sponsor: Exabeam (https://www.exabeam.com/)")
    out.append("github.com/open-agent-ai-security/praxen  |  Apache-2.0")
    out.append(bar)
    return "\n".join(out) + "\n"


# ── I/O ──────────────────────────────────────────────────────────────────────
def _write(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)


def _load_json(path: str):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        sys.exit(f"render.py: findings file not found: {path}")
    except OSError as e:
        sys.exit(f"render.py: cannot read {path}: {e}")
    except json.JSONDecodeError as e:
        sys.exit(f"render.py: {path}: invalid JSON ({e})")


def _read_template(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError as e:
        sys.exit(f"render.py: cannot read template {path}: {e}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="render.py",
        description="Render a Praxen canonical findings JSON to HTML and/or TXT.")
    ap.add_argument("--findings", required=True, metavar="PATH",
                    help="canonical findings JSON (Stage-1 output)")
    ap.add_argument("--template", metavar="PATH",
                    help="report_template.html (required when --out-html is given)")
    ap.add_argument("--out-html", dest="out_html", metavar="PATH",
                    help="write the rendered HTML report here")
    ap.add_argument("--out-txt", dest="out_txt", metavar="PATH",
                    help="write the plain-text summary here")
    args = ap.parse_args(argv)

    if not args.out_html and not args.out_txt:
        ap.error("at least one of --out-html / --out-txt is required")
    if args.out_html and not args.template:
        ap.error("--template is required when --out-html is given")

    data = _load_json(args.findings)
    try:
        schema.validate(data)
    except SchemaError as e:
        sys.exit(f"render.py: schema validation failed — {e}")

    # Schema validation passed — `schema.validate` raises on any failure, so
    # reaching this point means zero schema errors. The summary line below
    # reports that explicitly so the operator has a positive confirmation
    # without having to re-read the validator's silence.
    n_findings = len(data["findings"])
    summary = f"{n_findings} findings, 0 schema errors"

    if args.out_html:
        try:
            html_out = render_html(_read_template(args.template), data)
        except RenderError as e:
            sys.exit(f"render.py: HTML render error — {e}")
        _write(args.out_html, html_out)
        print(f"render.py: wrote {args.out_html} ({summary})")

    if args.out_txt:
        _write(args.out_txt, render_txt(data))
        print(f"render.py: wrote {args.out_txt} ({summary})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
