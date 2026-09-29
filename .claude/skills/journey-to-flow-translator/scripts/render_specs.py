#!/usr/bin/env python3
"""
Render outputs from parse_journeys.py.

  --out <dir>        same dir passed to parse_journeys.py (reads ir/, register.csv, summary.json)
  --client "<Name>"  printed in headers
  --edition growth|advanced   drives Path Experiment availability notes

Writes:
  specs/<slug>.md          build spec per translated journey (Confluence-ready, Mermaid)
  prompts/<slug>.md        ready-to-paste Claude in Chrome build prompt
  estate_summary.md        triage story: retire / consolidate / migrate, verdict mix, systemic flags
  manifest_fragment.json   journeys block for the shared migration manifest
"""
import argparse, csv, glob, json, os, re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
RULES = json.load(open(os.path.join(HERE, "mapping_rules.json")))


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:80] or "journey"

def mm(s):
    return re.sub(r'["\[\]{}()<>|#;]', "", str(s))[:60]

def wait_text(d):
    if d.get("waitDuration"):
        n = d["waitDuration"]; u = str(d.get("waitUnit", "")).lower()
        t = f"{n} {u[:-1] if n == 1 and u.endswith('s') else u}"
        if d.get("specifiedTime") and d["specifiedTime"] != "00:00":
            t += f" then at {d['specifiedTime']}"
        return t
    if d.get("specificDate"):
        return f"until {d['specificDate']}"
    if d.get("waitEndDateAttributeExpression"):
        return f"until {d['waitEndDateAttributeExpression']}"
    if d.get("waitForEventKey"):
        return f"until event {d['waitForEventKey']}"
    return "wait"


def element_label(n):
    d = n["detail"]
    if n["type"] == "WAIT":
        return f"Wait: {wait_text(d)}"
    if n["type"].startswith("EMAIL"):
        return f"Email: {n['name'] or d.get('emailId')}"
    if n["type"].startswith("SMS"):
        return f"SMS: {n['name'] or d.get('assetId')}"
    if n["type"] == "MULTICRITERIADECISION":
        return f"Decision: {n['name'] or 'split'}"
    return f"{n['element']}: {n['name'] or n['type']}"


def mermaid(rec):
    lines = ["flowchart TD", f'  START(["{mm(rec["flow_type"])} entry<br/>{mm(rec["entry_source"])}"])']
    keep = {n["key"]: n for n in rec["elements"] if n["status"] != "drop"}
    ids = {k: f"N{i}" for i, k in enumerate(keep)}
    for k, n in keep.items():
        shape = ('{{"%s"}}' if n["type"] == "MULTICRITERIADECISION" else '["%s"]') % mm(element_label(n))
        lines.append(f"  {ids[k]}{shape}")
    for r in rec["roots"]:
        if r in ids:
            lines.append(f"  START --> {ids[r]}")
    ended = set()
    for e in rec["edges"]:
        a, b = e["from"], e["to"]
        if a not in ids:
            continue
        lab = f'|"{mm(e["label"])}"|' if e.get("label") else ""
        if b in ids:
            lines.append(f"  {ids[a]} -->{lab} {ids[b]}")
        else:  # edge into a dropped terminal wait = end of path
            lines.append(f"  {ids[a]} -->{lab} END((End))")
            ended.add(a)
    styles = {"adapt": "fill:#FFF4D6,stroke:#C98A00", "rearchitect": "fill:#FDE2E1,stroke:#C23934", "direct": "fill:#E3F4E8,stroke:#2E844A"}
    for k, n in keep.items():
        lines.append(f"  style {ids[k]} {styles.get(n['status'], '')}")
    return "\n".join(lines)


