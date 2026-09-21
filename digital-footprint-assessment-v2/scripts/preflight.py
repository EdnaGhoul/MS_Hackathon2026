#!/usr/bin/env python3
"""preflight.py — prove the pipeline works on ONE subject before dispatching N.

A roster is expensive: ten subjects is up to two hours of serial capture. If the
render-and-gate path is broken, every minute of that is wasted, and the failure
only becomes visible at the very end — which is precisely when it is most costly
to discover. This pushes subject 1 all the way through render → both gates and
reports whether the rest of the roster should start.

  python scripts/preflight.py --run <run-dir>            # first subject with a model
  python scripts/preflight.py --run <run-dir> --subject <slug>

Exit 0 = the path is green, dispatch the rest. Exit 1 = stop; fix the pipeline
before spending the roster's capture budget.
"""
import argparse, os, subprocess, sys
import _dfa

HERE = os.path.dirname(os.path.abspath(__file__))
NODE_PATH = os.environ.get("NODE_PATH", "/usr/lib/node_modules")


def step(label, cmd, env=None):
    p = subprocess.run(cmd, capture_output=True, text=True,
                       cwd=os.path.dirname(HERE), env=env or os.environ.copy())
    ok = p.returncode == 0
    tail = (p.stdout + p.stderr).strip().splitlines()
    print("%-6s %s" % ("ok" if ok else "FAIL", label))
    if not ok:
        for line in tail[-6:]:
            print("        %s" % line)
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--subject")
    args = ap.parse_args()

    subjects = _dfa.read_json(os.path.join(args.run, "subjects.json"))
    slug = args.subject
    if not slug:
        ready = [s["slug"] for s in subjects
                 if os.path.exists(_dfa.report_path(args.run, s["slug"]))
                 and os.path.exists(_dfa.manifest_path(args.run, s["slug"]))]
        if not ready:
            print("PREFLIGHT CANNOT RUN — no subject has both report.json and assets.json yet. "
                  "Finish one subject's research and capture first.")
            return 1
        slug = ready[0]

    print("Preflight on %s (%d subject(s) in this roster)\n%s" % (slug, len(subjects), "-" * 62))
    env = dict(os.environ, NODE_PATH=NODE_PATH)
    py = sys.executable
    ok = True
    ok &= step("contracts validate", [py, "scripts/validate_json.py", "report",
                                      _dfa.report_path(args.run, slug)])
    ok &= step("manifest validates", [py, "scripts/validate_json.py", "assets",
                                      _dfa.manifest_path(args.run, slug)])
    ok &= step("images reconcile", [py, "scripts/image_qc.py", "--run", args.run,
                                    "--subject", slug])
    ok &= step("HTML renders", [py, "scripts/render_html.py", "--run", args.run,
                                "--subject", slug])
    ok &= step("Word renders", ["node", "scripts/render_docx.js", "--run", args.run,
                                "--subject", slug], env)
    ok &= step("HTML gate green", [py, "scripts/accept_report.py", "--run", args.run,
                                   "--subject", slug])
    ok &= step("Word gate green", [py, "scripts/accept_docx.py", "--run", args.run,
                                   "--subject", slug])

    print("-" * 62)
    if ok:
        print("PREFLIGHT GREEN — the render-and-gate path works end to end.\n"
              "Dispatch the remaining %d subject(s)." % max(0, len(subjects) - 1))
        return 0
    print("PREFLIGHT RED — do NOT start the rest of the roster.\n"
          "Every subject would hit the same failure after its capture budget was spent.\n"
          "Fix the step above, re-run preflight, then dispatch.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
