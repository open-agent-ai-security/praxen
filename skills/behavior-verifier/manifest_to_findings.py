#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Praxen draft-manifest → canonical findings JSON converter.

Stage 1.5 of the Praxen pipeline. The behavior-verifier skill writes a
parser-grade markdown manifest at Step 9.9; this module reads it and emits the
canonical findings JSON that Stage 2 (`render.py`) consumes.

Deterministic and mechanical: the same manifest in produces byte-identical
JSON out every time. No judgment, no inference. `schema.py` validates the
emitted dict before it touches disk; a malformed manifest is a skill bug, not
something the converter papers over — it stops here with a message naming the
offending manifest line or JSON path.

Manifest format (Step 9.9, `manifest_format_version: 1`):

  ## section
  - field_name: value                   flat field at depth 0
  - array_field:                        array — items at depth 2
    - item_first_field: value           array item starts with `- ` at depth 2
      item_next_field: value            continuation at depth 4, no bullet
    - item_first_field: value           next item

  ### subsection                        either a prose block or a nested section

  #### R-NN                             rule separator inside remit_coverage.rules
  ### PRAX-YYYY-MM-DD-NNN (Severity)    finding separator inside findings

Prose sections (paragraphs under a heading, not bullets):

  intro_band.agent_remit_summary
  intro_band.agent_structure_summary
  behavior_summary
  raise_posture.weighted_rationale

Usage:
  python manifest_to_findings.py --manifest M.md --out F.json

Exit code 0 on success; non-zero with a diagnostic on any error.

Python 3.9+ stdlib only. No third-party dependencies.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

# schema.py and manifest_to_findings.py ship together in skills/behavior-verifier/.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schema  # noqa: E402
from schema import SchemaError  # noqa: E402


# Manifest format version this converter understands. The manifest's
# `manifest_format_version` (first bullet under `## scan`) must equal this.
MANIFEST_FORMAT_VERSION = 1


class ManifestError(ValueError):
    """Raised when the draft manifest cannot be parsed cleanly."""


# ── value coercion ───────────────────────────────────────────────────────────
# Per-section field types. Fields not listed here default to string.
# `null` is permitted everywhere a type is `str_or_none`, `int_or_none`, etc.
_NULL = object()  # sentinel: caller treats as None

_SCAN_FIELD_TYPES = {
    "agent": "str",
    "agent_slug": "str",
    "schema_version": "str",          # strip surrounding quotes if present
    "praxen_version": "str",
    "scan_date": "str",
    "scan_timestamp": "str",
    "workspace": "str",
    "artifact_count": "int",
    "manifest_format_version": "int",
}

_RAISE_POSTURE_FIELD_TYPES = {
    "weighted_overall": "float",
}

_RAISE_CATEGORY_FIELD_TYPES = {
    "key": "str",
    "name": "str",
    "score": "int",
    "confidence": "str",
    "weight": "float",
    "rationale": "str",
}

_REMIT_STAT_COUNT_FIELD_TYPES = {k: "int" for k in
    ("verified", "gap", "partial", "vague", "enp", "total")}

_RULE_FIELD_TYPES = {
    "section": "str",
    "rule_text": "str",
    "status": "str",
    "finding_id": "str_or_none",
}

_FINDING_FIELD_TYPES = {
    "id": "str",
    "severity": "str",
    "summary": "str",
    "description": "str_or_none",     # null means omit from JSON entirely
    "policy_rule_ids": "str_or_none",
    "policy_rule_text": "str_or_none",
    "raise_category": "str",
    "owasp_llm": "str_or_none",
    "owasp_agentic": "str_or_none",
    "confidence": "str",
    "escalation": "str",
    # tags / evidence / recommended_actions / related_findings are arrays —
    # handled separately.
}

_EVIDENCE_ITEM_FIELD_TYPES = {
    "file": "str",
    "line": "int_or_none",
    "snippet": "str",
}

_POSITIVE_ITEM_FIELD_TYPES = {
    "title": "str",
    "description": "str",
    "evidence_path": "str",
}

