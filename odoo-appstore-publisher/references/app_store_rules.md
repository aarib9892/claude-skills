# Odoo App Store rules (v18 / v19) — quick reference

Condensed from official Odoo docs + vendor guidelines. Sources at the bottom.

## `__manifest__.py`

Odoo itself only requires `name`. For a good **listing**, set:

| Field | Notes |
|---|---|
| `name` | Explicit; ≤ 25 chars reads best in the store. English. |
| `version` | `<series>.x.y.z` → `18.0.1.0.0` or `19.0.1.0.0`. Bump when a schema change needs an update. |
| `summary` | One SEO line — feeds store search. Put the strongest accurate keywords here + in `name`. |
| `description` | Long text (RST/plain). |
| `license` | `LGPL-3` (free/open) or `OPL-1` (paid/proprietary). Full valid set below. |
| `author` | `Vizion Tools` |
| `website` | `https://viziontools.com` |
| `category`, `application`, `installable` | `application: True` gets an app tile. `installable: True`. |
| `depends` | Must list every real dependency; a missing/nonexistent one = automatic rejection. |
| `images` | Every image shown on the listing must be declared here (paths under `static/description/`). |
| `price` + `currency` | Paid apps only. **`currency` must be `USD` or `EUR`.** Odoo takes 30% commission. Price on Odoo ≤ price elsewhere. |
| `support`, `live_test_url`, `maintainer` | Optional. `live_test_url` = canonical YouTube link or a demo URL. |

**Valid `license` strings:** `GPL-2`, `GPL-2 or any later version`, `GPL-3`, `GPL-3 or any later version`, `AGPL-3`, `LGPL-3`, `Other OSI approved licence`, `OEEL-1`, `OPL-1`, `Other proprietary`. Default when omitted: `LGPL-3`. Ship a `LICENSE` file at the module root matching it.

## `static/description/index.html`

The listing description page. Rendered inside an Odoo (Bootstrap) page and **run through Odoo's HTML sanitizer on upload**, which **strips** from inline `style`:
`display:flex`, `display:grid`, `grid-template`, `gap`, `flex-*`, `justify-content`, `align-items`, `transform`, `transition`, `linear-gradient`, `rgba()`, `box-shadow`, animations, and any JS handlers. Bootstrap `d-flex`/`d-grid` classes also produce flex → avoid them too.

**Do:** simple stacked/block layout (`<section>`/`<div>` with `max-width` + `margin:auto`, images `max-width:100%`) — mobile-friendly by construction. Allowed inline props: hex colors, `font-*`, `margin-*`, `padding-*`, `border-*`, `text-align`, `width`. Use `<table>` **only for genuinely tabular content**, never for page layout. Start the file with content — no `<!DOCTYPE>/<html>/<head>/<body>`. Reference images relative to `static/description/`.

Template: `templates/index.html` in this skill.

## Assets

- **Icon:** `static/description/icon.png`, **PNG only**, ~140×140 px (community standard). Wrong path or non-PNG → generic white-cube icon.
- **Screenshots / banner:** declared in manifest `images`. The first image whose name ends in `_screenshot` becomes the large listing image — make it a real demo screen, not a logo.
- **Formats:** PNG / GIF / JPEG only (no SVG). Keep source width ≤ ~1920px (Odoo compresses beyond that).
- **Video → GIF:** videos can't be embedded (iframes/JS stripped). Convert to an animated GIF `<img>`. Only canonical YouTube links are allowed, as `live_test_url`.

## Validation (before upload)

No official "app store linter." The upload scan parses the manifest and requires the module to install by copy-into-addons. Common auto-fail causes: bad `version` format; nonexistent `depends`; `currency` not USD/EUR; `data`/`images` entries pointing at missing files; malformed manifest (missing comma, `date` vs `data`, non-UTF-8/hidden chars); missing `license`/`LICENSE`.

Validate locally:
- `python scripts/validate_module.py <module_dir>` (this skill) — catches the above + forbidden index.html layout.
- `odoo -i <module> -d testdb --stop-after-init` on a clean DB — catches manifest/dependency/XML errors.

Content grounds for later rejection/unpublish: clones of Enterprise modules, obfuscated/malicious code, undocumented hidden behavior, collecting user data without opt-in, no customer support, promotional text / links to other app stores.

## v18 vs v19

Manifest format, license values, and version rule are identical — only the `18.0.`/`19.0.` prefix differs. `countries` key (target/restrict by country) exists in both. Each series is a **separate upload**; there's no cross-version listing.

---

## Gotchas / lessons learned  (append here as the team hits new issues — note #4)

- Odoo's sanitizer silently strips inline flex/grid/gap/transform/gradient — an inline-flex layout collapses after upload. Use stacked blocks.
- `currency` must be exactly `USD` or `EUR`; anything else fails the scan.
- `version` must carry the series prefix (`18.0.`/`19.0.`) and be 5 parts.
- `ffmpeg` is required for the video→GIF step (`sudo apt install ffmpeg`).
- PDF image order is not reliable → always confirm which extracted image is icon/banner/screenshot before building.
- `name` ≤ 25 chars; every displayed image must be in manifest `images`.
- `icon.png` must be a real PNG at `static/description/icon.png`.
- Each Odoo series (18, 19) is uploaded separately.
- Assets are often **linked (Google Drive), not embedded** in the PDF — check `extracted/links.txt`
  and download with `scripts/fetch_drive.py`. Links must be shared "anyone with the link".
- No app icon in the PDF? Crop the glyph/logo from the banner to make an on-brand `icon.png`.
- PDFs may carry **placeholder support fields** (`[support email]`, `[support URL]`). Don't ship
  placeholders — get the real support email or omit the `support` key.
- Paid module → set `license` = `OPL-1`, `price`, and `currency` (USD/EUR), and ship the OPL-1
  `LICENSE` file at the module root.
- Don't repeat the banner as the first block of index.html — it's already the listing cover
  (`images[0]`); start the page with the title.
- **Icon is standardized:** every Vizion module ships the SAME icon — `assets/vizion_icon.png` (gold
  "V" on navy), copied verbatim. Never generate or crop a per-module icon. 16+ modules already share
  this exact file.
- **House naming convention:** the cover banner is `main_screenshot.png` (= `images[0]`), a wide
  branded graphic — NOT a raw app screen. Real app screenshots are `screenshot_1.png`,
  `screenshot_2.png`, … Never name a real screenshot `main_screenshot`. (`banner.png` is an accepted
  alternate cover name in older modules; prefer `main_screenshot.png` going forward.)

---

### Sources
- Manifest reference: https://www.odoo.com/documentation/19.0/developer/reference/backend/module.html · https://www.odoo.com/documentation/18.0/developer/reference/backend/module.html
- Vendor guidelines: https://apps.odoo.com/apps/vendor-guidelines
- Apps FAQ: https://apps.odoo.com/apps/faq
- Upload page (shows current per-slot image requirements when logged in): https://apps.odoo.com/apps/upload
- index.html HTML guide: https://github.com/apexive/odoo-llm/blob/18.0/ODOO_APP_STORE_HTML_GUIDE.md
- OCA description template: https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/index.html
