# Section playbooks — how each block of the brief is computed

Order is fixed. Every fact traces to a tool result; every claim is badged. Time is the executive's
local time zone from config.

## 0. Read state and requests first
- `state-YYYY-MM-DD.json` (last 7 days): decisionsDone, hygieneDone, meetingsPrepared, ledgerOverrides,
  log. Carry ledger statuses forward; drop decisions marked taken unless new evidence reopens them;
  count closed items for the KPI trend.
- `requests/brief-*.json` without a matching `briefs/<date>-<eventId>.json`: answer them (meeting-brief.md).

## 1. Decisions required today
- Sources: decisions implied by today's customer meetings on at-risk items, unanswered asks from the
  manager or team, calendar conflicts needing a choice, expiring approvals/offers.
- Check SENT items for the last 24 h first: anything already sent changes the decision.
- Each item: status, evidence badge, title as a question, SCQA fields, lens verb, ask, links (email /
  chat / draft). A customer meeting on a deal at risk today always yields a decision.
- The **ask is self-contained**: if it involves sending or posting something, quote the suggested
  wording inline and link the thread — never "see Inbox" or "see section 4".

## 2. Day ahead (calendar completeness is mandatory)
- `ListCalendarView` bounded to today 00:00–23:59 local; then one request per day for the next 5
  working days. Follow every continuation. Never one week-wide request.
- Include EVERY event: recurring and modified instances, organiser-owned blocks, all-day/overnight,
  tentative, not-responded, declined (mark declined). Personal → kind "personal", title "Personal", no
  detail, masked brief.
- kind: accepted (accepted or organiser with attendees) · customer (external attendee/organiser or
  named account in title, regardless of response) · block (own solo recurring blocks) · optional
  (broadcasts, office hours, community calls not accepted) · personal.
- Reconcile: events in brief == events Outlook returned. State "Calendar: N of N Outlook events
  included" in meta.evidenceNote. Extend dayStart/dayEnd to cover every event.
- Brief on every event per meeting-brief.md.

## 3. Customer risk and escalations
- Scan mail + Teams (including account group chats) for escalations, blockers, pricing/seat
  negotiations, renewal or deal risk across ALL named accounts.
- Row: status, evidence, account, item (quote the operative words), owner, age, projectionDate +
  projection ("if nothing changes by…"), lens verb + action.
- Accounts with nothing new → risksNote "no new signals for …" (never green).

## 4. Inbox and Teams (last 48 h)
- Weight to manager, team members, named accounts. Split reply vs fyi.
- **Links come from unified search, not from the mailbox listing.** `outlook-ListMessages` and
  `outlook-GetMessage` return no web link; `m365_search-SearchM365` (sources email / teams) returns
  the "Open in Outlook" link and the Teams deep link. Use the listing to find items, then resolve
  EVERY item that goes into the brief (decisions[].links, inbox reply/fyi, preReads, sources) by
  searching its subject/quote with SearchM365 and copying that link. Never construct a URL; if search
  returns none for an item, leave `url` empty and say so in the item text.
- Emails needing a reply the executive has not answered (check sent items in the thread): create a
  reply draft (never send); reuse an existing draft by subject; put its link in draftUrl; channel
  "email"; action text "Draft reply ready — review and send".
- Teams asks: suggested reply text in action; channel "teams". Form/approval asks: channel "form".

## 5. Commitment ledger
- Promises the executive made in mail, chats, transcripts (last 7 days) + anything still open from
  earlier briefs. Row: status (overdue/open/waiting/closed), owner, due, age, evidence + note.
- Close only on evidence (sent item, reply, calendar change) or a state-file closure.

## 6. Calendar hygiene (next 5 working days)
- Proposals only: accept / decline / tentative / reschedule / flag, one-line reason each.
- Never propose declining or moving customer/partner meetings; never touch personal events.
- dayFlag: "no free block", "double-booked HH:MM", etc.

## 7. Team
- `GetDirectReportsDetails`. If reports exist: mode "directReports", members = reports, upn = email.
  Else: mode "frequentContacts" (top by mail + Teams exchanges in 14 days).
- Per member: lastTouch, lastOneToOne, nextOneToOne (events titled "1:1" or with both names),
  daysSinceOneToOne (null if none), waitingOnYou, youWaitOn, raiseNext, signal = blocked (explicit
  ask unanswered) / quiet (no touch in quietAfterDays) / nominal. Engagement facts only.

## KPI tiles
- decisions waiting · revenue at risk in deal-days (days left on the most time-bound approval/offer)
  · accepted calendar hours today · commitments overdue. Each: value, unit, status by fixed threshold
  from config, fires, decision served, trend vs history or "baseline forming", evidence badge.

## Write
- Validate with scripts/validate_brief.py. Write brief-DATE.json (new). Update latest.json in place
  (download → replace → upload). Answer requests into briefs/. Reply <300 words, governing answer first.
