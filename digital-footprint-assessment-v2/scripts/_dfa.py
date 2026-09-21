#!/usr/bin/env python3
"""Shared helpers for the digital-footprint-assessment v2 pipeline.

Everything in v2 reads and writes the same two files per subject —
`report.json` (content) and `assets.json` (the photo manifest). This module
owns those file operations, the asset state machine, and the REASON templates,
so no script ever re-types a state name or an explanation line.
"""
import hashlib, json, os, re

# Bump when a renderer's OUTPUT SHAPE changes, so a stale build is detectable.
BUILD_VERSION = "dfa2-1"

# ---------------------------------------------------------------- state machine
NON_TERMINAL = {"candidate", "queued", "capturing", "captured", "verified"}
TERMINAL = {"shown", "duplicate", "not_photo", "budget_capped", "unverifiable",
            "wrong_person", "exhausted", "budget_exhausted", "browser_unavailable",
            "unresolved_address"}

# Terminal states that mean THE RUN failed, not that the web refused. These are
# retryable, and a report full of them is a report to re-run — which is why the
# coverage gate treats them differently from a genuine refusal.
RUN_FAILURE = {"browser_unavailable", "unresolved_address", "budget_exhausted"}
SHOWN_STATES = {"verified", "shown"}          # verified assets are always shown
LADDER = ["A+", "A", "B", "C", "D"]

# Reason lines are GENERATED, never typed by an agent. The document prints these
# verbatim, so they are written for a reader, not for an engineer.
REASONS = {
    "duplicate": "the same photograph as {ref}, republished by another outlet",
    "not_photo": "not a photograph of the subject",
    "budget_capped": "attempt budget of {budget} reached; listed as text",
    "budget_exhausted": "the time and attempt budget for this subject was reached before this asset was tried",
    "unverifiable": "the face is not identifiable at any size that could be reached",
    "wrong_person": "captured, inspected, WRONG PERSON — discarded",
    "exhausted": "every route to the file refused: {rungs}",
    "browser_unavailable": "the browser became unavailable during this run, so this photograph was "
                           "never tested against its host \u2014 it is not known to be unreachable",
    "unresolved_address": "no address for the image file could be resolved \u2014 only the page that "
                          "publishes it is known, so there was nothing to retrieve",
}
# Short labels for the single section-7 table. A truncated sentence ("only the…")
# reads as a bug; these are written for the cell they appear in, with the full
# sentence carried once in the note beneath the table.
SHORT_REASON = {
    "duplicate": "Duplicate \u2014 the same photograph as another row",
    "not_photo": "Not a photograph of the subject",
    "budget_capped": "Not attempted \u2014 capture budget reached",
    "budget_exhausted": "Not attempted \u2014 subject budget reached",
    "unverifiable": "Face not identifiable at any size reached",
    "wrong_person": "Inspected \u2014 WRONG PERSON, discarded",
    "exhausted": "Every route to the file refused",
    "browser_unavailable": "Not tested \u2014 the browser became unavailable",
    "unresolved_address": "No image address could be resolved",
}

RUNG_PROSE = {
    "A+": "the image server refused a larger rendition",
    "A": "the original refused ({outcome})",
    "B": "the search detail view failed to render it",
    "C": "the hosting page failed to render it",
    "D": "the results-grid tile could not be cropped",
}
OUTCOMES = ["ok", "http_403", "login_wall", "not_found", "tab_mismatch", "timeout", "not_photo",
            "browser_unavailable"]

# An attempt whose failure says nothing about the host. Logging one of these
# never advances the ladder and never contributes to an `exhausted` reason.
RUN_FAILURE_OUTCOMES = {"tab_mismatch", "browser_unavailable"}


def build_stamp(run_dir, slug):
    """A provenance marker the renderers embed and the gates require.

    The whole v2 design rests on one rule — agents produce data, scripts produce
    documents — and a rule that can be skipped will be skipped under load. The
    stamp makes the rule CHECKABLE: it is a digest of the two contract files as
    the renderer read them, so only a real pipeline run can produce it, and a
    hand-written document cannot pass the gate no matter how good it looks.
    """
    h = hashlib.sha256()
    for path in (report_path(run_dir, slug), manifest_path(run_dir, slug)):
        with open(path, "rb") as fh:
            h.update(fh.read())
    man = load_manifest(run_dir, slug)
    sm = man["summary"]
    return "%s %s %s shown=%d/%d" % (BUILD_VERSION, slug, h.hexdigest()[:16],
                                     sm["shown"], sm["found_distinct"])


