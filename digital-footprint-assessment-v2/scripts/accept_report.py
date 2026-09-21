#!/usr/bin/env python3
"""accept_report.py — acceptance gate for the HTML report.

v1 checked that the report CONTAINED things (>= 1 photograph, >= 10 chips). v2
reconciles the document against the model it was built from: the figures must
equal the manifest's verified count, and the chip, pill and classification
counts must equal the counts in report.json. A renderer that drops a label is
caught here rather than by eye.

  python scripts/accept_report.py --run <run-dir> [--subject <slug>] [--json]

Exit 1 on any FAIL. A REJECT blocks delivery — fix and re-run, never publish
and mention it.
"""
import argparse, json, os, re, sys
import _dfa

S7_START = "7. Photo, video and audio inventory"
S7_END = "8. Professional network and registers"


def _between(b, start, end):
    i, j = b.find(start), b.find(end)
    return b[i:j] if i >= 0 and j > i else ""


def _section1(b):
    return _between(b, "1. First-impression sample", "2. Career and professional background")


def _section7(b):
    return _between(b, S7_START, S7_END)


def _s7table(b):
    s = _section7(b)
    i = s.find("<table")
    return s[i:] if i >= 0 else ""


def _sourcelist(b):
    i = b.find("12. Complete source list")
    return b[i:] if i >= 0 else ""


def model_counts(rep):
    """What the CONTENT MODEL says the document must carry."""
    sec = rep["sections"]
    rows = []
    for key in ("career", "public_profile", "network", "title_variants"):
        rows += sec.get(key) or []
    for key in ("coverage", "adverse"):
        rows += (sec.get("media") or {}).get(key) or []
    for key in ("by", "about", "not_assessable"):
        rows += (sec.get("digital_social") or {}).get(key) or []
    return {
        "tags": len(rows),
        "marks": sum(len(r.get("marks") or []) for r in rows),
        "classifications": len(rep["first_impression"]),
        "pills": len(rep["layer1"]["scorecard"]),
        "quotes": len((sec.get("topics") or {}).get("quotes") or []),
        "sources": len({s["url"] for s in rep["sources"]}),
    }


