# Output contracts — HTML (default), docx, pptx, pdf

Route A (decision card, incl. the REVIEW variant) is defined in SKILL.md and is the fallback
if a render errors (G6). Every BUILD produces the HTML first, then asks the user which
additional format they want (SKILL.md → Output routing). All routes obey
`references/design-system.md`; page-1 anatomy, callout, tags, tables and footer block are
defined there and not repeated here.

## HTML document (default for briefs, papers, QBR pre-reads, deck outlines)
Template: `assets/document-shell.html`. Self-contained, inline CSS with the design tokens
as CSS variables, inline SVG charts, print stylesheet (A4, page breaks before sections,
tables keep rows). Order:

| # | Block | Content |
|---|---|---|
| 1 | Header line | wordmark · artefact type — date |
| 2 | Title | Message title |
| 3 | Provenance | One line, meta size |
| 4 | Decision callout | Ask · authority · from · by |
| 5 | Recommendation + why now | ≤ 4 sentences each |
| 6 | The three facts | Table: finding · position · comparator · tag |
| 7 | Options (S2+) | Table per decision-paper playbook |
| 8 | Evidence | Message-titled sections; one chart or table each |
| 9 | Risk and uncertainty | Assumptions table; outlook with a forward statement (FWD-03) |
| 10 | Implementation | Action · owner · timing · measure · depends on |
| 11 | What the source does not provide | Grouped placeholders, once |
| 12 | Footer block | Lens · tier · emphasis / tag legend · gap count · sources |

Deck outline mode: the same blocks rendered as numbered slide cards, one message title per
card, ready to hand to the `pptx` skill.


## HTML dashboard (recurring dashboards / scorecards)
Template: `assets/dashboard-shell.html`. No external scripts, fonts or images. Inline
CSS and inline SVG only. Must open from a local file with no network. KPI governance
fields collapsed by default; first screen ≤ 300 words.

| # | Region | Content | Checks |
|---|---|---|---|
| 1 | Decision strip | The recurring decision(s) this dashboard serves; refresh cadence; as-of date; lens; tier | DEC-01 |
| 2 | Exception panel | Material exceptions first, as fragments: KPI · actual vs target · breach · action · owner · due · tag | FIN-02, CLO-01 |
| 3 | KPI grid | One tile per KPI: title · actual vs target · status (icon + word) on the face; all governance fields collapsed; bullet with zero baseline, no tick when target absent | KPI-01..05, VIS-02, VIS-04 |
| 4 | Driver view | ≤3 driver charts (line with target/forecast; waterfall for variance), annotated | VIS-01, VIS-03 |
| 5 | Forward view | Outlook: at least one next-period statement with range and trigger; top 3 sensitivities with switching values where available | FWD-02, FWD-03 |
| 6 | Assumptions register | Assumption · basis · owner · last validated; F/E/A/J tags | UNC-02 |
| 7 | Decisions and asks | Open decisions with owner and date; changes since last refresh | DEC-02 |
| 8 | Footer | Source and as-of per KPI; threshold history; placeholder list; generated date; "public sources only" | SRC-02 |

Build steps: fill the shell's data block → run `scripts/contrast_check.py` on the status
palette → write to `working/` → publish with the artifact tools → confirm presence with
`Glob output/**` → visual self-check → ask the format question → only then report.

## pptx (via the `pptx` skill, on request)
| # | Slide | Content |
|---|---|---|
| 1 | Executive summary | Question · answer · ≤3 facts with comparators · ask · owner. Stands alone. |
| 2 | Situation → complication | Only when the SCQ exception is invoked; one slide |
| 3–5 | Evidence | One message title per slide; one chart or table; annotation; comparator; F/E/A/J tags in footer |
| 6 | Options and trade-offs | Decision table: options (incl. BAU) × value · cost · risk · time; recommendation restated |
| 7 | Risk and uncertainty | Ranges, sensitivities, assumptions with owners; recommendation restated |
| 8 | Decision required and follow-through | Exact ask · action · owner · timing · measure · next review |
| A | Appendix | Methodology, definitions, secondary cuts, source list with as-of dates |

Constraints: emphasis policy `minimal` unless keynote confirmed; zero baseline on all
bars; status never colour-only; every derived number computed in code before insertion.

## docx (via the `docx` skill, on request) — start from `assets/decision-paper-template.docx`
| # | Section | Content |
|---|---|---|
| 1 | Page 1 — decision page | Decision required (exact wording, authority) · recommendation and why · why now · headline evidence (≤3, with comparators) · ask · owner / timing / measure |
| 2 | Options | Including BAU; trade-offs financial and non-financial |
| 3 | Evidence | Message-titled sub-sections; charts / tables per selection rules; F/E/A/J tags inline |
| 4 | Risk and uncertainty | Assumptions register; ranges; sensitivities; downside |
| 5 | Implementation | Owner, resources, conditions, dependencies, review mechanism |
| 6 | Appendix | Methodology, definitions, sources with as-of dates |

## pdf (on explicit request only)
Produced from the docx (or printed from the HTML). Never the primary route. Run the visual
self-check on page 1 of the PDF.

## QBR override (any route)
Replace the generic order with the eight blocks in `playbook-qbr.md`. Block 7
(decisions and asks) is additionally emitted as a separable pre-wire one-pager.

## Chart-only BUILD (any comparison question)
Text: the recommended chart, why (perceptual reason), what to annotate, the comparator,
the anti-chart to avoid. Plus one rendered example via `core-render_ui` if data is
supplied; otherwise a described example — never fabricated data points.

## Common footer (all routes)
Lens applied (+ "inferred") · stake tier · placeholder count with the list · sources and
as-of dates · "Known gaps" from the B9 self-check · emphasis policy in force.
No internal identifiers, workspace paths, or private file links appear in any artefact.
