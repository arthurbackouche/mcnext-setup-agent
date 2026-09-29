#!/usr/bin/env python3
"""QA the rendered outputs. Exit 1 on any failure.  Usage: qa_outputs.py --out <dir>"""
import argparse, glob, json, os, re, sys

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:80] or "journey"

def check_mermaid(md, name):
    errs = []
    for block in re.findall(r"```mermaid\n(.*?)```", md, re.S):
        defined = set(re.findall(r"^\s*(\w+)[\[\(\{]", block, re.M)) | {"END", "START"}
        for a, b in re.findall(r"^\s*(\w+)\s*-->(?:\|[^|]*\|)?\s*(\w+)", block, re.M):
            for n in (a, b):
                if n not in defined:
                    errs.append(f"{name}: mermaid edge references undefined node {n}")
        for lab in re.findall(r'\["([^"]*)"\]|\{\{"([^"]*)"\}\}', block):
            txt = "".join(lab)
            if re.search(r'["\[\]{}]', txt):
                errs.append(f"{name}: unsafe characters in mermaid label '{txt}'")
    return errs

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
    errs, n = [], 0
    for f in glob.glob(os.path.join(a.out, "ir", "*.json")):
        rec = json.load(open(f)); s = slug(rec["name"]); n += 1
        spec = open(os.path.join(a.out, "specs", s + ".md")).read()
        prompt = open(os.path.join(a.out, "prompts", s + ".md")).read()
        eff = [e for e in rec["elements"] if e["status"] != "drop"]
        m = re.search(r"Element count \(excluding Start/End\) = (\d+)", prompt)
        if not m or int(m.group(1)) != len(eff):
            errs.append(f"{s}: prompt element count mismatch")
        numbered = len(re.findall(r"^\d+\. ", prompt.split("## Elements")[1].split("## Edge list")[0], re.M))
        if numbered != len(eff):
            errs.append(f"{s}: {numbered} numbered steps vs {len(eff)} elements")
        for d in [e for e in eff if e["type"] == "MULTICRITERIADECISION"]:
            if not any(b["outcome"] == "remainder_path" for b in d["detail"]["branches"]):
                errs.append(f"{s}: decision {d['key']} has no default outcome")
        if rec.get("orphans"):
            errs.append(f"{s}: WARNING orphans {rec['orphans']} (not an error, mention in summary)")
        errs += check_mermaid(spec, s)
    hard = [e for e in errs if "WARNING" not in e]
    print(f"QA checked {n} journeys. {len(hard)} errors, {len(errs) - len(hard)} warnings.")
    for e in errs:
        print(" -", e)
    sys.exit(1 if hard else 0)

if __name__ == "__main__":
    main()