_LOG_FILES_FIELD_TYPES = {
    "present": "bool",
    "no_logs_note": "str_allow_empty",
}

_LOG_ROW_FIELD_TYPES = {
    "path": "str",
    "source": "str",
    "content_type": "str",
    "purpose": "str",
    "mtime": "str",
    "status": "str",
}

_FOOTER_SEVERITY_FIELD_TYPES = {k: "int" for k in
    ("critical", "high", "medium", "low", "info")}


def _coerce(raw, kind, lineno, fieldname):
    """Convert a raw string value to the declared Python type.

    raw is the substring after `field_name: ` with trailing whitespace stripped.
    lineno/fieldname are used only for error messages.
    """
    if raw is None:
        return None
    if kind.endswith("_or_none") and raw.strip() == "null":
        return None
    if kind == "str_or_none":
        return raw  # null already handled above
    if kind in ("str", "str_allow_empty"):
        return raw
    if kind == "int" or kind == "int_or_none":
        try:
            return int(raw)
        except ValueError:
            raise ManifestError(
                f"line {lineno}: {fieldname!r}: expected integer, got {raw!r}")
    if kind == "float":
        try:
            return float(raw)
        except ValueError:
            raise ManifestError(
                f"line {lineno}: {fieldname!r}: expected number, got {raw!r}")
    if kind == "bool":
        if raw.strip() == "true":
            return True
        if raw.strip() == "false":
            return False
        raise ManifestError(
            f"line {lineno}: {fieldname!r}: expected true/false, got {raw!r}")
    raise AssertionError(f"unknown field kind {kind!r}")


# ── line classification helpers ──────────────────────────────────────────────
_HEADING_RE = re.compile(r"^(#{2,4})\s+(.*?)\s*$")
_FIELD_BULLET_RE = re.compile(r"^(\s*)- ([a-z_][a-z0-9_]*):\s?(.*?)\s*$")
_CONTINUATION_FIELD_RE = re.compile(r"^(\s*)([a-z_][a-z0-9_]*):\s?(.*?)\s*$")
_STRING_BULLET_RE = re.compile(r"^(\s*)- (.+?)\s*$")
_TAG_ITEM_RE = re.compile(
    r"^kind=([a-z_]+),\s+label=(.+?)\s*$")
_FINDING_HEADER_RE = re.compile(
    r"^(PRAX-\d{4}-\d{2}-\d{2}-\d{3})\s+\((Critical|High|Medium|Low|Informational)\)\s*$")
_RULE_HEADER_RE = re.compile(r"^(R-\d+)\s*$")


def _indent(line):
    """Count leading spaces (no tabs allowed in manifest)."""
    return len(line) - len(line.lstrip(" "))


def _is_heading(line):
    return _HEADING_RE.match(line) is not None


def _heading_info(line):
    """Return (level, text) for a `## …` / `### …` / `#### …` line, or None."""
    m = _HEADING_RE.match(line)
    if not m:
        return None
    return len(m.group(1)), m.group(2)


# ── primitive readers ────────────────────────────────────────────────────────
def _skip_blank(lines, i):
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    return i


def _read_flat_fields(lines, i, indent, field_types, lineno_base, *,
                      stop_on_heading=True):
    """Read flat field bullets `<indent>- key: value` into a dict.

    Stops at: a line at indent < `indent`, a non-field bullet at this indent
    (e.g., array marker), a heading (if `stop_on_heading`), or EOF.

    Returns (new_i, dict).
    """
    out = {}
    while i < len(lines):
        line = lines[i]
        if line.strip() == "":
            i += 1
            continue
        if stop_on_heading and _is_heading(line):
            break
        if _indent(line) < indent:
            break
        m = _FIELD_BULLET_RE.match(line)
        if not m:
            break
        if len(m.group(1)) != indent:
            # bullet at deeper indent — array marker, not a flat field
            break
        key = m.group(2)
        raw = m.group(3)
        if key not in field_types:
            raise ManifestError(
                f"line {lineno_base + i + 1}: unknown field {key!r} in this section")
        # Handle array-marker bullets where the value is empty (e.g. `- tags:`).
        # Caller may special-case these before calling this function; here we
        # only consume scalar fields, so an empty value is recorded as-is.
        out[key] = _coerce(raw, field_types[key], lineno_base + i + 1, key)
        i += 1
    return i, out


