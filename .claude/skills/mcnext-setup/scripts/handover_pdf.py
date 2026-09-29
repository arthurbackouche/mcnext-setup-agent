#!/usr/bin/env python3
"""Generate the MC Next setup handover PDF for an engagement.

  handover_pdf.py <engagement dir> [--out <file.pdf>]

Reads (all inside the engagement folder):
  manifest.json            client, org aliases, setup verdict
  out/setup/steps.json     status and evidence per step (S1-S23)
  out/setup/intake.json    answers collected before the setup (optional)
  out/setup/dns_records.md DNS table for the sending domain (optional)
Writes out/setup/<Client>_MC_Next_Setup_Handover.pdf by default. Needs reportlab (pip install reportlab).
"""
import argparse, datetime as dt, json, os, re, sys
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

STEPS = [
    ("S1", "Org reachable and identified"), ("S2", "MC Next and Data 360 licences"),
    ("S5", "Permission sets exist"), ("S6", "Permission sets and licences assigned to the setup user"),
    ("S3", "Data 360 enabled"), ("S4", "Salesforce CRM connector streams"),
    ("S21", "Custom-object DLO to DMO mapping"), ("S7", "Basic Settings and Enable Marketing Cloud"),
    ("S15", "Data protection details"), ("S9", "Data space selected"), ("S8", "Marketing data kits"),
    ("S10", "Identity resolution (Unified Individual)"), ("S12", "Marketing Cloud Engagement connector"),
    ("S11", "Data Graph selected for personalisation"), ("S13", "Authenticated sending domain"),
    ("S16", "Set Up Email: address, consent validation, subscriptions"), ("S22", "Consent for test contacts"),
    ("S17", "Einstein features"), ("S18", "Analytics packages"), ("S19", "Analytics access"),
    ("S20", "Record page components"), ("S14", "Flow types available"), ("S23", "First test send"),
]
FEATURES = {"metrics_guard": "Metrics Guard", "send_time_optimization": "Send Time Optimization",
            "engagement_frequency": "Engagement Frequency", "engagement_scoring": "Engagement Scoring"}
STATUS_COLOUR = {"done": "#1b7f3b", "skipped": "#6b7280", "running": "#b45309", "handback": "#b91c1c",
                 "failed": "#b91c1c", "pending": "#b45309", "unknown": "#b45309"}
VERIFY = [
    ("Licences", "SELECT MasterLabel, UsedLicenses, TotalLicenses FROM PermissionSetLicense"),
    ("Admin permission sets", "SELECT PermissionSet.Name FROM PermissionSetAssignment WHERE Assignee.Username = '<setup user>'"),
    ("Data space", "SELECT Name FROM DataSpace"),
    ("Data streams", "SELECT Name FROM DataStream ORDER BY Name"),
    ("Marketing Cloud enabled", "SELECT Name FROM CommSubscription"),
    ("Unified profiles", "SELECT COUNT() FROM UnifiedIndividual__dlm (name may carry a ruleset suffix)"),
    ("Company address", "SELECT Street, City, State, PostalCode, Country FROM Organization"),
]

def load(p, default=None):
    try:
        return json.load(open(p))
    except Exception:
        return default

def clip(s, n=260):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    return s if len(s) <= n else s[: n - 1] + "…"

def clean(ev):
    """Fallback when a step has no client-facing `summary`: drop internal run chatter."""
    s = re.sub(r"\s+", " ", str(ev or "")).strip()
    s = re.sub(r"^(?:(?:RETRACTED|CORRECTED|CORRECTION)[^.:]*[.:]\s*|Run \d+[^:]*:\s*)+", "", s, flags=re.I)
    return s

def dns_rows(md_path):
    rows = []
    if not os.path.exists(md_path):
        return rows
    for line in open(md_path, encoding="utf-8"):
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        types = [c for c in cells if c in ("CNAME", "TXT", "MX")]
        if line.startswith("|") and types and len(cells) >= 4:
            i = cells.index(types[0])
            rows.append([cells[i], cells[i + 1], cells[i + 2]])
    return rows

