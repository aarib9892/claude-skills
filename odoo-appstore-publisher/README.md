# odoo-appstore-publisher

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

## What's inside

| Path | Purpose |
|---|---|
| `SKILL.md` | The procedure Claude follows. |
| `references/app_store_rules.md` | Odoo App Store rules + a living "Gotchas" log. |
| `templates/index.html` | House description-page template (stacked layout, no flex/grid). |
| `scripts/extract_pdf.py` | PDF → text + embedded images. |
| `scripts/process_images.py` | Icon (140×140 PNG), banner/screenshot normalize. |
| `scripts/video_to_gif.py` | Video → optimized animated GIF (ffmpeg). |
| `scripts/validate_module.py` | Pre-upload gate: manifest, version, currency, files, index.html. |

Every script runs a self-check with `--selftest`.

## Contributing

Hit a new App Store gotcha? Add it to the **Gotchas / lessons learned** section of
`references/app_store_rules.md` and commit — that's how the skill gets smarter over time.