def _read_prose_block(lines, i):
    """Read paragraph lines under a heading until the next heading or EOF.

    Concatenates non-blank lines with single spaces, preserves paragraph breaks
    as ``\\n\\n``. Trailing whitespace is stripped from the returned string.
    """
    paragraphs = []
    current = []
    while i < len(lines):
        line = lines[i]
        if _is_heading(line):
            break
        if line.strip() == "":
            if current:
                paragraphs.append(" ".join(current))
                current = []
            i += 1
            continue
        # In prose blocks, indent is preserved as part of the text only if
        # it's part of a quoted/code block; for our use case (single-paragraph
        # human prose), we strip leading whitespace.
        current.append(line.strip())
        i += 1
    if current:
        paragraphs.append(" ".join(current))
    return i, "\n\n".join(paragraphs).strip()


def _read_array_of_items(lines, i, item_indent, item_field_types, lineno_base,
                         *, item_label):
    """Read an array whose items start with `<item_indent>- first_field: value`
    and continue with `<item_indent + 2>next_field: value` lines (no bullet).

    Stops when a non-matching bullet/continuation appears at this indent, or
    indent drops below `item_indent`, or a heading appears, or EOF.

    Returns (new_i, list_of_dicts).
    """
    out = []
    cont_indent = item_indent + 2
    current = None
    while i < len(lines):
        line = lines[i]
        if line.strip() == "":
            i += 1
            continue
        if _is_heading(line):
            break
        ind = _indent(line)
        if ind < item_indent:
            break
        if ind == item_indent:
            m = _FIELD_BULLET_RE.match(line)
            if not m:
                break
            if current is not None:
                out.append(current)
            key = m.group(2)
            raw = m.group(3)
            if key not in item_field_types:
                raise ManifestError(
                    f"line {lineno_base + i + 1}: {item_label}: unknown field "
                    f"{key!r} (item must start with one of {sorted(item_field_types)})")
            current = {key: _coerce(raw, item_field_types[key],
                                    lineno_base + i + 1, key)}
            i += 1
            continue
        if ind == cont_indent and current is not None:
            m = _CONTINUATION_FIELD_RE.match(line)
            if not m:
                raise ManifestError(
                    f"line {lineno_base + i + 1}: {item_label}: expected "
                    f"continuation field at indent {cont_indent}, got {line!r}")
            key = m.group(2)
            raw = m.group(3)
            if key not in item_field_types:
                raise ManifestError(
                    f"line {lineno_base + i + 1}: {item_label}: unknown field "
                    f"{key!r}")
            if key in current:
                raise ManifestError(
                    f"line {lineno_base + i + 1}: {item_label}: duplicate field "
                    f"{key!r} in item")
            current[key] = _coerce(raw, item_field_types[key],
                                   lineno_base + i + 1, key)
            i += 1
            continue
        # Deeper than continuation, or shallower than item but greater than
        # the containing section — that's a format error.
        raise ManifestError(
            f"line {lineno_base + i + 1}: {item_label}: unexpected indent "
            f"{ind} (item bullets at {item_indent}, continuations at {cont_indent})")
    if current is not None:
        out.append(current)
    return i, out


def _read_string_array(lines, i, item_indent, lineno_base, *, item_label):
    """Read an array of single-string items, each ``<item_indent>- text``."""
    out = []
    while i < len(lines):
        line = lines[i]
        if line.strip() == "":
            i += 1
            continue
        if _is_heading(line):
            break
        ind = _indent(line)
        if ind < item_indent:
            break
        if ind != item_indent:
            raise ManifestError(
                f"line {lineno_base + i + 1}: {item_label}: unexpected indent {ind}")
        m = _STRING_BULLET_RE.match(line)
        if not m:
            break
        out.append(m.group(2))
        i += 1
    return i, out


