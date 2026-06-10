# Praxen Graphics

Brand and site assets for Praxen.

**Convention**
- **`graphics/`** holds **source masters** (full-resolution originals).
- **`graphics/web/`** holds the **site-linked copies** actually referenced by the landing page (`index.html`) and the docs nav (`docs_build.py` → every `guide/*.html`).
- References are **by path**. Replacing a file *in place* (same name) updates every consumer with no markup change and no `guide/` regeneration. **Renaming** a file means updating each consumer below and regenerating `guide/` (`python3 docs_build.py`), or the release freshness backstop will fail.
- No PIL/ImageMagick in the build environment, but macOS `sips` is available and is the right tool for PNG resize/convert (it handles alpha and Adam7-interlaced sources that a naive stdlib decoder mangles).

## `graphics/web/` — site-linked copies

| File | Size | Status | Used by |
|------|------|--------|---------|
| `praxen-logo-dark-background.png` | 1000×295 | **Used** | Landing nav (`index.html:284`) + footer (`:496`) and the docs nav template (`docs_build.py:135`, propagated to all 10 `guide/*.html`). White wordmark + "Agent Behavior Verifier" lockup, for **dark** backgrounds. |
| `praxen-logo-light-background.png` | — | **Planned** | Dark-ink version of the same lockup for **light** backgrounds. Not yet added; no consumer wired up yet. |
| `praxy-working.png` | 1500×1001 | **Used** | Hero mascot (`index.html:321`) — Praxy the fox inspecting a robot agent. Transparent. |
| `favicon-32.png` | 32×32 | **Used** | Browser tab icon (`index.html:16`). |
| `favicon-180.png` | 180×180 | **Used** | Apple touch icon (`index.html:18`). |
| `favicon-256.png` | 256×256 | **Used** | Bookmark / high-res icon (`index.html:17`). |

The three favicons are **generated from `../favicon-master.png`** (the orange-tile shield, sized down with `sips`) — re-derive them from it if the favicon art changes. See *Editing notes* for the commands. (256 is a mild upscale: the master is 192×192.)

## `graphics/` — source masters & other assets

| File | Size | Status | Purpose |
|------|------|--------|---------|
| `favicon-master.png` | 192×192 | **Master** | Orange-tile shield favicon — reads on light **and** dark. Source the `web/favicon-32/180/256.png` files are generated from (via `sips`). Not directly linked by the site. |
| `logo-only.png` | 345×371 | **Master** | Transparent shield-only logo. A brand master; no longer the favicon source (see `favicon-master.png`). Not directly linked by the site. |
| `praxy-working.png` | 1500×1001 | **Master** | Full-res source master for the hero; kept in sync with `web/praxy-working.png`. |
| `praxen-logo-dark-background.png` *(see web/)* | — | — | The lockup lives in `web/`; no separate master file. A `praxen-logo-light-background.png` companion is planned. |
| `praxen-social.png` | 1280×640 | **Used** | Open Graph + Twitter card image (`index.html:25`, `:29`). |
| `praxen-banner.png` | 1536×1024 | **Used** | Banner image in the repo `README.md` (`README.md:7`). |
| `exabeam-logo-white.svg` | — | **Used** | Sponsor band on the landing page (`index.html:528`). |
| `praxen-social-2.png` | 1280×640 | **Pending replacement** | Alternate social card; not currently linked. Kept — a replacement is coming. |
| `praxy-waves.png` | 1536×1024 | **Pending replacement** | Alternate mascot pose; not currently linked. Kept — a replacement is coming. |

## Editing notes

- **Swapping the hero or logo:** drop the new art on top of the file in `graphics/web/` (same name) and, for masters, update the matching `graphics/` file too. Verify transparency before committing — the hero and logo sit on dark backgrounds, so a baked-in white background will look wrong.
- **Changing the favicon:** update `favicon-master.png`, then regenerate the three sizes with `sips` (macOS built-in):
  ```sh
  for sz in 32 180 256; do sips -z $sz $sz graphics/favicon-master.png --out graphics/web/favicon-$sz.png; done
  ```
  (No PIL/ImageMagick on the box, but `sips` handles PNG resize + alpha. For a *correct* transparency check of an Adam7-interlaced PNG, use `sips`, not a naive stdlib decoder.)
- **Changing the docs nav logo across all guide pages:** the logo is templated in `docs_build.py` (the `guide/*.html` pages are generated, not hand-edited); replacing `web/praxen-logo-dark-background.png` in place is enough (path unchanged). Changing the *filename* or template means editing `docs_build.py` and regenerating with `python3 docs_build.py`.
