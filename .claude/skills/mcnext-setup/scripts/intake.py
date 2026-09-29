#!/usr/bin/env python3
"""Setup intake: create, validate and summarise the answers collected before an MC Next setup.

  intake.py init  <engagement dir>   copy scaffold/setup_intake.template.json to out/setup/intake.json
  intake.py check <engagement dir>   validate; list missing or invalid answers; exit 1 if any
  intake.py plan  <engagement dir>   print the steps in scope and the steps skipped by the answers

All answers are collected from the user in one pass BEFORE any change is made in the org.
"""
import json, os, re, shutil, sys

HERE = os.path.dirname(os.path.realpath(__file__))
FW = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TEMPLATE = os.path.join(FW, "scaffold", "setup_intake.template.json")
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DOMAIN = re.compile(r"^(?!-)[a-z0-9-]+(\.[a-z0-9-]+)+$", re.I)

def path(eng):
    return os.path.join(eng, "out", "setup", "intake.json")

def placeholder(v):
    return isinstance(v, str) and (v.startswith("<") or " | " in v)

def check(d):
    errs = []
    def need(obj, key, label, pat=None):
        v = (obj or {}).get(key)
        if v in (None, "") or placeholder(v):
            errs.append(f"missing: {label}")
        elif pat and not pat.match(str(v)):
            errs.append(f"invalid: {label} = {v}")
    o = d.get("org", {})
    need(o, "my_domain", "org.my_domain")
    need(o, "sf_alias", "org.sf_alias")
    if o.get("org_type") not in ("sandbox", "demo_or_trial"):
        errs.append("invalid: org.org_type must be sandbox or demo_or_trial (production is not supported)")
    if o.get("edition") not in ("growth", "advanced"):
        errs.append("invalid: org.edition must be growth or advanced")
    need(d.get("setup_user"), "username", "setup_user.username")
    if not d.get("data_space"):
        errs.append("missing: data_space (usually 'default'; the choice is permanent)")
    for k in ("street", "city", "state", "postal_code", "country"):
        need(d.get("company"), k, f"company.{k}")
    sc = d.get("security_contact", {})
    need(sc, "name", "security_contact.name")
    need(sc, "email", "security_contact.email", EMAIL)
    need(sc, "phone", "security_contact.phone")
    sd = d.get("sending_domain") or {}
    if sd.get("root_domain") not in (None, ""):
        need(sd, "root_domain", "sending_domain.root_domain", DOMAIN)
        need(sd, "from_display_name", "sending_domain.from_display_name")
        need(sd, "from_username", "sending_domain.from_username")
    t = (d.get("test_send") or {}).get("recipient_email")
    if t not in (None, "") and (placeholder(t) or not EMAIL.match(t)):
        errs.append(f"invalid: test_send.recipient_email = {t}")
    return errs

def plan(d):
    skip = {}
    if not (d.get("mce") or {}).get("eid"):
        skip["S12"] = "no MCE tenant (mce.eid is null)"
    sd = d.get("sending_domain") or {}
    if not sd.get("root_domain"):
        skip["S13"] = "no sending domain provided"
    t = (d.get("test_send") or {}).get("recipient_email")
    if not t:
        skip["S22"] = "no test recipient: no consent seeding"
        skip["S23"] = "no test send requested"
    elif not sd.get("activate"):
        skip["S23"] = "test send needs an activated sending domain (sending_domain.activate is false)"
    opt = d.get("options") or {}
    if not opt.get("install_analytics", True):
        skip["S18"] = skip["S19"] = "analytics not requested"
    if not opt.get("contact_page_components", True):
        skip["S20"] = "record page components not requested"
    return skip

def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("init", "check", "plan"):
        sys.exit(__doc__)
    cmd, eng = sys.argv[1], os.path.abspath(os.path.expanduser(sys.argv[2]))
    p = path(eng)
    if cmd == "init":
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if os.path.exists(p):
            sys.exit(f"{p} already exists")
        shutil.copy(TEMPLATE, p)
        print(f"created {p}")
        return
    d = json.load(open(p))
    if cmd == "check":
        errs = check(d)
        print("\n".join(errs) or "intake complete")
        sys.exit(1 if errs else 0)
    for k, v in plan(d).items():
        print(f"skip {k}: {v}")
    sd = d.get("sending_domain") or {}
    if sd.get("root_domain"):
        print(f"sending domain: {sd.get('subdomain_prefix') or 'e'}.{sd['root_domain']} (activate: {bool(sd.get('activate'))})")
    print(f"data space: {d.get('data_space')} (permanent once selected)")

if __name__ == "__main__":
    main()
