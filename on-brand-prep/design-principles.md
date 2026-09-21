# Design principles — executive-audience rules served with the brand brief

Served alongside [brand-brief.md](brand-brief.md) to whatever authors the deck, document,
spreadsheet, HTML dashboard or image. The brief says **which** colours, fonts and logo; this page
says **how much, where and when**. Not for Step 8 (App Builder apps) — the app receives tokens via
`scripts/apply_brand_to_app.py`, never prose.

Grounding, in one line each: **Minto / SCQA** — lead with the answer, then the support.
**Tufte** — maximise data-ink, remove chartjunk. **Few / Knaflic** — pre-attentive focus: one
highlight colour, grey for context. **IBCS** — same message, same notation and chart shape
everywhere. **WCAG 2.2** — ≥4.5:1 text contrast, information never carried by colour alone.
**Cleveland–McGill** — readers decode position more accurately than length, length more than angle
or area.

## Colour budget

- Roughly **60% neutral surfaces** (background, cards, table bands) / **30% text and structure**
  (text role, borders, grey series) / **≤10% brand primary** as emphasis.
- **ONE highlight colour per view** — the brand primary. It marks the thing the reader must see
  first: the key number, the one series that matters, the action title accent.
- Secondary and accents are for **categorical distinction in charts only**, in the profile's
  **Chart order**; never as decoration, never as a second highlight on the same view.
- **Never recolour semantic statuses** (red / amber / green / grey) to brand hues. Status is always
  **colour + shape + word** (● ▲ ■ plus "On track" / "At risk" / "Off track").
- Primary fails 4.5:1 on the background → surfaces and chart fills only; body text stays in the text role.

## Typography

- **Heading font for titles only**; body font everywhere else. Corporate fonts render only where
  installed — use the fallback stack and say so in one line.
- **Max 3 sizes per artefact** (title / heading / body). Sentence case. **Body ≥ 11 pt in print,
  ≥ 14 px on screen**; line length 45–75 characters.
- **Action titles** state the conclusion ("Churn fell 12% after the pricing change"), not the topic
  ("Churn update").

## Layout & whitespace

- **One message per slide or section.** **Answer first** — summary before detail, conclusion before
  evidence (SCQA: situation → complication → question → answer, answer stated up front).
- Consistent grid and margins across the artefact; group related items by proximity; align to a
  single left edge unless the template says otherwise.
- **Logo once per artefact** — title slide, document cover / running header, dashboard header — at
  **≤ 1/8 of the width** with **clear space ≈ its own height**. Never on every chart, never in every
  page corner, unless the customer's template already does.

## Charts

- Choose the form by the question: **sorted bars** for ranking, **lines with a target line** for
  trends, **dot plots** for actual-vs-target, **stacked bars only for composition of a total**.
- **No pies, 3D, gradients, shadows or dual axes.** Bars start at zero. Direct labels beat legends.
- **Muted grey for every series except the one that matters**, which gets the brand primary. Several
  categories that all matter → Chart order, still one emphasised.
- Same message → same chart shape, scale and colour across the artefact (IBCS). Consistent number
  formats, units in the title or axis label once, not on every value.

**Existing charts on the live Office surface** (Excel / PowerPoint already open):

1. **Set the theme colours to the brand FIRST** — charts inherit theme accents, so this alone
   recolours what can be recoloured.
2. **An existing chart cannot be recoloured in place.** Ask the user once: *"Replace it with an
   identical chart in brand colours?"* On yes: after the theme change, add the new chart with the
   same data (sorted per the rules above), then remove the old one — PowerPoint: rebuild the
   slide; Excel: move it to a hidden sheet if delete is unavailable.
3. **Only if that genuinely fails, say so in one line.** Never silently leave default-coloured
   charts, never fake it.

## Tables

- Right-align numbers; thousands separators; **max 2 decimals**; units in the header.
- **Header row in a muted neutral surface, not the brand primary**; zebra striping optional and faint.
- RAG columns as **shape + word**, colour optional. Sort by the thing the reader ranks on.

## Per artefact

| Artefact | Apply the brand as |
|---|---|
| **Deck (pptx)** | Logo on the title slide only; section dividers may use the brand primary sparingly (one flat fill, white text if ≥4.5:1); ≤ 6 lines of body per slide; one chart per slide; action titles. |
| **Document (docx)** | Cover with logo; running-header logo optional and small; headings in the heading font, body in the body font; callouts in an accent **tint** (~10% of the primary), never a saturated fill behind body text. |
| **Spreadsheet (xlsx)** | Leave the modelling convention alone (blue text = inputs, black = formulas, green = links). Brand only in the header band (primary fill + contrasting text) and chart series in Chart order. |
| **HTML / dashboard** | Map roles to CSS tokens (primary → `--primary`, text → `--foreground`, background → `--background`); same status and one-highlight rules; grey for context series. |
| **Image** | Brand palette as the **dominant hues** of the composition; logo only if the profile has one, and only pasted as the asset — never generated or redrawn. |

## Accessibility

Text ≥ 4.5:1 against its background (≥ 3:1 for large text and graphical objects); never colour
alone; alt text on every logo and chart image; heading structure real (styles), not faked with bold.

## When the brand fights the rule

**Legibility wins.** A brand primary that fails contrast moves to surfaces; a brand that wants the
logo on every page gets it once unless the template shows otherwise; a status palette stays
red/amber/green even when the brand is red. Tell the user in one line what you kept back and why.
