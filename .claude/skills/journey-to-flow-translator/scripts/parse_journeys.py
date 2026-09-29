#!/usr/bin/env python3
"""
Translate Marketing Cloud Engagement journeys into an MC Next Flow intermediate representation.

Two tiers, same script:
  Tier 1 (triage):   --list  <file(s)>   Output of GET /interaction/v1/interactions (no activities).
  Tier 2 (translate): --workdir <dir>    One JSON per journey from sfmc_get_journey (extras=activities).
                                          Full payloads or the slim schema in references/slim_schema.md.

Outputs to --out:
  register.csv   one row per journey (triage fields + translation fields where available)
  ir/<slug>.json per translated journey: ordered flow elements, conditions, flags, dependencies
  summary.json   headline counts, verdict mix, families, top flags
"""
import argparse, csv, glob, hashlib, html, json, os, re, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
RULES = json.load(open(os.path.join(HERE, "mapping_rules.json")))
SEVERITY = {"drop": 0, "direct": 1, "adapt": 2, "rearchitect": 3}
VERDICT = {1: "A", 2: "B", 3: "C"}
VERDICT_LABEL = {"A": "Direct rebuild", "B": "Adapt", "C": "Re-architect"}
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
LOYALTY_KEY = re.compile(r"^(PL|AJP|FSU|FP)_([A-Z0-9]+)_")


# ---------------------------------------------------------------- helpers
def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:80] or "journey"

def parse_dt(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s[:26], fmt)
        except ValueError:
            continue
    return None

def load_json_any(path):
    txt = open(path, encoding="utf-8").read()
    # tolerate the MCP wrapper text around the JSON body
    start = min([i for i in (txt.find("{"), txt.find("[")) if i >= 0], default=0)
    return json.loads(txt[start:txt.rfind("}") + 1] if txt[start] == "{" else txt[start:txt.rfind("]") + 1])


# ---------------------------------------------------------------- entry
def entry_source(j):
    """Return (entry_type, source_key). Uses triggers when present, else infers from defaults.email."""
    trig = (j.get("triggers") or [{}])[0]
    ttype = trig.get("type", "")
    key = (trig.get("metaData") or {}).get("eventDefinitionKey", "") or j.get("key", "")
    email_default = " ".join((j.get("defaults") or {}).get("email", []) or [])
    m = re.search(r"\{\{Event\.([^.\"]+)\.", email_default)
    src = m.group(1) if m else key

    if LOYALTY_KEY.match(j.get("key", "") or ""):
        return "Loyalty", j.get("key")
    if ttype in RULES["entry"]:
        return ttype, src
    if ttype == "SalesforceObjectTriggerV2" or src.startswith("SalesforceObj"):
        return "SalesforceObj", src
    if ttype == "APIEvent" or src.startswith("APIEvent"):
        return "APIEvent", src
    if src.startswith("AutomationAud"):
        return "AutomationAudience", src
    if src.startswith("DEAudience"):
        return "EmailAudience", src
    if "Contact.SendableAttribute" in email_default or ttype == "ContactAudience":
        return "ContactAudience", "Contact model"
    if ttype in ("CloudPagesEvent", "SmartCapture"):
        return "CloudPages", src
    return "Unknown", src


def salesforce_object(j):
    email_default = " ".join((j.get("defaults") or {}).get("email", []) or [])
    m = re.search(r"\\?\"(?:\[\[UNTRUSTED: )?(?:[^:\"]+: \]\])?([A-Za-z0-9_]+):", email_default)
    return m.group(1) if m else ""


# ---------------------------------------------------------------- families
def family_key(name, key):
    lk = LOYALTY_KEY.match(key or "")
    if lk:
        return f"Loyalty promotion {lk.group(2)}"
    n = re.sub(rf"_?({MONTHS})_?", "_", name)
    n = re.sub(r"_?Sprint\d+", "", n)
    n = re.sub(r"_?V\d+\b", "", n)
    n = re.sub(r"_?\d{4}\b", "", n)
    n = re.sub(r"_+", "_", n).strip("_ ")
    return n

def series_key(name):
    m = re.search(rf"_({MONTHS})_Sprint\d+_\d{{4}}", name)
    return "Life-stage Sprint series" if m else ""


