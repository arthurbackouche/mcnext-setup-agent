#!/usr/bin/env python3
"""Build the client-neutral AMPscript compatibility PDF: explainer page + register appendix.

Usage:
  python3 build_report.py --client "Acme Retail" --outdir out/content \
      --register out/content/register.csv --stats out/content/stats.json

stats.json schema (author it from the parse results before running):
{
 "audit_date": "6 August 2026",
 "release": "Summer '26",
 "total": 494, "functions_live": 41, "clear_path_pct": "96%", "redesign_count": 3,
 "verdict_counts": {"A": 40, "B": 2, "C": 11, "D": 103, "E": 335, "F": 3},
 "legend": [["A","No AMPscript","40","Plain content..."], ...six rows...],
 "left_title": "What already maps to Marketing Cloud Next",
 "left_rows": [["Heading","Body..."], ...],
 "right_title": "The one change that unlocks 335 emails",
 "right_text": "Paragraphs with <br/><br/> breaks and <b>bold</b>...",
 "spike_title": "ONE TEST DE-RISKS 90% OF THE ESTATE",
 "spike_text": "...",
 "cta_main": "Most of this estate is buildable in Marketing Cloud Next today.",
 "redesign_names": ["Email A", "Email B"]
}
All panels are measured before drawing; still run the visual QA loop after building.
"""
import csv, json, argparse, os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

