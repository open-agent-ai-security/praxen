#!/usr/bin/env python3
# Copyright © 2026 Exabeam, Inc. All Rights Reserved.
# Confidential and Proprietary. Do not distribute. Use by permission only.
"""Self-contained smoke tests for the Praxa render pipeline (schema.py + render.py).

No pytest dependency — run directly:

    python3 tests/render/test_render.py

Covers:
  * schema validation accepts a well-formed canonical fixture
  * render.py produces HTML with zero unsubstituted placeholders / leftover markers
  * render.py output is byte-deterministic
  * --out-txt-only mode works
  * negative cases (legacy bare list, missing field, count mismatch, bad enum,
    missing RAISE category, broken anchor) all fail loudly with a non-zero exit
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile

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


def main():
    tmp = tempfile.mkdtemp(prefix="praxa_render_test_")
    data = json.load(open(FIXTURE, encoding="utf-8"))

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
    html = open(out_html, encoding="utf-8").read() if os.path.exists(out_html) else ""
    txt = open(out_txt, encoding="utf-8").read() if os.path.exists(out_txt) else ""
    check("HTML has no unsubstituted {{PLACEHOLDER}}",
          not re.search(r"\{\{[A-Z0-9_]+\}\}", html))
    check("HTML has no leftover REPEAT/END/PICK/Variant markers",
          not re.search(r"<!--\s*(REPEAT:|END:|PICK:|Variant [AB]:)", html))
    check("HTML keeps the copyright comment", "Copyright" in html and "<!--" in html[:400])
    check("HTML carries the agent name and version", "FinBot" in html and "Praxa v0.1.0" in html)
    check("HTML footer findings tally matches the fixture",
          "8 Critical" in html and "6 High" in html and "2 Medium" in html)
    check("TXT summary is non-empty and names the agent", "FinBot" in txt and len(txt) > 200)
    check("TXT lists Critical findings", "CRITICAL FINDINGS" in txt)

    # 3. determinism
    out_html2 = os.path.join(tmp, "b.html")
    out_txt2 = os.path.join(tmp, "b.txt")
    run_render(["--findings", FIXTURE, "--template", TEMPLATE,
                "--out-html", out_html2, "--out-txt", out_txt2])
    check("HTML render is byte-deterministic",
          open(out_html, "rb").read() == open(out_html2, "rb").read())
    check("TXT render is byte-deterministic",
          open(out_txt, "rb").read() == open(out_txt2, "rb").read())

    # 4. txt-only mode (no template needed)
    out_txt_only = os.path.join(tmp, "only.txt")
    r = run_render(["--findings", FIXTURE, "--out-txt", out_txt_only])
    check("--out-txt without --out-html works", r.returncode == 0 and os.path.exists(out_txt_only))

    # 4b. cited code that *looks* like a template placeholder must not corrupt the
    #     render or trip the "unsubstituted placeholder" check.
    spiced = json.loads(json.dumps(data))
    spiced["findings"][0]["evidence"].append(
        "docker-compose.yml:12 — DATABASE_URL: {{DATABASE_URL}}, AGENT: {{AGENT_NAME}}")
    spiced["raise_posture"]["categories"][0]["rationale"] += " (config uses {{SCORE}} interpolation)"
    sp_path = os.path.join(tmp, "spiced.json")
    sp_html = os.path.join(tmp, "spiced.html")
    json.dump(spiced, open(sp_path, "w"))
    r = run_render(["--findings", sp_path, "--template", TEMPLATE, "--out-html", sp_html,
                    "--out-txt", os.path.join(tmp, "spiced.txt")])
    sp_out = open(sp_html, encoding="utf-8").read() if os.path.exists(sp_html) else ""
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
    json.dump(rich, open(rich_path, "w"))
    r = run_render(["--findings", rich_path, "--template", TEMPLATE,
                    "--out-html", rich_html, "--out-txt", rich_txt])
    rh = open(rich_html, encoding="utf-8").read() if os.path.exists(rich_html) else ""
    rt = open(rich_txt, encoding="utf-8").read() if os.path.exists(rich_txt) else ""
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

    # 5. negative cases — each must exit non-zero with a useful message
    def negative(name, mutate):
        bad = json.loads(json.dumps(data))
        path = os.path.join(tmp, "bad.json")
        if mutate is None:                       # special: write a legacy bare list
            json.dump([{"id": "x"}], open(path, "w"))
        else:
            mutate(bad)
            json.dump(bad, open(path, "w"))
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

    print(f"\n{_passed} passed, {_failed} failed")
    return 1 if _failed else 0


if __name__ == "__main__":
    sys.exit(main())
