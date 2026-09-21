# App source — Exec Command Center

React 19 + Vite + Tailwind + shadcn/ui (App Builder scaffold). Deploy through the app-generation skill.

This zip ships **generic** — no customer names, no fixed counts, no connection ids. Every header sentence,
section answer and pill is derived from the loaded brief (schema v2, `src/types/brief.ts`). The header greets
the signed-in user by their **directory first name** (Office 365 Users `MyProfile_V2` → `givenName`, falling
back to the first token of `displayName`, then of `meta.owner`), shows the governing answer as the one bold
sentence, and a single muted line `dayLabel · Updated HH:MM · Calendar n of m`. The full evidence note lives
in the footer under "How this brief was built". KPI tiles **1 (decisions)** and **4 (overdue)** update live as
the user ticks decisions or cycles ledger statuses; their RED/AMBER/GREEN is recomputed from the tile's own
published threshold string. Personal calendar events are always rendered as "Personal" — title and note masked.
A header theme switch (Auto · Light · Dark · Warm; `src/lib/theme.ts`, `.warm` in `src/index.css` overrides neutral surfaces
only, never brand tokens) persists the choice to `ExecCommandCenter/settings.json` (localStorage cache for first paint; MOCK_MODE → localStorage only).

## Mock-up phase (install step 1c)

1. `src/data/mock-brief.json` is already present (fictional, schema v2). Optionally personalise it for the
   executive (name in `meta.owner`, day label, plausible-but-fictional items) — never real data.
2. In `src/lib/brief-store.ts` set `MOCK_MODE = true`.
3. Leave the two connector imports pointing at `./mock-connectors` (typed stand-ins; every method throws
   "Connector not bound", and in MOCK_MODE the store never calls them). No connectors are bound in this phase;
   a MOCK-UP banner shows; actions are kept in memory and not saved.
4. Run type-check, lint and build check; preview.

## Build phase (install step 1e)

1. Bind **OneDrive for Business** (action) and **Office 365 Users** (action) via the app-data-connectivity
   flow. This produces the `generated/` client folder (not in this zip).
2. In `src/lib/brief-store.ts` repoint the two imports:
   ```ts
   import { OneDriveforBusinessService } from "../../generated/services/OneDriveforBusinessService";
   import { Office365UsersService } from "../../generated/services/Office365UsersService";
   ```
3. Delete `src/lib/mock-connectors.ts` and `src/data/mock-brief.json`.
4. Set `MOCK_MODE = false` and set `FOLDER` to the configured OneDrive folder (default `ExecCommandCenter`).
5. Run type-check, lint and build check; preview; then publish through the skill.

## Files

- `src/pages/home.tsx` — the page: header, KPI tiles (live for decisions/overdue), six sections, team, footer.
  All copy is derived from `data`; `statusFromThreshold()` parses `RED ≥ 3 · AMBER 1–2 · GREEN 0`-style strings.
- `src/components/meeting-brief-panel.tsx` — one-minute meeting brief panel (request → OneDrive → reply).
- `src/lib/brief-store.ts` — OneDrive read/write, roster (direct reports), `loadMyProfile()`, `loadSettings()`/`saveSettings()`, requests, MOCK_MODE, FOLDER.
- `src/lib/theme.ts` — theme class mapping (auto → none, light → `light`, dark → `dark`, warm → `light warm`) and localStorage cache.
- `src/lib/mock-connectors.ts` — mock-up-phase stand-ins for the generated connector clients (delete at build).
- `src/data/mock-brief.json` — fictional sample brief for the mock-up phase (delete at build).
- `src/types/brief.ts` — schema v2 types. `src/index.css` — theme tokens.
