#!/usr/bin/env python3
"""
Generate Flow metadata (.flow-meta.xml) from a translated journey IR.

Template-driven. Element XML for MC Next marketing elements is NOT hand-written here: it is captured
from a flow built once in the org UI (see references/deploy_bootstrap.md) and stored in --templates.
This follows the empirical rule: build one in the UI, retrieve it, use it as the template.

Required template files (tokens in {{DOUBLE_BRACES}}):
  header.xml        whole <Flow> document with {{API_NAME}} {{LABEL}} {{DESCRIPTION}} {{START_TARGET}} {{ELEMENTS}}
  wait.xml          {{NAME}} {{LABEL}} {{X}} {{Y}} {{DURATION}} {{UNIT}} {{NEXT}}
  email.xml         {{NAME}} {{LABEL}} {{X}} {{Y}} {{EMAIL_REF}} {{NEXT}}
  sms.xml           {{NAME}} {{LABEL}} {{X}} {{Y}} {{SMS_REF}} {{NEXT}}
  decision.xml      {{NAME}} {{LABEL}} {{X}} {{Y}} {{RULES}} {{DEFAULT_NEXT}} {{DEFAULT_LABEL}}
  rule.xml          {{NAME}} {{LABEL}} {{LOGIC}} {{CONDITIONS}} {{NEXT}}
  condition.xml     {{FIELD_REF}} {{OPERATOR}} {{VALUE_XML}}
  connector.xml     {{TARGET}}   (bare <targetReference>; the builder wraps it in connector/defaultConnector
                    and omits it at path ends)

--map JSON resolves MCE references to MC Next ones:
  {"emails": {"40002": "<MC Next email ref>"}, "sms": {"50002": "<ref>"},
   "attributes": {"DEAudience-2f6e...Plan": "<Data Graph field path>", "Store_Customer_Master.ItemID": "<path>"},
   "units": {"MINUTES": "Minutes", "DAYS": "Days", "WEEKS": "Weeks"}}

Unresolved references block generation unless --allow-placeholders (then they are written as
UNRESOLVED__<ref> and listed in the build report, so deploy fails loudly rather than silently).
"""
import argparse, json, os, re, sys, html

OPS = {  # JB operator -> (Flow operator, value kind)
    "Equal": ("EqualTo", "str"), "NotEqual": ("NotEqualTo", "str"), "Is": ("EqualTo", "bool"),
    "IsNull": ("IsNull", "true"), "IsNotNull": ("IsNull", "false"),
    "GreaterThan": ("GreaterThan", "num"), "LessThan": ("LessThan", "num"),
    "GreaterThanOrEqual": ("GreaterThanOrEqualTo", "num"), "LessThanOrEqual": ("LessThanOrEqualTo", "num"),
    "Contains": ("Contains", "str"), "ExistsInString": ("Contains", "str"),
    "BeginsWith": ("StartsWith", "str"), "EndsWith": ("EndsWith", "str"),
    "ExistsInWholeWord": ("EqualTo", "list"),  # expanded into an OR group
}

def api(s, prefix="E"):
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    if not s or not s[0].isalpha():
        s = prefix + "_" + s
    return s[:80]

def fill(tpl, **kw):
    out = tpl
    for k, v in kw.items():
        out = out.replace("{{" + k + "}}", str(v))
    left = re.findall(r"\{\{[A-Z_]+\}\}", out)
    if left:
        raise ValueError(f"unfilled tokens {set(left)}")
    return out