def _read_tag_array(lines, i, item_indent, lineno_base):
    """Read finding tags: each item is ``<item_indent>- kind=K, label=L``."""
    out = []
    while i < len(lines):
        line = lines[i]
        if line.strip() == "":
            i += 1
            continue
        if _is_heading(line):
            break
        ind = _indent(line)
        if ind < item_indent:
            break
        if ind != item_indent:
            raise ManifestError(
                f"line {lineno_base + i + 1}: tag item: unexpected indent {ind}")
        m = _STRING_BULLET_RE.match(line)
        if not m:
            break
        body = m.group(2)
        tm = _TAG_ITEM_RE.match(body)
        if not tm:
            raise ManifestError(
                f"line {lineno_base + i + 1}: tag item: expected "
                f"`kind=K, label=L`, got {body!r}")
        out.append({"kind": tm.group(1), "label": tm.group(2)})
        i += 1
    return i, out


# ── section parsers ──────────────────────────────────────────────────────────
def _parse_scan_section(lines, i):
    """Parse `## scan`. Returns (new_i, {schema_version, praxen_version, scan})."""
    i = _skip_blank(lines, i)
    i, fields = _read_flat_fields(lines, i, 0, _SCAN_FIELD_TYPES, lineno_base=0)
    # Required: manifest_format_version, schema_version, praxen_version
    mfv = fields.pop("manifest_format_version", None)
    if mfv is None:
        raise ManifestError("## scan: missing `manifest_format_version` bullet")
    if mfv != MANIFEST_FORMAT_VERSION:
        raise ManifestError(
            f"## scan: manifest_format_version is {mfv}; this converter "
            f"understands version {MANIFEST_FORMAT_VERSION}")
    sv = fields.pop("schema_version", None)
    pv = fields.pop("praxen_version", None)
    if sv is None or pv is None:
        raise ManifestError(
            "## scan: `schema_version` and `praxen_version` are required")
    # The manifest may quote schema_version (`"2.0"`); strip surrounding quotes.
    sv = sv.strip()
    if sv.startswith('"') and sv.endswith('"') and len(sv) >= 2:
        sv = sv[1:-1]
    return i, {"schema_version": sv, "praxen_version": pv, "scan": fields}


def _parse_intro_band_section(lines, i):
    """Parse `## intro_band` — two `### subsection` prose blocks."""
    out = {}
    while i < len(lines):
        i = _skip_blank(lines, i)
        if i >= len(lines):
            break
        line = lines[i]
        info = _heading_info(line)
        if info is None:
            break
        level, text = info
        if level == 2:
            break  # next `## section`
        if level != 3:
            raise ManifestError(
                f"line {i + 1}: intro_band: expected `### subsection` heading, got {line!r}")
        key = text.strip()
        if key not in ("agent_remit_summary", "agent_structure_summary"):
            raise ManifestError(
                f"line {i + 1}: intro_band: unknown subsection {key!r}")
        i += 1
        i, prose = _read_prose_block(lines, i)
        if not prose:
            raise ManifestError(
                f"intro_band.{key}: prose body is required (non-empty)")
        out[key] = prose
    return i, out


def _parse_behavior_summary_section(lines, i):
    """Parse `## behavior_summary` — single prose block under the section."""
    i = _skip_blank(lines, i)
    i, prose = _read_prose_block(lines, i)
    if not prose:
        raise ManifestError("## behavior_summary: prose body is required (non-empty)")
    return i, prose


