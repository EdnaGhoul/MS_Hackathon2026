---
name: strategy-money-and-measures
description: |
  Shows where the money and the people actually go against what you said mattered, and whether your
  measures would prove any of it. Traces every budget line and every initiative back to a priority,
  names what answers to nothing, compares what each priority was promised against what it was funded,
  and tests objectives and key results for baselines, owners, counter-measures and pairs that fight
  each other. Use when the user asks "where is our money actually going", "are we investing behind
  what we said mattered", "how much went to X versus what we promised", "which projects don't tie
  back to anything", "do our OKRs match the strategy", "help me set objectives for this", "review our
  objectives", "what's funded with no way out", or "take these objectives down to my functions". Do
  NOT use to write the strategy itself, or to prepare a review meeting.
metadata:
  category: analysis
  icon: DataTrending
---

# Money and measures

The largest component. It holds the methodology for turning a strategy into measures, tests what already exists against that methodology, advises, and — on approval — applies changes.

## When NOT to Use

- Writing or reshaping the strategy itself. Use `strategy-shape`.
- Preparing a strategy meeting. Use `strategy-review`.
- Deciding whether the strategy still holds. Use `strategy-decide`.
- Costing the strategy or stress-testing it under scenarios. Use `strategy-financial-model`.
- Working one specific decision. Use `strategy-decision-memo`.
- General budget or project reporting with no strategy attached. Use answer directly.

## Preconditions

```
Required:      a core or the plan, PLUS at least one of resources, initiative registry, scorecard
Hard gate:     drafting new objectives or target levels, and any apply, need an AGREED core
Ask for:       whichever of resources / registry / scorecard is Not yet asked
Lock without:  resources -> funding fidelity, headcount trace, stated-vs-funded
               scorecard -> OKR quality, conflict pairs, counter-measures
               registry -> orphan initiatives, stop conditions
               any one -> the tri-link reports which link has no data; it never claims the chain holds
```

The gate is split. The traceability check, the tri-link and the registers run against a **stated** strategy — a board deck, a plan, a published set of priorities. Only the drafting of new objectives and target levels needs an agreed core. Say in the output which was used, and that the run must be repeated once the core is agreed.

## Workflow

1. **Load the `strategy-standard` skill via the Skill tool before any search, read or drafting.** Do not proceed on memory of it. It carries the source hierarchy, the output contract, the approval classes and the presentation standard that govern everything below, and none of that binds unless the skill is actually loaded.
2. **Run the preconditions check** from section 3 of the standard. No index at all: route to `strategy-shape`.
3. Read the core and the register sheets the Inputs block says are supplied. Column-level, not file-level.
4. Run the tri-link in both directions.
5. Run the OKR rules and the anti-pattern scan.
6. Run fidelity: stated against funded, money and headcount.
7. Write findings to the register sheets **in review mode only** — proposals, not writes — unless the user has asked for apply and the apply protocol has been followed.
8. Card, then dashboard staleness stamp, then the menu.
9. **Run the standard's checks** and report every failure in a closing standards note.

## The tri-link

Every link checked in both directions. A break anywhere is a finding.

| Link | Forward | Reverse |
|---|---|---|
| Action to objective | Every core action carries at least one objective | Every objective traces to exactly one core action |
| Objective to key result | Every objective carries three to five key results | Every key result names its objective |
| Key result to initiative | Every key result has at least one initiative behind it | Every initiative names the key result it serves. One that serves none is flagged, not deleted |
| Initiative to funding | Every initiative has a funding line and a headcount | Every budget line traces to an initiative or is explicitly marked run the business |

The most common and most expensive breaks: **an objective with no funding, which is theatre, and funding with no objective, which is drift.**

## OKR rules

An objective is a sentence with intent in it. Key results are the outcomes that prove it happened. A label with a number beside it is neither.

