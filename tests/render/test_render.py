#!/usr/bin/env python3
# Copyright 2026 Exabeam, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Self-contained smoke tests for the Praxen render pipeline (schema.py + render.py).

No pytest dependency — run directly:

    python3 tests/render/test_render.py

Covers:
  * schema validation accepts a well-formed canonical fixture
  * render.py produces HTML with zero unsubstituted placeholders / leftover markers
  * render.py output is byte-deterministic
  * rendered HTML/TXT match the committed golden files (tests/fixtures/finbot.golden.*)
  * HTML normalises stray HTML entities in prose (no double-escaping)
  * untrusted evidence laced with XSS payloads is HTML-escaped — no live
    <script>/<img>/event-handler/javascript: markup reaches the report, while the
    bare-tag allowlist (<strong> etc.) still renders (security regression net)
  * a credential-shaped evidence snippet triggers a best-effort stderr WARNING
    (location + pattern, never the value) without changing the rendered output
  * --out-txt-only mode works
  * every committed regression baseline under tests/baselines/ validates against
    schema.py, and the post-relicense ones re-render byte-identically from their
    JSON and quote their remit doc verbatim
  * negative cases (legacy bare list, missing field, count mismatch, bad enum,
    missing RAISE category, broken anchor) all fail loudly with a non-zero exit
