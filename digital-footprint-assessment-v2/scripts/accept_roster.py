#!/usr/bin/env python3
"""accept_roster.py — the cross-subject gate. Publish is all-or-nothing.

Runs both per-subject gates over every subject directory, then adds the check
neither of them can make: the thin subject hiding behind the batch. A uniform
defect is invisible one report at a time and obvious across ten.

  python scripts/accept_roster.py --run <run-dir> [--json]

FAILS when: a subject is missing either build file · either gate is red for any
subject · a subject's photo coverage is below half the roster median.
"""
import argparse, json, os, statistics, sys
import accept_docx, accept_report
import _dfa


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    subjects = _dfa.read_json(os.path.join(args.run, "subjects.json"))
    run = _dfa.read_json(os.path.join(args.run, "run.json"), {})
    brand = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        "brand", "%s.json" % run.get("brand", "default")),
                           encoding="utf-8"))
    rows, red = [], 0
    for s in subjects:
        slug = s["slug"]
        bdir = os.path.join(args.run, slug, "build")
        html = os.path.join(bdir, "%s-digital-footprint.html" % slug)
        docx = os.path.join(bdir, "%s-digital-footprint.docx" % slug)
        row = {"subject": slug, "html": os.path.exists(html), "docx": os.path.exists(docx),
               "html_failed": None, "docx_failed": None, "coverage": None, "status": "PASS"}
        if not (row["html"] and row["docx"]):
            row["status"] = "FAIL"
            row["note"] = "missing build file(s) — a batch that silently drops one person is the failure mode"
            red += 1
            rows.append(row)
            continue
        _, hf = accept_report.audit(args.run, slug)
        _, df = accept_docx.audit(args.run, slug, brand)
        man = _dfa.load_manifest(args.run, slug)
        sm = man["summary"]
        row["html_failed"], row["docx_failed"] = hf, df
        row["found"] = sm["found_distinct"]
        row["shown"] = sm["shown"]
        row["coverage"] = round(100.0 * sm["shown"] / sm["found_distinct"], 1) if sm["found_distinct"] else 0.0
        if hf or df:
            row["status"] = "FAIL"
            row["note"] = "acceptance gate red (%d HTML, %d DOCX)" % (hf, df)
            red += 1
        rows.append(row)

    # DISCOVERY outliers, checked before coverage. Coverage is shown/found, so a
    # subject whose research recorded only one candidate scores 100% and sails
    # through every other check — the "2 documented and 2 shown" trap. Against a
    # roster you can see it: when the team median is four candidates and one
    # executive has one, the shortfall is in DISCOVERY, not capture.
    founds = [r["found"] for r in rows if r.get("found")]
    fmedian = statistics.median(founds) if founds else 0.0
    for r in rows:
        if r.get("found") is None or not fmedian:
            continue
        if r["found"] < max(2, fmedian / 2.0):
            r["status"] = "WARN" if r["status"] == "PASS" else r["status"]
            r["discovery_note"] = (
                "only %d photograph candidate(s) recorded against a roster median of %.0f — "
                "this subject's coverage of %.0f%% is measured against a suspiciously short "
                "inventory, so re-run discovery before trusting it"
                % (r["found"], fmedian, r["coverage"] or 0))

    covs = [r["coverage"] for r in rows if r["coverage"] is not None]
    median = statistics.median(covs) if covs else 0.0
    for r in rows:
        if r["coverage"] is None or not median or r["coverage"] >= median / 2.0:
            continue
        # An outlier is always SURFACED — that is the point of the check. Whether
        # it BLOCKS depends on whose fault it is: a subject whose photographs were
        # genuinely refused by their hosts is a finding about that person's record,
        # and holding nine finished reports hostage to it helps nobody. A subject
        # whose capture failed on our side is a run to redo.
        man = _dfa.load_manifest(args.run, r["subject"])
        ours = [a["id"] for a in man["assets"] if a.get("state") in _dfa.RUN_FAILURE]
        if ours:
            r["status"] = "FAIL"
            r["note"] = ("coverage %.0f%% against a roster median of %.0f%%, and %d asset(s) failed on "
                         "our side (%s) — re-run this subject's capture before publishing"
                         % (r["coverage"], median, len(ours), ", ".join(ours[:4])))
            red += 1
        else:
            r["status"] = "WARN"
            r["note"] = ("coverage %.0f%% against a roster median of %.0f%% — every failure reached a "
                         "host, so this is a thin visual record, not a failed run. Say so in the chat "
                         "summary rather than leaving it to be noticed"
                         % (r["coverage"], median))
            r["outlier"] = True

    warns = [r for r in rows if r["status"] == "WARN"]
    out = {"subjects": len(rows), "median_coverage": median, "red": red,
           "flagged": [r["subject"] for r in warns], "rows": rows,
           "publish": "ALLOWED" if not red else "BLOCKED"}
    if args.json:
        print(json.dumps(out, indent=1))
    else:
        print("Roster gate — %d subject(s), median coverage %.0f%%" % (len(rows), median))
        print("-" * 72)
        for r in rows:
            print("%-6s %-22s html:%-5s docx:%-5s photos:%-7s coverage:%s"
                  % (r["status"], r["subject"], r["html_failed"], r["docx_failed"],
                     "%s of %s" % (r.get("shown", "?"), r.get("found", "?")),
                     "%.0f%%" % r["coverage"] if r["coverage"] is not None else "n/a"))
            if r.get("note"):
                print("       ** %s" % r["note"])
            if r.get("discovery_note"):
                print("       ** %s" % r["discovery_note"])
        if founds:
            print("\nDiscovery across the roster: %d photograph(s) recorded for %d subject(s), "
                  "median %.0f each." % (sum(founds), len(founds), fmedian))
            if fmedian < 3:
                print("       ** A median under three candidates for public-company executives is low. "
                      "Before accepting it, confirm discovery actually ran: image search per subject, "
                      "plus captions from retrieved pages. A short inventory makes every coverage "
                      "number look perfect.")
        if warns:
            print("\n%d subject(s) flagged as thin but publishable — name them in the chat summary: %s"
                  % (len(warns), ", ".join(r["subject"] for r in warns)))
        print("\nPublish: %s" % out["publish"])
    return 1 if red else 0


if __name__ == "__main__":
    sys.exit(main())
