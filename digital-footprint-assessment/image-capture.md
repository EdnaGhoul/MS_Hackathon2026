# Image capture ladder — publication-grade evidence images

The photo/video inventory is a priority section. A soft, blocky picture makes the whole report look
unreliable, so capture quality is gated, not assumed.

**The rule: get as close to the ORIGINAL image file as possible, and never enlarge.**

## Scope — what may be captured at all

**Photographs of the subject. Nothing else.** Before capturing anything, ask what the picture depicts. If the
answer is not "the subject, photographed", do not capture it.

| Asset | Capture it? |
|---|---|
| Corporate headshot, event photo, stage shot, press photo of the subject | **Yes** — this is the job |
| Video thumbnail, still frame, auto-generated frame (`maxresdefault.jpg`, `hq1/2/3.jpg`) | **No** |
| Podcast cover art, episode card, channel banner, show masthead | **No** |
| Screenshot of a bio page, team listing or directory entry | **Only** when the page itself is the finding — a visible defect, a superseded title rendered on screen. Never as decoration |
| Logo, product shot, building, generic stock imagery | **No** |

**Video and audio are TEXT ROWS in the inventory — always, without exception.** They get a row carrying date,
platform, duration, reach, the exact job title used, and any finding. They never get a picture. The temptation
is real and it is wrong: an A/V thumbnail is usually sharp, easy to reach at Tier A, and captioned with the
subject's name — so it sails through the quality gate while depicting a host's face, a show logo or a title
card. A reader scanning the report reads a displayed picture as "this is them". Do not create that false
impression to fill a section.

Findings ABOUT video and audio are valuable and belong in the report — in prose. "The episode frame shows the
host, not the subject." "Three sampled frames are identical; it is audio over a static card, so no footage
exists." "No moving-image asset of this person could be located anywhere." Those sentences carry the finding
honestly. A thumbnail pasted beside them does not.

Investigating A/V is still expected — sample frames, trace a film to its source, check who is actually on
screen. Just report the result in words and discard the captures.

## Coverage — how many photographs to capture

**The inventory sets the count, not a fixed number per person.** Every distinct photograph you document in
section 7 gets a capture attempt, because section 7 must SHOW what it documents. One portrait per subject is
the wrong default: it produces a report that lists five published photographs and displays one, which tells
the reader either that nobody looked or that the subject has almost no imagery — and neither is the finding.

What counts as distinct:

| Situation | Assets |
|---|---|
| The same canonical headshot republished by five outlets | **ONE.** Capture it once; record the recurrence — it is a real consistency finding |
| One corporate image library serving many URLs at different crops or presets | **ONE.** Reach for the largest rendition (Tier A+) and note the pattern |
| A corporate headshot, a conference stage photo, and an award presentation | **THREE.** Different photographs, different contexts, different captions to check |
| A photograph appearing with two different job titles in its captions | **ONE** asset, but the discrepancy is a finding in the title-variants section too |

**Cap at six per subject.** Beyond six, capture the six most significant — most recent, most independent of
the employer, most widely republished — list the remainder as text rows, and say you capped. The cap keeps a
ten-person roster finite; without it the browser work is unbounded.

**Record a reason for every documented photograph you do not capture** — 403 on the original, below the
sharpness floor, duplicate, login-walled. An uncaptured row is a legitimate outcome; an unexplained one is not.

**When delegating capture, hand over this rule — never a number.** A subagent told "capture a portrait of each
person" returns exactly one each and reports success; the ceiling in the brief becomes the ceiling in the
report, and the parent's intent never reaches it. Brief the rule: capture every distinct photograph the
subject's inventory documents, up to six.

## Why this matters

Measured on the same photograph, same pipeline:

| Method | Captured pixels | Sharpness (var. of Laplacian) |
|---|---|---|
| Tile cropped from a search-results grid, then enlarged 2× | 304 × 184 | 156 |
| Original image URL opened full-viewport, cropped natively | 1024 × 510 | **427** |

