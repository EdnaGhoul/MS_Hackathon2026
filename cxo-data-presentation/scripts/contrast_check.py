#!/usr/bin/env python3
"""Contrast check for status palettes (WCAG 2.2).

Computes the WCAG relative-luminance contrast ratio between each status colour and a
background, and between every pair of status colours. Flags:
  - any status colour below 3:1 against the background (SC 1.4.11 / 1.4.1 lightness cue)
  - (with --strict-pairs) any pair of status colours below 3:1 against each other
and reminds that colour must never be the sole cue (SC 1.4.1 requires icon or text).

Usage:
  python contrast_check.py --bg "#ffffff" --colors ok=#1B7F3B risk=#B8860B off=#B02A2A nodata=#6B6B6B
  python contrast_check.py --json ...

Pure standard library. Exit code 1 if any check fails.
"""
import argparse
import json
import sys


def _hex_to_rgb(h: str):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"bad colour: {h}")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _lin(c: int) -> float:
    s = c / 255.0
    return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4


def luminance(h: str) -> float:
    r, g, b = _hex_to_rgb(h)
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--bg", default="#ffffff", help="background colour (hex)")
    p.add_argument("--colors", nargs="+", required=True, help="name=#hex pairs")
    p.add_argument("--min", type=float, default=3.0, help="minimum ratio (default 3.0)")
    p.add_argument("--strict-pairs", action="store_true",
                   help="also fail when two status colours are below the ratio against each other "
                        "(only needed when no icon/text cue is present)")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    colours = {}
    for item in a.colors:
        if "=" not in item:
            print(f"expected name=#hex, got {item}", file=sys.stderr)
            return 2
        name, hexv = item.split("=", 1)
        colours[name] = hexv

    results = {"background": a.bg, "min_ratio": a.min, "vs_background": [], "pairs": [], "passed": True}

    for name, hexv in colours.items():
        r = round(contrast(hexv, a.bg), 2)
        ok = r >= a.min
        results["vs_background"].append({"status": name, "color": hexv, "ratio": r, "pass": ok})
        results["passed"] &= ok

    names = list(colours)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            r = round(contrast(colours[names[i]], colours[names[j]]), 2)
            ok = r >= a.min
            results["pairs"].append({"a": names[i], "b": names[j], "ratio": r, "pass": ok})
            if a.strict_pairs:
                results["passed"] &= ok

    results["reminder"] = ("WCAG 2.2 SC 1.4.1: colour must never be the only cue. "
                           "Every status also needs an icon or text label regardless of these ratios.")

    if a.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"Background {a.bg}, minimum ratio {a.min}:1")
        for row in results["vs_background"]:
            print(f"  {row['status']:<8} {row['color']:<8} vs bg  {row['ratio']:>5}:1  {'PASS' if row['pass'] else 'FAIL'}")
        for row in results["pairs"]:
            print(f"  {row['a']:<8} vs {row['b']:<8}      {row['ratio']:>5}:1  {'PASS' if row['pass'] else 'FAIL'}")
        print(results["reminder"])
        print("RESULT:", "PASS" if results["passed"] else "FAIL")

    return 0 if results["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
