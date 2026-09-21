---
name: strategy-standard
description: |
  The evidence and presentation standard behind every strategy output. Sets how claims are sourced,
  how facts are kept apart from assumptions and estimates, what every output must contain, who signs
  what, and how any of it is presented to an executive. Also carries the shared working files, the
  input requirements of every strategy skill, and the health dashboard format. Use when the user asks
  "is this good enough to go to the board", "does this stand up", "review this before I send it",
  "what's missing from this analysis", "check the evidence behind this", or "who needs to approve
  this". Hard dependency of every other strategy-* skill: always load it when any of them runs. Do NOT
  use for drafting strategy content or for general document formatting with no strategy in it.
metadata:
  category: analysis
  icon: DocumentBulletListCheckmark
---

# Strategy standard

The shared standard for every artefact the strategy framework produces. Used on its own to stress-test a pack before executives see it, and loaded by every other strategy skill before it does anything else.

## When NOT to use

- Getting a strategy onto one page, or onboarding an existing one. Use `strategy-shape`.
- Money, objectives, key results, initiatives. Use `strategy-money-and-measures`.
- Preparing a strategy meeting. Use `strategy-review`.
- Testing whether the strategy still holds. Use `strategy-decide`.
- Explaining the framework or routing someone. Use `strategy-start`.
- Testing assumptions against the outside world. Use `strategy-outside-test`.
- Costing or stress-testing the strategy. Use `strategy-financial-model`.
- Working one decision against the strategy. Use `strategy-decision-memo`.
- Explaining the strategy to an audience. Use `strategy-communications`.
- General writing, formatting or document production with no strategy content.

## 1. The five inputs

One vocabulary, used identically in every skill, in every question to the user, and on the dashboard.

| Name | What it is |
|---|---|
| **the plan** | What the organisation said it would do. Board deck, strategy paper, published priorities |
| **resources** | Budget lines with amounts, and headcount by priority. Run and change separated where available |
| **initiative registry** | What is actually running: name, owner, status, start, planned end, spend to date |
| **scorecard** | How it is measured today: OKRs, KPIs, a board scorecard, a slide of numbers |
| **execution status** | What has happened since: last review, minutes, current actuals, recent mail and meetings |

**the plan** and **resources** are the floor. Inputs are named by the user and read as given. Never trawl the tenant for a strategy before asking; it returns the wrong decade of deck.

## 2. The three files

```
Documents/Cowork/Strategy/<Org> <Period>/
  Strategy Core.docx        authored, signed by the CEO      state
  Strategy Registers.xlsx   machine state, eight sheets      state
  Strategy Health.html      the rendered view                derived
```

**Two files hold state. The third renders it.** Anything that cannot be rebuilt from the core and the registers is state and belongs in one of them. Anything that can is a rendering and is not a new artefact.

### Strategy Core.docx — authored, four parts, one page

| Part | What it is | Test it must pass |
|---|---|---|
| Header | Period, owner, date, status: provisional or agreed | A named owner and a date |
| The problem | What is really going on. One thing, stated so someone who disagrees would call it fair | Falsifiable. Not the ambition restated. Not a list |
| Our approach | The approach chosen to deal with the problem, and **what it rules out** | Rules something out. An approach that excludes nothing is an aspiration |
| The actions | Three to five, each with an owner and the objective it serves | Each answers the problem. One that does not is an orphan and is named as one |

Use "the problem", never "the diagnosis" and never "the kernel". The question printed beneath it is "what's really going on?".

### Strategy Registers.xlsx — eight sheets