Same source photo. **37× the real pixels and 2.7× the measured sharpness** — purely from where it was
captured. Enlarging the small one does not recover anything; it only adds soft pixels, and `image_qc.py`
detects it.

## The browser is mandatory

**Every photograph is found AND captured through `simple_browser-browser_actions`.** Both halves, every time:

1. **Find** in the browser — `navigate_to` a Bing image-search URL, `get_screenshot`, `view` the grid.
2. **Capture** in the browser — `navigate_to` the original image URL, then `get_screenshot`.

Never build a photo inventory from `web_search` snippets, alt text, `host-search_images` /
`host-image_search` metadata, or a caption you read on a page. Those tell you a picture exists; they do not
show it to you. Publishing on that basis is precisely how the wrong face reaches a document — and the failure
is invisible until a reader who knows the person spots it.

The browser is also what makes the verification rule below enforceable: you cannot `view` an image you never
rendered. If the browser is unavailable, publish **no pictures at all** and say so — see the fallback at the
end of this file. A text-only inventory is a perfectly good outcome; an unverified picture is not.

## The ladder — always start at Tier A

### Tier A — the original image, full viewport (BEST)

1. Run an image search in the browser:
   `simple_browser-browser_actions` → `navigate_to`
   `https://www.bing.com/images/search?q=<urlencoded query>`
