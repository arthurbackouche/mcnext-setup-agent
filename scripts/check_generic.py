#!/usr/bin/env python3
"""Fail if the framework contains instance-specific data.

Scans the framework folder (agents, skills, memory, scripts, scaffold, docs) for:
- Salesforce sandbox or My Domain hosts, MCE tenant hosts, connected-app client ids,
  Salesforce record ids, phone numbers, email addresses (except placeholders);
- the client name, aliases and EID of every engagement passed with --engagement,
  and every term in an optional denylist file kept OUTSIDE the framework.

Usage: python3 scripts/check_generic.py [--engagement <dir> ...] [--denylist ~/.mcnext-denylist]
Exit 1 on any finding.
"""
import argparse, json, os, re, sys

FW = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# Git-ignored folders (engagement data, raw third-party research) are not published, so not scanned.
SKIP_DIRS = {"out", "approvals", "templates", ".git", "__pycache__", "node_modules", "raw", "html"}
SKIP_FILES = {".mcp.json", "manifest.json", "STATUS.md", "settings.local.json", "check_generic.py"}
PATTERNS = {
    "sandbox/mydomain host": r"\b(?!example--|mydomain--|<mydomain>--)[a-z0-9-]+--[a-z0-9]+\.sandbox\.(my\.salesforce|lightning\.force|my\.salesforce-setup)\.com",
    "my domain host": r"(?<![<>\w-])(?!company\.|example\.|yourdomain\.|mydomain\.|sandbox\.)[a-z0-9-]{3,}\.my\.salesforce\.com",
    "MCE tenant host": r"\bmc[a-z0-9]{20,}(-[a-z0-9]+)?\.(login\.)?(exacttarget|rest\.marketingcloudapis|auth\.marketingcloudapis)\.com",
    "MCE MCP tenant url": r"svc\.sfdcfc\.net/t/[a-z0-9-]+",
    "connected app client id": r"\b3MVG[A-Za-z0-9._]{20,}",
    "salesforce record id": r"\b0[0-9A-Za-z]{2}(?=[0-9A-Za-z]*[0-9])(?=[0-9A-Za-z]*[A-Z])[0-9A-Za-z]{12}(?:[0-9A-Za-z]{3})?\b",
    "phone number": r"\b(\+?61|\+?64|\+?1)?4\d{8}\b",
    "email address": r"\b[\w.+-]+@(?![\w.-]*(example\.com|anthropic\.com)\b)[\w-]+\.[\w.]+\b",
}

ap = argparse.ArgumentParser()
ap.add_argument("--engagement", action="append", default=[])
ap.add_argument("--denylist", default=os.path.expanduser("~/.mcnext-denylist"))
a = ap.parse_args()

terms = set()
for e in a.engagement:
    m = json.load(open(os.path.join(os.path.expanduser(e), "manifest.json")))
    o = m.get("orgs", {})
    terms |= {m.get("client", ""), o.get("mce_eid", ""), o.get("sandbox_alias", "")} | set(o.get("production_aliases", []))
if os.path.exists(a.denylist):
    terms |= {l.strip() for l in open(a.denylist) if l.strip() and not l.startswith("#")}
PLACEHOLDERS = {"none", "unknown", "n/a", "tbd", "no-prod", "placeholder"}
terms = {t for t in terms if len(t) >= 3 and t.lower() not in PLACEHOLDERS}
rx = {k: re.compile(v, re.I) for k, v in PATTERNS.items()}
rx.update({f"term '{t}'": re.compile(r"(?<![A-Za-z0-9])" + re.escape(t) + r"(?![A-Za-z0-9])", re.I) for t in terms})

hits = 0
for d, dirs, files in os.walk(FW):
    dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
    for f in files:
        if f in SKIP_FILES or f.endswith((".png", ".jpg", ".gif", ".pdf", ".xlsx", ".docx")):
            continue
        p = os.path.join(d, f)
        try:
            lines = open(p, encoding="utf-8").read().splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(lines, 1):
            for name, r in rx.items():
                if r.search(line):
                    hits += 1
                    print(f"{os.path.relpath(p, FW)}:{i}: {name}: {line.strip()[:120]}")
print(f"{hits} finding(s)")
sys.exit(1 if hits else 0)
