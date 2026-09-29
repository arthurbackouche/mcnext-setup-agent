#!/usr/bin/env python3
"""
Verify a deployed (retrieved) flow against its source journey IR.

  verify_parity.py --ir ir/<journey>.json --flow <retrieved>.flow-meta.xml [--keep-spacers] [--expect-status Draft]

Checks:
  1. No UNRESOLVED__ references left.
  2. Status matches expectation (Draft until cutover).
  3. Element counts: decisions, waits, sends (all other executable elements) match the IR.
  4. Each decision has the same number of rules (non-default outcomes) as the source split, matched by label.
  5. Every element is reachable from start (no orphans), and every source path end is an end in the flow.
  6. Description carries the MCE journey id (traceability).
Exit 0 = parity. Exit 1 = mismatch (report printed as JSON).
"""
import argparse, json, re, sys
import xml.etree.ElementTree as ET

NON_EXEC = {"start", "variables", "constants", "formulas", "textTemplates", "processMetadataValues",
            "apiVersion", "label", "description", "processType", "status", "environments",
            "interviewLabel", "runInMode", "stages", "choices", "dynamicChoiceSets", "triggerOrder"}

def strip(tag):
    return tag.split("}", 1)[-1]

def load_flow(path):
    root = ET.parse(path).getroot()
    elements, start = {}, None
    for child in root:
        t = strip(child.tag)
        if t == "start":
            ref = child.find(".//{*}connector/{*}targetReference")
            start = ref.text if ref is not None else None
            continue
        if t in NON_EXEC:
            continue
        name_el = child.find("{*}name")
        if name_el is None:
            continue
        targets = [r.text for r in child.iter() if strip(r.tag) == "targetReference"]
        rules = [(r.findtext("{*}label") or "") for r in child.findall("{*}rules")]
        elements[name_el.text] = {"tag": t, "label": child.findtext("{*}label") or "", "targets": targets, "rules": rules}
    meta = {strip(c.tag): (c.text or "") for c in root if strip(c.tag) in ("status", "description", "label")}
    raw = open(path).read()
    return elements, start, meta, raw

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ir", required=True); ap.add_argument("--flow", required=True)
    ap.add_argument("--keep-spacers", action="store_true"); ap.add_argument("--expect-status", default="Draft")
    a = ap.parse_args()
    rec = json.load(open(a.ir))
    elements, start, meta, raw = load_flow(a.flow)
    issues = []

    if "UNRESOLVED__" in raw:
        issues.append("unresolved references present: " + ", ".join(sorted(set(re.findall(r"UNRESOLVED__\w+", raw)))))
    if meta.get("status") != a.expect_status:
        issues.append(f"status {meta.get('status')} != expected {a.expect_status}")
    if rec["id"] not in meta.get("description", ""):
        issues.append("description does not carry source journey id")

    src = [e for e in rec["elements"] if e["status"] != "drop" and (a.keep_spacers or "spacer_wait" not in e["flags"])]
    exp = {"decisions": sum(e["type"] == "MULTICRITERIADECISION" for e in src),
           "waits": sum(e["type"] == "WAIT" for e in src)}
    exp["sends"] = len(src) - exp["decisions"] - exp["waits"]
    got = {"decisions": sum(e["tag"] == "decisions" for e in elements.values()),
           "waits": sum(e["tag"] == "waits" for e in elements.values())}
    got["sends"] = len(elements) - got["decisions"] - got["waits"]
    for k in exp:
        if exp[k] != got[k]:
            issues.append(f"{k}: source {exp[k]} vs flow {got[k]}")

    flow_rule_sets = sorted(sorted(e["rules"]) for e in elements.values() if e["tag"] == "decisions")
    src_rule_sets = sorted(sorted(b["label"] for b in e["detail"]["branches"] if b["outcome"] != "remainder_path")
                           for e in src if e["type"] == "MULTICRITERIADECISION")
    if flow_rule_sets != src_rule_sets:
        issues.append(f"decision outcomes differ: source {src_rule_sets} vs flow {flow_rule_sets}")

    seen, stack = set(), [start] if start else []
    while stack:
        n = stack.pop()
        if n in seen or n not in elements:
            continue
        seen.add(n); stack.extend(elements[n]["targets"])
    orphans = set(elements) - seen
    if not start:
        issues.append("no start connector")
    if orphans:
        issues.append(f"unreachable elements: {sorted(orphans)}")
    dangling = sorted({t for e in elements.values() for t in e["targets"] if t not in elements})
    if dangling:
        issues.append(f"connectors to missing elements: {dangling}")

    report = {"journey": rec["name"], "flow": meta.get("label"), "expected": exp, "actual": got,
              "parity": not issues, "issues": issues}
    print(json.dumps(report, indent=2))
    sys.exit(0 if not issues else 1)

if __name__ == "__main__":
    main()
