---
name: strategy-outside-test
description: |
  Tests what your strategy quietly assumes about the outside world against what the evidence now says —
  the market, competitors, customers, regulation, technology and cost — and reports which assumptions
  have stopped being true, which are close to breaking, and which nobody can check. Use when the user
  asks "are our assumptions still true", "has the market moved", "what's changed out there", "is our
  read on the competition still right", "pressure-test our assumptions against the outside world",
  "what are we wrong about externally", or "check our strategy against what's happening in the market".
  Do NOT use to test internal delivery or execution, to reach a persist/adapt/stop verdict, or to
  analyse budget and objectives.
metadata:
  category: analysis
  icon: Globe
---

# The outside test

Every strategy rests on a read of the outside world. Most of that read is never written down, and none of it is retested once the deck is signed. This skill takes each external assumption, finds what the evidence now says, and reports which have stopped being true.

It reaches outside the tenant, so the sourcing bar is higher than anywhere else in the framework.

## When NOT to Use

- Testing internal delivery or execution. Use `strategy-decide`.
- Reaching a persist, adapt or stop verdict. Use `strategy-decide`.
- Analysing budget, objectives or initiatives. Use `strategy-money-and-measures`.
- Preparing a strategy meeting. Use `strategy-review`.
- General market or competitor research with no strategy behind it. Use web research directly.

## Preconditions

```
Required:      a core, or the plan
Hard gate:     none
Ask for:       nothing. It runs at Tier 1, on the plan alone
Lock without:  thresholds on the Assumptions sheet -> assumptions are tested for direction
               but not for breach; say which and why
```

This is the only framework skill that needs no internal data beyond the strategy itself. It runs on day one.

## Workflow

1. **Load the `strategy-standard` skill via the Skill tool before any search, read or drafting.** Do not proceed on memory of it. It carries the source hierarchy, the output contract, the approval classes and the presentation standard that govern everything below, and none of that binds unless the skill is actually loaded.
2. **Run the preconditions check** from section 3 of the standard.
3. **Separate the assumptions into internal and external.** Only external ones are in scope here — an assumption about our own delivery capacity belongs to `strategy-decide`. Say how many were set aside and why.
4. **State each external assumption as a testable claim** with a number and a direction before searching for anything. An assumption you cannot falsify cannot be tested, and saying so is the finding.
5. **Search for evidence**, ranked against the source hierarchy. Regulators, official statistics, filings and standards bodies outrank vendor research, which outranks trade press, which outranks commentary.
6. **Judge each assumption:** Holding, At risk, Broken, or Untestable. Give the evidence, the publisher and the date for every judgement.
7. **Update the Assumptions sheet** — status, current value, last tested — under review before action.
8. Card, then the menu, then the standard's checks.

## The sourcing bar

Higher than elsewhere, because external evidence is the easiest place in the framework to fabricate.

- **Every external claim names its publisher and its publication date, in the output.** No publisher, no claim.
- **Never use a single source for a Broken verdict.** Two independent sources, or the verdict is At risk with the reason.
- **Date-check everything.** An assumption tested against three-year-old research has not been tested. Say how old the evidence is.
- **Say when you found nothing.** "No current evidence located" is an honest result and appears as Untestable. It is never rounded to Holding.
- **Never infer a market number from an adjacent one.** A figure for a neighbouring category, a different geography or a different year is a different figure.

## Assumption categories to sweep

Run each as its own pass, so none is quietly skipped.

| | What to test |
|---|---|
| Market | Size, growth rate, segment mix, the direction the assumption depends on |
| Customer | Demand, willingness to pay, switching behaviour, channel shift |
| Competitor | Moves, entries, exits, pricing, capability the strategy assumed was hard to copy |
| Regulatory | Rules in force, rules announced, consultation stage, dates |
| Technology | The capability the strategy assumed would or would not arrive |
| Input cost | Energy, materials, labour, capital — anything a margin assumption rests on |

Report the categories the strategy makes no assumption about. A strategy silent on regulation in a regulated industry is a finding.

## Output

**Layer 1** card: how many external assumptions were tested, broken out of the total, in the title. A horizontal bar of assumed against current for the assumptions with numbers, sorted by gap. The broken ones in a table with the evidence and its date. The counter-case — the strongest reading under which the assumption still holds. What would change the answer.

**Layer 2**: the updated Assumptions sheet, plus an evidence appendix in the health dashboard listing every source with publisher, date and what it was used for.

## Approval class

Advisory. **Review before action** to write status back to the Assumptions sheet. **Prohibited delegation** for any decision that follows — a broken assumption is evidence for a decision, not the decision.

## When something goes wrong

- **A named file cannot be read.** Report which file and which lookup came back empty. Run limited and name the locked capability. Never substitute a figure from another source, another period or memory.
- **The registers exist but a required column does not.** That is a missing input, not an empty result. Say the column is missing. `No issues found` and `could not look` must never read the same.
- **A write fails partway.** Report what landed and what did not, naming file, sheet and fields. Do not retry blind. Re-read the record before proposing the remainder.
- **The card fails to render.** Retry once. Then fall back to markdown, say the card failed, and carry every obligation the card carried into the markdown — including the largest gap as a number in the first two lines.
- **Two strategy folders could match.** Ask which one, once. Never merge two strategies, and never guess from the most recently modified file.
- **A source is unreachable.** Report the output as partial and name what was missing, rather than presenting a complete-looking answer built on less.

## Guardrails

- Never state an external fact without a publisher and a date. Never reconstruct one from memory.
- Never reproduce source material verbatim. Summarise, attribute, and link where a link exists in the tool result.
- Never turn an absence of evidence into a Holding verdict.
- Never return a persist / adapt / stop verdict. That is `strategy-decide`, and it needs the internal picture this skill deliberately does not read.
- An assumption the core does not support is not inferred into existence. If the strategy's external read is unstated, say it is unstated — that is the finding, not a gap to fill.

## Handoff

`strategy-decide` when an assumption breaks — a broken external assumption is exactly what puts the problem itself back on the table. Otherwise the menu.