STAMP_RE = re.compile(r"(dfa2-\d+) (\S+) ([0-9a-f]{16}) shown=(\d+)/(\d+)")


def parse_stamp(text):
    m = STAMP_RE.search(text or "")
    if not m:
        return None
    return {"version": m.group(1), "subject": m.group(2), "digest": m.group(3),
            "shown": int(m.group(4)), "found": int(m.group(5))}


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)


def read_json(path, default=None):
    if not os.path.exists(path):
        if default is None:
            raise SystemExit("missing file: %s" % path)
        return default
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


def subject_dir(run_dir, slug):
    return os.path.join(run_dir, slug)


def manifest_path(run_dir, slug):
    return os.path.join(run_dir, slug, "assets.json")


def report_path(run_dir, slug):
    return os.path.join(run_dir, slug, "report.json")


def log_path(run_dir, slug):
    return os.path.join(run_dir, slug, "capture_log.jsonl")


def load_manifest(run_dir, slug):
    """Load the manifest and RECOMPUTE its summary.

    The summary is derived, never authored. Recomputing on every load means a
    hand-edited or half-written manifest can never hand a gate a stale count of
    what is shown.
    """
    man = read_json(manifest_path(run_dir, slug))
    recount(man)
    return man


def save_manifest(run_dir, slug, man):
    recount(man)
    write_json(manifest_path(run_dir, slug), man)


def asset(man, asset_id):
    for a in man.get("assets", []):
        if a.get("id") == asset_id:
            return a
    raise SystemExit("no such asset in the manifest: %s" % asset_id)


def read_log(run_dir, slug):
    p = log_path(run_dir, slug)
    if not os.path.exists(p):
        return []
    rows = []
    with open(p, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def append_log(run_dir, slug, row):
    p = log_path(run_dir, slug)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def exhausted_reason(rows):
    """Build the 'every route refused' line from the ATTEMPT LOG, not from prose.

    Only attempts that actually reached a host count. A tab collision or a dead
    browser says nothing about the publisher, and must never be reported as one.
    """
    rows = [r for r in rows if r.get("outcome") not in RUN_FAILURE_OUTCOMES]
    parts = []
    for tier in LADDER:
        tried = [r for r in rows if r.get("tier") == tier]
        if tried:
            parts.append(RUNG_PROSE[tier].format(outcome=tried[-1].get("outcome", "refused")))
    return REASONS["exhausted"].format(rungs="; ".join(parts) or "no rung could be reached")


def recount(man):
    """Recompute assets.summary from the asset rows. Never hand-maintained."""
    assets = man.get("assets", [])
    photographic = [a for a in assets if a.get("state") != "not_photo"]
    distinct = {a.get("dedupe_group") or a["id"] for a in photographic}
    verified = [a for a in assets if a.get("state") in SHOWN_STATES]
    man["summary"] = {
        "found_distinct": len(distinct),
        "attempted": len([a for a in assets if a.get("attempts")]),
        "verified": len(verified),
        "shown": len(verified),
        "budget_applied": any(a.get("state") == "budget_capped" for a in assets),
    }
    return man["summary"]


def shown_assets(man):
    """The figures a renderer must embed — every verified asset, in rank order."""
    out = [a for a in man.get("assets", []) if a.get("state") in SHOWN_STATES]
    return sorted(out, key=lambda a: (a.get("rank") or 99, a["id"]))


def not_shown_assets(man):
    out = [a for a in man.get("assets", []) if a.get("state") not in SHOWN_STATES]
    return sorted(out, key=lambda a: (a.get("rank") or 99, a["id"]))


def non_terminal(man):
    return [a for a in man.get("assets", []) if a.get("state") in NON_TERMINAL
            and a.get("state") != "verified"]
