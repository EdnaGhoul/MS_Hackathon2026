#!/usr/bin/env python3
"""plan_capture.py — dedupe, rank and budget the photo candidates; brief the
capture agent; and close a subject only when every asset is terminal.

Three modes:
  python scripts/plan_capture.py --run <run-dir>                 # plan every subject
  python scripts/plan_capture.py --run <run-dir> --brief <slug>  # the capture agent's brief
  python scripts/plan_capture.py --run <run-dir> --finalize <slug>
  python scripts/plan_capture.py --run <run-dir> --refill <slug>

The budget limits ATTEMPTS, never display. Every verified capture is shown, and
`--refill` re-spends the budget when attempts failed rather than leaving the
easiest assets capped behind a queue of hard ones.
"""
import argparse, os, re, sys
import _dfa

# CDN width/preset parameters that make one photograph look like several URLs.
_PRESET = re.compile(r"[?&](wid|w|width|h|hei|height|q|fmt|format|rev|\$[A-Za-z0-9_-]+\$)=[^&]*", re.I)
_WP_SIZE = re.compile(r"-\d{2,4}x\d{2,4}(\.[a-z]{3,4})$", re.I)


def normalise(url):
    u = (url or "").split("#")[0]
    u = re.sub(r"\$[A-Za-z0-9_-]+\$", "", u)
    u = _PRESET.sub("", u)
    u = _WP_SIZE.sub(r"\1", u)
    return u.rstrip("?&").lower()


def is_canonical(a, org=""):
    """The employer-controlled headshot: the picture an ordinary searcher meets first."""
    host = (a.get("host") or "").lower()
    org_word = (org or "").lower().split()[0] if org else ""
    return a.get("context") == "corporate headshot" or bool(org_word and org_word in host)


def address_unresolved(a):
    """No image address was ever resolved — only the page that publishes it.

    Capturing such an asset is not possible: tiers A+ and A have nothing to open.
    It needs an address-resolution step first, and saying so beats logging five
    rung failures that blame the publisher for a lookup that never happened.
    """
    img = a.get("image_url_best") or a.get("image_url") or ""
    return (not img) or normalise(img) == normalise(a.get("page_url") or "")


def rank_key(a):
    """Reachability first, then independence from the employer, then size.

    The canonical employer headshot is pinned to the top. It is the most-seen
    picture in the record and the one most certain to be retrievable, so it must
    never be the asset a budget cuts — which is exactly what happened when this
    function ranked purely on independence.
    """
    host = (a.get("host") or "").lower()
    org = (a.get("_org") or "").lower()
    canonical = 0 if is_canonical(a, org) else 1
    reachable = 1 if address_unresolved(a) else 0
    independent = 0 if (org and org.split()[0] in host) else 1
    context_rank = {"corporate headshot": 0, "press": 1, "event": 1, "stage": 1,
                    "award": 2, "other": 3}.get(a.get("context"), 3)
    pixels = -(int(a.get("native_w") or 0) * int(a.get("native_h") or 0))
    return (canonical, reachable, -independent, context_rank, pixels)


def plan_subject(run_dir, slug, budget, org=""):
    man = _dfa.load_manifest(run_dir, slug)
    budget = man.get("capture_budget") or budget
    assets = man.get("assets", [])
    for a in assets:
        a["_org"] = org

    # 1. Group by normalised URL — the same headshot behind two presets is ONE asset.
    groups, gi = {}, 0
    for a in assets:
        key = normalise(a.get("image_url_best") or a.get("image_url"))
        if key not in groups:
            gi += 1
            groups[key] = "g%d" % gi
        a["dedupe_group"] = groups[key]

    # 2. Rank, then queue up to the attempt budget. One asset per dedupe group.
    ordered = sorted([a for a in assets if a.get("state") in {"candidate", "queued"}], key=rank_key)
    seen, rank = set(), 0
    for a in ordered:
        a.pop("_org", None)
        g = a["dedupe_group"]
        if g in seen:
            a["state"] = "duplicate"
            ref = next(x["id"] for x in assets if x.get("dedupe_group") == g and x.get("state") != "duplicate")
            a["reason"] = _dfa.REASONS["duplicate"].format(ref=ref)
            continue
        seen.add(g)
        rank += 1
        a["rank"] = rank
        a["address_unresolved"] = address_unresolved(a)
        if rank <= budget:
            a["state"] = "queued"
            a.setdefault("attempts", 0)
        else:
            a["state"] = "budget_capped"
            a["reason"] = _dfa.REASONS["budget_capped"].format(budget=budget)
    for a in assets:
        a.pop("_org", None)
    man["capture_budget"] = budget
    _dfa.save_manifest(run_dir, slug, man)
    return man