def spec_md(rec, client, edition):
    f = rec["flags"]
    deps = rec["dependencies"]
    out = [f"# {rec['name']} → MC Next Flow build spec", "",
           f"Client: {client}  ",
           f"Source journey: `{rec['id']}` v{rec['version']}  ",
           f"Verdict: **{rec['verdict']} · {rec['verdict_label']}**  ",
           f"Disposition: **{rec['disposition']}**  ",
           f"Last contact processed: {rec['last_contact_processed'] or 'never'}"
           + (f" ({rec['days_idle']} days idle)" if rec['days_idle'] is not None else ""), ""]
    if rec["disposition"] == "Retire":
        out += ["> Dormant. Confirm with the business owner before rebuilding. Default recommendation: retire.", ""]
    if rec.get("structural_twins"):
        out += [f"> {rec['structural_twins']} other journey(s) share this exact structure (signature `{rec['signature']}`). "
                "Build one parameterised flow, not one per journey.", ""]

    out += ["## Entry", "",
            f"| Item | MCE | MC Next |", "|---|---|---|",
            f"| Trigger | {rec['entry_type']} (`{rec['entry_source']}`) | {rec['flow_type']} Flow |",
            f"| Re-entry | {rec['entry_mode']} | {rec['reentry_pattern']} |", "",
            rec["entry_note"], ""]
    if rec["salesforce_object"]:
        out += [f"Trigger object: `{rec['salesforce_object']}`.", ""]
    if rec["exit_criteria"]:
        out += ["**Exit criteria (carry across):** " + "; ".join(rec["exit_criteria"]),
                "MC Next evaluates exit criteria at entry and after each wait. Max 10 conditions.", ""]

    out += ["## Target flow", "", "```mermaid", mermaid(rec), "```", "",
            "Green = direct. Amber = adapt. Red = re-architect. Trailing JB spacer waits removed "
            f"({rec['dropped_steps']} dropped).", "",
            "## Elements in build order", "",
            "| # | MCE activity | MC Next element | Status | Config | Flags |", "|---|---|---|---|---|---|"]
    i = 0
    for n in rec["elements"]:
        if n["status"] == "drop":
            continue
        i += 1
        d = n["detail"]
        if n["type"] == "WAIT":
            cfg = wait_text(d) + (f" ({d.get('timeZone')})" if d.get("timeZone") else "")
        elif n["type"].startswith("EMAIL"):
            cfg = f"emailId {d.get('emailId')} · subject: {d.get('subject','')}"
        elif n["type"].startswith("SMS"):
            cfg = f"asset {d.get('assetId')} · from {d.get('from')} {d.get('country','')}" + (f" · blackout {d['blackout']}" if d.get("blackout") else "")
        elif n["type"] == "MULTICRITERIADECISION":
            cfg = "<br>".join(f"**{b['label']}** → {b['readable']}" for b in d["branches"])
        else:
            cfg = n["note"]
        out.append(f"| {i} | {n['type']} · {n['name']} | {n['element']} | {n['status']} | {cfg} | {', '.join(n['flags'])} |")
    out.append("")

    if rec["decisions"]:
        out += ["## Decision attributes required on the Data Graph", "",
                "Every attribute below must resolve from the Unified Individual Data Graph set in "
                "Setup > Marketing Cloud > Basic Personalization. Missing attributes block the Decision element.", ""]
        for a in deps["attributes"]:
            out.append(f"- `{a}`")
        out.append("")

    out += ["## Dependencies", "",
            f"- Emails (Content Builder / legacy IDs): {', '.join(map(str, deps['emails'])) or 'none'}. Rebuild via content migration; check AMPscript verdicts first.",
            f"- SMS assets: {', '.join(map(str, deps['sms_assets'])) or 'none'}. Senders: {', '.join(deps['sms_senders']) or 'none'}.",
            f"- Publication lists: {', '.join(map(str, deps['publication_lists'])) or 'none'}. Map to MC Next subscriptions before go-live (consent migration).",
            f"- Entry data: `{deps['entry_source']}`. Ingest to Data 360 and map to a DMO (see mce-to-data360-mapper).", ""]

    out += ["## Flags and required decisions", ""]
    if not f:
        out.append("None.")
    for k, v in sorted(f.items(), key=lambda kv: -kv[1]):
        note = RULES["flags"].get(k, "")
        if k == "list_operator" or k == "hardcoded_list":
            pass
        out.append(f"- **{k}** (×{v}): {note}")
    rand = [n for n in rec["elements"] if n["type"] in ("RANDOMSPLIT", "ABNTEST", "PATHOPTIMIZER")]
    if rand and edition == "growth":
        out.append("- **edition**: Path Experiment is Advanced only. On Growth, rebuild the split with a random-number field and a Decision.")
    out.append("")
    return "\n".join(out)


