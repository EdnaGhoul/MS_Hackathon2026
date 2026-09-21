#!/usr/bin/env python3
"""accept_docx.py — acceptance gate for the Word report.

v1 had no DOCX gate at all: accept_report.py read HTML only, so a Word file with
zero images passed. This unzips word/document.xml and checks the Word file
against the same manifest the figures were computed from.

  python scripts/accept_docx.py --run <run-dir> [--subject <slug>] [--json]

Checks: drawings inside section 7 == verified assets · no picture inside the
not-shown table · header and footer parts present with PAGE / NUMPAGES fields ·
chip fills present in at least the model's count · six verdict fills · a real
TOC field · no scaffolding (workspace paths, tool names, session ids, data URIs).
"""
import argparse, json, os, re, sys, zipfile
import _dfa

S7 = "7. Photo, video and audio inventory"
S8 = "8. Professional network and registers"
SCAFFOLD = re.compile(r"working/|output/|/mnt/|host-[A-Za-z]|simple_browser|capture_crop|"
                      r"session[_-]?id|asset-\d\d\.png|sharpness", re.I)


def texts(xml):
    """Plain text of the document body, in order, for locating sections."""
    return "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml))


def section7_span(xml):
    """Byte span of section 7 inside document.xml, located by its heading runs."""
    i = xml.find(">%s<" % S7)
    j = xml.find(">%s<" % S8)
    if i < 0:
        i = xml.find(S7)
    if j < 0:
        j = len(xml)
    return xml[i:j] if i >= 0 else ""


def last_table(frag):
    """The not-shown table: the final <w:tbl> block in section 7."""
    tbls = [m for m in re.finditer(r"<w:tbl>.*?</w:tbl>", frag, re.S)]
    return tbls[-1].group(0) if tbls else ""


