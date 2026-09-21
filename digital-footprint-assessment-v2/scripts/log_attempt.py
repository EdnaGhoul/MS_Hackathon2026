#!/usr/bin/env python3
"""log_attempt.py — record one capture attempt and move the asset's state.

The attempt log is what makes the ladder real. A rung that was never tried can
no longer look like a rung that failed, and the report's "not shown" reason is
generated from these rows rather than typed.

  python scripts/log_attempt.py --run <dir> --subject <slug> --asset asset-01 \
      --tier A --url <url> --outcome ok [--returned <browserState.url>] [--shot shots/x.webp]
  python scripts/log_attempt.py --run <dir> --subject <slug> --asset asset-01 --next
  python scripts/log_attempt.py --run <dir> --subject <slug> --browser-down

`--next` returns the rung to try next, so the agent never decides to give up.
Exit 3 means the ladder is finished (state becomes `exhausted`).

`--browser-down` is what you call when the browser session stops responding.
It closes every remaining asset as `browser_unavailable` \u2014 honest, retryable,
and explicitly NOT a finding about the publishers. A dead tool must never be
reported to the reader as "every route to the file refused".
"""
import argparse, datetime, sys
import _dfa


def next_rung(rows):
    # Only attempts that actually reached a host advance the ladder.
    tried = [r.get("tier") for r in rows if r.get("outcome") not in _dfa.RUN_FAILURE_OUTCOMES]
    for tier in _dfa.LADDER:
        if tier not in tried:
            return tier
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--subject", required=True)
    ap.add_argument("--asset", default="")
    ap.add_argument("--tier", choices=_dfa.LADDER)
    ap.add_argument("--url", default="")
    ap.add_argument("--returned", default="", help="browserState.url actually returned")
    ap.add_argument("--outcome", choices=_dfa.OUTCOMES)
    ap.add_argument("--shot", default="")
    ap.add_argument("--next", action="store_true", dest="want_next")
    ap.add_argument("--browser-down", action="store_true",
                    help="the browser session died: close every remaining asset as retryable")
    args = ap.parse_args()

    man = _dfa.load_manifest(args.run, args.subject)
    if args.browser_down:
        hit = []
        for a in man["assets"]:
            if a.get("state") in {"candidate", "queued", "capturing", "captured", "budget_capped"}:
                if a.get("state") == "captured":
                    continue          # captured but unverified is a verification job, not a browser one
                a["state"] = "browser_unavailable"
                a["reason"] = _dfa.REASONS["browser_unavailable"]
                hit.append(a["id"])
        _dfa.save_manifest(args.run, args.subject, man)
        print("browser marked down \u2014 %d asset(s) closed as retryable: %s"
              % (len(hit), ", ".join(hit) or "none"))
        print("These are NOT reported as host refusals. Re-run capture for this subject when the "
              "browser is back.")
        return 0

    if not args.asset:
        print("--asset is required unless --browser-down is used", file=sys.stderr)
        return 2
    a = _dfa.asset(man, args.asset)
    rows = [r for r in _dfa.read_log(args.run, args.subject) if r.get("asset_id") == args.asset]

    if args.want_next:
        rung = next_rung(rows)
        if rung:
            print(rung)
            return 0
        reached = [r for r in rows if r.get("outcome") not in _dfa.RUN_FAILURE_OUTCOMES]
        a["state"] = "exhausted" if reached else "browser_unavailable"
        a["reason"] = _dfa.exhausted_reason(rows) if reached else _dfa.REASONS["browser_unavailable"]
        _dfa.save_manifest(args.run, args.subject, man)
        print("%s — %s" % (a["state"].upper(), a["reason"]))
        return 3
    if not args.tier or not args.outcome:
        print("--tier and --outcome are required unless --next is used", file=sys.stderr)
        return 2

    row = {"ts": datetime.datetime.now().isoformat(timespec="seconds"),
           "asset_id": args.asset, "tier": args.tier, "url": args.url,
           "browser_url_returned": args.returned, "outcome": args.outcome, "shot": args.shot}
    _dfa.append_log(args.run, args.subject, row)
    rows.append(row)
    a["attempts"] = len(rows)

    if args.outcome == "browser_unavailable":
        a["state"] = "browser_unavailable"
        a["reason"] = _dfa.REASONS["browser_unavailable"]
        print("browser_unavailable logged \u2014 %s is retryable, not refused. Use --browser-down to "
              "close the rest of the queue the same way." % args.asset)
    elif args.outcome == "tab_mismatch":
        # Contention is VISIBLE, not silent: the asset stays in capturing and is retried.
        a["state"] = "capturing"
        print("tab_mismatch logged — another tab answered. %s stays `capturing`; retry the same rung."
              % args.asset)
    elif args.outcome == "ok":
        a["state"] = "captured"
        print("captured — now `view` the crop and record verification with set_state.py")
    elif args.outcome == "not_photo":
        a["state"] = "not_photo"
        a["reason"] = _dfa.REASONS["not_photo"]
        print("not_photo — out of scope, no capture")
    else:
        rung = next_rung(rows)
        if rung:
            a["state"] = "capturing"
            print("%s at tier %s — next rung: %s" % (args.outcome, args.tier, rung))
        else:
            a["state"] = "exhausted"
            a["reason"] = _dfa.exhausted_reason(rows)
            print("EXHAUSTED — %s" % a["reason"])
    _dfa.save_manifest(args.run, args.subject, man)
    return 0


if __name__ == "__main__":
    sys.exit(main())