# ---------------------------------------------------------------- decisions
def parse_criteria(xml_text):
    conds = []
    if not xml_text:
        return conds
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return [{"raw": xml_text[:200], "flags": ["unparsed"]}]
    for c in root.iter("Condition"):
        key = c.get("Key", "")
        op = c.get("Operator", "")
        val_el = c.find("Value")
        val = (val_el.text or "") if val_el is not None else ""
        ref_param = c.get("ValueParameterName", "")
        flags = []
        if key.startswith("Event."):
            parts = key.split(".")
            source, field = parts[1], parts[-1]
            flags.append("event_attribute")
        else:
            parts = key.split(".")
            source, field = (parts[0], parts[-1]) if len(parts) > 1 else ("", key)
            flags.append("contact_attribute")
        if c.get("ValueIsReference") == "true" or ref_param:
            flags.append("reference_join")
            val = val or ref_param
        if op == "ExistsInWholeWord":
            flags.append("list_operator")
            if len([v for v in val.split(",") if v.strip()]) > 3:
                flags.append("hardcoded_list")
        ref_target = ""
        if "reference_join" in flags:
            ref_target = re.sub(r"^Event\.[^.]+\.", "", val) if val else ""
        conds.append({
            "source": source, "field": field, "operator": op, "ref_target": ref_target,
            "operator_text": RULES["decision_operators"].get(op, op),
            "value": val.strip(), "flags": flags,
        })
    srcs = {("event" if "event_attribute" in c.get("flags", []) else "contact") for c in conds}
    if len(srcs) > 1:
        for c in conds:
            c["flags"].append("mixed_data_sources")
    return conds

def human_condition(c):
    if "raw" in c:
        return c["raw"]
    v = c["value"]
    if c["operator"] in ("IsNull", "IsNotNull"):
        return f"{c['field']} {c['operator_text']}"
    if "reference_join" in c["flags"]:
        return f"{c['field']} {c['operator_text']} {v} (cross-object)"
    return f"{c['field']} {c['operator_text']} {v}"


# ---------------------------------------------------------------- activities
def classify_activity(a, has_next):
    t = a.get("type", "")
    ca = a.get("configurationArguments") or {}
    md = a.get("metaData") or {}
    out = {"key": a.get("key"), "name": a.get("name", ""), "type": t, "flags": [], "detail": {}}

    if t == "WAIT":
        wtype = md.get("waitType") or ("duration" if ca.get("waitDuration") else "date")
        if ca.get("waitEndDateAttributeExpression"):
            wtype = "attribute"
        if ca.get("waitForEventKey"):
            wtype = "event"
        if not has_next:
            rule_key = "WAIT_terminal"
        else:
            rule_key = f"WAIT_{wtype}"
            if wtype == "duration" and str(ca.get("waitUnit", "")).upper() == "MINUTES" and (ca.get("waitDuration") or 0) <= 5:
                out["flags"].append("spacer_wait")
        out["detail"] = {k: ca.get(k) for k in ("waitDuration", "waitUnit", "specifiedTime", "timeZone",
                                                  "specificDate", "waitEndDateAttributeExpression", "waitForEventKey") if ca.get(k)}
    elif t in ("EMAILV2", "EMAIL"):
        rule_key = t
        ts = ca.get("triggeredSend") or {}
        subj = ts.get("emailSubject") or (a.get("arguments") or {}).get("emailSubjectDataBound", "")
        out["detail"] = {"emailId": ts.get("emailId"), "subject": subj, "preheader": ts.get("preHeader", ""),
                         "publicationListId": ts.get("publicationListId"),
                         "sendClassificationId": ts.get("sendClassificationId"),
                         "senderProfileId": ts.get("senderProfileId")}
        if "%%" in (subj or ""):
            out["flags"].append("subject_ampscript")
    elif t in ("SMSSYNC", "SMS"):
        rule_key = t
        body = (a.get("metaData") or {}).get("store", {}).get("selectedContentBuilderMessage", "") if isinstance(md.get("store"), dict) else ""
        body = body or md.get("smsBody", "")
        sel = ((md.get("store") or {}).get("messageConfiguration") or {}).get("selectedCode", {}) if isinstance(md.get("store"), dict) else {}
        out["detail"] = {"assetId": ca.get("assetId"), "from": ca.get("fromName"),
                         "country": sel.get("countryCode") or md.get("country", ""),
                         "isOptIn": ca.get("isOptIn"),
                         "blackout": f"{ca.get('mobileBlackoutWindowStartTime')}-{ca.get('mobileBlackoutWindowEndTime')}"
                                     if ca.get("honorBlackoutWindowEnum") else ""}
        if ca.get("honorBlackoutWindowEnum"):
            out["flags"].append("sms_blackout")
        if re.search(r"\bLookup(Rows|OrderedRows)?\s*\(", body or "", re.I):
            out["flags"].append("sms_ampscript_lookup")
        out["detail"]["body_excerpt"] = re.sub(r"%%\[.*?\]%%", "", body or "", flags=re.S).strip()[:160]
    elif t == "MULTICRITERIADECISION":
        rule_key = t
        crit = ca.get("criteria") or {}
        branches = []
        for o in a.get("outcomes", []):
            ok = o.get("key")
            label = (o.get("metaData") or {}).get("label") or ok
            conds = parse_criteria(crit.get(ok, "")) if ok != "remainder_path" else []
            for c in conds:
                out["flags"].extend(c.get("flags", []))
            branches.append({"outcome": ok, "label": label, "next": o.get("next"),
                             "conditions": conds,
                             "readable": " AND ".join(human_condition(c) for c in conds) if conds
                                         else ("Everyone else" if ok == "remainder_path" else
                                               (o.get("metaData") or {}).get("criteriaDescription", ""))})
        out["detail"] = {"branches": branches}
        if not out["name"]:
            fields = [c["field"] for b in branches for c in b["conditions"] if "field" in c]
            out["name"] = ("Split on " + ", ".join(dict.fromkeys(fields))[:60]) if fields else "Split"
    else:
        rule_key = t if t in RULES["activities"] else "_default"

    rule = RULES["activities"].get(rule_key, RULES["activities"]["_default"])
    out["rule_key"] = rule_key
    out["element"] = rule["element"]
    out["status"] = rule["status"]
    out["note"] = rule["note"]
    out["flags"] = sorted(set(out["flags"]))
    return out


