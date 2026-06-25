#!/usr/bin/env python3
"""
Praxen launch traffic report generator.

Emits TWO self-contained HTML files (no external deps, emailable as-is):
  - launch-traffic-report.html   (with commentary / analysis)
  - launch-traffic-facts.html    (data only, no commentary)

Inputs (see README.md for the full provenance):
  - GoatCounter export    : the unzipped community-account export (NOT committed).
  - praxen-stars.svg       : star-history.com chart (committed; refresh via curl).
  - LinkedIn / GitHub-repo : hand-keyed from screenshots (LI = post analytics,
                             GH = the repo's GitHub Insights → Traffic page).
  - Press list / stars     : hand-maintained below.

Regenerate:  python3 stats/generate.py
"""
import json, collections, datetime, glob, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Point this at your unzipped GoatCounter export. Last run: export 20260625T140651Z.
_cands = glob.glob(os.path.join(SCRIPT_DIR, "goatcounter-export*", "")) + glob.glob("/tmp/gc2/goatcounter-*")
EXPORT_DIR = _cands[0]

def load(f): return [json.loads(l) for l in open(os.path.join(EXPORT_DIR, f)) if l.strip()]
paths = {p["id"]: p["path"] for p in load("paths.jsonl")}
refs  = {r["id"]: (r["ref"] or "(direct)") for r in load("refs.jsonl")}
hits  = load("hit_stats.jsonl"); locs = load("location_stats.jsonl")
total = sum(h["count"] for h in hits)
praxen = sum(h["count"] for h in hits if paths.get(h["path_id"], "").startswith("/praxen"))
days = sorted({h["hour"][:10] for h in hits})
byday = collections.Counter(); byday_px = collections.Counter()
for h in hits:
    d = h["hour"][:10]; byday[d] += h["count"]
    if paths.get(h["path_id"], "").startswith("/praxen"): byday_px[d] += h["count"]
px_ids = {pid for pid, p in paths.items() if p == "/praxen"}
def catf(ref):
    r = ref.lower()
    if r == "(direct)": return "Direct"
    if "linkedin" in r or "lnkd" in r: return "LinkedIn"
    if "github.io" in r: return "Internal site nav"
    if r == "google" or "google" in r or "bing" in r: return "Search (Google/Bing)"
    if "teams" in r or "office.net" in r or "onecdn.static.microsoft" in r: return "MS Teams"
    if "facebook" in r: return "Facebook"
    if "businesswire" in r: return "BusinessWire (release)"
    if "exabeam" in r: return "Exabeam.com"
    if "github.com" in r: return "GitHub.com"
    if "slack" in r: return "Slack"
    if any(p in r for p in ["siliconangle","helpnetsecurity","yahoo","comparethecloud","securitybrief","itbrief","cyberrisk","aitech","techintel","soc-news","itnewsafrica","cioinfluence","zawya","tmcnet","financialcontent","itwire","digitalitnews","techround","africabusiness","anbaa"]): return "Editorial press"
    return "Other"
pxref = collections.Counter()
for h in hits:
    if h["path_id"] in px_ids: pxref[h["ref_id"]] += h["count"]
px_total = sum(pxref.values())
px_cat = collections.Counter()
for rid, c in pxref.items(): px_cat[catf(refs.get(rid, ""))] += c
px_ext = sorted([(refs.get(rid), c) for rid, c in pxref.items() if catf(refs.get(rid, "")) not in ("Internal site nav", "Direct")], key=lambda x: -x[1])
lk = px_cat.get("LinkedIn", 0); press = px_cat.get("Editorial press", 0)
byloc = collections.Counter()
for l in locs: byloc[l["location"]] += l["count"]
us = sum(c for loc, c in byloc.items() if loc.startswith("US-"))
bypath = collections.Counter()
for h in hits: bypath[h["path_id"]] += h["count"]
pxpaths = sorted([(paths.get(pid), c) for pid, c in bypath.items() if paths.get(pid, "").startswith("/praxen")], key=lambda x: -x[1])