| # | Sheet | Columns |
|---|---|---|
| 0 | Index | Item, Value, Set by, Date. Holds org and period, core owner, core status, date agreed, lifecycle position, last verdict, next review, decision rights, measurement convention, currency, version, and the **Inputs block** below |
| 1 | Objectives | ID, objective, core action served, objective owner, committed or aspirational, key result, baseline, target, current value, as of, due date, source system, KR owner, behaviour it drives, counter-measure, conflict pair, flag. **One row per key result** |
| 2 | Registry | ID, name, key result served, owner, status, start, planned end, budget, spent to date, stop condition, last reviewed, flag |
| 3 | Trace | Line, amount, initiative served, core action served, run or change, headcount, flag. Plus a summary block beneath: one row per core action with stated share, funded share, divergence, headcount share |
| 4 | Assumptions | ID, assumption, source, current value, threshold that breaks it, status, owner, last tested |
| 5 | Issues | ID, issue or decision, type, owner, opened, age in days, blocked on, status |
| 6 | Health | KPI, owner, baseline, current, target, source, as of. Licence-to-operate measures only, never mixed into Objectives |
| 7 | History | Cycle, date, skill, core status, KRs on track / behind / no data, funded total, envelope position, largest divergence, verdict. One row per cycle |

Conventions: header in row 1, data from row 2, one row per record, no merged cells inside data, no spacer rows. Stable prefixed IDs (`O1`, `O1-KR2`, `I-07`, `B-112`, `A-04`, `S-03`). Values, not cross-sheet formulas, with the counting rule stated. Flags are text (`ORPHAN`, `NO STOP`, `BROKEN`, `ACTIVITY`, `NO BASELINE`, `SERVES TWO`, `CONFLICT`). ISO dates, one currency, both declared in the Index. Trailing `Last updated` and `Updated by` on every maintained sheet.

**The Inputs block on sheet 0.** One row per input: `Input, Status, File or source, As of, Recorded by, Date`. Status is exactly one of **Supplied**, **Declared unavailable**, **Not yet asked**.

## 3. Preconditions — run this before any search, read or draft

Every skill calls this as its numbered workflow step 2. Read sheet 0 of the registers, compare the Inputs block against the requirements below, and take exactly one of four outcomes. Do not proceed past this step on assumption.

| Outcome | When | Behaviour |
|---|---|---|
| **Run** | Everything required is Supplied | Proceed without comment |
| **Ask** | Missing, but likely to exist and answerable in one reply, and Status is `Not yet asked` | One question card, then proceed. Never a second card in the same run |
| **Run limited** | Missing and genuinely absent, or Status is already `Declared unavailable` | Produce what is possible. Lead the output with what was locked and why |
| **Refuse and route** | A hard gate below | Name the gate, name the skill to run instead, stop |

Deciding between Ask and Run limited: **could the user hand this over in one answer?** A budget file they have but have not mentioned, ask. A scorecard the company has never written, do not ask.

**Presence is not sufficiency.** Test for the required columns, not for a file existing. A registry with no stop-condition column is a missing input for the stop sweep and is named as that. "Found nothing" and "could not look" must never read the same.

**Record the answer.** When a user says an input does not exist, write `Declared unavailable` with the date into the Inputs block. Do not ask again on later runs; show the capability as locked with the reason.

**Staleness warns, it never locks.** An input two quarters old still runs; state its age.

### The capability table

| Skill | Required to run | Hard gate | Locked without |
|---|---|---|---|
| `strategy-start` | nothing | none | nothing |
| `strategy-shape` | the plan (brownfield path only) | no plan: offer the greenfield path instead | resources: no gap and no money answer. registry / scorecard: those sheets open empty |
| `strategy-money-and-measures` | a core or the plan, **plus at least one of** resources, registry, scorecard | drafting objectives or target levels, and any apply, need an **agreed** core | resources: funding fidelity and headcount trace. scorecard: OKR quality, conflict pairs, counter-measures. registry: orphans and stop conditions. Any one missing: the tri-link reports which link has no data, and never claims the chain holds |
| `strategy-review` | an index, a core, and at least one populated register sheet | no index: route to `strategy-shape`, never assemble a review from loose files | execution status: current state only. no prior cycle: "no prior point, drift not computable" |
| `strategy-decide` | a core and at least one assumption carrying **both** a threshold and a current value | none | execution status or current KR values: assumptions are listed and reported untestable, and no verdict is returned |
| `strategy-outside-test` | a core or the plan | none | thresholds on the Assumptions sheet: assumptions tested for direction but not for breach |
| `strategy-financial-model` | a core, resources, and a registry carrying budget and spend | none, but an unsourced driver is never modelled | the envelope: absolute cost only, no headroom. scorecard: money at risk, not key results at risk |
| `strategy-decision-memo` | an agreed core, and the decision stated by the user | no decision stated: ask once. A memo without a decision is an essay | resources: cost but not displacement. registry: no overlap check. scorecard: cannot name the key result it moves |
| `strategy-communications` | a core with status **agreed**, and a named audience | provisional core: **refuse**, route to `strategy-shape` | scorecard: cannot say how success is judged. resources: cannot say what is being invested |