# ---------------------------------------------------------------- graph
def walk(j):
    acts = {a["key"]: a for a in j.get("activities", []) if a.get("key")}
    referenced = {o.get("next") for a in acts.values() for o in a.get("outcomes", []) if o.get("next")}
    roots = [k for k in acts if k not in referenced] or list(acts)[:1]
    order, seen, edges = [], set(), []
    queue = [(r, 0, "") for r in roots]
    while queue:
        k, depth, via = queue.pop(0)
        if k in seen or k not in acts:
            continue
        seen.add(k)
        a = acts[k]
        nexts = [o for o in a.get("outcomes", []) if o.get("next")]
        node = classify_activity(a, has_next=bool(nexts))
        node["depth"] = depth
        order.append(node)
        for o in a.get("outcomes", []):
            if o.get("next"):
                label = (o.get("metaData") or {}).get("label", "")
                edges.append({"from": k, "to": o["next"], "label": label})
                queue.append((o["next"], depth + 1, label))
    orphans = [k for k in acts if k not in seen]
    return order, edges, roots, orphans


def signature(order, entry_type):
    parts = [entry_type]
    for n in order:
        if n["status"] == "drop":
            continue
        if n["type"] == "WAIT":
            d = n["detail"]
            parts.append(f"W{d.get('waitDuration','')}{(d.get('waitUnit') or '')[:1]}")
        elif n["type"] == "MULTICRITERIADECISION":
            parts.append(f"D{len(n['detail']['branches'])}")
        else:
            parts.append(n["type"][:3])
    return hashlib.md5("|".join(parts).encode()).hexdigest()[:8], "|".join(parts)


