#!/usr/bin/env python3
"""make_fixture.py — build the renderer round-trip fixture.

A wholly FICTIONAL subject on example.com. Its only job is to exercise every
structure the renderers and gates care about: chips, marks, classifications,
verdict pills, quotes, four figures, a not-shown row with a generated reason,
A/V text rows, and a full source list. Both renderers must round-trip it green.

  python fixtures/make_fixture.py [--out fixtures]
"""
import argparse, json, os, sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Pillow is required", file=sys.stderr)
    sys.exit(2)

SLUG = "jane-murphy"
DATE = "2026-09-19"


def row(tag, finding, url, marks=None, date="", title_used=""):
    r = {"tag": tag, "finding": finding, "url": url, "accessed": DATE}
    if marks:
        r["marks"] = marks
    if date:
        r["date"] = date
    if title_used:
        r["title_used"] = title_used
    return r


def build_report():
    career = [
        row("FACT", "Named Chief Operations Officer of Example Group in March 2021, a promotion from "
            "Director of Supply Chain, a role she had held since 2017 according to the company's own "
            "leadership page and two subsequent annual reports.",
            "https://www.example.com/leadership/jane-murphy", date="Mar 2021"),
        row("FACT", "Holds a degree in industrial engineering and a management qualification, both listed "
            "consistently on the employer page and on two independent conference biographies reviewed "
            "for this assessment.", "https://www.example.com/about/board"),
        row("FLAG", "An aggregator profile still presents the 2017 supply-chain title as current, and it "
            "ranks on the first screen for the bare-name query, so an ordinary searcher meets a role she "
            "left five years ago before meeting the one she holds.",
            "https://directory.example.org/people/jane-murphy", marks=["SINGLE-SOURCE"]),
        row("FACT", "Appointed a non-executive director of an industry standards body in 2023; the "
            "appointment is recorded on the body's own register and repeated in trade coverage.",
            "https://standards.example.org/register/2023", date="2023"),
        row("FLAG", "No independent record of the 2019 operational programme credited to her on the "
            "employer page could be located in trade press or regulatory filings during this run.",
            "https://www.example.com/news/2019-programme", marks=["NOT VERIFIED"]),
    ]
    public = [
        row("FACT", "Panel member, Example Supply Chain Forum, on the resilience of multi-site "
            "manufacturing networks; the session page carries a recorded video and a full speaker list.",
            "https://forum.example.org/2025/panel-resilience", date="May 2025",
            title_used="Chief Operations Officer, Example Group"),
        row("FACT", "Interviewed for a trade podcast on automation in food manufacturing, a 34-minute "
            "episode with a written summary and a transcript published alongside it.",
            "https://podcast.example.net/episodes/142", date="Nov 2025",
            title_used="COO, Example Group"),
        row("FLAG", "A university alumni page announces her as a 2024 guest lecturer under the superseded "
            "supply-chain title, which is the same defect the aggregator carries and suggests the source "
            "of both is an old press biography.",
            "https://alumni.example.edu/events/2024-guest-lecture", date="2024",
            title_used="Director of Supply Chain"),
        row("FACT", "Keynote at a regional manufacturing awards evening, reported by one local outlet "
            "with a photograph and a two-paragraph write-up.",
            "https://localnews.example.co/awards-2025", date="Oct 2025"),
    ]
    network = [
        row("FACT", "Non-executive director, Example Standards Body, listed on the public register with "
            "an appointment date and a current status.", "https://standards.example.org/register/murphy"),
        row("FACT", "Member of a regional manufacturing association, named on its member directory page "
            "alongside her employer.", "https://association.example.org/members"),
        row("FLAG", "A second register entry lists an Example Group board seat that the group's own "
            "corporate page does not mention, which may be a renamed entity rather than a discrepancy.",
            "https://registry.example.gov/entities/48921", marks=["SINGLE-SOURCE"]),
    ]
    titles = [
        row("FACT", "\u201cChief Operations Officer, Example Group\u201d \u2014 the employer leadership page "
            "and the 2025 forum speaker listing agree on this form, and it is the correct current title.",
            "https://www.example.com/leadership/jane-murphy"),
        row("FLAG", "\u201cCOO\u201d \u2014 the abbreviated form used by the podcast and by two syndicated "
            "republications of its summary.", "https://podcast.example.net/episodes/142"),
        row("FLAG", "\u201cDirector of Supply Chain\u201d \u2014 superseded, still live on the alumni page and "
            "the aggregator profile, both of which rank in the first screen.",
            "https://directory.example.org/people/jane-murphy"),
        row("FLAG", "The business unit named in her employer biography was restructured in 2024 and no "
            "longer exists under that name, so the biography describes an organisation a reader cannot find.",
            "https://www.example.com/news/2024-restructure", marks=["NOT VERIFIED"]),
    ]
    coverage = [
        row("FACT", "Trade quarterly profile of the group's operations programme, quoting her twice and "
            "carrying an independently commissioned photograph.",
            "https://trade.example.net/features/operations-2025", date="Jun 2025"),
        row("FACT", "Regional outlet reports the awards keynote with a stage photograph credited to a "
            "named staff photographer.", "https://localnews.example.co/awards-2025", date="Oct 2025"),
        row("FACT", "A wire summary of the 2021 appointment, republished verbatim by four aggregators, "
            "which is why the appointment is the single most repeated fact about her online.",
            "https://wire.example.net/2021/appointments", date="Mar 2021"),
    ]
    dsby = [
        row("FACT", "Occasional posts under her own name on a professional network, all work-related and "
            "all tied to employer announcements; the platform requires a login, so volume and reach could "
            "not be assessed.", "https://www.example.com/leadership/jane-murphy",
            marks=["NOT VERIFIED"]),
        row("FACT", "Two bylined comment pieces on the employer's own newsroom, both about operational "
            "resilience rather than about her.", "https://www.example.com/news/resilience-comment"),
    ]
    dsabout = [
        row("FACT", "The wire appointment summary and its four republications account for most of what "
            "third parties publish about her.", "https://wire.example.net/2021/appointments"),
        row("FLAG", "A data-broker page assembles an unverified profile from scraped sources; its contents "
            "were not reproduced here.", "https://broker.example.info/p/jane-murphy",
            marks=["SINGLE-SOURCE"]),
    ]
    dsnot = [
        row("FLAG", "The professional network profile is login-walled, and it is almost certainly her "
            "largest owned channel; nothing behind that wall was assessed.",
            "https://www.example.com/leadership/jane-murphy", marks=["NOT VERIFIED"]),
    ]
    fi = []
    for i, (t, c, u) in enumerate([
        ("Jane Murphy \u2014 Example Group leadership", "company-owned", "https://www.example.com/leadership/jane-murphy"),
        ("Jane Murphy, Director of Supply Chain \u2014 directory profile", "aggregator", "https://directory.example.org/people/jane-murphy"),
        ("Operations chief on resilience \u2014 trade quarterly", "editorial", "https://trade.example.net/features/operations-2025"),
        ("Jane Murphy \u2014 public records and contact details", "data-broker", "https://broker.example.info/p/jane-murphy"),
        ("Jane Murphy, ceramic artist \u2014 studio site", "wrong-person", "https://studio.example.art/about"),
    ], start=1):
        fi.append({"query": "Jane Murphy", "rank": i, "title": t, "url": u, "class": c})
    for i, (t, c, u) in enumerate([
        ("Jane Murphy \u2014 Example Group leadership", "company-owned", "https://www.example.com/leadership/jane-murphy"),
        ("Example Group names new COO \u2014 wire summary", "editorial", "https://wire.example.net/2021/appointments"),
        ("Example Group executive team \u2014 company profile", "company-owned", "https://www.example.com/about/board"),
        ("Jane Murphy \u2014 auto-generated biography", "auto-generated", "https://bios.example.info/jane-murphy"),
        ("Example Group \u2014 sponsored listing", "sponsored", "https://ads.example.net/example-group"),
    ], start=1):
        fi.append({"query": "Jane Murphy Example Group", "rank": i, "title": t, "url": u, "class": c})

    sources = [{"url": r["url"], "title": r["finding"][:70] + "\u2026", "accessed": DATE}
               for r in career + public + network + titles + coverage + dsby + dsabout + dsnot]
    sources += [{"url": r["url"], "title": r["title"], "accessed": DATE} for r in fi]
    sources += [{"url": u, "title": t, "accessed": DATE} for u, t in [
        ("https://forum.example.org/2025/speakers", "Example Supply Chain Forum \u2014 full speaker list"),
        ("https://www.example.com/annual-report-2025", "Example Group annual report 2025"),
        ("https://www.example.com/annual-report-2024", "Example Group annual report 2024"),
        ("https://standards.example.org/about", "Example Standards Body \u2014 about"),
        ("https://trade.example.net/archive", "Trade quarterly archive search"),
        ("https://localnews.example.co/archive", "Regional outlet archive search"),
        ("https://video.example.net/channel/forum", "Forum video channel"),
    ]]
    seen, uniq = set(), []
    for s in sources:
        if s["url"] not in seen:
            seen.add(s["url"])
            uniq.append(s)

    return {
        "subject": {"slug": SLUG, "name": "Jane Murphy", "org": "Example Group",
                    "role_verified": "Chief Operations Officer", "sample_date": DATE},
        "layer1": {
            "headline": "Jane Murphy's public record is accurate where her employer controls it and five "
                        "years out of date everywhere else, so the first screen introduces a role she left "
                        "in 2021 before it introduces the one she holds.",
            "key_figures": [
                {"label": "Title variants live", "value": "3", "note": "one superseded, one abbreviated"},
                {"label": "Sources reviewed", "value": "31", "note": "retrieved during this run"},
                {"label": "Adverse items", "value": "0", "note": "in the sources searched"},
                {"label": "Wrong-person results", "value": "1", "note": "in the first five"},
            ],
            "searcher_finds": [
                "The employer leadership page ranks first for both queries and is accurate and current.",
                "The second result is an aggregator profile carrying a title she left in 2021, and the "
                "fifth is a different Jane Murphy entirely.",
                "Independent, editorial material exists but sits below the aggregated and sponsored "
                "results a casual searcher stops at.",
            ],
            "scorecard": [
                {"dimension": "Credibility", "verdict": "Adequate",
                 "evidence": "Facts corroborate across the employer page, two annual reports and the "
                             "standards register, with one unverified programme claim."},
                {"dimension": "Adverse material", "verdict": "Clean",
                 "evidence": "Nothing critical or disputed in the sources searched, which did not include "
                             "paywalled archives, court filings or broadcast."},
                {"dimension": "Distinctiveness", "verdict": "Moderate",
                 "evidence": "A consistent operational-resilience theme runs through her appearances, but "
                             "most published material restates her job description."},
                {"dimension": "Discoverability", "verdict": "Diluted",
                 "evidence": "A namesake and an outdated aggregator profile both occupy the first screen "
                             "for the bare-name query."},
                {"dimension": "Consistency", "verdict": "Mixed",
                 "evidence": "Three live title forms and one restructured business unit named in the "
                             "employer biography."},
                {"dimension": "Momentum", "verdict": "Steady",
                 "evidence": "Four dated public items across 2024 and 2025, roughly one every six months."},
            ],
            "fixes": [
                {"title": "Correct the aggregator entry", "effort": "Low",
                 "what": "Submit the current title and employer through the directory's correction form, "
                         "then re-sample the first screen four weeks later.",
                 "why": "It is the second result for her name and it is wrong, which costs more than any "
                        "amount of new content would add."},
                {"title": "Refresh the employer biography", "effort": "Low",
                 "what": "Remove the restructured unit name, state the standards-body appointment, and "
                         "date the page so republication carries a timestamp.",
                 "why": "The employer page is what every aggregator copies, so one correction propagates."},
                {"title": "Publish one owned piece a quarter", "effort": "Medium",
                 "what": "Short bylined comment on operational resilience, published on the newsroom and "
                         "syndicated once.",
                 "why": "It is the only lever that moves Distinctiveness without relying on other people's "
                        "coverage."},
            ],
        },
        "first_impression": fi,
        "sections": {
            "career": career, "public_profile": public,
            "topics": {
                "quotes": [
                    {"text": "Resilience is not a project you finish; it is a cost you choose to keep "
                             "paying after the crisis is over.",
                     "said_where": "Example Supply Chain Forum panel", "date": "May 2025",
                     "url": "https://forum.example.org/2025/panel-resilience"},
                    {"text": "Automation moved our constraint from the line to the people who plan it.",
                     "said_where": "Trade podcast, episode 142", "date": "Nov 2025",
                     "url": "https://podcast.example.net/episodes/142"},
                ],
                "themes": [
                    {"theme": "Operational resilience after disruption", "weight": 5, "evidence_count": 6},
                    {"theme": "Automation and the planning constraint", "weight": 3, "evidence_count": 3},
                    {"theme": "Multi-site manufacturing networks", "weight": 2, "evidence_count": 2},
                ],
            },
            "media": {"coverage": coverage, "adverse": [],
                      "not_covered": ["paywalled trade archives", "court and regulatory filings",
                                      "broadcast and radio", "non-English media",
                                      "login-walled platforms"]},
            "digital_social": {"by": dsby, "about": dsabout, "not_assessable": dsnot},
            "inventory_lead":
                "The visual record is narrow and almost entirely employer-controlled. One corporate "
                "headshot, served from a single image library, accounts for the photograph a searcher "
                "meets on the employer page, on the wire summary and on all four of its republications: "
                "many result URLs, one photograph. Two assets sit outside that control \u2014 a stage "
                "photograph from the 2025 awards evening credited to a named staff photographer, and a "
                "panel photograph from the forum \u2014 and both are more recent than the headshot and show "
                "her working rather than posed. Captions attach three different job titles across those "
                "assets, which is the same inconsistency the title-variants section records. One further "
                "candidate was captured, inspected and discarded: it shows a different person with the "
                "same name. For a Corporate Affairs team the practical consequence is narrow rather than "
                "serious: the imagery is accurate but monotonous, and a single refreshed sitting would "
                "replace the one picture that carries the whole record.",
            "av_items": [
                {"kind": "VIDEO", "title": "Panel: resilience in multi-site manufacturing",
                 "host": "forum.example.org", "date": "May 2025", "duration": "48 min",
                 "title_used": "Chief Operations Officer, Example Group",
                 "on_screen": "the subject appears from 06:10, seated, third from left",
                 "finding": "three frames sampled across the runtime show the panel wide; the thumbnail "
                            "is the event's branded title card, not the subject.",
                 "url": "https://video.example.net/channel/forum"},
                {"kind": "AUDIO", "title": "Trade podcast, episode 142",
                 "host": "podcast.example.net", "date": "Nov 2025", "duration": "34 min",
                 "title_used": "COO, Example Group",
                 "on_screen": "none \u2014 audio over a static show card",
                 "finding": "audio only, so no moving-image or still asset of the subject exists here.",
                 "url": "https://podcast.example.net/episodes/142"},
            ],
            "network": network, "title_variants": titles,
        },
        "assessment": {
            "best_known_for": "Being the operations lead who talks about resilience as a running cost "
                              "rather than a recovery project \u2014 a line that is quoted twice and echoed "
                              "in the trade profile.",
            "unfamiliar_concludes": "A searcher who stops at the first screen concludes she is a "
                                    "supply-chain director at a company they cannot quite place, because "
                                    "the two results above the editorial coverage are an outdated "
                                    "aggregator entry and a namesake.",
            "strong": [
                "The employer-controlled record is accurate, current and consistently titled.",
                "Two independent, dated appearances in 2025 with verbatim quotes attached.",
                "A public register entry corroborates the non-executive appointment.",
            ],
            "gaps": [
                "Three live title forms, one of them five years superseded and ranking on page one.",
                "A restructured business unit still named in the employer biography.",
                "One photograph carries almost the entire visual record.",
                "The largest owned channel is login-walled and could not be assessed.",
            ],
            "fixes_ranked": [
                "Correct the aggregator entry \u2014 lowest effort, largest first-screen effect.",
                "Refresh and date the employer biography so republication carries a timestamp.",
                "Commission one refreshed photographic sitting outside the corporate library.",
                "Publish one owned comment piece a quarter to build a theme of her own.",
            ],
        },
        "limitations": [
            "Only public web sources retrieved during this run on %s were used." % DATE,
            "Paywalled archives, court and regulatory filings, broadcast and non-English media were not "
            "searched, so the adverse-material finding is bounded by that.",
            "Login-walled platforms could not be assessed at all.",
            "Search visibility is a point-in-time sample and will differ by searcher and location.",
        ],
        "sources": uniq,
        "confidence": {
            "level": "Medium",
            "statement": "The employer-controlled facts are corroborated across three independent sources "
                         "and the register entry is public, so the core record is reliable. Confidence is "
                         "held at Medium because the largest owned channel is login-walled, one programme "
                         "claim could not be verified anywhere, and paywalled and broadcast archives were "
                         "not searched.",
        },
    }


