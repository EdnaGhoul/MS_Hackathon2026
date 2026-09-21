#!/usr/bin/env python3
"""selftest.py — prove the gates actually bite (test plan T1-T6, offline).

A gate nobody tests is a gate that passes everything, which is exactly how v1
shipped a vacuous section-7 check. This copies the fixture into a temp run,
breaks one thing at a time, and asserts the right script goes red.

  python scripts/selftest.py [--keep]
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIX = os.path.join(ROOT, "fixtures")
ENV = dict(os.environ, NODE_PATH=os.environ.get("NODE_PATH", "/usr/lib/node_modules"))
SLUG = "jane-murphy"
RESULTS = []


def run(cmd, cwd=ROOT):
    p = subprocess.run(cmd, cwd=cwd, env=ENV, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def case(name, expect_fail, cmd, cwd=ROOT):
    rc, out = run(cmd, cwd)
    ok = (rc != 0) if expect_fail else (rc == 0)
    RESULTS.append((name, ok, rc, out.strip().splitlines()[-1] if out.strip() else ""))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="dfa-selftest-")
    run_dir = os.path.join(tmp, "run")
    shutil.copytree(FIX, run_dir)
    for junk in ("build", "qa"):
        shutil.rmtree(os.path.join(run_dir, SLUG, junk), ignore_errors=True)
    man_p = os.path.join(run_dir, SLUG, "assets.json")

    # T1 — renderer round-trip: fixture renders and both gates are green.
    case("T1 html render", False, [sys.executable, "scripts/render_html.py", "--run", run_dir, "--all"])
    case("T1 docx render", False, ["node", "scripts/render_docx.js", "--run", run_dir, "--all"])
    case("T1 html gate", False, [sys.executable, "scripts/accept_report.py", "--run", run_dir])
    case("T1 docx gate", False, [sys.executable, "scripts/accept_docx.py", "--run", run_dir])

    # T2 — a dropped chip must be caught by structure_from_model, not by eye.
    html = os.path.join(run_dir, SLUG, "build", "%s-digital-footprint.html" % SLUG)
    body = open(html, encoding="utf-8").read()
    open(html, "w", encoding="utf-8").write(body.replace('<span class="tag fact">FACT</span>', "", 1))
    case("T2 dropped chip detected", True, [sys.executable, "scripts/accept_report.py", "--run", run_dir])
    open(html, "w", encoding="utf-8").write(body)

    # T3 — a verified asset whose file vanished must fail QC with its id.
    png = os.path.join(run_dir, SLUG, "img", "asset-02.png")
    os.rename(png, png + ".hidden")
    case("T3 missing capture detected", True, [sys.executable, "scripts/image_qc.py", "--run", run_dir])
    os.rename(png + ".hidden", png)

    # T4 — the ladder is logged, so --next walks A+ -> A -> B -> C -> D, then exhausts.
    man = json.load(open(man_p, encoding="utf-8"))
    man["assets"][0]["state"] = "queued"
    json.dump(man, open(man_p, "w", encoding="utf-8"), indent=1)
    rungs = []
    for _ in range(6):
        rc, out = run([sys.executable, "scripts/log_attempt.py", "--run", run_dir, "--subject", SLUG,
                       "--asset", "asset-01", "--next"])
        rung = out.strip().splitlines()[-1]
        if rc == 3:
            rungs.append("exhausted")
            break
        rungs.append(rung)
        run([sys.executable, "scripts/log_attempt.py", "--run", run_dir, "--subject", SLUG,
             "--asset", "asset-01", "--tier", rung, "--url", "https://example.com/x",
             "--outcome", "http_403"])
    RESULTS.append(("T4 ladder order", rungs[:6] == ["A+", "A", "B", "C", "D", "exhausted"], 0,
                    " -> ".join(rungs)))

    # T5 — a tab_mismatch never becomes a capture; contention stays visible.
    run([sys.executable, "scripts/log_attempt.py", "--run", run_dir, "--subject", SLUG,
         "--asset", "asset-03", "--tier", "A", "--url", "https://example.com/a",
         "--returned", "https://example.com/somebody-else", "--outcome", "tab_mismatch"])
    st = next(a["state"] for a in json.load(open(man_p, encoding="utf-8"))["assets"]
              if a["id"] == "asset-03")
    RESULTS.append(("T5 contention detector", st == "capturing", 0, "state=%s" % st))

    # T6 — budget limits ATTEMPTS: 12 candidates, budget 8 -> 8 queued, rest budget_capped.
    man = json.load(open(man_p, encoding="utf-8"))
    man["assets"] = []
    for i in range(1, 13):
        man["assets"].append({"id": "asset-%02d" % i, "candidate_source": "search_images",
                              "page_url": "https://example.com/p%d" % i,
                              "image_url": "https://cdn.example.com/i%d.jpg" % i,
                              "native_w": 1200, "native_h": 800, "host": "example.com",
                              "context": "event", "state": "candidate"})
    json.dump(man, open(man_p, "w", encoding="utf-8"), indent=1)
    run([sys.executable, "scripts/plan_capture.py", "--run", run_dir])
    man = json.load(open(man_p, encoding="utf-8"))
    queued = [a for a in man["assets"] if a["state"] == "queued"]
    capped = [a for a in man["assets"] if a["state"] == "budget_capped"]
    RESULTS.append(("T6 budget applied", len(queued) == 8 and len(capped) == 4
                    and all(a.get("reason") for a in capped), 0,
                    "%d queued, %d capped with reasons" % (len(queued), len(capped))))

    # A capture that was never verified must block the close — no silent drop.
    man = json.load(open(man_p, encoding="utf-8"))
    man["assets"][0]["state"] = "captured"
    json.dump(man, open(man_p, "w", encoding="utf-8"), indent=1)
    case("T7 finalize refuses unverified", True,
         [sys.executable, "scripts/plan_capture.py", "--run", run_dir, "--finalize", SLUG])

    # And a subject whose capture phase never ran must not close as 'budget exhausted'.
    fresh = os.path.join(tmp, "fresh")
    shutil.copytree(FIX, fresh)
    fm = os.path.join(fresh, SLUG, "assets.json")
    m2 = json.load(open(fm, encoding="utf-8"))
    for a in m2["assets"]:
        a["state"] = "candidate"
        a.pop("attempts", None)
    json.dump(m2, open(fm, "w", encoding="utf-8"), indent=1)
    run([sys.executable, "scripts/plan_capture.py", "--run", fresh])
    case("T8 finalize refuses empty capture log", True,
         [sys.executable, "scripts/plan_capture.py", "--run", fresh, "--finalize", SLUG])

    # T9 - the canonical employer headshot is never the asset a budget cuts.
    man = json.load(open(man_p, encoding="utf-8"))
    man["assets"] = [{"id": "asset-%02d" % i, "candidate_source": "search_images",
                      "page_url": "https://press%d.example.net/story" % i,
                      "image_url": "https://cdn.press%d.example.net/i.jpg" % i,
                      "native_w": 1600, "native_h": 1067, "host": "press%d.example.net" % i,
                      "context": "press", "state": "candidate"} for i in range(1, 10)]
    man["assets"].append({"id": "asset-99", "candidate_source": "page_caption",
                          "page_url": "https://www.example.com/leadership/jane-murphy",
                          "image_url": "https://cdn.example.com/is/image/example/jane-murphy",
                          "native_w": 2000, "native_h": 1452, "host": "example.com",
                          "context": "corporate headshot", "state": "candidate"})
    json.dump(man, open(man_p, "w", encoding="utf-8"), indent=1)
    run([sys.executable, "scripts/plan_capture.py", "--run", run_dir])
    head = next(a for a in json.load(open(man_p, encoding="utf-8"))["assets"] if a["id"] == "asset-99")
    RESULTS.append(("T9 canonical headshot queued", head["state"] == "queued" and head["rank"] == 1,
                    0, "rank=%s state=%s" % (head.get("rank"), head["state"])))

    # T10 - a dead browser is retryable, and is never reported as a host refusal.
    run([sys.executable, "scripts/log_attempt.py", "--run", run_dir, "--subject", SLUG,
         "--browser-down"])
    man = json.load(open(man_p, encoding="utf-8"))
    states = {a["state"] for a in man["assets"]}
    reasons = " ".join(a.get("reason", "") for a in man["assets"])
    RESULTS.append(("T10 browser-down is retryable",
                    states == {"browser_unavailable"} and "route to the file refused" not in reasons,
                    0, "states=%s" % ",".join(sorted(states))))

    # T11 - the coverage gate blocks a run whose photographs failed on OUR side.
    cov = os.path.join(tmp, "cov")
    shutil.copytree(FIX, cov)
    cm = os.path.join(cov, SLUG, "assets.json")
    m3 = json.load(open(cm, encoding="utf-8"))
    for a in m3["assets"][1:4]:
        a["state"] = "browser_unavailable"
        a["reason"] = "the browser became unavailable during this run, so this photograph was never tested"
        a.pop("file", None)
    json.dump(m3, open(cm, "w", encoding="utf-8"), indent=1)
    run([sys.executable, "scripts/render_html.py", "--run", cov, "--all"])
    case("T11 coverage gate blocks failed run", True,
         [sys.executable, "scripts/accept_report.py", "--run", cov])

    # And the same report with the SAME coverage passes when the web refused.
    m3 = json.load(open(cm, encoding="utf-8"))
    for a in m3["assets"][1:4]:
        a["state"] = "exhausted"
        a["reason"] = "every route to the file refused: the original refused (http_403)"
    json.dump(m3, open(cm, "w", encoding="utf-8"), indent=1)
    run([sys.executable, "scripts/render_html.py", "--run", cov, "--all"])
    case("T12 host refusal still publishes", False,
         [sys.executable, "scripts/accept_report.py", "--run", cov])

    # T13 - a picture on a video or audio row is a scope breach, single table or not.
    html2 = os.path.join(cov, SLUG, "build", "%s-digital-footprint.html" % SLUG)
    good = open(html2, encoding="utf-8").read()
    open(html2, "w", encoding="utf-8").write(good.replace(
        '<td class="nopic">No picture \u2014 video item',
        '<td class="nopic"><img src="data:image/png;base64,AAAA">No picture \u2014 video item', 1))
    case("T13 picture on an A/V row detected", True,
         [sys.executable, "scripts/accept_report.py", "--run", cov])
    open(html2, "w", encoding="utf-8").write(good)

    # T14 - a roster outlier is surfaced either way, but only BLOCKS when the
    # shortfall was ours. Nine finished reports are not held hostage to one
    # subject whose photographs their hosts genuinely refused.
    ros = os.path.join(tmp, "roster")
    os.makedirs(ros, exist_ok=True)
    subs = []
    for i, slug in enumerate(["subject-a", "subject-b", "subject-c"]):
        shutil.copytree(os.path.join(FIX, SLUG), os.path.join(ros, slug))
        subs.append({"slug": slug, "name": "Subject %d" % i, "org": "Example Group"})
        rp = os.path.join(ros, slug, "report.json")
        rep = json.load(open(rp, encoding="utf-8"))
        rep["subject"]["slug"] = slug
        json.dump(rep, open(rp, "w", encoding="utf-8"), indent=1)
    json.dump(subs, open(os.path.join(ros, "subjects.json"), "w", encoding="utf-8"), indent=1)
    shutil.copy(os.path.join(FIX, "run.json"), os.path.join(ros, "run.json"))

    def thin(slug, state, reason):
        mp = os.path.join(ros, slug, "assets.json")
        m = json.load(open(mp, encoding="utf-8"))
        for a in m["assets"][1:4]:
            a["state"] = state
            a["reason"] = reason
            f = a.pop("file", None)
            if f and os.path.exists(os.path.join(ros, slug, f)):
                os.remove(os.path.join(ros, slug, f))
        json.dump(m, open(mp, "w", encoding="utf-8"), indent=1)

    thin("subject-c", "exhausted", "every route to the file refused: the original refused (http_403)")
    run([sys.executable, "scripts/render_html.py", "--run", ros, "--all"])
    run(["node", "scripts/render_docx.js", "--run", ros, "--all"])
    case("T14 host-refused outlier still publishes", False,
         [sys.executable, "scripts/accept_roster.py", "--run", ros])

    thin("subject-c", "browser_unavailable", "the browser became unavailable during this run")
    run([sys.executable, "scripts/render_html.py", "--run", ros, "--all"])
    run(["node", "scripts/render_docx.js", "--run", ros, "--all"])
    case("T15 our-failure outlier blocks roster", True,
         [sys.executable, "scripts/accept_roster.py", "--run", ros])

    # T16-T18 - a hand-built or stale document cannot pass, however good it looks.
    # This is what makes "agents produce data, scripts produce documents"
    # enforceable rather than merely stated.
    prov = os.path.join(tmp, "prov")
    shutil.copytree(FIX, prov)
    run([sys.executable, "scripts/render_html.py", "--run", prov, "--all"])
    run(["node", "scripts/render_docx.js", "--run", prov, "--all"])
    case("T16 pipeline build passes provenance", False,
         [sys.executable, "scripts/accept_report.py", "--run", prov])
    hp = os.path.join(prov, SLUG, "build", "%s-digital-footprint.html" % SLUG)
    built = open(hp, encoding="utf-8").read()
    open(hp, "w", encoding="utf-8").write(re.sub(r"<!-- dfa-build [^>]*-->", "", built))
    case("T17 hand-built HTML rejected", True,
         [sys.executable, "scripts/accept_report.py", "--run", prov])
    open(hp, "w", encoding="utf-8").write(built)

    rp2 = os.path.join(prov, SLUG, "report.json")
    rep2 = json.load(open(rp2, encoding="utf-8"))
    rep2["layer1"]["headline"] += " Edited after the render."
    json.dump(rep2, open(rp2, "w", encoding="utf-8"), indent=1)
    case("T18 stale build rejected", True,
         [sys.executable, "scripts/accept_report.py", "--run", prov])

    # T19-T20 - preflight is green on a healthy subject and red on a broken model,
    # so a roster never spends its capture budget on a path that cannot publish.
    pre = os.path.join(tmp, "pre")
    shutil.copytree(FIX, pre)
    case("T19 preflight green", False, [sys.executable, "scripts/preflight.py", "--run", pre])
    rp3 = os.path.join(pre, SLUG, "report.json")
    rep3 = json.load(open(rp3, encoding="utf-8"))
    rep3["layer1"]["scorecard"][0]["verdict"] = "Excellent"      # outside the fixed vocabulary
    json.dump(rep3, open(rp3, "w", encoding="utf-8"), indent=1)
    case("T20 preflight red on a broken model", True,
         [sys.executable, "scripts/preflight.py", "--run", pre])

    # T21 - a short inventory is flagged even though its coverage reads 100%.
    disc = os.path.join(tmp, "disc")
    os.makedirs(disc, exist_ok=True)
    dsubs = []
    for slug, n in [("subject-full", 4), ("subject-full2", 4), ("subject-thin", 1)]:
        shutil.copytree(os.path.join(FIX, SLUG), os.path.join(disc, slug))
        dsubs.append({"slug": slug, "name": slug, "org": "Example Group"})
        rp4 = os.path.join(disc, slug, "report.json")
        r4 = json.load(open(rp4, encoding="utf-8"))
        r4["subject"]["slug"] = slug
        json.dump(r4, open(rp4, "w", encoding="utf-8"), indent=1)
        mp4 = os.path.join(disc, slug, "assets.json")
        m4 = json.load(open(mp4, encoding="utf-8"))
        m4["assets"] = [a for a in m4["assets"] if a.get("state") == "shown"][:n]
        json.dump(m4, open(mp4, "w", encoding="utf-8"), indent=1)
    json.dump(dsubs, open(os.path.join(disc, "subjects.json"), "w", encoding="utf-8"), indent=1)
    shutil.copy(os.path.join(FIX, "run.json"), os.path.join(disc, "run.json"))
    run([sys.executable, "scripts/render_html.py", "--run", disc, "--all"])
    run(["node", "scripts/render_docx.js", "--run", disc, "--all"])
    rc, out = run([sys.executable, "scripts/accept_roster.py", "--run", disc])
    RESULTS.append(("T21 short inventory flagged at 100%",
                    "suspiciously short inventory" in out and "subject-thin" in out, rc,
                    "flagged despite 100% coverage"))

    print("\nSelf-test \u2014 %d case(s)" % len(RESULTS))
    print("-" * 72)
    bad = 0
    for name, ok, rc, note in RESULTS:
        bad += (not ok)
        print("%-6s %-32s %s" % ("PASS" if ok else "FAIL", name, note[:34]))
    print("\n%d failed" % bad)
    if args.keep:
        print("run kept at %s" % run_dir)
    else:
        shutil.rmtree(tmp, ignore_errors=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
