#!/usr/bin/env python3
"""
Generate a per-journey cutover runbook. Every action on production is a human-confirmed step.

  cutover_runbook.py --out <outdir> [--jbsystem-flows JBSystem_Credit_c_RecordFlow,JBSystemFlow_Credit_c,...]

Reads ir/*.json and register.csv. Writes cutover/<journey>.md and cutover/jbsystem_decommission.md.
Drain window = longest cumulative wait on any path, so contacts already in the MCE journey finish there.
"""
import argparse, csv, glob, json, os, re
from collections import defaultdict

UNIT_DAYS = {"MINUTES": 1 / 1440, "HOURS": 1 / 24, "DAYS": 1, "WEEKS": 7, "MONTHS": 31, "YEARS": 365}

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:80] or "journey"

def drain_days(rec):
    el = {e["key"]: e for e in rec["elements"]}
    nxt = defaultdict(list)
    for e in rec["edges"]:
        nxt[e["from"]].append(e["to"])
    memo = {}
    def longest(k, stack=()):
        if k in memo:
            return memo[k]
        if k in stack or k not in el:
            return 0
        e = el[k]; d = 0
        if e["type"] == "WAIT" and e["status"] != "drop":
            d = (e["detail"].get("waitDuration") or 0) * UNIT_DAYS.get(str(e["detail"].get("waitUnit")).upper(), 0)
        memo[k] = d + max([longest(n, stack + (k,)) for n in nxt[k]] or [0])
        return memo[k]
    return round(max([longest(r) for r in rec["roots"]] or [0]), 1)

def stop_entry(r):
    t = r["entry_type"]
    if t == "SalesforceObj":
        return (f"Entry is MC Connect on `{r['salesforce_object']}`. Do not deactivate the JBSystem flow for this object here. "
                "See jbsystem_decommission.md: it can only go once every journey on the object has cut over.")
    if t == "AutomationAudience":
        return "Pause the automation that feeds the entry DE (`sfmc_schedule_automation`, pause). Confirm with the owner first."
    if t == "EmailAudience":
        return "Stop whatever populates the entry DE (import, query or API). Then confirm the DE stops receiving rows."
    if t == "Loyalty":
        return "Disable the Loyalty promotion's MCE journey generation, then confirm no new entries."
    return "Identify and stop the entry source manually before activation."

def runbook(rec, row):
    days = drain_days(rec)
    once = row["entry_mode"] in ("OnceAndDone", "SingleEntryAcrossAllVersions", "NoReentry")
    lines = [f"# Cutover: {rec['name']}", "",
             f"Target flow: `{re.sub(r'[^A-Za-z0-9]+','_',rec['name']).strip('_')}_MCNext` · {row['flow_type']} · verdict {row.get('verdict','-')}",
             f"Drain window: **{days} days** (longest wait path). Contacts already in MCE finish there.", "",
             "## Gate: all must be true before go-live", "",
             "- [ ] Parity check passed on the deployed Draft (`verify_parity.py` exit 0).",
             "- [ ] Every email and SMS referenced is published in MC Next and passed seed tests.",
             "- [ ] Entry segment published and count reconciled against the MCE entry DE (±2%).",
             "- [ ] Data Graph exposes every Decision attribute in the build spec.",
             "- [ ] Subscriptions/consent for the send classification's publication list migrated.",
             "- [ ] UAT run with seed records down every Decision outcome, screenshots attached.",
             "- [ ] Business owner sign-off.", ""]
    if once:
        lines += ["## Re-entry guard seed", "",
                  f"Entry mode `{row['entry_mode']}`. Before activation, load everyone who already entered the MCE journey "
                  "into the guard (flag field, Campaign Member or segment exclusion). Source: `_JourneyActivity` + `_Journey` "
                  f"data views filtered on journey id `{rec['id']}`. Skipping this re-sends to past recipients.", ""]
    lines += ["## Sequence (production)", "",
              "1. " + stop_entry(row),
              "2. Activate the MC Next flow. Confirm first entries within one segment refresh or trigger cycle.",
              "3. Leave the MCE journey running (no new entries) for the drain window.",
              f"4. After {days} days, confirm `currentPopulation = 0` on the MCE journey, then stop the version.",
              "5. Update the migration manifest: status `live`, cutover date.", "",
              "## Rollback (within drain window)", "",
              "1. Deactivate the MC Next flow.",
              "2. Re-enable the MCE entry source stopped in step 1.",
              "3. Contacts who entered the flow keep their guard record, so they will not re-enter either system.", ""]
    return "\n".join(lines)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--jbsystem-flows", default="", help="comma list of JBSystem flow API names found in the org")
    a = ap.parse_args()
    rows = {r["id"]: r for r in csv.DictReader(open(os.path.join(a.out, "register.csv")))}
    os.makedirs(os.path.join(a.out, "cutover"), exist_ok=True)
    for f in glob.glob(os.path.join(a.out, "ir", "*.json")):
        rec = json.load(open(f))
        open(os.path.join(a.out, "cutover", slug(rec["name"]) + ".md"), "w").write(runbook(rec, rows[rec["id"]]))

    by_obj = defaultdict(list)
    for r in rows.values():
        if r["entry_type"] == "SalesforceObj" and r["disposition"] != "Retire":
            by_obj[r["salesforce_object"]].append(r["name"])
    flows = [f.strip() for f in a.jbsystem_flows.split(",") if f.strip()]
    lines = ["# JBSystem flow decommission", "",
             "MC Connect creates `JBSystem_<Object>_RecordFlow` and `JBSystemFlow_<Object>` in core to feed Salesforce-entry journeys. "
             "Deactivate a pair only when **every** live journey on that object has cut over. Deactivating early silently stops the rest.", "",
             "| Object | Live journeys depending on it | JBSystem flows found |", "|---|---|---|"]
    def pair(obj):
        k = obj.replace("__", "_")
        return {f"JBSystem_{k}_RecordFlow", f"JBSystemFlow_{k}"}
    for obj, names in sorted(by_obj.items()):
        found = sorted(pair(obj) & set(flows))
        lines.append(f"| `{obj}` | {'; '.join(names)} | {', '.join(found) or 'none listed'} |")
    claimed = set().union(*[pair(o) for o in by_obj]) if by_obj else set()
    orphan = [f for f in flows if f not in claimed]
    if orphan:
        lines += ["", "JBSystem flows with no live journey in the register (candidates to deactivate after confirming in JB):", ""]
        lines += [f"- `{f}`" for f in orphan]
    open(os.path.join(a.out, "cutover", "jbsystem_decommission.md"), "w").write("\n".join(lines) + "\n")
    print(f"Runbooks written for {len(glob.glob(os.path.join(a.out, 'ir', '*.json')))} journeys + JBSystem decommission table.")

if __name__ == "__main__":
    main()
