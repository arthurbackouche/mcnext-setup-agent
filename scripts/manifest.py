#!/usr/bin/env python3
"""Manifest helper.
  manifest.py validate                 schema + referential checks
  manifest.py status                   phase and journey progress
  manifest.py merge <fragment.json>    merge a skill's journeys fragment by mce_id (never drops fields)
  manifest.py phase <name> <status> [--evidence path]"""
import json, os, sys, datetime as dt
from collections import Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MF, SC = os.path.join(ROOT, "manifest.json"), os.path.join(ROOT, "schema", "manifest.schema.json")
ORDER = ["triaged", "translated", "blocked", "deployed_draft", "parity_passed", "cutover_ready", "live", "retired"]

def load(): return json.load(open(MF))
def save(m): json.dump(m, open(MF, "w"), indent=2); print("manifest saved")

def validate(m):
    errs = []
    try:
        import jsonschema
        errs += [f"schema: {e.message} at {list(e.path)}" for e in jsonschema.Draft202012Validator(json.load(open(SC))).iter_errors(m)]
    except ImportError:
        for k in ("client", "orgs", "phases", "journeys"):
            if k not in m: errs.append(f"missing {k}")
    ids = [j["mce_id"] for j in m.get("journeys", [])]
    errs += [f"duplicate journey {i}" for i, c in Counter(ids).items() if c > 1]
    for j in m.get("journeys", []):
        if j.get("status") == "blocked" and not j.get("blocked_reason"):
            errs.append(f"{j['name']}: blocked without blocked_reason")
        for k, p in (j.get("artefacts") or {}).items():
            if isinstance(p, str) and not os.path.exists(os.path.join(ROOT, p)):
                errs.append(f"{j['name']}: artefact {k} missing at {p}")
    for name, ph in m.get("phases", {}).items():
        if ph.get("status") == "passed" and not ph.get("gate_evidence"):
            errs.append(f"phase {name} passed without gate_evidence")
    return errs

def merge(m, frag):
    by = {j["mce_id"]: j for j in m["journeys"]}
    for j in frag.get("journeys", []):
        cur = by.get(j["mce_id"])
        if cur is None:
            by[j["mce_id"]] = j; continue
        new_status = j.get("status")
        for k, v in j.items():
            if k == "status" and ORDER.index(cur.get("status", "triaged")) > ORDER.index(new_status or "triaged") and cur.get("status") != "blocked":
                continue  # never move a journey backwards
            if isinstance(v, dict) and isinstance(cur.get(k), dict):
                cur[k].update(v)
            elif v is not None:
                cur[k] = v
    m["journeys"] = list(by.values())
    return m

cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
m = load()
if cmd == "validate":
    e = validate(m); print("\n".join(e) or "manifest valid"); sys.exit(1 if e else 0)
elif cmd == "merge":
    m = merge(m, json.load(open(sys.argv[2]))); e = validate(m)
    if e: print("\n".join(e)); sys.exit(1)
    save(m)
elif cmd == "phase":
    ph = m["phases"].setdefault(sys.argv[2], {}); ph["status"] = sys.argv[3]
    ph["updated"] = dt.date.today().isoformat()
    if "--evidence" in sys.argv: ph["gate_evidence"] = sys.argv[sys.argv.index("--evidence") + 1]
    e = validate(m)
    if e: print("\n".join(e)); sys.exit(1)
    save(m)
else:
    print(f"{m['client']} · {m.get('edition','?')} · sandbox {m['orgs']['sandbox_alias']}")
    for n, p in m["phases"].items(): print(f"  {n:<12} {p['status']}")
    c = Counter(j["status"] for j in m["journeys"]); print("  journeys:", dict(c) or "none")
