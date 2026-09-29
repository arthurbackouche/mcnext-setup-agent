#!/usr/bin/env python3
"""Download arthurbackouche.com MC Next / Data 360 docs and extract them to markdown.

Reads the site's sitemap index, fetches every URL in docs-sitemap.xml plus selected blog posts,
then runs extract_arthurbackouche.py to keep only the article body.

Usage:
  python3 tools/kb/fetch_arthurbackouche.py --out research/arthurbackouche
Outputs: <out>/html/ (git-ignored), <out>/raw/*.md and raw/_index.json.
"""
import argparse, os, re, subprocess, sys, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--site", default="https://arthurbackouche.com")
ap.add_argument("--posts", default="data-graphs,orchestrate", help="regex fragments of blog posts to include")
a = ap.parse_args()

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "ignore")

def locs(xml):
    return [u for u in re.findall(r"<loc>([^<]+)</loc>", xml) if not re.search(r"\.(png|jpe?g|webp|gif)$", u)]

urls = [u for u in locs(get(f"{a.site}/docs-sitemap.xml")) if not u.rstrip("/").endswith("/docs")]
posts = re.compile("|".join(x.strip() for x in a.posts.split(",") if x.strip()))
urls += [u for u in locs(get(f"{a.site}/post-sitemap.xml")) if posts.search(u)]

html = os.path.join(a.out, "html"); os.makedirs(html, exist_ok=True)
for u in urls:
    name = re.sub(r"^https?://[^/]+/", "", u).rstrip("/").replace("/", "__") + ".html"
    path = os.path.join(html, name)
    if not os.path.exists(path):
        open(path, "w").write(get(u))
print(f"fetched {len(urls)} pages")
here = os.path.dirname(os.path.abspath(__file__))
sys.exit(subprocess.call([sys.executable, os.path.join(here, "extract_arthurbackouche.py"), html, os.path.join(a.out, "raw")]))
