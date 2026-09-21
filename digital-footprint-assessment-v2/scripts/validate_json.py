#!/usr/bin/env python3
"""validate_json.py — fail fast on the data contracts.

An agent's deliverable in v2 is DATA, not markup, so the data has to be checked
the moment it is written. This validates a file against its JSON Schema (a
self-contained subset validator — no third-party package) and then applies the
report rules a schema cannot express: the fixed six-dimension score vocabulary,
in the fixed order, and the chip/classification vocabulary.

Usage
  python scripts/validate_json.py report  <path/report.json>
  python scripts/validate_json.py assets  <path/assets.json>
  python scripts/validate_json.py subjects <path/subjects.json>
  python scripts/validate_json.py report <path> --json

Exit 0 = valid, 1 = invalid (with every error listed), 2 = usage error.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMAS = os.path.join(os.path.dirname(HERE), "schemas")

# The fixed vocabulary. Comparability across a roster is the whole point:
# one person assessed today must line up against another assessed next month.
SCORECARD = [
    ("Credibility", ["Strong", "Adequate", "Thin"]),
    ("Adverse material", ["Clean", "Minor", "Material"]),
    ("Distinctiveness", ["High", "Moderate", "Low", "Absent"]),
    ("Discoverability", ["Strong", "Adequate", "Diluted", "Invisible"]),
    ("Consistency", ["Consistent", "Mixed", "Inconsistent"]),
    ("Momentum", ["Rising", "Steady", "Slowing", "Dormant"]),
]


# ------------------------------------------------------------- schema subset
def _type_ok(val, t):
    return {
        "object": lambda v: isinstance(v, dict),
        "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
        "boolean": lambda v: isinstance(v, bool),
    }[t](val)


def check(node, schema, path, root, errs):
    if "$ref" in schema:
        ref = schema["$ref"].lstrip("#/").split("/")
        tgt = root
        for part in ref:
            tgt = tgt[part]
        return check(node, tgt, path, root, errs)

    t = schema.get("type")
    if t and not _type_ok(node, t):
        errs.append("%s: expected %s, got %s" % (path, t, type(node).__name__))
        return
    if "enum" in schema and node not in schema["enum"]:
        errs.append("%s: %r is not one of %s" % (path, node, schema["enum"]))
    if isinstance(node, str):
        if len(node) < schema.get("minLength", 0):
            errs.append("%s: shorter than %d characters — placeholder or missing content"
                        % (path, schema["minLength"]))
    if isinstance(node, list):
        if len(node) < schema.get("minItems", 0):
            errs.append("%s: %d item(s), at least %d required" % (path, len(node), schema["minItems"]))
        if "maxItems" in schema and len(node) > schema["maxItems"]:
            errs.append("%s: %d item(s), at most %d allowed" % (path, len(node), schema["maxItems"]))
        if "items" in schema:
            for i, item in enumerate(node):
                check(item, schema["items"], "%s[%d]" % (path, i), root, errs)
    if isinstance(node, dict):
        for req in schema.get("required", []):
            if req not in node:
                errs.append("%s: missing required field %r" % (path, req))
        for key, sub in schema.get("properties", {}).items():
            if key in node:
                check(node[key], sub, "%s.%s" % (path, key), root, errs)


# --------------------------------------------------------------- extra rules
def report_rules(doc, errs):
    sc = (doc.get("layer1") or {}).get("scorecard") or []
    if len(sc) == 6:
        for i, (dim, allowed) in enumerate(SCORECARD):
            got = sc[i] if isinstance(sc[i], dict) else {}
            if got.get("dimension") != dim:
                errs.append("layer1.scorecard[%d]: dimension must be %r (fixed order), got %r"
                            % (i, dim, got.get("dimension")))
            elif got.get("verdict") not in allowed:
                errs.append("layer1.scorecard[%d] (%s): verdict %r is outside the fixed vocabulary %s"
                            % (i, dim, got.get("verdict"), allowed))
    queries = {r.get("query") for r in doc.get("first_impression", []) if isinstance(r, dict)}
    if len(queries) < 2:
        errs.append("first_impression: both queries must be sampled (bare name, and name + organisation)")
    rows = 0
    secs = doc.get("sections") or {}
    for key in ("career", "public_profile", "network", "title_variants"):
        rows += len(secs.get(key) or [])
    for key in ("coverage", "adverse"):
        rows += len((secs.get("media") or {}).get(key) or [])
    for key in ("by", "about", "not_assessable"):
        rows += len((secs.get("digital_social") or {}).get(key) or [])
    if rows < 10:
        errs.append("sections: %d tagged evidence rows — the labelling rule needs at least 10" % rows)


def assets_rules(doc, errs):
    ids = [a.get("id") for a in doc.get("assets", [])]
    if len(ids) != len(set(ids)):
        errs.append("assets: duplicate asset ids")
    for a in doc.get("assets", []):
        st = a.get("state")
        if st in {"verified", "shown"}:
            if not a.get("file"):
                errs.append("%s: %s but no captured file" % (a.get("id"), st))
            v = a.get("verification") or {}
            if v.get("result") != "match":
                errs.append("%s: %s without a recorded visual match — verification is mandatory"
                            % (a.get("id"), st))
        elif st not in {"candidate", "queued", "capturing", "captured"} and not a.get("reason"):
            errs.append("%s: terminal state %r with no machine-generated reason" % (a.get("id"), st))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    if len(args) != 2:
        print(__doc__)
        return 2
    kind, path = args
    schema_file = os.path.join(SCHEMAS, "%s.schema.json" % kind)
    if not os.path.exists(schema_file):
        print("unknown contract %r" % kind, file=sys.stderr)
        return 2
    schema = json.load(open(schema_file, encoding="utf-8"))
    try:
        doc = json.load(open(path, encoding="utf-8"))
    except Exception as exc:
        print("%s: unreadable JSON — %s" % (path, exc), file=sys.stderr)
        return 1

    errs = []
    check(doc, schema, kind, schema, errs)
    if kind == "report":
        report_rules(doc, errs)
    elif kind == "assets":
        assets_rules(doc, errs)

    if as_json:
        print(json.dumps({"file": path, "contract": kind, "valid": not errs, "errors": errs}, indent=1))
    else:
        if errs:
            print("INVALID  %s  (%d problem(s))" % (path, len(errs)))
            for e in errs:
                print("   ** %s" % e)
        else:
            print("VALID    %s  (%s contract)" % (path, kind))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
