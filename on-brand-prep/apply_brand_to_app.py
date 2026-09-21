#!/usr/bin/env python3
"""apply_brand_to_app.py — serve a stored brand profile INTO an App Builder app's theme file.

Deterministic, stdlib-only. Reads `brands/<slug>/brand.md`, converts the palette to OKLCH and
rewrites a fixed set of shadcn/Tailwind v4 CSS variables in `<app_dir>/src/index.css`. Stages the
logo under `src/assets/`. Keeps a byte-exact copy of the untouched theme at
`src/index.css.neutral` so `--remove` restores the app exactly.

Usage:
    python apply_brand_to_app.py <app_dir> --brand /mnt/user-config/brands/<slug>/brand.md
    python apply_brand_to_app.py <app_dir> --brand <brand.md> --dry-run
    python apply_brand_to_app.py <app_dir> --remove

Touches ONLY: --primary, --primary-foreground, --ring, --accent, --accent-foreground,
--background, --foreground, --secondary, --secondary-foreground, --radius inside `:root {` and the dark blocks, plus
--font-sans / --font-heading inside `@theme inline {`. Never `.warm {` (surface theme), --chart-*, --destructive*, sidebar
vars, or anything else — status colours must stay recognisable (colour + shape + word).

Output: one JSON object on stdout (see `result` below). Exit 0 on success, 2 on usage/IO errors.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import re
import shutil
import sys
from pathlib import Path

# --------------------------------------------------------------------------------------------
# brand.md parsing
# --------------------------------------------------------------------------------------------

KEYS = {
    "company": ("Company",),
    "primary": ("Primary",),
    "secondary": ("Secondary",),
    "accent": ("Accent",),
    "background": ("Background",),
    "text": ("Text / foreground", "Text/foreground", "Text", "Foreground"),
    "heading_font": ("Heading font",),
    "body_font": ("Body font",),
    "fallback": ("Fallback stack",),
    "logo": ("Primary logo",),
    "logo_dark": ("Dark-background variant", "Dark background variant"),
    "scheme": ("Scheme",),
    "shape": ("Shape style",),
}

MARKER_RE = re.compile(r"\((inferred[^)]*|default\s*[—-]+\s*not extracted[^)]*)\)", re.I)
LINE_RE = re.compile(r"^\*\*(?P<key>[^*]+?):\*\*\s*(?P<val>.*?)\s*$")
HEX_RE = re.compile(r"#([0-9a-fA-F]{6})\b")


def parse_brand(path: Path) -> tuple[dict, dict]:
    """Return ({field: value}, {field: marker}) with `(inferred)`/`(default …)` markers stripped."""
    values: dict[str, str] = {}
    markers: dict[str, str] = {}
    lookup = {alias.lower(): field for field, aliases in KEYS.items() for alias in aliases}
    for raw in path.read_text(encoding="utf-8").splitlines():
        m = LINE_RE.match(raw.strip())
        if not m:
            continue
        field = lookup.get(m.group("key").strip().lower())
        if not field:
            continue
        val = m.group("val")
        val = re.sub(r"<!--.*?-->", "", val).strip()  # template comments
        mk = MARKER_RE.search(val)
        if mk:
            markers[field] = mk.group(1).strip()
            val = MARKER_RE.sub("", val).strip()
        if not val or val.startswith("<"):  # unfilled template placeholder
            continue
        values[field] = val
    return values, markers


def hex_of(val: str | None) -> str | None:
    if not val:
        return None
    m = HEX_RE.search(val)
    return ("#" + m.group(1).upper()) if m else None


# --------------------------------------------------------------------------------------------
# colour maths: sRGB -> linear -> OKLab -> OKLCH, plus WCAG contrast
# --------------------------------------------------------------------------------------------

def hex_to_rgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))  # type: ignore[return-value]


def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c: float) -> float:
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def rgb_to_oklab(r: float, g: float, b: float) -> tuple[float, float, float]:
    lr, lg, lb = srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b)
    l = 0.4122214708 * lr + 0.5363325363 * lg + 0.0514459929 * lb
    m = 0.2119034982 * lr + 0.6806995451 * lg + 0.1073969566 * lb
    s = 0.0883024619 * lr + 0.2817188376 * lg + 0.6299787005 * lb
    l_, m_, s_ = math.copysign(abs(l) ** (1 / 3), l), math.copysign(abs(m) ** (1 / 3), m), math.copysign(abs(s) ** (1 / 3), s)
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b2 = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, a, b2


def oklab_to_rgb(L: float, a: float, b: float) -> tuple[float, float, float]:
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    lr = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    lg = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    lb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return linear_to_srgb(lr), linear_to_srgb(lg), linear_to_srgb(lb)


def hex_to_oklch(h: str) -> tuple[float, float, float]:
    L, a, b = rgb_to_oklab(*hex_to_rgb(h))
    C = math.hypot(a, b)
    H = math.degrees(math.atan2(b, a)) % 360 if C > 1e-4 else 0.0
    return L, C, H


def oklch_to_rgb(L: float, C: float, H: float) -> tuple[float, float, float]:
    a = C * math.cos(math.radians(H))
    b = C * math.sin(math.radians(H))
    return oklab_to_rgb(L, a, b)


def oklch_css(L: float, C: float, H: float) -> str:
    L = max(0.0, min(1.0, L))
    C = max(0.0, C)
    return f"oklch({round(L, 3):.3f} {round(C, 3):.3f} {round(H % 360, 1):.1f})"


def rel_luminance(rgb: tuple[float, float, float]) -> float:
    r, g, b = (srgb_to_linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(rgb1, rgb2) -> float:
    l1, l2 = rel_luminance(rgb1), rel_luminance(rgb2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


WHITE = (0.99, 0.99, 0.99)
NEAR_BLACK = (0.10, 0.10, 0.10)


def foreground_for(L: float, C: float, H: float) -> tuple[str, float]:
    """White or near-black text over the given colour, whichever has the better WCAG ratio."""
    bg = oklch_to_rgb(L, C, H)
    cw, cb = contrast(WHITE, bg), contrast(NEAR_BLACK, bg)
    if cw >= cb:
        return "oklch(0.990 0.000 0.0)", cw
    return "oklch(0.145 0.000 0.0)", cb


# --------------------------------------------------------------------------------------------
# CSS block editing (regex per `--name:` line, within one block only)
# --------------------------------------------------------------------------------------------

def find_block(css: str, opener_re: str) -> tuple[int, int] | None:
    """Return (start, end) offsets of the body between the braces of the first block whose opener
    matches `opener_re` (a regex ending just before `{`). Brace-balanced."""
    m = re.search(opener_re + r"\s*\{", css)
    if not m:
        return None
    depth, i = 1, m.end()
    while i < len(css) and depth:
        if css[i] == "{":
            depth += 1
        elif css[i] == "}":
            depth -= 1
        i += 1
    return m.end(), i - 1


def set_vars_in_block(css: str, opener_re: str, assignments: dict[str, str]) -> tuple[str, list[str], list[str]]:
    """Replace `--name: …;` lines inside the block. Returns (css, set_names, missing_names)."""
    span = find_block(css, opener_re)
    if span is None:
        return css, [], list(assignments)
    start, end = span
    body = css[start:end]
    done, missing = [], []
    for name, value in assignments.items():
        pat = re.compile(r"(^[ \t]*" + re.escape(name) + r"\s*:\s*)([^;\n]*)(;)", re.M)
        if pat.search(body):
            body = pat.sub(lambda m: m.group(1) + value + m.group(3), body, count=1)
            done.append(name)
        else:
            missing.append(name)
    return css[:start] + body + css[end:], done, missing


ROOT_RE = r"(?<![\w.:#-]):root"
DARK_RE = r"(?<![\w.:#-])\.dark"
OS_DARK_RE = r"@media\s*\(\s*prefers-color-scheme\s*:\s*dark\s*\)\s*\{\s*:root:not\(\.light\)"
THEME_RE = r"@theme\s+inline"
WARM_RE = r"(?<![\w.:#-])\.warm"  # user-selectable surface theme — NEVER written; brand tokens inherit from :root

# --------------------------------------------------------------------------------------------
# radius / fonts
# --------------------------------------------------------------------------------------------

DEFAULT_FONT_MARKERS = ("system-ui", "sans-serif")


def radius_for(shape: str | None) -> str | None:
    if not shape:
        return None
    s = shape.lower()
    if "square" in s or "sharp" in s:
        return "0.125rem"
    if "round" in s:
        m = re.search(r"(\d+(?:\.\d+)?)\s*px", s)
        if m:
            return f"{round(float(m.group(1)) / 16, 4):g}rem"
    return None


def font_stack(font: str | None, fallback: str | None, marker: str | None) -> str | None:
    if not font or marker:  # `(default — not extracted)` / `(inferred)` fonts are not applied
        return None
    if font.strip().lower() in DEFAULT_FONT_MARKERS:
        return None
    fb = fallback or "system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    parts = [p.strip().strip("'\"") for p in fb.split(",") if p.strip()]
    parts = [p for p in parts if p.lower() != font.strip().lower()]
    quoted = [f"'{p}'" if (" " in p and p.lower() not in ("sans-serif", "serif", "monospace")) else p for p in parts]
    return f"'{font.strip()}', " + ", ".join(quoted)


# --------------------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------------------

def emit(obj: dict, code: int = 0) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False))
    sys.exit(code)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("app_dir", help="App Builder app root (contains src/index.css)")
    ap.add_argument("--brand", help="Path to brands/<slug>/brand.md")
    ap.add_argument("--remove", action="store_true", help="Restore src/index.css.neutral and delete the staged logo")
    ap.add_argument("--dry-run", action="store_true", help="Compute and print, write nothing")
    args = ap.parse_args()

    app = Path(args.app_dir).resolve()
    css_path = app / "src" / "index.css"
    neutral_path = app / "src" / "index.css.neutral"
    assets_dir = app / "src" / "assets"

    result: dict = {
        "app_dir": str(app),
        "theme_file": str(css_path),
        "applied": {},
        "fonts": {},
        "logo": None,
        "logo_dark": None,
        "company": None,
        "contrast": {},
        "warnings": [],
        "header_iterate_needed": False,
        "restored": False,
        "dry_run": bool(args.dry_run),
        "date": _dt.date.today().isoformat(),
    }

    if not css_path.is_file():
        result["warnings"].append(f"theme file not found: {css_path}")
        emit(result, 2)

    # ---------------------------------------------------------------- remove
    if args.remove:
        if not neutral_path.is_file():
            result["warnings"].append("no src/index.css.neutral — the app was never branded by this script; nothing restored")
            emit(result, 2)
        logos = sorted(assets_dir.glob("brand-logo*.*")) if assets_dir.is_dir() else []
        if not args.dry_run:
            shutil.copyfile(neutral_path, css_path)
            for lg in logos:
                lg.unlink()
            try:
                if assets_dir.is_dir() and not any(assets_dir.iterdir()):
                    assets_dir.rmdir()
            except OSError:
                pass
        result["restored"] = True
        result["removed_logos"] = [str(p) for p in logos]
        result["header_iterate_needed"] = bool(logos)  # revert the header import/markup
        emit(result)

    # ---------------------------------------------------------------- apply
    if not args.brand:
        result["warnings"].append("--brand <brand.md> is required unless --remove")
        emit(result, 2)
    brand_path = Path(args.brand).resolve()
    if not brand_path.is_file():
        result["warnings"].append(f"brand profile not found: {brand_path}")
        emit(result, 2)

    vals, markers = parse_brand(brand_path)
    result["company"] = vals.get("company")
    result["markers"] = markers

    primary = hex_of(vals.get("primary"))
    if not primary:
        result["warnings"].append("brand.md has no Primary colour — nothing applied (never invent a palette)")
        emit(result, 2)
    if "primary" in markers:
        result["warnings"].append(f"Primary is marked ({markers['primary']}) — applied as-is; confirm with the user")

    secondary = hex_of(vals.get("secondary"))
    background = hex_of(vals.get("background"))
    text = hex_of(vals.get("text"))
    scheme = (vals.get("scheme") or "light").lower()
    is_light = "dark" not in scheme.split("|")[0].strip() if scheme else True

    pL, pC, pH = hex_to_oklch(primary)

    # light block
    root_vars: dict[str, str] = {}
    root_vars["--primary"] = oklch_css(pL, pC, pH)
    pf, pf_ratio = foreground_for(pL, pC, pH)
    root_vars["--primary-foreground"] = pf
    root_vars["--ring"] = root_vars["--primary"]
    root_vars["--accent"] = oklch_css(0.95, pC * 0.15, pH)
    root_vars["--accent-foreground"] = oklch_css(0.38, pC * 0.8, pH)
    if background and is_light:
        root_vars["--background"] = oklch_css(*hex_to_oklch(background))
    if text:
        root_vars["--foreground"] = oklch_css(*hex_to_oklch(text))
    if secondary:
        sL, sC, sH = hex_to_oklch(secondary)
        root_vars["--secondary"] = oklch_css(sL, sC, sH)
        root_vars["--secondary-foreground"], sf_ratio = foreground_for(sL, sC, sH)
    radius = radius_for(vals.get("shape"))
    if radius:
        root_vars["--radius"] = radius

    # dark block(s)
    dL = max(pL, 0.63)
    dark_vars: dict[str, str] = {}
    dark_vars["--primary"] = oklch_css(dL, pC, pH)
    dpf, dpf_ratio = foreground_for(dL, pC, pH)
    dark_vars["--primary-foreground"] = dpf
    dark_vars["--ring"] = dark_vars["--primary"]
    dark_vars["--accent"] = oklch_css(0.26, pC * 0.3, pH)
    dark_vars["--accent-foreground"] = oklch_css(0.90, pC * 0.2, pH)
    if secondary:
        dsL = max(sL, 0.63)
        dark_vars["--secondary"] = oklch_css(dsL, sC, sH)
        dark_vars["--secondary-foreground"], dsf_ratio = foreground_for(dsL, sC, sH)

    # fonts
    theme_vars: dict[str, str] = {}
    body_stack = font_stack(vals.get("body_font"), vals.get("fallback"), markers.get("body_font"))
    head_stack = font_stack(vals.get("heading_font"), vals.get("fallback"), markers.get("heading_font"))
    if body_stack:
        theme_vars["--font-sans"] = body_stack
    elif vals.get("body_font"):
        result["warnings"].append(f"Body font '{vals['body_font']}' is a default/inferred marker — kept the app's bundled font")
    if head_stack:
        theme_vars["--font-heading"] = head_stack
    elif body_stack:
        theme_vars["--font-heading"] = "var(--font-sans)"
    if body_stack or head_stack:
        result["warnings"].append("Fonts are not installed by this script: the app renders '<font>' only where the machine has it, else the fallback stack")

    # contrast (light): primary vs background, text vs background
    bg_rgb = hex_to_rgb(background) if background else oklch_to_rgb(0.975, 0.004, 250)
    pr = contrast(hex_to_rgb(primary), bg_rgb)
    result["contrast"] = {
        "primary_vs_background": round(pr, 2),
        "primary_foreground_on_primary": round(pf_ratio, 2),
        "dark_primary_foreground_on_primary": round(dpf_ratio, 2),
    }
    if secondary:
        result["contrast"]["secondary_foreground_on_secondary"] = round(sf_ratio, 2)
        result["contrast"]["dark_secondary_foreground_on_secondary"] = round(dsf_ratio, 2)
        if sf_ratio < 4.5:
            result["warnings"].append(f"Best text over secondary reaches only {sf_ratio:.2f}:1 (< 4.5:1)")
    if text:
        result["contrast"]["text_vs_background"] = round(contrast(hex_to_rgb(text), bg_rgb), 2)
    if pr < 3.0:
        result["warnings"].append(f"Primary {primary} on background is {pr:.2f}:1 (< 3:1) — buttons/rings will be faint; consider a darker primary")
    if pf_ratio < 4.5:
        result["warnings"].append(f"Best text over primary reaches only {pf_ratio:.2f}:1 (< 4.5:1) — button labels are large/bold only")

    # ---------------------------------------------------------------- write CSS
    css = css_path.read_text(encoding="utf-8")
    if neutral_path.is_file():
        base = neutral_path.read_text(encoding="utf-8")  # always re-derive from the neutral copy → idempotent
    else:
        base = css
        if not args.dry_run:
            shutil.copyfile(css_path, neutral_path)

    new_css, set_root, miss_root = set_vars_in_block(base, ROOT_RE, root_vars)
    new_css, set_dark, miss_dark = set_vars_in_block(new_css, DARK_RE, dark_vars)
    new_css, set_os, miss_os = set_vars_in_block(new_css, OS_DARK_RE, dark_vars)
    new_css, set_theme, miss_theme = set_vars_in_block(new_css, THEME_RE, theme_vars)

    result["applied"] = {
        ":root": {k: root_vars[k] for k in set_root},
        ".dark": {k: dark_vars[k] for k in set_dark},
        "@media prefers-color-scheme dark": {k: dark_vars[k] for k in set_os},
    }
    result["fonts"] = {k: theme_vars[k] for k in set_theme}
    for blk, miss in ((":root", miss_root), (".dark", miss_dark), ("@theme inline", miss_theme)):
        if miss:
            result["warnings"].append(f"{blk}: variables not present in the app, skipped: {', '.join(miss)}")
    warm = find_block(base, WARM_RE)
    if warm is not None:
        new_warm = find_block(new_css, WARM_RE)
        if new_warm is None or base[warm[0]:warm[1]] != new_css[new_warm[0]:new_warm[1]]:
            result["warnings"].append("INTERNAL: .warm block changed — refusing to write")
            emit(result, 2)
        result.setdefault("notes", []).append(".warm surface theme left untouched by design — in Warm the brand background/foreground are overridden by the warm surfaces; primary/accent/ring inherit from :root")
    if find_block(base, OS_DARK_RE) is None:
        result.setdefault("notes", []).append("no OS-dark mirror block in this theme file — .dark only")

    # ---------------------------------------------------------------- logo
    logo_src = None
    if vals.get("logo"):
        cand = (brand_path.parent / vals["logo"]).resolve()
        if cand.is_file():
            logo_src = cand
        else:
            result["warnings"].append(f"Primary logo path does not resolve: {cand} — nothing placed")
    dark_src = None
    if vals.get("logo_dark"):
        cand = (brand_path.parent / vals["logo_dark"]).resolve()
        if cand.is_file():
            dark_src = cand
        else:
            result["warnings"].append(f"Dark logo path does not resolve: {cand} — skipped")

    if logo_src:
        dest = assets_dir / f"brand-logo{logo_src.suffix.lower()}"
        result["logo"] = str(dest.relative_to(app))
        result["logo_import"] = f'import brandLogo from "@/assets/brand-logo{logo_src.suffix.lower()}";'
        result["header_iterate_needed"] = True
        if dark_src:
            ddest = assets_dir / f"brand-logo-dark{dark_src.suffix.lower()}"
            result["logo_dark"] = str(ddest.relative_to(app))
    else:
        result["warnings"].append("no logo in the profile — header keeps its text kicker; never draw or substitute one")

    if not args.dry_run:
        css_path.write_text(new_css, encoding="utf-8")
        if logo_src:
            assets_dir.mkdir(parents=True, exist_ok=True)
            for old in assets_dir.glob("brand-logo*.*"):
                old.unlink()
            shutil.copyfile(logo_src, assets_dir / f"brand-logo{logo_src.suffix.lower()}")
            if dark_src:
                shutil.copyfile(dark_src, assets_dir / f"brand-logo-dark{dark_src.suffix.lower()}")

    result["neutral_backup"] = str(neutral_path)
    result["application_note"] = (
        f"Applied to Exec Command Center app {app.name} on {result['date']}"
    )
    emit(result)


if __name__ == "__main__":
    main()
