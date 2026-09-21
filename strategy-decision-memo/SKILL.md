---
name: strategy-decision-memo
description: |
  Takes one decision and works it against the strategy: whether it answers the problem you named, what
  it displaces, what would have to be true for it to work, what the credible alternative is, and the
  strongest case against. Returns a memo a board or an executive committee can actually decide from.
  Use when the user asks "should we do X or Y", "help me think this one through", "what would have to
  be true for this to work", "make the case for this", "what are our options here", "does this project
  fit our strategy", "write me a decision memo", or "I need a paper for the board on this". Do NOT use
  for a broad strategy review, for whether the whole strategy still holds, or for routine analysis with
  no decision attached.
metadata:
  category: analysis
  icon: DocumentQuestionMark
---

# One decision, worked against the strategy

Starts from the decision and works backwards to the evidence, rather than starting from whatever data happens to exist. The difference from a generic analysis is the core: every decision is tested against the problem the organisation actually named.

## When NOT to Use

- Reviewing the whole strategy rather than one decision. Use `strategy-review`.
- Deciding whether the strategy itself still holds. Use `strategy-decide`.
- Writing or reshaping the strategy. Use `strategy-shape`.
- Tracing money and objectives across the whole plan. Use `strategy-money-and-measures`.
- Costing a decision under multiple scenarios. Use `strategy-financial-model`.
- General analysis with no decision attached. Use answer directly.

## Preconditions

```
Required:      an agreed core, and the decision stated by the user
Hard gate:     no decision stated -> ask once for it. A memo without a decision is an essay
               provisional core -> runs, but says the core is provisional and the fit test is
               provisional with it
Ask for:       the decision, the decider, and the date it has to be made by
Lock without:  resources -> cannot say what this displaces, only what it costs
               initiative registry -> cannot name what it overlaps or duplicates
               scorecard -> cannot say which key result it would move
```

## Workflow

1. **Load the `strategy-standard` skill via the Skill tool before any search, read or drafting.** Do not proceed on memory of it. It carries the source hierarchy, the output contract, the approval classes and the presentation standard that govern everything below, and none of that binds unless the skill is actually loaded.
2. **Run the preconditions check** from section 3 of the standard.
3. **State the decision as one sentence**, with the decider named and the date it is needed. Play it back before going further. A decision stated loosely produces a memo about a topic.
4. **Run the fit test** against the core.
5. **Find what it displaces** — money, people, attention, and the initiatives that would slip.
6. **Build the what-would-have-to-be-true list**, each item with a threshold and a way to check it.
7. **Construct one credible alternative**, not a straw man, and state why it was rejected.
8. **Write the strongest case against** the recommendation.
9. Card, then the memo, then the menu, then the standard's checks.

## The fit test

Four questions, answered plainly.

| | |
|---|---|
| **Does it answer the problem?** | Name the part of the problem it addresses. If it addresses none, say so — a good idea that answers no stated problem is still an orphan |
| **Does it fit the approach?** | Including what the approach rules out. A decision that contradicts an explicit exclusion is a strategy change, not a project |
| **Which action does it serve?** | And which key result would move, with its baseline and target |
| **What does it displace?** | Nothing is free. If the answer is "nothing", the envelope has headroom and that should be stated as a fact, with the figure |

## What would have to be true

The heart of the memo. Not a risk list — a list of conditions, each one falsifiable.

Each item carries: the condition, the threshold that makes it true or false, how it would be checked, who would check it, and by when. A condition nobody can check is a hope and is labelled as one.

Rank them by how much the decision depends on each, and lead with the one that carries the most weight.

## The counter-case

Written as if by someone who wants the decision refused, and written well. It names the strongest evidence against, the most likely way this fails, and the cost of being wrong — which is not the same as the cost of the decision.

State plainly whether the decision is reversible. An irreversible decision with a thin case is the most expensive thing in this framework.

## Output

**Layer 1** card: the decision and the recommendation in the title, with confidence and the reason for it. KPI row: cost, what it displaces, the key result it moves, the date it is needed. A table of the options with the two or three factors that actually separate them. The counter-case in a warning container. The decision required, naming the decider.

**Layer 2**: the memo as a document, following the output contract in order — the decision, the facts with sources, the assumptions separately, the estimates with ranges, the recommendation with the rejected alternative, the evidence against, the confidence with its reason, and what would change the answer.

## Approval class

Advisory. **Prohibited delegation for the decision itself**, and for anything board-facing, capital-committing, headcount-affecting or irreversible. Prepare the evidence and stop.

## When something goes wrong

- **A named file cannot be read.** Report which file and which lookup came back empty. Run limited and name the locked capability. Never substitute a figure from another source, another period or memory.
- **The registers exist but a required column does not.** That is a missing input, not an empty result. Say the column is missing. `No issues found` and `could not look` must never read the same.
- **A write fails partway.** Report what landed and what did not, naming file, sheet and fields. Do not retry blind. Re-read the record before proposing the remainder.
- **The card fails to render.** Retry once. Then fall back to markdown, say the card failed, and carry every obligation the card carried into the markdown — including the largest gap as a number in the first two lines.
- **Two strategy folders could match.** Ask which one, once. Never merge two strategies, and never guess from the most recently modified file.
- **A source is unreachable.** Report the output as partial and name what was missing, rather than presenting a complete-looking answer built on less.

## Guardrails

- Never make the decision. Recommend, state confidence, and name the decider.
- Never build a straw-man alternative. If there is genuinely no credible alternative, say so and explain why — that is itself a finding, and usually a worrying one.
- Never invent a cost, a benefit, a date or a competitor move.
- Never let a recommendation carry high confidence on thin evidence. Say what evidence would raise it.
- Where the decision affects named individuals, prepare the evidence about the work and stop. Never evaluate a person.
- A memo with no ask has failed. State precisely what authority, funding, priority or risk acceptance is being requested.

## Handoff

`strategy-money-and-measures` if the decision is approved and needs tying into objectives and funding. `strategy-shape` if the decision contradicts the approach — that is a strategy change and belongs back at the core. Otherwise the menu.
