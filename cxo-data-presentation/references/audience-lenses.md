# Audience lenses

These are differences of **emphasis**, not separate communication systems. The numbers
stay identical. What changes is the executive's decision right, value lens, risk
language and the required action.

## Lens table

| Lens | Primary framing | Typical emphasis (materiality filter) | Risk treatment | Best call to action (ask verbs) |
|---|---|---|---|---|
| CEO / board | Enterprise trajectory and strategic choice | Growth, profitability, customer position, strategic initiatives, material capability, reputation | Portfolio-level exposure, risk appetite, downside, resilience | Set strategic direction, allocate capital, accept risk |
| CFO | Economic value and financial control | Revenue quality, margin, cash, variance, forecast, return, affordability, sensitivities | Quantified ranges, downside, assumptions, controls | Fund, defer, reallocate, set conditions, revise forecast |
| CIO / CTO / CDO | Business outcome enabled by technology and data | Value delivery, resilience, security, architecture constraints, adoption, technical debt, delivery risk | Business impact of cyber, resilience, concentration, data and execution risk | Prioritise portfolio, accept trade-off, retire, invest |
| Sales / business executive | Attainment and future revenue motion | Revenue vs plan, pipeline quality, conversion, sales cycle, retention, account concentration, capacity | Forecast confidence, deal slippage, renewal, concentration | Reallocate coverage, unblock deal, change play, reset commit |
| COO / Risk / HSE | Operational continuity, harm prevention and regulatory standing | Incident frequency and severity, contractor and supplier performance, assurance and audit coverage, data integrity of returns, regulatory obligations and deadlines | Incident severity, regulatory exposure and disclosure, concentration in one contractor or site, unverified self-reported data | Escalate, suspend, audit, remediate, restate a return, accept or withhold a return, issue a non-conformance |

## Lens-specific notes
- **COO / Risk / HSE** material leads with the obligation and the exposure, not the trend:
  what must be notified, corrected or stopped, by when, and what happens if it is not.
  Self-reported data (contractor hours, severity classification) is tagged A until verified.
- **CEO / board** material stays forward-looking and proportionate to governance
  responsibility. Boards need to look further out than anyone else in the company;
  directors' time is dominated by backward-looking review, so the forward view is the
  scarce contribution.
- **CFO** material keeps the distinction between *economic value* (real terms, discounted,
  wider effects) and *financial affordability* (nominal, cash, budget constraints). Never
  present one as the other.
- **CIO / CTO / CDO** material frames technology as high-level outcomes that support
  prioritisation and communication, not low-level controls (the NIST CSF 2.0 pattern).
- **Sales / business executive** material ties every metric to an intervention still
  available this period: coverage, deal, play, commit.

## Detection signal words

| Lens | Signal words in the ask or artefact |
|---|---|
| CEO / board | board, exec committee, strategy, portfolio, market position, reputation, capital, M&A, resilience |
| CFO | budget, forecast, variance, margin, cash, ROI, NPV, payback, affordability, cost centre, accrual, sensitivity |
| CIO / CTO / CDO | platform, architecture, roadmap, adoption, tech debt, security, resilience, data quality, integration, migration |
| Sales / business exec | pipeline, quota, attainment, commit, coverage, conversion, churn, renewal, ACV/ARR, deal, play |
| COO / Risk / HSE | incident, LTI, LTIFR, near miss, HSA/HSE/regulator, SOP, audit, non-conformance, contractor, return, assurance, compliance, restatement |

## Canonical illustration — one finding, four versions
Hypothetical finding (illustration only): enterprise renewals forecast 8 percentage
points below plan; customers completing executive onboarding renew at materially higher
rates; a proposed onboarding expansion costs £1.2m and is expected to protect £6m ARR,
plausible range £3m–£7m.

| Lens | Version |
|---|---|
| CEO / board | "Enterprise retention threatens the growth plan. Approve a targeted onboarding intervention to protect strategic accounts, with a downside case and quarterly outcome review." |
| CFO | "The £1.2m intervention has a £3m–£7m protected-revenue range. Release funding in stages, conditional on early cohort retention and cost-per-account thresholds." |
| CIO / CTO / CDO | "Renewal risk correlates with weak implementation adoption. Prioritise onboarding telemetry and workflow automation, while explicitly managing integration capacity and data-quality dependencies." |
| Sales / business exec | "Focus customer-success capacity on the highest-risk enterprise renewals. Assign an owner to each account, track onboarding completion weekly and adjust the renewal forecast using observed cohort conversion." |

Same numbers in all four. Use this pattern when reframing (LEN-01) — change the ask
verb and the lead value driver, never the evidence.

## Decision-holder rule
When the source itself names who holds the decision (a policy clause, a delegation
schedule, a RACI), that role sets the lens, ahead of artefact type or content. Say so in
the footer: "Lens: Risk / HSE — decision right per §5.3".

## LEN-01 reframing procedure
1. Identify the current lens the artefact is written for (dominant vocabulary, ask verb).
2. Identify the target lens (detection ladder in SKILL.md).
3. Rewrite only: the title, the implication sentence, the risk sentence, the ask verb.
4. Leave every number, comparator, source and F/E/A/J tag untouched.
