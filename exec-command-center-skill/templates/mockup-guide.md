# Mock-up phase — how to personalise the example brief

Start from `brief.example.json`. Replace, from `ecc-config.json`:
- `meta.owner` → identity.name; manager references → identity.manager; `meta.evidenceNote` →
  "MOCK-UP — fictional data for layout review".
- Account names (Northwind, Fabrikam, Tailspin, Adatum, Woodgrove) → the configured accounts, keeping
  the storylines fictional (an expiring offer, a briefing day, a closed invoice, quiet accounts).
- Lens verbs → the configured lens (sales: Unblock / Reallocate / Change play / Reset commit;
  finance: Fund / Defer / Reallocate / Set conditions; technology: Prioritise / Accept trade-off /
  Retire / Invest; general: Decide / Delegate / Defer / Escalate).
- `kpis[].threshold` → the configured bands, and recompute each tile's `status` from its value.
- `team.mode` → configured mode; member names fictional; `signal` values illustrate blocked / quiet /
  nominal so the executive sees all three states.
- Protected calendar: keep one `personal` event so the masking is visible.
- Every `url` stays empty. No real names, IDs or links anywhere.

Validate: `python scripts/validate_brief.py <mock>.json --outlook-event-count <events>`.
Copy to the app as `src/data/mock-brief.json`, set `MOCK_MODE = true` in `src/lib/brief-store.ts`.

Typical refinements the executive asks for, and where they land:
| Change | Where |
|---|---|
| Section order, collapse defaults, wording | app iterate (home.tsx) |
| Which KPI tiles / thresholds | config → mock brief → schedule prompt |
| What counts as a customer meeting | config.accounts → schedule prompt |
| Team section: reports vs contacts, quiet days | config.team |
| Lens vocabulary | config.lens |
| Density / fonts / colours | app iterate (index.css tokens) |
