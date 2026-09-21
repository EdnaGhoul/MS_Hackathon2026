# Playbook — executive dashboards

Load when the route is HTML dashboard or the reviewed input is a dashboard / scorecard.

## Governing principle
A dashboard begins with **recurring executive decisions**, not with available data.
If a KPI supports no recurring decision, it is not on the dashboard.

## KPI card schema (every KPI, no exceptions)
| Field | Content | Check |
|---|---|---|
| Message title | Sentence stating what the KPI currently shows | TTL-01 |
| Strategic objective | Which objective this KPI serves | STR-01 |
| Decision supported | Which recurring decision this KPI informs | KPI-01 |
| Owner | Named person accountable for the KPI | CLO-01 |
| Definition | Precise, including inclusions/exclusions and unit | — |
| Type | Outcome (lagging) or driver (leading) | FWD-01 |
| Target | Value | CMP-01 |
| Tolerance | Band within which no action is needed | KPI-03 |
| Escalation threshold | Numeric; identical to prior period unless declared; threshold owner named | KPI-03 |
| Comparison period | Prior period / same period last year / plan | CMP-01 |
| Refresh cadence | Follows decision latency (below) | — |
| Exception action | What happens, who acts, when a threshold is breached | CLO-01 |
| Status | Icon + text + colour; never colour alone | VIS-04 |
| Source and as-of | Per KPI | SRC-02 |

## Refresh cadence follows decision latency
| KPI kind | Cadence | Reason |
|---|---|---|
| Fast-moving sales / service drivers | Daily–weekly | Intervention is still possible |
| Financial outcomes | Monthly with the close | Decision rhythm is monthly |
| Strategic outcomes | Quarterly, or when new information could change an executive decision | More often adds noise, not decisions |

## Metric architecture
Use the Balanced Scorecard's four perspectives — financial, customer, internal process,
learning and growth — **only with explicit causal logic** connecting driver measures to
outcome measures. Without that logic it degenerates into four disconnected buckets.
Draw the causal chain (driver → outcome → objective) in the dashboard's methodology note.

## Notation
IBCS 2.0 / ISO 24896 consistency: same measure → same colour, pattern and position
across every refresh; actual solid, plan outlined, forecast hatched, prior year grey.

## Expected-element list for absence checks (⊘)
Decision strip · exception panel · per-KPI fields above · assumptions register ·
threshold history · source/as-of per KPI · open decisions with owner and date.

## REVIEW specifics for dashboards
- Any KPI missing a field in the schema → named failure with the KPI and the field.
- All KPIs green → KPI-05 unless an explicit verification statement is present.
- Thresholds changed vs prior refresh without declared reason → KPI-03 (Blocker).
- Colour-only status → VIS-04; run `scripts/contrast_check.py` on the palette.
- KPI count is not a check. Seven is a heuristic, not evidence. Judge each KPI on KPI-01.

## Density rules
- KPI tile face shows: message title · actual vs target · status (icon + word). Everything
  else (objective, decision, owner, definition, tolerance, threshold, cadence, source,
  as-of) is collapsed behind an expand control. First screen ≤ 300 words.
- Exception rows are fragments: KPI · actual vs comparator · action · owner · due.
- No target → status ◇ "No target", no bar, no tick; the missing target is listed once in
  "What the source does not provide".
- Every value the build introduces (a threshold it proposes) is tagged A or J.

## Layout order (see output-contracts.md, HTML dashboard)
Decision strip → exception panel → KPI grid → driver view → forward view →
assumptions register → decisions & asks → footer.
