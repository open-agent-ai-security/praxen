# Praxen Graphics

Brand and site assets for Praxen.

**Convention**
- **`graphics/`** holds **source masters** (full-resolution originals).
- **`graphics/web/`** holds the **site-linked copies** actually referenced by the landing page (`index.html`) and the docs nav (`docs_build.py` → every `guide/*.html`).
- References are **by path**. Replacing a file *in place* (same name) updates every consumer with no markup change and no `guide/` regeneration. **Renaming** a file means updating each consumer below and regenerating `guide/` (`python3 docs_build.py`), or the release freshness backstop will fail.
- No PIL/ImageMagick in the build environment — favicon generation and any resizing are done with pure-stdlib PNG decode/encode.

## `graphics/web/` — site-linked copies

| File | Size | Status | Used by |
|------|------|--------|---------|
| `praxen-logo-dark-background.png` | 1000×295 | **Used** | Landing nav (`index.html:284`) + footer (`:496`) and the docs nav template (`docs_build.py:135`, propagated to all 10 `guide/*.html`). White wordmark + "Agent Behavior Verifier" lockup, for **dark** backgrounds. |
| `praxen-logo-light-background.png` | — | **Planned** | Dark-ink version of the same lockup for **light** backgrounds. Not yet added; no consumer wired up yet. |
| `praxy-working.png` | 1500×1001 | **Used** | Hero mascot (`index.html:321`) — Praxy the fox inspecting a robot agent. Transparent. |
| `favicon-32.png` | 32×32 | **Used** | Browser tab icon (`index.html:16`). |
| `favicon-180.png` | 180×180 | **Used** | Apple touch icon (`index.html:18`). |
| `favicon-256.png` | 256×256 | **Used** | Bookmark / high-res icon (`index.html:17`). |

The three favicons are **generated from `../logo-only.png`** (the shield master) — re-derive them from it if the shield changes.

## `graphics/` — source masters & other assets

| File | Size | Status | Purpose |
|------|------|--------|---------|
| `logo-only.png` | 345×371 | **Master** | Shield-only logo. Source master the favicons (`web/favicon-32/180/256.png`) are generated from. Not directly linked by the site. |
| `praxy-working.png` | 1500×1001 | **Master** | Full-res source master for the hero; kept in sync with `web/praxy-working.png`. |
| `praxen-logo-dark-background.png` *(see web/)* | — | — | The lockup lives in `web/`; no separate master file. A `praxen-logo-light-background.png` companion is planned. |
| `praxen-social.png` | 1280×640 | **Used** | Open Graph + Twitter card image (`index.html:25`, `:29`). |
| `praxen-banner.png` | 1536×1024 | **Used** | Banner image in the repo `README.md` (`README.md:7`). |
| `exabeam-logo-white.svg` | — | **Used** | Sponsor band on the landing page (`index.html:528`). |
| `praxen-social-2.png` | 1280×640 | **Pending replacement** | Alternate social card; not currently linked. Kept — a replacement is coming. |
| `praxy-waves.png` | 1536×1024 | **Pending replacement** | Alternate mascot pose; not currently linked. Kept — a replacement is coming. |

## Editing notes

- **Swapping the hero or logo:** drop the new art on top of the file in `graphics/web/` (same name) and, for masters, update the matching `graphics/` file too. Verify transparency before committing — the hero and logo sit on dark backgrounds, so a baked-in white background will look wrong.
- **Changing the shield:** update `logo-only.png`, then regenerate `web/favicon-32/180/256.png` from it.
- **Changing the docs nav logo across all guide pages:** the logo is templated in `docs_build.py` (the `guide/*.html` pages are generated, not hand-edited); replacing `web/praxen-logo-dark-background.png` in place is enough (path unchanged). Changing the *filename* or template means editing `docs_build.py` and regenerating with `python3 docs_build.py`.
