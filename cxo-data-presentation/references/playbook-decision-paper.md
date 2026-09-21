# Playbook — decision papers and business cases

Load when the route is docx, or the artefact type is a decision paper / business case.

## First page must answer (in this order)
| # | Element | Content | Checks |
|---|---|---|---|
| 1 | Decision required | Exact wording and the authority requested | DEC-01, DEC-02 |
| 2 | Recommendation | Proposed option and why | ORD-01 |
| 3 | Why now | Consequence of delay or non-decision | OPT-02 |
| 4 | Options | Including business-as-usual / status quo | OPT-01 |
| 5 | Evidence and trade-offs | Financial and non-financial; ≤3 headline facts with comparators | ORD-02, CMP-01 |
| 6 | Risk and uncertainty | Assumptions, ranges, sensitivities, downside | FWD-02, UNC-02 |
| 7 | Implementation | Owner, resources, conditions, review mechanism | CLO-01/02/03/04 |

The first page stands alone (FIN-01). Everything after it is support.

## Body sections
| # | Section | Content |
|---|---|---|
| 2 | Options appraisal | Options × criteria table; BAU as the benchmark column; trade-offs financial and non-financial; state what was excluded from the longlist and why |
| 3 | Evidence | Message-titled sub-sections; charts per `chart-selection.md`; F/E/A/J tags inline |
| 4 | Risk and uncertainty | Assumptions register (assumption · basis · owner · last validated); central estimates with ranges; sensitivity and switching values on the key assumptions; optimism-bias adjustment where forecasts are internally generated |
| 5 | Implementation | Owner, resources, conditions/dependencies, milestones, review mechanism and date |
| 6 | Appendix | Methodology, definitions, sources with as-of dates |

## Options table rule
Columns: Option · What it does · Risk carried · Tag. Mark the recommended option with the
accent word "Recommended" in its row label — no Yes/No column. Drop a cost column when
more than half its cells would be placeholders; say so in one meta-size line beneath.
Cells ≤ 20 words.

## Decision-quality chain (S3)
A decision is only as strong as its weakest link. Check each link is present:
appropriate frame · creative alternatives · meaningful reliable information · clear
values and trade-offs · sound reasoning · commitment to action. A missing link is
reported as the specific gap (frame → DEC-01; alternatives → OPT-01; information →
SRC-02; values → OPT-01 trade-offs; reasoning → CAU-01; commitment → CLO-01).

## Five-case lens (S3 investment cases — adapt, do not copy)
Strategic case (fit, case for change) · Economic case (options, value for money) ·
Commercial case (deliverability, procurement) · Financial case (affordability, cash) ·
Management case (delivery, governance, benefits realisation). Keep the economic /
financial distinction explicit: economic value is real-terms and discounted; financial
affordability is nominal and cash-based.

## Plain-language discipline
Personal pronouns, active voice, strong verbs, if–then conditionals, parallel
construction, no defined-term overload, descriptive headings that say what the section
concludes.

## Expected-element list for absence checks (⊘)
Decision wording and authority · why now · BAU option · trade-offs · assumptions
register · range on every forecast · owner · resources · conditions · review mechanism.

## REVIEW specifics for papers
- A paper whose first page lacks the exact decision wording is "Not exec-ready".
- A single-option paper fails OPT-01 even if the option is obviously right — BAU must be
  shown and dismissed with evidence.
- Point forecasts anywhere in the paper fail FWD-02.
