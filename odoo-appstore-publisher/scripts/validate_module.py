#!/usr/bin/env python3
"""Validate an Odoo module folder is safe to upload to apps.odoo.com.

Usage:
    python validate_module.py <module_dir>     # validate, exit 1 on any error
    python validate_module.py --selftest       # run built-in checks

Checks (errors block upload, warnings are advisory):
  - __manifest__.py parses to a dict, has a name
  - version matches <series>.x.y.z with series 18.0 or 19.0
  - license is a value Odoo accepts
  - currency is USD or EUR when a price is set
  - every file listed in data / images actually exists
  - static/description/icon.png exists and is a real PNG
  - index.html uses no flex/grid/gap/transform/gradient (Odoo's sanitizer strips them)
"""
import ast
import os
import re
import sys

VERSION_RE = re.compile(r"^(18|19)\.0\.\d+\.\d+\.\d+$")
VALID_LICENSES = {
    "GPL-2", "GPL-2 or any later version", "GPL-3", "GPL-3 or any later version",
    "AGPL-3", "LGPL-3", "Other OSI approved licence", "OEEL-1", "OPL-1",
    "Other proprietary",
}
VALID_CURRENCIES = {"USD", "EUR"}
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

# Patterns that Odoo's HTML sanitizer strips from inline styles, plus the
# Bootstrap flex utility classes. Any hit is a hard error.
FORBIDDEN_HTML = [
    (re.compile(r"display\s*:\s*flex", re.I), "inline display:flex"),
    (re.compile(r"display\s*:\s*grid", re.I), "inline display:grid"),
    (re.compile(r"grid-template", re.I), "css grid-template"),
    (re.compile(r"\bgap\s*:", re.I), "inline gap:"),
    (re.compile(r"flex-(direction|wrap|grow|shrink|basis|flow)", re.I), "flex-* property"),
    (re.compile(r"justify-content", re.I), "justify-content"),
    (re.compile(r"align-items", re.I), "align-items"),
    (re.compile(r"transform\s*:", re.I), "inline transform:"),
    (re.compile(r"linear-gradient", re.I), "linear-gradient"),
    (re.compile(r'class\s*=\s*["\'][^"\']*\bd-(flex|grid|inline-flex)\b', re.I), "Bootstrap d-flex/d-grid class"),
]


def load_manifest(module_dir):
    path = os.path.join(module_dir, "__manifest__.py")
    if not os.path.isfile(path):
        raise FileNotFoundError("__manifest__.py not found")
    with open(path, encoding="utf-8") as fh:
        return ast.literal_eval(fh.read())


def scan_index_html(text):
    """Return list of (lineno, description) for forbidden layout usage."""
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        for pat, desc in FORBIDDEN_HTML:
            if pat.search(line):
                hits.append((i, desc))
    return hits


def validate(module_dir):
    errors, warnings = [], []

    try:
        manifest = load_manifest(module_dir)
    except Exception as exc:  # noqa: BLE001 - report any parse failure
        return [f"__manifest__.py: {exc}"], []
    if not isinstance(manifest, dict):
        return ["__manifest__.py did not evaluate to a dict"], []

    if not manifest.get("name"):
        errors.append("manifest: 'name' is missing or empty")

    version = manifest.get("version", "")
    if not VERSION_RE.match(str(version)):
        errors.append(f"manifest: version {version!r} must match 18.0.x.y.z or 19.0.x.y.z")

    lic = manifest.get("license")
    if lic is None:
        warnings.append("manifest: no 'license' (Odoo defaults to LGPL-3)")
    elif lic not in VALID_LICENSES:
        errors.append(f"manifest: license {lic!r} is not a valid Odoo license")

    if not any(os.path.isfile(os.path.join(module_dir, n))
               for n in ("LICENSE", "LICENSE.txt", "COPYING")):
        warnings.append("no LICENSE file at module root (Odoo reads the license text from it)")

    price = manifest.get("price")
    if price:
        cur = manifest.get("currency")
        if cur not in VALID_CURRENCIES:
            errors.append(f"manifest: price is set but currency {cur!r} is not USD or EUR")

    for key in ("data", "images"):
        for rel in manifest.get(key, []) or []:
            if not os.path.isfile(os.path.join(module_dir, rel)):
                errors.append(f"manifest: {key} file missing on disk: {rel}")

    icon = os.path.join(module_dir, "static", "description", "icon.png")
    if not os.path.isfile(icon):
        errors.append("static/description/icon.png is missing")
    else:
        with open(icon, "rb") as fh:
            if fh.read(8) != PNG_MAGIC:
                errors.append("static/description/icon.png is not a real PNG file")

    index = os.path.join(module_dir, "static", "description", "index.html")
    if not os.path.isfile(index):
        warnings.append("static/description/index.html is missing")
    else:
        with open(index, encoding="utf-8") as fh:
            for lineno, desc in scan_index_html(fh.read()):
                errors.append(f"index.html:{lineno}: forbidden layout ({desc}) — sanitizer strips it")

    return errors, warnings


def _report(module_dir, errors, warnings):
    for w in warnings:
        print(f"  warn  {w}")
    for e in errors:
        print(f"  FAIL  {e}")
    if errors:
        print(f"\n✗ {module_dir}: {len(errors)} error(s), not ready to upload")
    else:
        print(f"\n✓ {module_dir}: ready to upload"
              + (f" ({len(warnings)} warning(s))" if warnings else ""))


def _selftest():
    # version regex
    assert VERSION_RE.match("19.0.1.0.0")
    assert VERSION_RE.match("18.0.2.13.1")
    assert not VERSION_RE.match("16.0.1.0.0")   # out of scope
    assert not VERSION_RE.match("1.0")
    assert not VERSION_RE.match("19.0.1.0")     # only 4 parts

    # forbidden-html scan catches inline flex/grid, gap, gradient, d-flex class
    bad = '<div style="display:flex; gap:8px"></div>\n<div class="row d-flex"></div>'
    hits = scan_index_html(bad)
    kinds = {d for _, d in hits}
    assert "inline display:flex" in kinds
    assert "inline gap:" in kinds
    assert "Bootstrap d-flex/d-grid class" in kinds

    # a clean block layout passes
    ok = '<section style="max-width:900px;margin:0 auto"><img style="max-width:100%"></section>'
    assert scan_index_html(ok) == []
    print("selftest ok")


def main(argv):
    if "--selftest" in argv:
        _selftest()
        return 0
    if len(argv) != 2:
        print(__doc__)
        return 2
    module_dir = argv[1]
    errors, warnings = validate(module_dir)
    _report(module_dir, errors, warnings)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