**The governing rule, verbatim in every locked output: a missing input locks a capability. It never degrades one into a guess.**

## 4. The menu — what the user can do next

Render it at the end of onboarding, as the closing move of every run, and whenever the user asks what they can do. Compute it from the capability table above and the Inputs block; never store it. Use `core-AskUserQuestion` so choosing an option starts the skill.

Three states, these words:

- **Available** — the question it answers, in the user's words, then the skill name
- **Limited** — same, plus one clause saying what is thin (`runs, but only 2 of 9 assumptions carry a threshold and a current value`)
- **Needs input** — same, plus **the one specific thing that unlocks it**. Never a generic "insufficient data"

Show the as-of date of each supplied input in the footer.

## 5. The source hierarchy

1. Primary evidence or a system of record. Finance, CRM, HR, the contract, the regulator.
2. Approved internal analysis, with date and author.
3. Authoritative external research, naming publisher and publication date.
4. Commentary and opinion, labelled as such.

A claim with no source does not appear. Say what is missing instead.

## 6. The output contract

Every output carries these, in this order.

1. The decision it supports, as one sentence.
2. Facts, each with source and date.
3. Assumptions, separately from facts, each with what would break it.
4. Estimates, with range and the basis for the range.
5. The recommendation, and one credible rejected alternative.
6. The strongest evidence against the recommendation.
7. Confidence, low / medium / high, with the reason.
8. What would change the answer, and when we would know.

## 7. The absence rule

Any check that inspects a set also reports the members of that set with the attribute missing: actions with no owner, commitments with no stop condition, objectives with no funding, key results with no baseline, assumptions with no threshold. Things that exist are visible and things that are absent are not, so the absent ones are counted deliberately. They are usually the finding.

## 8. Approval classes

- **Advisory.** The output informs a person who then acts. No gate. Analysis, gap reports, review packs, drafts.
- **Review before action.** Nothing changes a shared record without a named reviewer signing it off, and the reviewer is named in the artefact. Re-tagging an initiative, updating a register field, adding a counter-measure, correcting a baseline.
- **Prohibited delegation.** The work is human. Prepare the evidence and stop. Committing capital, changing headcount, choosing the problem, setting a target level, anything board-facing, anything affecting a named individual, anything irreversible.

### The apply protocol

Where a change is permitted it follows this sequence without exception.

1. Propose. State what would change, in which file and sheet, and why.
2. Show the difference. Current value and proposed value, side by side, for every field.
3. Wait for explicit approval. Silence is not approval, and neither is a general instruction given earlier in the conversation.
4. Apply, one sheet at a time.
5. Confirm what changed, naming the file, sheet and fields, and stamp the Index.

Never apply to a record not read in the same run. Never apply to more than one sheet per approval. If a write fails partway, report what landed and what did not, and do not retry blind. Writes are permitted only to the two working files. Never to a planning tool, an ERP or a semantic model.

## 9. The OKR house default

Declared, and overridable by the organisation: quarterly cadence, committed and aspirational marked separately, no 0.7 scoring convention, and **no grading of named individuals** — that last one is a hard rule, not a house style. Record whatever convention is in force in the Index.

## 10. Presenting to a CxO

### Answer first

1. The business question, in one sentence. 2. The answer, as a complete sentence. 3. The two or three most decision-relevant facts, no more. 4. The implication. 5. The recommendation. 6. The decision required. 7. Next steps with owner, timing and measure.

### Non-negotiables

Decision relevance. Strategic context. Hierarchy between conclusion and detail. **Comparative context — never a bare number.** A forward view. Transparent uncertainty. Closure: decision, owner, timing, dependencies, next review.

