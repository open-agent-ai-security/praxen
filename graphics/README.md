# Praxen Graphics

Brand and site assets for Praxen.

**Convention**
- **`graphics/brand/`** — the canonical **brand source set**: an **SVG vector master** (the source of truth) plus a matching **PNG raster** export for every logo form × background. Delivered by the art department; the SVGs are outlined-path vectors (no live `<text>`, so no font dependency) with a `viewBox`, gradients, and no external refs.
- **`graphics/`** — other source masters (the Praxy mascot, social/banner art) and the sponsor logo.
- **`graphics/web/`** — the **raster web copies** the site links that genuinely need rasterization (the favicons). On-page logos are **SVG, referenced directly from `graphics/brand/`** — vectors need no separate optimized copy.
- **Format policy.** On-page logos (landing nav/footer, docs nav) use **SVG** — sharp at any DPI, tiny, scales perfectly. **Favicons, social/OG cards, and the repo README banner stay PNG** for browser/scraper compatibility (see *Editing notes*).
- No PIL/ImageMagick in the build environment; macOS **`sips`** handles PNG resize (and the Adam7-interlaced art-dept PNGs). SVG→raster isn't needed — the art department ships both formats.

## `graphics/brand/` — brand source set (SVG master + PNG raster per entry)

Naming is by the **background the asset sits on**: `-dark-background` = light/white art for dark backgrounds; `-light-background` = dark-ink art for light backgrounds.

| Base name (`.svg` + `.png`) | Form | For background | Used by |
|---|---|---|---|
| `praxen-favicon` | Shield app-tile (orange) | self-contained | **Favicon master** → `web/favicon-32/180/256.png` |
| `praxen-lockup-dark-background` | Shield + "Praxen" + descriptor, horizontal | dark | **Landing nav (`index.html:284`) + footer (`:496`) + docs nav (`docs_build.py:135` → all `guide/*.html`)** — the SVG is referenced directly |
| `praxen-lockup-light-background` | Same lockup | light | Available (no light-bg surface on the site yet) |
| `praxen-lockup-stacked-dark-background` | Shield over wordmark+descriptor | dark | Available (square-ish contexts) |
| `praxen-lockup-stacked-light-background` | Same, stacked | light | Available |
| `praxen-wordmark-dark-background` | Shield + "Praxen", **no** descriptor, horizontal | dark | Available |
| `praxen-wordmark-light-background` | Same wordmark | light | Available |
| `community-logo-dark-background` | "Open Agentic and AI Security Community" (umbrella org — purple shield) | dark | Available — the **parent-org** brand, not Praxen's |
| `community-logo-light-background` | Same | light | Available |

## `graphics/web/` — raster web copies

| File | Size | Status | Used by |
|---|---|---|---|
| `favicon-32.png` | 32×32 | **Used** | Browser tab icon (`index.html:16`) |
| `favicon-180.png` | 180×180 | **Used** | Apple touch icon (`index.html:18`) |
| `favicon-256.png` | 256×256 | **Used** | Bookmark / high-res icon (`index.html:17`) |
| `praxy-working.png` | 1500×1001 | **Used** | Hero mascot (`index.html:321`) |

The three favicons are **generated from `../brand/praxen-favicon.png`** (the 743² orange-tile master, sized down with `sips`).

## `graphics/` — other masters & assets

| File | Status | Purpose |
|---|---|---|
| `praxy-working.png` | **Master** | Full-res source master for the hero; kept in sync with `web/praxy-working.png` |
| `logo-only.png` | **Master** | Transparent shield-only mark; a brand master (the new favicon's tile lives in `brand/`). Not directly linked by the site |
| `praxen-social.png` | **Used** | Open Graph + Twitter card image (`index.html:25`, `:29`) — fox + robot, 1.91:1. **Stays PNG** (social scrapers don't render SVG) |
| `praxen-banner.png` | **Used** | Promo banner in the repo `README.md` (`README.md:7`) — logo + mascot + four-step overview. **Stays PNG** |
| `exabeam-logo-white.svg` | **Used** | Sponsor band on the landing page (`index.html:528`) |
| `praxy-waves.png` | **Pending replacement** | Alternate mascot pose; not currently linked |

## Editing notes

- **Swapping the on-page logo:** edit the SVG in `graphics/brand/` — it's both the master *and* what the site renders. Replacing it in place (same path) updates the landing nav/footer and all 10 `guide/*.html` with no markup change and no `guide/` regen. Changing the *filename* means updating `index.html` + `docs_build.py` and running `python3 docs_build.py`.
- **Changing the favicon:** edit `brand/praxen-favicon.{svg,png}`, then regenerate the three sizes with `sips`:
  ```sh
  for sz in 32 180 256; do sips -z $sz $sz graphics/brand/praxen-favicon.png --out graphics/web/favicon-$sz.png; done
  ```
- **Why SVG on-page but PNG for favicons/social/banner:** `<img>`-referenced SVG is universal in browsers and these logos are outlined paths (no font dependency). But SVG favicons aren't reliable in Safari/older browsers, social-card scrapers (`og:image`) require raster, and GitHub renders SVG in markdown inconsistently — so those three stay PNG, generated from the masters.
