#!/usr/bin/env python3
"""
image_qc.py — quality gate for captured evidence images.

Every image placed in a reputation / digital-footprint report must pass this
gate. It measures real resolution and real sharpness and FAILS anything that
would print badly, so a poor capture gets re-captured at a better tier instead
of silently shipping.

Usage
  python scripts/image_qc.py <dir-or-file> [...]            # check
  python scripts/image_qc.py <dir> --json                   # machine output
  python scripts/image_qc.py <dir> --min-short 500          # override floor

Exit codes: 0 = all PASS/WARN, 1 = at least one FAIL.

Thresholds (defaults)
  sharpness   >= 60       FAIL below   — a BLURRY image is unusable at any size
  upscaled                FAIL         — enlarging invents detail that isn't there

  Resolution does NOT fail. It CAPS DISPLAY SIZE. A small, sharp image placed
  small looks excellent; the same image stretched looks terrible. So the gate
  computes `max_display_mm` (at PLACEMENT_DPI) and the document builder must
  place the image at or below that width. Too-small-to-be-useful is a WARN.
  sharpness   >= 60       FAIL below   (variance of Laplacian on the luma plane)
  sharpness   >= 150      WARN below

A sidecar `<image>.json` written by the capture step may carry:
  {"source_url": "...", "native_w": 2048, "native_h": 1365,
   "capture_tier": "A", "upscaled": false}
When present, native_w/native_h are compared with the captured size, so a
capture that threw away most of the original's detail is flagged.
"""
import argparse, json, os, sys

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow is required (PIL).", file=sys.stderr)
    sys.exit(2)

EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}


def laplacian_variance(im):
    """Sharpness proxy: variance of the Laplacian over the luma plane.

    Pure-Pillow so the script needs no numpy/opencv.
    """
    g = im.convert("L")
    w, h = g.size
    if w < 3 or h < 3:
        return 0.0
    try:
        px = list(g.get_flattened_data())     # Pillow >= 11
    except AttributeError:
        px = list(g.getdata())                # older Pillow

    def at(x, y):
        return px[y * w + x]

    vals = []
    stride = max(1, int(((w * h) / 40000.0) ** 0.5))  # keep ~40k samples
    for y in range(1, h - 1, stride):
        for x in range(1, w - 1, stride):
            vals.append(float(at(x - 1, y) + at(x + 1, y) + at(x, y - 1)
                              + at(x, y + 1) - 4 * at(x, y)))
    if not vals:
        return 0.0
    mean = sum(vals) / len(vals)
    return sum((v - mean) ** 2 for v in vals) / len(vals)


