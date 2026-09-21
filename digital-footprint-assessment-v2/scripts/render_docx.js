#!/usr/bin/env node
/**
 * render_docx.js — build the Word report from the same content model the HTML
 * renderer uses. docx-js only; no agent ever hand-writes Word content.
 *
 *   NODE_PATH=/usr/lib/node_modules node scripts/render_docx.js --run <dir> --subject <slug>
 *   NODE_PATH=/usr/lib/node_modules node scripts/render_docx.js --run <dir> --all
 *
 * Every `shown` asset in assets.json becomes a figure. The figure list is
 * computed here, so the Word file cannot show fewer photographs than were
 * captured — that mismatch is what accept_docx.py fails on.
 */
const fs = require("fs");
const path = require("path");
const D = require("docx");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
  ExternalHyperlink, TableOfContents, Header, Footer, PageNumber, AlignmentType,
  BorderStyle, WidthType, ShadingType, HeadingLevel, TabStopType, convertMillimetersToTwip,
} = D;

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const RUN = opt("--run");
const ALL = args.includes("--all");
const ONE = opt("--subject");
if (!RUN) { console.error("--run <run-dir> is required"); process.exit(2); }

const readJson = (p) => JSON.parse(fs.readFileSync(p, "utf8"));
const runCfg = fs.existsSync(path.join(RUN, "run.json")) ? readJson(path.join(RUN, "run.json")) : {};
const BRAND = readJson(path.join(__dirname, "..", "brand",
  (opt("--brand", runCfg.brand || "default")) + ".json"));

const NONE = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const NO_BORDERS = { top: NONE, bottom: NONE, left: NONE, right: NONE,
                     insideHorizontal: NONE, insideVertical: NONE };
const HAIR = { style: BorderStyle.SINGLE, size: 2, color: BRAND.rule };
const GRID = { top: HAIR, bottom: HAIR, left: NONE, right: NONE,
               insideHorizontal: HAIR, insideVertical: NONE };
const BODY = Math.round(BRAND.size_body_pt * 2);        // half-points
const FONT = BRAND.font_body;
const RIGHTS = "all rights reserved; no licence stated. Reproduced at identification scale only \u2014 not cleared for reuse";

const SECTION_TITLES = [
  "First-impression sample", "Career and professional background",
  "Public profile and appearances", "Topics and messages", "Media presence",
  "Digital and social presence", "Photo, video and audio inventory",
  "Professional network and registers", "Title variants and naming consistency",
  "Assessment", "Limitations", "Complete source list", "Confidence",
];

// When several assets fail for the SAME reason, the full sentence is stated once
// beneath the table and the rows carry its short form. Six identical five-line
// blocks read as a wall and hide the one row that differs.
const SHORT_REASON = {
  duplicate: "Duplicate \u2014 the same photograph as another row",
  not_photo: "Not a photograph of the subject",
  budget_capped: "Not attempted \u2014 capture budget reached",
  budget_exhausted: "Not attempted \u2014 subject budget reached",
  unverifiable: "Face not identifiable at any size reached",
  wrong_person: "Inspected \u2014 WRONG PERSON, discarded",
  exhausted: "Every route to the file refused",
  browser_unavailable: "Not tested \u2014 the browser became unavailable",
  unresolved_address: "No image address could be resolved",
};

function reasonNotes(assets) {
  const counts = {};
  assets.forEach((a) => { if (a.reason) counts[a.reason] = (counts[a.reason] || 0) + 1; });
  const shared = Object.keys(counts).filter((r) => counts[r] >= 2);
  const shortOf = {};
  shared.forEach((r, i) => { shortOf[r] = (i + 1) + " below (" + counts[r] + " photographs)"; });
  return { shared, shortOf };
}