### Titles carry the message

A message title, not a topic label. "Revenue performance" is weak. "Revenue finished 6 per cent below plan as enterprise conversion slowed" is better. "Reallocate acquisition spend to enterprise onboarding to recover the gap" is stronger.

### Two layers, every run

**Layer 1, an Adaptive Card** via `core-render_ui`. Under 200 words of prose, standing alone. One `render_ui` call per response, so build the whole card in one go. Anatomy in order: a message-title `TextBlock` carrying the conclusion; a `ColumnSet` of three or four KPI columns each with label, value and comparator in the same order; the chart with its figures stated in a `TextBlock` beneath it; the decision table; a `Container` with `style: warning` holding the counter-case; a `Container` with `style: accent` holding the decision required; an `Accordion` for anything optional. Close with a standards note listing anything that failed a check and the evidence that would clear it.

**Layer 2**, the artefact: the health dashboard, or a document or workbook where the artefact is genuinely one of those. It holds the evidence, the full tables and the working, and references nothing off-host, so it survives being emailed and opened offline. `strategy-start` is the only skill exempt from layer 2.

**If the card fails after one retry**, fall back to markdown, say the card failed, and carry every obligation the card carried into the markdown, including the largest gap as a number in the first two lines. A failed card costs the picture. It never costs the answer.

### Charts

Safe types only: `Chart.HorizontalBar`, `Chart.VerticalBar`, `Chart.VerticalBar.Grouped`, `Chart.HorizontalBar.Stacked`, `Chart.Line`. **`Chart.Gauge` and `Chart.Donut` are banned** — they render unreliably and sit at the wrong end of the Cleveland-McGill accuracy ordering. A gauge is an actual against a target, so use a horizontal bar with both values. A donut is a part-to-whole, so use a stacked horizontal bar. State the figures in a text block directly beneath every chart. Time runs left to right, rankings sort by value, no non-zero baseline that distorts proportion, never encode status by colour alone.

### Anti-patterns that fail the output

Data dumping. Burying the answer. A number with no comparator. All-green reporting. False precision. Unsupported causality. No ask. No ownership.

## 11. Strategy Health.html — the dashboard

A deliverable, not a by-product. Self-contained, printable, and it must make sense to someone who was not in the chat. Created by `strategy-shape` at onboarding, refreshed by `strategy-review`; every other skill updates the Index and stamps the dashboard stale with a date rather than rebuilding it.

Header: organisation, period, core status, as-of date, and the files it was built from. Then five panels, in this order.

1. **Status strip** — period, core status, last run, last verdict, next review.
2. **Health** — key results on track / behind / **no data**, the third never hidden.
3. **Money** — stated against funded per core action, largest divergence leading.
4. **Risk** — assumptions at or near threshold, orphan initiatives, commitments with no stop condition, each as a count and a list.
5. **Capability** — Available, Limited, Needs input, computed from the capability table, each locked row naming its one unlock.

## 12. Checks — run these as the final numbered step of every skill

- Every material claim carries a source and a date.
- No assumption is presented as a fact.
- At least one real alternative is present, and it is not a straw man.
- The evidence against the recommendation is stated, not implied.
- Confidence is stated, and it is not "high" on thin evidence.
- The approval class is present, and the reviewer is named where the class requires it.
- Absence is counted, not just presence.
- Every number has a comparator.
- The handoff is named: one skill, and the input it needs.

Report every failure in a closing standards note. **Never end a run with the checks unrun.**

## Guardrails

- Never invent a name, number, date, owner, customer or commitment. Where a fact cannot be found, write a visible placeholder such as `[confirm Q3 headcount]` and say which lookup came back empty.
- Never soften a verdict into diplomatic vagueness. State the view and state the confidence.
- Never send anything. Draft only, and hand the send decision to the user.
- Meeting transcripts are evidence about what was said, not a performance record of any individual. Attributing a statement to a speaker is correct. Evaluating the speaker is a hard fail.
- A clean set of checks means the artefact is well formed. It is not proof that the strategy is right.
- End every output by naming the handoff and the menu.
