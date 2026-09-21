# One-minute meeting brief

Fill `event.brief` for EVERY calendar event. Depth follows kind.

## Inputs
The event (attendees, organiser, series); the most recent transcript of the same series (look it up —
do not skip for recurring meetings); mail and chats with the attendees in the last 14 days; files
attached to the invite or shared in those threads; the executive's open ledger items involving these
people; the account's risk row.

## Contract (exact keys)
```
readTime: "1 min" | "30 sec"
stake:      { text, evidence }                       — what's at stake and why it matters; or "Routine — no decision expected"
decisions:  [{ text, owner, deadline }]              — only decisions the executive owns
preReads:   [{ title, url, why, minutes }]           — max 3, must exist and be linked; never suggested reading
questions:  [{ rank 1–5 (no ties), text, impact }]  — exactly five, ranked by the size of the decision each unlocks
outOfTime:  { criticalDecision, fallback }           — the single decision that must be made; what happens if not
sources:    [{ type: email|chat|transcript|file|calendar, label, url }]
generatedAt
```

## Depth by kind
- **customer / accepted** — full brief, ≤ ~220 words excluding pre-read titles.
- **optional / block** — 30-second brief: one or two sentences of stake plus the single reason it
  might matter today; decisions only if one genuinely exists; pre-reads only if a recording/agenda
  exists; questions filled to five with the first one or two real and the rest "—" (impact "No
  further question warranted"); outOfTime = "None — no decision expected." / "Skip or leave early
  without consequence."
- **personal** — masked: stake "Personal — no brief prepared", empty lists, empty outOfTime strings.

## Rules
- Tie the stake to a decision, deal, risk or relationship already in the brief.
- Every element badged; a meeting with no discoverable context gets a short honest brief, never padding.
- On-demand requests (`requests/brief-<date>-<eventId>.json`) are answered into
  `briefs/<date>-<eventId>.json` with the same contract.