const VERDICT_GRADE = {
  Strong: "good", Adequate: "mid", Thin: "bad", Clean: "good", Minor: "mid", Material: "bad",
  High: "good", Moderate: "mid", Low: "bad", Absent: "bad", Diluted: "mid", Invisible: "bad",
  Consistent: "good", Mixed: "mid", Inconsistent: "bad", Rising: "good", Steady: "mid",
  Slowing: "bad", Dormant: "bad",
};
const CLASS_LABEL = {
  "company-owned": "COMPANY-OWNED", editorial: "EDITORIAL", sponsored: "SPONSORED",
  aggregator: "AGGREGATOR", "auto-generated": "AUTO-GENERATED", "data-broker": "DATA BROKER",
  "wrong-person": "WRONG PERSON",
};

// ---------------------------------------------------------------- primitives
const text = (t, o = {}) => new TextRun({ text: String(t == null ? "" : t), font: FONT,
  size: o.size || BODY, bold: o.bold, italics: o.italics, color: o.color || BRAND.ink,
  shading: o.fill ? { type: ShadingType.SOLID, color: o.fill, fill: o.fill } : undefined });

const para = (children, o = {}) => new Paragraph({
  children: Array.isArray(children) ? children : [children],
  spacing: { before: o.before || 0, after: o.after == null ? 80 : o.after },
  alignment: o.align, keepNext: o.keepNext, keepLines: true, widowControl: true });

const p = (t, o = {}) => para([text(t, o)], o);

let TIGHT = false;   // set per document when Layer 1 is dense
const h = (t, level) => new Paragraph({
  children: [text(t, { bold: true, size: level === 1 ? 26 : (level === 2 ? 24 : 21),
                       color: BRAND.accent })],
  heading: level === 1 ? HeadingLevel.HEADING_1 : (level === 2 ? HeadingLevel.HEADING_2 : HeadingLevel.HEADING_3),
  spacing: { before: (level === 1 ? 240 : 200) * (TIGHT ? 0.4 : 1), after: TIGHT ? 50 : 100 },
  keepNext: true, keepLines: true, widowControl: true });

// A chip is a shaded RUN: bold white text on the token colour. This is what the
// DOCX gate counts, and why a renderer cannot quietly drop a label.
const chip = (label) => text(" " + label + " ",
  { bold: true, size: 15, color: "FFFFFF", fill: BRAND.chip[label] || BRAND.chip.FACT });

const link = (url, label) => new ExternalHyperlink({
  children: [new TextRun({ text: label || shortUrl(url), style: "Hyperlink", font: FONT, size: 16 })],
  link: url });

