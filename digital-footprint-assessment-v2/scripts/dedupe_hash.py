#!/usr/bin/env python3
"""dedupe_hash.py — collapse the same photograph captured through two CDNs.

URL normalisation catches most of it at plan time; this catches the rest after
capture, with a 64-bit difference hash (Pillow only). The same headshot served
by two outlets is ONE asset and a consistency finding — never two figures.

  python scripts/dedupe_hash.py --run <dir> --subject <slug> [--distance 6]
"""
import argparse, os, sys
import _dfa

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow is required (PIL).", file=sys.stderr)
    sys.exit(2)


def dhash(path, size=8):
    im = Image.open(path).convert("L").resize((size + 1, size), Image.LANCZOS)
    try:
        px = list(im.get_flattened_data())
    except AttributeError:
        px = list(im.getdata())
    bits = 0
    for row in range(size):
        for col in range(size):
            left = px[row * (size + 1) + col]
            right = px[row * (size + 1) + col + 1]
            bits = (bits << 1) | (1 if left > right else 0)
    return bits


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--subject", required=True)
    ap.add_argument("--distance", type=int, default=6)
    args = ap.parse_args()

    man = _dfa.load_manifest(args.run, args.subject)
    kept = []
    collapsed = 0
    for a in _dfa.shown_assets(man):
        path = os.path.join(args.run, args.subject, a.get("file", ""))
        if not os.path.exists(path):
            continue
        h = dhash(path)
        match = next((k for k in kept if bin(k[1] ^ h).count("1") <= args.distance), None)
        if match:
            a["state"] = "duplicate"
            a["dedupe_group"] = match[2]
            a["reason"] = _dfa.REASONS["duplicate"].format(ref=match[0])
            collapsed += 1
        else:
            kept.append((a["id"], h, a.get("dedupe_group") or a["id"]))
    _dfa.save_manifest(args.run, args.subject, man)
    print("%s — %d distinct photograph(s) kept, %d collapsed as republication(s)"
          % (args.subject, len(kept), collapsed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
