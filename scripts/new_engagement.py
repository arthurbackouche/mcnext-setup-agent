#!/usr/bin/env python3
"""Create a client engagement folder that uses this framework.

The framework (this folder) holds only client-agnostic agents, skills, scripts and memory.
Each engagement folder holds everything instance-specific: manifest.json, STATUS.md, .mcp.json,
out/, templates/, approvals/. The shared parts are symlinked, so fixes to the framework reach
every engagement.

Usage:
  python3 scripts/new_engagement.py <slug> --client "Acme Retail" --sandbox-alias acme-uat \
      --prod-alias acme-prod --mce-eid 12345678 --edition advanced \
      [--root ~/Documents/Claude/mcnext-engagements]

Then: cd <root>/<slug>, fill .mcp.json, run `claude`.
"""
import argparse, datetime as dt, json, os, sys

FW = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
LINKS = [".claude", "scripts", "schema", "scaffold", "CLAUDE.md", "README.md"]

ap = argparse.ArgumentParser()
ap.add_argument("slug")
ap.add_argument("--client", required=True)
ap.add_argument("--sandbox-alias", required=True)
ap.add_argument("--prod-alias", required=True)
ap.add_argument("--mce-eid", required=True)
ap.add_argument("--edition", choices=["growth", "advanced"], required=True)
ap.add_argument("--root", default=os.path.expanduser("~/Documents/Claude/mcnext-engagements"))
a = ap.parse_args()

dest = os.path.join(os.path.expanduser(a.root), a.slug)
if os.path.realpath(dest).startswith(os.path.realpath(FW) + os.sep):
    sys.exit("Engagement folders must live outside the framework folder.")
if os.path.exists(dest):
    sys.exit(f"{dest} already exists.")
os.makedirs(dest)

vals = {"{{CLIENT}}": a.client, "{{EDITION}}": a.edition, "{{SANDBOX_ALIAS}}": a.sandbox_alias,
        "{{PROD_ALIAS}}": a.prod_alias, "{{MCE_EID}}": a.mce_eid, "{{DATE}}": dt.date.today().isoformat()}

def render(src, dst):
    t = open(os.path.join(FW, "scaffold", src)).read()
    for k, v in vals.items():
        t = t.replace(k, v)
    open(os.path.join(dest, dst), "w").write(t)

for name in LINKS:
    os.symlink(os.path.join(FW, name), os.path.join(dest, name))
render("manifest.template.json", "manifest.json")
render("STATUS.template.md", "STATUS.md")
render("mcp.json.example", ".mcp.json")
json.loads(open(os.path.join(dest, "manifest.json")).read())
for d in ("out/logs", "out/setup", f"templates/{a.sandbox_alias}", "approvals"):
    os.makedirs(os.path.join(dest, d), exist_ok=True)
open(os.path.join(dest, ".gitignore"), "w").write("approvals/\nout/**/raw/\n.sf/\n.sfdx/\n*.log\n")

print(f"Engagement ready: {dest}")
print("Next: fill .mcp.json ({{MCE_MCP_URL}}, {{CONNECTED_APP_CLIENT_ID}}),")
print(f"      sf org login web -a {a.sandbox_alias} -r https://test.salesforce.com,")
print(f"      cd {dest} && claude")