CAPTURE_BRIEF = """# Capture brief — {name} ({slug})

You hold the browser ALONE for this subject. Nobody else is navigating. Work the
queue below in order, one asset at a time, and stop when the queue is done or a
budget is hit. You write NO report content — only captures and state.

Queue ({n} asset(s), attempt budget {budget}, max {max_attempts} attempts / {max_minutes} minutes for this subject):
{queue}
{cdn}
## Per asset, every time
1. `simple_browser-browser_actions` → `navigate_to` the URL for the current rung,
   with a marker appended so contention is visible:  <url>{marker}
2. `get_screenshot`, then check `browserState.url` contains the marker. If it does
   NOT, another tab was selected: log `tab_mismatch` and retry ONCE.
      python scripts/log_attempt.py --run {run} --subject {slug} --asset <id> \\
        --tier <tier> --url <url> --returned <browserState.url> --outcome tab_mismatch
3. Crop and record provenance (this never enlarges):
      python scripts/capture_crop.py shot.webp {dir}/img/<id>.png \\
        --auto --source-url "<original URL>" --native <W>x<H> --tier <tier>
4. Log the attempt — the log, not your memory, is what generates the report's
   reason lines:
      python scripts/log_attempt.py --run {run} --subject {slug} --asset <id> \\
        --tier <tier> --url <url> --outcome ok --shot shots/<file>
5. `view` the cropped PNG and record the verification decision:
      python scripts/set_state.py --run {run} --subject {slug} --asset <id> \\
        verified --matched-against "<what you matched it against>"
   or `unverifiable` / `wrong_person` — each needs the same flag. A drop without
   a recorded reason is what makes photographs disappear; there is no silent drop.

## Before anything else: resolve the address
{unresolved}
An asset whose only known URL is the PAGE that publishes it has nothing for rungs
A+ or A to open. Resolve the real image address first: open the page, or run the
image search in the browser (`navigate_to https://www.bing.com/images/search?q=...`),
click the tile, and read `mediaurl=` (the true original, percent-decode it) and
`expw=`/`exph=` (the native size) out of the browser URL. Log the resolution as a
Tier D attempt. If no address can be resolved, say so with
`set_state.py ... unresolved_address` \u2014 never walk five rungs against a page URL
and report that the publishers refused.

## If the browser stops responding
      python scripts/log_attempt.py --run {run} --subject {slug} --browser-down
This closes the remaining queue as `browser_unavailable`: honest, retryable, and
explicitly NOT a finding about the hosts. A dead tool reported as "every route
refused" tells a Corporate Affairs team the press will not serve them images,
which is a false finding and worse than no finding.

## When the queue empties and attempts failed
      python scripts/plan_capture.py --run {run} --refill {slug}
The budget bounds attempts, not ambition: if several attempts failed, capped
candidates come back into the queue while the subject's allowance holds.

## The ladder — never stop at the first refusal
A+ bigger rendition from the image server · A the original image URL, full
viewport · B the search detail view (click Full screen first) · C the hosting page,
scrolled into view · D the results-grid tile.
Ask for the next rung rather than deciding to give up:
      python scripts/log_attempt.py --run {run} --subject {slug} --asset <id> --next
`exhausted` is only reachable after all five rungs are logged. A paywalled ARTICLE
is not a refused IMAGE — test the file itself. A login-walled page still has its
picture in the search index. A Tier D crop of a verified face beats an empty row.

## Verification rule for this subject
{verify_rule}

## Scope
Photographs of the subject ONLY. Never capture or crop a video thumbnail, still
frame, podcast cover, channel banner, episode card or platform screenshot — those
show a host's face or somebody else's brand. If an A/V item carries a finding,
it is already a text row in report.json.
"""


