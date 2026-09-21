---
name: strategy-start
description: |
  The front door to the strategy framework. Explains what it is in plain words, works out what you
  already have, and points you at the right place to begin — then shows everything you can do with
  your strategy and what each thing would need. Also brings someone new up to speed on a strategy that
  has already been set up. Use when the user asks "what is this strategy thing", "how do I use this",
  "where do I start with strategy", "introduce me to the framework", "I want to work on our strategy",
  "help me with strategy", "what can I do now", "what else can this do", or "brief me on our strategy".
  Do NOT use to write or reshape a strategy, to analyse money or objectives, to prepare a review, or to
  decide whether a strategy still holds — it produces no analysis of its own.
metadata:
  category: productivity
  icon: DoorArrowLeft
---

# Where do I start

The skill a user meets first. It explains what the framework is, finds out what they already have, and routes them. **It produces no analysis of its own and never creates a strategy artefact.**

## When NOT to Use

- Writing a strategy, or getting an existing one onto one page. Use `strategy-shape`.
- Money, objectives, key results or initiatives. Use `strategy-money-and-measures`.
- Preparing a strategy meeting. Use `strategy-review`.
- Testing whether the strategy still holds. Use `strategy-decide`.
- General orientation or onboarding with no strategy in it. Use answer directly.

## Preconditions

```
Required:      nothing
Hard gate:     none
Ask for:       whether a written strategy exists, and what they want to do first
Lock without:  nothing
```

## Workflow

1. **Load the `strategy-standard` skill via the Skill tool before any search, read or drafting.** Do not proceed on memory of it. It carries the source hierarchy, the output contract, the approval classes and the presentation standard that govern everything below, and none of that binds unless the skill is actually loaded.
2. **Check for an existing strategy folder and read sheet 0 if one exists.** If a core is already there, do not start again — explain what exists and render the menu.
3. **Explain the framework in under 200 words** — the five questions, the one artefact the CEO owns, what the machine does and what stays human.
4. **Ask the two questions**, in one card: do you have a written strategy already, and what do you want to do first.
5. **Route**, and name the input the next skill needs.
6. **Run the standard's checks** and report any failure in a closing standards note.

**Never search the tenant before asking.** It costs time and credits and usually returns the wrong decade of strategy deck.

## The five questions the framework answers

1. What is this and where do I begin? — this skill
2. What is our strategy, and does it hold together? — `strategy-shape`
3. Does our money and do our measures match what we said? — `strategy-money-and-measures`
4. What needs my attention before the meeting? — `strategy-review`
5. Does this still make sense? — `strategy-decide`

## What the framework needs from you

Five inputs, in the user's words. Point at them; nothing is searched for.

| | |
|---|---|
| **the plan** | What you said you'd do — the board deck, the strategy paper, the priorities |
| **resources** | Budget lines and headcount by priority |
| **initiative registry** | What's actually running |
| **scorecard** | How you measure it today |
| **execution status** | What's happened since — last review, minutes, current actuals |

**the plan** and **resources** are the floor. The other three make the answers sharper. The opening ask is one sentence: *"Point me at what you've written down and what you're spending. Anything else you have — projects, measures, last review — add it and the answer gets sharper."*

## What you get back

Three files. `Strategy Core.docx`, one page, the only artefact the CEO personally owns. `Strategy Registers.xlsx`, the working lists. `Strategy Health.html`, the dashboard.

## Routing

| Situation | Send them to |
|---|---|
| No strategy written down | `strategy-shape`, greenfield path |
| A strategy exists but is scattered | `strategy-shape`, brownfield path |
| A core already exists in the framework | `strategy-money-and-measures`, or `strategy-review` if the registers are populated |
| They want to know what they can do | The menu, section 4 of the standard |

## Briefing someone new

When the user asks to be brought up to speed on a strategy already onboarded — a new executive, a board member, a chief of staff — read the core and the Index and give them: the problem, the approach and what it rules out, the actions with owners, the core status and when it was agreed, the last verdict, and the largest open divergence. Under 400 words. No new analysis, and nothing from a transcript about any individual.

## Output

**Layer 1** card: the five questions, a one-line description of each component, and the recommended next skill with the input it needs. Then the menu, with Available, Limited and Needs input computed from the capability table.

**No layer 2.** This is the only skill exempt, because there is nothing to evidence yet.

## Approval class

Advisory.

## When something goes wrong

- **A named file cannot be read.** Report which file and which lookup came back empty. Run limited and name the locked capability. Never substitute a figure from another source, another period or memory.
- **The registers exist but a required column does not.** That is a missing input, not an empty result. Say the column is missing. `No issues found` and `could not look` must never read the same.
- **A write fails partway.** Report what landed and what did not, naming file, sheet and fields. Do not retry blind. Re-read the record before proposing the remainder.
- **The card fails to render.** Retry once. Then fall back to markdown, say the card failed, and carry every obligation the card carried into the markdown — including the largest gap as a number in the first two lines.
- **Two strategy folders could match.** Ask which one, once. Never merge two strategies, and never guess from the most recently modified file.
- **A source is unreachable.** Report the output as partial and name what was missing, rather than presenting a complete-looking answer built on less.

## Guardrails

- Never produce a strategy artefact. No core, no registers, no analysis.
- Never search before asking.
- If the user already has a core in the framework, say so and route rather than starting again.
- Never promise a capability the inputs do not support. Locked is shown as locked, with its one unlock named.

## Handoff

`strategy-shape` for a new or unstructured strategy. `strategy-money-and-measures` if a core already exists.