2. `get_screenshot`, then `view` it to pick the right tile. **Screenshot coordinates are scaled** — the
   viewport is wider than the 1024px screenshot. Scale click coordinates by `viewport_width / 1024`
   (the viewport width is in the page URL's `cw=` parameter, and in the DOM header).
3. `click` the tile at the scaled x,y. This opens the detail view, and **the browser URL now contains the
   provenance you need**:
   - `mediaurl=` — the **true original image URL** (percent-decode it)
   - `expw=` / `exph=` — the **true native dimensions**
   The detail view also prints the host domain, native size and age on screen.
4. `navigate_to` that decoded `mediaurl`. The image renders alone, filling the viewport. The tab title
   confirms native size, e.g. `photo.jpg (2048×1365)`.
5. `get_screenshot`, then crop the content box:
   ```bash
   python scripts/capture_crop.py shot.webp working/img/asset-01.png \
     --auto --source-url "<decoded mediaurl>" --native 2048x1365 --tier A
   ```
   `--auto` finds the non-letterbox content box, so nothing is guessed.

### Tier A+ — ask the image CDN for a bigger rendition (do this whenever you can)

Many corporate sites serve images through a **dynamic image server**, and the `mediaurl` reveals it. These
accept a width parameter, so you can request a rendition far larger than the one the page happened to embed.

| CDN | Tell-tale in the URL | Ask for more |
|---|---|---|
| Adobe Scene7 / Dynamic Media | `scene7.com/is/image/...`, `$PRESET$` | replace the preset with `?wid=2400` |
| Cloudinary | `res.cloudinary.com/.../upload/w_400/` | raise or drop the `w_` segment |
| Imgix | `?w=600&h=400` | raise `w`/`h` |
| WordPress | `photo-1024x683.jpg` | try the un-suffixed `photo.jpg` |

Worked example — the embedded rendition was 1320×480; the CDN returned 2400×1080 for the same asset:

```
https://s7g10.scene7.com/is/image/kerry/Listowel+WW-CA?$TERTIARYHERO-Large$   →  1320×480
https://s7g10.scene7.com/is/image/kerry/Listowel+WW-CA?wid=2400               →  2400×1080
```

Captured through the browser that yielded **1024×464 at sharpness 1154** — roughly seven times sharper than a
grid-tile crop of the same picture. Always cite the **page** as the source in the report; the CDN URL is a
capture detail, recorded in the sidecar.

### Tier B — the search detail view

If `mediaurl` cannot be reached (hotlink protection, 403, login wall), screenshot the **detail view** itself
and crop the large rendered preview with an explicit `--box`. Typically 480–700px — acceptable, not ideal.
Pass `--tier B`.

### Tier C — the hosting page

Navigate to the page that publishes the image, `scroll` it into view (`scroll` needs integer
`x, y, scroll_x, scroll_y`), screenshot, and crop with `--box`. Typically 150–450px. Pass `--tier C`.
Often below the floor — expect to re-capture at A or B.

### Tier D — a results-grid tile (AVOID)

Never acceptable for a delivered document. Use only to *identify* which assets exist, then re-capture the
ones you will show. Pass `--tier D` so the QC gate flags it.

## Quality gate — run before building any document

```bash
python scripts/image_qc.py working/img                                  # human-readable
python scripts/image_qc.py working/img --json                           # machine-readable
python scripts/image_qc.py working/img --expect 4                       # + coverage check
python scripts/image_qc.py working/img --expect-manifest expected.json  # + per-subject coverage
```

**Coverage is gated too.** The gate cannot know how many photographs you documented unless you tell it, so
pass `--expect N` (or, on a roster, `--expect-manifest` with `{"<subject-slug>": <count>}` checked per
subdirectory). A shortfall is a **FAIL**: `coverage 1/4 — 3 documented photographs have no captured asset`.
Without this the gate happily passes a single sharp image while the inventory promises five.

**The model, and it matters:**

- **Sharpness gates.** A blurry or upscaled image is unusable at *any* size — that is a FAIL, and resizing
  cannot fix it. Re-capture.
- **Resolution sizes.** It does **not** fail. It caps how wide the image may be placed. The gate computes
  `max_display_mm` (long side ÷ placement dpi). A small, sharp image **placed small looks excellent**; the
  same image stretched across a page looks terrible.

So the rule for the document builder is one line:

> **Place every image at or below its `place<=` width. Downscaling to fit is always fine. Enlarging beyond it
> is never fine.**

A 333×251 crop at sharpness 845 is a perfectly good 42mm inline thumbnail. Do not throw it away for being
small, and do not stretch it to 120mm to fill a column — shrink the frame instead.

The gate also reads the sidecar `<image>.json` and flags a recorded upscale (FAIL), a capture holding <10% of
the original's pixels, tier C/D captures, lossy formats (save evidence as **PNG**), and a missing
`source_url`. Adjust placement density with `--dpi` (default 200) and the thumbnail warning with
`--min-useful-mm`.

## Accuracy rules — more important than sharpness

- **Verify the face before you publish it — every single time.** `view` every image after cropping and before
  it goes near a document. Search results are keyed on the *page*, not the person: a result captioned with the
  subject's name routinely turns out to be a product shot, a co-presenter, or an award winner. In one run of
  this skill, two of four "portraits" retrieved under the subject's name were other subjects entirely — a stack
  of books and a different individual — and both were caught only by looking. Where the subject also shares a
  name with other people, a confident wrong photograph is far worse than no photograph.
- **Record what the caption claims**, including the job title attached to it, and flag every asset carrying
  an outdated title or none.
- **Note whether one canonical headshot recurs or many images circulate**, and identify any single photograph
  propagating across multiple outlets with different captions — that is a real consistency finding.
- **Capture the credit and licence** where the page states one (photographer, agency, CC terms,
  "repro-free for this story"). Most assets are all-rights-reserved by default; say so.
- If an image cannot be captured above the floor, **keep the inventory row and omit the picture**, stating why.

## If the browser is unavailable

**Publish no pictures.** Do not substitute a lower-fidelity route — no `host-search_images` metadata, no
alt-text reconstruction, no "representative" image. Build the inventory from evidence in retrieved page text
(captions, "Pictured:" lines, photographer credits, alt text), and say plainly, in the report, that the
inventory is evidence-based rather than visual and that no image was captured or verified. Never imply you saw
a picture you did not.