# ---------------------------------------------------------------- journey
def triage(j, as_of, dormant_days):
    etype, src = entry_source(j)
    last = parse_dt((j.get("activity") or {}).get("lastContactProcessed"))
    days_idle = (as_of - last).days if last else None
    dormant = days_idle is None or days_idle > dormant_days
    exits = j.get("exits") or []
    goals = j.get("goals") or []
    mode = j.get("entryMode", "MultipleEntries")
    return {
        "id": j.get("id"), "name": j.get("name", ""), "key": j.get("key", ""),
        "version": j.get("version"), "status": j.get("status", ""),
        "entry_type": etype, "entry_source": src, "salesforce_object": salesforce_object(j) if etype == "SalesforceObj" else "",
        "flow_type": RULES["entry"][etype]["flow_type"], "entry_status": RULES["entry"][etype]["status"],
        "entry_note": RULES["entry"][etype]["note"],
        "entry_mode": mode, "reentry_status": RULES["entry_mode"].get(mode, {"status": "adapt"})["status"],
        "reentry_pattern": RULES["entry_mode"].get(mode, {"pattern": "Unknown mode. Verify."})["pattern"],
        "has_sms": bool((j.get("defaults") or {}).get("mobileNumber")) and "legacyfallback" not in str((j.get("defaults") or {}).get("mobileNumber")),
        "exit_criteria": [((e.get("metaData") or {}).get("criteriaDescription", "")) for e in exits],
        "goals": [((g.get("metaData") or {}).get("criteriaDescription", "")) for g in goals],
        "last_contact_processed": last.isoformat() if last else "",
        "days_idle": days_idle, "dormant": dormant,
        "family": family_key(j.get("name", ""), j.get("key", "")),
        "series": series_key(j.get("name", "")),
        "last_published": j.get("lastPublishedDate", ""),
    }


def translate(j, as_of, dormant_days):
    t = triage(j, as_of, dormant_days)
    order, edges, roots, orphans = walk(j)
    flags = Counter()
    for n in order:
        flags.update(n["flags"])
    if t["exit_criteria"]:
        flags["exit_criteria"] += len(t["exit_criteria"])
    if t["goals"]:
        flags["goal"] += len(t["goals"])
    if t["dormant"]:
        flags["dormant"] += 1

    statuses = [SEVERITY[n["status"]] for n in order] + [SEVERITY[t["entry_status"]], SEVERITY[t["reentry_status"]]]
    worst = max([s for s in statuses if s > 0] or [1])
    if flags.get("reference_join") and worst < 3:
        worst = 3  # cross-object joins in decisions need data model work before the flow can exist
    verdict = VERDICT[worst]

    effective = [n for n in order if n["status"] != "drop"]
    decisions = [n for n in effective if n["type"] == "MULTICRITERIADECISION"]
    sig, sig_text = signature(order, t["entry_type"])

    deps = {
        "emails": sorted({n["detail"].get("emailId") for n in effective if n["type"].startswith("EMAIL") and n["detail"].get("emailId")}),
        "sms_assets": sorted({n["detail"].get("assetId") for n in effective if n["type"].startswith("SMS") and n["detail"].get("assetId")}),
        "sms_senders": sorted({f"{n['detail'].get('from')} ({n['detail'].get('country')})" for n in effective if n["type"].startswith("SMS")}),
        "publication_lists": sorted({n["detail"].get("publicationListId") for n in effective if n["detail"].get("publicationListId")}),
        "entry_source": t["entry_source"],
        "attributes": sorted({f"{c['source']}.{c['field']}" for d in decisions for b in d["detail"]["branches"] for c in b["conditions"] if "field" in c}
                             | {c["ref_target"] for d in decisions for b in d["detail"]["branches"] for c in b["conditions"] if c.get("ref_target")}),
    }
    complexity = len(effective) + 2 * len(decisions) + 3 * sum(1 for n in effective if n["status"] == "rearchitect") \
                 + sum(v for k, v in flags.items() if k in ("reference_join", "mixed_data_sources", "hardcoded_list"))

    t.update({
        "translated": True, "verdict": verdict, "verdict_label": VERDICT_LABEL[verdict],
        "elements": order, "edges": edges, "roots": roots, "orphans": orphans,
        "effective_steps": len(effective), "dropped_steps": len(order) - len(effective),
        "decisions": len(decisions), "flags": dict(flags), "dependencies": deps,
        "signature": sig, "signature_text": sig_text, "complexity": complexity,
    })
    return t


TEST_NAME = re.compile(r"(^|[_\s-])(test|tst|copy|sandbox|demo)([_\s-]|$)", re.I)