W, H = A4
NAVY, NAVY2, NAVY3 = (colors.HexColor(x) for x in ("#0D1B2A","#152236","#1C3050"))
SF_BLUE, ORANGE = colors.HexColor("#00A1E0"), colors.HexColor("#FF6B35")
OFFWHITE, MID_GRAY, DIM_GRAY = (colors.HexColor(x) for x in ("#D6E4F0","#7A99B0","#2E4560"))
GREEN, AMBER, WHITE = colors.HexColor("#3DDC97"), colors.HexColor("#FFC857"), colors.white
MARGIN, GAP_SM, GAP_MD = 14*mm, 4*mm, 7*mm
CW = W - 2*MARGIN
VCOL = {"A":GREEN,"B":GREEN,"C":SF_BLUE,"D":NAVY3,"E":AMBER,"F":ORANGE}
VLABEL = {"A":"A \u00b7 Ready now","B":"B \u00b7 Ready now","C":"C \u00b7 Validate",
          "D":"D \u00b7 Native rebuild","E":"E \u00b7 Data-prep fix","F":"F \u00b7 Redesign"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--register", required=True)
    ap.add_argument("--stats", required=True)
    args = ap.parse_args()
    S = json.load(open(args.stats))
    out = os.path.join(args.outdir, "AMPscript_MCNext_Compatibility.pdf")
    c = rl_canvas.Canvas(out, pagesize=A4)

    def panel(x,y,w,h,fill=NAVY2,stroke=DIM_GRAY,lw=0.5,r=3*mm):
        c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(lw)
        c.roundRect(x,y,w,h,r,fill=1,stroke=1)
    def text(x,y,s,font="Helvetica",size=8,col=OFFWHITE,align="l"):
        c.setFont(font,size); c.setFillColor(col)
        {"l":c.drawString,"c":c.drawCentredString,"r":c.drawRightString}[align](x,y,s)
    def para(x,y,w,h,txt,size=7.6,leading=10.2,col=OFFWHITE):
        st = ParagraphStyle("p",fontName="Helvetica",fontSize=size,leading=leading,textColor=col)
        p = Paragraph(txt,st); pw,ph = p.wrap(w,h); p.drawOn(c,x,y-ph); return ph
    def m_para(txt,w,size,leading):
        st = ParagraphStyle("m",fontName="Helvetica",fontSize=size,leading=leading)
        p = Paragraph(txt,st); pw,ph = p.wrap(w,300*mm); return ph
    def header_footer(label):
        c.setFillColor(NAVY); c.rect(0,0,W,H,fill=1,stroke=0)
        HB = 20*mm
        c.setFillColor(NAVY2); c.rect(0,H-HB,W,HB,fill=1,stroke=0)
        text(MARGIN,H-HB+11*mm,S.get("client",args.client),"Helvetica-Bold",12.5,WHITE)
        text(MARGIN,H-HB+6.2*mm,"Marketing Cloud Engagement \u2192 Marketing Cloud Next","Helvetica",7,MID_GRAY)
        text(W-MARGIN,H-HB+8.6*mm,label,"Helvetica-Bold",8.5,MID_GRAY,"r")
        c.setStrokeColor(SF_BLUE); c.setLineWidth(1.2); c.line(0,H-HB,W,H-HB)
        c.setFillColor(NAVY2); c.rect(0,0,W,12*mm,fill=1,stroke=0)
        c.setStrokeColor(SF_BLUE); c.line(0,12*mm,W,12*mm)
        text(MARGIN,4.8*mm,f"Prepared for {args.client}  \u00b7  Confidential","Helvetica",6.5,MID_GRAY)
        text(W-MARGIN,4.8*mm,f"Live tenant audit \u00b7 {S['audit_date']}","Helvetica",6.5,MID_GRAY,"r")

    # ---------- Page 1 ----------
    header_footer("AMPSCRIPT COMPATIBILITY ANALYSIS")
    y = H - 20*mm - GAP_MD
    text(MARGIN,y-6*mm,"Your email estate is ready for Marketing Cloud Next.","Helvetica-Bold",16.5,SF_BLUE)
    y -= 11*mm
    para(MARGIN,y,CW,12*mm,
        f"Every AMPscript-personalised email in the {args.client} Marketing Cloud Engagement tenant was pulled via API and "
        f"tested, function by function, against the {S['functions_live']} AMPscript functions live in Marketing Cloud Next ({S['release']} release).",8.2,11)
    y -= 10*mm + GAP_SM

    SB_H = 19*mm; sw = (CW-3*GAP_SM)/4
    stats = [(str(S["total"]),"emails & templates","analysed in full",SF_BLUE),
             (str(S["functions_live"]),"AMPscript functions","live in MC Next today",SF_BLUE),
             (S["clear_path_pct"],"of the estate has a","clear path to Next now",GREEN),
             (str(S["redesign_count"]),"emails need genuine","process redesign",ORANGE)]
    for i,(num,l1,l2,col) in enumerate(stats):
        x = MARGIN+i*(sw+GAP_SM); panel(x,y-SB_H,sw,SB_H)
        text(x+sw/2,y-9.5*mm,num,"Helvetica-Bold",17,col,"c")
        text(x+sw/2,y-13.8*mm,l1,"Helvetica",6.6,MID_GRAY,"c")
        text(x+sw/2,y-16.8*mm,l2,"Helvetica",6.6,MID_GRAY,"c")
    y -= SB_H + GAP_MD

    text(MARGIN,y-3*mm,"WHERE EVERY EMAIL LANDS","Helvetica-Bold",8,MID_GRAY)
    y -= 3*mm + GAP_SM
    BAR_H = 9*mm; vc = S["verdict_counts"]
    segs = [("A+B \u00b7 %d"%(vc.get("A",0)+vc.get("B",0)),GREEN,vc.get("A",0)+vc.get("B",0))] + \
           [(f"{k} \u00b7 {vc[k]}",VCOL[k],vc[k]) for k in ("C","D","E","F") if vc.get(k)]
    total = sum(s[2] for s in segs); x = MARGIN; under = []
    for label,col,n in segs:
        sw2 = CW*n/total
        c.setFillColor(col); c.rect(x,y-BAR_H,sw2,BAR_H,fill=1,stroke=0)
        tcol = OFFWHITE if col==NAVY3 else NAVY
        if sw2 > 22*mm: text(x+sw2/2,y-5.8*mm,label,"Helvetica-Bold",7.5,tcol,"c")
        else: under.append((x+sw2/2,label,col))
        x += sw2
    uy = y-BAR_H-3*mm; slots = [MARGIN, MARGIN+26*mm, W-MARGIN-12*mm]
    for i,(ux,ul,ucol) in enumerate(under):
        lx = slots[i] if i < len(slots) else ux
        c.setStrokeColor(ucol); c.setLineWidth(0.8)
        c.line(ux,y-BAR_H,ux,uy+1.2*mm); c.line(ux,uy+1.2*mm,lx,uy+1.2*mm)
        text(lx,uy-1.6*mm,ul,"Helvetica-Bold",6.6,ucol,"c" if lx>W/2 else "l")
    y -= BAR_H + 8*mm

    # Legend (measured)
    row_hs = [4.4*mm + m_para(d,CW-19*mm,6.5,8.2) + 2.2*mm for *_,d in S["legend"]]
    LEG_H = 11*mm + sum(row_hs) + 1.5*mm
    panel(MARGIN,y-LEG_H,CW,LEG_H)
    text(MARGIN+5*mm,y-6.5*mm,"Reading the verdicts","Helvetica-Bold",9,WHITE)
    ly = y-11*mm
    for letter,title,count,desc in S["legend"]:
        col = VCOL[letter]
        c.setFillColor(col); c.roundRect(MARGIN+5*mm,ly-3.6*mm,5*mm,4.6*mm,1*mm,fill=1,stroke=0)
        text(MARGIN+7.5*mm,ly-2.6*mm,letter,"Helvetica-Bold",7.5,OFFWHITE if col==NAVY3 else NAVY,"c")
        text(MARGIN+12.5*mm,ly-2.6*mm,title,"Helvetica-Bold",7.3,WHITE)
        text(MARGIN+12.5*mm+c.stringWidth(title,"Helvetica-Bold",7.3)+2*mm,ly-2.6*mm,
             f"\u00b7 {count} emails","Helvetica",6.6,MID_GRAY)
        ph = para(MARGIN+12.5*mm,ly-4.4*mm,CW-19*mm,25*mm,desc,6.5,8.2)
        ly -= 4.4*mm + ph + 2.2*mm
    y -= LEG_H + GAP_MD

    # Two columns (measured)
    col_w = (CW-GAP_SM)/2
    left_need = 13.5*mm + sum(3.2*mm + m_para(b,col_w-10*mm,6.7,8.5) + 2.2*mm for _,b in S["left_rows"]) + 2*mm
    right_need = 13.5*mm + m_para(S["right_text"],col_w-10*mm,7.2,9.8) + 4*mm
    COL_H = max(left_need,right_need)
    panel(MARGIN,y-COL_H,col_w,COL_H)
    c.setFillColor(SF_BLUE); c.roundRect(MARGIN,y-3*mm,col_w,3*mm,1.4*mm,fill=1,stroke=0)
    c.rect(MARGIN,y-3*mm,col_w,1.6*mm,fill=1,stroke=0)
    xx = MARGIN+5*mm
    text(xx,y-9*mm,S["left_title"],"Helvetica-Bold",9,WHITE)
    yy = y-13.5*mm
    for h,b in S["left_rows"]:
        text(xx,yy,h,"Helvetica-Bold",7.4,SF_BLUE)
        ph = para(xx,yy-3.2*mm,col_w-10*mm,25*mm,b,6.7,8.5)
        yy -= 3.2*mm + ph + 2.2*mm
    x2 = MARGIN+col_w+GAP_SM
    panel(x2,y-COL_H,col_w,COL_H,stroke=ORANGE,lw=1.8)
    c.setFillColor(ORANGE); c.roundRect(x2,y-3*mm,col_w,3*mm,1.4*mm,fill=1,stroke=0)
    c.rect(x2,y-3*mm,col_w,1.6*mm,fill=1,stroke=0)
    text(x2+5*mm,y-9*mm,S["right_title"],"Helvetica-Bold",9,WHITE)
    para(x2+5*mm,y-13.5*mm,col_w-10*mm,80*mm,S["right_text"],7.2,9.8)
    y -= COL_H + GAP_MD

    VS_H = 11*mm + m_para(S["spike_text"],CW-10*mm,6.9,8.8) + 3*mm
    panel(MARGIN,y-VS_H,CW,VS_H,fill=NAVY3)
    text(MARGIN+5*mm,y-6.5*mm,S["spike_title"],"Helvetica-Bold",8,SF_BLUE)
    para(MARGIN+5*mm,y-9.8*mm,CW-10*mm,20*mm,S["spike_text"],6.9,8.8)
    y -= VS_H + GAP_MD

    CTA_H = 14*mm
    c.setFillColor(SF_BLUE); c.roundRect(MARGIN,y-CTA_H,CW,CTA_H,3*mm,fill=1,stroke=0)
    text(W/2,y-6*mm,S["cta_main"],"Helvetica-Bold",9.5,NAVY,"c")
    text(W/2,y-10.4*mm,"Full function-by-function register: see Appendix.","Helvetica",7.2,NAVY,"c")
    c.showPage()

    # ---------- Appendix ----------
    reg = list(csv.reader(open(args.register)))[1:]
    redesign_names = set(S.get("redesign_names",[]))
    ROW_H = 3.55*mm; TOP = H-20*mm-8*mm; BOT = 16*mm
    per_page = int((TOP-BOT-10*mm)/ROW_H)
    pages = [reg[i:i+per_page] for i in range(0,len(reg),per_page)]
    for pi,chunk in enumerate(pages):
        header_footer("APPENDIX \u00b7 EMAIL-BY-EMAIL REGISTER")
        yy = TOP
        text(MARGIN,yy,f"All emails and templates \u00b7 verdict against Marketing Cloud Next \u00b7 page {pi+1} of {len(pages)}","Helvetica-Bold",7.5,MID_GRAY)
        yy -= 5*mm
        text(MARGIN,yy,"EMAIL / TEMPLATE","Helvetica-Bold",6.2,SF_BLUE)
        text(MARGIN+96*mm,yy,"VERDICT","Helvetica-Bold",6.2,SF_BLUE)
        text(MARGIN+124*mm,yy,"FUNCTIONS TO REPLACE / REDESIGN","Helvetica-Bold",6.2,SF_BLUE)
        yy -= 1.6*mm
        c.setStrokeColor(DIM_GRAY); c.setLineWidth(0.4); c.line(MARGIN,yy,W-MARGIN,yy)
        yy -= 3*mm
        for i,(name,at,verdict,native,redesign) in enumerate(chunk):
            letter = verdict.strip()[0].upper()
            if name in redesign_names: letter = "F"
            lab, colr = VLABEL[letter], (ORANGE if letter=="F" else
                        {"A":GREEN,"B":GREEN,"C":SF_BLUE,"D":SF_BLUE,"E":AMBER}[letter])
            if i % 2 == 0:
                c.setFillColor(NAVY2); c.rect(MARGIN-1*mm,yy-1.1*mm,CW+2*mm,ROW_H,fill=1,stroke=0)
            nm = name if len(name) <= 62 else name[:59]+"\u2026"
            text(MARGIN,yy,nm,"Helvetica",6.0,OFFWHITE)
            text(MARGIN+96*mm,yy,lab,"Helvetica-Bold",6.0,colr)
            fns = ", ".join(x for x in (redesign,native) if x)
            fns = fns if len(fns) <= 52 else fns[:49]+"\u2026"
            text(MARGIN+124*mm,yy,fns or "\u2014","Helvetica",5.6,MID_GRAY)
            yy -= ROW_H
        c.showPage()
    c.save()
    print("written:", out, "| pages:", 1+len(pages))

if __name__ == "__main__":
    main()
