---
name: odoo-appstore-publisher
description: |
  Prepare a delivered Odoo module (v18 or v19) for publishing on the Odoo App Store from a PDF of
  marketing assets plus the module zip. Produces a module zip that uploads to apps.odoo.com with no
  errors: correct __manifest__.py, sized icon/banner/screenshots, videos converted to GIFs, and a
  sanitizer-safe, mobile-friendly static/description/index.html. Use when the user wants to publish
  or republish an Odoo module to the app store, or invokes /odoo-appstore-publisher.
---

You are preparing an Odoo module for the Odoo App Store. **Input:** an asset PDF + a module zip.
**Output:** `output/<module>-<version>.zip`, ready to upload with no errors.

All paths below (`scripts/`, `templates/`, `references/`) are inside this skill's directory. Read
`references/app_store_rules.md` before editing the manifest or index.html — it holds the exact rules
and a "Gotchas" log. Deep house style: author **Vizion Tools**, website **https://viziontools.com**,
brand purple **#875A7B**.

## 0. Gather inputs

Ask the user for the **PDF path** and the **module zip path** if not given. Determine the **target
Odoo version (18 or 19)** and **free vs paid** — infer from the existing manifest; ask only if
unclear. Do the work in a scratch dir, e.g. `./_publish_work/`.

## 1. Unzip & locate the module

Unzip into the scratch dir. The module folder is the one containing `__manifest__.py`. Read that
manifest — it's your starting point; you're upgrading it, not replacing it.

## 2. Extract the PDF

```bash
python scripts/extract_pdf.py <pdf> ./_publish_work/extracted
```

Read `extracted/text.txt`. If it warns that PyMuPDF is missing (no images extracted), tell the user
and either install PyMuPDF or ask them to supply logo/banner/screenshots as separate files.

**Also check `extracted/links.txt`** — PMs often link assets (banner, hi-res screenshots) via Google
Drive instead of embedding them. Download each linked asset:

```bash
python scripts/fetch_drive.py "<url from links.txt>" ./_publish_work/extracted/banner.png
```

(Drive links must be shared "anyone with the link".) The linked versions are usually higher quality
than any embedded copy — prefer them.

## 3. Map assets → roles

From the text, pull: module **name**, **summary** (one line), **description**, **feature list**,
**price** + **currency** (if paid), **keywords**, and any **video** file names. Look at the extracted
images and decide which is the **banner** and which are the **screenshots** (and their order). Image
order out of a PDF is unreliable — do not guess silently. (The icon is not sourced from the PDF — it's
always the standard `assets/vizion_icon.png`.)

## 4. Missing / ambiguous gate — ASK IMMEDIATELY  (note #1)

Before building anything, confirm you have each required item. If **any** are missing, or an
image→role mapping is uncertain, **ask the user right now** (AskUserQuestion when interactive) — do
not invent assets or proceed on a guess.

Required checklist:
- [ ] name  · summary  · description
- [ ] banner (cover)  · at least one screenshot   (icon is always the standard `assets/vizion_icon.png`)
- [ ] which video file → GIF (videos come as separate files)
- [ ] price + currency (USD or EUR) — only if paid
- [ ] license (LGPL-3 free / OPL-1 paid)
- [ ] target Odoo version (18 or 19)

## 5. Process assets into `static/description/`

```bash
cp assets/vizion_icon.png                             <module>/static/description/icon.png
python scripts/process_images.py image <banner_src>   <module>/static/description/main_screenshot.png
python scripts/process_images.py image <shot1_src>    <module>/static/description/screenshot_1.png
python scripts/process_images.py image <shot2_src>    <module>/static/description/screenshot_2.png
# ... one screenshot_N.png per app screenshot
python scripts/video_to_gif.py <video>  <module>/static/description/demo.gif
```

Images → PNG/JPG/GIF, width ≤ 1920.

**Icon: always the same standard Vizion brand icon** — copy `assets/vizion_icon.png` verbatim to every
module (do NOT generate or crop a per-module icon). It matches the icon the rest of the Vizion catalog
ships. (A non-Vizion team swaps `assets/vizion_icon.png` for their own brand icon.)

**House naming convention (match the existing published modules):**
- The **cover banner** is `main_screenshot.png` — the wide branded graphic, and `images[0]` in the
  manifest. (`banner.png` is an accepted alternate, but prefer `main_screenshot.png`.)
- Real app screenshots are `screenshot_1.png`, `screenshot_2.png`, … **Never** name a real screenshot
  `main_screenshot` — that name is reserved for the banner.

## 6. Patch `__manifest__.py`

Edit the dict (keep existing valid values). Set:
- `name` (≤ 25 chars if you can), SEO `summary`, `description`
- `author='Vizion Tools'`, `website='https://viziontools.com'`, `category`
- `version` = `18.0.x.y.z` or `19.0.x.y.z` (match target series; bump from current)
- `license` = `'LGPL-3'` (free) or `'OPL-1'` (paid)
- if paid: `price` + `currency` (`'USD'` or `'EUR'` only)
- `images` = cover banner first (`static/description/main_screenshot.png`), then every screenshot/GIF you reference
- `support` email, `live_test_url` (YouTube/demo) if provided
- `application=True`, `installable=True`
- Verify every `depends` entry is a real module (a bad depend = auto-reject).

## 7. Write `static/description/index.html`

Copy `templates/index.html` and fill the `{{PLACEHOLDERS}}`; delete unused blocks and the guidance
comment. **Rules (enforced in step 9):** stacked/block layout only, mobile-friendly (`max-width:100%`
images); **no flexbox, grid, gap, transform, gradient, or `d-flex`/`d-grid` classes** — Odoo's
sanitizer strips them. Use a `<table>` only for genuinely tabular content, never for layout. Purple
`#875A7B`. Reference images by bare filename (relative to `static/description/`). **Do not lead the
page with the banner image** — it's already the listing cover (`images[0]`), so repeating it as the
first block is redundant; start with the title.

## 8. LICENSE file

Ensure a `LICENSE` file exists at the module root matching the chosen license (create it if missing).

## 9. Validate — the no-errors gate

```bash
python scripts/validate_module.py <module_dir>
```

Fix everything it flags and re-run until it prints `✓ ... ready to upload`. It checks manifest parse,
version format, currency, that all `data`/`images` files exist, icon is a real PNG, and index.html
has no forbidden layout.

## 10. Package

Zip the module folder (not its parent) so the archive root is the module dir:

```bash
mkdir -p output && (cd <module_parent> && \
  zip -r ../output/<module>-<version>.zip <module> \
      -x '*/__pycache__/*' '*.pyc' '*/.git/*' '*/.DS_Store')
```

Report the output path and a one-line summary of what changed. Optionally suggest the user smoke-test
with `odoo -i <module> -d testdb --stop-after-init` on a clean DB before uploading.

---

**When you learn something new** (a rejection reason, a sanitizer quirk, a manifest gotcha), append it
to the *Gotchas / lessons learned* section of `references/app_store_rules.md` so the next run doesn't
repeat it (note #4).
