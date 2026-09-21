#!/usr/bin/env python3
"""Validate an Exec Command Center brief against the schema AND the design rules.

Usage: python scripts/validate_brief.py path/to/brief.json [--outlook-event-count N]
Exit 0 = valid; 1 = errors (printed one per line). No network, no side effects.
"""
import json, re, sys, os

ALLOWED_STATUS = {"red", "amber", "green", "grey"}
ALLOWED_EVIDENCE = {"verified", "inferred", "estimate"}
ALLOWED_KIND = {"accepted", "customer", "optional", "block", "personal"}
ALLOWED_LEDGER = {"overdue", "open", "waiting", "closed"}
ALLOWED_SIGNAL = {"blocked", "quiet", "nominal"}
URL_RE = re.compile(r"^https?://", re.I)

def err(errors, msg): errors.append(msg)

def req(obj, keys, where, errors):
    for k in keys:
        if k not in obj: err(errors, f"{where}: missing '{k}'")

def words(text): return len(re.findall(r"\w+", text or ""))

def check_brief(b, where, kind, errors):
    req(b, ["readTime", "stake", "decisions", "preReads", "questions", "outOfTime", "sources", "generatedAt"], where, errors)
    if b.get("readTime") not in ("1 min", "30 sec"): err(errors, f"{where}: readTime must be '1 min' or '30 sec'")
    st = b.get("stake") or {}
    if st.get("evidence") not in ALLOWED_EVIDENCE: err(errors, f"{where}: stake.evidence invalid")
    qs = b.get("questions") or []
    if kind != "personal":
        if len(qs) != 5: err(errors, f"{where}: exactly five questions required (got {len(qs)})")
        ranks = sorted(q.get("rank") for q in qs)
        if ranks != [1, 2, 3, 4, 5]: err(errors, f"{where}: question ranks must be 1..5 with no ties")
    if len(b.get("preReads") or []) > 3: err(errors, f"{where}: at most three pre-reads")
    for i, p in enumerate(b.get("preReads") or []):
        if p.get("title") and not p.get("url"): err(errors, f"{where}: preRead {i+1} '{p.get('title')}' has no link — pre-reads must exist and be linked")
    oot = b.get("outOfTime") or {}
    if kind in ("customer", "accepted") and (not oot.get("criticalDecision") or not oot.get("fallback")):
        err(errors, f"{where}: outOfTime.criticalDecision and fallback required for a full brief")
    if kind in ("customer", "accepted"):
        body = " ".join([st.get("text", "")] + [d.get("text", "") for d in b.get("decisions", [])] +
                        [q.get("text", "") + " " + q.get("impact", "") for q in qs] +
                        [oot.get("criticalDecision", ""), oot.get("fallback", "")])
        if words(body) > 260: err(errors, f"{where}: full brief exceeds the one-minute read (~{words(body)} words > 260)")
    if kind == "personal" and st.get("text") != "Personal — no brief prepared":
        err(errors, f"{where}: personal event brief must be masked")

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    path = sys.argv[1]
    outlook_count = None
    if "--outlook-event-count" in sys.argv:
        outlook_count = int(sys.argv[sys.argv.index("--outlook-event-count") + 1])
    with open(path, encoding="utf-8") as f:
        try: b = json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR: not valid JSON: {e}"); sys.exit(1)
    errors = []
    if b.get("schemaVersion") != 2: err(errors, "schemaVersion must be 2")
    req(b, ["meta", "kpis", "decisions", "calendar", "risks", "risksNote", "inbox", "ledger", "hygiene", "people"], "root", errors)
    meta = b.get("meta") or {}
    req(meta, ["date", "dayLabel", "generatedAt", "owner", "governingAnswer", "evidenceNote", "updateMechanism"], "meta", errors)
    if meta.get("governingAnswer") and words(meta["governingAnswer"]) < 8: err(errors, "meta.governingAnswer too short to be a claim")
    if "Calendar:" not in meta.get("evidenceNote", "") and outlook_count is not None:
        err(errors, "meta.evidenceNote must state the calendar reconciliation count ('Calendar: N of N Outlook events included')")
    kpis = b.get("kpis") or []
    if len(kpis) != 4: err(errors, f"exactly four KPI tiles required (got {len(kpis)})")
    for k in kpis:
        req(k, ["id", "label", "value", "unit", "status", "threshold", "fires", "decision", "trend", "evidence"], f"kpi {k.get('id')}", errors)
        if k.get("status") not in ALLOWED_STATUS: err(errors, f"kpi {k.get('id')}: bad status")
        if k.get("evidence") not in ALLOWED_EVIDENCE: err(errors, f"kpi {k.get('id')}: bad evidence")
        if not re.search(r"RED|AMBER|GREEN", k.get("threshold", ""), re.I): err(errors, f"kpi {k.get('id')}: threshold must publish the RED/AMBER/GREEN bands")
    for d in b.get("decisions") or []:
        req(d, ["id", "status", "evidence", "title", "situation", "complication", "whyNow", "ifNothingChanges", "verb", "recommendation", "ask", "links"], f"decision {d.get('id')}", errors)
        if d.get("status") not in ALLOWED_STATUS: err(errors, f"decision {d.get('id')}: bad status")
        if d.get("evidence") not in ALLOWED_EVIDENCE: err(errors, f"decision {d.get('id')}: bad evidence")
        if not d.get("whyNow"): err(errors, f"decision {d.get('id')}: whyNow is mandatory")
        for l in d.get("links") or []:
            if l.get("url") and not URL_RE.match(l["url"]): err(errors, f"decision {d.get('id')}: link '{l.get('label')}' is not a URL")
    cal = b.get("calendar") or {}
    events = cal.get("events") or []
    if outlook_count is not None and len(events) != outlook_count:
        err(errors, f"calendar: {len(events)} events in brief vs {outlook_count} returned by Outlook — reconcile before writing")
    for e in events:
        w = f"event {e.get('id')} '{e.get('title')}'"
        req(e, ["id", "title", "start", "end", "kind", "note", "brief"], w, errors)
        if e.get("kind") not in ALLOWED_KIND: err(errors, f"{w}: bad kind")
        if e.get("kind") == "personal" and (e.get("title") != "Personal" or e.get("note")): err(errors, f"{w}: personal events must be masked (title 'Personal', empty note)")
        if isinstance(e.get("brief"), dict): check_brief(e["brief"], w + " brief", e.get("kind"), errors)
        else: err(errors, f"{w}: brief missing — every event carries a brief")
        try:
            sh = int(e.get("start", "0:0").split(":")[0]); eh = int(e.get("end", "0:0").split(":")[0])
            if sh < int(cal.get("dayStart", 0)) or eh > int(cal.get("dayEnd", 24)) + 1: err(errors, f"{w}: falls outside dayStart/dayEnd window")
        except ValueError: err(errors, f"{w}: start/end must be HH:MM")
    for r in b.get("risks") or []:
        req(r, ["id", "status", "evidence", "account", "item", "owner", "age", "projectionDate", "projection", "verb", "action"], f"risk {r.get('id')}", errors)
        if r.get("status") in ("red", "amber") and not r.get("projection"): err(errors, f"risk {r.get('id')}: projection ('if nothing changes by') is mandatory for RED/AMBER")
    if "no new signals" not in (b.get("risksNote") or "").lower() and not b.get("risks"):
        err(errors, "risksNote must say 'no new signals' when there are no risk rows")
    inbox = b.get("inbox") or {}
    for m in inbox.get("reply") or []:
        req(m, ["id", "channel", "from", "subject", "quote", "action", "url"], f"reply {m.get('id')}", errors)
        if m.get("channel") not in ("email", "teams", "form"): err(errors, f"reply {m.get('id')}: bad channel")
        if m.get("channel") == "email" and not m.get("draftUrl"): err(errors, f"reply {m.get('id')}: email needing a reply must carry a draftUrl (create the draft, never send)")
        if m.get("url") and not URL_RE.match(m["url"]): err(errors, f"reply {m.get('id')}: url is not a URL")
    for m in inbox.get("fyi") or []:
        req(m, ["id", "channel", "from", "text", "url"], f"fyi {m.get('id')}", errors)
        if m.get("url") and not URL_RE.match(m["url"]): err(errors, f"fyi {m.get('id')}: url is not a URL")
    for l in b.get("ledger") or []:
        req(l, ["id", "status", "commitment", "owner", "due", "age", "evidence", "evidenceNote"], f"ledger {l.get('id')}", errors)
        if l.get("status") not in ALLOWED_LEDGER: err(errors, f"ledger {l.get('id')}: bad status")
        if l.get("status") == "closed" and not l.get("evidenceNote"): err(errors, f"ledger {l.get('id')}: closed items need closing evidence")
    for h in b.get("hygiene") or []:
        req(h, ["id", "day", "dayFlag", "event", "proposal", "why"], f"hygiene {h.get('id')}", errors)
    team = b.get("team")
    if team:
        if team.get("mode") not in ("directReports", "frequentContacts"): err(errors, "team.mode invalid")
        for m in team.get("members") or []:
            if m.get("signal") not in ALLOWED_SIGNAL: err(errors, f"team member {m.get('name')}: bad signal")
            for bad in ("underperform", "poor performer", "low performer", "rating"):
                if bad in json.dumps(m).lower(): err(errors, f"team member {m.get('name')}: performance judgement language is not allowed")
    # colour-only guard: statuses are enums; the app renders glyph + word. Nothing else to check statically.
    if errors:
        print(f"INVALID — {len(errors)} issue(s):")
        for e in errors: print(" -", e)
        sys.exit(1)
    print(f"VALID — {len(events)} events, {len(b.get('decisions') or [])} decisions, {len(b.get('risks') or [])} risks, {len(b.get('ledger') or [])} ledger rows")
    sys.exit(0)

if __name__ == "__main__":
    main()
