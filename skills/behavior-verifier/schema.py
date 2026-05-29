#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Praxen canonical findings-JSON schema and validator.

Stage 1 of the Praxen pipeline (the behavior-verifier skill) emits a JSON
conforming to this schema. Stage 2 (render.py) consumes it. This module owns
the validation rules: shape, types, enumerations, required fields, and
cross-field consistency (counts, anchor resolution, RAISE category set,
weighted-overall sanity).

The validator is strict and fails loudly. A missing or malformed field is a
skill bug, never something the renderer should paper over — so it stops the
pipeline here with a message naming the offending JSON path.

Python 3.9+ stdlib only. No third-party dependencies.

The matching JSON-Schema document at `findings.schema.json` (alongside this
file) is the published machine-readable contract for downstream tooling;
`schema.py` stays the runtime validator. A test in `tests/render/test_render.py`
asserts the enums declared here and in the JSON-Schema doc agree.
"""
from __future__ import annotations

import math
import re

# ── version ──────────────────────────────────────────────────────────────────
# The schema major version this validator (and the bundled renderer) understands.
# A JSON with a different MAJOR is rejected; a newer MINOR is accepted.
SCHEMA_VERSION = "2.0"

# ── fixed enumerations ───────────────────────────────────────────────────────
RAISE_KEYS = [                       # canonical category order — never reorder
    "limit_your_domain",
    "balance_your_knowledge_base",
    "implement_zero_trust",
    "manage_your_supply_chain",
    "build_an_ai_red_team",
    "monitor_continuously",
]
RAISE_NAMES = {
    "limit_your_domain":           "Limit Your Domain",
    "balance_your_knowledge_base": "Balance Your Knowledge Base",
    "implement_zero_trust":        "Implement Zero Trust",
    "manage_your_supply_chain":    "Manage Your Supply Chain",
    "build_an_ai_red_team":        "Build an AI Red Team",
    "monitor_continuously":        "Monitor Continuously",
}
# Zero Trust counts double (0.25); the other five each count 0.15.
RAISE_WEIGHTS = {k: (0.25 if k == "implement_zero_trust" else 0.15) for k in RAISE_KEYS}

SEVERITIES = ["Critical", "High", "Medium", "Low", "Informational"]
SEVERITY_COUNT_KEYS = {              # finding.severity -> footer.severity_counts key
    "Critical": "critical", "High": "high", "Medium": "medium",
    "Low": "low", "Informational": "info",
}
REMIT_STATUSES = ["verified", "gap", "partial", "vague", "enp"]
CONFIDENCES = ["High", "Medium", "Low"]
TAG_KINDS = ["raise", "owasp_llm", "owasp_agentic", "mcp"]
LOG_STATUSES = ["active", "inferred"]
ESCALATIONS = ["alert", "log_only"]

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# Finding IDs are PRAX-YYYY-MM-DD-NNN — a three-digit sequence, so the
# implicit ceiling is 999 findings in a single scan. No real target has come
# close; if one ever does, widen the sequence here and in findings.schema.json.
_FINDING_ID_RE = re.compile(r"^PRAX-\d{4}-\d{2}-\d{2}-\d{3}$")
# OWASP taxonomy codes, canonical form: LLM01–LLM10, ASI01–ASI10. The `tags[]`
# label carries the full "CODE — Name" string; these scalar fields carry the
# code alone (or null).
_OWASP_LLM_RE = re.compile(r"^LLM(?:0[1-9]|10)$")
_OWASP_ASI_RE = re.compile(r"^ASI(?:0[1-9]|10)$")

# Escalation is a function of severity, not a free choice:
# Critical/High -> "alert"; Medium/Low/Informational -> "log_only".
_ESCALATION_FOR_SEVERITY = {
    "Critical": "alert", "High": "alert",
    "Medium": "log_only", "Low": "log_only", "Informational": "log_only",
}


class SchemaError(ValueError):
    """Raised when a findings JSON does not conform to the canonical schema."""


# ── small typed-accessor helpers ─────────────────────────────────────────────
def _err(path, msg):
    raise SchemaError(f"{path}: {msg}")


def _obj(value, path):
    if not isinstance(value, dict):
        _err(path, f"expected object, got {type(value).__name__}")
    return value


def _get(obj, key, path):
    _obj(obj, path)
    if key not in obj:
        _err(f"{path}.{key}", "required field is missing")
    return obj[key]


def _str(obj, key, path, *, allow_none=False):
    val = _get(obj, key, path)
    if val is None and allow_none:
        return None
    if not isinstance(val, str):
        _err(f"{path}.{key}", f"expected string, got {type(val).__name__}")
    return val


def _nonempty_str(obj, key, path):
    val = _str(obj, key, path)
    if not val.strip():
        _err(f"{path}.{key}", "must not be empty")
    return val


def _enum(obj, key, path, choices, *, allow_none=False):
    val = _str(obj, key, path, allow_none=allow_none)
    if val is None:
        return None
    if val not in choices:
        _err(f"{path}.{key}", f"must be one of {choices}; got {val!r}")
    return val


def _int(obj, key, path, *, minimum=None, maximum=None):
    val = _get(obj, key, path)
    if isinstance(val, bool) or not isinstance(val, int):
        _err(f"{path}.{key}", f"expected integer, got {type(val).__name__}")
    if minimum is not None and val < minimum:
        _err(f"{path}.{key}", f"must be >= {minimum}; got {val}")
    if maximum is not None and val > maximum:
        _err(f"{path}.{key}", f"must be <= {maximum}; got {val}")
    return val


def _number(obj, key, path, *, minimum=None, maximum=None):
    val = _get(obj, key, path)
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        _err(f"{path}.{key}", f"expected number, got {type(val).__name__}")
    val = float(val)
    if minimum is not None and val < minimum - 1e-9:
        _err(f"{path}.{key}", f"must be >= {minimum}; got {val}")
    if maximum is not None and val > maximum + 1e-9:
        _err(f"{path}.{key}", f"must be <= {maximum}; got {val}")
    return val


def _bool(obj, key, path):
    val = _get(obj, key, path)
    if not isinstance(val, bool):
        _err(f"{path}.{key}", f"expected boolean, got {type(val).__name__}")
    return val


def _list(obj, key, path, *, min_len=0):
    val = _get(obj, key, path)
    if not isinstance(val, list):
        _err(f"{path}.{key}", f"expected array, got {type(val).__name__}")
    if len(val) < min_len:
        _err(f"{path}.{key}", f"must contain at least {min_len} item(s); got {len(val)}")
    return val


def _str_list(value, path, *, allow_empty_items=False):
    if not isinstance(value, list):
        _err(path, f"expected array of strings, got {type(value).__name__}")
    out = []
    for i, item in enumerate(value):
        if not isinstance(item, str):
            _err(f"{path}[{i}]", f"expected string, got {type(item).__name__}")
        if not allow_empty_items and not item.strip():
            _err(f"{path}[{i}]", "must not be empty")
        out.append(item)
    return out


# ── section validators ───────────────────────────────────────────────────────
def _validate_version(data):
    sv = _nonempty_str(data, "schema_version", "$")
    want_major = SCHEMA_VERSION.split(".", 1)[0]
    got_major = sv.split(".", 1)[0]
    if got_major != want_major:
        _err("$.schema_version",
             f"renderer understands schema {want_major}.x; got {sv!r}")
    _nonempty_str(data, "praxen_version", "$")


def _validate_scan(data):
    scan = _obj(_get(data, "scan", "$"), "$.scan")
    _nonempty_str(scan, "agent", "$.scan")
    _nonempty_str(scan, "agent_slug", "$.scan")
    sd = _nonempty_str(scan, "scan_date", "$.scan")
    if not _DATE_RE.match(sd):
        _err("$.scan.scan_date", f"must be YYYY-MM-DD; got {sd!r}")
    _nonempty_str(scan, "scan_timestamp", "$.scan")
    _nonempty_str(scan, "workspace", "$.scan")
    _int(scan, "artifact_count", "$.scan", minimum=0)


def _validate_intro_band(data):
    ib = _obj(_get(data, "intro_band", "$"), "$.intro_band")
    _nonempty_str(ib, "agent_remit_summary", "$.intro_band")
    _nonempty_str(ib, "agent_structure_summary", "$.intro_band")


def _validate_behavior_summary(data):
    _nonempty_str(data, "behavior_summary", "$")


def _validate_remit_coverage(data):
    rc = _obj(_get(data, "remit_coverage", "$"), "$.remit_coverage")
    sc = _obj(_get(rc, "stat_counts", "$.remit_coverage"), "$.remit_coverage.stat_counts")
    for k in REMIT_STATUSES + ["total"]:
        _int(sc, k, "$.remit_coverage.stat_counts", minimum=0)
    rules = _list(rc, "rules", "$.remit_coverage", min_len=1)
    seen_ids = set()
    for i, rule in enumerate(rules):
        p = f"$.remit_coverage.rules[{i}]"
        _obj(rule, p)
        rid = _nonempty_str(rule, "rule_id", p)
        if rid in seen_ids:
            _err(f"{p}.rule_id", f"duplicate rule_id {rid!r}")
        seen_ids.add(rid)
        _nonempty_str(rule, "section", p)
        _nonempty_str(rule, "rule_text", p)
        _enum(rule, "status", p, REMIT_STATUSES)
        fid = _str(rule, "finding_id", p, allow_none=True)
        if fid is not None and not fid.strip():
            _err(f"{p}.finding_id", "must be a non-empty string or null")


def _validate_findings(data):
    findings = _list(data, "findings", "$")          # may legitimately be empty
    seen = set()
    for i, f in enumerate(findings):
        p = f"$.findings[{i}]"
        _obj(f, p)
        fid = _nonempty_str(f, "id", p)
        if fid in seen:
            _err(f"{p}.id", f"duplicate finding id {fid!r}")
        seen.add(fid)
        severity = _enum(f, "severity", p, SEVERITIES)
        _nonempty_str(f, "summary", p)
        tags = _list(f, "tags", p, min_len=1)
        for j, tag in enumerate(tags):
            tp = f"{p}.tags[{j}]"
            _obj(tag, tp)
            _enum(tag, "kind", tp, TAG_KINDS)
            _nonempty_str(tag, "label", tp)
        # policy_rule_ids / policy_rule_text are null together when the finding
        # does not trace to a specific remit rule (a RAISE-category or
        # detection-pattern finding), and non-empty strings together when it does.
        pri = _str(f, "policy_rule_ids", p, allow_none=True)
        if pri is not None and not pri.strip():
            _err(f"{p}.policy_rule_ids", "must be a non-empty string or null")
        prt = _str(f, "policy_rule_text", p, allow_none=True)
        if prt is not None and not prt.strip():
            _err(f"{p}.policy_rule_text", "must be a non-empty string or null")
        if (pri is None) != (prt is None):
            _err(p, "policy_rule_ids and policy_rule_text must both be set or both be "
                    "null (a finding either cites a remit rule or it does not)")
        ev = _list(f, "evidence", p, min_len=1)
        for j, item in enumerate(ev):
            ip = f"{p}.evidence[{j}]"
            _obj(item, ip)
            _nonempty_str(item, "file", ip)
            line_val = _get(item, "line", ip)
            if line_val is not None:
                if isinstance(line_val, bool) or not isinstance(line_val, int):
                    _err(f"{ip}.line", f"expected integer or null, got {type(line_val).__name__}")
                if line_val < 1:
                    _err(f"{ip}.line", f"must be >= 1 (1-indexed) or null; got {line_val}")
            _nonempty_str(item, "snippet", ip)
        actions = _list(f, "recommended_actions", p, min_len=1)
        _str_list(actions, f"{p}.recommended_actions")
        # `description` is optional — if present, must be a non-empty string.
        if "description" in f:
            val = f["description"]
            if not isinstance(val, str) or not val.strip():
                _err(f"{p}.description", "if present, must be a non-empty string")
        _enum(f, "raise_category", p, RAISE_KEYS)
        owasp_llm = _str(f, "owasp_llm", p, allow_none=True)
        if owasp_llm is not None and not _OWASP_LLM_RE.match(owasp_llm):
            _err(f"{p}.owasp_llm",
                 f"must be a canonical code LLM01–LLM10 or null; got {owasp_llm!r}")
        owasp_agentic = _str(f, "owasp_agentic", p, allow_none=True)
        if owasp_agentic is not None and not _OWASP_ASI_RE.match(owasp_agentic):
            _err(f"{p}.owasp_agentic",
                 f"must be a canonical code ASI01–ASI10 or null; got {owasp_agentic!r}")
        _enum(f, "confidence", p, CONFIDENCES)
        rel = _get(f, "related_findings", p)
        _str_list(rel, f"{p}.related_findings")
        for j, r in enumerate(rel or []):
            if not _FINDING_ID_RE.match(r):
                _err(f"{p}.related_findings[{j}]",
                     f"{r!r} is not a PRAX-YYYY-MM-DD-NNN id")
            if r == fid:
                _err(f"{p}.related_findings[{j}]",
                     f"finding {fid!r} lists its own id in related_findings")
        escalation = _enum(f, "escalation", p, ESCALATIONS)
        expected_esc = _ESCALATION_FOR_SEVERITY[severity]
        if escalation != expected_esc:
            _err(f"{p}.escalation",
                 f"must be {expected_esc!r} for a {severity} finding; got {escalation!r}")
    return findings, seen


def _validate_positives(data):
    pos = _list(data, "positives", "$")              # may be empty
    for i, item in enumerate(pos):
        p = f"$.positives[{i}]"
        _obj(item, p)
        _nonempty_str(item, "title", p)
        _nonempty_str(item, "description", p)
        _nonempty_str(item, "evidence_path", p)


def _validate_log_files(data):
    lf = _obj(_get(data, "log_files", "$"), "$.log_files")
    present = _bool(lf, "present", "$.log_files")
    _str(lf, "no_logs_note", "$.log_files")          # presence required; emptiness checked below
    rows = _list(lf, "rows", "$.log_files")
    if present:
        if len(rows) < 1:
            _err("$.log_files.rows", "must contain at least one row when present is true")
    else:
        if rows:
            _err("$.log_files.rows", "must be empty when present is false")
        if not lf["no_logs_note"].strip():
            _err("$.log_files.no_logs_note", "must not be empty when present is false")
    for i, row in enumerate(rows):
        p = f"$.log_files.rows[{i}]"
        _obj(row, p)
        _nonempty_str(row, "path", p)
        _nonempty_str(row, "source", p)
        _nonempty_str(row, "content_type", p)
        _nonempty_str(row, "purpose", p)
        _nonempty_str(row, "mtime", p)
        _enum(row, "status", p, LOG_STATUSES)


def _validate_raise_posture(data):
    rp = _obj(_get(data, "raise_posture", "$"), "$.raise_posture")
    wo = _number(rp, "weighted_overall", "$.raise_posture", minimum=0.0, maximum=5.0)
    _nonempty_str(rp, "weighted_rationale", "$.raise_posture")
    cats = _list(rp, "categories", "$.raise_posture")
    if len(cats) != len(RAISE_KEYS):
        _err("$.raise_posture.categories",
             f"must contain exactly {len(RAISE_KEYS)} entries; got {len(cats)}")
    seen_keys = set()
    for i, c in enumerate(cats):
        p = f"$.raise_posture.categories[{i}]"
        _obj(c, p)
        key = _enum(c, "key", p, RAISE_KEYS)
        if key in seen_keys:
            _err(f"{p}.key", f"duplicate category key {key!r}")
        seen_keys.add(key)
        name = _nonempty_str(c, "name", p)
        if name != RAISE_NAMES[key]:
            _err(f"{p}.name", f"must be {RAISE_NAMES[key]!r} for key {key!r}; got {name!r}")
        _int(c, "score", p, minimum=0, maximum=5)
        _enum(c, "confidence", p, CONFIDENCES)
        w = _number(c, "weight", p, minimum=0.0, maximum=1.0)
        if abs(w - RAISE_WEIGHTS[key]) > 1e-9:
            _err(f"{p}.weight", f"must be {RAISE_WEIGHTS[key]} for key {key!r}; got {w}")
        _nonempty_str(c, "rationale", p)
    missing = [k for k in RAISE_KEYS if k not in seen_keys]
    if missing:
        _err("$.raise_posture.categories", f"missing categories: {missing}")
    return rp


def _validate_footer(data):
    ft = _obj(_get(data, "footer", "$"), "$.footer")
    sc = _obj(_get(ft, "severity_counts", "$.footer"), "$.footer.severity_counts")
    for k in ("critical", "high", "medium", "low", "info"):
        _int(sc, k, "$.footer.severity_counts", minimum=0)


# ── cross-field consistency ──────────────────────────────────────────────────
def _validate_consistency(data, findings, finding_ids):
    # 1. footer severity counts match the findings array.
    actual = {k: 0 for k in ("critical", "high", "medium", "low", "info")}
    for f in findings:
        actual[SEVERITY_COUNT_KEYS[f["severity"]]] += 1
    stated = data["footer"]["severity_counts"]
    for k in actual:
        if actual[k] != stated[k]:
            _err("$.footer.severity_counts",
                 f"{k}={stated[k]} but findings[] contains {actual[k]} {k}")

    # 2. remit stat counts match the rules array.
    rules = data["remit_coverage"]["rules"]
    by_status = {s: 0 for s in REMIT_STATUSES}
    for r in rules:
        by_status[r["status"]] += 1
    sc = data["remit_coverage"]["stat_counts"]
    for s in REMIT_STATUSES:
        if by_status[s] != sc[s]:
            _err("$.remit_coverage.stat_counts",
                 f"{s}={sc[s]} but rules[] contains {by_status[s]}")
    if sc["total"] != len(rules):
        _err("$.remit_coverage.stat_counts.total",
             f"declared {sc['total']} but rules[] has {len(rules)}")

    # 3. every remit-rule finding anchor resolves to a real finding.
    for r in rules:
        fid = r.get("finding_id")
        if fid and fid not in finding_ids:
            _err(f"$.remit_coverage (rule {r['rule_id']})",
                 f"references finding {fid!r} which does not exist in findings[]")

    # 3b. every related_findings entry resolves to a real finding.
    for f in findings:
        for r in f.get("related_findings", []):
            if r not in finding_ids:
                _err(f"$.findings ({f['id']}).related_findings",
                     f"references finding {r!r} which does not exist in findings[]")

    # 4. weighted overall matches Σ(score × weight).
    # Scores are integers and weights are exact (0.25 / 0.15), so the true sum
    # has no floating-point error; the only slack we allow is the rounding in
    # the two-decimal JSON representation (so 0.011, just over half a unit in
    # the last place) — not a fudge factor for anything else.
    cats = data["raise_posture"]["categories"]
    computed = sum(c["score"] * c["weight"] for c in cats)
    declared = data["raise_posture"]["weighted_overall"]
    if abs(computed - declared) > 0.011:
        _err("$.raise_posture.weighted_overall",
             f"declared {declared} but Σ(score×weight) = {computed:.4f}")


# ── public API ───────────────────────────────────────────────────────────────
def validate(data):
    """Validate a parsed canonical findings JSON. Raises SchemaError on any problem.

    Returns the same object on success (a convenience for ``data = validate(data)``).
    """
    if not isinstance(data, dict):
        raise SchemaError("$: top-level value must be a JSON object "
                          f"(got {type(data).__name__}). This looks like a legacy "
                          "bare-list findings file, which the v1 renderer does not support.")
    _validate_version(data)
    _validate_scan(data)
    _validate_intro_band(data)
    _validate_behavior_summary(data)
    _validate_remit_coverage(data)
    findings, finding_ids = _validate_findings(data)
    _validate_positives(data)
    _validate_log_files(data)
    _validate_raise_posture(data)
    _validate_footer(data)
    _validate_consistency(data, findings, finding_ids)
    return data


def maturity_label(weighted_overall):
    """Map a 0.0–5.0 weighted score to its RAISE maturity label."""
    return {0: "Absent", 1: "Ad hoc", 2: "Partial",
            3: "Established", 4: "Strong", 5: "Exemplary"}[int(math.floor(weighted_overall))]
