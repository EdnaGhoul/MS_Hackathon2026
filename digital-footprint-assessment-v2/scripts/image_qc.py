#!/usr/bin/env python3
"""image_qc.py — manifest-driven quality gate for captured photographs.

v1 asked the agent how many images to expect (`--expect`), which meant the
expectation could be lowered to match whatever survived. v2 reads assets.json:
the manifest is the expectation, and the gate reconciles files against it in
both directions.

FAILS on: a verified asset with no file · a file on disk with no manifest row ·
a sidecar recording an upscale · any asset left in a non-terminal state ·
an unreadable image. Sharpness stays ADVISORY — it decides how WIDE a picture
is placed, never whether it ships. The computed width is written back to the
manifest as `placement_mm` (80 mm, or the image's own ceiling when smaller).

  python scripts/image_qc.py --run <run-dir>                # every subject
  python scripts/image_qc.py --run <run-dir> --subject <slug> [--json]
"""
import argparse, json, os, sys
import _dfa

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow is required (PIL).", file=sys.stderr)
    sys.exit(2)

EXTS = {".png", ".jpg", ".jpeg", ".webp"}
PLACEMENT_DPI = 200
UNIFORM_MM = 80.0


def laplacian_variance(im):
    """Sharpness proxy: variance of the Laplacian on the luma plane (pure Pillow)."""
    g = im.convert("L")
    w, h = g.size
    if w < 3 or h < 3:
        return 0.0
    try:
        px = list(g.get_flattened_data())   # Pillow >= 11
    except AttributeError:
        px = list(g.getdata())
    stride = max(1, int(((w * h) / 40000.0) ** 0.5))
    vals = []
    for y in range(1, h - 1, stride):
        for x in range(1, w - 1, stride):
            vals.append(float(px[y * w + x - 1] + px[y * w + x + 1] + px[(y - 1) * w + x]
                              + px[(y + 1) * w + x] - 4 * px[y * w + x]))
    if not vals:
        return 0.0
    mean = sum(vals) / len(vals)
    return sum((v - mean) ** 2 for v in vals) / len(vals)


def qc_subject(run_dir, slug):
    man = _dfa.load_manifest(run_dir, slug)
    sdir = os.path.join(run_dir, slug)
    rec = {"subject": slug, "images": [], "issues": [], "warnings": []}

    stuck = [a["id"] for a in man.get("assets", [])
             if a.get("state") in {"candidate", "queued", "capturing", "captured"}]
    if stuck:
        rec["issues"].append("asset(s) left in a non-terminal state: %s — run plan_capture.py "
                             "--finalize before rendering" % ", ".join(stuck))

    claimed = set()
    for a in _dfa.shown_assets(man):
        f = a.get("file") or ""
        path = os.path.join(sdir, f)
        claimed.add(os.path.normpath(path))
        if not f or not os.path.exists(path):
            rec["issues"].append("%s is %s but its file is missing (%s)" % (a["id"], a["state"], f or "none"))
            continue
        try:
            im = Image.open(path)
            im.load()
        except Exception as exc:
            rec["issues"].append("%s: unreadable image — %s" % (a["id"], exc))
            continue
        w, h = im.size
        sharp = round(laplacian_variance(im), 1)
        ceiling = round(max(w, h) / float(PLACEMENT_DPI) * 25.4, 1)
        place = min(UNIFORM_MM, ceiling)
        a["placement_mm"] = place

        sc = {}
        scp = os.path.join(sdir, a.get("sidecar") or (os.path.splitext(f)[0] + ".json"))
        if os.path.exists(scp):
            try:
                sc = json.load(open(scp, encoding="utf-8"))
            except Exception:
                sc = {}
        if sc.get("upscaled"):
            rec["issues"].append("%s: the sidecar records an UPSCALE — an evidence image is never enlarged"
                                 % a["id"])
        if not sc:
            rec["warnings"].append("%s: no sidecar — source URL, native size and tier unrecorded" % a["id"])
        if sharp < 60:
            rec["warnings"].append("%s: soft capture (sharpness %.0f) — placed at %.0f mm, which hides it"
                                   % (a["id"], sharp, place))
        rec["images"].append({"asset": a["id"], "file": f, "w": w, "h": h,
                              "sharpness": sharp, "placement_mm": place})

    # The other direction: a file nobody claims means a capture was lost from the manifest.
    imgdir = os.path.join(sdir, "img")
    if os.path.isdir(imgdir):
        for name in sorted(os.listdir(imgdir)):
            if os.path.splitext(name)[1].lower() in EXTS:
                p = os.path.normpath(os.path.join(imgdir, name))
                if p not in claimed:
                    owner = next((a for a in man["assets"]
                                  if os.path.normpath(os.path.join(sdir, a.get("file") or "")) == p), None)
                    if owner is None:
                        rec["issues"].append("%s exists on disk with no manifest row — a capture that no "
                                             "document will ever show" % os.path.join("img", name))

    _dfa.save_manifest(run_dir, slug, man)
    rec["status"] = "FAIL" if rec["issues"] else ("WARN" if rec["warnings"] else "PASS")
    rec["summary"] = man["summary"]
    return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--subject")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    subjects = ([{"slug": args.subject}] if args.subject
                else _dfa.read_json(os.path.join(args.run, "subjects.json")))
    recs = [qc_subject(args.run, s["slug"]) for s in subjects
            if os.path.exists(_dfa.manifest_path(args.run, s["slug"]))]
    failed = [r for r in recs if r["status"] == "FAIL"]

    if args.json:
        print(json.dumps({"subjects": recs, "failed": len(failed)}, indent=1))
    else:
        for r in recs:
            s = r["summary"]
            print("%-6s %-24s %d shown of %d distinct found"
                  % (r["status"], r["subject"], s["shown"], s["found_distinct"]))
            for i in r["images"]:
                print("         %-9s %5dx%-5d sharp=%-7.0f place=%.0fmm"
                      % (i["asset"], i["w"], i["h"], i["sharpness"], i["placement_mm"]))
            for i in r["issues"]:
                print("         FAIL  %s" % i)
            for wn in r["warnings"]:
                print("         warn  %s" % wn)
        print("\n%d subject(s), %d failed" % (len(recs), len(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
