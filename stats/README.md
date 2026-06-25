<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# stats/ — launch traffic reports

Internal launch retrospective for Praxen's **2026-06-23** public launch. Not linked from
anywhere on the site; this is a "if you know, you know" record. Two self-contained HTML
reports (no external dependencies — open in a browser, or attach to an email as-is):

| File | What it is |
|---|---|
| [`launch-traffic-report.html`](launch-traffic-report.html) | **With commentary** — the data plus the analysis (what drove traffic, the press-conversion finding). |
| [`launch-traffic-facts.html`](launch-traffic-facts.html) | **Data only** — same charts/tables, no commentary. |
| `generate.py` | The generator that produces both from the inputs below. |
| `praxen-stars.svg` | The star-history.com chart, embedded inline (so the report stays self-contained). |

## The headline finding

Coverage **converts to wherever it links.** The ~25 press placements that named Praxen
drove **~0** measured traffic to the **Pages hero site** (most didn't link it). **Help Net
Security** linked straight to the **GitHub repo** and drove 18 repo views / 16 unique — the
top external press referrer to the repo. The Pages-site traffic that *did* land came from
**audience-owned, directly-linked channels**: the **LinkedIn launch post** (164 clicks ≈ 90%
of LinkedIn referrals) and the **ISSA Los Angeles preview talk** (the Jun 18 direct spike).

## Data sources (all hand-captured into `generate.py` — point-in-time snapshots)

| Source | What it gives | How captured |
|---|---|---|
| **GoatCounter export** (`open-agent-ai-security` community account) | Pages-site pageviews, referrers, geography, top pages | Unzipped export → `generate.py` computes the aggregates. **Not committed** (per-account analytics; keep it local). Snapshot used: export `20260625T140651Z` (complete Jun 18–25). |
| **LinkedIn post analytics** | Impressions / reach / video / engagements / **link clicks** | Hand-keyed into the `LI = {...}` dict from the post's analytics screenshot (2026-06-25). |
| **GitHub repo Insights → Traffic** | Repo views (14-day) + referring sites | Hand-keyed into `GH_DAILY` / `GH_REFS` from the Insights screenshot (2026-06-25). |
| **GitHub API** | Star count + per-day adds | `gh api repos/open-agent-ai-security/praxen` (+ the star+json stargazers endpoint). |
| **star-history.com** | The star chart SVG | `curl -sL "https://api.star-history.com/svg?repos=open-agent-ai-security/praxen&type=Date" -o praxen-stars.svg` |

> Note: GoatCounter is one half of a temporary GoatCounter/Cloudflare A/B and undercounts
> (blockers, no-JS), so true Pages traffic is higher. The GitHub-repo numbers are a separate
> property (GitHub's own Insights) and are **not additive** with the Pages numbers.

## Regenerate

```bash
# 1. refresh the star chart (optional)
curl -sL "https://api.star-history.com/svg?repos=open-agent-ai-security/praxen&type=Date" \
  -o stats/praxen-stars.svg

# 2. unzip a fresh GoatCounter export and point EXPORT_DIR (top of generate.py) at it,
#    then update the LI / GH_* / STARS values from the latest screenshots/API.

# 3. build both HTML reports
python3 stats/generate.py
```

To make PDFs for emailing (not committed — regenerate on demand):

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --no-pdf-header-footer --print-to-pdf=stats/launch-traffic-report.pdf \
  "file://$PWD/stats/launch-traffic-report.html"
```
