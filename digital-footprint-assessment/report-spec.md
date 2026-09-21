# Report specification — structure and fixed scoring scale

## Fixed score vocabulary

Use these words **only**. The point is comparability: one person assessed today must line up against another
assessed next month, and against a whole roster.

| Dimension | Allowed one-word verdicts (best → worst) |
|---|---|
| Credibility | Strong / Adequate / Thin |
| Adverse material | Clean / Minor / Material |
| Distinctiveness | High / Moderate / Low / Absent |
| Discoverability | Strong / Adequate / Diluted / Invisible |
| Consistency | Consistent / Mixed / Inconsistent |
| Momentum | Rising / Steady / Slowing / Dormant |

All six, in that order, each with **one sentence of evidence**. No half-grades, no invented words.

What each dimension means:

- **Credibility** — do the facts corroborate across independent sources without contradiction?
- **Adverse material** — is there critical, disputed or damaging material in credible sources? `Clean` is always bounded by what was not searched.
- **Distinctiveness** — is there a story that is theirs, or only their job description?
- **Discoverability** — can an ordinary searcher find the right person quickly?
- **Consistency** — do name, title, employer and imagery agree across the web?
- **Momentum** — is the record current, or is the substance years old?

## Layer 1 — the one-page card (must stand alone)

1. **Headline finding** — one sentence stating *what the evidence shows*. Not a compliment, not a job summary; a finding someone could disagree with.
2. **Four key figures** — countable things: title variants live, years in a role, sources reviewed, adverse items, wrong-person results in the top five.
3. **What a searcher actually finds** — two to four plain sentences on the first screen.
4. **The six-dimension scorecard** — verdict plus evidence sentence.
5. **The three fixes that would change the record** — each with what it involves, the effort, and why it matters.

## Layer 2 — the evidence pack

In this order, every substantive line carrying a **full URL** and the access date:

1. First-impression sample (both queries, first screen, in order, each result classified)
2. Career and professional background
3. Public profile — appearances, in date order, with the exact job title used on each page
4. Topics and messages — verbatim quotes, then themes ranked by weight of evidence
5. Media presence — significant coverage, then adverse material, then what was not covered
6. Digital and social presence — published *by* vs published *about*
7. Photo, video and audio inventory — with rights and credit (see the required shape below)
8. Professional network and registers
9. Title variants and naming consistency — plus renamed or restructured organisations
10. Assessment — best known for · what someone unfamiliar concludes · what is strong · what is missing, outdated, inconsistent or hard to find · fixes in priority order
11. **Limitations**
12. **Complete source list**
13. **Confidence** — a level, plus a plain statement of what could not be checked and why

## Section 7 — required shape

Section 7 is a **table with one row per asset**, and every photographic row carries an **Image** cell holding
either the picture itself or a stated reason it is absent. A row with neither is a defect, not a gap — the
structure exists so that "documented but not shown" cannot ship silently.

| Column | Photograph | Video / audio |
|---|---|---|
| Image | The captured picture, placed at or below its `place<=` width — **or** a reason: "403 on the original", "below the sharpness floor", "duplicate of asset 1", "login-walled" | **Always** an em-dash. Never a picture — see the scope rule in the capture reference |
| Where published | Page URL and host | Platform, URL |
| Date | Publication or capture date | Publication date, duration |
| Caption / title used | The caption verbatim, and **the job title it attaches** | The title used |
| Credit / licence | Photographer, agency, CC terms, or "all rights reserved (default)" | As stated |
| Finding | Outdated title, recurring canonical headshot, single asset propagating across outlets | Whether the subject actually appears; who is on screen |

Before publishing, **count the pictures against the photographic rows**. They must agree, or every unmatched
row must carry its reason. A gallery that shows one image beneath a list of five URLs is the exact failure
this shape prevents.

## Labelling rules

- **Fact vs analysis must be visibly separated.** Sections 1–9 are fact. Section 10, the theme ranking and the scores are analysis. Say so in the document.
- Tag each finding `FACT` or `FLAG`; mark `SINGLE-SOURCE` and `NOT VERIFIED` inline.
- Never let internal scaffolding — workspace paths, session ids, tool names — reach the document body. Reader-facing attribution only.

## Things that reliably turn up, and are worth checking every time

- **The employer's own page is often the error source**, and databases republish it verbatim — so one defect propagates everywhere. Test it rather than trusting it.
- **Superseded titles persist** on conference sites, association pages and university alumni pages long after a role changes.
- **Renamed entities** — a board seat or business unit named on a bio may no longer exist under that name.
- **Auto-generated biographies** on aggregator sites frequently present an old role as current, and can rank first.
- **Name collisions** — unrelated people with the same name dilute the first screen.
- **Login-walled platforms** are usually the subject's largest owned channel and usually cannot be assessed. Say so.
- **A single corporate image library behind many URLs.** Where an organisation serves every executive headshot from one digital-asset manager, a dozen result URLs can resolve to ONE photograph at different crops or presets. That is one asset and a genuine consistency finding — not a dozen images, and never a reason to pad the gallery.
- **Roster-wide patterns outrank individual ones.** When the same defect — an inconsistent title convention, a stale leadership page, an employer-only record — appears across most of a team, the pattern is the finding and it belongs in every affected report as well as the roster summary.

## Boundaries

- Public professional information only. No private life, family, health, relationships, beliefs, politics or personality; no personal contact details.
- This assesses a public **record**, never a person's competence or performance.
- Search visibility is a point-in-time sample. Date it, and say so.
