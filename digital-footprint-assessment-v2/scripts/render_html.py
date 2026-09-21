#!/usr/bin/env python3
"""render_html.py — build the self-contained HTML report from the content model.

Agents produce data; scripts produce documents. The figure list here is COMPUTED
from the asset manifest, so it cannot drift from what was captured: every
`shown` asset is embedded, every other asset becomes a row with its generated
reason. No agent writes any of this markup.

  python scripts/render_html.py --run <run-dir> --subject <slug> [--brand default]
  python scripts/render_html.py --run <run-dir> --all
"""
import argparse, base64, html, json, os, re, sys
import _dfa

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND_DIR = os.path.join(os.path.dirname(HERE), "brand")

VERDICT_GRADE = {
    "Strong": "good", "Adequate": "mid", "Thin": "bad",
    "Clean": "good", "Minor": "mid", "Material": "bad",
    "High": "good", "Moderate": "mid", "Low": "bad", "Absent": "bad",
    "Diluted": "mid", "Invisible": "bad",
    "Consistent": "good", "Mixed": "mid", "Inconsistent": "bad",
    "Rising": "good", "Steady": "mid", "Slowing": "bad", "Dormant": "bad",
}
CLASS_LABEL = {
    "company-owned": "COMPANY-OWNED", "editorial": "EDITORIAL", "sponsored": "SPONSORED",
    "aggregator": "AGGREGATOR", "auto-generated": "AUTO-GENERATED",
    "data-broker": "DATA BROKER", "wrong-person": "WRONG PERSON",
}
RIGHTS = ("all rights reserved; no licence stated. Reproduced at identification scale only "
          "— not cleared for reuse")


def e(s):
    return html.escape(str(s or ""))


def css(b):
    c = b["chip"]
    chips = "\n".join(".tag.%s{background:#%s}" % (k.lower().replace(" ", "-"), v) for k, v in c.items())
    return """
:root{--ink:#%(ink)s;--muted:#%(muted)s;--rule:#%(rule)s;--accent:#%(accent)s;--callout:#%(callout)s}
*{box-sizing:border-box}
body{font:%(size)spt/1.5 '%(font)s','%(fallback)s',system-ui,sans-serif;color:var(--ink);
 max-width:190mm;margin:0 auto;padding:18mm 14mm}
h1{font-size:22pt;margin:0 0 2mm;color:var(--accent)}
h2{font-size:13pt;margin:10mm 0 3mm;color:var(--accent);border-bottom:1px solid var(--rule);padding-bottom:1mm}
h3{font-size:11pt;margin:6mm 0 2mm}
.sub{color:var(--muted);margin:0 0 6mm}
.callout{background:var(--callout);border-left:3px solid var(--accent);padding:4mm 5mm;margin:4mm 0;font-size:12pt}
.kpis{display:flex;gap:4mm;margin:5mm 0}
.kpi{flex:1;border:1px solid var(--rule);padding:3mm;text-align:center}
.kpi .v{font-size:20pt;font-weight:700;color:var(--accent);display:block;line-height:1.1}
.kpi .l{font-size:7.5pt;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.kpi .n{font-size:8pt;color:var(--muted)}
table{border-collapse:collapse;width:100%%;margin:3mm 0;font-size:9.5pt}
th{text-align:left;background:#f4f4f4;border-bottom:1px solid var(--rule);padding:2mm;font-size:8.5pt;
 text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
td{border-bottom:1px solid var(--rule);padding:2mm;vertical-align:top}
td.src{word-break:break-all;font-size:8.5pt}
.tag{display:inline-block;color:#fff;font-size:7.5pt;font-weight:700;letter-spacing:.04em;
 padding:.5mm 2mm;border-radius:2px;white-space:nowrap;margin-right:1mm}
%(chips)s
.verdict{display:inline-block;color:#fff;font-weight:700;font-size:9pt;padding:.7mm 3mm;border-radius:2px}
.verdict.good{background:#%(good)s}.verdict.mid{background:#%(mid)s}.verdict.bad{background:#%(bad)s}
.verdict.grey{background:#%(grey)s}
blockquote{border-left:3px solid var(--rule);margin:3mm 0;padding:0 0 0 4mm;font-style:italic}
blockquote .attr{display:block;font-style:normal;font-size:9pt;color:var(--muted);margin-top:1mm}
figure{margin:0;width:50mm;break-inside:avoid}
figure img{display:block;width:100%%;height:auto;border:1px solid var(--rule)}
table.inv td{vertical-align:top}
table.inv td.pic{width:54mm}
table.inv td.nopic{width:54mm;font-size:8.5pt;color:var(--muted);font-style:italic}
table.inv .rights{font-style:italic}
ol,ul{margin:2mm 0 2mm 5mm;padding:0}
.note{font-size:9pt;color:var(--muted);margin:3mm 0}
.footer{margin-top:10mm;border-top:1px solid var(--rule);padding-top:3mm;font-size:8.5pt;color:var(--muted)}
""" % {"ink": b["ink"], "muted": b["muted"], "rule": b["rule"], "accent": b["accent"],
       "callout": b["callout_bg"], "size": b["size_body_pt"], "font": b["font_body"],
       "fallback": b["font_body_fallback"], "chips": chips,
       "good": b["verdict"]["good"], "mid": b["verdict"]["mid"],
       "bad": b["verdict"]["bad"], "grey": b["verdict"]["grey"]}


