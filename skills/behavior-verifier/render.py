#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Praxa report renderer — turns a canonical findings JSON into HTML and TXT.

Stage 2 of the Praxa pipeline. Deterministic: the same JSON in produces
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

Python 3.8+ stdlib only. No third-party dependencies.
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

_LOG_STATUS_CLASS = {"active": "log-status-active", "new": "log-status-new"}
_LOG_STATUS_LABEL = {"active": "Active", "new": "New"}

_SCORE_CLASS = {0: "score-0-1", 1: "score-0-1", 2: "score-2",
                3: "score-3", 4: "score-4-5", 5: "score-4-5"}

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
    like) can never collide with — or get mistaken for — a Praxa template placeholder.
    Renders identically to the literal braces in a browser."""
    return s.replace("{{", "&#123;&#123;").replace("}}", "&#125;&#125;")


def esc(value) -> str:
    """HTML-escape a value for either text content or an attribute value, and
    neutralise any literal ``{{...}}`` (see ``_neutralise_braces``)."""
    return _neutralise_braces(html.escape(str(value)))


def render_rich(text, allow=("code",)) -> str:
    """Escape ``text`` but preserve a small allowlist of inline tags.

    The Praxa skill emits these fields as plain prose plus, at most, the tags in
    ``allow`` (``<p>`` / ``<code>`` / ``<strong>`` / ``<em>``). We protect those
    exact tags, escape everything else, then restore them — so an unbalanced
    ``<`` in the prose is rendered as text, not as a stray tag, and a tag the
    skill reached for that is *not* in ``allow`` shows as escaped text rather
    than affecting layout. Literal ``{{...}}`` is neutralised too.
    """
    text = str(text)
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
    and every other HTML-ish tag (``<p>``, ``<code>``, ``<strong>``, a stray
    ``<a ...>``, …) is dropped. A lone ``<`` that is not a tag is left alone."""
    t = re.sub(r"\s*</p\s*>\s*", " ", str(text), flags=re.IGNORECASE)
    t = re.sub(r"</?[a-zA-Z][^>]*>", "", t)
    return t


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
    carries the Praxa attribution and the project-sponsor link.
    """
    return re.sub(r"<!--.*?-->", "", tpl, flags=re.DOTALL)


def assert_fully_rendered(tpl: str) -> None:
    leftovers = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", tpl)))
    if leftovers:
        raise RenderError(f"unsubstituted placeholders remain: {leftovers}")
    for marker in ("REPEAT:", "END:", "PICK:", "Variant A:", "Variant B:"):
        if re.search(rf"<!--\s*{re.escape(marker)}", tpl):
            raise RenderError(f"unresolved template marker remains: <!-- {marker} ...")


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


def _finding_tag_ctx(tag, _idx):
    return {"TAG_CLASS": _TAG_CLASS[tag["kind"]], "TAG_LABEL": esc(tag["label"])}


def _expand_finding_tags(block, finding):
    return expand_repeat(block, "finding_tag", finding["tags"], _finding_tag_ctx)


def _finding_ctx(finding, _idx):
    return {
        "FINDING_ANCHOR": esc(finding["id"]),
        "SEVERITY_CLASS": _SEV_CLASS[finding["severity"]],
        "SEVERITY_LABEL": _SEV_LABEL[finding["severity"]],
        "FINDING_ID": esc(finding["id"]),
        "FINDING_SUMMARY": esc(finding["summary"]),
        "RULE_IDS": esc(finding["policy_rule_ids"]),
        "QUOTED_RULE_TEXT": esc(finding["policy_rule_text"]),
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
        "SCAN_DATE": esc(scan["scan_date"]),
        "SCAN_TIMESTAMP": esc(scan["scan_timestamp"]),
        "ARTIFACT_COUNT": str(scan["artifact_count"]),
        "PRAXA_VERSION": esc(data["praxa_version"]),
        "OVERALL_STATUS_CLASS": status_cls,
        "OVERALL_STATUS_LABEL": status_label,
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
    tpl = expand_repeat(tpl, "finding", findings_sorted, _finding_ctx, inner=_expand_finding_tags)
    tpl = expand_repeat(
        tpl, "positive", data["positives"], _positive_ctx,
        empty_replacement='<div class="none-found">No confirmed positive controls '
                          'were verified during this scan.</div>',
    )
    cats_sorted = sorted(data["raise_posture"]["categories"], key=lambda c: RAISE_KEYS.index(c["key"]))
    tpl = expand_repeat(tpl, "raise_card", cats_sorted, _raise_card_ctx)

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
    out.append("PRAXA — AGENT BEHAVIOR VERIFIER")
    out.append(f"Agent:    {scan['agent']}")
    out.append(f"Analysis: {scan['scan_timestamp']}")
    out.append(f"Praxa v{data['praxa_version']}")
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
    out.append("Generated by Praxa  |  project sponsor: Exabeam (https://www.exabeam.com/)")
    out.append("github.com/Exabeam/deckard  |  Apache-2.0")
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
        description="Render a Praxa canonical findings JSON to HTML and/or TXT.")
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

    if args.out_html:
        try:
            html_out = render_html(_read_template(args.template), data)
        except RenderError as e:
            sys.exit(f"render.py: HTML render error — {e}")
        _write(args.out_html, html_out)
        print(f"render.py: wrote {args.out_html}")

    if args.out_txt:
        _write(args.out_txt, render_txt(data))
        print(f"render.py: wrote {args.out_txt}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