# ---- hand-keyed inputs ----
LI = dict(impr=5279, reach=3331, vid=2212, eng=220, clicks=164, react=144, com=32, save=23, rep=17, send=4, prof=37, foll=7, watch="9h&nbsp;12m", avg="14s")
STARS = 28
GH_TOTAL = 442
GH_DAILY = [("06/11",31),("06/12",23),("06/13",0),("06/14",3),("06/15",13),("06/16",15),("06/17",22),("06/18",54),("06/19",39),("06/20",3),("06/21",10),("06/22",30),("06/23",51),("06/24",148)]
GH_REFS = [("open-agent-ai-security.github.io (Pages hero)",157,48),("github.com",68,15),("helpnetsecurity.com",18,16),("Bing",9,3),("MS Teams (onecdn)",4,3),("DuckDuckGo",3,3),("Google",2,1)]
PRESS = [("Exabeam (press release)","Launches Open-Source Praxen to Bring Agent Behavior Verification to AI Agents and Digital Workers","https://www.exabeam.com/press-releases/exabeam-launches-open-source-praxen-to-bring-agent-behavior-verification-to-ai-agents-and-digital-workers/"),
("SiliconANGLE","Exabeam launches Praxen, an open-source tool to verify AI agent behavior","https://siliconangle.com/2026/06/23/exabeam-launches-praxen-open-source-tool-verify-ai-agent-behavior/"),
("Help Net Security","Praxen: Open-source AI agent behavior verification","https://www.helpnetsecurity.com/2026/06/24/praxen-open-source-ai-agent-behavior-verification/"),
("Compare the Cloud","Exabeam releases Praxen, an open-source tool for verifying AI agent behaviour before deployment","https://www.comparethecloud.net/news/exabeam-releases-praxen-an-open-source-tool-for-verifying-ai-agent-behaviour-before-deployment"),
("IT Brief Australia","Exabeam launches open-source Praxen to verify AI agents","https://itbrief.com.au/story/exabeam-launches-open-source-praxen-to-verify-ai-agents"),
("SecurityBrief Asia","Exabeam launches open-source Praxen to verify AI agents","https://securitybrief.asia/story/exabeam-launches-open-source-praxen-to-verify-ai-agents"),
("Cyber Risk Leaders","Exabeam releases open-source Praxen tool for AI agent behaviour verification","https://cyberriskleaders.com/exabeam-releases-open-source-praxen-tool-for-ai-agent-behaviour-verification/"),
("AI Tech365","Exabeam unveils open-source Praxen to establish Agent Behavior Verification for enterprise AI workers","https://aitech365.com/business-technology/cybersecurity/exabeam-unveils-open-source-praxen-to-establish-agent-behavior-verification-for-enterprise-ai-workers/"),
("TechIntelPro","Exabeam launches open-source Praxen for Agent Behavior Verification","https://techintelpro.com/news/cybersecurity/ai/exabeam-launches-open-source-praxen-for-agent-behavior-verification"),
("SOC News","Exabeam launches Praxen for AI agent security","https://soc-news.com/exabeam-launches-praxen-for-ai-agent-security/"),
("IT News Africa","Exabeam launches open-source Praxen for AI agent verification","https://www.itnewsafrica.com/2026/06/exabeam-launches-open-source-praxen-for-ai-agent-verification/"),
("LinkedIn · Joanne Pei Lee Wong","Frontier AI is Changing Cyber Risk: Agent Behavior Needs a New Approach","https://www.linkedin.com/pulse/frontier-ai-changing-cyber-risk-agent-behavior-needs-part-wong-oxptc/")]
SYND = [("Yahoo Finance","https://finance.yahoo.com/technology/ai/articles/exabeam-launches-open-source-praxen-130000884.html"),("Zawya","https://www.zawya.com/en/press-release/companies-news/exabeam-launches-open-source-praxen-to-bring-agent-behavior-verification-to-ai-agents-and-digital-workers-q1c0rggt"),("FinancialContent","https://www.financialcontent.com/article/bizwire-2026-6-23-exabeam-launches-open-source-praxen-to-bring-agent-behavior-verification-to-ai-agents-and-digital-workers"),("TMCnet","https://www.tmcnet.com/usubmit/-exabeam-launches-open-source-praxen-bring-agent-behavior-/2026/06/23/10404217.htm"),("CIO Influence","https://cioinfluence.com/security/exabeam-launches-open-source-praxen-to-bring-agent-behavior-verification-to-ai-agents-and-digital-workers/"),("iTWire","https://itwire.com/business-it-news/data/exabeam-launches-open-source-praxen-to-bring-agent-behaviour-verification-to-ai-agents-and-digital-workers"),("AdTechToday","https://adtechtoday.com/exabeam-launches-open-source-praxen-to-bring-agent-behavior-verification-to-ai-agents-and-digital-workers/"),("InAI Today","https://inaitoday.com/exabeam-launches-open-source-praxen-to-bring-agent-behaviour-verification-to-ai-agents-and-digital-workers/"),("FinTech Gate","https://fintechgate.net/2026/06/23/exabeam-launches-open-source-praxen-to-bring-agent-behavior-verification-to-ai-agents-and-digital-workers/"),("TechRound","https://techround.co.uk/artificial-intelligence/exabeam-open-source-praxen-agent-behaviour-verification-ai-agents-digital-workers/"),("Africa Business Communities","https://africabusinesscommunities.com/tech-24/exabeam-launches-praxen-to-verify-ai-agent-behavior/"),("Anbaa Al-Youm","https://www.anbaaalyoumeg.com/655510")]

