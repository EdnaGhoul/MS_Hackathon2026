# Design system

Loaded on every BUILD. Two layers: **tokens** (an organisation may change these, in one
place) and **rules** (fixed — they are what make any two outputs recognisably siblings).
Nothing in the rules references a brand.

## Tokens (the only block an organisation edits)
```yaml
typeface:        "Aptos, Segoe UI, Calibri, Carlito, Helvetica, Arial, sans-serif"   # one family only
accent:          "#1F4E79"   # the single identity colour
ink:             "#1A1A1A"
muted:           "#6B6B6B"
tag:             "#8A8A8A"
hairline:        "#D9D9D9"
fill:            "#F3F4F6"   # callout background — the only fill on the page
status_ok:       "#1B7F3B"   # always paired with ● and the word
status_risk:     "#B8860B"   # ▲
status_off:      "#B02A2A"   # ■
status_nodata:   "#6B6B6B"   # ○  (value absent)
status_unjudged: "#6B6B6B"   # ◇  (value present, no target)
wordmark:        ""          # header text, e.g. organisation name; empty = omit
footer_line:     "Confidential — internal use only"
date_format:     "D Month YYYY"
paper:           "A4"
```

## Type scale — exactly four sizes
| Role | Size / leading | Weight | Colour |
|---|---|---|---|
| Title (message title of the artefact) | 20 / 24 | Bold | ink |
| Section heading (message title) | 13 / 16 | Bold | ink |
| Body and table cells | 10.5 / 14 (cells 9.5 / 12.5) | Regular; bold only for the number that carries the message | ink |
| Meta, captions, footers, table headers | 8.5 / 11 | Regular (headers bold) | muted |
Small label above a block (e.g. "DECISION REQUIRED"): 8.5 bold, accent, letter-spaced caps.

## Colour rules
- Accent appears in: the small labels, the callout rule, the message series in charts, the
  word "Recommended". Nowhere else.
- Status colours are never the only cue: icon + word + colour, always (WCAG 2.2 SC 1.4.1).
- Context series in charts are grey; the message series is accent. No third data colour
  without a documented reason.
- No fills except the callout. No gradients. No decorative imagery. No logos inside the
  body — wordmark text in the header only.

## Spacing rhythm
13 pt before every section heading, 5 pt after · 5 pt after paragraphs · table row padding
4 pt · 10 pt after the title block · line height 1.35. Margins 20 mm sides, 18 mm top,
22 mm bottom. Sections start with their heading and first paragraph on the same page.

## Page 1 anatomy (papers, briefs, decks slide 1, dashboards first screen)
1. Header line: wordmark · artefact type (left) — date (right), meta size.
2. Title — a message title, not a topic.
3. One line of provenance, meta size.
4. **Decision callout** (see below).
5. Recommendation + why now.
6. The three facts (table).
7. Options (table) when S2+.
Nothing else sits above the callout. Lens, tier, emphasis, tag legend, placeholder count
and sources move to the **footer block** on the last page.

## Decision callout
Grey fill (`fill`), 3 pt accent rule on the left, 10 pt inner padding.
Line 1: label "DECISION REQUIRED". Line 2: the ask, one sentence, body size 11.
Line 3, meta size: `Authority  <bold>  ·  From  <bold>  ·  By  <bold or placeholder>`.

## Evidence tags — rendering
- Prose: a small superscript letter at the end of the sentence, tag colour, 6.5 pt:
  ᶠ fact · ᴱ estimate · ᴬ assumption · ᴶ judgement. Never bold, never in brackets.
- Tables: a right-hand "Tag" column, 8 % width, tag colour, meta size.
- Cards / HTML: a 10 px outlined letter badge in tag colour.
- Legend once, in the footer block. Never repeated per section.
- Any value the build itself introduces (a threshold, a range, a derived figure with a
  chosen method) is tagged A or J — never F.

## Tables
Header: bold meta size, muted, single 0.8 pt ink rule below. Rows: 0.4 pt hairline between,
no vertical lines, no fills, no zebra. Numbers right-aligned; the number carrying the
message bold. Header row repeats across pages; rows never split. **Cells ≤ 20 words** —
anything longer becomes a message-titled paragraph and the table keeps only the value,
comparator and tag. Drop a column when more than half its cells would be placeholders;
state that gap once in a meta-size line under the table. Mark the recommended option
with the accent word "Recommended" in its row label, not in a Yes/No column.

## Charts
IBCS-style notation. Grey track/context, accent message series, black tick or dashed line
for target/standard, direct labels (no legend when labels suffice), zero baseline for any
length encoding, time left→right, ranks sorted. One-line caption in meta size under the
chart carrying source and as-of. Actual = solid, plan = outline, forecast = hatched,
prior = grey. Height: variance bar 58 pt; ranked bars 16 pt per row; line charts ≤ 180 pt.

## Placeholders
Inline: grey italic in square brackets, e.g. *[Q2-2026 comparator]* — short, no
explanation inline. Collected once in a section **"What the source does not provide"**
grouped as Owners · Dates · Comparators & ranges · Other, with a one-line meta note:
"N items. Each shown once here; marked in grey italics where it affects a statement above.
None has been estimated." Never repeat the explanation at each occurrence.

## Sentences vs fragments
Titles and headings are complete sentences (the message). Table cells, callout strip,
KPI fields, exception rows and footer entries are fragments. Body paragraphs ≤ 4 sentences.

## Footer block (last page; HTML: page footer)
Two columns, meta size, hairline above:
Left — Lens · Stake tier · Emphasis. Right — Tag legend · "N items the source does not
provide — page X" · Sources with as-of dates. Running footer on every page: wordmark ·
artefact type · `footer_line` (left), "Page n of N" (right).

## Route-specific notes
- **HTML**: `assets/dashboard-shell.html` and the document shell implement these tokens
  as CSS variables. Governance fields on KPI tiles are collapsed by default (`<details>`).
  First screen ≤ 300 words.
- **docx**: start from `assets/decision-paper-template.docx` (named styles: Title,
  Heading 1, Body, Meta, Label, Callout). Never use the generator's default styles.
- **pptx**: one message title per slide (13 → 24 pt on slides), same palette, chart rules
  unchanged, tags in the slide footer.
- **pdf**: produced only on explicit request, from the docx or the HTML — never as the
  primary route.

## Visual self-check (BUILD step B9, mandatory for docx / pptx / pdf / HTML)
Render page 1 (or the first screen) to an image and inspect it. Fail and fix if any of:
1. more than one typeface family visible;
2. any bold bracketed tag in body text;
3. vertical table borders, filled header bands or zebra rows;
4. anything above the decision callout other than header, title, provenance;
5. status shown by colour alone;
6. a table row or heading split across a page break;
7. a chart bar not starting at zero, or a target tick drawn where no target exists;
8. more than one accent colour, or a fill outside the callout;
9. first screen / page 1 over its word budget (HTML 300; paper page 1 ≈ 450).
Record the outcome as "Visual check: pass" or list the fixes in "Known gaps".
