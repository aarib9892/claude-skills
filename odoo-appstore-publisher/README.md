# odoo-appstore-publisher

[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-skill-8A3FFC)](https://code.claude.com/docs/en/skills)
[![Odoo 18 | 19](https://img.shields.io/badge/Odoo-18%20%7C%2019-875A7B)](https://apps.odoo.com)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org)

A Claude Code **skill** that turns a delivered Odoo module + a PM's asset PDF into a
module zip that uploads to [apps.odoo.com](https://apps.odoo.com) with no errors —
correct manifest, sized icon/banner/screenshots, video→GIF, and a sanitizer-safe,
mobile-friendly `static/description/index.html`.

Targets Odoo **18** and **19**. Built for the Vizion Tools team; anyone can use it.

## Install

This skill lives in the [`claude-skills`](https://github.com/aarib9892/claude-skills) collection.
Clone the collection and symlink this skill into your Claude Code skills directory:

```bash
git clone https://github.com/aarib9892/claude-skills.git
ln -s "$(pwd)/claude-skills/odoo-appstore-publisher" ~/.claude/skills/odoo-appstore-publisher
```

Or copy just this subdirectory into `~/.claude/skills/` (personal, all projects) or a project's
`.claude/skills/` so it ships with that repo.

### Dependencies

```bash
pip install -r requirements.txt      # Pillow, PyMuPDF
sudo apt install ffmpeg              # video -> GIF
```

## Use

In Claude Code:

```
/odoo-appstore-publisher
```

Then give it the **asset PDF**, the **module zip**, and (if not obvious) the target
Odoo version and whether the module is free or paid. The skill extracts assets, asks
you about anything missing or ambiguous, rebuilds the module, validates it, and writes
`output/<module>-<version>.zip`.

## Example

Publishing `vizion_low_stock_notification` (a paid v18 module) from a PM's PDF:

```
> /odoo-appstore-publisher
  PDF:    ~/Downloads/Low_Stock_Notification.pdf
  Module: ~/dev_odoo/vizion_18/vizion_low_stock_notification
```

What the skill does:

1. Extracts the PDF text + images, finds the Drive-linked banner/screenshots (`links.txt`) and downloads them.
2. Flags what's missing or ambiguous — here: no icon embedded, a $25 price, a placeholder support email — and asks you before building.
3. Crops the bell from the banner into a 140×140 `icon.png`; sizes the banner (≤1920px) and screenshots.
4. Patches `__manifest__.py` (paid → `license='OPL-1'`, `price='25.00'`, `currency='USD'`, `images=[…]`), writes the OPL-1 `LICENSE`, and builds a stacked, sanitizer-safe `index.html`.
5. Runs `validate_module.py` until green, then zips → `output/vizion_low_stock_notification-18.0.1.0.2.zip`.

Any script also runs standalone:

```bash
python scripts/extract_pdf.py assets.pdf ./out                 # text + images + links.txt
python scripts/fetch_drive.py "<drive-share-url>" ./out/banner.png
python scripts/process_images.py icon logo.png ./mod/static/description
python scripts/video_to_gif.py demo.mp4 ./mod/static/description/demo.gif --fps 12 --width 720
python scripts/validate_module.py ./mod                        # exits non-zero if not ready
```

## What's inside

| Path | Purpose |
|---|---|
| `SKILL.md` | The procedure Claude follows. |
| `references/app_store_rules.md` | Odoo App Store rules + a living "Gotchas" log. |
| `templates/index.html` | House description-page template (stacked layout, no flex/grid). |
| `assets/vizion_icon.png` | Standard Vizion brand icon, copied to every module (swap for your own brand). |
| `scripts/extract_pdf.py` | PDF → text + embedded images + hyperlinks (`links.txt`). |
| `scripts/fetch_drive.py` | Download a linked asset (Google Drive share URL → file). |
| `scripts/process_images.py` | Icon (140×140 PNG), banner/screenshot normalize. |
| `scripts/video_to_gif.py` | Video → optimized animated GIF (ffmpeg). |
| `scripts/validate_module.py` | Pre-upload gate: manifest, version, currency, files, index.html. |

Every script runs a self-check with `--selftest`.

## Contributing

Hit a new App Store gotcha? Add it to the **Gotchas / lessons learned** section of
`references/app_store_rules.md` and commit — that's how the skill gets smarter over time.