def sidecar_for(path):
    cand = os.path.splitext(path)[0] + ".json"
    if os.path.exists(cand):
        try:
            return json.load(open(cand, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def check(path, dpi, min_useful_mm, min_sharp, warn_sharp):
    rec = {"file": os.path.basename(path), "path": path,
           "issues": [], "warnings": [], "status": "PASS"}
    try:
        im = Image.open(path)
        im.load()
    except Exception as exc:
        rec["status"] = "FAIL"
        rec["issues"].append("unreadable image: %s" % exc)
        return rec

    w, h = im.size
    short = min(w, h)
    rec.update(width=w, height=h, short_side=short,
               megapixels=round(w * h / 1e6, 3),
               format=(im.format or "?"), bytes=os.path.getsize(path))

    sharp = laplacian_variance(im)
    rec["sharpness"] = round(sharp, 1)

    long = max(w, h)
    rec["long_side"] = long

    # Resolution caps DISPLAY SIZE; it is not a pass/fail on its own.
    max_mm = round(long / float(dpi) * 25.4, 1)
    rec["placement_dpi"] = dpi
    rec["max_display_mm"] = max_mm
    rec["max_display_in"] = round(long / float(dpi), 2)
    if max_mm < min_useful_mm:
        rec["warnings"].append(
            "can only be placed %.0fmm wide at %ddpi — usable as an inline "
            "thumbnail only; re-capture at a higher tier if it needs to be a "
            "feature image" % (max_mm, dpi))

    if sharp < min_sharp:
        rec["issues"].append(
            "sharpness %.1f is below the %.0f floor — the image is blurred, or was "
            "enlarged from a thumbnail" % (sharp, min_sharp))
    elif sharp < warn_sharp:
        rec["warnings"].append("sharpness %.1f is soft (target >= %.0f)"
                               % (sharp, warn_sharp))

    if (im.format or "").upper() in {"JPEG", "WEBP"}:
        rec["warnings"].append(
            "%s is lossy — save evidence crops as PNG to avoid recompression artefacts"
            % im.format)

    sc = sidecar_for(path)
    if sc:
        rec["source_url"] = sc.get("source_url", "")
        rec["capture_tier"] = sc.get("capture_tier", "")
        nw, nh = sc.get("native_w"), sc.get("native_h")
        if sc.get("upscaled"):
            rec["issues"].append(
                "sidecar records an UPSCALE — never enlarge an evidence image")
        if isinstance(nw, int) and isinstance(nh, int) and nw > 0 and nh > 0:
            rec["native"] = "%dx%d" % (nw, nh)
            frac = (w * h) / float(nw * nh)
            rec["captured_fraction_of_native"] = round(frac, 3)
            if frac < 0.10:
                rec["warnings"].append(
                    "capture holds only %.0f%% of the original's pixels (%dx%d "
                    "available) — the original is far larger than the capture"
                    % (frac * 100, nw, nh))
        if sc.get("capture_tier") in {"C", "D"}:
            rec["warnings"].append(
                "capture tier %s — tier A (navigate to the original image URL) "
                "yields far more detail" % sc.get("capture_tier"))
        if not sc.get("source_url"):
            rec["warnings"].append(
                "sidecar has no source_url — provenance cannot be cited")
    else:
        rec["warnings"].append(
            "no sidecar JSON — source URL, native size and capture tier unrecorded")

    rec["status"] = "FAIL" if rec["issues"] else ("WARN" if rec["warnings"] else "PASS")
    return rec


def collect(targets):
    out = []
    for t in targets:
        if os.path.isdir(t):
            for root, _dirs, files in os.walk(t):
                for f in sorted(files):
                    if os.path.splitext(f)[1].lower() in EXTS:
                        out.append(os.path.join(root, f))
        elif os.path.isfile(t):
            out.append(t)
    return out


def coverage(targets, files, expect, manifest_path):
    """Compare captured assets against the number of photographs documented.

    The gate otherwise measures only the images it can see, so a report that
    documents five photographs and captures one passes silently. `--expect`
    (one subject) and `--expect-manifest` (a roster) close that hole.
    """
    if not expect and not manifest_path:
        return []

    rows = []
    if manifest_path:
        try:
            want = json.load(open(manifest_path, encoding="utf-8"))
        except Exception as exc:
            return [{"scope": manifest_path, "expected": None, "captured": None,
                     "status": "FAIL",
                     "message": "expectation manifest unreadable: %s" % exc}]
        # count captured images per immediate subdirectory (one per subject)
        got = {}
        for f in files:
            slug = os.path.basename(os.path.dirname(f))
            got[slug] = got.get(slug, 0) + 1
        for slug in sorted(set(list(want.keys()) + list(got.keys()))):
            n_want = int(want.get(slug, 0))
            n_got = got.get(slug, 0)
            rows.append(_cov_row(slug, n_want, n_got))
    else:
        rows.append(_cov_row(", ".join(targets), int(expect), len(files)))
    return rows


def _cov_row(scope, n_want, n_got):
    rec = {"scope": scope, "expected": n_want, "captured": n_got, "status": "PASS",
           "message": "%d of %d documented photograph(s) captured" % (n_got, n_want)}
    if n_want and n_got < n_want:
        rec["status"] = "FAIL"
        rec["message"] = (
            "coverage %d/%d — %d documented photograph(s) have no captured asset; "
            "capture them, or give each uncaptured row a stated reason"
            % (n_got, n_want, n_want - n_got))
    elif n_want == 0 and n_got:
        rec["status"] = "WARN"
        rec["message"] = ("%d image(s) captured but none documented for this subject — "
                          "every published image needs an inventory row" % n_got)
    return rec


def main():
    ap = argparse.ArgumentParser(
        description="Quality gate for captured evidence images.")
    ap.add_argument("targets", nargs="+", help="image files or directories")
    ap.add_argument("--expect", type=int, default=0,
                    help="number of photographs the inventory documents; "
                         "FAILS when fewer were captured")
    ap.add_argument("--expect-manifest", default=None,
                    help='JSON {"<subject-slug>": <documented count>} checked per '
                         "subdirectory — use on a roster so one thin subject cannot "
                         "hide behind another's gallery")
    ap.add_argument("--dpi", type=int, default=200,
                    help="placement density used to compute max display width")
    ap.add_argument("--min-useful-mm", type=float, default=35.0,
                    help="WARN when the image can only be placed narrower than this")
    ap.add_argument("--min-sharp", type=float, default=60.0)
    ap.add_argument("--warn-sharp", type=float, default=150.0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    files = collect(args.targets)
    if not files:
        print("No images found in: %s" % ", ".join(args.targets))
        return 0

    recs = [check(f, args.dpi, args.min_useful_mm, args.min_sharp, args.warn_sharp)
            for f in files]
    fails = [r for r in recs if r["status"] == "FAIL"]
    warns = [r for r in recs if r["status"] == "WARN"]

    cov = coverage(args.targets, files, args.expect, args.expect_manifest)
    cov_fails = [c for c in cov if c["status"] == "FAIL"]

    if args.json:
        print(json.dumps({"checked": len(recs), "failed": len(fails),
                          "warned": len(warns), "results": recs,
                          "coverage": cov,
                          "coverage_failed": len(cov_fails)}, indent=1))
        return 1 if (fails or cov_fails) else 0

    print("Image QC — %d image(s): %d PASS, %d WARN, %d FAIL"
          % (len(recs), len(recs) - len(fails) - len(warns), len(warns), len(fails)))
    print("-" * 74)
    for r in recs:
        if "width" in r:
            print("%-6s %-28s %5dx%-5d sharp=%-8.1f place<=%-6smm %s"
                  % (r["status"], r["file"][:28], r["width"], r["height"],
                     r["sharpness"], r.get("max_display_mm", "?"),
                     r.get("native", "")))
        else:
            print("%-6s %-30s (unreadable)" % (r["status"], r["file"][:30]))
        for i in r["issues"]:
            print("         FAIL  %s" % i)
        for wn in r["warnings"]:
            print("         warn  %s" % wn)
    if fails:
        print("\n%d image(s) FAILED on sharpness or upscaling — those cannot be fixed "
              "by resizing. Re-capture them." % len(fails))

    if cov:
        print("\nCoverage — captured assets vs photographs documented")
        print("-" * 74)
        for c in cov:
            print("%-6s %-28s %s" % (c["status"], str(c["scope"])[:28], c["message"]))
        if cov_fails:
            print("\n%d subject(s) SHORT of the documented photograph count. Section 7 "
                  "must SHOW what it documents — capture the missing assets, or give "
                  "each uncaptured row a stated reason." % len(cov_fails))

    print("\nPlace each image at or below its 'place<=' width. Downscaling to fit is "
          "always fine; enlarging beyond it is never fine.")
    return 1 if (fails or cov_fails) else 0


if __name__ == "__main__":
    sys.exit(main())
