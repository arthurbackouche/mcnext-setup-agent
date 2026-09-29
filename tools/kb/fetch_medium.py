#!/usr/bin/env python3
"""Fetch setup-relevant Medium articles for the mcnext-setup knowledge base.

Input: an index JSON list of {"url", "title", "date"} (built with Chrome read_page after
scrolling the author's profile to the end; Medium's RSS and API do not give the full list).
Selects "Marketing Cloud Next" / "Data Cloud" titles plus any --extra numbers, and fetches
each through the r.jina.ai reader. Resumable; Cloudflare challenge pages count as failures.

Usage:
  python3 tools/kb/fetch_medium.py --index research/medium/medium_index.json \
      --out research/medium [--extra 28,143]
Outputs: <out>/raw/<num>_<slug>.md (git-ignored: third-party content), <out>/selection.json,
<out>/failed.json (retry these through Chrome get_page_text).
"""
import argparse, json, os, re, subprocess, time

ap = argparse.ArgumentParser()
ap.add_argument("--index", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--extra", default="", help="comma-separated article numbers to include")
ap.add_argument("--prefixes", default="marketing cloud next,data cloud")
a = ap.parse_args()

raw = os.path.join(a.out, "raw"); os.makedirs(raw, exist_ok=True)
extra = {int(x) for x in a.extra.split(",") if x.strip()}
prefixes = tuple(p.strip().lower() for p in a.prefixes.split(","))

def num(t):
    m = re.match(r"SFMC Tips #(\d+)", t)
    return int(m.group(1)) if m else None

def good(path):
    if not os.path.exists(path) or os.path.getsize(path) < 1500:
        return False
    head = open(path, encoding="utf-8", errors="ignore").read(800)
    return "Just a moment" not in head and "error 403" not in head

sel = []
for i in json.load(open(a.index)):
    n = num(i["title"])
    body = re.sub(r"^SFMC Tips #\d+\s*:\s*", "", i["title"]).lower()
    if body.startswith(prefixes) or n in extra:
        slug = i["url"].rstrip("/").split("/")[-1]
        sel.append({**i, "num": n, "file": f"{n if n else 'x'}_{slug}.md"})
json.dump(sel, open(os.path.join(a.out, "selection.json"), "w"), indent=1)
print("selected", len(sel), flush=True)

ok, failed = 0, []
for s in sel:
    path = os.path.join(raw, s["file"])
    if good(path):
        ok += 1
        continue
    code = "?"
    for attempt in range(3):
        r = subprocess.run(["curl", "-sL", "-m", "60", "-w", "%{http_code}", "-o", path,
                            "https://r.jina.ai/" + s["url"]], capture_output=True, text=True)
        code = r.stdout.strip()
        if code == "200" and good(path):
            ok += 1
            break
        time.sleep(10 * (attempt + 1))
    else:
        failed.append(s)
        print("FAIL", code, s["file"], flush=True)
        if os.path.exists(path):
            os.remove(path)
    time.sleep(3)
json.dump(failed, open(os.path.join(a.out, "failed.json"), "w"), indent=1)
print(f"done ok={ok} fail={len(failed)}", flush=True)
