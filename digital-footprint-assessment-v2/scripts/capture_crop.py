#!/usr/bin/env python3
"""
capture_crop.py — turn a browser screenshot into a publication-grade evidence
image, losslessly, and record its provenance.

The browser returns a .webp screenshot. This script crops the region that holds
the actual photograph, saves it as PNG (lossless), and writes a sidecar JSON so
image_qc.py can verify provenance and so the report can cite the real source.

It NEVER enlarges. Enlarging a thumbnail is what produces the soft, blocky
images this whole pipeline exists to prevent.

Usage
  # Tier A — the browser was navigated to the ORIGINAL image URL, so the photo
  # fills the viewport. Auto-detect the content box and crop it:
  python scripts/capture_crop.py shot.webp out/asset-01.png \
      --auto --source-url https://host/photo.jpg --native 2048x1365 --tier A

  # Tier B/C — the photo occupies part of a page render; give explicit pixels:
  python scripts/capture_crop.py shot.webp out/asset-02.png \
      --box 690,196,868,326 --source-url https://host/page --tier C

  # Downscale for layout (allowed; uses LANCZOS). Upscaling is refused.
  python scripts/capture_crop.py shot.webp out/a.png --auto --max-width 1600
"""
import argparse, json, os, sys

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow is required (PIL).", file=sys.stderr)
    sys.exit(2)


def auto_box(im, tolerance=20, margin=1):
    """Find the bounding box of the rendered image inside a browser screenshot.

    The browser letterboxes a directly-opened image against a uniform
    background — black in some themes, white in others — so the background
    colour is sampled from the corners rather than assumed. Anything differing
    from that background by more than `tolerance` is content.
    """
    g = im.convert("L")
    w, h = g.size
    px = g.load()

    corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    corners.sort()
    bg = corners[len(corners) // 2]          # median corner = background

    step = max(1, min(w, h) // 400)

    def differs(x, y):
        return abs(px[x, y] - bg) > tolerance

    ys = list(range(0, h, step))
    xs = list(range(0, w, step))
    # A row/column counts as content only when a MINIMUM FRACTION of its
    # sampled pixels differ from the background. `any()` is too permissive:
    # a one-pixel theme band or compression noise would swallow the whole
    # frame and the crop would include the letterboxing.
    min_frac = 0.04
    need_y = max(1, int(len(ys) * min_frac))
    need_x = max(1, int(len(xs) * min_frac))

    cols, rows = [], []
    for x in xs:
        if sum(1 for y in ys if differs(x, y)) >= need_y:
            cols.append(x)
    for y in ys:
        if sum(1 for x in xs if differs(x, y)) >= need_x:
            rows.append(y)
    if not cols or not rows:
        return (0, 0, w, h)
    x0 = max(0, min(cols) - margin)
    y0 = max(0, min(rows) - margin)
    x1 = min(w, max(cols) + step + margin)
    y1 = min(h, max(rows) + step + margin)
    return (x0, y0, x1, y1)


def main():
    ap = argparse.ArgumentParser(
        description="Crop a browser screenshot into a lossless evidence image.")
    ap.add_argument("screenshot")
    ap.add_argument("output", help="destination .png")
    ap.add_argument("--box", help="x0,y0,x1,y1 in screenshot pixels")
    ap.add_argument("--auto", action="store_true",
                    help="auto-detect the content box (use for a full-viewport image)")
    ap.add_argument("--source-url", default="", help="the ORIGINAL asset/page URL")
    ap.add_argument("--native", default="", help="true native size, e.g. 2048x1365")
    ap.add_argument("--tier", default="", choices=["A", "B", "C", "D", ""],
                    help="capture tier (A is best)")
    ap.add_argument("--max-width", type=int, default=0,
                    help="downscale so width <= this (LANCZOS). Never upscales.")
    ap.add_argument("--no-fit-native", action="store_true",
                    help="keep the browser's stretched size instead of "
                         "downscaling back to the true native width")
    args = ap.parse_args()

    im = Image.open(args.screenshot)
    im.load()
    im = im.convert("RGB")

    if args.box:
        try:
            x0, y0, x1, y1 = [int(v) for v in args.box.split(",")]
        except ValueError:
            print("ERROR: --box must be x0,y0,x1,y1", file=sys.stderr)
            return 2
    elif args.auto:
        x0, y0, x1, y1 = auto_box(im)
    else:
        x0, y0, x1, y1 = (0, 0, im.size[0], im.size[1])

    crop = im.crop((x0, y0, x1, y1))
    w, h = crop.size
    if w < 2 or h < 2:
        print("ERROR: crop is empty — check --box / --auto", file=sys.stderr)
        return 2

    upscaled = False
    fitted_to_native = False

    # Parse the true native size first — it caps the honest resolution.
    native_w = native_h = None
    if args.native:
        try:
            nw, nh = args.native.lower().replace("×", "x").split("x")
            native_w, native_h = int(nw), int(nh)
        except ValueError:
            native_w = native_h = None

    # If the browser stretched a small image to fill the viewport, the capture
    # has MORE pixels than the original ever had. Downscale back to native so
    # the file never claims resolution the source does not contain.
    if native_w and w > native_w and not args.no_fit_native:
        nh2 = int(round(h * native_w / float(w)))
        crop = crop.resize((native_w, max(1, nh2)), Image.LANCZOS)
        w, h = crop.size
        fitted_to_native = True

    if args.max_width and w > args.max_width:
        nh = int(round(h * args.max_width / float(w)))
        crop = crop.resize((args.max_width, nh), Image.LANCZOS)
        w, h = crop.size
    elif args.max_width and w < args.max_width:
        # explicitly refuse to enlarge
        pass

    os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
    crop.save(args.output, "PNG", optimize=True)

    sidecar = {
        "source_url": args.source_url,
        "native_w": native_w,
        "native_h": native_h,
        "capture_tier": args.tier,
        "captured_w": w,
        "captured_h": h,
        "upscaled": upscaled,
        "fitted_to_native": fitted_to_native,
        "from_screenshot": os.path.basename(args.screenshot),
        "crop_box": [x0, y0, x1, y1],
    }
    json.dump(sidecar, open(os.path.splitext(args.output)[0] + ".json", "w",
                            encoding="utf-8"), indent=1)

    print("saved %s  %dx%d  (short side %d)%s"
          % (args.output, w, h, min(w, h),
             ("  native %dx%d" % (native_w, native_h)) if native_w else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