def chrome_prompt(rec, client):
    steps = []
    for n in rec["elements"]:
        if n["status"] == "drop":
            continue
        d = n["detail"]
        if n["type"] == "WAIT":
            if "spacer_wait" in n["flags"]:
                steps.append(f"Journey Builder used a {wait_text(d)} spacer here. Omit it unless the business confirms it is intentional.")
            else:
                steps.append(f"Add a **Wait for Amount of Time** element: {wait_text(d)}. Timezone {d.get('timeZone','org default')}.")
        elif n["type"].startswith("EMAIL"):
            steps.append(f"Add **Send Email Message** named \"{n['name']}\". Select the rebuilt email for MCE emailId {d.get('emailId')}. "
                         f"If it does not exist yet, add a placeholder and note it. Do not author content.")
        elif n["type"].startswith("SMS"):
            steps.append(f"Add **Send SMS Message** named \"{n['name']}\". Select the rebuilt SMS for MCE asset {d.get('assetId')}. "
                         f"Sender {d.get('from')} ({d.get('country','')}).")
        elif n["type"] == "MULTICRITERIADECISION":
            br = "; ".join(f"outcome \"{b['label']}\" when {b['readable']}" for b in d["branches"] if b["outcome"] != "remainder_path")
            dflt = next((b["label"] for b in d["branches"] if b["outcome"] == "remainder_path"), "Remainder")
            steps.append(f"Add a **Decision** named \"{n['name'] or 'Split'}\" with {br}; default outcome \"{dflt}\". "
                         "If any attribute is not selectable, STOP and list the missing attributes.")
        else:
            steps.append(f"Add **{n['element']}** for MCE {n['type']} \"{n['name']}\". Flag for manual build: {n['note']}")
    numbered = "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1))
    edges = "\n".join(f"- {e['from']} → {e['to']}" + (f" (outcome: {e['label']})" if e.get("label") else "") for e in rec["edges"])
    return f"""# Claude in Chrome build prompt: {rec['name']}

You are in the {client} Salesforce org, Marketing Cloud Next. Build one flow in Flow Builder. Do not activate it.

## Setup
1. Open the Marketing app > Flows. Create a new **{rec['flow_type']} Flow** named "{rec['name']} (MC Next)".
2. Entry: {rec['entry_note']}
   - Source: `{rec['entry_source']}`{(' on object ' + rec['salesforce_object']) if rec['salesforce_object'] else ''}.
   - If the segment or object is not available, STOP and report which one is missing.
3. Re-entry: {rec['reentry_pattern']}
{('4. Exit criteria: ' + '; '.join(rec['exit_criteria'])) if rec['exit_criteria'] else ''}

## Elements (connect in this order, branches per the edge list)
{numbered}

## Edge list from the source journey (JB keys)
{edges}

## Constraints
- Save as draft only. Never activate.
- Do not create or edit email/SMS content, segments or Data Graphs. Report gaps instead.
- Where a Decision outcome path in the source ends in a 1-minute wait, end the path instead.

## Validation before you finish
- Element count (excluding Start/End) = {rec['effective_steps']}.
- Decision count = {rec['decisions']}.
- Every Decision has a default outcome.
- Screenshot the canvas and list any element you could not configure, with the reason.
"""