def _parse_raise_posture_section(lines, i):
    """Parse `## raise_posture` — flat `weighted_overall` bullet, then
    `### weighted_rationale` prose, then `### categories` array."""
    i = _skip_blank(lines, i)
    i, top = _read_flat_fields(lines, i, 0, _RAISE_POSTURE_FIELD_TYPES,
                               lineno_base=0)
    if "weighted_overall" not in top:
        raise ManifestError("## raise_posture: missing `- weighted_overall: …` bullet")
    out = {
        "weighted_overall": top["weighted_overall"],
        "weighted_rationale": None,
        "categories": None,
    }
    # Now `### weighted_rationale` (prose) and `### categories` (array of items).
    while i < len(lines):
        i = _skip_blank(lines, i)
        if i >= len(lines):
            break
        info = _heading_info(lines[i])
        if info is None:
            break
        level, text = info
        if level == 2:
            break
        if level != 3:
            raise ManifestError(
                f"line {i + 1}: raise_posture: expected `### subsection`, got {lines[i]!r}")
        sub = text.strip()
        i += 1
        if sub == "weighted_rationale":
            i, prose = _read_prose_block(lines, i)
            if not prose:
                raise ManifestError("raise_posture.weighted_rationale: prose required")
            out["weighted_rationale"] = prose
        elif sub == "categories":
            i = _skip_blank(lines, i)
            i, cats = _read_array_of_items(
                lines, i, 0, _RAISE_CATEGORY_FIELD_TYPES,
                lineno_base=0, item_label="raise category")
            out["categories"] = cats
        else:
            raise ManifestError(
                f"line {i}: raise_posture: unknown subsection {sub!r}")
    if out["weighted_rationale"] is None:
        raise ManifestError("## raise_posture: missing `### weighted_rationale`")
    if out["categories"] is None:
        raise ManifestError("## raise_posture: missing `### categories`")
    return i, out


def _parse_remit_coverage_section(lines, i):
    """Parse `## remit_coverage` — `### stat_counts` (flat bullets) and
    `### rules` (array of rules, each separated by `#### R-NN` heading)."""
    out = {"stat_counts": None, "rules": None}
    while i < len(lines):
        i = _skip_blank(lines, i)
        if i >= len(lines):
            break
        info = _heading_info(lines[i])
        if info is None:
            break
        level, text = info
        if level == 2:
            break
        if level != 3:
            raise ManifestError(
                f"line {i + 1}: remit_coverage: expected `### subsection`, got {lines[i]!r}")
        sub = text.strip()
        i += 1
        if sub == "stat_counts":
            i = _skip_blank(lines, i)
            i, sc = _read_flat_fields(lines, i, 0,
                                      _REMIT_STAT_COUNT_FIELD_TYPES,
                                      lineno_base=0)
            out["stat_counts"] = sc
        elif sub == "rules":
            i, rules = _parse_rules_subsection(lines, i)
            out["rules"] = rules
        else:
            raise ManifestError(
                f"line {i}: remit_coverage: unknown subsection {sub!r}")
    if out["stat_counts"] is None:
        raise ManifestError("## remit_coverage: missing `### stat_counts`")
    if out["rules"] is None:
        raise ManifestError("## remit_coverage: missing `### rules`")
    return i, out


def _parse_rules_subsection(lines, i):
    """Parse the body of `### rules` — repeating `#### R-NN` blocks."""
    rules = []
    while i < len(lines):
        i = _skip_blank(lines, i)
        if i >= len(lines):
            break
        info = _heading_info(lines[i])
        if info is None:
            break
        level, text = info
        if level <= 3:
            break  # back up to `## ` or `### `
        if level != 4:
            raise ManifestError(
                f"line {i + 1}: rules: expected `#### R-NN`, got {lines[i]!r}")
        m = _RULE_HEADER_RE.match(text.strip())
        if not m:
            raise ManifestError(
                f"line {i + 1}: rules: expected `#### R-NN`, got {text!r}")
        rule_id = m.group(1)
        i += 1
        i = _skip_blank(lines, i)
        i, fields = _read_flat_fields(lines, i, 0, _RULE_FIELD_TYPES,
                                      lineno_base=0)
        rule = {"rule_id": rule_id}
        rule.update(fields)
        # Required fields: section, rule_text, status, finding_id (may be null).
        for k in ("section", "rule_text", "status"):
            if k not in rule:
                raise ManifestError(
                    f"rule {rule_id}: missing required `- {k}: …` bullet")
        if "finding_id" not in rule:
            raise ManifestError(
                f"rule {rule_id}: missing `- finding_id: …` bullet "
                "(use `null` if no linked finding)")
        rules.append(rule)
    return i, rules


