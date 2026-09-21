#!/usr/bin/env python3
"""render_pages.py — rasterise the Word report so its pages can be LOOKED AT.

The DOCX gate proves the parts are there; only a rendered page proves the layout
works. Renders to qa/page-NN.png for the mandatory visual QA loop.

  python scripts/render_pages.py --run <run-dir> --subject <slug> [--dpi 110]
"""
import argparse, glob, os, shutil, subprocess, sys

SOFFICE = shutil.which("soffice") or "/usr/local/cowork-bin/soffice"
PDFTOPPM = shutil.which("pdftoppm") or "/usr/local/cowork-bin/pdftoppm"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--subject", required=True)
    ap.add_argument("--dpi", type=int, default=110)
    args = ap.parse_args()

    sdir = os.path.join(args.run, args.subject)
    docx = os.path.join(sdir, "build", "%s-digital-footprint.docx" % args.subject)
    qa = os.path.join(sdir, "qa")
    if not os.path.exists(docx):
        print("no Word file at %s — render it first" % docx, file=sys.stderr)
        return 2
    os.makedirs(qa, exist_ok=True)
    for old in glob.glob(os.path.join(qa, "page-*.png")):
        os.remove(old)
    subprocess.run([SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", qa, docx],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pdf = os.path.join(qa, os.path.basename(docx).replace(".docx", ".pdf"))
    subprocess.run([PDFTOPPM, "-png", "-r", str(args.dpi), pdf, os.path.join(qa, "page")], check=True)
    pages = sorted(glob.glob(os.path.join(qa, "page-*.png")))
    print("%d page(s) rendered to %s" % (len(pages), qa))
    for p in pages:
        print("  %s" % p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
