# Report specification — content, structure and the Word build

The research method and the report content are unchanged from v1. What changed
is that every requirement below is a **typed field in `report.json` or a row in
`assets.json`**, rendered by a script and counted by a gate.

## Fixed score vocabulary

Use these words **only**. The point is comparability: one person assessed today
must line up against another assessed next month, and against a whole roster.

| Dimension | Allowed one-word verdicts (best → worst) |
|---|---|
| Credibility | Strong / Adequate / Thin |
| Adverse material | Clean / Minor / Material |
| Distinctiveness | High / Moderate / Low / Absent |
| Discoverability | Strong / Adequate / Diluted / Invisible |
| Consistency | Consistent / Mixed / Inconsistent |
| Momentum | Rising / Steady / Slowing / Dormant |

All six, in that order, each with one sentence of evidence. No half-grades, no
invented words — `validate_json.py` rejects both.

- **Credibility** — do the facts corroborate across independent sources without contradiction?
- **Adverse material** — is there critical, disputed or damaging material in credible sources? `Clean` is always bounded by what was not searched.
- **Distinctiveness** — is there a story that is theirs, or only their job description?
- **Discoverability** — can an ordinary searcher find the right person quickly?
- **Consistency** — do name, title, employer and imagery agree across the web?
- **Momentum** — is the record current, or is the substance years old?

## Layer 1 — the one-page card (must stand alone)

1. **Headline finding** — one sentence stating what the evidence shows. Not a compliment, not a job summary; a finding someone could disagree with.
2. **Four key figures** — countable things: title variants live, years in a role, sources reviewed, adverse items, wrong-person results in the top five.
3. **What a searcher actually finds** — two to four plain sentences on the first screen.
4. **The six-dimension scorecard** — verdict plus evidence sentence.
5. **The three fixes that would change the record** — what it involves, the effort, and why it matters.

## Layer 2 — the evidence pack

In this order, every substantive line carrying a full URL and the access date:

1. First-impression sample (both queries, first screen, in order, each classified)
2. Career and professional background
3. Public profile — appearances in date order, with the exact job title used on each page
4. Topics and messages — verbatim quotes, then themes ranked by weight of evidence
5. Media presence — significant coverage, then adverse material, then what was not covered
6. Digital and social presence — published *by* vs published *about*
7. Photo, video and audio inventory (shape below)
8. Professional network and registers
9. Title variants and naming consistency, plus renamed or restructured organisations
10. Assessment — best known for · what someone unfamiliar concludes · what is strong · what is missing, outdated, inconsistent or hard to find · fixes in priority order
11. Limitations
12. Complete source list
13. Confidence — a level, plus a plain statement of what could not be checked and why

## Section 7 — required shape

**One inventory table, one row per item, one shape for everything.** Photographs,
video and audio sit in the same table; a captured photograph shows its picture,
and every other row states in that same column why it has none. There is no
separate gallery and no separate not-shown table, and a picture appears exactly
once.

Above the table sits **a prose lead carrying the findings about the visual
record** (`inventory_lead`). Not scene-setting: what does the canonical
photograph do, and how narrow is the range around it? Which assets sit outside
the employer's control, and how old are they? What do the captions attach? Close
with the practical consequence for a Corporate Affairs team, and note any
candidate captured, inspected and discarded.

| Column | Holds |
|---|---|
| **Picture** | The photograph, sized to the column (50 mm wide, 55 mm tall at most, never wider than native). For everything else, the short reason in italics — "Every route to the file refused", "No image address could be resolved", "Not tested — the browser became unavailable", "Inspected — WRONG PERSON, discarded" — plus a note reference where several rows share a cause |
| **Asset, provenance and rights** | Bold descriptive title (A/V prefixed `VIDEO —` / `AUDIO —`) · the published caption verbatim and the job title it attaches, flagged if outdated · the host · the visual-verification statement for a shown photograph · the rights line in italics. For A/V: date, duration, the exact title used, who is actually on screen, and the finding |
| **Source** | The page URL |

Order: shown photographs by rank, then unshown photographs, then video and audio.

**No video or audio row may carry a picture** — a thumbnail shows a host's face,
a show logo or a title card, so it looks like the subject's imagery while
depicting somebody else's brand. Both gates check this per row.

Where three or more rows share one reason, the cell carries its short form and
the full sentence is stated **once** as a note beneath the table.