svg = open(os.path.join(SCRIPT_DIR, "praxen-stars.svg")).read().replace(
    'width="800" height="533.333" style="stroke-width:3;font-family:xkcd;background:#fff"',
    'viewBox="0 0 800 533.333" width="100%" style="stroke-width:3;font-family:xkcd;background:#fff;max-width:760px;height:auto;display:block;margin:0 auto;border-radius:10px"')
today = datetime.date.today().isoformat()

def bar(label, val, vmax, sub="", color="#ff7a2e"):
    w = max(2, round(val / vmax * 100))
    return f'<div class="row"><span class="rl">{label}</span><span class="rbar"><i style="width:{w}%;background:{color}"></i></span><span class="rv">{val}{(" · "+sub) if sub else ""}</span></div>'

CSS = """:root{--bg:#0a1020;--bg2:#0c1424;--panel:rgba(255,255,255,.04);--bd:rgba(255,255,255,.09);--bdhi:rgba(255,138,61,.45);--tx:#e9eff8;--mut:#9aabc0;--mut2:#6f819a;--or:#ff7a2e;--or2:#ff9d4d;--bl:#5b8def}
*{box-sizing:border-box}html,body{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;background:var(--bg);color:var(--tx);font:16px/1.6 Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
.wrap{max-width:920px;margin:0 auto;padding:38px 22px 70px}
h1{font-size:30px;margin:0 0 6px;font-weight:700;letter-spacing:-.02em}
h2{font-size:19px;margin:34px 0 14px;font-weight:700;letter-spacing:-.01em}
.sub{color:var(--mut);margin:0 0 22px;font-size:14.5px}
.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:18px 0 6px}
.card{background:var(--panel);border:1px solid var(--bd);border-radius:14px;padding:16px}
.card b{display:block;font-size:27px;font-weight:700;color:var(--or2);line-height:1.05;font-family:"Space Grotesk",Inter}
.card span{font-size:12.5px;color:var(--mut)}
.sec{background:var(--panel);border:1px solid var(--bd);border-radius:16px;padding:20px 22px;margin-bottom:8px}
.row{display:flex;align-items:center;gap:12px;margin:7px 0;font-size:13.5px}
.rl{flex:0 0 230px;color:var(--mut);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rbar{flex:1 1 auto;background:rgba(255,255,255,.05);border-radius:6px;height:14px;overflow:hidden}
.rbar i{display:block;height:100%;border-radius:6px}
.rv{flex:0 0 130px;text-align:right;color:var(--tx);font-weight:600;font-size:12.5px}
.callout{border-left:3px solid var(--or);background:linear-gradient(160deg,rgba(255,122,46,.08),rgba(255,255,255,.012));border-radius:0 14px 14px 0;padding:18px 22px;margin:14px 0}
.callout.warn{border-left-color:#e8621d}.callout h3{margin:0 0 8px;font-size:16px}.callout p{margin:0 0 8px;color:var(--mut);font-size:14px}.callout p:last-child{margin:0}
table{width:100%;border-collapse:collapse;font-size:13.5px;margin-top:6px}
td{padding:7px 8px;border-bottom:1px solid var(--bd);color:var(--mut)}td.n{text-align:right;color:var(--tx);font-weight:600;width:70px}
.foot{color:var(--mut2);font-size:12px;margin-top:30px;border-top:1px solid var(--bd);padding-top:16px}
.tag{display:inline-block;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--or2);font-weight:700}
@media(max-width:680px){.cards{grid-template-columns:repeat(2,1fr)}.rl{flex-basis:120px}}"""

