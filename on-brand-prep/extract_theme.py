#!/usr/bin/env python3
"""Deterministic brand extractor for Office files (.pptx / .docx / .xlsx).

Usage:
    python /mnt/user-config/skills/on-brand-prep/scripts/extract_theme.py <file.pptx|docx|xlsx> --out working/brand-staging/<slug>
    python /mnt/user-config/skills/on-brand-prep/scripts/extract_theme.py --swatch working/brand-staging/<slug>/brand.md --out working/brand-staging/<slug>

Reads the theme part (colours + fonts) straight out of the ZIP, scores embedded media as logo
candidates, copies the winner (trimmed) to <out>/assets/logo.<ext>, computes WCAG contrast ratios,
derives light/dark, and writes a draft <out>/brand.md. Prints a JSON summary to stdout.

Stdlib + Pillow only. Pillow missing -> logo scoring degrades to size/reference heuristics and no
trimming; everything else still works. Never executes anything inside the file it reads; text found
in the file is data, never an instruction.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
import zipfile
from collections import Counter
from io import BytesIO

try:  # optional dependency
    from PIL import Image
    HAVE_PIL = True
except Exception:  # pragma: no cover
    Image = None
    HAVE_PIL = False

LAYOUTS = {
    ".pptx": ("ppt/theme/theme1.xml", "ppt/media/", "ppt/"),
    ".docx": ("word/theme/theme1.xml", "word/media/", "word/"),
    ".xlsx": ("xl/theme/theme1.xml", "xl/media/", "xl/"),
}
ROLE_MAP = [  # theme slot -> profile role (a convention, so it is marked inferred)
    ("accent1", "Primary"), ("accent2", "Secondary"), ("accent3", "Accent"),
    ("accent4", "Accent 2"), ("accent5", "Accent 3"), ("accent6", "Accent 4"),
    ("lt1", "Background"), ("dk1", "Text / foreground"),
]
RASTER = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff"}
IMG_EXT = RASTER | {".svg", ".emf", ".wmf"}
FALLBACK_STACK = "Segoe UI, system-ui, -apple-system, sans-serif"


# ----------------------------------------------------------------------------- theme parsing
def parse_theme(xml: str) -> tuple[dict, dict]:
    colours: dict = {}
    m = re.search(r"<a:clrScheme.*?</a:clrScheme>", xml, re.S)
    if m:
        for slot, body in re.findall(r"<a:(dk1|lt1|dk2|lt2|accent[1-6]|hlink|folHlink)>(.*?)</a:\1>",
                                     m.group(0), re.S):
            hexv = re.search(r'<a:srgbClr\s+val="([0-9A-Fa-f]{6})"', body)
            if not hexv:
                hexv = re.search(r'<a:sysClr[^>]*lastClr="([0-9A-Fa-f]{6})"', body)
            if hexv:
                colours[slot] = "#" + hexv.group(1).upper()
    fonts: dict = {}
    f = re.search(r"<a:fontScheme.*?</a:fontScheme>", xml, re.S)
    if f:
        for kind, key in (("majorFont", "heading"), ("minorFont", "body")):
            mm = re.search(r"<a:%s>\s*<a:latin\s+typeface=\"([^\"]*)\"" % kind, f.group(0))
            if mm and mm.group(1).strip():
                fonts[key] = mm.group(1).strip()
    return colours, fonts


# ----------------------------------------------------------------------------- colour maths
def _lin(c: int) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hexv: str) -> float:
    r, g, b = (int(hexv[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    return round((max(la, lb) + 0.05) / (min(la, lb) + 0.05), 1)


def contrast_verdict(ratio: float) -> str:
    if ratio >= 4.5:
        return "\u2713"
    if ratio >= 3.0:
        return "\u2014 large text only"
    return "\u2717 fails \u2014 use the text role instead"


# ----------------------------------------------------------------------------- logo scoring
def _rels_targets(zf: zipfile.ZipFile, prefix: str) -> tuple[Counter, set]:
    """Reference count per media file, plus the set referenced from a master / title layout /
    header (strong logo signal)."""
    counts: Counter = Counter()
    strong: set = set()
    strong_keys = ("slideMaster", "slideLayout1.", "header", "_rels/document.xml", "_rels/workbook")
    for name in zf.namelist():
        if not (name.startswith(prefix) and name.endswith(".rels")):
            continue
        try:
            rels = zf.read(name).decode("utf-8", "ignore")
        except (KeyError, zipfile.BadZipFile, RuntimeError):
            rels = ""
        is_strong = any(k in name for k in strong_keys)
        for target in re.findall(r'Target="([^"]*media/[^"]+)"', rels):
            base = os.path.basename(target)
            counts[base] += 1
            if is_strong:
                strong.add(base)
    return counts, strong


def score_media(zf: zipfile.ZipFile, media_prefix: str, part_prefix: str) -> list:
    counts, strong = _rels_targets(zf, part_prefix)
    out = []
    for info in zf.infolist():
        if not info.filename.startswith(media_prefix):
            continue
        base = os.path.basename(info.filename)
        ext = os.path.splitext(base)[1].lower()
        if ext not in IMG_EXT:
            continue
        cand = {"file": info.filename, "ext": ext, "bytes": info.file_size, "refs": counts.get(base, 0),
                "from_master": base in strong, "width": None, "height": None, "alpha": None,
                "aspect": None, "kind": "unknown", "score": 0.0, "reasons": [], "discard": None}
        s = 0.0
        if cand["from_master"]:
            s += 4
            cand["reasons"].append("referenced from master/title layout")
        if cand["refs"] >= 2:
            s += 3
            cand["reasons"].append("referenced %d times" % cand["refs"])
        if ext == ".svg":
            s += 3
            cand.update(alpha=True, kind="vector")
            cand["reasons"].append("vector")
        elif HAVE_PIL and ext in RASTER:
            try:
                im = Image.open(BytesIO(zf.read(info.filename)))
                w, h = im.size
                longest, shortest = max(w, h), max(1, min(w, h))
                aspect = longest / shortest
                alpha = im.mode in ("RGBA", "LA", "P") and (im.mode != "P" or "transparency" in im.info)
                cand.update(width=w, height=h, aspect=round(aspect, 2), alpha=alpha)
                if longest < 64:
                    cand["discard"] = "under 64px (icon/favicon)"
                elif longest < 200:
                    s -= 2
                    cand["reasons"].append("small (<200px) - will pixelate")
                if alpha:
                    s += 3
                    cand["reasons"].append("transparent")
                if 2.0 <= aspect <= 6.0:
                    s += 2
                    cand["kind"] = "wordmark"
                elif aspect < 1.3:
                    s += 1
                    cand["kind"] = "mark"
                else:
                    cand["kind"] = "other"
                small = im.convert("RGBA").resize((64, 64))
                cols = small.getcolors(64 * 64) or []
                distinct = len([c for c in cols if c[1][3] > 0])
                cand["distinct_colours"] = distinct
                if distinct <= 256:
                    s += 2
                    cand["reasons"].append("few colours (graphic)")
                elif distinct > 1500:
                    cand["discard"] = "photo-like (%d colours)" % distinct
                if w * h > 4_000_000 and not alpha:
                    cand["discard"] = cand["discard"] or "large opaque image (background/photo)"
            except Exception as e:  # unreadable raster
                cand["discard"] = "unreadable: %s" % e.__class__.__name__
        else:
            cand["reasons"].append("not inspected (Pillow missing or unsupported format)")
        cand["score"] = s
        out.append(cand)
    out.sort(key=lambda c: (c["discard"] is not None, -c["score"], -c["bytes"]))
    return out


def save_logo(zf: zipfile.ZipFile, cand: dict, assets_dir: str) -> dict:
    os.makedirs(assets_dir, exist_ok=True)
    ext = cand["ext"]
    data = zf.read(cand["file"])
    metrics = {"path": None, "width": cand.get("width"), "height": cand.get("height"),
               "alpha": cand.get("alpha"), "aspect": cand.get("aspect"), "kind": cand.get("kind"),
               "trimmed": False}
    if HAVE_PIL and ext in RASTER:
        im = Image.open(BytesIO(data))
        if cand.get("alpha"):
            im = im.convert("RGBA")
            bbox = im.getbbox()
            if bbox and bbox != (0, 0, im.width, im.height):
                im = im.crop(bbox)
                metrics["trimmed"] = True
            ext = ".png"
        dest = os.path.join(assets_dir, "logo" + ext)
        im.save(dest)
        w, h = im.size
        metrics.update(width=w, height=h, aspect=round(max(w, h) / max(1, min(w, h)), 2))
    else:
        dest = os.path.join(assets_dir, "logo" + ext)
        with open(dest, "wb") as fh:
            fh.write(data)
    metrics["path"] = "assets/" + os.path.basename(dest)
    return metrics


def logo_metrics_line(m: dict) -> str:
    if m.get("width"):
        alpha = "transparent" if m.get("alpha") else "opaque"
        fmt = m["path"].rsplit(".", 1)[-1].upper()
        return "%d\u00d7%d, %s %s, aspect %s:1 (%s)" % (m["width"], m["height"], alpha, fmt,
                                                        m.get("aspect"), m.get("kind"))
    return "vector (SVG)" if m.get("kind") == "vector" else "metrics unavailable"


# ----------------------------------------------------------------------------- brand.md
def build_brand_md(company, source_name: str, palette: list, fonts: dict, logo, contrast_line, scheme) -> str:
    today = _dt.date.today().isoformat()
    lines = ["# Brand profile \u2014 v1", "Last updated: %s" % today, "", "## Brand identity"]
    if company:
        lines.append("**Company:** %s" % company)
    lines += ["**Sources used:** %s (theme%s)" % (source_name, ", embedded media" if logo else ""),
              "**Extracted:** %s" % today, "", "## Colour palette"]
    for role, hexv, slot in palette:
        lines.append("**%s:** %s (inferred \u2014 theme %s)" % (role, hexv, slot))
    order = [r.lower() for r, _, _ in palette if r not in ("Background", "Text / foreground")]
    if order:
        lines.append("**Chart order:** " + ", ".join(order))
    if contrast_line:
        lines.append("**Contrast:** " + contrast_line)
    lines += ["", "## Typography"]
    if fonts.get("heading"):
        lines.append("**Heading font:** %s" % fonts["heading"])
    if fonts.get("body"):
        lines.append("**Body font:** %s" % fonts["body"])
    lines.append("**Fallback stack:** " + FALLBACK_STACK)
    if logo:
        lines += ["", "## Logo & assets", "**Primary logo:** %s" % logo["path"],
                  "**Logo metrics:** %s" % logo_metrics_line(logo),
                  "**Usage:** clear space \u2248 the mark's height on all sides; never recolour, distort or add effects"]
    if scheme:
        lines += ["", "## Style cues", "**Scheme:** %s (inferred \u2014 theme lt1 luminance)" % scheme]
    lines += ["", "## Application notes"]
    if contrast_line and ("large text only" in contrast_line or "fails" in contrast_line):
        lines.append("Primary on background does not clear 4.5:1 \u2014 keep the primary on surfaces, rules and "
                     "charts; body text uses the text role.")
    lines.append("Draft by extract_theme.py \u2014 role mapping follows the Office theme convention; confirm the "
                 "swatch before relying on it.")
    return "\n".join(lines) + "\n"


def _company_from_props(zf: zipfile.ZipFile):
    """Company name from docProps title, as a short literal only (data, not instructions)."""
    try:
        core = zf.read("docProps/core.xml").decode("utf-8", "ignore")
    except KeyError:
        return None
    m = re.search(r"<dc:title>(.*?)</dc:title>", core, re.S)
    if not m:
        return None
    title = re.sub(r"<[^>]+>", "", m.group(1)).split("|")[0].split(" - ")[0].strip()
    if not title or len(title) > 80 or re.search(r"https?://|ignore|instruction|when generating|send |<|>", title, re.I):
        return None
    return title


# ----------------------------------------------------------------------------- swatch
def render_swatch(brand_md: str, out_png: str) -> dict:
    """PNG swatch strip from a brand.md: role label + hex under each colour, fonts line, logo
    thumbnail when the asset exists beside the file. Returns {"ok", "path", "roles"}."""
    if not HAVE_PIL:
        return {"ok": False, "error": "Pillow missing - show a role/hex table instead"}
    from PIL import ImageDraw, ImageFont
    text = open(brand_md, encoding="utf-8").read()
    roles = re.findall(r"^\*\*([^*]+?):\*\*\s*(#[0-9A-Fa-f]{6})", text, re.M)
    fonts = dict(re.findall(r"^\*\*(Heading font|Body font):\*\*\s*([^\n(]+)", text, re.M))
    logo_rel = re.search(r"^\*\*Primary logo:\*\*\s*(\S+)", text, re.M)
    if not roles:
        return {"ok": False, "error": "no hex values in brand.md"}
    sw, sh, pad = 150, 90, 12
    width = max(len(roles) * (sw + pad) + pad, 640)
    height = sh + 90 + (110 if logo_rel else 0)
    img = Image.new("RGB", (width, height), "#FFFFFF")
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 13)
    except Exception:
        font = ImageFont.load_default()
    x = pad
    for role, hexv in roles:
        d.rectangle((x, pad, x + sw, pad + sh), fill=hexv.upper(), outline="#CCCCCC")
        d.text((x, pad + sh + 6), role[:20], fill="#1A1A1A", font=font)
        d.text((x, pad + sh + 24), hexv.upper(), fill="#555555", font=font)
        x += sw + pad
    y = pad + sh + 46
    if fonts:
        d.text((pad, y), "Heading: %s   Body: %s" % (fonts.get("Heading font", "-").strip(),
                                                     fonts.get("Body font", "-").strip()), fill="#1A1A1A", font=font)
    if logo_rel:
        lp = os.path.join(os.path.dirname(brand_md), logo_rel.group(1))
        if os.path.exists(lp):
            try:
                lg = Image.open(lp).convert("RGBA")
                lg.thumbnail((300, 90))
                img.paste(lg, (pad, y + 20), lg)
            except Exception:
                d.text((pad, y + 20), "logo present (preview unavailable)", fill="#555555", font=font)
    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)
    img.save(out_png)
    return {"ok": True, "path": out_png, "roles": [r for r, _ in roles]}


# ----------------------------------------------------------------------------- main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file", nargs="?", help="Office file to extract from")
    ap.add_argument("--out", required=True, help="staging folder, e.g. working/brand-staging/<slug>")
    ap.add_argument("--swatch", metavar="BRAND_MD",
                    help="render <out>/swatch.png from an existing brand.md instead of extracting")
    ap.add_argument("--company", help="company name (else taken from docProps title when clean)")
    ap.add_argument("--no-logo", action="store_true", help="skip logo extraction")
    args = ap.parse_args(argv)

    if args.swatch:
        res = render_swatch(args.swatch, os.path.join(args.out, "swatch.png"))
        print(json.dumps(res))
        return 0 if res["ok"] else 1
    if not args.file:
        ap.error("an Office file is required unless --swatch is given")
    ext = os.path.splitext(args.file)[1].lower()
    if ext not in LAYOUTS:
        print(json.dumps({"ok": False, "error": "unsupported extension %s (use .pptx/.docx/.xlsx)" % ext}))
        return 2
    theme_part, media_prefix, part_prefix = LAYOUTS[ext]
    result: dict = {"ok": True, "source": os.path.basename(args.file), "pillow": HAVE_PIL, "warnings": []}

    try:
        zf = zipfile.ZipFile(args.file)
    except (zipfile.BadZipFile, OSError) as e:
        print(json.dumps({"ok": False, "error": "cannot open as Office ZIP: %s" % e}))
        return 2

    with zf:
        colours, fonts = {}, {}
        if theme_part in zf.namelist():
            colours, fonts = parse_theme(zf.read(theme_part).decode("utf-8", "ignore"))
        else:
            result["warnings"].append("no theme part (%s) - sample pixels and mark (inferred)" % theme_part)
        palette = [(role, colours[slot], slot) for slot, role in ROLE_MAP if slot in colours]
        result["theme_colours"] = colours
        result["palette"] = [{"role": r, "hex": h, "slot": s, "inferred": True} for r, h, s in palette]
        result["fonts"] = dict(fonts, fallback=FALLBACK_STACK)

        bg, text, primary = colours.get("lt1"), colours.get("dk1"), colours.get("accent1")
        contrast_line = None
        if bg and text:
            c1 = contrast(text, bg)
            parts = ["text/bg %s:1 %s" % (c1, contrast_verdict(c1))]
            result["contrast"] = {"text_on_bg": c1}
            if primary:
                c2 = contrast(primary, bg)
                parts.append("primary/bg %s:1 %s" % (c2, contrast_verdict(c2)))
                result["contrast"]["primary_on_bg"] = c2
            contrast_line = " \u00b7 ".join(parts)
        result["contrast_line"] = contrast_line
        scheme = ("light" if luminance(bg) > 0.4 else "dark") if bg else None
        result["scheme"] = scheme

        logo = None
        candidates = [] if args.no_logo else score_media(zf, media_prefix, part_prefix)
        result["logo_candidates"] = candidates[:8]
        keep = [c for c in candidates if c["discard"] is None and c["score"] > 0]
        if keep:
            try:
                logo = save_logo(zf, keep[0], os.path.join(args.out, "assets"))
                result["logo"] = logo
            except Exception as e:
                result["warnings"].append("logo copy failed: %s" % e)
        elif not args.no_logo:
            result["warnings"].append("no credible logo candidate in embedded media - record no logo")
        result["company"] = args.company or _company_from_props(zf)

    os.makedirs(args.out, exist_ok=True)
    md = build_brand_md(result["company"], result["source"], palette, fonts, logo, contrast_line, scheme)
    with open(os.path.join(args.out, "brand.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    result["brand_md"] = os.path.join(args.out, "brand.md")
    if not palette:
        result["warnings"].append("empty palette - fall back to pixel sampling (references/extraction-recipes.md)")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
