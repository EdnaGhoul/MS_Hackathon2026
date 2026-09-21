---
name: strategy-communications
description: |
  Turns the agreed strategy into something a particular audience will actually understand — the all
  hands, the board, investors, one function, new joiners, or a customer-facing team — without adding a
  single fact the strategy does not already carry. Says what changed, why, what it means for that
  audience specifically, and what is being asked of them. Use when the user asks "how do I explain this
  to the team", "write the all-hands version of our strategy", "communicate the strategy to my org",
  "what do I tell investors about this", "put this in words my function will understand", or "draft the
  message about our new direction". Drafts only, never sends. Do NOT use to write or change the
  strategy itself, or to communicate a strategy still marked provisional.
metadata:
  category: communication
  icon: MegaphoneLoud
---

# Say it so the audience understands it

Re-frames an agreed strategy for a named audience. It is a translation job, not an authoring job: **no fact enters the message that the core does not already carry.**

## When NOT to Use

- Writing or changing the strategy itself. Use `strategy-shape`.
- Communicating a core still marked provisional. Use refuse, and route to `strategy-shape`.
- Preparing a strategy meeting. Use `strategy-review`.
- Explaining the framework rather than the strategy. Use `strategy-start`.
- General stakeholder or audience writing with no strategy behind it. Use `stakeholder-comms`.

## Preconditions

```
Required:      a core with status = agreed, and a named audience
Hard gate:     core status is provisional -> REFUSE. Never communicate a strategy outward before
               a human has agreed the problem. Route to strategy-shape to get it agreed
Ask for:       the audience, the channel, and what the audience already knows
Lock without:  scorecard -> the message cannot say how success will be judged, and says so
               resources -> the message cannot say what is being invested, and says so
```

The provisional gate is absolute. A provisional core communicated outward becomes agreed by accident, and the organisation ends up committed to a problem nobody chose.

## Workflow

1. **Load the `strategy-standard` skill via the Skill tool before any search, read or drafting.** Do not proceed on memory of it. It carries the source hierarchy, the output contract, the approval classes and the presentation standard that govern everything below, and none of that binds unless the skill is actually loaded.
2. **Run the preconditions check** from section 3 of the standard. Check core status first; refuse on provisional.
3. **Establish the audience**: who they are, what they already know, what they are worried about, and what they can actually do about it.
4. **Draft against the message frame** below.
5. **Run the fidelity check** — every claim traced back to a line in the core or a register sheet.
6. **Present the draft for review.** Never send.
7. The menu, then the standard's checks.

## The message frame

Five parts, in this order, whatever the audience.

| | |
|---|---|
| **What is changing** | Stated plainly, in the first two sentences. Not a preamble about the journey |
| **Why** | The problem, in the audience's language. This is the part organisations skip, and it is the part that determines whether anyone believes the rest |
| **What it means for you** | Specific to this audience. Generic here is worse than nothing |
| **What is not changing** | Reassurance is information. It also stops people inventing it |
| **What we are asking of you** | One thing, and something they can actually do |

## Adapting to the audience

Same facts, different weight. Never different facts.

| Audience | Leads with | Needs most | Do not |
|---|---|---|---|
| All hands | What changes for the work, and what does not | Why, in plain words. The problem, not the ambition | Use the board's vocabulary or quote unexplained numbers |
| Board | The problem and the choice made, with what it rules out | The counter-case and the measures | Present it as certain, or omit what was rejected |
| Investors | The change, the commitment, the measure | Comparative context on every figure | Disclose anything not already public. Flag it and stop |
| One function | What it means for their objectives specifically | The link from their work to a named core action | Send the company-wide version with the function's name pasted in |
| New joiners | The problem and the approach | Context they have no way to know | Assume any shared history |
| Customer-facing | What customers will notice, and what to say | Clear boundaries on what not to promise | Let them infer commitments the strategy never made |

## The fidelity check — run every time

- Every claim traces to the core, a register sheet, or something already public. **Anything else is cut, not softened.**
- No number appears without the comparator the core or the registers give it.
- No commitment is made that the strategy does not contain. Warmth is not a licence to promise.
- Nothing about a named individual. No implication about anyone's performance, role or future.
- Nothing non-public goes to an external audience. Where the draft needs a figure that is not public, leave a visible placeholder and name who must clear it.
- List, in the output, anything the audience will want to know that the core does not answer. That list is useful — it tells the CEO what they will be asked.

## Output

**Layer 1** card: the audience, the channel, and the one-line message in the title. The five-part frame as a table. The fidelity check result, including anything cut and why. Anything needing clearance before this can go out.

**Layer 2**: the draft itself, in the format the channel needs — a document for a written message, a short deck outline for a presentation, a script for a spoken one.

## Approval class

**Review before action** for anything internal — name the reviewer in the artefact. **Prohibited delegation** for anything board-facing, investor-facing or public.

## When something goes wrong

- **A named file cannot be read.** Report which file and which lookup came back empty. Run limited and name the locked capability. Never substitute a figure from another source, another period or memory.
- **The registers exist but a required column does not.** That is a missing input, not an empty result. Say the column is missing. `No issues found` and `could not look` must never read the same.
- **A write fails partway.** Report what landed and what did not, naming file, sheet and fields. Do not retry blind. Re-read the record before proposing the remainder.
- **The card fails to render.** Retry once. Then fall back to markdown, say the card failed, and carry every obligation the card carried into the markdown — including the largest gap as a number in the first two lines.
- **Two strategy folders could match.** Ask which one, once. Never merge two strategies, and never guess from the most recently modified file.
- **A source is unreachable.** Report the output as partial and name what was missing, rather than presenting a complete-looking answer built on less.

## Guardrails

- **Never send.** Draft only, and hand the send decision to the user, every time, whatever the channel.
- Never communicate a provisional core.
- Never add a fact, a figure, a date or a commitment that the strategy does not carry.
- Never spin a difficult message into vagueness. If a strategy involves stopping something, the message says what is stopping.
- Never write anything that evaluates, ranks or implies a judgement about a named person.
- Where the message would carry bad news for a group of people, prepare the content and flag that a human must own the delivery.

## Handoff

`strategy-shape` if the core turns out not to say what the user wants to communicate — that is a strategy gap, not a wording problem. Otherwise the menu.
