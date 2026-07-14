#!/usr/bin/env python3
"""Download an asset URL (esp. Google Drive share links) referenced in the PDF.

The non-obvious bit: a Drive "…/file/d/<ID>/view?usp=sharing" link is not a file —
it must be turned into "…/uc?export=download&id=<ID>". The file must be shared as
"anyone with the link".

Usage:
    python fetch_drive.py <url> <dst_path>
    python fetch_drive.py --selftest
"""
import re
import sys
import urllib.request

DRIVE_ID = re.compile(r"drive\.google\.com/(?:file/d/|open\?id=|uc\?[^ ]*id=)([\w-]+)")


def download_url(url):
    """Normalize a Google Drive share URL to a direct-download URL; pass others through."""
    m = DRIVE_ID.search(url)
    return f"https://drive.google.com/uc?export=download&id={m.group(1)}" if m else url


def fetch(url, dst):
    req = urllib.request.Request(download_url(url), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
    if data[:15].lstrip().lower().startswith(b"<!doctype html") or data[:6] == b"<html>":
        raise RuntimeError(f"got an HTML page, not a file — is {url} shared as 'anyone with the link'?")
    with open(dst, "wb") as fh:
        fh.write(data)
    return dst


def _selftest():
    assert download_url("https://drive.google.com/file/d/1HxqABC-de_f/view?usp=sharing") == \
        "https://drive.google.com/uc?export=download&id=1HxqABC-de_f"
    assert download_url("https://drive.google.com/open?id=XYZ123") == \
        "https://drive.google.com/uc?export=download&id=XYZ123"
    assert download_url("https://example.com/banner.png") == "https://example.com/banner.png"
    print("selftest ok")


def main(argv):
    if "--selftest" in argv:
        _selftest()
        return 0
    if len(argv) != 3:
        print(__doc__)
        return 2
    print(fetch(argv[1], argv[2]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