def build_assets(outdir):
    imgdir = os.path.join(outdir, SLUG, "img")
    os.makedirs(imgdir, exist_ok=True)
    specs = [
        ("asset-01", "corporate headshot", "Corporate headshot, Example Group leadership page",
         "Jane Murphy, Chief Operations Officer", "Chief Operations Officer", False,
         "https://www.example.com/leadership/jane-murphy",
         "https://cdn.example.com/is/image/example/jane-murphy?$PRESET$", 2000, 1452, "example.com"),
        ("asset-02", "stage", "On stage at the 2025 regional manufacturing awards",
         "Jane Murphy accepts the operations award", "COO, Example Group", False,
         "https://localnews.example.co/awards-2025",
         "https://media.localnews.example.co/2025/awards-murphy.jpg", 1600, 1067, "localnews.example.co"),
        ("asset-03", "event", "Panel session, Example Supply Chain Forum",
         "Pictured: Jane Murphy, Director of Supply Chain", "Director of Supply Chain", True,
         "https://forum.example.org/2025/panel-resilience",
         "https://forum.example.org/media/panel-2025.jpg", 1200, 800, "forum.example.org"),
        ("asset-04", "press", "Trade quarterly commissioned portrait",
         "Jane Murphy photographed at the Example Group site", "Chief Operations Officer", False,
         "https://trade.example.net/features/operations-2025",
         "https://trade.example.net/img/murphy-portrait.jpg", 1400, 1867, "trade.example.net"),
    ]
    assets = []
    for i, (aid, ctx, title, cap, tattached, outdated, page, img, nw, nh, host) in enumerate(specs, 1):
        w, h = 600, int(600 * nh / nw)
        im = Image.new("RGB", (w, h), (232, 236, 240))
        d = ImageDraw.Draw(im)
        for y in range(0, h, 12):
            d.line([(0, y), (w, y)], fill=(210 - i * 8, 218, 228), width=4)
        d.rectangle([40, 40, w - 40, h - 40], outline=(90, 100, 115), width=3)
        d.text((56, 56), "FIXTURE IMAGE\n%s\nnot a real person" % aid, fill=(40, 48, 60))
        im.save(os.path.join(imgdir, "%s.png" % aid))
        with open(os.path.join(imgdir, "%s.json" % aid), "w", encoding="utf-8") as fh:
            json.dump({"source_url": img, "native_w": nw, "native_h": nh,
                       "capture_tier": "A", "upscaled": False}, fh, indent=1)
        assets.append({
            "id": aid, "candidate_source": "search_images", "page_url": page, "image_url": img,
            "image_url_best": img.replace("$PRESET$", "wid=2400"), "native_w": nw, "native_h": nh,
            "host": host, "caption_verbatim": cap, "title_attached": tattached,
            "title_outdated": outdated, "credit": "", "licence": "", "context": ctx,
            "descriptive_title": title, "dedupe_group": "g%d" % i, "rank": i, "state": "shown",
            "file": "img/%s.png" % aid, "sidecar": "img/%s.json" % aid, "placement_mm": 80,
            "verification": {"by": "view", "matched_against":
                             "asset-01 corporate headshot; the published caption names the subject",
                             "result": "match"},
            "attempts": 1,
        })
    assets.append({
        "id": "asset-05", "candidate_source": "search_images",
        "page_url": "https://studio.example.art/about",
        "image_url": "https://studio.example.art/img/portrait.jpg", "native_w": 900, "native_h": 900,
        "host": "studio.example.art", "caption_verbatim": "Jane Murphy in the studio",
        "title_attached": "Ceramic artist", "context": "other",
        "descriptive_title": "Namesake portrait, studio site", "dedupe_group": "g5", "rank": 5,
        "state": "wrong_person",
        "reason": "captured, inspected, WRONG PERSON \u2014 discarded",
        "verification": {"by": "view", "matched_against": "asset-01; a different person", "result": "no-match"},
        "attempts": 2,
    })
    return {"subject": SLUG, "capture_budget": 8, "assets": assets}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.dirname(os.path.abspath(__file__)))
    args = ap.parse_args()
    out = args.out
    os.makedirs(os.path.join(out, SLUG), exist_ok=True)
    with open(os.path.join(out, "subjects.json"), "w", encoding="utf-8") as fh:
        json.dump([{"slug": SLUG, "name": "Jane Murphy", "org": "Example Group",
                    "role_claimed": "Chief Operations Officer", "aliases": []}], fh, indent=1)
    with open(os.path.join(out, "run.json"), "w", encoding="utf-8") as fh:
        json.dump({"depth": "standard", "capture_budget": 8, "brand": "default",
                   "sample_date": DATE, "max_attempts_per_subject": 24,
                   "max_minutes_per_subject": 12}, fh, indent=1)
    with open(os.path.join(out, SLUG, "report.json"), "w", encoding="utf-8") as fh:
        json.dump(build_report(), fh, indent=1, ensure_ascii=False)
    man = build_assets(out)
    with open(os.path.join(out, SLUG, "assets.json"), "w", encoding="utf-8") as fh:
        json.dump(man, fh, indent=1, ensure_ascii=False)
    print("fixture written to %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
