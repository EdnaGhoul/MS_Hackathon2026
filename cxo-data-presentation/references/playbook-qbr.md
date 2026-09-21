# Playbook — QBRs and business reviews

Load when the artefact type is a QBR, in either mode. Overrides the generic section
order on any route (card, HTML, pptx, docx).

## Eight-block order
| # | Block | Must contain | Checks |
|---|---|---|---|
| 1 | Prior commitments and executive summary | Every commitment made last quarter with status; the answer to "how did the quarter go and what do we need from you" | FIN-01, DEC-01 |
| 2 | Scorecard — actual vs plan | **Every KPI committed last quarter** with target, actual, status; thresholds identical to last quarter | KPI-04, KPI-03, CMP-01 |
| 3 | Material exceptions | Positive and negative; the nearest miss if all green | KPI-05, FIN-02 |
| 4 | Driver and root-cause analysis | Waterfall or driver table; causality evidenced or tagged [J] | CAU-01, VIS-01 |
| 5 | Updated full-year outlook | Central estimate + range + key sensitivity; change vs last outlook | FWD-02, CMP-01 |
| 6 | Risks and opportunities | Each with likelihood/impact language of the lens, owner, mitigation | FWD-01, CLO-01 |
| 7 | Decisions and executive asks | Precise asks with authority and date | DEC-02 |
| 8 | Next-quarter priorities | Owner, measure, review date per priority | CLO-01/02/03 |

Appendix: methodology, definitions, secondary cuts, source list with as-of dates.

## Non-negotiable QBR practices
1. **Show every KPI committed last quarter** — target, actual, status. A scorecard that
   only shows green erodes trust faster than a red rating ever will.
2. **Keep amber/green/red thresholds numeric and consistent across quarters.** A change
   must be declared with a reason and a named threshold owner. Elastic thresholds are the
   "watermelon" / all-green failure (KPI-03, Blocker).
3. **Pre-wire the decisions.** Share the decisions-required content with key stakeholders
   before the meeting so the meeting confirms decisions rather than introducing them.
   In BUILD, emit block 7 as a separable one-pager for pre-wiring.
4. A QBR is a decision meeting, not a document read-aloud. If nothing needs deciding,
   say so explicitly in block 7 ("No decisions required this quarter; for information").

## Customer-facing QBR variant
Same eight blocks. Additional expectations: history and goals of the partnership
restated in block 1; financial check-in (budgeted vs actual) in block 2; feedback
solicited and recorded in block 6; forward roadmap with owners on both sides in block 8.
Lens defaults to Sales / business executive unless the recipient's title says otherwise.

## Expected-element list for absence checks (⊘)
Prior-commitment list · every committed KPI · threshold owner · at least one exception
or verification statement · full-year outlook with range · decisions-required block ·
owner/measure/review per priority.

## REVIEW specifics for QBRs
- Obtain last quarter's KPI list if available (attached, or `m365_search-SearchM365`
  for the prior QBR). If not available, state that KPI-04 could not be verified — do not
  pass it.
- A QBR with no block 7 is "Not exec-ready" regardless of everything else.