class Builder:
    def __init__(self, tdir, mapping, allow_placeholders, keep_spacers):
        self.t = {n: open(os.path.join(tdir, n + ".xml")).read() for n in
                  ("header", "wait", "email", "sms", "decision", "rule", "condition", "connector")}
        self.m = mapping
        self.allow = allow_placeholders
        self.keep_spacers = keep_spacers
        self.unresolved = []

    def ref(self, kind, key):
        v = self.m.get(kind, {}).get(str(key))
        if v:
            return v
        self.unresolved.append(f"{kind}:{key}")
        return f"UNRESOLVED__{kind}_{key}"

    def conn(self, target, wrap="connector"):
        return f"<{wrap}>" + fill(self.t["connector"], TARGET=target) + f"</{wrap}>" if target else ""

    def value_xml(self, kind, v):
        if kind == "bool":
            return f"<booleanValue>{'true' if str(v).lower() == 'true' else 'false'}</booleanValue>"
        if kind in ("true", "false"):
            return f"<booleanValue>{kind}</booleanValue>"
        if kind == "num":
            return f"<numberValue>{html.escape(str(v))}</numberValue>"
        return f"<stringValue>{html.escape(str(v))}</stringValue>"

    def rule_conditions(self, conds):
        parts, logic, i = [], [], 0
        for c in conds:
            if "field" not in c:
                raise ValueError(f"unparsed condition {c}")
            op, kind = OPS.get(c["operator"], (None, None))
            if not op:
                raise ValueError(f"no operator mapping for {c['operator']}")
            field = self.ref("attributes", f"{c['source']}.{c['field']}")
            if "reference_join" in c["flags"]:
                # cross-object compare: right side is another field, never a literal
                right = self.ref("attributes", c["ref_target"])
                i += 1
                parts.append(fill(self.t["condition"], FIELD_REF=field, OPERATOR=op,
                                  VALUE_XML=f"<elementReference>{right}</elementReference>"))
                logic.append(str(i))
            elif kind == "list":
                grp = []
                for v in [x.strip() for x in c["value"].split(",") if x.strip()]:
                    i += 1
                    parts.append(fill(self.t["condition"], FIELD_REF=field, OPERATOR=op, VALUE_XML=self.value_xml("str", v)))
                    grp.append(str(i))
                logic.append("(" + " OR ".join(grp) + ")")
            else:
                i += 1
                parts.append(fill(self.t["condition"], FIELD_REF=field, OPERATOR=op, VALUE_XML=self.value_xml(kind, c["value"])))
                logic.append(str(i))
        expr = " AND ".join(logic)
        return "".join(parts), ("and" if re.fullmatch(r"\d+( AND \d+)*", expr) else expr)

    def build(self, rec, label_suffix=" (MC Next)"):
        elems = {e["key"]: e for e in rec["elements"]}
        # skipped = dropped terminals + spacer waits; resolve connectors through them
        skip = {k for k, e in elems.items() if e["status"] == "drop" or ("spacer_wait" in e["flags"] and not self.keep_spacers)}
        nxt = {}
        for e in rec["edges"]:
            nxt.setdefault(e["from"], []).append(e)

        def resolve(target, seen=()):
            while target in skip:
                outs = nxt.get(target, [])
                if not outs or target in seen:
                    return None
                seen = seen + (target,)
                target = outs[0]["to"]
            return target

        names = {k: api(k) for k in elems}
        xml, col = [], {}
        y = 0
        for e in rec["elements"]:
            if e["key"] in skip:
                continue
            y += 1
            X, Y = 176 + 240 * min(e.get("depth", 0), 8), 120 * y
            d, name = e["detail"], names[e["key"]]
            single_next = resolve(nxt[e["key"]][0]["to"]) if e["key"] in nxt and e["type"] != "MULTICRITERIADECISION" else None
            NEXT = self.conn(names[single_next]) if single_next else ""
            label = html.escape((e["name"] or e["type"])[:80])
            if e["type"] == "WAIT":
                unit = self.m.get("units", {}).get(str(d.get("waitUnit")).upper(), d.get("waitUnit"))
                xml.append(fill(self.t["wait"], NAME=name, LABEL=label, X=X, Y=Y, DURATION=d.get("waitDuration", ""), UNIT=unit, NEXT=NEXT))
            elif e["type"].startswith("EMAIL"):
                xml.append(fill(self.t["email"], NAME=name, LABEL=label, X=X, Y=Y, EMAIL_REF=self.ref("emails", d.get("emailId")), NEXT=NEXT))
            elif e["type"].startswith("SMS"):
                xml.append(fill(self.t["sms"], NAME=name, LABEL=label, X=X, Y=Y, SMS_REF=self.ref("sms", d.get("assetId")), NEXT=NEXT))
            elif e["type"] == "MULTICRITERIADECISION":
                rules, dflt_next, dflt_label = [], "", "Default"
                for b in d["branches"]:
                    tgt = resolve(b["next"]) if b.get("next") else None
                    if b["outcome"] == "remainder_path":
                        dflt_next, dflt_label = (self.conn(names[tgt], "defaultConnector") if tgt else ""), html.escape(b["label"])
                        continue
                    conds, logic = self.rule_conditions(b["conditions"])
                    rules.append(fill(self.t["rule"], NAME=api(f"{name}_{b['label']}"), LABEL=html.escape(b["label"]),
                                      LOGIC=logic, CONDITIONS=conds, NEXT=self.conn(names[tgt]) if tgt else ""))
                xml.append(fill(self.t["decision"], NAME=name, LABEL=label, X=X, Y=Y, RULES="".join(rules),
                                DEFAULT_NEXT=dflt_next, DEFAULT_LABEL=dflt_label))
            else:
                raise ValueError(f"{e['type']} ({e['key']}) has no template. It is a re-architect item; build manually.")
        start = resolve(rec["roots"][0])
        api_name = api(rec["name"] + "_MCNext", "Flow")
        doc = fill(self.t["header"], API_NAME=api_name, LABEL=html.escape(rec["name"] + label_suffix),
                   DESCRIPTION=html.escape(f"Migrated from MCE journey {rec['id']} v{rec['version']}. Generated by journey-to-flow-translator."),
                   START_TARGET=names[start], ELEMENTS="\n".join(xml))
        return api_name, doc

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ir", required=True, nargs="+")
    ap.add_argument("--templates", required=True)
    ap.add_argument("--map", required=True)
    ap.add_argument("--project", required=True, help="SFDX project dir; writes force-app/main/default/flows/")
    ap.add_argument("--allow-placeholders", action="store_true")
    ap.add_argument("--keep-spacers", action="store_true")
    a = ap.parse_args()

    mapping = json.load(open(a.map))
    fdir = os.path.join(a.project, "force-app", "main", "default", "flows")
    os.makedirs(fdir, exist_ok=True)
    report, blocked = [], False
    for f in a.ir:
        rec = json.load(open(f))
        b = Builder(a.templates, mapping, a.allow_placeholders, a.keep_spacers)
        try:
            name, doc = b.build(rec)
        except ValueError as ex:
            report.append({"journey": rec["name"], "status": "blocked", "reason": str(ex)}); blocked = True; continue
        if b.unresolved and not a.allow_placeholders:
            report.append({"journey": rec["name"], "status": "blocked", "unresolved": sorted(set(b.unresolved))}); blocked = True; continue
        open(os.path.join(fdir, name + ".flow-meta.xml"), "w").write(doc)
        report.append({"journey": rec["name"], "flow": name, "status": "generated",
                       "unresolved": sorted(set(b.unresolved)), "source_id": rec["id"]})
    json.dump(report, open(os.path.join(a.project, "build_report.json"), "w"), indent=2)
    print(json.dumps(report, indent=2))
    sys.exit(2 if blocked else 0)

if __name__ == "__main__":
    main()
