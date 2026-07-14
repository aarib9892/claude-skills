# claude-skills

Claude Code skills for the Vizion Tools team. Each subdirectory is a self-contained skill.

## Skills

| Skill | Purpose |
|---|---|
| [odoo-appstore-publisher](odoo-appstore-publisher/) | Prepare a delivered Odoo module (v18/v19) for publishing on the Odoo App Store from an asset PDF + module zip. |

## Install

Clone the repo, then symlink the skill(s) you want into your Claude Code skills directory:

```bash
git clone https://github.com/aarib9892/claude-skills.git
ln -s "$(pwd)/claude-skills/odoo-appstore-publisher" ~/.claude/skills/odoo-appstore-publisher
```

(Or copy the subdirectory instead of symlinking.) See each skill's own `README.md` for its
dependencies and usage.