def capture_brief(run_dir, slug, run, subj, report):
    man = _dfa.load_manifest(run_dir, slug)
    q = [a for a in man["assets"] if a.get("state") == "queued"]
    lines = []
    for a in q:
        lines.append("  %-9s rank %-2s %-18s %s" % (
            a["id"], a.get("rank", "?"), (a.get("context") or "")[:18],
            a.get("image_url_best") or a.get("image_url")))
        lines.append("            page: %s" % a.get("page_url", ""))
    collisions = [r for r in (report or {}).get("first_impression", []) if r.get("class") == "wrong-person"]
    verify = ("This subject SHARES A NAME with other people (%d wrong-person result(s) in the "
              "first-impression sample). TWO independent caption-named assets must agree before "
              "any third is accepted." % len(collisions)) if collisions else (
        "Match each capture against the highest-ranked asset whose caption names the subject on an "
        "employer-owned or editorial page. If you cannot confirm the person, the state is "
        "`unverifiable` — never a guess.")
    unresolved_ids = [a["id"] for a in q if a.get("address_unresolved")]
    cdn = man.get("cdn_pattern") or run.get("cdn_pattern", "")
    return CAPTURE_BRIEF.format(
        name=subj.get("name", slug), slug=slug, run=run_dir,
        dir=os.path.join(run_dir, slug), n=len(q),
        budget=man.get("capture_budget", 8),
        max_attempts=run.get("max_attempts_per_subject", 24),
        max_minutes=run.get("max_minutes_per_subject", 12),
        queue="\n".join(lines) or "  (no queued assets — nothing to capture)",
        marker="&run=%s-<asset>-<tier>" % slug,
        unresolved=(("\n%d queued asset(s) have no resolved image address: %s\n"
                     % (len(unresolved_ids), ", ".join(unresolved_ids)))
                    if unresolved_ids else
                    "\nEvery queued asset already carries a resolved image address.\n"),
        cdn=("\n## This organisation's image server\n%s\nApply it at rung A+ before settling for the "
             "embedded rendition.\n" % cdn) if cdn else "",
        verify_rule=verify)


def refill(run_dir, slug, run):
    """Re-spend the attempt budget on capped assets when attempts failed.

    The budget bounds work, not ambition. If seven of eight attempts failed, the
    ninth candidate should still be tried while the subject's attempt allowance
    holds — leaving it `budget_capped` is how the easiest picture in the record
    ends up as a text row.
    """
    man = _dfa.load_manifest(run_dir, slug)
    rows = _dfa.read_log(run_dir, slug)
    spent = len([r for r in rows if r.get("outcome") not in _dfa.RUN_FAILURE_OUTCOMES])
    allowance = run.get("max_attempts_per_subject", 24)
    live = [a for a in man["assets"] if a.get("state") in {"queued", "capturing"}]
    if live:
        print("%s — %d asset(s) still queued; work those before refilling." % (slug, len(live)))
        return 0
    if spent >= allowance:
        print("%s — attempt allowance spent (%d of %d). Nothing refilled."
              % (slug, spent, allowance))
        return 0
    capped = sorted([a for a in man["assets"] if a.get("state") == "budget_capped"],
                    key=lambda a: a.get("rank") or 99)
    room = max(0, allowance - spent) // 3 or 1          # ~3 rungs per asset
    promoted = []
    for a in capped[:room]:
        a["state"] = "queued"
        a.pop("reason", None)
        promoted.append(a["id"])
    _dfa.save_manifest(run_dir, slug, man)
    print("%s — %d attempt(s) of %d spent; %d capped asset(s) returned to the queue: %s"
          % (slug, spent, allowance, len(promoted), ", ".join(promoted) or "none"))
    return 0


