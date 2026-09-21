# Data contracts — what each phase writes, and what reads it

v1 was a set of rules for an agent. v2 is a pipeline with contracts: **agents
produce data, scripts produce documents.** An agent's output is a JSON file that
validates against a schema; no agent writes HTML or Word markup. That is what
removes the "found but not shown" class of defect — the figure list in the
document is computed from the manifest by code, so it cannot drift from what was
captured.

## Run directory — everything under `working/dfa/<run-id>/`

```
subjects.json                      # [{slug, name, org, role_claimed, aliases[]}]
run.json                           # depth, capture_budget, brand, budgets, sample_date
<slug>/
  report.json                      # the content model      (schemas/report.schema.json)
  assets.json                      # the photo manifest     (schemas/assets.schema.json)
  capture_log.jsonl                # one line per capture attempt
  img/asset-NN.png + asset-NN.json # cropped PNG + provenance sidecar
  shots/                           # raw browser screenshots, kept for audit
  build/<slug>-digital-footprint.html
  build/<slug>-digital-footprint.docx
  qa/page-NN.png                   # rendered Word pages for visual QA
roster-summary.json                # N > 1 only
```

`run.json` fields: `depth` (standard | deep) · `capture_budget` (default 8
capture ATTEMPTS per subject) · `max_attempts_per_subject` (default 24) ·
`max_minutes_per_subject` (default 12) · `brand` (default | kerry) ·
`sample_date` · optional `cdn_pattern` (the organisation's image-server rule,
resolved ONCE and handed to every subject).

## The build stamp — how a document proves it came from the pipeline

"Agents produce data, scripts produce documents" is the design principle, and a
principle that can be skipped will be skipped under load — a roster is long, and
hand-writing the HTML looks faster than wiring up the renderer. So the rule is
made checkable rather than merely stated.

Both renderers embed a stamp: `dfa2-<v> <slug> <digest> shown=<M>/<N>`, where the
digest is a SHA-256 over `report.json` + `assets.json` exactly as the renderer
read them. It lives in an HTML comment and in the DOCX core properties, so no
reader ever meets it.

`built_by_pipeline` is the FIRST check in both gates, and it fails three ways:

| Result | Means |
|---|---|
| no stamp | the file was hand-written — every other check is then meaningless, because there is no manifest behind it |
| stale | the model changed after the file was rendered; re-render, never hand-patch |
| version mismatch | built by an older renderer; re-render |

This is what stops the v1 defect returning in a new costume: a hand-built report
can satisfy every structural check — chips, pills, section counts — while having
no reconciliation behind it at all.

## report.json — the content model

Every chip, pill and classification the report spec requires is a **typed
field**, so no renderer can drop it and the gate can count it from the source
rather than from the output. Key structures:

```
subject            {slug, name, org, role_verified, sample_date}
layer1.headline    one sentence a reader could disagree with
layer1.key_figures exactly 4   {label, value, note}
layer1.searcher_finds 2-4 sentences
layer1.scorecard   exactly 6   {dimension, verdict, evidence} — fixed order, fixed vocabulary
layer1.fixes       exactly 3   {title, what, effort: Low|Medium|High, why}
first_impression   [{query, rank, title, url, class}]  class ∈ company-owned |
                   editorial | sponsored | aggregator | auto-generated |
                   data-broker | wrong-person
sections.career / public_profile / network / title_variants   [ROW]
sections.topics    {quotes: [{text, said_where, date, url}], themes: [{theme, weight, evidence_count}]}
sections.media     {coverage: [ROW], adverse: [ROW], not_covered: [""]}
sections.digital_social {by: [ROW], about: [ROW], not_assessable: [ROW]}
sections.inventory_lead  prose carrying the visual-record findings
sections.av_items  [{kind: VIDEO|AUDIO, title, host, date, duration, title_used,
                    on_screen, finding, url}]   — text rows, never pictures
assessment         {best_known_for, unfamiliar_concludes, strong[], gaps[], fixes_ranked[]}
limitations[] · sources[{url, title, accessed}] · confidence {level, statement}

ROW = {tag: FACT|FLAG, marks: [SINGLE-SOURCE|NOT VERIFIED], finding, date,
       title_used, url, accessed}
```

## assets.json — the photo manifest, the single source of truth for section 7

One row per candidate photograph, carrying discovery metadata, the capture
result, the verification decision and the placement width. Discovery, capture,
QC, both renderers and both gates all read and write this one file.

```
{"subject": "...", "capture_budget": 8, "assets": [{
   "id": "asset-01", "candidate_source": "search_images|browser_grid|page_caption",
   "page_url": "...", "image_url": "...", "image_url_best": "...",
   "native_w": 2000, "native_h": 1452, "host": "...",
   "caption_verbatim": "...", "title_attached": "...", "title_outdated": false,
   "credit": "", "licence": "", "context": "corporate headshot|event|stage|press|award|other",
   "descriptive_title": "...", "dedupe_group": "g1", "rank": 1,
   "state": "shown", "reason": "",
   "file": "img/asset-01.png", "sidecar": "img/asset-01.json", "placement_mm": 80,
   "verification": {"by": "view", "matched_against": "...", "result": "match|no-match|unsure"},
   "attempts": 3}],
 "summary": {"found_distinct": 7, "attempted": 7, "verified": 6, "shown": 6,
             "budget_applied": false}}
```

`summary` is **recomputed by the scripts**, never hand-maintained.

## The asset state machine

```
candidate ─▶ queued ─▶ capturing ─▶ captured ─▶ verified ─▶ shown
                │                     │            │
                ├─▶ duplicate         ├─▶ unverifiable (face not identifiable at any reached size)
                ├─▶ not_photo         ├─▶ wrong_person (inspected, discarded)
                ├─▶ budget_capped     └─▶ exhausted (A+, A, B, C, D all reached a host and failed)
                ├─▶ budget_exhausted (subject budget hit before this asset was tried)
                ├─▶ browser_unavailable (the browser died — retryable, NOT a host refusal)
                └─▶ unresolved_address (no image address was ever resolved)
```

`browser_unavailable`, `unresolved_address` and `budget_exhausted` are **run
failures**: the web never refused anything, and the right response is to re-run,
not to publish. `accept_report.py` blocks any report that shows under half the
photographs it found when the shortfall traces to one of them.

Terminal: `shown, duplicate, not_photo, budget_capped, unverifiable,
wrong_person, exhausted, budget_exhausted`. `plan_capture.py --finalize` refuses
to close a subject while any asset is still `captured`, `capturing` or queued
with rungs left, and refuses to close at all when the capture log is empty.

**The reason line is generated, never typed.** It is a template over the state
plus the attempt log — `exhausted` becomes "every route to the file refused: the
original refused (403); the search detail view failed to render it; …". This is
what eliminates the bare "403" and "paywalled" rows, which are first-rung
failures with four rungs still below them.

## capture_log.jsonl

One line per attempt:

```
{"ts", "asset_id", "tier": "A+|A|B|C|D", "url", "browser_url_returned",
 "outcome": "ok|http_403|login_wall|not_found|tab_mismatch|timeout|not_photo", "shot"}
```

`tab_mismatch` — the returned `browserState.url` is not the URL that was
requested — is what makes browser contention **visible** instead of silently
producing another subject's face. Neither it nor `browser_unavailable` advances
the ladder or contributes to an `exhausted` reason: an attempt that never
reached a host says nothing about the host.
