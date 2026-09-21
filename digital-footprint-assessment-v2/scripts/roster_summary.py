#!/usr/bin/env python3
"""roster_summary.py — the cross-subject read, computed from N report.json files.

Roster-wide patterns outrank individual ones: when the same defect appears across
most of a team, the pattern IS the finding. This builds the scorecard grid, the
repeating patterns and the coverage table from the models — no agent re-types a
verdict into a summary.

  python scripts/roster_summary.py --run <run-dir> [--json]
"""
import argparse, json, os, sys
import _dfa

DIMS = ["Credibility", "Adverse material", "Distinctiveness", "Discoverability",
        "Consistency", "Momentum"]
WEAK = {"Thin", "Material", "Low", "Absent", "Diluted", "Invisible", "Inconsistent",
        "Slowing", "Dormant"}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    subjects = _dfa.read_json(os.path.join(args.run, "subjects.json"))
    grid, coverage, patterns = [], [], {}
    for s in subjects:
        rp = _dfa.report_path(args.run, s["slug"])
        if not os.path.exists(rp):
            coverage.append({"subject": s["slug"], "status": "research_failed"})
            continue
        rep = _dfa.read_json(rp)
        man = _dfa.read_json(_dfa.manifest_path(args.run, s["slug"]), {"summary": {}})
        verdicts = {r["dimension"]: r["verdict"] for r in rep["layer1"]["scorecard"]}
        grid.append(dict(subject=rep["subject"]["name"], slug=s["slug"],
                         **{d: verdicts.get(d, "?") for d in DIMS}))
        sm = man.get("summary", {})
        coverage.append({"subject": s["slug"], "found": sm.get("found_distinct", 0),
                         "shown": sm.get("shown", 0),
                         "pct": round(100.0 * sm.get("shown", 0) / sm["found_distinct"], 1)
                         if sm.get("found_distinct") else 0.0})
        for d in DIMS:
            if verdicts.get(d) in WEAK:
                patterns.setdefault(d, []).append(s["slug"])

    shared = {d: v for d, v in patterns.items() if len(v) >= max(2, int(0.6 * len(grid)))}
    out = {"subjects": len(subjects), "scorecard": grid, "coverage": coverage,
           "repeating_patterns": shared}
    _dfa.write_json(os.path.join(args.run, "roster-summary.json"), out)

    if args.json:
        print(json.dumps(out, indent=1))
        return 0
    print("%-22s %s" % ("Subject", "  ".join(d[:12].ljust(12) for d in DIMS)))
    for row in grid:
        print("%-22s %s" % (row["subject"][:22], "  ".join(str(row[d])[:12].ljust(12) for d in DIMS)))
    print("\nCoverage")
    for c in coverage:
        print("  %-22s %s" % (c["subject"],
                              c.get("status") or "%d of %d shown (%.0f%%)"
                              % (c["shown"], c["found"], c["pct"])))
    if shared:
        print("\nRepeating across the team \u2014 the pattern is the finding")
        for d, who in shared.items():
            print("  %-18s weak for %d of %d: %s" % (d, len(who), len(grid), ", ".join(who)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
