# The consumption contract

Copy the block below **verbatim** into any sibling skill in the cohort — normally as a
`## Voice & context (Signature)` section just before the drafting step. It is deliberately short:
loading Signature must cost one file read and nothing else.

---

```markdown
## Voice & context (Signature)

Before producing user-facing prose, load the user's Signature profile:

1. **Read** `/mnt/user-config/skills/signature/profile.md` (one read, at drafting time — not at
   skill start, and never more than once per turn).
2. **Missing, empty or unreadable? Proceed with defaults** — business-standard formality,
   bottom-line-up-front, bullets for anything over three points, plain English, no humour. Do not
   block, do not interrogate the user, do not run a setup interview. You may mention once, in one
   short line at the end, that "set up my Signature" would personalise this — then drop it.
3. **Apply it as context on the draft you were already producing.** No verification pass, no
   rewrite pass, no second model call. Signature nudges; it does not gate.
4. **Pick one audience mode** if the `## Audience modes` section exists and the audience is clear
   (exec sponsor / customer / peer / internal team). Its settings override the global
   `## Voice dimensions`; anything it does not list inherits from them. No clear match, or no such
   section → use the global dimensions alone.
5. **Honour `## Lexicon & guardrails` literally** — banned terms and the never-say list are the
   one part of the profile to treat as hard constraints.
6. **Precedence: an explicit instruction from the user in the moment always beats the stored
   profile.** The profile only fills silence. A one-off instruction is not a preference — don't
   store it.
7. **A section that isn't there means "no preference"** — fall back to your default for it and
   carry on. Never error on a missing or hand-edited section.

If the user corrects tone, length or structure of what you produced, hand that correction to the
`signature` skill as durable drift (generalised to a dimension, not the verbatim phrase) and
acknowledge it in at most one line.
```

---

## Why it is shaped this way

- **One read, at drafting time.** Reading at drafting time means the profile is loaded only when
  prose is actually produced — a data-only or tool-only turn pays nothing.
- **Defaults instead of a blocked turn.** The most common failure mode for an identity layer is a
  skill that refuses to work until onboarding is done. Signature is a substrate: a new user with no
  profile must get a good answer, just a less personalised one.
- **Overrides, not merges.** Mode beats global, field by field. No deep-merge logic, no precedence
  table to get wrong.
- **Guardrails are the only hard part.** Everything else is a nudge; banned terms and never-say are
  constraints the user asked for explicitly.
- **Fail soft on malformed input.** The file is hand-editable by design, so it *will* be edited by
  hand. Every reader must tolerate a missing section, a reordered file, a typo'd key and a deleted
  line without erroring.
