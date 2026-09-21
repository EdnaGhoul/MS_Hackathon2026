# Brand brief

The block the orchestrator pastes, filled in from the active `brand.md`, into any deck, document,
spreadsheet, dashboard, page or image request as context — always together with
[design-principles.md](design-principles.md). Under twenty lines, no commentary. Fill only what the
profile has — a line with no value is dropped, not invented.

```markdown
## Brand brief — <Company> (brands/<slug>/brand.md)
Palette: primary #RRGGBB · secondary #RRGGBB · accent #RRGGBB · background #RRGGBB · text #RRGGBB
Chart order: primary, secondary, accent, accent 2
Fonts: heading <name> · body <name> · fallback <stack>
Logo: brands/<slug>/assets/logo.png — 1200×260, transparent PNG, aspect 4.6:1 (wordmark); clear space ≈ its height
Scheme: light | dark
Contrast: text/bg 14.2:1 ✓ · primary/bg 3.1:1 — large text only: keep the primary on surfaces and charts, body text uses the text role
Marked (inferred) or (default — not extracted): <roles, if any>
Rules:
- An explicit instruction from the user in this request beats the stored brand.
- Missing logo → place nothing. Never draw, generate or substitute one.
- Say in one line what could not be applied (font dropped, fill unsupported, logo absent).
Apply with references/design-principles.md:
- One highlight colour per view — the primary; grey for context; ≤10% of the surface in brand colour.
- Statuses stay red / amber / green, always colour + shape + word; never rebrand them.
- Logo once per artefact (title slide / cover / header), ≤ 1/8 width, clear space ≈ its height.
- Answer first: action titles state the conclusion; one message per slide or section.
- Text ≥ 4.5:1 — when the brand fights legibility, legibility wins; say so in one line.
- Charts on a live Office file: theme first; replace, don't leave default colours — ask once.
```

How to fill it: read `brands/active.md` → the slug → `brands/<slug>/brand.md`. No active brand or
no profile → skip the block, use neutral defaults and carry on; never ask the user to set one up
mid-request (one closing line "say *set up my brand* to make this on-brand" at most).