Close with **a generated note**: how many distinct photographs were found, how
many are shown, whether the budget applied, and the rights statement.

**Capture quality is NEVER reported to the reader.** No tier letters, pixel
counts, sharpness scores, PASS/WARN or placement widths.

## Labelling rules — rendered, not described

A tag that exists only in prose is not a tag. `accept_report.py` and
`accept_docx.py` count these against `report.json`, so a renderer that drops one
is caught by the gate rather than by eye.

| Element | Requirement |
|---|---|
| Evidence tags | Each finding in sections 2-9 is its own row: a `FACT` / `FLAG` chip, the finding, its URL. `SINGLE-SOURCE` and `NOT VERIFIED` are chips too |
| Result classifications | Every first-impression result carries a classification chip; `WRONG PERSON` is visually distinct |
| Verdict pills | Each of the six verdicts is a pill coloured by its position on its own scale |

Sections 1-9 are fact; section 10, the theme ranking and the scores are
analysis. Say so in the document. Never let internal scaffolding — workspace
paths, session ids, tool names — reach the document body.

## The Word document — how `render_docx.js` builds it

| Element | Implementation |
|---|---|
| Page | A4 portrait, 20 mm margins, Aptos/Calibri 10.5 pt, headings in the brand colour, `keepNext` on all headings, widow control on |
| Running header / footer | Header: subject name · "Public-record assessment — point-in-time sample, \<date\>". Footer: "Page X of Y" (PAGE / NUMPAGES fields) · "Public professional information only" |
| Cover / Layer 1 | Title block · headline as a single-cell shaded callout · four KPI tiles as a 4-column borderless table (28 pt value, caps label) · the searcher paragraph · scorecard as a 3-column table with the verdict cell shaded by grade in white bold · three fixes as a numbered 4-column table |
| Contents | A GENERATED list after Layer 1, page break before Layer 2. Not a TOC field — a field renders blank until Word is asked to update it, so a PDF or a LibreOffice render shows an empty page |
| Dense cards | When the scorecard evidence and fixes are long, the tiles and card tables shrink a notch and the fixes table takes the next page whole, at full size — page 1 is the card at a glance, page 2 is what to do about it |
| Evidence rows | 3-column table: Chip · Finding · Source. The chip is bold 7.5 pt white text in a run with `w:shd` fill. Source is a hyperlink displayed as domain + path ≤ 40 chars, full URL in the target. Header row repeats; rows `cantSplit` |
| First impression | One table per query: rank · title · classification chip · URL |
| Quotes | Italic, left rule, attribution line beneath |
| Section 7 inventory | ONE 3-column table (Picture · Asset, provenance and rights · Source) covering photographs, video and audio. Pictures are capped at 50 mm wide and 55 mm tall; rows are `cantSplit` so a picture never separates from its provenance; A/V rows carry no picture |
| Source list | Numbered, hyperlinked, accessed date per entry |
| Confidence | Shaded callout, same style as the headline |
| Prohibited in the body | Tier letters, sharpness scores, PASS/WARN, workspace paths, tool names, session ids — gate-checked |

Fix layout defects **in `render_docx.js`, never in the document**: because the
fix lands in the renderer, one fix repairs all N reports on a roster.

## Things that reliably turn up, and are worth checking every time

- **The employer's own page is often the error source**, and databases republish it verbatim — so one defect propagates everywhere. Test it rather than trusting it.
- **Superseded titles persist** on conference, association and alumni pages long after a role changes.
- **Renamed entities** — a board seat or business unit named on a bio may no longer exist under that name.
- **Auto-generated biographies** on aggregator sites frequently present an old role as current, and can rank first.
- **Name collisions** dilute the first screen — and they tighten the photo verification rule.
- **Login-walled platforms** are usually the subject's largest owned channel and usually cannot be assessed. Say so.
- **A single corporate image library behind many URLs** is ONE asset and a consistency finding.
- **A thin subject and a failed capture look identical in a batch.** The roster gate separates them: coverage under half the median blocks when the failures were ours and warns when the hosts refused. Say which it was.
- **Roster-wide patterns outrank individual ones.** When the same defect appears across most of a team, the pattern is the finding and it belongs in every affected report as well as the roster summary.

## Boundaries

- Public professional information only. No private life, family, health, relationships, beliefs, politics or personality; no personal contact details.
- This assesses a public **record**, never a person's competence or performance.
- Search visibility is a point-in-time sample. Date it, and say so.
