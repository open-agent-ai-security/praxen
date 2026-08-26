#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Praxen threat-model graph schema and validator (contract v1.0).

The threat-model extraction pass emits a graph JSON conforming to
``THREAT_MODEL_SPEC.md`` (alongside this file); ``render_threatmodel.py``
consumes it. This module owns the validation rules: shape, types,
enumerations, required fields, and cross-field consistency (refs resolve,
status-dependent field requirements, count conservation).

Like ``schema.py`` for the findings JSON, this validator is strict and fails
loudly: a malformed graph is an extraction bug, never something the renderer
should paper over. The graph is the pipeline's second large exact-format
model-written artifact — it ships with a real validator from day one (#217).

Python 3.9+ stdlib only. Reuses ``schema.py``'s typed accessors and shared
enums (remit coverage statuses, OWASP code patterns, finding-ID pattern) so
the two contracts cannot drift apart silently.
"""
from __future__ import annotations

import re

import schema as _s
from schema import SchemaError  # re-exported: callers catch one error type

# ── version ──────────────────────────────────────────────────────────────────
SPEC_VERSION = "1.4"

# ── fixed enumerations ───────────────────────────────────────────────────────
LANES = [
    "user_inputs",
    "client_adapters",
    "agent_core",
    "tools_mcp",
    "external_deploy",
]
NODE_KINDS = [
    "entrypoint", "client", "adapter", "orchestrator", "model", "prompt",
    "memory", "datastore", "tool", "mcp_server", "control",
    "external_service", "deploy_surface", "secret_store", "log_sink",
]
BOUNDARY_ARCHETYPES = [
    "untrusted-ingress", "control-plane-exposure", "model-egress",
    "tool-invocation", "state-commit", "data-at-rest", "secret-material",
    "telemetry-egress", "supply-chain", "value-transfer", "peer-a2a",
    "stored-state",
]
STRIDE = ["S", "T", "R", "I", "D", "E"]
# Severity order (worst first) — the renderer's boundary coloring ladder.
THREAT_STATUSES = ["confirmed", "potential", "partial", "mitigated"]
# Probe-era synonyms, rejected during the vocabulary review (2026-08-17).
# v1.0 documents must not use them; naming them in the error message saves
# the next person an archaeology session.
_LEGACY_STATUSES = {"finding": "confirmed", "residual": "potential", "open": "potential"}

_KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_ARCHETYPE_SUFFIX_RE = re.compile(
    r"^(?:" + "|".join(re.escape(a) for a in BOUNDARY_ARCHETYPES) + r")-\d+$"
)


def _closed(obj, path, allowed):
    for key in obj:
        if key not in allowed:
            _s._err(f"{path}.{key}", "unknown field (the contract is closed)")


def _evidence_list(obj, key, path, *, min_len=1):
    items = _s._list(obj, key, path, min_len=min_len)
    for i, ev in enumerate(items):
        p = f"{path}.{key}[{i}]"
        _s._obj(ev, p)
        _closed(ev, p, {"file", "line", "note"})
        _s._nonempty_str(ev, "file", p)
        if ev.get("line") is not None:
            _s._int(ev, "line", p, minimum=1)
        _s._nonempty_str(ev, "note", p)
    return items


# ── section validators ───────────────────────────────────────────────────────
def _validate_top(data):
    _s._obj(data, "$")
    _closed(data, "$", {
        "spec_version", "praxen_version", "target", "analysis_ref",
        "model_identity", "executive_summary", "lanes", "nodes", "edges",
        "trust_boundaries", "attack_paths", "notes", "remit_version",
    })
    version = _s._nonempty_str(data, "spec_version", "$")
    if version != SPEC_VERSION:
        _s._err("$.spec_version",
                f"this validator understands exactly {SPEC_VERSION!r}; got {version!r}")
    _s._nonempty_str(data, "praxen_version", "$")
    target = _s._get(data, "target", "$")
    _s._obj(target, "$.target")
    _closed(target, "$.target", {"slug", "source_root"})
    _s._nonempty_str(target, "slug", "$.target")
    _s._nonempty_str(target, "source_root", "$.target")
    _s._str(data, "analysis_ref", "$", allow_none=True)
    # Optional provenance: the remit's own declared version, carried so the
    # rendered model names the policy edition it was extracted against.
    if "remit_version" in data:
        _s._nonempty_str(data, "remit_version", "$")
    _s._nonempty_str(data, "model_identity", "$")
    _s._nonempty_str(data, "executive_summary", "$")
    lanes = _s._get(data, "lanes", "$")
    if lanes != LANES:
        _s._err("$.lanes", f"must be exactly {LANES}")


def _validate_nodes(data):
    nodes = _s._list(data, "nodes", "$", min_len=1)
    ids = set()
    for i, n in enumerate(nodes):
        p = f"$.nodes[{i}]"
        _s._obj(n, p)
        _closed(n, p, {"id", "name", "lane", "kind", "description", "evidence"})
        nid = _s._nonempty_str(n, "id", p)
        if not _KEBAB_RE.match(nid):
            _s._err(f"{p}.id", f"must be kebab-case; got {nid!r}")
        if nid in ids:
            _s._err(f"{p}.id", f"duplicate node id {nid!r}")
        ids.add(nid)
        _s._nonempty_str(n, "name", p)
        _s._enum(n, "lane", p, LANES)
        _s._enum(n, "kind", p, NODE_KINDS)
        _s._nonempty_str(n, "description", p)
        _evidence_list(n, "evidence", p)
    return ids


def _validate_edges(data, node_ids):
    edges = _s._list(data, "edges", "$")
    edge_ids = set()
    for i, e in enumerate(edges):
        p = f"$.edges[{i}]"
        _s._obj(e, p)
        _closed(e, p, {"id", "from", "to", "label", "data", "evidence"})
        src = _s._nonempty_str(e, "from", p)
        dst = _s._nonempty_str(e, "to", p)
        for ref, key in ((src, "from"), (dst, "to")):
            if ref not in node_ids:
                _s._err(f"{p}.{key}", f"references unknown node {ref!r}")
        if src == dst:
            _s._err(f"{p}.to", "self-edges are not allowed")
        eid = _s._nonempty_str(e, "id", p)
        if eid != f"{src}--{dst}":
            _s._err(f"{p}.id", f"must be '<from>--<to>' (expected {src}--{dst!r})")
        if eid in edge_ids:
            _s._err(f"{p}.id", f"duplicate edge id {eid!r}")
        edge_ids.add(eid)
        _s._nonempty_str(e, "label", p)
        _s._nonempty_str(e, "data", p)
        _evidence_list(e, "evidence", p)
    return edge_ids


def _validate_threat(t, p):
    _s._obj(t, p)
    _closed(t, p, {"stride", "owasp", "summary", "status", "finding_id",
                   "mitigation_evidence", "remainder"})
    _s._enum(t, "stride", p, STRIDE)
    owasp = _s._str(t, "owasp", p, allow_none=True)
    if owasp is not None and not (_s._OWASP_LLM_RE.match(owasp)
                                  or _s._OWASP_ASI_RE.match(owasp)):
        _s._err(f"{p}.owasp", f"must be LLM01–LLM10, ASI01–ASI10, or null; got {owasp!r}")
    _s._nonempty_str(t, "summary", p)
    status = _s._str(t, "status", p)
    if status in _LEGACY_STATUSES:
        _s._err(f"{p}.status",
                f"{status!r} is a probe-era synonym retired in v1.0 — "
                f"emit {_LEGACY_STATUSES[status]!r}")
    if status not in THREAT_STATUSES:
        _s._err(f"{p}.status", f"must be one of {THREAT_STATUSES}; got {status!r}")

    finding_id = t.get("finding_id")
    if status == "confirmed":
        if not isinstance(finding_id, str) or not _s._FINDING_ID_RE.match(finding_id):
            _s._err(f"{p}.finding_id",
                    "status=confirmed requires a finding_id matching PRAX-YYYY-MM-DD-NNN")
    elif finding_id is not None:
        _s._err(f"{p}.finding_id", f"must be null unless status=confirmed (status={status})")

    mev = t.get("mitigation_evidence")
    if status in ("mitigated", "partial"):
        if mev is None:
            _s._err(f"{p}.mitigation_evidence",
                    f"status={status} requires a citation to the enforcing code/config")
        _s._obj(mev, f"{p}.mitigation_evidence")
        _closed(mev, f"{p}.mitigation_evidence", {"file", "line"})
        _s._nonempty_str(mev, "file", f"{p}.mitigation_evidence")
        if mev.get("line") is not None:
            _s._int(mev, "line", f"{p}.mitigation_evidence", minimum=1)
    elif status == "potential" and mev is not None:
        _s._err(f"{p}.mitigation_evidence",
                "status=potential means no control was found — this field must be null")

    remainder = t.get("remainder")
    if status == "partial":
        if not isinstance(remainder, str) or not remainder.strip():
            _s._err(f"{p}.remainder",
                    "status=partial requires a stated remainder (what the control does not cover)")
    elif remainder is not None:
        _s._err(f"{p}.remainder", f"must be null unless status=partial (status={status})")

    return finding_id if status == "confirmed" else None


def _validate_boundaries(data, edge_ids):
    boundaries = _s._list(data, "trust_boundaries", "$", min_len=1)
    bids = set()
    n_threats = 0
    cited_findings = []
    for i, b in enumerate(boundaries):
        p = f"$.trust_boundaries[{i}]"
        _s._obj(b, p)
        _closed(b, p, {"id", "name", "crossing_edges", "remit_rules", "threats"})
        bid = _s._nonempty_str(b, "id", p)
        if not (bid in BOUNDARY_ARCHETYPES
                or _ARCHETYPE_SUFFIX_RE.match(bid)
                or "--" in bid):
            _s._err(f"{p}.id",
                    "must be an archetype id, an archetype with a -N suffix, or a "
                    "coined '<from-concept>--<to-concept>' id")
        if bid in bids:
            _s._err(f"{p}.id", f"duplicate boundary id {bid!r}")
        bids.add(bid)
        _s._nonempty_str(b, "name", p)
        for j, ce in enumerate(_s._list(b, "crossing_edges", p)):
            if ce not in edge_ids:
                _s._err(f"{p}.crossing_edges[{j}]", f"references unknown edge {ce!r}")
        for j, r in enumerate(_s._list(b, "remit_rules", p)):
            rp = f"{p}.remit_rules[{j}]"
            _s._obj(r, rp)
            _closed(r, rp, {"rule_id", "excerpt", "coverage_status"})
            _s._nonempty_str(r, "rule_id", rp)
            _s._nonempty_str(r, "excerpt", rp)
            _s._enum(r, "coverage_status", rp, _s.REMIT_STATUSES)
        threats = _s._list(b, "threats", p, min_len=1)
        for j, t in enumerate(threats):
            fid = _validate_threat(t, f"{p}.threats[{j}]")
            if fid:
                cited_findings.append(fid)
        n_threats += len(threats)
    return n_threats, cited_findings


def _validate_attack_paths(data, node_ids):
    # undirected adjacency: an attack path must be a WALK over real edges, so
    # the rendered chain never teleports over a missing hop. Direction is
    # undirected because attacker *influence* can run opposite to the data
    # edge (poisoned memory the loop reads back is memory→loop influence over a
    # loop→memory query edge).
    adj = set()
    for e in data.get("edges", []):
        if isinstance(e, dict) and "from" in e and "to" in e:
            adj.add((e["from"], e["to"])); adj.add((e["to"], e["from"]))
    paths = _s._list(data, "attack_paths", "$")
    pids = set()
    for i, ap in enumerate(paths):
        p = f"$.attack_paths[{i}]"
        _s._obj(ap, p)
        _closed(ap, p, {"id", "name", "steps"})
        pid = _s._nonempty_str(ap, "id", p)
        if not _KEBAB_RE.match(pid):
            _s._err(f"{p}.id", f"must be kebab-case; got {pid!r}")
        if pid in pids:
            _s._err(f"{p}.id", f"duplicate attack-path id {pid!r}")
        pids.add(pid)
        _s._nonempty_str(ap, "name", p)
        steps = _s._list(ap, "steps", p, min_len=2)
        for j, st in enumerate(steps):
            sp = f"{p}.steps[{j}]"
            _s._obj(st, sp)
            _closed(st, sp, {"node", "finding_id", "summary"})
            node = _s._nonempty_str(st, "node", sp)
            if node not in node_ids:
                _s._err(f"{sp}.node", f"references unknown node {node!r}")
            if j > 0:
                prev = steps[j - 1]["node"]
                if (prev, node) not in adj:
                    _s._err(f"{sp}.node",
                            f"attack-path step {j}→{j + 1} has no connecting edge "
                            f"({prev!r} → {node!r}); a path must be a WALK over real "
                            f"edges. Insert the intermediate node the influence "
                            f"passes through (usually the orchestrator/loop where "
                            f"injected content becomes an action), or add the edge "
                            f"that carries the hop with its evidence — do not skip "
                            f"the hijack step.")
            fid = st.get("finding_id")
            if fid is not None and (not isinstance(fid, str)
                                    or not _s._FINDING_ID_RE.match(fid)):
                _s._err(f"{sp}.finding_id",
                        "must be null or match PRAX-YYYY-MM-DD-NNN")
            _s._nonempty_str(st, "summary", sp)


def _validate_notes(data, node_ids, edge_ids, n_boundaries, n_threats):
    notes = _s._get(data, "notes", "$")
    _s._obj(notes, "$.notes")
    _closed(notes, "$.notes", {"lane_fit", "omissions", "counts"})
    _s._nonempty_str(notes, "lane_fit", "$.notes")
    _s._str(notes, "omissions", "$.notes")
    counts = _s._get(notes, "counts", "$.notes")
    _s._obj(counts, "$.notes.counts")
    _closed(counts, "$.notes.counts", {"nodes", "edges", "boundaries", "threats"})
    expected = {"nodes": len(node_ids), "edges": len(edge_ids),
                "boundaries": n_boundaries, "threats": n_threats}
    for key, want in expected.items():
        got = _s._int(counts, key, "$.notes.counts", minimum=0)
        if got != want:
            _s._err(f"$.notes.counts.{key}",
                    f"declared {got} but the document contains {want} "
                    "(count conservation)")


# ── public API ───────────────────────────────────────────────────────────────
def validate(data):
    """Validate a parsed threat-model graph JSON. Raises SchemaError on any
    problem. Returns the same object on success.
    """
    if not isinstance(data, dict):
        raise SchemaError("$: top-level value must be a JSON object "
                          f"(got {type(data).__name__})")
    _validate_top(data)
    node_ids = _validate_nodes(data)
    edge_ids = _validate_edges(data, node_ids)
    n_threats, cited = _validate_boundaries(data, edge_ids)
    _validate_attack_paths(data, node_ids)
    _validate_notes(data, node_ids, edge_ids,
                    len(data["trust_boundaries"]), n_threats)
    return data


def cited_finding_ids(data):
    """Finding IDs cited by confirmed threats and attack-path steps, deduped
    in first-appearance order. The caller cross-checks these against the
    findings JSON named by ``analysis_ref`` (the validator cannot — it sees
    only the graph).
    """
    seen, out = set(), []
    for b in data.get("trust_boundaries", []):
        for t in b.get("threats", []):
            fid = t.get("finding_id")
            if fid and fid not in seen:
                seen.add(fid); out.append(fid)
    for ap in data.get("attack_paths", []):
        for st in ap.get("steps", []):
            fid = st.get("finding_id")
            if fid and fid not in seen:
                seen.add(fid); out.append(fid)
    return out