def finalize(run_dir, slug, run):
    man = _dfa.load_manifest(run_dir, slug)
    rows = _dfa.read_log(run_dir, slug)
    stuck = []
    queued = [a for a in man["assets"] if a.get("state") in {"candidate", "queued"}]
    if queued and not rows:
        print("CANNOT CLOSE %s \u2014 %d asset(s) are queued and the capture log is empty: capture has "
              "not run for this subject. Closing now would mark every photograph `budget_exhausted` "
              "and publish an empty section 7." % (slug, len(queued)))
        return 1
    for a in man["assets"]:
        st = a.get("state")
        if st == "verified":
            continue
        if st == "captured":
            stuck.append("%s: captured but never verified — run set_state.py" % a["id"])
        elif st in {"candidate", "queued"}:
            # never tried: the subject's budget ran out before it came up
            if a.get("attempts"):
                arows = [r for r in rows if r.get("asset_id") == a["id"]]
                if len({r.get("tier") for r in arows}) >= len(_dfa.LADDER):
                    a["state"] = "exhausted"
                    a["reason"] = _dfa.exhausted_reason(arows)
                else:
                    stuck.append("%s: %d attempt(s) logged but rungs remain — ask log_attempt.py --next"
                                 % (a["id"], a.get("attempts", 0)))
            elif a.get("address_unresolved") or address_unresolved(a):
                a["state"] = "unresolved_address"
                a["reason"] = _dfa.REASONS["unresolved_address"]
            else:
                a["state"] = "budget_exhausted"
                a["reason"] = _dfa.REASONS["budget_exhausted"]
        elif st == "capturing":
            stuck.append("%s: still capturing — finish it or log the failure" % a["id"])
    if stuck:
        print("CANNOT CLOSE %s — %d asset(s) not in a terminal state:" % (slug, len(stuck)))
        for s in stuck:
            print("   ** %s" % s)
        return 1
    for a in man["assets"]:
        if a.get("state") == "verified":
            a["state"] = "shown"
    _dfa.save_manifest(run_dir, slug, man)
    s = man["summary"]
    print("CLOSED %s — %d distinct found, %d verified, %d shown, budget applied: %s"
          % (slug, s["found_distinct"], s["verified"], s["shown"], s["budget_applied"]))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--brief")
    ap.add_argument("--finalize")
    ap.add_argument("--refill")
    args = ap.parse_args()

    subjects = _dfa.read_json(os.path.join(args.run, "subjects.json"))
    run = _dfa.read_json(os.path.join(args.run, "run.json"), {})
    by_slug = {s["slug"]: s for s in subjects}

    if args.finalize:
        return finalize(args.run, args.finalize, run)
    if args.refill:
        return refill(args.run, args.refill, run)
    if args.brief:
        subj = by_slug.get(args.brief, {"name": args.brief})
        report = _dfa.read_json(_dfa.report_path(args.run, args.brief), {})
        print(capture_brief(args.run, args.brief, run, subj, report))
        return 0

    budget = run.get("capture_budget", 8)
    for s in subjects:
        if not os.path.exists(_dfa.manifest_path(args.run, s["slug"])):
            print("skip %s — no assets.json yet" % s["slug"])
            continue
        man = plan_subject(args.run, s["slug"], budget, s.get("org", ""))
        q = len([a for a in man["assets"] if a.get("state") == "queued"])
        d = len([a for a in man["assets"] if a.get("state") == "duplicate"])
        c = len([a for a in man["assets"] if a.get("state") == "budget_capped"])
        print("%-24s %2d queued, %2d duplicate, %2d over budget" % (s["slug"], q, d, c))
    return 0


if __name__ == "__main__":
    sys.exit(main())