def _parse_findings_section(lines, i):
    """Parse `## findings` — repeating `### PRAX-... (Severity)` blocks."""
    findings = []
    while i < len(lines):
        i = _skip_blank(lines, i)
        if i >= len(lines):
            break
        info = _heading_info(lines[i])
        if info is None:
            break
        level, text = info
        if level == 2:
            break  # next `## section`
        if level != 3:
            raise ManifestError(
                f"line {i + 1}: findings: expected `### PRAX-…`, got {lines[i]!r}")
        m = _FINDING_HEADER_RE.match(text.strip())
        if not m:
            raise ManifestError(
                f"line {i + 1}: findings: expected `### PRAX-YYYY-MM-DD-NNN (Severity)`, "
                f"got {text!r}")
        # The id/severity in the heading is informational; the authoritative
        # values come from the `- id:` / `- severity:` bullets below. (The
        # parser checks they agree.)
        heading_id = m.group(1)
        heading_severity = m.group(2)
        i += 1
        i, fdg = _parse_one_finding(lines, i)
        if fdg.get("id") != heading_id:
            raise ManifestError(
                f"finding {heading_id}: `- id:` bullet ({fdg.get('id')!r}) "
                f"disagrees with `### …` heading id ({heading_id!r})")
        if fdg.get("severity") != heading_severity:
            raise ManifestError(
                f"finding {heading_id}: `- severity:` bullet ({fdg.get('severity')!r}) "
                f"disagrees with `### …` heading severity ({heading_severity!r})")
        findings.append(fdg)
    return i, findings


def _parse_one_finding(lines, i):
    """Parse the bullets of one finding (everything between its `### …` heading
    and the next heading)."""
    out = {}
    while i < len(lines):
        if i >= len(lines):
            break
        line = lines[i]
        if line.strip() == "":
            i += 1
            continue
        if _is_heading(line):
            break
        ind = _indent(line)
        if ind != 0:
            raise ManifestError(
                f"line {i + 1}: finding: unexpected indent {ind}; finding fields "
                "must be flat bullets at depth 0")
        m = _FIELD_BULLET_RE.match(line)
        if not m:
            break
        key = m.group(2)
        raw = m.group(3)
        if key == "tags":
            if raw.strip() != "":
                raise ManifestError(
                    f"line {i + 1}: finding {out.get('id')!r}: `- tags:` must be "
                    "followed by sub-bullets, not an inline value")
            i += 1
            i, tags = _read_tag_array(lines, i, item_indent=2, lineno_base=0)
            if not tags:
                raise ManifestError(
                    f"finding {out.get('id', '?')!r}: tags[] requires at least one item")
            out["tags"] = tags
            continue
        if key == "evidence":
            if raw.strip() != "":
                raise ManifestError(
                    f"line {i + 1}: finding: `- evidence:` must be followed by sub-bullets")
            i += 1
            i, items = _read_array_of_items(
                lines, i, item_indent=2,
                item_field_types=_EVIDENCE_ITEM_FIELD_TYPES,
                lineno_base=0, item_label="evidence item")
            if not items:
                raise ManifestError(
                    f"finding {out.get('id', '?')!r}: evidence[] requires at least one item")
            # Required per item: file, line (may be null), snippet.
            for ei, item in enumerate(items):
                for req in ("file", "line", "snippet"):
                    if req not in item:
                        raise ManifestError(
                            f"finding {out.get('id', '?')!r}: evidence[{ei}]: "
                            f"missing required field {req!r}")
            out["evidence"] = items
            continue
        if key == "recommended_actions":
            if raw.strip() != "":
                raise ManifestError(
                    f"line {i + 1}: finding: `- recommended_actions:` must be "
                    "followed by sub-bullets")
            i += 1
            i, items = _read_string_array(lines, i, item_indent=2,
                                          lineno_base=0,
                                          item_label="recommended_actions item")
            if not items:
                raise ManifestError(
                    f"finding {out.get('id', '?')!r}: recommended_actions[] "
                    "requires at least one item")
            out["recommended_actions"] = items
            continue
        if key == "related_findings":
            # Comma-separated PRAX-… ids, or empty for none.
            stripped = raw.strip()
            if stripped == "":
                out["related_findings"] = []
            else:
                out["related_findings"] = [
                    s.strip() for s in stripped.split(",") if s.strip()]
            i += 1
            continue
        if key not in _FINDING_FIELD_TYPES:
            raise ManifestError(
                f"line {i + 1}: finding: unknown field {key!r}")
        value = _coerce(raw, _FINDING_FIELD_TYPES[key], i + 1, key)
        if key == "description" and value is None:
            # `- description: null` means omit the key from the JSON entirely
            # (the schema treats `description` as optional and rejects null).
            pass
        else:
            out[key] = value
        i += 1
    # `description: null` was suppressed above. Anything else missing is a
    # schema problem, surfaced by schema.validate later.
    return i, out