| Element | Required shape | Fails if |
|---|---|---|
| Objective | One qualitative sentence saying what changes. Time-boxed. Named owner | It is a metric, a task, or the ambition restated. No owner |
| Key result | Outcome not activity. Baseline, target, date, source system, owner. Countable by someone other than its owner | It is an activity ("run three studies" rather than "three claims live on pack"). No baseline. No date. No named source |
| Set | Three to five key results per objective. No more than five objectives at company level. Committed and aspirational marked separately | A long list. Unmarked ambition level, so nobody knows whether missing is failure |
| Counter-measure | Every key result names the behaviour it drives and the counter-measure that stops it being gamed | A measure that can be met by damaging another objective, with nothing beside it |

## Anti-patterns, named explicitly

- **Activity as outcome.** Counting completed studies rewards cheap, fast, low-power ones. Count claims that reach a pack.
- **Counting anything.** A count of signed joint business plans rewards signing on any terms. Count only plans at or above target net price.
- **Ratios without absolutes.** A share target rewards deleting cheap lines. Pair it with the absolute number.
- **Coverage measures.** Coverage rewards doing the easy ones first. Lead on residual risk.
- **Health KPIs inside the strategy scorecard.** Safety incidents and complaint rates are licence to operate, not what the strategy is trying to change. Mixing them in makes "seven of thirteen behind" a meaningless sentence. They go on the Health sheet.
- **Conflict pairs.** Two measures on the same scorecard where meeting one damages the other. Found by reading the whole set at once, which is the single thing a machine does better than a workshop.

## Fidelity, not just traceability

Tracing and fidelity are different questions and this skill asks both. An initiative can trace perfectly to a priority that was promised a fifth of the money and given a fiftieth.

Where a stated or announced allocation exists — a board slide, a plan, a public commitment — compare it line by line against the funded allocation and **lead with the largest divergence**. Trace people as well as money.

## Depths, on request

- **Cascade.** Take the objectives down a level to functions. Check each function set traces up to a company objective and adds up to it. Needs the scorecard and the org structure.
- **Cut simulation.** "If I take N per cent out, what loses its backing?" Report which key results lose all funded initiatives, not which cost centres shrink. Needs resources and the registry.
- **Stop sweep.** Every initiative past its planned end, or carrying spend with no stop condition, ranked by money at risk.

## Modes

**Review** (assess what exists), **draft** (propose what is missing), **apply** (write approved changes). Default is review. Draft on request. Apply only under section 8 of the standard — propose, show the difference, wait for explicit approval, apply one sheet at a time, confirm what changed.

## Output

**Layer 1** card leading with the largest divergence as a number. **Layer 2**: the registers workbook — objectives, registry, trace with its summary block, the tri-link result, the conflict pairs, and health KPIs listed separately.

## Approval class

Advisory for the analysis. **Review before action** for any change to a register sheet. **Prohibited delegation** for the funding decision and the target level.

## When something goes wrong

- **A named file cannot be read.** Report which file and which lookup came back empty. Run limited and name the locked capability. Never substitute a figure from another source, another period or memory.
- **The registers exist but a required column does not.** That is a missing input, not an empty result. Say the column is missing. `No issues found` and `could not look` must never read the same.
- **A write fails partway.** Report what landed and what did not, naming file, sheet and fields. Do not retry blind. Re-read the record before proposing the remainder.
- **The card fails to render.** Retry once. Then fall back to markdown, say the card failed, and carry every obligation the card carried into the markdown — including the largest gap as a number in the first two lines.
- **Two strategy folders could match.** Ask which one, once. Never merge two strategies, and never guess from the most recently modified file.
- **A source is unreachable.** Report the output as partial and name what was missing, rather than presenting a complete-looking answer built on less.

## Guardrails

- Never set a target level. State what the target implies in money and resource, and leave the call.
- Never invent a figure, owner or date. Never infer an allocation that is not in the file.
- When reporting a share as aligned or a count as complete, state the counting rule and whether the source could be incomplete.
- If an initiative could serve two objectives, list it against both and flag it rather than choosing. Whoever tags it is making a strategy statement, not an admin correction.
- A missing column is a finding, not an empty result. "No initiatives without stop conditions" and "the registry has no stop-condition column" are different sentences and must never be printed as the same one.

## Handoff

`strategy-review`. Then the menu.
