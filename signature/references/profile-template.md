# Profile template

The canonical artefact Signature writes to `/mnt/user-config/skills/signature/profile.md`.

**Structure rules (keep these true — every reader depends on them):**

- Markdown only. `##` for sections, `###` for audience modes, `**Key:** value` for settings.
- Keys are stable; values are free text. A reader that does not recognise a value treats it as prose.
- **Every section is optional.** A missing section means "no preference" — the reader falls back to
  its default. Delete any section you don't want; nothing else breaks.
- **Every line is optional.** Omit a dimension rather than guessing a value for it.
- Append `(inferred)` to any value that was inferred rather than stated by the user. Name the
  source where it is useful — `(inferred — Teams)`, `(inferred — email)` — so the user can see
  which channel a setting came from and correct it.
- Keep it short. Under ~80 lines stays readable and cheap to load.

---

```markdown
# Signature profile — v1
Last updated: 2026-09-16

## Identity & context
**Name:** <from directory>
**Role:** <job title>
**Org:** <company / department / team>
**Works on:** <1-2 lines: products, accounts, domains, the actual day job>
**Process:** <the stages or frameworks they work in, e.g. discovery → design → pilot → scale;
             MEDDPICC; quarterly OKR cycle. Downstream skills use this so they don't start from zero.>
**Timezone / language:** <from settings>

## Voice dimensions
**Formality register:** formal | business-standard | conversational | blunt
**Directness:** bottom-line-up-front | context-then-point | narrative build
**Evidence density:** claim-only | one supporting number per point | data-heavy
**Hedging tolerance:** none (state it flat) | light qualifiers ok | hedge anything uncertain
**Jargon & acronyms:** plain English | industry-standard ok | internal shorthand ok (expand on first use?)
**Humour:** none | dry aside occasionally | warm and informal
**Voice:** first person ("I recommend") | institutional ("the team recommends") | mixed
**Structure:** bullets-first | prose-first | headed sections
**Length ceilings:** <e.g. email ≤150 words; exec summary ≤5 bullets; doc ≤2 pages>
**Opening / closing habits:** <greeting and sign-off patterns observed in their originated mail>

## Audience modes
Named modes holding ONLY the overrides that differ from the dimensions above.
Anything not listed inherits from Voice dimensions.

### Executive sponsor
**Directness:** bottom-line-up-front
**Length ceilings:** ≤5 bullets, no preamble
**Evidence density:** one supporting number per point

### Customer
**Formality register:** business-standard
**Jargon & acronyms:** plain English, expand every acronym
**Hedging tolerance:** light qualifiers ok — never commit to dates or numbers on their behalf

### Internal team
**Formality register:** conversational
**Voice:** first person
**Structure:** bullets-first

## Lexicon & guardrails
**Preferred terms:** <term → use instead of …>
**Banned terms:** <style words to avoid, with a replacement where there is one —
                  e.g. leverage → use; utilise → use; synergy → (drop)>
**Acronym policy:** expand on first use | assume audience knows | avoid entirely
**Never say:** <claims, commitments or phrases that must never appear — e.g. no delivery dates,
               no pricing, no competitor comparisons, no "guarantee">
```

---

## Notes for the writer of this file

- **Audience modes are overrides, not copies.** Never restate a dimension in a mode unless it
  differs; a duplicated value is a future inconsistency.
- **2-4 modes.** More than four and the reader cannot pick reliably; fewer than two and the
  section is not earning its place.
- **Dimensions, not adjectives.** "Professional but friendly" is unusable. `Formality register:
  business-standard` + `Humour: dry aside occasionally` is.
- **Never say is a hard list**, distinct from Banned terms: banned terms are style, never-say is a
  constraint the user does not want crossed.