def chips_for(row):
    out = ['<span class="tag %s">%s</span>' % (row.get("tag", "FACT").lower(), e(row.get("tag", "FACT")))]
    for m in row.get("marks", []) or []:
        out.append('<span class="tag %s">%s</span>' % (m.lower().replace(" ", "-"), e(m)))
    return "".join(out)


def rows_table(rows, head="Finding"):
    if not rows:
        return '<p class="note">Not found — nothing in the public record for this section.</p>'
    out = ['<table><tr><th>Tag</th><th>%s</th><th>Source</th></tr>' % e(head)]
    for r in rows:
        extra = ""
        if r.get("date"):
            extra += " <span class=note>(%s)</span>" % e(r["date"])
        if r.get("title_used"):
            extra += "<br><span class=note>Title used on the page: %s</span>" % e(r["title_used"])
        out.append('<tr><td>%s</td><td>%s%s</td><td class="src"><a href="%s">%s</a>%s</td></tr>' % (
            chips_for(r), e(r.get("finding")), extra, e(r.get("url")), e(short(r.get("url"))),
            ("<br><span class=note>accessed %s</span>" % e(r["accessed"])) if r.get("accessed") else ""))
    out.append("</table>")
    return "".join(out)


def reason_notes(assets):
    """When several assets fail for the same reason, state it once under the table."""
    counts = {}
    for a in assets:
        if a.get("reason"):
            counts[a["reason"]] = counts.get(a["reason"], 0) + 1
    shared = [r for r, n in counts.items() if n >= 2]
    short_of = {}
    for i, r in enumerate(shared, 1):
        short_of[r] = "%d below (%d photographs)" % (i, counts[r])
    return shared, short_of


def short(url, n=44):
    u = (url or "").replace("https://", "").replace("http://", "")
    return u if len(u) <= n else u[:n - 1] + "\u2026"


TABLE_MM = 50          # picture column width in the single section-7 table
TABLE_MAX_H_MM = 55    # height ceiling, so a tall portrait cannot own the page


def _b64(path):
    with open(path, "rb") as fh:
        return base64.b64encode(fh.read()).decode("ascii")


def png_size(path):
    """PNG header: width and height are big-endian 32-bit at bytes 16 and 20."""
    with open(path, "rb") as fh:
        head = fh.read(24)
    return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")


def picture_cell(run_dir, slug, a):
    """The picture, sized to the column. Shown assets only — never an A/V item."""
    path = os.path.join(run_dir, slug, a.get("file", ""))
    w, h = png_size(path)
    width = min(TABLE_MM, a.get("placement_mm") or TABLE_MM)
    if w and h and width * (h / float(w)) > TABLE_MAX_H_MM:
        width = round(TABLE_MAX_H_MM * (w / float(h)), 1)
    return ('<figure style="width:%smm"><img src="data:image/png;base64,%s" '
            'alt="Photograph of the subject"></figure>'
            % (width, _b64(path)))