def estate_md(summary, rows, client):
    live = [r for r in rows if r["disposition"] != "Retire"]
    fam = Counter(r["family"] for r in rows if r["disposition"] == "Consolidate" and not r.get("series"))
    lines = [f"# {client}: Journey Builder → MC Next Flow estate triage", "",
             f"As of {summary['as_of']}. Dormant = no contact processed in {summary['dormant_days']} days.", "",
             "## Headline", "",
             f"- Published journeys: **{summary['total']}**",
             f"- Live: **{summary['live']}**. Dormant: **{summary['dormant']}**.",
             f"- Disposition: " + ", ".join(f"{k} {v}" for k, v in summary["disposition"].items()),
             f"- Deep-translated: {summary['translated']}. Verdicts: " + (", ".join(f"{k} {v}" for k, v in sorted(summary['verdicts'].items())) or "n/a"), "",
             "## Target flow types (live journeys)", ""]
    for k, v in summary["flow_types"].items():
        lines.append(f"- {k}: {v}")
    lines += ["", "## Re-entry modes needing a guard pattern (live)", ""]
    for k, v in summary["entry_modes"].items():
        lines.append(f"- {k}: {v} → {RULES['entry_mode'].get(k, {}).get('status', 'adapt')}")
    lines += ["", "## Consolidation candidates", ""]
    for k, v in fam.most_common():
        if v > 1:
            lines.append(f"- {k}: {v} live journeys in one family. Merge into one flow.")
    if summary.get("series"):
        for k, v in summary["series"].items():
            lines.append(f"- {k}: {v} journeys share one template. Build once, parameterise by segment.")
    if summary.get("structural_groups"):
        lines += ["", "Structurally identical (after deep translation):"]
        for sig, names in summary["structural_groups"].items():
            lines.append(f"- `{sig}`: {', '.join(names)}")
    lines += ["", "## Systemic flags", ""]
    for k, v in Counter(summary["flags"]).most_common():
        lines.append(f"- **{k}** ×{v}: {RULES['flags'].get(k, '')}")
    lines += ["", "## Retire list", ""]
    for r in sorted(rows, key=lambda r: r["name"]):
        if r["disposition"] == "Retire":
            lines.append(f"- {r['name']} · {r.get('retire_reason','')}")
    lines += ["", "## Migrate list (live, not consolidated)", ""]
    for r in sorted(live, key=lambda r: r["name"]):
        if r["disposition"] == "Migrate":
            lines.append(f"- {r['name']} · {r['flow_type']} · {r['entry_mode']}" + (f" · verdict {r['verdict']}" if r.get("verdict") else ""))
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--client", required=True)
    ap.add_argument("--edition", choices=["growth", "advanced"], default="advanced")
    args = ap.parse_args()

    for d in ("specs", "prompts"):
        os.makedirs(os.path.join(args.out, d), exist_ok=True)
    summary = json.load(open(os.path.join(args.out, "summary.json")))
    rows = list(csv.DictReader(open(os.path.join(args.out, "register.csv"))))
    disp = {r["id"]: r["disposition"] for r in rows}
    twins = {r["id"]: r["structural_twins"] for r in rows}

    manifest = {"journeys": []}
    for f in sorted(glob.glob(os.path.join(args.out, "ir", "*.json"))):
        rec = json.load(open(f))
        rec["disposition"] = disp.get(rec["id"], "Migrate")
        rec["structural_twins"] = int(twins.get(rec["id"]) or 0)
        s = slug(rec["name"])
        open(os.path.join(args.out, "specs", s + ".md"), "w").write(spec_md(rec, args.client, args.edition))
        open(os.path.join(args.out, "prompts", s + ".md"), "w").write(chrome_prompt(rec, args.client))
    for r in rows:
        manifest["journeys"].append({
            "mce_id": r["id"], "name": r["name"], "disposition": r["disposition"],
            "verdict": r.get("verdict") or None, "target_flow_type": r["flow_type"],
            "family": r["family"], "status": "translated" if r.get("verdict") else "triaged",
            "depends_on": {"entry_source": r["entry_source"]},
        })
    json.dump(manifest, open(os.path.join(args.out, "manifest_fragment.json"), "w"), indent=2)
    open(os.path.join(args.out, "estate_summary.md"), "w").write(estate_md(summary, rows, args.client))
    print(f"Rendered {len(glob.glob(os.path.join(args.out, 'specs', '*.md')))} specs, estate summary, manifest fragment.")


if __name__ == "__main__":
    main()
