---
name: strategy-review
description: |
  Prepares a strategy meeting around the exceptions and the open decisions rather than a full status
  report, and keeps it from collapsing into the operations meeting. Covers what has changed since last
  time and why it matters, what is off track and what that tells you, which decisions are open and who
  owns each, and what is overdue — late, or dead. Refreshes the strategy health dashboard. Use when the
  user asks "what actually needs my attention", "what's changed since we last looked", "what should I
  be worried about before the board", "what can I skip", "what's slipped and why", "get me ready for
  the strategy meeting", or "how healthy is our strategy right now". Do NOT use to write or reshape the
  strategy itself, to analyse money and objectives in depth, or to decide whether the strategy still
  holds.
metadata:
  category: analysis
  icon: ClipboardTaskListLtr
---

# What needs my attention

Prepares a strategy meeting around exceptions and open decisions. Four questions and nothing else.

1. What has changed since the last review that matters?
2. Which moves are off track, and what does that tell us?
3. What decisions are open, and who owns each?
4. What is overdue — and is it late, or is it dead?

## When NOT to Use

- Writing or reshaping the strategy. Use `strategy-shape`.
- Deep analysis of money, objectives or initiatives. Use `strategy-money-and-measures`.
- Deciding whether the strategy still holds. Use `strategy-decide`.
- Costing or stress-testing the strategy. Use `strategy-financial-model`.
- A general daily or weekly catch-up with no strategy in it. Use `daily-briefing`.
- Preparing for an ordinary meeting rather than a strategy review. Use `meeting-intel`.

## Preconditions

```
Required:      an index, a core, and at least one populated register sheet
Hard gate:     no index -> route to strategy-shape. Never assemble a review from loose files
Ask for:       execution status, if Not yet asked
Lock without:  execution status -> current state only, no movement
               no prior cycle in History -> "no prior point, drift not computable"
```

## Workflow

1. **Load the `strategy-standard` skill via the Skill tool before any search, read or drafting.** Do not proceed on memory of it. It carries the source hierarchy, the output contract, the approval classes and the presentation standard that govern everything below, and none of that binds unless the skill is actually loaded.
2. **Run the preconditions check** from section 3 of the standard.
3. Read the core, the register sheets, and the History sheet.
4. Read execution status where supplied — recent mail, meetings and transcripts included.
5. Compute drift against the last History row. Do not describe it; compute it.
6. Assemble the four answers. Everything else goes to the appendix or is dropped.
7. **Refresh `Strategy Health.html`** — this skill owns it — and append a row to the History sheet.
8. Card, then the menu.
9. **Run the standard's checks** and report every failure in a closing standards note.

## The separation rule

Anything that is a performance conversation rather than a strategy conversation goes to a short appendix marked for the operational review. **Never merged into the body, even when the user is short of time.** Offer to drop the appendix instead.

## Drift

Where a previous cycle exists, **compute the movement rather than describing it**. The highest-value output this skill produces comes from comparing two points in time: an envelope reported intact at one review and several million over at the next, with no decision recorded in between.

Where no previous cycle exists, say *"no prior point — drift not computable"*. Never imply movement from a single reading.

## Refuse all-green

If everything reports green, say so explicitly and state what would have to be true for that to be credible.

## Output

**Layer 1** card: the one thing that changed and matters, the most material exception as a chart, the open-decisions table with an age in days and what each is blocked on, and the ask.

**Layer 2**: `Strategy Health.html`, refreshed, with the operational appendix collapsed.

The open-decisions table draws from the Issues sheet, so age is measured from when the decision opened, not from this run. Where the Issues sheet is empty or new, say the age is measured from this pack.

## Approval class

Advisory. The intervention decision is the user's.

## When something goes wrong

- **A named file cannot be read.** Report which file and which lookup came back empty. Run limited and name the locked capability. Never substitute a figure from another source, another period or memory.
- **The registers exist but a required column does not.** That is a missing input, not an empty result. Say the column is missing. `No issues found` and `could not look` must never read the same.
- **A write fails partway.** Report what landed and what did not, naming file, sheet and fields. Do not retry blind. Re-read the record before proposing the remainder.
- **The card fails to render.** Retry once. Then fall back to markdown, say the card failed, and carry every obligation the card carried into the markdown — including the largest gap as a number in the first two lines.
- **Two strategy folders could match.** Ask which one, once. Never merge two strategies, and never guess from the most recently modified file.
- **A source is unreachable.** Report the output as partial and name what was missing, rather than presenting a complete-looking answer built on less.

## Guardrails

- Never report a full status. Exceptions and open decisions only.
- Never recommend an intervention as if it were decided.
- Meeting transcripts are evidence about what was said, not a performance record of any individual. Attributing a statement to a speaker is correct. **Evaluating the speaker is a hard fail.**
- If a source is unreachable, report the exception list as partial and name what was missing.
- Key results with no data are a visible category beside on-track and behind. Never fold them into either.

## Handoff

`strategy-decide` when the review surfaces a broken assumption. Otherwise the menu.

## Running this on a cadence

This skill is the engine behind a recurring strategy health check. To set one up, the user schedules a prompt naming the strategy folder and the cadence; the run is this skill, unchanged, with the assumption sweep from the Assumptions sheet included in the risk panel.
