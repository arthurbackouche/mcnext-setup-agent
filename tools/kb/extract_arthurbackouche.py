import html, json, os, re, sys
from html.parser import HTMLParser

SRC, DST = sys.argv[1], sys.argv[2]
os.makedirs(DST, exist_ok=True)

class Body(HTMLParser):
    """Collect text inside the first element whose class contains a body marker."""
    MARKERS = ("betterdocs-entry-content", "elementor-widget-theme-post-content", "entry-content")
    BLOCK = {"p": "\n\n", "br": "\n", "li": "\n- ", "tr": "\n", "h1": "\n\n# ", "h2": "\n\n## ", "h3": "\n\n### ", "h4": "\n\n#### ", "td": " | ", "th": " | "}
    def __init__(s):
        super().__init__(); s.depth = 0; s.out = []; s.skip = 0
    def handle_starttag(s, tag, attrs):
        a = dict(attrs)
        if s.depth == 0:
            if any(m in (a.get("class") or "") for m in s.MARKERS) and tag in ("div", "article", "section"):
                s.depth = 1
            return
        if tag in ("script", "style", "svg", "noscript"): s.skip += 1
        if tag in ("div", "article", "section"): s.depth += 1
        if tag == "img" and a.get("alt"): s.out.append(f" [image: {a['alt']}] ")
        if tag in s.BLOCK: s.out.append(s.BLOCK[tag])
    def handle_endtag(s, tag):
        if s.depth == 0: return
        if tag in ("script", "style", "svg", "noscript") and s.skip: s.skip -= 1
        if tag in ("div", "article", "section"): s.depth -= 1
    def handle_data(s, d):
        if s.depth and not s.skip: s.out.append(d)

index = []
for fn in sorted(os.listdir(SRC)):
    raw = open(os.path.join(SRC, fn), encoding="utf-8", errors="ignore").read()
    title = re.search(r"<title>(.*?)</title>", raw, re.S)
    title = html.unescape(title.group(1)).split(" - ")[0].strip() if title else fn
    mod = re.search(r'"dateModified":"([^"]+)"', raw)
    p = Body(); p.feed(raw)
    text = re.sub(r"[ \t]+", " ", "".join(p.out))
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text).strip()
    parts = fn[:-5].split("__")
    url = "https://arthurbackouche.com/" + "/".join(parts) + "/"
    slug = parts[-1]
    section = "/".join(parts[1:-1])
    name = f"{section.replace('/', '__')}__{slug}.md" if section else f"{slug}.md"
    with open(os.path.join(DST, name), "w") as fh:
        fh.write(f"# {title}\n\nSource: {url}\nModified: {mod.group(1) if mod else 'unknown'}\nSection: {section}\n\n{text}\n")
    index.append({"file": name, "title": title, "url": url, "section": section, "words": len(text.split())})
json.dump(index, open(os.path.join(DST, "_index.json"), "w"), indent=1)
print(len(index), "files;", sum(i["words"] for i in index), "words; empty:", [i["file"] for i in index if i["words"] < 150])
