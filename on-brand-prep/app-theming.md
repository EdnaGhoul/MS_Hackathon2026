# App theming — serving a brand into an App Builder app

How Step 8 puts the active brand profile into an Exec Command Center app (React 19 + Vite +
Tailwind v4 + shadcn/ui). One deterministic script patches the theme tokens; the only LLM step is a
tiny iterate for the header logo. Test on a **second app instance** before touching a live one —
duplicate the app (or build a throwaway one) and run the command there first.

```bash
python /mnt/user-config/skills/on-brand-prep/scripts/apply_brand_to_app.py apps/<app_id> \
  --brand /mnt/user-config/brands/<slug>/brand.md          # add --dry-run to preview
python /mnt/user-config/skills/on-brand-prep/scripts/apply_brand_to_app.py apps/<app_id> --remove
```

## Token map (brand role → CSS variable in `src/index.css`)

| Brand role (brand.md) | `:root {` (light) | `.dark {` and the OS-dark mirror `@media (prefers-color-scheme: dark) { :root:not(.light) {` |
|---|---|---|
| **Primary** | `--primary` = Primary as `oklch(L C H)`; `--ring` = same | `--primary` = Primary with L raised to max(L, 0.63); `--ring` = same |
| *(derived)* | `--primary-foreground` = white or near-black, whichever gives the higher WCAG ratio over Primary (≥4.5:1 preferred, warned otherwise) | same rule against the dark primary |
| *(derived tint/shade)* | `--accent` = (H, C×0.15, L 0.95); `--accent-foreground` = (H, C×0.8, L 0.38) | `--accent` = (H, C×0.3, L 0.26); `--accent-foreground` = (H, C×0.2, L 0.90) |
| **Background** | `--background` — only when Scheme is light | left alone |
| **Text / foreground** | `--foreground` | left alone |
| **Secondary** | `--secondary` — only when the profile has one; `--secondary-foreground` = white or near-black by WCAG contrast over it (same rule as primary) | `--secondary` = Secondary with L raised to max(L, 0.63); `--secondary-foreground` by the same contrast rule |
| **Shape style** | `--radius`: "square"/"sharp" → `0.125rem`; "rounded … Npx" → N/16 rem; otherwise unchanged | — (`--radius` lives in `:root`) |
| **Body font** + Fallback stack | `@theme inline { --font-sans: '<Body>', <fallback>; }` | — |
| **Heading font** + Fallback stack | `@theme inline { --font-heading: '<Heading>', <fallback>; }` (falls back to `var(--font-sans)`) | — |
| **Primary logo** / **Dark-background variant** | copied to `src/assets/brand-logo.<ext>` / `brand-logo-dark.<ext>` | — |

Fonts marked `(default — not extracted)` or `(inferred)` are **not** applied — the app keeps its
bundled Geist. The script never installs a font: the machine renders the brand font only where it
is present, else the fallback stack (say so in the one-line note).

Why the dark values are written twice: the scaffold mirrors `.dark` into an OS-preference block so
the first paint matches the OS theme; if only `.dark` is patched, OS-dark users keep the neutral
indigo primary (see the app's own `THEMING.md`).

## What stays fixed — and why

- **`--chart-1..5`** — the chart palette is tuned for ≥3:1 on both backgrounds and for five
  mutually distinguishable hues; a brand palette rarely offers that.
- **`--destructive*`, status pills (red / amber / green / grey), evidence tags** — status meaning
  is carried by colour **+ shape + word**; rebranding them silently breaks that accessibility rule.
- **`--sidebar-*`, `--card`, `--popover`, `--muted`, `--border`, `--input`** — surface scaffolding;
  changing it is a redesign, not a rebrand.
- **`.warm {`** — the user-selectable surface theme (Auto / Light / Dark / Warm). It intentionally
  defines only neutral surface tokens (background, foreground, card, popover, secondary, muted,
  border, input, sidebar) and **no brand tokens**, so primary / accent / ring inherit from `:root`.
  The script never writes into it (its matchers target only `:root {`, `.dark {`, the
  `prefers-color-scheme: dark` block and `@theme inline {`, and it aborts if `.warm` changed). In
  Warm, the brand's background / foreground are overridden by the warm surfaces **by design**.
- Anything outside the three token blocks and `@theme inline`.

## Header iterate (the only LLM step)

Only when the script's JSON says `"header_iterate_needed": true` (a logo was staged). Hand the
app-generation skill exactly this, nothing more:

> In `src/pages/home.tsx`, add `import brandLogo from "@/assets/brand-logo.<ext>";`. Replace each
> of the three kicker paragraphs `<p className="text-[11px] font-semibold uppercase tracking-[0.08em]
> text-muted-foreground">Exec Command Center</p>` (loading, empty and main states) with:
>
> ```tsx
> <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.08em] text-muted-foreground">
>   <img src={brandLogo} alt="<Company>" className="h-6 w-auto" />
>   <span>Exec Command Center</span>
> </div>
> ```
>
> Change nothing else. Do not touch status colours, evidence tags, charts or any other file.

Then run the app's `check` (typecheck + build + lint) through the app skill and show the preview.

## Remove path

`--remove` copies `src/index.css.neutral` back over `src/index.css` byte-for-byte, deletes
`src/assets/brand-logo*.*`, and reports `"restored": true`. If it also reports
`header_iterate_needed: true`, hand the app skill the reverse iterate: drop the `brandLogo` import
and put the three plain `<p …>Exec Command Center</p>` kickers back. The neutral file is created on
the **first** apply and never rewritten, so re-applying a different brand still restores to the
original theme. No `index.css.neutral` → the script refuses (`exit 2`) rather than guess.

## Bookkeeping

The brand profile gets one Application-notes line — `Applied to Exec Command Center app <app_id>
on <date>` (the script prints it as `application_note`). Nothing else in the profile changes, and
extracted customer assets go only into **that customer's** app, never into an app or package
redistributed to others.