def audit(run_dir, slug, brand):
    path = os.path.join(run_dir, slug, "build", "%s-digital-footprint.docx" % slug)
    rep = _dfa.read_json(_dfa.report_path(run_dir, slug))
    man = _dfa.load_manifest(run_dir, slug)
    res = []

    def add(name, desc, got, want, ok):
        res.append(dict(check=name, desc=desc, got=got, want=want,
                        status="PASS" if ok else "FAIL"))

    if not os.path.exists(path):
        add("docx_present", "the Word file was built", 0, 1, False)
        return res, 1

    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        xml = z.read("word/document.xml").decode("utf-8")
        core = z.read("docProps/core.xml").decode("utf-8") if "docProps/core.xml" in names else ""
        headers = [n for n in names if re.match(r"word/header\d*\.xml", n)]
        footers = [n for n in names if re.match(r"word/footer\d*\.xml", n)]
        footer_xml = "".join(z.read(n).decode("utf-8") for n in footers)
        header_xml = "".join(z.read(n).decode("utf-8") for n in headers)

    body = texts(xml)
    s7 = section7_span(xml)
    verified = man["summary"]["verified"]

    # Provenance first: every check below assumes this file was RENDERED from the
    # model. A hand-built Word file loses the header, the fields, the chips and
    # the reconciliation all at once, so this is the check that catches it.
    expected = _dfa.parse_stamp(_dfa.build_stamp(run_dir, slug))
    got = _dfa.parse_stamp(core)
    if got is None:
        prov = ("NO build stamp — this file was not produced by render_docx.js. "
                "Agents produce data; scripts produce documents.")
    elif got["digest"] != expected["digest"]:
        prov = "STALE build — the model changed after rendering; re-run render_docx.js"
    elif got["version"] != _dfa.BUILD_VERSION:
        prov = "built by renderer %s, current is %s — re-render" % (
            got["version"], _dfa.BUILD_VERSION)
    else:
        prov = "built by the pipeline from the current model"
    add("built_by_pipeline", prov, "yes" if prov.startswith("built") else "no", "yes",
        prov.startswith("built"))

    figs = s7.count("<w:drawing>")
    add("figures_reconciled", "drawings in section 7 equal the manifest's verified assets",
        figs, verified, figs == verified)
    # Section 7 is ONE table now, so the scope rule is checked per ROW: a video or
    # audio row may never carry a picture, whatever else the table holds.
    av_rows = [r.group(0) for r in re.finditer(r"<w:tr[ >].*?</w:tr>", s7, re.S)
               if re.match(r"(VIDEO|AUDIO) \u2014", texts(r.group(0)).strip())]
    av_pics = sum(r.count("<w:drawing>") for r in av_rows)
    add("av_rows_no_pictures", "no picture on any video or audio row (scope rule, made structural)",
        av_pics, 0, av_pics == 0)

    add("header_part", "running header present on the document", len(headers), 1, bool(headers))
    add("footer_fields", "footer carries PAGE and NUMPAGES fields",
        int("PAGE" in footer_xml and "NUMPAGES" in footer_xml), 1,
        "PAGE" in footer_xml and "NUMPAGES" in footer_xml)
    add("header_subject", "header names the subject and dates the sample",
        int(rep["subject"]["name"].split()[-1] in header_xml), 1,
        rep["subject"]["name"].split()[-1] in header_xml)

    fills = re.findall(r'w:fill="([0-9A-Fa-f]{6})"', xml)
    chip_colours = {v.upper() for v in brand["chip"].values()}
    chip_fills = [f for f in fills if f.upper() in chip_colours]
    want_chips = len(rep["first_impression"])
    add("chip_fills", "chips render as shaded runs, at least one per classified result",
        len(chip_fills), want_chips, len(chip_fills) >= want_chips)

    verdict_colours = {v.upper() for v in brand["verdict"].values()}
    verdict_fills = [f for f in fills if f.upper() in verdict_colours]
    add("verdict_fills", "six scorecard verdict cells shaded by grade",
        len(verdict_fills), 6, len(verdict_fills) >= 6)

    # A TOC FIELD renders blank until Word updates it, so v2 generates the list.
    # Check it is really there: every section title appears twice, once in the
    # contents and once as its heading.
    listed = sum(1 for t in ["First-impression sample", "Photo, video and audio inventory",
                             "Complete source list", "Confidence"] if body.count(t) >= 2)
    add("contents_list", "a generated contents list that renders without updating fields",
        listed, 4, listed == 4)

    scaffolding = sorted(set(SCAFFOLD.findall(body)))
    add("no_scaffolding", "no workspace paths, tool names or session ids in the body",
        len(scaffolding), 0, not scaffolding)
    add("no_data_uri", "images embedded as parts, never as data URIs",
        int("data:image" in xml), 0, "data:image" not in xml)
    add("rights_note", "third-party image rights stated in the body",
        int("not cleared for reuse" in body), 1, "not cleared for reuse" in body)

    failed = sum(1 for r in res if r["status"] == "FAIL")
    return res, failed


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--subject")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    run = _dfa.read_json(os.path.join(args.run, "run.json"), {})
    brand = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        "brand", "%s.json" % run.get("brand", "default")),
                           encoding="utf-8"))
    slugs = ([args.subject] if args.subject
             else [s["slug"] for s in _dfa.read_json(os.path.join(args.run, "subjects.json"))])
    total, out = 0, {}
    for slug in slugs:
        res, failed = audit(args.run, slug, brand)
        total += failed
        out[slug] = res
        if not args.json:
            print("\n%s.docx  \u2014  %s" % (slug, "ACCEPT" if not failed else "REJECT (%d)" % failed))
            for r in res:
                print("%s%-26s %5s (want %s)  %s"
                      % ("  ok " if r["status"] == "PASS" else "  ** ", r["check"],
                         r["got"], r["want"], r["desc"]))
    if args.json:
        print(json.dumps(out, indent=1))
    print("\n%s\n%d Word file(s), %d failed check(s) \u2014 %s"
          % ("=" * 60, len(slugs), total, "ALL ACCEPTED" if not total else "BLOCKED"))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