def audit(run_dir, slug):
    html_path = os.path.join(run_dir, slug, "build", "%s-digital-footprint.html" % slug)
    rep = _dfa.read_json(_dfa.report_path(run_dir, slug))
    man = _dfa.load_manifest(run_dir, slug)
    raw = open(html_path, encoding="utf-8").read()
    b = re.sub(r"<style.*?</style>", "", raw, flags=re.S)
    b = re.sub(r"data:image/[^\"')]+", "data:image/EMBED", b)
    m = model_counts(rep)
    res = []

    def add(name, desc, got, want, ok=None):
        res.append(dict(check=name, desc=desc, got=got, want=want,
                        status="PASS" if (ok if ok is not None else got >= want) else "FAIL"))

    # --- provenance: was this document BUILT by the pipeline, or written by hand?
    # Every other check here assumes the document was rendered from the model, so
    # a hand-written report can satisfy all of them with no manifest behind it —
    # which is exactly how a roster run silently loses its reconciliation.
    expected = _dfa.parse_stamp(_dfa.build_stamp(run_dir, slug))
    got = _dfa.parse_stamp(raw)
    if got is None:
        detail = ("NO build stamp — this file was not produced by render_html.py. "
                  "Agents produce data; scripts produce documents.")
    elif got["digest"] != expected["digest"]:
        detail = "STALE build — the model changed after rendering; re-run render_html.py"
    elif got["version"] != _dfa.BUILD_VERSION:
        detail = "built by renderer %s, current is %s — re-render" % (
            got["version"], _dfa.BUILD_VERSION)
    else:
        detail = "built by the pipeline from the current model"
    ok_prov = detail.startswith("built")
    res.append(dict(check="built_by_pipeline", desc=detail,
                    got="yes" if ok_prov else "no", want="yes",
                    status="PASS" if ok_prov else "FAIL"))

    # --- reconciliation: the checks v1 did not have
    figs = _section7(b).count("<figure")   # one per shown photograph, inside the inventory table
    add("photographs_reconciled",
        "every verified photograph appears exactly once as a figure in section 7",
        figs, man["summary"]["verified"], figs == man["summary"]["verified"])

    stuck = [a["id"] for a in man["assets"] if a.get("state") in _dfa.NON_TERMINAL
             and a.get("state") != "verified"]
    add("asset_terminal_states", "no asset left pending or unknown at publish",
        len(stuck), 0, not stuck)

    # Coverage: reconciliation alone cannot tell a thin record from a failed run.
    # A document that honestly reports 1 of 9 still passes every other check here,
    # so this is the check that stops a broken run being published as a finding.
    sm = man["summary"]
    cov = (sm["shown"] / sm["found_distinct"]) if sm["found_distinct"] else 1.0
    run_failed = [a["id"] for a in man["assets"] if a.get("state") in _dfa.RUN_FAILURE]
    coverage_ok = not (cov < 0.5 and run_failed)
    res.append(dict(check="coverage_not_run_failure",
                    desc=("photo coverage is limited by the web, not by this run "
                          "(%d of %d shown; %d asset(s) closed as retryable: %s)"
                          % (sm["shown"], sm["found_distinct"], len(run_failed),
                             ", ".join(run_failed[:4]) or "none")),
                    got="%.0f%%" % (cov * 100), want=">=50% unless every failure reached a host",
                    status="PASS" if coverage_ok else "FAIL"))

    missing_reason = [a["id"] for a in _dfa.not_shown_assets(man)
                      if a.get("state") != "not_photo" and not a.get("reason")]
    add("not_shown_reasons", "every non-shown photograph carries a machine-generated reason",
        len(missing_reason), 0, not missing_reason)

    got_tags = len(re.findall(r'class="tag (?:fact|flag)"', b))
    add("structure_from_model_tags", "FACT / FLAG chips in the document equal the rows in the model",
        got_tags, m["tags"], got_tags == m["tags"])
    got_marks = len(re.findall(r'class="tag (?:single-source|not-verified)"', b))
    add("structure_from_model_marks", "SINGLE-SOURCE / NOT VERIFIED chips equal the model's marks",
        got_marks, m["marks"], got_marks == m["marks"])
    got_cls = len(re.findall(r'class="tag ', _section1(b)))
    add("structure_from_model_classes",
        "every first-impression result carries its classification chip",
        got_cls, m["classifications"], got_cls == m["classifications"])
    got_pills = len(re.findall(r'class="verdict ', b))
    add("verdict_pills", "all six scorecard verdicts render as graded pills",
        got_pills, m["pills"], got_pills == m["pills"])

    # --- unchanged v1 checks
    add("unique_urls", "distinct source URLs carried inline",
        len(set(re.findall(r'https?://[^\s"<)]+', b))), 25)
    add("listed_sources", "entries in the complete source list",
        len(set(re.findall(r'https?://[^\s"<)]+', _sourcelist(b)))), 25)
    add("table_rows", "evidence rows (findings itemised, not dissolved into prose)", b.count("<tr"), 40)
    add("words", "body length", len(re.sub(r"<[^>]+>", " ", b).split()), 2500)
    add("verbatim_quotes", "verbatim attributable quotes", b.count("<blockquote"), 1)
    add("photo_provenance", "shown photographs carrying a verification statement",
        len(re.findall(r"Visual verification", _section7(b))), man["summary"]["verified"],
        len(re.findall(r"Visual verification", _section7(b))) >= man["summary"]["verified"])
    # Section 7 is one table, so the A/V scope rule is a per-ROW check.
    av_rows = [r for r in re.findall(r"<tr>.*?</tr>", _s7table(b), re.S)
               if re.search(r"<b>(VIDEO|AUDIO) ", r)]
    av_pics = sum(r.count("data:image") for r in av_rows)
    add("av_no_pictures", "no picture on any video or audio row (scope rule)",
        av_pics, 0, av_pics == 0)
    add("inventory_single_table",
        "photographs, video and audio share one inventory table in section 7",
        _section7(b).count("<table"), 1, _section7(b).count("<table") == 1)
    add("no_quality_internals",
        "capture internals kept out of the artefact (tiers, sharpness, PASS/WARN, paths)",
        len(re.findall(r"sharpness \d|[Tt]ier [A-D]|PASS/WARN|working/|/mnt/", _section7(b))), 0,
        not re.search(r"sharpness \d|[Tt]ier [A-D]|PASS/WARN|working/|/mnt/", _section7(b)))

    for name, desc, pat in [
        ("bounded_clearance", "adverse-material finding bounded by what was NOT searched",
         r"not\s+searched|not a clearance"),
        ("point_in_time", "search visibility dated as a point-in-time sample", r"point[- ]in[- ]time"),
        ("fact_analysis_split", "fact vs analysis visibly separated", r"are analysis|analysis drawn from"),
        ("rights_note", "third-party image rights stated", r"rights reserved|not cleared for reuse"),
    ]:
        ok = re.search(pat, b, re.I) is not None
        add(name, desc, int(ok), 1, ok)

    failed = sum(1 for r in res if r["status"] == "FAIL")
    return res, failed


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--subject")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    slugs = ([args.subject] if args.subject
             else [s["slug"] for s in _dfa.read_json(os.path.join(args.run, "subjects.json"))])
    total, out = 0, {}
    for slug in slugs:
        res, failed = audit(args.run, slug)
        total += failed
        out[slug] = res
        if not args.json:
            print("\n%s  \u2014  %s" % (slug, "ACCEPT" if not failed else "REJECT (%d)" % failed))
            for r in res:
                print("%s%-30s %5s (want %s)  %s"
                      % ("  ok " if r["status"] == "PASS" else "  ** ", r["check"],
                         r["got"], r["want"], r["desc"]))
    if args.json:
        print(json.dumps(out, indent=1))
    print("\n%s\n%d report(s), %d failed check(s) \u2014 %s"
          % ("=" * 60, len(slugs), total, "ALL ACCEPTED" if not total else "BLOCKED"))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
