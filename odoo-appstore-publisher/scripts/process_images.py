#!/usr/bin/env python3
"""Normalize images for an Odoo App Store listing (Pillow).

Usage:
    python process_images.py icon   <src>  <dst_dir>            # -> <dst_dir>/icon.png (140x140)
    python process_images.py image  <src>  <dst>  [max_width]   # normalize + downscale, keep aspect
    python process_images.py --selftest

App Store rules enforced here: icon must be a 140x140 PNG; listing images must be
PNG/GIF/JPEG and no wider than ~1920px (Odoo compresses beyond that).
"""
import os
import sys

from PIL import Image

ICON_SIZE = (140, 140)
MAX_WIDTH = 1920
ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".gif"}


def make_icon(src, dst_dir):
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, "icon.png")
    with Image.open(src) as im:
        im = im.convert("RGBA")
        im.thumbnail(ICON_SIZE, Image.LANCZOS)  # fit inside 140x140, keep aspect (no squish)
        canvas = Image.new("RGBA", ICON_SIZE, (0, 0, 0, 0))
        canvas.paste(im, ((ICON_SIZE[0] - im.width) // 2, (ICON_SIZE[1] - im.height) // 2), im)
        canvas.save(dst, "PNG")
    return dst


def normalize(src, dst, max_width=MAX_WIDTH):
    ext = os.path.splitext(dst)[1].lower()
    if ext not in ALLOWED_EXT:
        raise ValueError(f"{dst}: extension {ext!r} not allowed (use PNG/JPG/GIF)")
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    with Image.open(src) as im:
        if im.width > max_width:
            h = round(im.height * max_width / im.width)
            im = im.resize((max_width, h), Image.LANCZOS)
        if ext in (".jpg", ".jpeg") and im.mode in ("RGBA", "P"):
            im = im.convert("RGB")  # JPEG has no alpha
        im.save(dst)
    return dst


def _selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        big = os.path.join(d, "big.png")
        Image.new("RGB", (4000, 2000), "navy").save(big)

        icon = make_icon(big, d)
        with Image.open(icon) as im:
            assert im.size == ICON_SIZE, im.size

        out = os.path.join(d, "banner.jpg")
        normalize(big, out)
        with Image.open(out) as im:
            assert im.width == MAX_WIDTH, im.width
            assert im.height == 960, im.height  # aspect preserved

        try:
            normalize(big, os.path.join(d, "x.svg"))
            assert False, "should reject svg"
        except ValueError:
            pass
    print("selftest ok")


def main(argv):
    if "--selftest" in argv:
        _selftest()
        return 0
    if len(argv) >= 2 and argv[1] == "icon" and len(argv) == 4:
        print(make_icon(argv[2], argv[3]))
        return 0
    if len(argv) >= 2 and argv[1] == "image" and len(argv) in (4, 5):
        mw = int(argv[4]) if len(argv) == 5 else MAX_WIDTH
        print(normalize(argv[2], argv[3], mw))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
