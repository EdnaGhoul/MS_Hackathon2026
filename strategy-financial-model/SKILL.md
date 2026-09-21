---
name: strategy-financial-model
description: |
  Puts the strategy into money and then stress-tests it: what each priority costs and what it is
  expected to return, how the envelope behaves period by period, and what happens to the objectives
  under a funding cut, a delivery slip, a cost shock or a demand miss. Shows which key results lose
  their backing first and where the envelope breaks. Use when the user asks "what does this strategy
  cost us", "can we afford this plan", "what if we cut 10 per cent", "stress-test our strategy",
  "what happens if the savings don't land", "model the downside", "where does the money run out", or
  "what's the return on these priorities". Do NOT use for routine budget tracing with no scenario in
  it, or to set a target or approve a funding decision.
metadata:
  category: analysis
  icon: Money
---

# The strategy in money

Builds the strategy as a financial shape — cost and expected return per core action, the envelope over the period — and then breaks it on purpose to see what fails first.

Modelling is not deciding. This skill prepares the evidence for a funding decision and stops.

## When NOT to Use

- Routine budget tracing with no scenario in it. Use `strategy-money-and-measures`.
- Working one specific investment decision. Use `strategy-decision-memo`.
- Deciding whether the strategy still holds. Use `strategy-decide`.
- Preparing a strategy meeting. Use `strategy-review`.
- Building a general financial model with no strategy attached. Use the spreadsheet skill.

## Preconditions

```
Required:      a core, resources, and an initiative registry carrying budget and spend to date
Hard gate:     none, but see the modelling gate below
Ask for:       the envelope, and the period the model should cover
Lock without:  the envelope -> no headroom position; report absolute cost only
               scorecard -> scenarios report money at risk, not key results at risk
               History -> no run-rate, so slippage scenarios use stated plan dates only
```

**The modelling gate.** Every driver in the model is either read from a file or supplied by the user. **A driver you cannot source is not modelled** — it is listed as a required input with the question that would resolve it. A model built on invented drivers is worse than no model, because it is persuasive.

## Workflow

1. **Load the `strategy-standard` skill via the Skill tool before any search, read or drafting.** Do not proceed on memory of it. It carries the source hierarchy, the output contract, the approval classes and the presentation standard that govern everything below, and none of that binds unless the skill is actually loaded.
2. **Run the preconditions check** from section 3 of the standard.
3. **Build the base case** from the registers. Cost per core action from the Trace, timing from the Registry, return only where a benefit figure exists in a source. Where no benefit figure exists, say so — an unquantified benefit stays unquantified.
4. **List every driver and every assumption**, each with its source and its value, before running a single scenario.
5. **Run the scenarios** below.
6. **Report what breaks first**, in key results where the scorecard allows it, in money where it does not.
7. Write the model to a Model sheet in the registers workbook, under review before action.
8. Card, then the menu, then the standard's checks.

## Depth

Two depths. State which was run, in the output.

- **Envelope** (default). Cost, timing and headroom against the stated envelope. No revenue modelling. Runs off the registers alone.
- **Full**. Adds revenue and cost drivers, and therefore needs those drivers supplied. Only run this when the user asks and the drivers exist.

## The scenarios

Run all five unless the user names a subset. Each states its trigger, its size and its source.

| Scenario | What it does |
|---|---|
| **Funding cut** | Take N per cent out of change spend. Report which key results lose all funded initiatives — not which cost centres shrink |
| **Delivery slip** | Push planned end dates by N months. Report benefits that move out of the period and the envelope effect of carrying cost longer |
| **Cost shock** | Move a named input cost by N per cent. Report which actions become unaffordable at the current envelope |
| **Benefit miss** | Deliver only N per cent of stated benefit. Report the payback position and the actions whose case no longer stands |
| **Combined downside** | The three most likely adverse moves together. Report the first period the envelope breaks |

Scenario sizes are the user's to set. Where they have not said, use a stated, visible default and label it as a default, never as a forecast.

## What the model must always show

- **The break point.** The first period where the envelope is exceeded, or a plain statement that it is not exceeded in the modelled period.
- **The order of failure.** Which key result loses its backing first, second, third. Order matters more than magnitude for a decision.
- **What is unfunded already.** Before any scenario runs — an objective with no funded initiative is a base-case finding, not a downside one.
- **Sensitivity.** Which single driver moves the answer most. If one assumption carries the model, the model is that assumption.
- **What is not modelled.** Named explicitly. Benefits with no figure, actions with no cost line, anything the user declined to supply.

## Output

**Layer 1** card: the break point or the headroom as a number in the title. A grouped bar of base case against the worst scenario by core action, sorted by gap. A table of scenario, trigger, effect on the envelope, and the first key result to lose backing. The counter-case — the most credible reading under which the plan holds. The decision required, stated as a question for the CFO and the CEO, never as a recommendation to cut.

**Layer 2**: the Model sheet — drivers with sources, base case, one block per scenario, and a clearly labelled unmodelled list. Every derived figure is a live formula, and every input is labelled with its unit and its source.

## Approval class

Advisory for the model. **Review before action** to write the Model sheet. **Prohibited delegation for the funding decision, the cut, and any target level.** Say what the number implies and leave the call.

## When something goes wrong

- **A named file cannot be read.** Report which file and which lookup came back empty. Run limited and name the locked capability. Never substitute a figure from another source, another period or memory.
- **The registers exist but a required column does not.** That is a missing input, not an empty result. Say the column is missing. `No issues found` and `could not look` must never read the same.
- **A write fails partway.** Report what landed and what did not, naming file, sheet and fields. Do not retry blind. Re-read the record before proposing the remainder.
- **The card fails to render.** Retry once. Then fall back to markdown, say the card failed, and carry every obligation the card carried into the markdown — including the largest gap as a number in the first two lines.
- **Two strategy folders could match.** Ask which one, once. Never merge two strategies, and never guess from the most recently modified file.
- **A source is unreachable.** Report the output as partial and name what was missing, rather than presenting a complete-looking answer built on less.

## Guardrails

- Never invent a driver, a benefit, a growth rate or a cost. An unsourced number is a required input, not an estimate.
- Never present a scenario as a forecast. A scenario is a stress, and the output says so.
- Never recommend which programme to cut. Show what each cut costs in key results and let a human choose.
- Never model headcount reduction as a line item. Headcount changes affect named individuals and are prohibited delegation.
- State the counting rule behind every share, and whether the source could be incomplete.

## Handoff

`strategy-money-and-measures` when the model exposes a traceability break. `strategy-decide` when it exposes a broken assumption. Otherwise the menu.