"""
from __future__ import annotations

import glob
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SKILL_DIR = os.path.join(REPO_ROOT, "skills", "behavior-verifier")
RENDER_PY = os.path.join(SKILL_DIR, "render.py")
TEMPLATE = os.path.join(SKILL_DIR, "report_template.html")
FIXTURE = os.path.join(REPO_ROOT, "tests", "fixtures", "finbot.canonical.json")

sys.path.insert(0, SKILL_DIR)
import schema  # noqa: E402

_passed = 0
_failed = 0


def check(name, cond, detail=""):
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  ok   {name}")
    else:
        _failed += 1
        print(f"  FAIL {name}" + (f"  — {detail}" if detail else ""))


def run_render(args):
    return subprocess.run([sys.executable, RENDER_PY, *args],
                          capture_output=True, text=True)


# Small file-I/O helpers — Path.read_*/write_* open, (de)serialise, and close in
# one call, so no bare `open(...).read()` is left dangling (matters in the
# baseline loop in section 6, and keeps the file uniform).
def read_text(path) -> str:
    return Path(path).read_text(encoding="utf-8")


def read_bytes(path) -> bytes:
    return Path(path).read_bytes()


def text_or_empty(path) -> str:
    return read_text(path) if os.path.exists(path) else ""


def load_json(path):
    return json.loads(read_text(path))


def dump_json(path, obj) -> None:
    Path(path).write_text(json.dumps(obj), encoding="utf-8")


def main():
    tmp = tempfile.mkdtemp(prefix="praxen_render_test_")
    data = load_json(FIXTURE)

    # 1. schema accepts the fixture
    try:
        schema.validate(data)
        check("schema.validate accepts the canonical fixture", True)
    except schema.SchemaError as e:
        check("schema.validate accepts the canonical fixture", False, str(e))

    # 2. happy-path render
    out_html = os.path.join(tmp, "a.html")
    out_txt = os.path.join(tmp, "a.txt")
    r = run_render(["--findings", FIXTURE, "--template", TEMPLATE,
                    "--out-html", out_html, "--out-txt", out_txt])
    check("render exits 0 on the fixture", r.returncode == 0, r.stderr.strip())
    # On success render.py emits one summary line per output file:
    #   render.py: wrote <path> (N findings, 0 schema errors)
    # so the operator has an explicit confirmation of the file written, the
    # finding count, and the validator's (silent) all-clear in one place.
    # Match against the set of stdout lines (not substrings of `r.stdout`) so
    # the expected line has to be a *whole* line — catches format drift that
    # a substring check would miss (e.g. a preamble warning prepended later).
    n_findings_fixture = len(load_json(FIXTURE)["findings"])
    expected_summary = f"({n_findings_fixture} findings, 0 schema errors)"
    stdout_lines = set(r.stdout.splitlines())
    check("stdout has one summary line per output file with count + schema status",
          (f"render.py: wrote {out_html} {expected_summary}" in stdout_lines
           and f"render.py: wrote {out_txt} {expected_summary}" in stdout_lines),
          f"got: {r.stdout!r}")
    html = text_or_empty(out_html)
    txt = text_or_empty(out_txt)
    check("HTML has no unsubstituted {{PLACEHOLDER}}",
          not re.search(r"\{\{[A-Z0-9_]+\}\}", html))
    check("HTML has no leftover REPEAT/END/PICK/Variant markers",
          not re.search(r"<!--\s*(REPEAT:|END:|PICK:|Variant [AB]:)", html))
    check("HTML strips all template comments (incl. the license header)", "<!--" not in html)
    check("HTML carries no Exabeam copyright / proprietary notice in the report body",
          "Copyright" not in html and "Proprietary" not in html and "All Rights Reserved" not in html)
    check("HTML footer carries the Praxen attribution and project-sponsor link",
          "Project sponsored by" in html and "exabeam.com" in html and "github.com/open-agent-ai-security/praxen" in html)
    check("HTML carries the agent name and version", "FinBot" in html and "Praxen v0.3.0" in html)
    check("TXT footer carries the Praxen attribution and project-sponsor link",
          "Generated by Praxen" in txt and "exabeam.com" in txt and "github.com/open-agent-ai-security/praxen" in txt)
    bad_links = [h for h in re.findall(r'href="([^"]*)"', html)
                 if not (h.startswith("#") or h.startswith("http://") or h.startswith("https://"))]
    check("HTML has no relative/broken <a href> (only #anchors and absolute URLs)",
          not bad_links, f"found: {bad_links}")
    # The findings tally lives in the masthead severity strip (the footer no longer
    # repeats it). Each tier renders as `<b>N</b><span>Tier</span>`.
    check("masthead severity strip matches the fixture tally",
          "<b>8</b><span>Critical</span>" in html and "<b>6</b><span>High</span>" in html
          and "<b>2</b><span>Medium</span>" in html)
    check("TXT summary is non-empty and names the agent", "FinBot" in txt and len(txt) > 200)
    check("TXT lists Critical findings", "CRITICAL FINDINGS" in txt)
    # The report must stay self-contained — it renders offline (file://) and
    # nothing phones home (PRAXEN_SPEC §7). It must carry NO external script or
    # analytics beacon; web analytics live only on the docs/landing pages, never
    # here. Guards against a "consistency" edit copying the docs analytics snippet
    # into report_template.html.
    check("report HTML loads no external script / analytics beacon (self-contained, no phone-home)",
          re.search(r"<script\b[^>]*\bsrc\s*=", html, re.I) is None
          and "goatcounter" not in html.lower() and "gc.zgo.at" not in html.lower())

    # 3. determinism
    out_html2 = os.path.join(tmp, "b.html")
    out_txt2 = os.path.join(tmp, "b.txt")
    run_render(["--findings", FIXTURE, "--template", TEMPLATE,
                "--out-html", out_html2, "--out-txt", out_txt2])
    check("HTML render is byte-deterministic", read_bytes(out_html) == read_bytes(out_html2))
    check("TXT render is byte-deterministic", read_bytes(out_txt) == read_bytes(out_txt2))

    # 3b. golden-file fixtures — the rendered HTML/TXT for the canonical fixture
    #     must match what's committed, byte for byte. This is the regression net
    #     for the renderer + template + derived-value tables together: any change
    #     to render.py, report_template.html, or the fixture that alters output
    #     trips this. To intentionally accept new output, regenerate the goldens:
    #       python3 skills/behavior-verifier/render.py \
    #         --findings tests/fixtures/finbot.canonical.json \
    #         --template skills/behavior-verifier/report_template.html \
    #         --out-html tests/fixtures/finbot.golden.html \
    #         --out-txt  tests/fixtures/finbot.golden.txt
    #     ...and review the diff before committing.
    golden_html = os.path.join(REPO_ROOT, "tests", "fixtures", "finbot.golden.html")
    golden_txt = os.path.join(REPO_ROOT, "tests", "fixtures", "finbot.golden.txt")
    check("HTML render matches the committed golden file (byte-identical)",
          os.path.isfile(out_html) and os.path.isfile(golden_html)
          and read_bytes(out_html) == read_bytes(golden_html),
          "rendered HTML differs from (or one side is missing) tests/fixtures/finbot.golden.html — see header comment to regenerate")
    check("TXT render matches the committed golden file (byte-identical)",
          os.path.isfile(out_txt) and os.path.isfile(golden_txt)
          and read_bytes(out_txt) == read_bytes(golden_txt),
          "rendered TXT differs from (or one side is missing) tests/fixtures/finbot.golden.txt — see header comment to regenerate")

    # 3c. HTML-entity tolerance in prose. The SKILL prompt asks for literal
    #     characters, but the renderer must normalise an entity written by
    #     mistake: un-escape prose before re-escaping for HTML (so &mdash; ->
    #     &mdash; not &amp;mdash;) and decode it entirely for the .txt summary.
    #     (The fixture has no entities, so this runs on a mutated copy.)
    ent = json.loads(json.dumps(data))
    ent["behavior_summary"] = "Tooling <code>a &amp; b</code> &mdash; see &lt;project&gt; notes."
    ent["raise_posture"]["categories"][0]["rationale"] = "Range &lt;1.0.0&gt; &amp; a &mdash; b."
    ent_path = os.path.join(tmp, "ent.json")
    dump_json(ent_path, ent)
    ent_html = os.path.join(tmp, "ent.html")
    ent_txt = os.path.join(tmp, "ent.txt")
    run_render(["--findings", ent_path, "--template", TEMPLATE, "--out-html", ent_html, "--out-txt", ent_txt])
    eh = text_or_empty(ent_html)
    et = text_or_empty(ent_txt)
    check("HTML normalises stray entities in prose (no double-escaping like &amp;mdash; / &amp;lt;)",
          "&amp;mdash;" not in eh and "&amp;lt;" not in eh and "&amp;amp;" not in eh
          # the full injected phrases, rendered: `&mdash;` -> the em-dash char, `&amp;` -> a single `&amp;`,
          # `&lt;..&gt;` -> a single `&lt;..&gt;`. These exact substrings can't come from a template default.
          and "Tooling <code>a &amp; b</code> — see &lt;project&gt; notes." in eh
          and "Range &lt;1.0.0&gt; &amp; a — b." in eh,   # the injected RAISE rationale (esc path)
          "stray HTML entities in prose were double-escaped (or not normalised) in the HTML output")
    check("TXT decodes HTML entities in prose (no raw &amp;/&mdash;/&lt; in the summary)",
          "Tooling a & b — see <project> notes." in et
          and "&amp;" not in et and "&mdash;" not in et and "&lt;" not in et,
          "entities were not decoded in the .txt output")

    # 4. txt-only mode (no template needed)
    out_txt_only = os.path.join(tmp, "only.txt")
    r = run_render(["--findings", FIXTURE, "--out-txt", out_txt_only])
    check("--out-txt without --out-html works", r.returncode == 0 and os.path.exists(out_txt_only))

    # 4b. cited code that *looks* like a template placeholder must not corrupt the
    #     render or trip the "unsubstituted placeholder" check.
    spiced = json.loads(json.dumps(data))
    spiced["findings"][0]["evidence"].append({
        "file": "docker-compose.yml", "line": 12,
        "snippet": "DATABASE_URL: {{DATABASE_URL}}, AGENT: {{AGENT_NAME}}",
    })
    spiced["raise_posture"]["categories"][0]["rationale"] += " (config uses {{SCORE}} interpolation)"
    sp_path = os.path.join(tmp, "spiced.json")
    sp_html = os.path.join(tmp, "spiced.html")
    dump_json(sp_path, spiced)
    r = run_render(["--findings", sp_path, "--template", TEMPLATE, "--out-html", sp_html,
                    "--out-txt", os.path.join(tmp, "spiced.txt")])
    sp_out = text_or_empty(sp_html)
    check("render survives {{placeholder-like}} text in cited evidence/rationale",
          r.returncode == 0, r.stderr.strip())
    check("cited braces are neutralised, not substituted, and not flagged as unfilled",
          "{{DATABASE_URL}}" not in sp_out          # no raw double braces survive...
          and "{{AGENT_NAME}}" not in sp_out        # ...for either the cited or the template forms
          and "{{SCORE}}" not in sp_out
          and "&#123;&#123;DATABASE_URL&#125;&#125;" in sp_out   # cited braces -> entities
          and "FinBot" in sp_out)                   # the real AGENT_NAME placeholder still resolved

    # 4c. multi-paragraph behavior summary with inline emphasis: <p>/<strong>/<em>
    #     survive in HTML; the TXT flattens them (paragraph break -> space, tags dropped).
    rich = json.loads(json.dumps(data))
    rich["behavior_summary"] = ("<p>First paragraph ends with a period.</p>"
                                "<p>Second paragraph has <strong>bold</strong> and <em>italic</em> and "
                                "<code>code()</code> spans.</p>")
    rich_path = os.path.join(tmp, "rich.json")
    rich_html = os.path.join(tmp, "rich.html")
    rich_txt = os.path.join(tmp, "rich.txt")
    dump_json(rich_path, rich)
    r = run_render(["--findings", rich_path, "--template", TEMPLATE,
                    "--out-html", rich_html, "--out-txt", rich_txt])
    rh = text_or_empty(rich_html)
    rt = text_or_empty(rich_txt)
    check("render succeeds with <p>/<strong>/<em>/<code> in behavior_summary",
          r.returncode == 0, r.stderr.strip())
    check("HTML keeps <p>/<strong>/<em>/<code> in the behavior summary",
          "<p>First paragraph" in rh and "<strong>bold</strong>" in rh
          and "<em>italic</em>" in rh and "<code>code()</code>" in rh)
    check("TXT flattens paragraphs to a space and drops all tags",
          "period. Second paragraph" in rt        # </p><p> -> single space, no run-together
          and "<strong>" not in rt and "<p>" not in rt and "<code>" not in rt
          and "</p>" not in rt and "<em>" not in rt
          and "bold" in rt and "italic" in rt and "code() spans" in rt)  # content kept, tags gone

    # 4d. v2.0 structured evidence renders as `file:line — snippet`;
    #     multi-item recommended_actions renders as a <ul>; single-item stays inline.
    sched = json.loads(json.dumps(data))
    sched["findings"][0]["evidence"] = [
        {"file": "src/foo.py", "line": 42, "snippet": "needs validation"},
        {"file": "src/bar.py", "line": None, "snippet": "file-level note"},
    ]
    sched["findings"][0]["recommended_actions"] = [
        "First action with a <code>code</code> span.",
        "Second action.",
    ]
    sched_path = os.path.join(tmp, "sched.json")
    sched_html = os.path.join(tmp, "sched.html")
    dump_json(sched_path, sched)
    r = run_render(["--findings", sched_path, "--template", TEMPLATE,
                    "--out-html", sched_html, "--out-txt", os.path.join(tmp, "sched.txt")])
    sh = text_or_empty(sched_html)
    check("v2.0 evidence renders as `file:line — snippet` and `file — snippet`",
          r.returncode == 0
          and "src/foo.py:42 — needs validation" in sh
          and "src/bar.py — file-level note" in sh, r.stderr.strip())
    check("multi-item recommended_actions renders as a <ul> with inline <code> preserved",
          "<ul><li>" in sh and "<code>code</code>" in sh and "Second action." in sh)

    # 4d-bis. A finding with null policy_rule_ids/policy_rule_text (a RAISE-category
    #         or detection-pattern finding that does not trace to a remit rule)
    #         validates and renders — its finding card simply omits the policy-ref.
    norule = json.loads(json.dumps(data))
    norule["findings"][0]["policy_rule_ids"] = None
    norule["findings"][0]["policy_rule_text"] = None
    norule_path = os.path.join(tmp, "norule.json")
    norule_html = os.path.join(tmp, "norule.html")
    dump_json(norule_path, norule)
    r = run_render(["--findings", norule_path, "--template", TEMPLATE,
                    "--out-html", norule_html, "--out-txt", os.path.join(tmp, "norule.txt")])
    nh = text_or_empty(norule_html)
    # every fixture finding cites a rule, so the policy-ref count drops by exactly
    # one when a single finding's policy fields are nulled.
    check("null policy_rule_ids/text validates and renders; the policy-ref is dropped for that finding",
          r.returncode == 0
          and nh.count('class="policy-ref"') == len(data["findings"]) - 1,
          r.stderr.strip())

    # 4e. The published JSON-Schema doc and the Python validator agree on enum values.
    sch_path = os.path.join(SKILL_DIR, "findings.schema.json")
    js = load_json(sch_path)
    finding_props = js["properties"]["findings"]["items"]["properties"]
    rules_props = js["properties"]["remit_coverage"]["properties"]["rules"]["items"]["properties"]
    cat_props = js["properties"]["raise_posture"]["properties"]["categories"]["items"]["properties"]
    log_props = js["properties"]["log_files"]["properties"]["rows"]["items"]["properties"]
    pairs = [
        (finding_props["severity"]["enum"],    schema.SEVERITIES,   "severity"),
        (finding_props["confidence"]["enum"],  schema.CONFIDENCES,  "confidence"),
        (finding_props["raise_category"]["enum"], schema.RAISE_KEYS, "raise_category"),
        (finding_props["tags"]["items"]["properties"]["kind"]["enum"], schema.TAG_KINDS, "tag.kind"),
        (rules_props["status"]["enum"],        schema.REMIT_STATUSES, "remit-rule status"),
        (cat_props["key"]["enum"],             schema.RAISE_KEYS,     "raise category key"),
        (log_props["status"]["enum"],          schema.LOG_STATUSES,   "log status"),
        (finding_props["escalation"]["enum"],  schema.ESCALATIONS,    "escalation"),
    ]
    disagreements = [name for (jenum, penum, name) in pairs if list(jenum) != list(penum)]
    check("findings.schema.json enums agree with the Python validator constants",
          not disagreements, f"diverged: {disagreements}")

    # 4f. SECURITY — XSS / HTML-injection hardening. Praxen renders UNTRUSTED
    #     evidence (a scanned agent's own code, prompts, and session-loaded files
    #     like SOUL.md / AGENTS.md) into a shareable, self-contained HTML report.
    #     Every untrusted field must be HTML-escaped via esc(), or pass through
    #     the bare-tag-only allowlist in render_rich() — no attacker-controlled
    #     markup may render live. The static template carries zero
    #     <script>/<img>/on*-handler/javascript: markup (the committed golden has
    #     none), so any live occurrence after injecting payloads is an escape
    #     regression. This locks in the behaviour the 1.0 security audit proved
    #     empirically: a crafted target repo cannot land executable markup in the
    #     report someone opens in a browser.
    P_SCRIPT = "<script>alert('xss1')</script>"
    P_IMG    = "<img src=x onerror=alert('xss2')>"
    P_CODE   = "<code onmouseover=\"alert('xss4')\">x</code>"   # event handler smuggled onto an allowlisted tag
    P_AHREF  = "<a href=\"javascript:alert('xss5')\">x</a>"      # javascript: URI inside a rich (allowlisted) field
    xss = json.loads(json.dumps(data))
    # esc() paths — plain fields the renderer emits as text/attribute content
    xss["scan"]["agent"] += P_SCRIPT
    xss["findings"][0]["summary"] += " " + P_SCRIPT
    xss["findings"][0]["evidence"][0]["snippet"] = (
        P_IMG + " // " + xss["findings"][0]["evidence"][0]["snippet"])
    xss["raise_posture"]["categories"][0]["rationale"] += " " + P_IMG
    # render_rich() path — behavior_summary allows only the bare tags <p>/<strong>/<em>/<code>
    xss["behavior_summary"] = (P_SCRIPT + P_CODE + P_AHREF
                               + " Legit <strong>prose</strong> survives.")
    xss_path = os.path.join(tmp, "xss.json")
    xss_html = os.path.join(tmp, "xss.html")
    dump_json(xss_path, xss)
    r = run_render(["--findings", xss_path, "--template", TEMPLATE,
                    "--out-html", xss_html, "--out-txt", os.path.join(tmp, "xss.txt")])
    check("render exits 0 on a findings file laced with XSS payloads",
          r.returncode == 0, r.stderr.strip())
    xh = text_or_empty(xss_html)
    xl = xh.lower()
    # (a) no attacker-controlled markup renders LIVE
    check("no live <script> tag survives injection (esc + render_rich)", "<script" not in xl)
    check("no live <img> tag survives injection", "<img" not in xl)
    check("no smuggled handler rides an allowlisted tag (<code onmouseover=...> is escaped)",
          "<code onmouseover" not in xl)
    check("no live event-handler attribute on any tag in the report",
          re.search(r"<[a-z][^>]*\son[a-z]+\s*=", xh, re.I) is None)
    check("no live <a> carries a javascript: URI",
          re.search(r"<a\b[^>]*javascript:", xh, re.I) is None)
    # (b) the payloads were ESCAPED (present-but-inert), not silently dropped —
    #     proving the escape path ran, rather than the content just vanishing.
    check("the <script> payload is present but escaped (&lt;script&gt;)", "&lt;script&gt;" in xh)
    check("the <img onerror> payload is present but escaped (&lt;img)", "&lt;img" in xh)
    check("the <code> handler-smuggle payload is escaped (&lt;code onmouseover)",
          "&lt;code onmouseover" in xh)
    check("the javascript: <a> payload is escaped (&lt;a href=&quot;javascript)",
          "&lt;a href=&quot;javascript" in xh)
    # (c) the bare-tag allowlist still works — a legitimate <strong> in the same
    #     rich field renders live, so the hardening didn't just strip every tag.
    check("legitimate allowlisted <strong> in a rich field still renders live",
          "<strong>prose</strong>" in xh)

    # 4g. SECURITY — secret backstop. The renderer REDACTS a credential-shaped
    #     evidence snippet before it reaches the report, and warns (to stderr,
    #     without the value) — enforcing the Never-Reprint-Secrets rule for the
    #     shareable HTML/TXT even if the model's own redaction missed it.
    sec = json.loads(json.dumps(data))
    # AKIAIOSFODNN7EXAMPLE is AWS's published, non-functional example key id.
    sec["findings"][0]["evidence"][0]["snippet"] = "aws_key = 'AKIAIOSFODNN7EXAMPLE'  # example only"
    sec_path = os.path.join(tmp, "sec.json")
    sec_html = os.path.join(tmp, "sec.html")
    sec_txt = os.path.join(tmp, "sec.txt")
    dump_json(sec_path, sec)
    r = run_render(["--findings", sec_path, "--template", TEMPLATE,
                    "--out-html", sec_html, "--out-txt", sec_txt])
    check("render still exits 0 on a secret-shaped snippet (redact, not fail)",
          r.returncode == 0, r.stderr.strip())
    check("render warns on stderr about a redacted secret",
          "WARNING" in r.stderr and "redacted" in r.stderr.lower() and "AWS access key id" in r.stderr,
          f"stderr: {r.stderr!r}")
    check("the secret warning names the location/pattern, not the value",
          "AKIAIOSFODNN7EXAMPLE" not in r.stderr)
    sh = text_or_empty(sec_html); st = text_or_empty(sec_txt)
    check("the secret VALUE never reaches the rendered HTML or TXT report",
          "AKIAIOSFODNN7EXAMPLE" not in sh and "AKIAIOSFODNN7EXAMPLE" not in st,
          "a credential value leaked into the rendered report")
    check("the report carries a [REDACTED] marker in place of the secret",
          "[REDACTED" in sh and "AWS access key id" in sh)
    # A full PEM private-key block must be redacted ENTIRELY (the base64 body, not
    # just the BEGIN header) — the body is the secret.
    pk = json.loads(json.dumps(data))
    body1, body2 = "MIIBVENOTAREALKEYbody0000xxxxYYYYzzzz1234567890abcdef", "SECONDbodyLINEnotreal99887766554433221100"
    pk["findings"][0]["evidence"][0]["snippet"] = (
        "-----BEGIN RSA PRIVATE KEY-----\n" + body1 + "\n" + body2 + "\n-----END RSA PRIVATE KEY-----")
    pk_path = os.path.join(tmp, "pk.json")
    pk_html = os.path.join(tmp, "pk.html")
    dump_json(pk_path, pk)
    rpk = run_render(["--findings", pk_path, "--template", TEMPLATE,
                      "--out-html", pk_html, "--out-txt", os.path.join(tmp, "pk.txt")])
    pkh = text_or_empty(pk_html)
    check("a full PEM private key is redacted entirely (body, not just the BEGIN header)",
          rpk.returncode == 0 and body1 not in pkh and body2 not in pkh
          and "BEGIN RSA PRIVATE KEY" not in pkh and "[REDACTED" in pkh,
          "private-key body leaked into the rendered HTML")

    clean = json.loads(json.dumps(data))
    clean["findings"][0]["evidence"][0]["snippet"] = "aws_key = '[REDACTED — AWS key at config.py:3]'"
    clean_path = os.path.join(tmp, "clean.json")
    dump_json(clean_path, clean)
    rc = run_render(["--findings", clean_path, "--out-txt", os.path.join(tmp, "clean.txt")])
    check("no secret warning on a clean (redacted) snippet", "WARNING" not in rc.stderr,
          f"stderr: {rc.stderr!r}")

    # 5. negative cases — each must exit non-zero with a useful message
    def negative(name, mutate):
        bad = json.loads(json.dumps(data))
        path = os.path.join(tmp, "bad.json")
        if mutate is None:                       # special: write a legacy bare list
            dump_json(path, [{"id": "x"}])
        else:
            mutate(bad)
            dump_json(path, bad)
        r = run_render(["--findings", path, "--out-txt", os.path.join(tmp, "n.txt")])
        check(name, r.returncode != 0 and bool(r.stderr.strip()),
              f"rc={r.returncode} stderr={r.stderr.strip()!r}")

    negative("rejects a legacy bare-list findings file", None)
    negative("rejects a missing required field (behavior_summary)",
             lambda d: d.pop("behavior_summary"))
    negative("rejects a footer/severity count mismatch",
             lambda d: d["footer"]["severity_counts"].__setitem__("critical", 99))
    negative("rejects a bad severity enum",
             lambda d: d["findings"][0].__setitem__("severity", "Sorta Bad"))
    negative("rejects a remit anchor pointing at a nonexistent finding",
             lambda d: d["remit_coverage"]["rules"][0].__setitem__("finding_id", "PRAX-9999-99-99-999"))
    negative("rejects fewer than six RAISE categories",
             lambda d: d["raise_posture"]["categories"].pop())
    negative("rejects a weighted_overall that doesn't match the category sum",
             lambda d: d["raise_posture"].__setitem__("weighted_overall", 4.99))
    negative("rejects an escalation inconsistent with severity (Critical + log_only)",
             lambda d: d["findings"][0].__setitem__("escalation", "log_only"))
    negative("rejects a non-canonical owasp_llm code",
             lambda d: d["findings"][0].__setitem__("owasp_llm", "LLM99"))
    negative("rejects a non-canonical owasp_agentic code",
             lambda d: d["findings"][0].__setitem__("owasp_agentic", "bananas"))
    negative("rejects a finding that lists its own id in related_findings",
             lambda d: d["findings"][0].__setitem__("related_findings", [d["findings"][0]["id"]]))
    negative("rejects policy_rule_ids null while policy_rule_text is set",
             lambda d: d["findings"][0].__setitem__("policy_rule_ids", None))
    negative("rejects an empty-string policy_rule_ids",
             lambda d: d["findings"][0].__setitem__("policy_rule_ids", "  "))

    # 6. committed regression baselines under tests/baselines/. The canonical
    #    JSON is the source of truth; the committed HTML/TXT are derived. For the
    #    post-relicense baselines (rendered with the current template) this asserts
    #    they re-render byte-for-byte from their JSON — the regression net that
    #    would have caught a renderer change silently desyncing a committed report.
    #    Pre-relicense baselines (and the schema-1.0 v0.2 set) keep the old report
    #    header by design — see tests/baselines/README.md → "Note on the relicense";
    #    those are validated as far as the current schema/template allow and the
    #    byte-compare is skipped. From praxen_version 0.6.0 on, the baseline must
    #    also quote its remit doc verbatim (tests/remits/<slug>.md): every rule_text
    #    and every `/`-separated policy_rule_text segment must be a substring.
    baselines_root = os.path.join(REPO_ROOT, "tests", "baselines")
    baseline_jsons = sorted(glob.glob(os.path.join(baselines_root, "*", "*", "*-findings-*.json")))
    check("found committed regression baselines under tests/baselines/", len(baseline_jsons) > 0)
    remit_cache: dict[str, str] = {}                 # slug -> remit text (one remit per target, but cache anyway)
    for bj in baseline_jsons:
        rel = os.path.relpath(bj, REPO_ROOT)
        bdata = load_json(bj)
        sv = str(bdata.get("schema_version", ""))
        if not sv.startswith("2."):
            check(f"baseline {rel}: schema_version {sv!r} — frozen pre-2.0 artifact, schema/render checks skipped", True)
            continue
        try:
            schema.validate(bdata)
            check(f"baseline {rel}: validates against schema.py", True)
        except schema.SchemaError as e:
            check(f"baseline {rel}: validates against schema.py", False, str(e))
            continue
        bdir = os.path.dirname(bj)
        c_html = next(iter(glob.glob(os.path.join(bdir, "*-analysis-*.html"))), None)
        c_txt = next(iter(glob.glob(os.path.join(bdir, "*-analysis-*.txt"))), None)
        check(f"baseline {rel}: has a committed .html and .txt alongside it", bool(c_html and c_txt))
        if not (c_html and c_txt):
            continue
        r_html = os.path.join(tmp, "bl.html")
        r_txt = os.path.join(tmp, "bl.txt")
        r = run_render(["--findings", bj, "--template", TEMPLATE, "--out-html", r_html, "--out-txt", r_txt])
        check(f"baseline {rel}: render exits 0", r.returncode == 0, r.stderr.strip())
        committed_html = read_bytes(c_html)
        if b"github.com/open-agent-ai-security/praxen" in committed_html and r.returncode == 0:   # post-relicense template
            check(f"baseline {rel}: HTML re-renders byte-identical from its JSON",
                  committed_html == read_bytes(r_html),
                  "committed HTML differs from a fresh render of the committed JSON")
            check(f"baseline {rel}: TXT re-renders byte-identical from its JSON",
                  read_bytes(c_txt) == read_bytes(r_txt),
                  "committed TXT differs from a fresh render of the committed JSON")
        else:
            check(f"baseline {rel}: pre-relicense template — byte re-render comparison skipped", True)
        # remit-quote invariant (praxen_version >= 0.6.0)
        try:
            pv = tuple(int(x) for x in str(bdata.get("praxen_version", "0")).split("."))
        except ValueError:
            pv = (0,)
        slug = bdata.get("scan", {}).get("agent_slug") or os.path.basename(bdir)
        remit_path = os.path.join(REPO_ROOT, "tests", "remits", f"{slug}.md")
        if pv < (0, 6, 0):
            check(f"baseline {rel}: praxen_version < 0.6.0 — remit-quote check skipped", True)
        elif not os.path.isfile(remit_path):
            check(f"baseline {rel}: has a matching tests/remits/{slug}.md", False)
        else:
            if slug not in remit_cache:
                remit_cache[slug] = read_text(remit_path)
            remit = remit_cache[slug]
            # rule_text / policy_rule_text quote the remit's policy *text*; Markdown
            # emphasis (** * `) is formatting, not content, and the skill strips it.
            # Compare modulo emphasis markers and whitespace runs — but the quote must
            # still be a contiguous verbatim span (no eliding the middle with "...").
            def _norm(s):
                return re.sub(r"\s+", " ", s.replace("**", "").replace("*", "").replace("`", "")).strip()
            norm_remit = _norm(remit)
            quoted = [("rule_text", rule["rule_id"], rule["rule_text"])
                      for rule in bdata["remit_coverage"]["rules"]]
            for f in bdata["findings"]:
                for seg in (f.get("policy_rule_text") or "").split(" / "):
                    if seg.strip():
                        quoted.append(("policy_rule_text", f["id"], seg.strip()))
            missing = [(kind, who, txt) for (kind, who, txt) in quoted if _norm(txt) not in norm_remit]
            check(f"baseline {rel}: every rule_text / policy_rule_text is quoted verbatim from tests/remits/{slug}.md",
                  not missing,
                  "; ".join(f"{kind} of {who}: {txt[:60]!r}" for kind, who, txt in missing[:3]))

    print(f"\n{_passed} passed, {_failed} failed")
    return 1 if _failed else 0


if __name__ == "__main__":
    sys.exit(main())
