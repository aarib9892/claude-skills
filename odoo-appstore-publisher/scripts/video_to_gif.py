#!/usr/bin/env python3
"""Convert a marketing video to an optimized animated GIF (ffmpeg, two-pass palette).

Odoo's App Store cannot embed video, so motion is shown as an animated GIF <img>.

Usage:
    python video_to_gif.py <input_video> <output.gif> [--fps 12] [--width 720]
    python video_to_gif.py --selftest

Requires ffmpeg on PATH (`sudo apt install ffmpeg`).
"""
import os
import shutil
import subprocess
import sys
import tempfile


def palette_cmd(src, palette, fps, width):
    vf = f"fps={fps},scale={width}:-1:flags=lanczos,palettegen"
    return ["ffmpeg", "-y", "-i", src, "-vf", vf, palette]


def gif_cmd(src, palette, dst, fps, width):
    lavfi = f"fps={fps},scale={width}:-1:flags=lanczos[x];[x][1:v]paletteuse"
    return ["ffmpeg", "-y", "-i", src, "-i", palette, "-lavfi", lavfi, dst]


def convert(src, dst, fps=12, width=720):
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found on PATH. Install it: sudo apt install ffmpeg")
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        palette = os.path.join(d, "palette.png")
        subprocess.run(palette_cmd(src, palette, fps, width), check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        subprocess.run(gif_cmd(src, palette, dst, fps, width), check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return dst


def _selftest():
    # verify command construction without needing ffmpeg or a real video
    assert palette_cmd("in.mp4", "p.png", 12, 720)[:3] == ["ffmpeg", "-y", "-i"]
    assert "palettegen" in palette_cmd("in.mp4", "p.png", 12, 720)[-2]
    g = gif_cmd("in.mp4", "p.png", "out.gif", 12, 720)
    assert g[-1] == "out.gif" and "paletteuse" in g[-2]
    assert "fps=15" in palette_cmd("in.mp4", "p.png", 15, 640)[-2]
    print("selftest ok")


def main(argv):
    if "--selftest" in argv:
        _selftest()
        return 0
    args = [a for a in argv[1:] if not a.startswith("--")]
    opts = {argv[i]: argv[i + 1] for i in range(len(argv)) if argv[i].startswith("--")}
    if len(args) != 2:
        print(__doc__)
        return 2
    try:
        out = convert(args[0], args[1], int(opts.get("--fps", 12)), int(opts.get("--width", 720)))
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        stderr = getattr(exc, "stderr", b"")
        msg = stderr.decode(errors="replace") if isinstance(stderr, bytes) else ""
        print(f"video_to_gif failed: {exc}\n{msg}", file=sys.stderr)
        return 1
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