function shortUrl(u, n = 40) {
  const s = String(u || "").replace(/^https?:\/\//, "");
  return s.length <= n ? s : s.slice(0, n - 1) + "\u2026";
}

const cell = (children, o = {}) => new TableCell({
  children: Array.isArray(children) ? children : [children],
  width: o.width ? { size: o.width, type: WidthType.PERCENTAGE } : undefined,
  shading: o.fill ? { type: ShadingType.SOLID, color: o.fill, fill: o.fill } : undefined,
  margins: { top: 60, bottom: 60, left: 80, right: 80 },
  verticalAlign: o.valign });

const table = (rows, o = {}) => new Table({
  rows, width: { size: 100, type: WidthType.PERCENTAGE },
  borders: o.borders || GRID, layout: D.TableLayoutType.FIXED, columnWidths: o.columnWidths });

const headerRow = (labels) => new TableRow({
  tableHeader: true, cantSplit: true,
  children: labels.map((l) => cell(p(l, { bold: true, size: 15, color: BRAND.muted, after: 0 }),
    { fill: "F2F2F2" })) });

// ------------------------------------------------------------- evidence rows
function evidenceTable(rows, headLabel) {
  if (!rows || !rows.length) {
    return [p("Not found \u2014 nothing in the public record for this section.",
      { italics: true, color: BRAND.muted })];
  }
  const trs = [headerRow(["Tag", headLabel || "Finding", "Source"])];
  rows.forEach((r) => {
    const tags = [chip(r.tag || "FACT")];
    (r.marks || []).forEach((m) => { tags.push(text(" ")); tags.push(chip(m)); });
    const body = [para([text(r.finding)], { after: 0 })];
    if (r.date) body.push(p(r.date, { size: 15, color: BRAND.muted, after: 0 }));
    if (r.title_used) body.push(p("Title used on the page: \u201c" + r.title_used + "\u201d",
      { size: 15, color: BRAND.muted, after: 0 }));
    const src = [para([link(r.url)], { after: 0 })];
    if (r.accessed) src.push(p("accessed " + r.accessed, { size: 14, color: BRAND.muted, after: 0 }));
    trs.push(new TableRow({ cantSplit: true,
      children: [cell(para(tags, { after: 0 }), { width: 16 }), cell(body, { width: 56 }),
                 cell(src, { width: 28 })] }));
  });
  return [table(trs, { columnWidths: [1600, 5600, 2800] }), p("", { after: 120 })];
}

// ------------------------------------------------------------------- section 7
const TABLE_MM = 50;   // picture column width in the single inventory table
const TABLE_MAX_H_MM = 55;   // and a height ceiling, so a tall portrait cannot own a page

function pngSize(file) {
  // PNG header: width and height are big-endian 32-bit at bytes 16 and 20.
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

function pictureCell(dir, a) {
  const file = path.join(dir, a.file);
  const d = pngSize(file);
  let mm = Math.min(TABLE_MM, a.placement_mm || TABLE_MM);
  if (mm * (d.h / d.w) > TABLE_MAX_H_MM) mm = TABLE_MAX_H_MM * (d.w / d.h);
  const px = Math.round((mm / 25.4) * 96);
  return cell([para([new ImageRun({ data: fs.readFileSync(file), type: "png",
    transformation: { width: px, height: Math.round(px * (d.h / d.w)) } })], { after: 0 })],
    { width: 30 });
}

function noPictureCell(label) {
  return cell(p(label, { size: 16, italics: true, color: BRAND.muted, after: 0 }), { width: 30 });
}

function provenanceCell(a) {
  const kids = [p(a.descriptive_title || a.context || a.id, { bold: true, after: 40 })];
  if (a.caption_verbatim) {
    let t = "Published caption: \u201c" + a.caption_verbatim.replace(/[. ]+$/, "") + "\u201d.";
    if (a.title_attached) {
      t += " It attaches the title \u201c" + a.title_attached + "\u201d" +
        (a.title_outdated ? " \u2014 outdated" : "") + ".";
    }
    kids.push(p(t, { size: 16, color: BRAND.muted, after: 30 }));
  }
  if (a.host) kids.push(p("Published by " + a.host + ".", { size: 16, color: BRAND.muted, after: 30 }));
  if (a.verification && a.verification.matched_against &&
      (a.state === "shown" || a.state === "verified")) {
    kids.push(p("Visual verification: matched against " + a.verification.matched_against + ".",
      { size: 16, color: BRAND.muted, after: 30 }));
  }
  kids.push(p((a.credit ? "Credit " + a.credit + ". " : "") + (a.licence || RIGHTS),
    { size: 16, italics: true, color: BRAND.muted, after: 0 }));
  return cell(kids, { width: 50 });
}

function avCell(v) {
  const meta = [v.date, v.duration, v.title_used ? "title used: \u201c" + v.title_used + "\u201d" : null]
    .filter(Boolean).join(" \u00b7 ");
  const kids = [p(v.kind + " \u2014 " + v.title, { bold: true, after: 40 })];
  if (meta) kids.push(p(meta, { size: 16, color: BRAND.muted, after: 30 }));
  if (v.on_screen) kids.push(p("On screen: " + v.on_screen, { size: 16, color: BRAND.muted, after: 30 }));
  kids.push(p(v.finding, { size: 16, color: BRAND.muted, after: 30 }));
  if (v.host) kids.push(p("Published by " + v.host + ".", { size: 16, color: BRAND.muted, after: 0 }));
  return cell(kids, { width: 50 });
}

const srcCell = (url) => cell([para([link(url)], { after: 0 })], { width: 20 });

// ------------------------------------------------------------------- document
function buildStamp(dir, slug, man) {
  // Mirror of _dfa.build_stamp: a digest of the two contract files as this
  // renderer read them. It rides in the document's core properties, never in
  // the body, so a reader never meets it and the gate cannot be talked out of it.
  const h = require("crypto").createHash("sha256");
  h.update(fs.readFileSync(path.join(dir, "report.json")));
  h.update(fs.readFileSync(path.join(dir, "assets.json")));
  const sm = man.summary || {};
  return "dfa2-1 " + slug + " " + h.digest("hex").slice(0, 16) +
    " shown=" + (sm.shown || 0) + "/" + (sm.found_distinct || 0);
}

function buildDoc(slug) {
  const dir = path.join(RUN, slug);
  const rep = readJson(path.join(dir, "report.json"));
  const man = readJson(path.join(dir, "assets.json"));
  const s = rep.subject, l1 = rep.layer1, sec = rep.sections;
  const shown = man.assets.filter((a) => a.state === "shown" || a.state === "verified")
    .sort((a, b) => (a.rank || 99) - (b.rank || 99));
  const notShown = man.assets.filter((a) => !["shown", "verified", "not_photo"].includes(a.state))
    .sort((a, b) => (a.rank || 99) - (b.rank || 99));
  const body = [];

  // The card must stand alone on ONE page. Long scorecard evidence and long
  // fixes push it over, so the tiles and those two tables shrink a notch when
  // the content is dense. Measured from the model, not guessed at by eye.
  const dense = (l1.searcher_finds.join(" ") + l1.scorecard.map((r) => r.evidence).join("") +
    l1.fixes.map((f) => f.what + f.why).join("")).length > 1900;
  const kpiSize = dense ? 34 : 56;
  const cardSize = dense ? 17 : BODY;
  TIGHT = dense;

  // ---- Layer 1
  body.push(h(s.name, 1));
  body.push(p([s.role_verified, s.org].filter(Boolean).join(" \u00b7 ") +
    " \u00b7 Public-record assessment \u2014 a point-in-time sample retrieved on " + s.sample_date,
    { color: BRAND.muted, size: 17, after: dense ? 80 : 200 }));

  body.push(table([new TableRow({
    children: [cell([para([text("Headline finding. ", { bold: true }), text(l1.headline)])],
      { fill: BRAND.callout_bg })] })], { borders: NO_BORDERS }));
  body.push(p("", { after: dense ? 60 : 160 }));

  body.push(table([new TableRow({
    children: l1.key_figures.map((k) => cell([
      p(k.value, { bold: true, size: kpiSize, color: BRAND.accent, align: AlignmentType.CENTER, after: 0 }),
      p(String(k.label).toUpperCase(), { size: 17, color: BRAND.muted, align: AlignmentType.CENTER, after: 0 }),
      p(k.note || "", { size: 16, color: BRAND.muted, align: AlignmentType.CENTER, after: 0 }),
    ], { width: 25 })) })], { borders: NO_BORDERS }));
  body.push(p("", { after: dense ? 60 : 160 }));

  body.push(h("What a searcher actually finds", 2));
  body.push(p(l1.searcher_finds.join(" "), { size: cardSize }));

  body.push(h("Scorecard", 2));
  body.push(table([headerRow(["Dimension", "Verdict", "Evidence"])].concat(
    l1.scorecard.map((r) => new TableRow({ cantSplit: true, children: [
      cell(p(r.dimension, { after: 0, size: cardSize }), { width: 22 }),
      cell(p(r.verdict, { bold: true, color: "FFFFFF", after: 0, size: cardSize }),
        { width: 18, fill: BRAND.verdict[VERDICT_GRADE[r.verdict] || "grey"] }),
      cell(p(r.evidence, { after: 0, size: cardSize }), { width: 60 }),
    ] }))), { columnWidths: [2200, 1800, 6000] }));

  // Dense cards cannot hold the fixes table as well. Rather than let it split
  // two-and-one across a page boundary, give it the next page whole and at full
  // size: page 1 is the card at a glance, page 2 is what to do about it.
  if (dense) { body.push(new Paragraph({ children: [new D.PageBreak()] })); TIGHT = false; }
  body.push(h("The three fixes that would change the record", 2));
  body.push(table([headerRow(["Fix", "What it involves", "Effort", "Why it matters"])].concat(
    l1.fixes.map((f, i) => new TableRow({ cantSplit: true, children: [
      cell(p((i + 1) + ". " + f.title, { bold: true, after: 0 }), { width: 22 }),
      cell(p(f.what, { after: 0 }), { width: 38 }),
      cell(p(f.effort, { after: 0 }), { width: 10 }),
      cell(p(f.why, { after: 0 }), { width: 30 }),
    ] }))), { columnWidths: [2200, 3800, 1000, 3000] }));

  body.push(p("Sections 1 to 9 are fact \u2014 retrieved, dated and sourced. Section 10, the theme ranking " +
    "and the scorecard above are analysis drawn from those facts.",
    { italics: true, size: 16, color: BRAND.muted, before: dense ? 60 : 160 }));

  // ---- TOC, then Layer 2 on a new page
  // A generated contents LIST, not a TOC field. A field renders blank until Word
  // is asked to update it, so a PDF, a LibreOffice render or a reader who clicks
  // "no" gets an empty page where the contents should be.
  body.push(h("Contents", 2));
  SECTION_TITLES.forEach((t, i) => body.push(new Paragraph({
    tabStops: [{ type: TabStopType.RIGHT, position: convertMillimetersToTwip(168), leader: "dot" }],
    children: [text((i + 1) + ".  " + t)], spacing: { after: 40 } })));
  body.push(new Paragraph({ children: [new D.PageBreak()] }));

  body.push(h("1. First-impression sample", 2));
  body.push(p("The first screen for each query, in order, on " + s.sample_date +
    ". A point-in-time sample, not a ranking.", { italics: true, color: BRAND.muted }));
  [...new Set(rep.first_impression.map((r) => r.query))].forEach((q) => {
    body.push(h("Query: \u201c" + q + "\u201d", 3));
    body.push(table([headerRow(["#", "Result", "Classification", "Source"])].concat(
      rep.first_impression.filter((r) => r.query === q).map((r) => new TableRow({
        cantSplit: true, children: [
          cell(p(String(r.rank), { after: 0 }), { width: 6 }),
          cell(p(r.title, { after: 0 }), { width: 44 }),
          cell(para([chip(CLASS_LABEL[r.class])], { after: 0 }), { width: 22 }),
          cell(para([link(r.url)], { after: 0 }), { width: 28 }),
        ] }))), { columnWidths: [600, 4400, 2200, 2800] }));
    body.push(p("", { after: 120 }));
  });

  body.push(h("2. Career and professional background", 2));
  evidenceTable(sec.career).forEach((x) => body.push(x));
  body.push(h("3. Public profile and appearances", 2));
  evidenceTable(sec.public_profile, "Appearance").forEach((x) => body.push(x));

  body.push(h("4. Topics and messages", 2));
  ((sec.topics || {}).quotes || []).forEach((q) => {
    body.push(new Paragraph({
      children: [text("\u201c" + q.text + "\u201d", { italics: true })],
      indent: { left: convertMillimetersToTwip(6) },
      border: { left: { style: BorderStyle.SINGLE, size: 12, color: BRAND.rule, space: 8 } },
      spacing: { before: 100, after: 20 }, keepLines: true }));
    body.push(new Paragraph({
      children: [text([q.said_where, q.date].filter(Boolean).join(", "),
        { size: 17, color: BRAND.muted })],
      indent: { left: convertMillimetersToTwip(6) }, spacing: { after: 120 } }));
  });
  const themes = (sec.topics || {}).themes || [];
  if (themes.length) {
    body.push(table([headerRow(["Theme", "Weight of evidence", "Items"])].concat(
      themes.map((t) => new TableRow({ cantSplit: true, children: [
        cell(p(t.theme, { after: 0 }), { width: 60 }),
        cell(p(String(t.weight == null ? "" : t.weight), { after: 0 }), { width: 20 }),
        cell(p(String(t.evidence_count == null ? "" : t.evidence_count), { after: 0 }), { width: 20 }),
      ] }))), { columnWidths: [6000, 2000, 2000] }));
  }

  const media = sec.media || {};
  body.push(h("5. Media presence", 2));
  evidenceTable(media.coverage, "Coverage").forEach((x) => body.push(x));
  body.push(h("Adverse, critical or disputed material", 3));
  if ((media.adverse || []).length) {
    evidenceTable(media.adverse, "Item").forEach((x) => body.push(x));
  } else {
    body.push(p("No adverse material was found in the sources searched."));
  }
  body.push(p("This is not a clearance. The following were not searched and could hold material this " +
    "assessment did not see: " + (media.not_covered || []).join("; ") + ".",
    { italics: true, size: 16, color: BRAND.muted }));

  const ds = sec.digital_social || {};
  body.push(h("6. Digital and social presence", 2));
  body.push(h("Published by the subject", 3));
  evidenceTable(ds.by).forEach((x) => body.push(x));
  body.push(h("Published about the subject", 3));
  evidenceTable(ds.about).forEach((x) => body.push(x));
  if ((ds.not_assessable || []).length) {
    body.push(h("Could not be assessed", 3));
    evidenceTable(ds.not_assessable).forEach((x) => body.push(x));
  }

  // ---- Section 7: figures computed from the manifest
  body.push(h("7. Photo, video and audio inventory", 2));
  body.push(p(sec.inventory_lead));
  // ONE inventory table, same shape for every item: a captured photograph shows
  // its picture, everything else says in that same column why it has none. A/V
  // rows never carry a picture \u2014 a thumbnail shows a host's face or a title card.
  const av = sec.av_items || [];
  const notes = reasonNotes(notShown);
  const invRows = [headerRow(["Picture", "Asset, provenance and rights", "Source"])];
  shown.forEach((a) => invRows.push(new TableRow({ cantSplit: true,
    children: [pictureCell(dir, a), provenanceCell(a), srcCell(a.page_url)] })));
  notShown.forEach((a) => {
    const label = (SHORT_REASON[a.state] || "No picture") +
      (notes.shortOf[a.reason] ? " \u2014 see note " + notes.shortOf[a.reason] : "");
    invRows.push(new TableRow({ cantSplit: true,
      children: [noPictureCell(label), provenanceCell(a), srcCell(a.page_url)] }));
  });
  av.forEach((v) => invRows.push(new TableRow({ cantSplit: true, children: [
    noPictureCell("No picture \u2014 " + v.kind.toLowerCase() + " item, not illustrated"),
    avCell(v), srcCell(v.url)] })));
  body.push(table(invRows, { columnWidths: [3000, 5000, 2000] }));
  notes.shared.forEach((r, i) => body.push(p("Note " + (i + 1) + ": " + r + ".",
    { size: 16, italics: true, color: BRAND.muted, after: 40 })));

  const sm = man.summary || {};
  body.push(p(sm.found_distinct + " distinct photograph(s) found; " + sm.shown + " shown; attempt budget " +
    "applied: " + (sm.budget_applied ? "yes" : "no") + ". " + RIGHTS.charAt(0).toUpperCase() + RIGHTS.slice(1) + ".",
    { italics: true, size: 16, color: BRAND.muted }));

  body.push(h("8. Professional network and registers", 2));
  evidenceTable(sec.network, "Position").forEach((x) => body.push(x));
  body.push(h("9. Title variants and naming consistency", 2));
  evidenceTable(sec.title_variants, "Variant").forEach((x) => body.push(x));

  const asm = rep.assessment;
  body.push(h("10. Assessment", 2));
  body.push(para([text("Best known for. ", { bold: true }), text(asm.best_known_for)]));
  body.push(para([text("What someone unfamiliar concludes. ", { bold: true }),
    text(asm.unfamiliar_concludes)]));
  [["What is strong", asm.strong], ["What is missing, outdated or hard to find", asm.gaps],
   ["Fixes in priority order", asm.fixes_ranked]].forEach(([label, items]) => {
    body.push(h(label, 3));
    (items || []).forEach((i) => body.push(new Paragraph({ children: [text(i)], bullet: { level: 0 },
      spacing: { after: 60 } })));
  });

  body.push(h("11. Limitations", 2));
  rep.limitations.forEach((i) => body.push(new Paragraph({ children: [text(i)], bullet: { level: 0 },
    spacing: { after: 60 } })));

  body.push(h("12. Complete source list", 2));
  rep.sources.forEach((src, i) => body.push(para([
    text((i + 1) + ". " + src.title + " \u2014 "), link(src.url, shortUrl(src.url, 60)),
    text(src.accessed ? " (accessed " + src.accessed + ")" : "", { size: 16, color: BRAND.muted }),
  ], { after: 40 })));

  body.push(h("13. Confidence", 2));
  body.push(table([new TableRow({ children: [cell(
    [para([text(rep.confidence.level + ". ", { bold: true }), text(rep.confidence.statement)])],
    { fill: BRAND.callout_bg })] })], { borders: NO_BORDERS }));

  const doc = new Document({
    creator: "Digital Footprint Assessment", title: s.name + " \u2014 digital footprint assessment",
    description: buildStamp(dir, slug, man),
    styles: { default: { document: { run: { font: FONT, size: BODY, color: BRAND.ink } } } },
    features: { updateFields: true },
    sections: [{
      properties: {
        page: { size: { width: convertMillimetersToTwip(210), height: convertMillimetersToTwip(297) },
                margin: { top: convertMillimetersToTwip(20), bottom: convertMillimetersToTwip(20),
                          left: convertMillimetersToTwip(20), right: convertMillimetersToTwip(20) } },
      },
      headers: { default: new Header({ children: [new Paragraph({
        children: [text(s.name + "  \u00b7  Public-record assessment \u2014 point-in-time sample, " +
          s.sample_date, { size: 15, color: BRAND.muted })],
        border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: BRAND.rule, space: 4 } } })] }) },
      footers: { default: new Footer({ children: [new Paragraph({
        tabStops: [{ type: TabStopType.RIGHT, position: convertMillimetersToTwip(170) }],
        children: [
          text("Public professional information only", { size: 15, color: BRAND.muted }),
          new TextRun({ children: ["\t", "Page ", PageNumber.CURRENT, " of ", PageNumber.TOTAL_PAGES],
            font: FONT, size: 15, color: BRAND.muted }),
        ] })] }) },
      children: body,
    }],
  });
  return { doc, out: path.join(dir, "build", slug + "-digital-footprint.docx") };
}

const slugs = ALL || !ONE
  ? readJson(path.join(RUN, "subjects.json")).map((s) => s.slug)
  : [ONE];

(async () => {
  for (const slug of slugs) {
    const { doc, out } = buildDoc(slug);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    fs.writeFileSync(out, await Packer.toBuffer(doc));
    console.log("built " + out + " (" + Math.round(fs.statSync(out).size / 1024) + " KB)");
  }
})().catch((err) => { console.error(err.message); process.exit(1); });
