#!/usr/bin/env python3
"""set_state.py — the verification transition, with a mandatory reason.

Verification is the accuracy guarantee of the whole skill: nothing is published
until a human-readable match has been recorded against a captured file. This is
also the only way an asset may be dropped, which is why the reason is required
rather than optional — "viewed it, wasn't sure, deleted it" is how a photograph
disappears with no trace.

  python scripts/set_state.py --run <dir> --subject <slug> --asset asset-01 \
      verified --matched-against "asset-02 corporate headshot; caption names the subject"
  python scripts/set_state.py ... unverifiable --matched-against "face is 40px at the best rung reached"
  python scripts/set_state.py ... wrong_person --matched-against "different person; caption names a namesake"
"""
import argparse, os, sys
import _dfa

ALLOWED = {"verified", "unverifiable", "wrong_person", "not_photo",
           "unresolved_address", "browser_unavailable"}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--subject", required=True)
    ap.add_argument("--asset", required=True)
    ap.add_argument("state", choices=sorted(ALLOWED))
    ap.add_argument("--matched-against", required=True,
                    help="what the capture was matched against — printed in the figure caption")
    args = ap.parse_args()

    man = _dfa.load_manifest(args.run, args.subject)
    a = _dfa.asset(man, args.asset)

    if args.state == "verified":
        f = a.get("file") or os.path.join("img", "%s.png" % args.asset)
        full = os.path.join(args.run, args.subject, f)
        if not os.path.exists(full):
            print("REFUSED — %s has no captured file at %s. Verify what was captured, not what was "
                  "found." % (args.asset, full), file=sys.stderr)
            return 1
        a["file"] = f
        a["sidecar"] = os.path.splitext(f)[0] + ".json"
        a["state"] = "verified"
        a["verification"] = {"by": "view", "matched_against": args.matched_against, "result": "match"}
        a.pop("reason", None)
    else:
        a["state"] = args.state
        a["verification"] = {"by": "view", "matched_against": args.matched_against,
                             "result": "no-match" if args.state == "wrong_person" else "unsure"}
        a["reason"] = _dfa.REASONS[args.state]

    _dfa.save_manifest(args.run, args.subject, man)
    print("%s → %s" % (args.asset, a["state"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
