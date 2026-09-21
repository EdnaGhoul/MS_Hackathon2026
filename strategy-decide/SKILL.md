---
name: strategy-decide
description: |
  Puts the strategy itself on the table rather than its execution: works out what the strategy quietly
  assumed, tests each assumption against what actually happened, separates an action that is failing
  from a problem that was wrong, and returns a persist, adapt or stop recommendation with the evidence
  behind it. Use when the user asks "does this still make sense", "should we keep going or change
  course", "are we still right about this", "what have we got wrong", "do we stick or shift", "should
  we kill this", "has the world moved on us", "which of our assumptions have broken", or "was the
  target wrong or the delivery". Do NOT use to prepare a review meeting, to analyse money and
  objectives, or to write the strategy in the first place.
metadata:
  category: analysis
  icon: Scales
---

# Does this still make sense

Tests what has happened against what the strategy assumed, and returns one of three verdicts with the evidence.

| Verdict | Meaning | What must accompany it |
|---|---|---|
| **Persist** | The problem still holds and the actions are working | What would change this |
| **Adapt** | The problem still holds but the actions are not delivering | Which actions change, and what replaces them |
| **Stop** | The problem itself is wrong. The strategy has reached the end of its life | The evidence, stated plainly. This is the verdict organisations avoid |

## When NOT to Use

- Preparing a strategy meeting. Use `strategy-review`.
- Analysing money, objectives or initiatives. Use `strategy-money-and-measures`.
- Writing or reshaping the strategy. Use `strategy-shape`.
- Testing external assumptions against market evidence. Use `strategy-outside-test`.
- Deciding one specific question rather than the strategy as a whole. Use `strategy-decision-memo`.

## Preconditions

```
Required:      a core, and at least one assumption carrying BOTH a threshold and a current value
Hard gate:     none
Ask for:       execution status or current key result values, if Not yet asked
Lock without:  nothing testable -> list the assumptions, report them untestable, and return NO verdict
```

An assumption with no threshold cannot break, and an assumption with no current value cannot be read. Without both, there is nothing to test — say so and stop. **A verdict without evidence is the thing this skill exists to prevent.**

## Workflow

1. **Load the `strategy-standard` skill via the Skill tool before any search, read or drafting.** Do not proceed on memory of it. It carries the source hierarchy, the output contract, the approval classes and the presentation standard that govern everything below, and none of that binds unless the skill is actually loaded.
2. **Run the preconditions check** from section 3 of the standard.
3. Extract the assumptions the core rests on — some written, most implicit, and the implicit ones are the ones worth surfacing. **List them all before testing anything.**
4. Test each against what actually happened. Update the Assumptions sheet status: Holding, At risk, Broken.
5. **Test the actions separately from the problem.** An action failing is not the same as the problem being wrong, and confusing the two is the most common error at this stage.
6. Run the pre-mortem.
7. Return the verdict, with the counter-case on the face of the card.
8. Write the verdict record, stamp the Index, append to History, mark the dashboard stale.
9. Card, then the menu.
10. **Run the standard's checks** and report every failure in a closing standards note.

## Pre-mortem

Assume the strategy has failed a year from now, and state the most likely reason. Include it in the output, every run.

## Target-miss analysis

When a key result misses, say whether the evidence points at a **wrong target** or **wrong execution**, and assemble the case for both readings. **Do not make the call.**

## Output

**Layer 1** card: the verdict and its reason in the title; assumptions broken shown out of the total; a grouped bar of assumed against actual, sorted by gap size; the counter-case on the face of the card because it is the most valuable line in the output; and what would reverse the verdict.

**Layer 2**: the verdict record as a document, plus the updated Assumptions sheet.

## Approval class

Advisory. **Prohibited delegation for the decision itself.**

## When something goes wrong

- **A named file cannot be read.** Report which file and which lookup came back empty. Run limited and name the locked capability. Never substitute a figure from another source, another period or memory.
- **The registers exist but a required column does not.** That is a missing input, not an empty result. Say the column is missing. `No issues found` and `could not look` must never read the same.
- **A write fails partway.** Report what landed and what did not, naming file, sheet and fields. Do not retry blind. Re-read the record before proposing the remainder.
- **The card fails to render.** Retry once. Then fall back to markdown, say the card failed, and carry every obligation the card carried into the markdown — including the largest gap as a number in the first two lines.
- **Two strategy folders could match.** Ask which one, once. Never merge two strategies, and never guess from the most recently modified file.
- **A source is unreachable.** Report the output as partial and name what was missing, rather than presenting a complete-looking answer built on less.

## Guardrails

- Never soften a verdict into diplomatic vagueness. State the view and state the confidence.
- Never return a verdict on assumptions that could not be tested. Report what was untestable and why.
- Never invent an assumption the core does not support. An implicit assumption is inferred from the core and labelled as inferred.
- Never evaluate an individual. Attribute statements, never performance.

## Handoff

`strategy-shape` on a stop verdict — the lifecycle re-enters at the core. `strategy-money-and-measures` on an adapt verdict. The menu on persist.