def _parse_positives_section(lines, i):
    """Parse `## positives` — array of items, or `(none)` for empty."""
    i = _skip_blank(lines, i)
    # `(none)` marker on a line by itself = empty array.
    if i < len(lines) and lines[i].strip() == "(none)":
        return i + 1, []
    i, items = _read_array_of_items(
        lines, i, item_indent=0,
        item_field_types=_POSITIVE_ITEM_FIELD_TYPES,
        lineno_base=0, item_label="positive item")
    for pi, item in enumerate(items):
        for req in ("title", "description", "evidence_path"):
            if req not in item:
                raise ManifestError(
                    f"positives[{pi}]: missing required field {req!r}")
    return i, items


def _parse_log_files_section(lines, i):
    """Parse `## log_files` — flat bullets (`present`, `no_logs_note`) and
    `### rows` array (empty when `present=false`)."""
    i = _skip_blank(lines, i)
    i, flat = _read_flat_fields(lines, i, 0, _LOG_FILES_FIELD_TYPES,
                                lineno_base=0)
    if "present" not in flat:
        raise ManifestError("## log_files: missing `- present: …` bullet")
    if "no_logs_note" not in flat:
        raise ManifestError("## log_files: missing `- no_logs_note: …` bullet")
    rows = []
    # Optional `### rows` subsection.
    if i < len(lines):
        i = _skip_blank(lines, i)
        if i < len(lines):
            info = _heading_info(lines[i])
            if info is not None and info[0] == 3 and info[1].strip() == "rows":
                i += 1
                i = _skip_blank(lines, i)
                # `(empty)` marker on a line = no rows.
                if i < len(lines) and lines[i].strip() == "(empty)":
                    i += 1
                else:
                    i, rows = _read_array_of_items(
                        lines, i, item_indent=0,
                        item_field_types=_LOG_ROW_FIELD_TYPES,
                        lineno_base=0, item_label="log_files row")
                    for ri, row in enumerate(rows):
                        for req in _LOG_ROW_FIELD_TYPES:
                            if req not in row:
                                raise ManifestError(
                                    f"log_files.rows[{ri}]: missing required "
                                    f"field {req!r}")
    return i, {"present": flat["present"],
               "no_logs_note": flat["no_logs_note"],
               "rows": rows}


def _parse_footer_section(lines, i):
    """Parse `## footer` — `### severity_counts` block."""
    i = _skip_blank(lines, i)
    if i >= len(lines):
        raise ManifestError("## footer: missing `### severity_counts`")
    info = _heading_info(lines[i])
    if info is None or info[0] != 3 or info[1].strip() != "severity_counts":
        raise ManifestError(
            f"line {i + 1}: footer: expected `### severity_counts`, got {lines[i]!r}")
    i += 1
    i = _skip_blank(lines, i)
    i, sc = _read_flat_fields(lines, i, 0, _FOOTER_SEVERITY_FIELD_TYPES,
                              lineno_base=0)
    for k in ("critical", "high", "medium", "low", "info"):
        if k not in sc:
            raise ManifestError(
                f"## footer.severity_counts: missing `- {k}: …` bullet")
    return i, {"severity_counts": sc}


# ── top-level orchestrator ───────────────────────────────────────────────────
_SECTION_DISPATCH = {
    "scan":             _parse_scan_section,
    "intro_band":       _parse_intro_band_section,
    "behavior_summary": _parse_behavior_summary_section,
    "raise_posture":    _parse_raise_posture_section,
    "remit_coverage":   _parse_remit_coverage_section,
    "findings":         _parse_findings_section,
    "positives":        _parse_positives_section,
    "log_files":        _parse_log_files_section,
    "footer":           _parse_footer_section,
}


