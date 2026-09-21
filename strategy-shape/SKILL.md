---
name: strategy-shape
description: |
  Gets a strategy onto one page — either writing one from scratch, or pulling together one that
  already exists and is scattered across a board deck, a budget and a dozen slides. Names the one
  real problem, checks the approach rules something out, flags actions that answer nothing, and shows
  the gap between the strategy written down and the strategy the spending reveals. Use when the user
  says "we've got a strategy but it's scattered everywhere", "help me get this onto one page", "I
  need to pull our strategy together", "turn this board deck into something I can work from", "is
  this actually a strategy or just a list of goals", "does our plan hold together", or "we need to
  write a strategy". Do NOT use for money or measures analysis on a strategy already onboarded, or
  for preparing a review.
metadata:
  category: analysis
  icon: DocumentOnePage
---

# Get the strategy onto one page

Two paths. Building a strategy that does not exist yet, and getting an existing one into a shape the rest of the framework can read. The second is the common one and the harder one.

## When NOT to Use

- Money, objectives, key results or initiatives on a strategy already onboarded. Use `strategy-money-and-measures`.
- Preparing a strategy meeting. Use `strategy-review`.
- Deciding whether the strategy still holds. Use `strategy-decide`.
- Explaining the framework or routing someone. Use `strategy-start`.
- Explaining the strategy to an audience. Use `strategy-communications`.
- General writing, formatting or document production with no strategy content. Use the document skills.

## Preconditions

```
Required:      the plan (brownfield path only)
Hard gate:     no plan and the user wants the brownfield path -> offer the greenfield path instead
Ask for:       resources, and the location of the plan
Lock without:  resources -> no gap analysis and no money answer
               initiative registry -> Registry sheet opens empty
               scorecard -> Objectives sheet opens empty
```

## Workflow

1. **Load the `strategy-standard` skill via the Skill tool before any search, read or drafting.** Do not proceed on memory of it. It carries the source hierarchy, the output contract, the approval classes and the presentation standard that govern everything below, and none of that binds unless the skill is actually loaded.

2. **Run the preconditions check** from section 3 of the standard. If a strategy folder already exists, read sheet 0 and say so rather than starting again — route to `strategy-money-and-measures` or `strategy-review` instead.

3. **Ask before searching.** One card, two questions: which path (write one from scratch, or work from what exists), and where the material is. Read only what is named. Searching the tenant first costs time and credits and usually returns the wrong decade of strategy deck.

4. **Run the path.** Greenfield or brownfield, below.

5. **Apply the quality test** and produce the readiness verdict.

6. **Build the artefacts.** `Strategy Core.docx`, `Strategy Registers.xlsx` with whatever sheets the supplied inputs populate, and `Strategy Health.html`. Record every input in the Inputs block on sheet 0 with its status and as-of date.

7. **Render the card, then the menu** from section 4 of the standard. Every locked capability names its one unlock.

8. **Run the standard's checks** and report every failure in a closing standards note. Never end a run with the checks unrun.

## Greenfield path

Six questions, once, in one card.

1. What has changed that you cannot ignore?
2. If nothing changes, what breaks first, and when?
3. What can you do that competitors find hard to copy?
4. What are you doing now that you would not start today?
5. What has to be true for the plan to work?
6. What would make you change your mind?

Questions four and six do the work: four surfaces sunk-cost commitments, six produces the assumption list. Then draft **two or three candidate problems** and stop. Never hand over a single problem.

## Brownfield path

Archaeology, not drafting.

1. Reconstruct the **stated** strategy from the documents.
2. Reconstruct the **revealed** strategy from the money, the headcount and the running initiatives.
3. Put them side by side.
4. Draft the core from the stated strategy, with candidate problems wherever the documents are ambiguous.
5. Force a number and a threshold onto every implicit assumption before it goes on the Assumptions sheet.

### The gap analysis

Brownfield only, and the most valuable thing this skill produces. It lives in the summary block at the foot of the Trace sheet, not in a file of its own. One row per core action, **ranked by size of gap rather than the order of the deck**. State the share of funded spend supporting the stated strategy and the share that does not. Trace people as well as money — a stated priority under-resourced in headcount is under-funded whatever its budget line says. Never soften the number.

Locked without resources. Say so on the face of the output: *"the gap between what you said and what you fund is the most useful thing here, and it needs the budget file."*

## The quality test

Applied to both paths.

- Does the problem name one thing?
- Would someone who disagrees accept it as fair?
- Does the approach rule anything out?
- Does each action answer the problem?
- Does each action have an owner and a measure?
- Is it one page?

## The readiness verdict

**Ready**, **ready with gaps**, or **not ready**. Not ready splits into two named outcomes needing different fixes: *no problem stated at all* (somebody needs to think) versus *stated and unowned* (somebody needs to decide).

State the headline performance position beside the verdict, so a reader cannot mistake a verdict about artefacts for a verdict about the business.

## Output

**Layer 1** card: the verdict and the largest gap as a number in the title. **Layer 2**: the core as a document, the registers workbook, the health dashboard.

Mark the core **provisional** until a human agrees the problem. Cap what happens next at five items, each carrying a decision and a named decider; governance items go in a short separate list beneath.

## Approval class

Advisory for the draft. **Prohibited delegation for the choice of problem.**

## When something goes wrong

- **A named file cannot be read.** Report which file and which lookup came back empty. Run limited and name the locked capability. Never substitute a figure from another source, another period or memory.
- **The registers exist but a required column does not.** That is a missing input, not an empty result. Say the column is missing. `No issues found` and `could not look` must never read the same.
- **A write fails partway.** Report what landed and what did not, naming file, sheet and fields. Do not retry blind. Re-read the record before proposing the remainder.
- **The card fails to render.** Retry once. Then fall back to markdown, say the card failed, and carry every obligation the card carried into the markdown — including the largest gap as a number in the first two lines.
- **Two strategy folders could match.** Ask which one, once. Never merge two strategies, and never guess from the most recently modified file.
- **A source is unreachable.** Report the output as partial and name what was missing, rather than presenting a complete-looking answer built on less.

## Guardrails

- Never hand over a single problem. Present two or three candidates with the evidence that separates them.
- Never invent a figure, owner, date or initiative.
- Never infer a budget allocation that is not in the file. Locked is locked.
- A document existing is not a column existing. If the registry has no stop-condition column, say the column is missing, not that no issues were found.

## Handoff

`strategy-money-and-measures`, with the core and resources. Then the menu.