def page(commentary):
    def cm(s): return s if commentary else ""
    P = []
    P.append(f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Praxen Launch — Traffic{" Report" if commentary else " (Data)"}</title><style>{CSS}</style></head><body><div class="wrap">')
    P.append(f'<span class="tag">GoatCounter · open-agent-ai-security</span><h1>Praxen Launch — Traffic{" Report" if commentary else " Data"}</h1>')
    P.append(f'<p class="sub">Window <b>{days[0]} → {days[-1]}</b> (UTC, complete). Shared community account; Praxen broken out. GoatCounter only — the Cloudflare half of the A/B is not in this export.</p>')
    P.append(f'<div class="cards"><div class="card"><b>{total}</b><span>total pageviews (all sites)</span></div><div class="card"><b>{praxen}</b><span>Praxen pageviews ({praxen/total*100:.0f}%)</span></div><div class="card"><b>{byday["2026-06-24"]}</b><span>peak day (Jun 24)</span></div><div class="card"><b>{byday["2026-06-25"]}</b><span>Jun 25 (sustained)</span></div></div>')

    # press
    press_rows = "".join(f'<a href="{u}" target="_blank" rel="noopener" style="display:flex;justify-content:space-between;gap:14px;padding:9px 2px;border-bottom:1px solid var(--bd);text-decoration:none"><span style="color:var(--mut)"><b style="color:var(--or2)">{o}</b> — {t}</span><span style="color:var(--mut2);flex:none">&#8599;</span></a>' for o, t, u in PRESS)
    synd_line = " &middot; ".join(f'<a href="{u}" target="_blank" rel="noopener">{n}</a>' for n, u in SYND)
    P.append('<h2>Press coverage — a strong launch pickup</h2>')
    P.append('<p class="sub">~25 placements across cybersecurity, AI, and enterprise-technology media; no negative coverage. The earned media:</p>')
    P.append('<div class="cards"><div class="card"><b>1</b><span>announcement</span></div><div class="card"><b>10</b><span>editorial</span></div><div class="card"><b>13</b><span>syndications</span></div><div class="card"><b>0</b><span>negative</span></div></div>')
    P.append(f'<div class="sec" style="padding:6px 22px">{press_rows}</div>')
    P.append(f'<p class="sub" style="margin:14px 0 0"><b style="color:var(--mut)">Also syndicated to:</b> {synd_line}</p>')
    P.append(cm('<div class="callout"><h3>Great earned media — but did it drive traffic?</h3><p>A strong footprint for a launch. The rest of this report asks the harder question: <b>did the coverage send people to the site (or the repo)?</b> The referrers — and the GitHub section — hold the answer.</p></div>'))

    # daily
    mx = max(byday.values())
    dl = {"2026-06-18": "  ← ISSA LA talk", "2026-06-23": "  ← launch", "2026-06-24": "  ← peak"}
    timeline = "".join(bar(d + dl.get(d, ""), byday[d], mx, sub=f"{byday_px[d]} praxen") for d in days)
    P.append('<h2>Daily traffic</h2>')
    cap_daily = '<b>Jun 18 (220)</b> is the ISSA Los Angeles talk where Praxen was previewed — ~80% direct, docs-engaged (the room going straight to the site). Launch on <b>Jun 23</b> (283) into the <b>Jun 24</b> peak (403). <b>Jun 25 held at 210</b> — the post-launch tail didn’t crater, and the mix shifted toward organic Search as the social spike faded.' if commentary else 'Jun 18 = the ISSA Los Angeles preview talk. Launch Jun 23 (283); peak Jun 24 (403); Jun 25 complete at 210.'
    P.append(f'<div class="sec">{timeline}<p class="sub" style="margin:12px 0 0">{cap_daily}</p></div>')

    # referrers
    order = ["LinkedIn","Direct","Internal site nav","Search (Google/Bing)","MS Teams","Facebook","Exabeam.com","GitHub.com","BusinessWire (release)","Slack","Editorial press","Other"]
    present = [(k, px_cat[k]) for k in order if px_cat.get(k)]
    cmax = max(c for _, c in present)
    def cc(k): return "#5b8def" if k == "LinkedIn" else ("#e8621d" if k == "Editorial press" else ("#6f819a" if k == "Direct" else "#ff9d4d"))
    refcat = "".join(bar(k, c, cmax, sub=f"{c/px_total*100:.0f}%", color=cc(k)) for k, c in present)
    ext_rows = "".join(f"<tr><td>{r}</td><td class='n'>{c}</td></tr>" for r, c in px_ext[:14])
    P.append('<h2>Referrers to the Praxen landing page (<code>/praxen</code>)</h2>')
    P.append(cm(f'<div class="callout warn"><h3>The editorial press isn’t converting to <i>this site</i></h3><p>Of <b>{px_total}</b> referrals to <code>/praxen</code>, the editorial coverage drove just <b>{press}</b>. Under default browser referrer policy those outlets <i>would</i> appear if readers clicked through — so the absence is real, not hidden in "direct."</p><p><b>What converted were audience-owned channels:</b> <b>LinkedIn ({lk})</b> (the launch post) and <b>Direct ({px_cat.get("Direct",0)})</b> (much of it the Jun 18 ISSA LA talk audience plus typed/app links). Big <i>awareness</i> from ~25 placements; little measured conversion to the Pages site — <b>but press that links the repo instead <i>does</i> convert there</b> (see <b>GitHub repository — traffic</b> below).</p></div>'))
    P.append(f'<div class="sec">{refcat}</div>')
    P.append('<h3 style="font-size:14px;color:var(--mut);margin:18px 0 4px">External referrers to <code>/praxen</code>, itemized</h3>')
    P.append(f'<div class="sec"><table><tr><td><b style="color:var(--tx)">Referrer</b></td><td class="n"><b style="color:var(--tx)">Hits</b></td></tr>{ext_rows}</table></div>')

    # top pages
    pxp = "".join(bar(p, c, pxpaths[0][1]) for p, c in pxpaths[:12])
    P.append('<h2>Top Praxen pages</h2>')
    P.append(f'<div class="sec">{pxp}' + cm('<p class="sub" style="margin:12px 0 0">Healthy funnel: landing → docs. Quickstart and "What is ABV" lead the docs.</p>') + '</div>')

    # geo
    geo_items = byloc.most_common(14); gmax = geo_items[0][1]
    geo = "".join(bar(loc, c, gmax) for loc, c in geo_items)
    P.append('<h2>Geography</h2>')
    P.append(f'<div class="sec">{geo}<p class="sub" style="margin:12px 0 0">US total across states ≈ <b>{us}</b>.' + cm(' US-heavy (California leads) but genuinely global: UK, India, Singapore, Australia, Canada, Germany, UAE.') + '</p></div>')

    # social
    ctr_i = LI["clicks"]/LI["impr"]*100; ctr_r = LI["clicks"]/LI["reach"]*100
    lk_share = LI["clicks"]/lk*100 if lk else 0
    P.append('<h2>Social — the LinkedIn launch post</h2>')
    P.append(f'<p class="sub">The single biggest identifiable driver of site traffic. <a href="https://www.linkedin.com/posts/wilsonsd_ive-been-working-like-crazy-on-this-for-ugcPost-7475219279647354880-Pz03/" target="_blank" rel="noopener" style="color:var(--or2)">View post &#8599;</a></p>')
    P.append(f'<div class="cards"><div class="card"><b>{LI["impr"]:,}</b><span>impressions</span></div><div class="card"><b>{LI["reach"]:,}</b><span>members reached</span></div><div class="card"><b>{LI["vid"]:,}</b><span>video views</span></div><div class="card"><b>{LI["clicks"]}</b><span>clicks &#8594; /praxen</span></div></div>')
    P.append('<div class="sec">'
        + f'<div class="row"><span class="rl">Impressions</span><span class="rbar"><i style="width:100%;background:#5b8def"></i></span><span class="rv">{LI["impr"]:,}</span></div>'
        + f'<div class="row"><span class="rl">Members reached</span><span class="rbar"><i style="width:{LI["reach"]/LI["impr"]*100:.0f}%;background:#5b8def"></i></span><span class="rv">{LI["reach"]:,}</span></div>'
        + f'<div class="row"><span class="rl">Video views</span><span class="rbar"><i style="width:{LI["vid"]/LI["impr"]*100:.0f}%;background:#5b8def"></i></span><span class="rv">{LI["vid"]:,}</span></div>'
        + f'<div class="row"><span class="rl">Social engagements</span><span class="rbar"><i style="width:5%;background:#ff9d4d"></i></span><span class="rv">{LI["eng"]}</span></div>'
        + f'<div class="row"><span class="rl">Link clicks &#8594; /praxen</span><span class="rbar"><i style="width:4%;background:#ff7a2e"></i></span><span class="rv">{LI["clicks"]}</span></div>'
        + f'<p class="sub" style="margin:12px 0 0">~{ctr_i:.1f}% click-through on impressions, ~{ctr_r:.1f}% on members reached. Avg video watch {LI["avg"]} across {LI["vid"]:,} views ({LI["watch"]} total); {LI["prof"]} profile viewers and {LI["foll"]} new followers.</p></div>')
    P.append(cm(f'<div class="callout"><h3>One post drove ~90% of LinkedIn traffic</h3><p>LinkedIn counts <b>{LI["clicks"]} visits</b> to the post’s link (<code>open-agent-ai-security.github.io/praxen/</code>) — about <b>{lk_share:.0f}% of GoatCounter’s {lk} LinkedIn referrals</b> to <code>/praxen</code> (the rest from the {LI["rep"]} reposts).</p><p><b>The pattern, restated:</b> a direct, trackable link converts. The launch post and the ISSA LA talk — both audience-owned, both linking straight in — did the work. Press placements that linked the Pages site drove ~0 there; the one that linked the repo (Help Net) converted to GitHub. The variable is always the link.</p></div>'))
    P.append(f'<h3 style="font-size:14px;color:var(--mut);margin:18px 0 4px">Engagement breakdown ({LI["eng"]} social engagements)</h3>')
    P.append('<div class="sec">'
        + f'<div class="row"><span class="rl">Reactions</span><span class="rbar"><i style="width:100%;background:#ff9d4d"></i></span><span class="rv">{LI["react"]}</span></div>'
        + f'<div class="row"><span class="rl">Comments</span><span class="rbar"><i style="width:{LI["com"]/LI["react"]*100:.0f}%;background:#ff9d4d"></i></span><span class="rv">{LI["com"]}</span></div>'
        + f'<div class="row"><span class="rl">Saves</span><span class="rbar"><i style="width:{LI["save"]/LI["react"]*100:.0f}%;background:#ff9d4d"></i></span><span class="rv">{LI["save"]}</span></div>'
        + f'<div class="row"><span class="rl">Reposts</span><span class="rbar"><i style="width:{LI["rep"]/LI["react"]*100:.0f}%;background:#ff9d4d"></i></span><span class="rv">{LI["rep"]}</span></div>'
        + f'<div class="row"><span class="rl">Sends</span><span class="rbar"><i style="width:3%;background:#ff9d4d"></i></span><span class="rv">{LI["send"]}</span></div></div>')

    # github repo traffic (separate property)
    ghmax = max(v for _, v in GH_DAILY)
    ghtl = "".join(bar(d + ("  ← ISSA LA" if d == "06/18" else ("  ← launch" if d == "06/23" else ("  ← peak" if d == "06/24" else ""))), v, ghmax, color="#67d98b") for d, v in GH_DAILY)
    ghrows = "".join(f"<tr><td>{s}</td><td class='n'>{v}</td><td class='n'>{u}</td></tr>" for s, v, u in GH_REFS)
    P.append('<h2>GitHub repository — traffic <span style="font-size:13px;color:var(--mut2);font-weight:400">(github.com · separate property from the Pages-site numbers above)</span></h2>')
    P.append(f'<p class="sub">The repo’s own GitHub Insights — a different property from the Pages hero measured above; the two are <b>not</b> additive. Repo views, last 14 days: <b>{GH_TOTAL}</b>.</p>')
    P.append(f'<div class="sec">{ghtl}<p class="sub" style="margin:12px 0 0">Same shape as the Pages site: a <b>Jun 18</b> bump (54 — the ISSA LA talk), then the launch on <b>Jun 23</b> (51) into the <b>Jun 24</b> peak (148).</p></div>')
    P.append('<h3 style="font-size:14px;color:var(--mut);margin:18px 0 4px">Referring sites to the repo</h3>')
    P.append(f'<div class="sec"><table><tr><td><b style="color:var(--tx)">Site</b></td><td class="n"><b style="color:var(--tx)">Views</b></td><td class="n"><b style="color:var(--tx)">Unique</b></td></tr>{ghrows}</table></div>')
    if commentary:
        P.append('<div class="callout"><h3>Press DOES convert — when it links the repo</h3><p><b>Help Net Security linked directly to GitHub</b> (not the Pages hero) and drove <b>18 repo views / 16 unique visitors</b> — the top external <i>press</i> referrer to the repo. GoatCounter never saw this (it only measures the Pages site), which is exactly why the Pages-side press referrals read ~0.</p><p>So the conversion finding sharpens rather than breaks: <b>coverage converts to wherever it links.</b> And the Pages hero is itself the #1 driver of repo traffic (157 views) — the hero &#8594; repo funnel works.</p></div>')
    else:
        P.append('<p class="sub">Help Net Security: 18 views / 16 unique — it linked to the repo, not the Pages hero. The Pages hero is the #1 referrer to the repo (157).</p>')

    # stars
    P.append('<h2>GitHub stars</h2>')
    P.append(f'<p class="sub">Stars on <code>open-agent-ai-security/praxen</code>. Currently <b>{STARS}</b>; <b>Jun 24</b> added 9 and <b>Jun 25</b> added 6 (the launch days).</p>')
    P.append(f'<div class="sec" style="background:#fff;padding:14px 14px 6px;overflow:hidden">{svg}</div>')
    P.append(cm(f'<p class="sub" style="margin:10px 0 0">Chart: star-history.com · snapshot {today}. A launch is a spike; the slope over the coming weeks is the real adoption signal.</p>'))

    P.append('<div class="callout"><h3>Caveats</h3><p>GoatCounter undercounts (privacy blockers, no-JS) and this is only the GoatCounter half of the Cloudflare A/B — true Pages traffic is higher. The GitHub-repo numbers are a separate property (GitHub Insights), not additive with the Pages numbers.</p></div>')
    P.append(f'<div class="foot">Sources: GoatCounter export 20260625T140651Z (Jun 18–25) · LinkedIn post analytics 2026-06-25 · GitHub repo Insights 2026-06-25 · stars via GitHub API · star-history.com · generated {today}.</div>')
    P.append('</div></body></html>')
    return "".join(P)

for fn, comm in [("launch-traffic-report.html", True), ("launch-traffic-facts.html", False)]:
    open(os.path.join(SCRIPT_DIR, fn), "w").write(page(comm))
    print("wrote", fn)
print(f"data: total={total} praxen={praxen} /praxen-refs={px_total} LinkedIn={lk} press={press} stars={STARS}")