def build(eng, out):
    m = load(os.path.join(eng, "manifest.json"), {})
    steps = load(os.path.join(eng, "out", "setup", "steps.json"), {})
    intake = load(os.path.join(eng, "out", "setup", "intake.json"), {}) or {}
    dns = dns_rows(os.path.join(eng, "out", "setup", "dns_records.md"))
    client = m.get("client", "Client")
    orgs = m.get("orgs", {})
    verdict = (m.get("setup") or {}).get("verdict", "UNKNOWN")
    my_domain = (intake.get("org") or {}).get("my_domain") or orgs.get("sandbox_alias", "")

    ss = getSampleStyleSheet()
    body = ParagraphStyle("b", parent=ss["BodyText"], fontName="Helvetica", fontSize=9.5, leading=13)
    small = ParagraphStyle("s", parent=body, fontSize=8, leading=10.5)
    h1 = ParagraphStyle("h1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=20, spaceAfter=8)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=13, spaceBefore=10, spaceAfter=6)
    P = lambda t, st=body: Paragraph(escape(str(t)), st)

    def table(rows, widths, header=True, zebra=True):
        t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
        style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d1d5db")),
                 ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]
        if header:
            style += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                      ("TEXTCOLOR", (0, 0), (-1, 0), colors.white)]
        if zebra:
            style += [("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")])]
        t.setStyle(TableStyle(style))
        return t
    hdr = lambda *cols: [Paragraph(f"<b>{escape(c)}</b>", ParagraphStyle("hd", parent=small, textColor=colors.white)) for c in cols]

    counts = {}
    for sid, _ in STEPS:
        st = (steps.get(sid) or {}).get("status", "unknown")
        counts[st] = counts.get(st, 0) + 1
    story = [P("Marketing Cloud Next setup handover", h1),
             P(f"{client} · org {my_domain} · {dt.date.today().isoformat()}"), Spacer(1, 6),
             table([[P("Setup verdict"), Paragraph(f"<b>{escape(verdict)}</b>", body)],
                    [P("Steps"), P(", ".join(f"{v} {k}" for k, v in sorted(counts.items())))],
                    [P("Salesforce CLI alias"), P(orgs.get("sandbox_alias", ""))],
                    [P("Edition"), P(m.get("edition", ""))]], [45 * mm, 125 * mm], header=False),
             Spacer(1, 8),
             P("This document records what was configured, how each step was verified, what was skipped and why, "
               "and what the customer still needs to do. Verification uses the org's own data (SOQL through the "
               "Salesforce CLI, or the Setup pages), never a cached connector.")]

    story += [P("1. Setup steps", h2)]
    rows = [hdr("Step", "Item", "Status", "Evidence")]
    for sid, name in STEPS:
        s = steps.get(sid) or {}
        st = s.get("status", "unknown")
        rows.append([P(sid, small), P(name, small),
                     Paragraph(f'<font color="{STATUS_COLOUR.get(st, "#111827")}"><b>{escape(st)}</b></font>', small),
                     P(clip(s.get("summary") or clean(s.get("evidence")) or s.get("handback")), small)])
    story.append(table(rows, [11 * mm, 45 * mm, 17 * mm, 97 * mm]))

    if intake:
        story += [P("2. Configuration reference", h2)]
        c, sc, sd = intake.get("company") or {}, intake.get("security_contact") or {}, intake.get("sending_domain") or {}
        addr = ", ".join(str(c.get(k)) for k in ("street", "city", "state", "postal_code", "country") if c.get(k))
        dom = (f"{sd.get('subdomain_prefix') or 'e'}.{sd['root_domain']}" if sd.get("root_domain") else "not configured")
        opt = intake.get("options") or {}
        ref = [[P("Data space"), P(f"{intake.get('data_space')} (permanent)")],
               [P("Company address (email footer)"), P(addr or "not provided")],
               [P("Security contact"), P(", ".join(x for x in (sc.get("name"), sc.get("email"), sc.get("phone")) if x))],
               [P("Sending domain"), P(f"{dom} ({'activated' if sd.get('activate') else 'created as Draft, not activated'})" if sd.get("root_domain") else dom)],
               [P("From address"), P(f"{sd.get('from_display_name', '')} <{sd.get('from_username', '')}@{dom}>" if sd.get("root_domain") else "n/a")],
               [P("Einstein features"), P(", ".join(FEATURES.get(f, f) for f in (opt.get("einstein_features") or [])) or "none")],
               [P("Test send"), P((intake.get("test_send") or {}).get("recipient_email") or "not requested")]]
        story.append(table(ref, [55 * mm, 115 * mm], header=False))

    skipped = [(sid, name, (steps.get(sid) or {}).get("summary") or clean((steps.get(sid) or {}).get("evidence", ""))) for sid, name in STEPS
               if (steps.get(sid) or {}).get("status") == "skipped"]
    open_items = [(sid, name, steps.get(sid) or {}) for sid, name in STEPS
                  if (steps.get(sid) or {}).get("status") not in ("done", "skipped")]
    story += [P("3. Decisions and skipped steps", h2)]
    story.append(table([hdr("Step", "Item", "Reason")] +
                       [[P(a, small), P(b, small), P(clip(c, 400), small)] for a, b, c in skipped] or
                       [hdr("Step", "Item", "Reason"), [P("-"), P("none"), P("")]],
                       [11 * mm, 45 * mm, 114 * mm]))

    story += [P("4. Actions for the customer", h2)]
    acts = [f"{sid} {name}: {clip(s.get('handback') or s.get('evidence'), 300)}" for sid, name, s in open_items]
    s20 = steps.get("S20") or {}
    if s20.get("status") == "done" and "activ" in str(s20.get("evidence", "")).lower():
        acts.append("Optional: review and activate the new record page with Data 360 components "
                    "(Setup > Object Manager > Contact > Lightning Record Pages > Activation).")
    s17 = str((steps.get("S17") or {}).get("evidence", ""))
    if "72" in s17 or "Send Time" in s17 or "STO" in s17:
        acts.append("Einstein Send Time Optimization trains its model in the background for up to 72 hours; no action needed.")
    if dns and (steps.get("S13") or {}).get("status") != "done":
        acts.append("To activate the sending domain later: add the DNS records below at the registrar, then in "
                    "Setup > Authenticated Domains tick 'I completed my changes with my DNS provider' and click "
                    "'Activate my Domain'. Validation can take up to 72 hours.")
    acts.append("Temporary automation grants (trust approvals) expire on their own; remove any left in the engagement's approvals folder.")
    for a in acts:
        story.append(P(f"• {a}"))

    if dns and (steps.get("S13") or {}).get("status") != "done":
        story.append(KeepTogether([P("5. DNS records for the sending domain", h2),
                                   table([hdr("Type", "Host / Name", "Value")] +
                                         [[P(a, small), P(b, small), P(c, small)] for a, b, c in dns],
                                         [14 * mm, 70 * mm, 86 * mm])]))

    story += [P("6. How to re-verify", h2),
              P("Run from any machine with the Salesforce CLI logged in to the org: sf data query -o <alias> -q \"<query>\"", small)]
    story.append(table([hdr("Check", "Query")] + [[P(a, small), P(b, small)] for a, b in VERIFY], [40 * mm, 130 * mm]))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.HexColor("#6b7280"))
        canvas.drawString(15 * mm, 10 * mm, f"MC Next setup handover · {client}")
        canvas.drawRightString(195 * mm, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    SimpleDocTemplate(out, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=15 * mm,
                      bottomMargin=16 * mm, title=f"{client} MC Next setup handover",
                      author="mcnext-setup agent").build(story, onFirstPage=footer, onLaterPages=footer)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("engagement")
    ap.add_argument("--out")
    a = ap.parse_args()
    eng = os.path.abspath(os.path.expanduser(a.engagement))
    client = (load(os.path.join(eng, "manifest.json"), {}) or {}).get("client", "Client")
    out = a.out or os.path.join(eng, "out", "setup", re.sub(r"[^A-Za-z0-9]+", "_", client).strip("_") + "_MC_Next_Setup_Handover.pdf")
    print(build(eng, out))

if __name__ == "__main__":
    main()