def provenance_cell(a):
    out = ["<b>%s</b>" % e(a.get("descriptive_title") or a.get("context") or a["id"])]
    if a.get("caption_verbatim"):
        t = "Published caption: \u201c%s\u201d." % e(a["caption_verbatim"].rstrip(". "))
        if a.get("title_attached"):
            t += " It attaches the title \u201c%s\u201d%s." % (
                e(a["title_attached"]), " \u2014 outdated" if a.get("title_outdated") else "")
        out.append(t)
    if a.get("host"):
        out.append("Published by %s." % e(a["host"]))
    v = a.get("verification") or {}
    if v.get("matched_against") and a.get("state") in _dfa.SHOWN_STATES:
        out.append("Visual verification: matched against %s." % e(v["matched_against"]))
    out.append('<span class="rights">%s%s</span>' % (
        ("Credit %s. " % e(a["credit"])) if a.get("credit") else "", e(a.get("licence") or RIGHTS)))
    return "<br>".join(out)


def av_cell(v):
    out = ["<b>%s \u2014 %s</b>" % (e(v["kind"]), e(v["title"]))]
    meta = " \u00b7 ".join(x for x in [e(v.get("date")), e(v.get("duration")),
                                  ("title used: \u201c%s\u201d" % e(v["title_used"]))
                                  if v.get("title_used") else ""] if x)
    if meta:
        out.append(meta)
    if v.get("on_screen"):
        out.append("On screen: %s" % e(v["on_screen"]))
    out.append(e(v["finding"]))
    if v.get("host"):
        out.append("Published by %s." % e(v["host"]))
    return "<br>".join(out)


