#!/usr/bin/env python3
"""Extract text and embedded images from the PM's asset PDF.

Prefers PyMuPDF (text + images). Falls back to PyPDF2 (text only, warns that images
must be supplied separately).

Usage:
    python extract_pdf.py <input.pdf> <out_dir>   # writes text.txt + img_001.ext ...
    python extract_pdf.py --selftest

Output layout:
    <out_dir>/text.txt        all page text, page-separated
    <out_dir>/img_001.png ..  every embedded image, in source order (native format)
"""
import os
import sys


def img_name(index, ext):
    return f"img_{index:03d}.{ext.lstrip('.')}"


def _extract_pymupdf(pdf, out_dir):
    import fitz  # PyMuPDF

    doc = fitz.open(pdf)
    texts, links, n = [], [], 0
    seen = set()
    for pno, page in enumerate(doc, 1):
        texts.append(f"----- page {pno} -----\n{page.get_text()}")
        for img in page.get_images(full=True):
            xref = img[0]
            if xref in seen:
                continue
            seen.add(xref)
            info = doc.extract_image(xref)
            n += 1
            path = os.path.join(out_dir, img_name(n, info["ext"]))
            with open(path, "wb") as fh:
                fh.write(info["image"])
        # hyperlinks — assets (banner, screenshots) are often linked, not embedded
        for l in page.get_links():
            uri = l.get("uri")
            if not uri:
                continue
            label = page.get_textbox(fitz.Rect(l["from"])).strip().replace("\n", " ") if l.get("from") else ""
            links.append((pno, uri, label))
    _write_text(out_dir, "\n\n".join(texts))
    if links:
        with open(os.path.join(out_dir, "links.txt"), "w", encoding="utf-8") as fh:
            for pno, uri, label in links:
                fh.write(f"p{pno}\t{uri}\t{label}\n")
        print(f"  {len(links)} hyperlink(s) -> links.txt (download linked assets before building)")
    return n, "PyMuPDF"


def _extract_pypdf2(pdf, out_dir):
    from PyPDF2 import PdfReader

    reader = PdfReader(pdf)
    texts = [f"----- page {i} -----\n{p.extract_text() or ''}"
             for i, p in enumerate(reader.pages, 1)]
    _write_text(out_dir, "\n\n".join(texts))
    print("WARNING: PyMuPDF not installed — extracted text only, no images. "
          "Install it (`pip install PyMuPDF`) or supply the logo/banner/screenshots separately.",
          file=sys.stderr)
    return 0, "PyPDF2"


def _write_text(out_dir, text):
    with open(os.path.join(out_dir, "text.txt"), "w", encoding="utf-8") as fh:
        fh.write(text)


def extract(pdf, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    try:
        import fitz  # noqa: F401
        return _extract_pymupdf(pdf, out_dir)
    except ImportError:
        return _extract_pypdf2(pdf, out_dir)


def _selftest():
    assert img_name(1, "png") == "img_001.png"
    assert img_name(42, ".jpeg") == "img_042.jpeg"
    assert img_name(7, "gif") == "img_007.gif"
    print("selftest ok")


def main(argv):
    if "--selftest" in argv:
        _selftest()
        return 0
    if len(argv) != 3:
        print(__doc__)
        return 2
    n, backend = extract(argv[1], argv[2])
    print(f"{backend}: wrote text.txt and {n} image(s) to {argv[2]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