def parse_manifest(text):
    """Parse a Praxen draft manifest into the canonical findings dict.

    Does NOT validate against `schema.py` — call ``schema.validate(result)``
    on the returned dict before writing JSON. Raises ``ManifestError`` on any
    structural problem in the manifest itself.
    """
    lines = text.splitlines()
    # Skip leading title (e.g., `# Praxen draft manifest`) and any preamble.
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("# ") and not line.startswith("## "):
            i += 1
            continue
        if line.strip() == "" or line.startswith("---"):
            i += 1
            continue
        break

    data = {}
    seen_sections = set()
    while i < len(lines):
        line = lines[i]
        if line.strip() == "":
            i += 1
            continue
        info = _heading_info(line)
        if info is None:
            raise ManifestError(
                f"line {i + 1}: expected `## section` heading, got {line!r}")
        level, text_name = info
        if level != 2:
            raise ManifestError(
                f"line {i + 1}: expected a top-level `## section` heading, "
                f"got `{'#' * level} {text_name}`")
        name = text_name.strip()
        if name not in _SECTION_DISPATCH:
            raise ManifestError(
                f"line {i + 1}: unknown section {name!r}")
        if name in seen_sections:
            raise ManifestError(
                f"line {i + 1}: duplicate section `## {name}`")
        seen_sections.add(name)
        i += 1
        new_i, payload = _SECTION_DISPATCH[name](lines, i)
        i = new_i
        if name == "scan":
            # `_parse_scan_section` returns the JSON-top-level + scan dict.
            data.update(payload)
        else:
            data[name] = payload

    # Check completeness — every required section must be present.
    required = set(_SECTION_DISPATCH.keys())
    missing = required - seen_sections
    if missing:
        raise ManifestError(
            f"manifest is missing required sections: {sorted(missing)}")

    # Re-emit the dict in canonical JSON key order. The manifest's natural
    # author-facing order puts `raise_posture` next to the RAISE work
    # (after behavior_summary); the canonical JSON puts it next to footer
    # so it remains a wrap-up block. We rearrange here so the JSON byte order
    # matches the schema's required-field declaration order — meaningful for
    # diff stability across re-renders.
    canonical = {}
    for key in (
        "schema_version", "praxen_version", "scan",
        "intro_band", "behavior_summary",
        "remit_coverage", "findings", "positives", "log_files",
        "raise_posture", "footer",
    ):
        if key in data:
            canonical[key] = data[key]
    return canonical


# ── I/O ──────────────────────────────────────────────────────────────────────
def _read_manifest(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        sys.exit(f"manifest_to_findings.py: manifest not found: {path}")
    except OSError as e:
        sys.exit(f"manifest_to_findings.py: cannot read {path}: {e}")


def _write_json(path, data):
    """Write `data` as pretty-printed JSON. Determinism: indent=2, no key sort
    (the dict is built in canonical order by the parser); newline at EOF."""
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="manifest_to_findings.py",
        description="Convert a Praxen Step 9.9 draft manifest into the canonical findings JSON.")
    ap.add_argument("--manifest", required=True, metavar="PATH",
                    help="draft manifest (Step 9.9 output)")
    ap.add_argument("--out", required=True, metavar="PATH",
                    help="write the canonical findings JSON here")
    args = ap.parse_args(argv)

    text = _read_manifest(args.manifest)
    try:
        data = parse_manifest(text)
    except ManifestError as e:
        sys.exit(f"manifest_to_findings.py: {args.manifest}: {e}")

    try:
        schema.validate(data)
    except SchemaError as e:
        sys.exit(f"manifest_to_findings.py: schema validation failed — {e}")

    _write_json(args.out, data)
    n = len(data["findings"])
    print(f"manifest_to_findings.py: wrote {args.out} "
          f"({n} findings, {len(data['remit_coverage']['rules'])} rules)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