def build(run_dir, slug, brand):
    rep = _dfa.read_json(_dfa.report_path(run_dir, slug))
    man = _dfa.load_manifest(run_dir, slug)
    s, l1, sec = rep["subject"], rep["layer1"], rep["sections"]
    p = []
    a = p.append

    a("<!doctype html><html lang=en><meta charset=utf-8>")
    # Provenance marker: proves this file came out of the pipeline, not a keyboard.
    # A comment, so no reader ever sees it and no gate can be fooled by prose.
    a("<!-- dfa-build %s -->" % _dfa.build_stamp(run_dir, slug))
    a("<title>%s — digital footprint assessment</title>" % e(s["name"]))
    a("<style>%s</style>" % css(brand))
    a("<h1>%s</h1>" % e(s["name"]))
    a('<p class="sub">%s%s · Public-record assessment — a point-in-time sample retrieved on %s</p>'
      % (e(s.get("role_verified") or ""), (" · " + e(s["org"])) if s.get("org") else "", e(s["sample_date"])))

    # ---- Layer 1
    a('<div class="callout"><b>Headline finding.</b> %s</div>' % e(l1["headline"]))
    a('<div class="kpis">')
    for k in l1["key_figures"]:
        a('<div class="kpi"><span class="v">%s</span><span class="l">%s</span><br><span class="n">%s</span></div>'
          % (e(k["value"]), e(k["label"]), e(k.get("note", ""))))
    a("</div>")
    a("<h2>What a searcher actually finds</h2><p>%s</p>" % e(" ".join(l1["searcher_finds"])))
    a("<h2>Scorecard</h2><table><tr><th>Dimension</th><th>Verdict</th><th>Evidence</th></tr>")
    for row in l1["scorecard"]:
        a('<tr><td>%s</td><td><span class="verdict %s">%s</span></td><td>%s</td></tr>'
          % (e(row["dimension"]), VERDICT_GRADE.get(row["verdict"], "grey"),
             e(row["verdict"]), e(row["evidence"])))
    a("</table>")
    a("<h2>The three fixes that would change the record</h2>")
    a("<table><tr><th>Fix</th><th>What it involves</th><th>Effort</th><th>Why it matters</th></tr>")
    for f in l1["fixes"]:
        a("<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td></tr>"
          % (e(f["title"]), e(f["what"]), e(f["effort"]), e(f["why"])))
    a("</table>")

    a('<p class="note">Sections 1 to 9 below are fact — retrieved, dated and sourced. Section 10, the theme '
      "ranking and the scorecard above are analysis drawn from those facts.</p>")

    # ---- Layer 2
    a("<h2>1. First-impression sample</h2>")
    a('<p class="note">The first screen for each query, in order, on %s. A point-in-time sample, not a '
      "ranking.</p>" % e(s["sample_date"]))
    for q in dict.fromkeys(r["query"] for r in rep["first_impression"]):
        a("<h3>Query: \u201c%s\u201d</h3>" % e(q))
        a("<table><tr><th>#</th><th>Result</th><th>Classification</th><th>Source</th></tr>")
        for r in [x for x in rep["first_impression"] if x["query"] == q]:
            a('<tr><td>%d</td><td>%s</td><td><span class="tag %s">%s</span></td>'
              '<td class="src"><a href="%s">%s</a></td></tr>'
              % (r["rank"], e(r["title"]), r["class"], e(CLASS_LABEL[r["class"]]),
                 e(r["url"]), e(short(r["url"]))))
        a("</table>")

    a("<h2>2. Career and professional background</h2>" + rows_table(sec.get("career")))
    a("<h2>3. Public profile and appearances</h2>" + rows_table(sec.get("public_profile"), "Appearance"))

    a("<h2>4. Topics and messages</h2>")
    for q in (sec.get("topics") or {}).get("quotes", []):
        a("<blockquote>\u201c%s\u201d<span class=attr>%s%s%s</span></blockquote>"
          % (e(q["text"]), e(q.get("said_where")), (", " + e(q["date"])) if q.get("date") else "",
             (' — <a href="%s">%s</a>' % (e(q["url"]), e(short(q["url"])))) if q.get("url") else ""))
    themes = (sec.get("topics") or {}).get("themes", [])
    if themes:
        a("<table><tr><th>Theme</th><th>Weight of evidence</th><th>Items</th></tr>")
        for t in themes:
            a("<tr><td>%s</td><td>%s</td><td>%s</td></tr>"
              % (e(t["theme"]), e(t.get("weight", "")), e(t.get("evidence_count", ""))))
        a("</table>")

    media = sec.get("media") or {}
    a("<h2>5. Media presence</h2>" + rows_table(media.get("coverage"), "Coverage"))
    a("<h3>Adverse, critical or disputed material</h3>")
    a(rows_table(media.get("adverse"), "Item") if media.get("adverse")
      else '<p class="note">No adverse material was found in the sources searched.</p>')
    a('<p class="note"><b>This is not a clearance.</b> The following were not searched and could hold '
      "material this assessment did not see: %s.</p>" % e("; ".join(media.get("not_covered", []))))

    ds = sec.get("digital_social") or {}
    a("<h2>6. Digital and social presence</h2><h3>Published by the subject</h3>" + rows_table(ds.get("by")))
    a("<h3>Published about the subject</h3>" + rows_table(ds.get("about")))
    if ds.get("not_assessable"):
        a("<h3>Could not be assessed</h3>" + rows_table(ds.get("not_assessable")))

    # ---- Section 7 — computed from the manifest, never from prose
    a("<h2>7. Photo, video and audio inventory</h2>")
    a("<p>%s</p>" % e(sec.get("inventory_lead")))
    # ONE inventory table: every photograph, video and audio item in the same
    # shape. A captured photograph shows its picture in the first column; every
    # other row states, in that same column, why there is no picture. A/V items
    # NEVER carry a picture \u2014 a thumbnail shows a host's face or a title card.
    shown = _dfa.shown_assets(man)
    not_shown = [x for x in _dfa.not_shown_assets(man) if x.get("state") != "not_photo"]
    av = sec.get("av_items") or []
    shared_reasons, short_of = reason_notes(not_shown)
    a('<table class="inv"><tr><th>Picture</th><th>Asset, provenance and rights</th>'
      "<th>Source</th></tr>")
    for x in shown:
        a('<tr><td class="pic">%s</td><td>%s</td><td class="src"><a href="%s">%s</a></td></tr>'
          % (picture_cell(run_dir, slug, x), provenance_cell(x),
             e(x.get("page_url")), e(short(x.get("page_url")))))
    for x in not_shown:
        label = _dfa.SHORT_REASON.get(x.get("state"), "No picture")
        note = short_of.get(x.get("reason"))
        a('<tr><td class="nopic">%s%s</td><td>%s</td><td class="src"><a href="%s">%s</a></td></tr>'
          % (e(label), (" \u2014 see note %s" % note) if note else "",
             provenance_cell(x), e(x.get("page_url")), e(short(x.get("page_url")))))
    for v in av:
        a('<tr><td class="nopic">No picture \u2014 %s item, not illustrated</td><td>%s</td>'
          '<td class="src"><a href="%s">%s</a></td></tr>'
          % (e(v["kind"].lower()), av_cell(v), e(v.get("url")), e(short(v.get("url")))))
    a("</table>")
    for i, r in enumerate(shared_reasons, 1):
        a('<p class="note">Note %d: %s.</p>' % (i, e(r)))
    sm = man["summary"]
    a('<p class="note">%d distinct photograph(s) found; %d shown; attempt budget applied: %s. %s</p>'
      % (sm["found_distinct"], sm["shown"], "yes" if sm["budget_applied"] else "no",
         RIGHTS[0].upper() + RIGHTS[1:]))

    a("<h2>8. Professional network and registers</h2>" + rows_table(sec.get("network"), "Position"))
    a("<h2>9. Title variants and naming consistency</h2>" + rows_table(sec.get("title_variants"), "Variant"))

    asm = rep["assessment"]
    a("<h2>10. Assessment</h2>")
    a("<p><b>Best known for.</b> %s</p>" % e(asm["best_known_for"]))
    a("<p><b>What someone unfamiliar concludes.</b> %s</p>" % e(asm["unfamiliar_concludes"]))
    for label, key in (("What is strong", "strong"), ("What is missing, outdated or hard to find", "gaps"),
                       ("Fixes in priority order", "fixes_ranked")):
        a("<h3>%s</h3><ul>%s</ul>" % (e(label), "".join("<li>%s</li>" % e(i) for i in asm.get(key, []))))

    a("<h2>11. Limitations</h2><ul>%s</ul>" % "".join("<li>%s</li>" % e(i) for i in rep["limitations"]))
    a("<h2>12. Complete source list</h2><ol>")
    for src in rep["sources"]:
        a('<li>%s — <a href="%s">%s</a>%s</li>'
          % (e(src["title"]), e(src["url"]), e(short(src["url"], 60)),
             (" (accessed %s)" % e(src["accessed"])) if src.get("accessed") else ""))
    a("</ol>")
    a('<h2>13. Confidence</h2><div class="callout"><b>%s.</b> %s</div>'
      % (e(rep["confidence"]["level"]), e(rep["confidence"]["statement"])))
    a('<p class="footer">%s · Public professional information only · Search visibility is a point-in-time '
      "sample retrieved on %s.</p>" % (e(s["name"]), e(s["sample_date"])))
    a("</html>")
    return "\n".join(p)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--subject")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--brand", default=None)
    args = ap.parse_args()

    run = _dfa.read_json(os.path.join(args.run, "run.json"), {})
    brand_name = args.brand or run.get("brand", "default")
    brand = json.load(open(os.path.join(BRAND_DIR, "%s.json" % brand_name), encoding="utf-8"))

    slugs = ([args.subject] if args.subject
             else [s["slug"] for s in _dfa.read_json(os.path.join(args.run, "subjects.json"))])
    for slug in slugs:
        out = os.path.join(args.run, slug, "build", "%s-digital-footprint.html" % slug)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(build(args.run, slug, brand))
        print("built %s (%.0f KB)" % (out, os.path.getsize(out) / 1024.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
