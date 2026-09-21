# Check catalogue

Severity: **B** Blocker (verdict → "Not exec-ready") · **M** Major · **m** Minor.
⊘ = absence check: run against the elements the artefact type *should* contain.
Tier: which stake tiers the check runs at (S1 readout · S2 pack · S3 board/paper).

Failure messages are templates. Replace `<…>` with the specific location and value found.
Never soften the wording. Never add "consider" or "might".

| ID | Check | Inspects | Pass condition (binary) | Failure message | Sev | Tier |
|---|---|---|---|---|---|---|
| DEC-01 ⊘ | Decision stated | First page / slide / card | A sentence names what is to be decided, approved, prioritised or understood, and by whom | "No decision stated. Add one sentence: what is being decided, by whom, by when." | B | all |
| DEC-02 ⊘ | Ask is precise | Recommendation block | Ask names authority, funding, priority or risk acceptance in concrete terms | "Ask is vague ('support', 'alignment', 'visibility'). State exactly what is requested and from whom." | B | all |
| ORD-01 | Answer first | Order of first page | Conclusion sentence precedes evidence, or the SCQ exception is invoked and justified | "Answer appears on <page/slide N>. Move the conclusion to the opening line, or justify an SCQ open." | B | all |
| ORD-02 | Facts capped | Opening section | ≤3 supporting facts before the implication | "<N> facts before the implication. Keep the three most decision-relevant; move the rest to the appendix." | M | all |
| ORD-03 ⊘ | Implication present | Story | A statement links the evidence to value, strategy, customers, risk or delivery | "Evidence given without implication. State what it means for <lens value driver>." | M | all |
| TTL-01 | Message titles | Every title / heading | Title is a full-sentence claim, not a topic label | "Title '<x>' is a topic label. Replace with the message the evidence shows, e.g. '<one-sentence example>'." | M | all |
| TTL-02 | Title matches chart | Title vs visual | The chart demonstrates the title's claim | "Title claims <a>; chart shows <b>. Align one to the other." | M | all |
| CMP-01 ⊘ | Comparator on every number | All numeric claims | Each has target, forecast, prior period, baseline or benchmark | "'<value>' has no comparator. Add target / prior / benchmark or remove." | B | all |
| CMP-02 | Difference plotted directly | Multi-series charts | Variance shown as its own series where the message is a gap | "Reader must subtract between series. Plot the variance directly." | m | all |
| FWD-01 ⊘ | Forward view | Outcome statements | Each outcome paired with a driver, risk or scenario that can still change it | "Lagging-only. Pair '<outcome>' with the driver or scenario that changes it." | M | all |
| FWD-02 ⊘ | Forecast has range | Any forecast / projection | Central estimate + range or interval + the key sensitivity | "Forecast '<x>' is a point value. Add the range and the assumption it is most sensitive to." | B | all |
| UNC-01 | F/E/A/J labelled | All material statements | Every statement carries a visible Fact / Estimate / Assumption / Judgement tag | "Unlabelled statements: <list>. Tag each [F]/[E]/[A]/[J]; do not blend into narrative." | B | all |
| UNC-02 ⊘ | Assumptions register | Whole artefact | Assumptions listed together with basis and owner | "Assumptions implicit. Add a register: assumption · basis · who validates it." | M | S2, S3 |
| UNC-03 | No false precision | Numbers | Precision consistent with source uncertainty | "'<x>' shows precision the source cannot support. Round to the source's confidence." | m | all |
| SRC-01 | Source on drivers | Numbers driving the recommendation | Source named | "'<x>' drives the recommendation but has no source." | M | S1 |
| SRC-02 | Source + date on material claims | All material claims | Source and as-of date on each | "<N> material claims lack source / as-of date: <list>." | B | S2, S3 |
| CAU-01 | Causality supported | "because / driven by / due to" statements | Evidence attached, or tagged [J] | "'<x> because <y>' is asserted, not shown. Add evidence or tag as [J]." | M | all |
| KPI-01 ⊘ | KPI tied to decision | Every KPI | Names the decision or strategic objective it supports | "KPI '<x>' has no decision attached. State the decision it informs or remove it." | M | all |
| KPI-02 | No vanity metrics | KPIs | Every metric is an outcome or a named driver | "'<x>' is activity, not outcome or driver. Link it or drop it." | m | all |
| KPI-03 | Threshold consistency + owner | Recurring scorecards | Thresholds numeric, identical to prior period unless a change is declared, and a named threshold owner exists | "RAG thresholds moved since last period without a stated reason, or no threshold owner named." | B | S2, S3 (QBR, dashboard) |
| KPI-04 | Scorecard completeness | QBR scorecard | Every KPI committed last period shown with target, actual, status | "Committed KPI '<x>' missing from the scorecard." | B | QBR |
| KPI-05 | Not all-green | Scorecard | ≥1 exception shown, or an explicit "no exceptions — verified against thresholds" statement | "All-green with no exception statement. Show the nearest miss or state the verification." | M | S2, S3 |
| VIS-01 | Encoding fit | Each chart | Chart type matches the comparison per `chart-selection.md` | "'<comparison>' shown as <chart>. Use <recommended> — aligned position beats <encoding>." | M | all |
| VIS-02 | Zero baseline | Bar / length charts | Axis starts at zero | "Bar axis starts at <v>; distorts proportion. Reset to zero or switch to a dot plot." | B | all |
| VIS-03 | Insight annotated | Each chart | Turning point / exception / threshold labelled on the chart | "Chart has no annotation. Label the <point> the title refers to." | m | all |
| VIS-04 | Colour not sole status cue | Status indicators | Second cue (icon, text, pattern); ≥3:1 contrast where lightness is the cue | "Status by colour alone (WCAG 2.2 SC 1.4.1). Add an icon or text label." | M | all |
| VIS-05 | Orientation and sort | Time / ranked charts | Time runs left → right; rankings sorted by value | "Ranking unsorted / time axis reversed." | m | all |
| VIS-06 | No clutter / 3D | Charts | No 3D, no gridline excess, no decorative imagery, one message per chart | "Chartjunk: <items>. Remove." | m | all |
| VIS-07 | Emphasis within policy | Charts | Emphasis matches `minimal`, or a confirmed `keynote`; no distortion either way | "Emphasis exceeds policy for a <artefact type>." | m | all |
| STR-01 | Strategic context | Story | Explicit tie to strategy, enterprise value, customers, risk or capability | "No link to a strategic objective. State which objective this serves." | M | all |
| STR-02 | One message per slide | Decks | Each slide carries one governing message | "Slide <N> carries <k> messages. Split or move to the appendix." | m | pptx |
| STR-03 | Interruption-safe | Decks, papers | Risk, financials and implementation sections each restate the recommendation | "Jumping to <section> loses the recommendation. Restate the ask there." | m | S2, S3 |
| OPT-01 ⊘ | Alternatives incl. BAU | Decision papers, S2+ asks | ≥2 options including business-as-usual | "Only one option. Add business-as-usual and at least one alternative with trade-offs." | M | S2, S3 |
| OPT-02 ⊘ | Why now | Decision papers | Consequence of delay or non-decision stated | "No 'why now'. State the cost of deferring." | M | S3 |
| CLO-01 ⊘ | Owner per action | Every action / next step | Named owner, or a visible placeholder | "Actions without owner: <list>." | B | all |
| CLO-02 ⊘ | Timing per action | Actions | Date or period | "Actions without timing: <list>." | M | all |
| CLO-03 ⊘ | Success measure + review | Recommendation | How success is measured and when it is reviewed | "No success measure / next review." | M | all |
| CLO-04 ⊘ | Dependencies | Recommendation | Dependencies or conditions stated, or "none" declared | "Dependencies not stated." | m | S2, S3 |
| FIN-01 | First page stands alone | First page | Contains decision, answer, top exception, ask, owner | "First page does not stand alone: missing <items>." | B | all |
| FIN-02 | Material exception visible | First page | Most material negative exception and top risk appear on the first page | "Top risk / exception buried on <page N>." | M | all |
| FWD-03 ⊘ | Outlook is forward | Outlook / forward-view block | ≥1 statement about the next period with a range and a trigger | "Outlook is a counterfactual about the past. Add: if <driver> persists, <next period> exposure is <low>–<high>." | M | all |
| SRC-03 | Date integrity | Source dates vs build date and version date | No source dated after the build date; version date not earlier than data it contains | "Source dated <d1> is after the build date <d2>" / "Pack version <d1> precedes returns received <d2>. Flag as a data-integrity exception." | M | all |
| DSN-01 | One typeface, one accent | Rendered artefact | Single typeface family; accent used only per design system | "<N> typefaces / <N> accent colours visible. Apply the design system tokens." | m | BUILD |
| DSN-02 | Tags not bold-bracketed | Body prose | Tags rendered as small grey superscript letters; none bold or bracketed in prose | "Bold bracketed tags in prose at <locations>. Render as superscript letters." | M | BUILD |
| DSN-03 | Table discipline | Every table | No vertical rules, no filled header band, cells ≤ 20 words, numbers right-aligned | "Table '<x>': <issue>." | m | BUILD |
| DSN-04 | Callout first | Page 1 / first screen | Decision callout is the first block after header, title, provenance | "<block> appears above the decision callout. Move it below." | M | BUILD |
| DSN-05 | Placeholders once | Whole artefact | Each placeholder explained once in the collected block; inline occurrences are short grey italics | "Placeholder explanations repeated inline <N> times. Collect once." | m | BUILD |
| DSN-06 | Word budget | First screen / page 1 | HTML first screen ≤ 300 words; paper page 1 ≈ 450 words | "First screen carries <N> words. Collapse governance fields / move detail below." | M | BUILD |
| LEN-01 | Lens fit | Whole artefact | Materiality, risk language and ask verb match the detected lens | "Framed for <lens A>; audience is <lens B>. Reframe the ask as <verb>; lead with <value driver>." | M | all |

Build-introduced values (thresholds, ranges, methods chosen by the build) tagged F fail UNC-01.

## Running order
1. Blockers first (DEC, ORD-01, CMP-01, FWD-02, UNC-01, SRC-02, KPI-03/04, VIS-02, CLO-01, FIN-01).
2. Majors, then Minors.
3. Absence checks (⊘) are run against the expected-element list for the artefact type
   (see the playbooks), never only against what is on the page.

## Placeholder handling
A `[MISSING: …]` placeholder counts as **flagged, not passed** for CMP-01, CLO-01, SRC-01/02.
It is reported in the gap table as "placeholder present — supply <item>".

## REVIEW gap-table row format
`ID · Severity · Location · Evidence found · What clears it (≤1 example sentence)`
