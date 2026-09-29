#!/usr/bin/env python3
"""Parse MCE asset JSON pages, extract AMPscript function usage, classify emails A-F.

Usage:
  python3 parse_ampscript.py --workdir out/content/assets --out out/content
       [--extra extra1.json ...] [--report-artifacts]

Inputs: the tool-result JSON files saved by sfmc_get_content_assets (copied into --workdir),
plus optional --extra JSON files mapping {"Email Name": ["Func1", ...]} for pages that were
captured inline rather than stored.

Outputs in --out: register.csv, verdicts.json, census.json
Update SUPPORTED_* sets each MC Next release (see references/mcnext-functions.md).
"""
import json, re, glob, csv, argparse, os
from collections import Counter

SUPPORTED_CONFIRMED = {"add","buildrowsetfromjson","concat","dateadd","datediff","dateparse",
 "divide","empty","field","format","formatcurrency","formatdate","formatnumber","iif",
 "indexof","isnull","length","lowercase","mod","multiply","now","output","outputline",
 "propercase","random","replace","replacelist","row","rowcount","stringtodate","subtract",
 "substring","trim","uppercase","v"}
SUPPORTED_UNTESTED = {"contentblockbyid","contentblockbykey","contentblockbyname","lookup",
 "retrievesalesforceobjects","raiseerror"}
NATIVE_REPLACE = {"attributevalue","redirectto","cloudpagesurl","beginimpressionregion",
 "endimpressionregion","regexmatch","systemdatetolocaldate","urlencode",
 "getsocialpublishurlbyname","treatascontent","buildrowsetfromstring"}
DATA_PREP = {"lookuprows","lookuporderedrows","lookuprowscs"}
REDESIGN = {"insertde","upsertde","updatede","deletede","httppost","httppost2","httpget"}
KEYWORDS = {"set","var","if","then","else","elseif","endif","for","to","next","do","and",
 "or","not","true","false","downto"}
# Tenant-specific text artifacts that match the function regex; extend per tenant.
ARTIFACTS = set()

FUNC_RE = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)\s*\(')

def extract_amp(text):
    funcs = Counter()
    for block in re.findall(r'%%\[(.*?)\]%%', text, re.S):
        for f in FUNC_RE.findall(block):
            if f.lower() not in KEYWORDS: funcs[f] += 1
    for expr in re.findall(r'%%=(.*?)=%%', text, re.S):
        for f in FUNC_RE.findall(expr):
            if f.lower() not in KEYWORDS: funcs[f] += 1
    return funcs

def classify(funcs):
    """Return (letter, blockers) using precedence F > E > D > C > B > A."""
    fl = {f.lower() for f in funcs} - ARTIFACTS
    if not fl: return "A", []
    unknown = sorted(f for f in fl if f not in SUPPORTED_CONFIRMED | SUPPORTED_UNTESTED
                     | NATIVE_REPLACE | DATA_PREP | REDESIGN)
    if fl & REDESIGN or unknown: return "F", sorted(fl & REDESIGN) + unknown
    if fl & DATA_PREP: return "E", sorted(fl & DATA_PREP)
    if fl & NATIVE_REPLACE: return "D", sorted(fl & NATIVE_REPLACE)
    if fl & SUPPORTED_UNTESTED: return "C", sorted(fl & SUPPORTED_UNTESTED)
    return "B", []

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--extra", nargs="*", default=[])
    ap.add_argument("--report-artifacts", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    per_asset, asset_type = {}, {}
    for fp in sorted(glob.glob(os.path.join(args.workdir, "*.json"))):
        try:
            raw = json.load(open(fp))
            raw = raw[0].get("text","") if isinstance(raw, list) else ""
        except Exception: continue
        i = raw.find("{")
        if i < 0: continue
        try: d = json.loads(raw[i:])
        except Exception: continue
        for it in d.get("items", []):
            name = it.get("name","?")
            blob = json.dumps(it.get("views",{})) + json.dumps(it.get("content","") or "")
            blob = blob.encode().decode("unicode_escape", errors="ignore")
            fc = extract_amp(blob)
            per_asset.setdefault(name, Counter()).update(fc)
            asset_type[name] = it.get("assetType",{}).get("name","?")
    for efp in args.extra:
        for name, fl in json.load(open(efp)).items():
            c = per_asset.setdefault(name, Counter())
            for f in fl: c[f] += 1
            asset_type.setdefault(name, "htmlemail")

    census = Counter()
    for c in per_asset.values(): census.update({k.lower(): v for k, v in c.items()})
    if args.report_artifacts:
        print("Review for artifacts (lowercase function -> count); add non-functions to ARTIFACTS:")
        for f, n in census.most_common(): print(f"  {f:36s} {n}")

    rows, verdicts, vcount = [], {}, Counter()
    for name in sorted(per_asset):
        letter, blockers = classify(per_asset[name])
        verdicts[name] = [letter, blockers, asset_type.get(name,"?")]
        vcount[letter] += 1
        native = ", ".join(b for b in blockers if b in NATIVE_REPLACE | SUPPORTED_UNTESTED)
        redesign = ", ".join(b for b in blockers if b not in NATIVE_REPLACE | SUPPORTED_UNTESTED)
        rows.append([name, asset_type.get(name,"?"), letter, native, redesign])

    with open(os.path.join(args.out, "register.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Email/Template","Type","Verdict","Validate or replace with native","Redesign"])
        w.writerows(rows)
    json.dump(verdicts, open(os.path.join(args.out, "verdicts.json"), "w"), indent=1)
    json.dump(dict(census.most_common()), open(os.path.join(args.out, "census.json"), "w"), indent=1)
    print("assets:", len(per_asset), "| verdicts:", dict(sorted(vcount.items())))

if __name__ == "__main__":
    main()