def disposition(rec, family_sizes):
    if TEST_NAME.search(rec["name"]):
        rec["retire_reason"] = "test/copy journey"
        return "Retire"
    if rec["dormant"]:
        rec["retire_reason"] = f"no contact in {rec['days_idle']} days" if rec["days_idle"] is not None else "never processed a contact"
        return "Retire"
    if rec.get("series") or family_sizes.get(rec["family"], 0) > 1:
        return "Consolidate"
    return "Migrate"


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", nargs="*", default=[], help="interaction list JSON file(s) for triage")
    ap.add_argument("--workdir", help="dir of full or slim journey JSON files for translation")
    ap.add_argument("--out", required=True)
    ap.add_argument("--as-of", default=None, help="YYYY-MM-DD for dormancy calc (default: today UTC)")
    ap.add_argument("--dormant-days", type=int, default=180)
    args = ap.parse_args()

    as_of = datetime.strptime(args.as_of, "%Y-%m-%d") if args.as_of else datetime.now(timezone.utc).replace(tzinfo=None)
    os.makedirs(os.path.join(args.out, "ir"), exist_ok=True)

    records = {}
    for f in args.list:
        data = load_json_any(f)
        for j in (data.get("items") if isinstance(data, dict) else data) or []:
            records[j["id"]] = triage(j, as_of, args.dormant_days)
    if args.workdir:
        for f in sorted(glob.glob(os.path.join(args.workdir, "*.json"))):
            j = load_json_any(f)
            if not j.get("activities"):
                continue
            rec = translate(j, as_of, args.dormant_days)
            records[rec["id"]] = rec
            json.dump(rec, open(os.path.join(args.out, "ir", slug(rec["name"]) + ".json"), "w"), indent=2, default=str)

    if not records:
        sys.exit("No journeys loaded. Check --list / --workdir inputs.")

    fam = Counter(r["family"] for r in records.values() if not r["dormant"] and not TEST_NAME.search(r["name"]))
    sig_groups = defaultdict(list)
    for r in records.values():
        r["disposition"] = disposition(r, fam)
        if r.get("signature"):
            sig_groups[r["signature"]].append(r["name"])
    for r in records.values():
        r["structural_twins"] = len(sig_groups.get(r.get("signature"), [])) - 1 if r.get("signature") else ""

    cols = ["name", "id", "version", "disposition", "verdict", "verdict_label", "flow_type", "entry_type", "entry_source",
            "salesforce_object", "entry_mode", "reentry_status", "has_sms", "effective_steps", "decisions", "complexity",
            "days_idle", "last_contact_processed", "family", "series", "structural_twins", "retire_reason", "exit_criteria", "top_flags"]
    with open(os.path.join(args.out, "register.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in sorted(records.values(), key=lambda r: (r["disposition"], r["family"], r["name"])):
            row = dict(r)
            row["exit_criteria"] = "; ".join(r["exit_criteria"])
            row["top_flags"] = ", ".join(sorted((r.get("flags") or {}).keys()))
            w.writerow(row)

    live = [r for r in records.values() if not r["dormant"]]
    summary = {
        "as_of": as_of.date().isoformat(), "dormant_days": args.dormant_days,
        "total": len(records), "live": len(live), "dormant": len(records) - len(live),
        "translated": sum(1 for r in records.values() if r.get("translated")),
        "disposition": Counter(r["disposition"] for r in records.values()),
        "verdicts": Counter(r["verdict"] for r in records.values() if r.get("verdict")),
        "flow_types": Counter(r["flow_type"] for r in live),
        "entry_modes": Counter(r["entry_mode"] for r in live),
        "families": {k: v for k, v in fam.most_common() if v > 1},
        "series": Counter(r["series"] for r in records.values() if r["series"]),
        "structural_groups": {k: v for k, v in sig_groups.items() if len(v) > 1},
        "flags": sum((Counter(r.get("flags") or {}) for r in records.values()), Counter()),
    }
    json.dump(summary, open(os.path.join(args.out, "summary.json"), "w"), indent=2, default=str)
    print(json.dumps({k: summary[k] for k in ("total", "live", "dormant", "translated", "disposition", "verdicts")}, default=str))


if __name__ == "__main__":
    main()
