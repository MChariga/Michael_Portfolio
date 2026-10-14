"""Builds the CV PDF from content.json so the site and the PDF never disagree. Run: python3 make_cv.py"""
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem, HRFlowable, KeepTogether
C = json.load(open("content.json", encoding="utf-8")); S = C["site"]; V = C["cv"]
NAVY, BLUE, MUTE = colors.HexColor("#0b2545"), colors.HexColor("#1d4e89"), colors.HexColor("#55627a")
st = lambda n, **k: ParagraphStyle(n, fontName=k.pop("f", "Helvetica"), fontSize=k.pop("s", 9.5), leading=k.pop("l", 13), **k)
body, small = st("b", textColor=colors.HexColor("#1b2638")), st("sm", s=8.8, l=11.5, textColor=MUTE)
h = st("h", f="Helvetica-Bold", s=10, l=12, textColor=BLUE, spaceBefore=11, spaceAfter=3)
role, org = st("r", f="Helvetica-Bold", s=11, l=14, textColor=NAVY), st("o", s=9.2, l=12, textColor=MUTE)
def sec(t): return [Paragraph(t.upper(), h), HRFlowable(width="100%", thickness=.6, color=colors.HexColor("#dbe3ee"), spaceAfter=4)]
def bullets(items): return ListFlowable([ListItem(Paragraph(x, body), leftIndent=11) for x in items], bulletType="bullet", start="\u2022", leftIndent=11, bulletFontSize=8)
doc = SimpleDocTemplate("Michael_Chariga_CV_Oct_2026.pdf", pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=15*mm, bottomMargin=14*mm,
                        title=f'{S["full"]} CV', author=S["full"])
f = []
head = Table([[Paragraph(S["full"], st("n", f="Helvetica-Bold", s=22, l=26, textColor=NAVY)),
               Paragraph(f'{S["location"]}<br/>{S["email"]}<br/>github.com/MChariga', st("c", s=9, l=12, textColor=MUTE, alignment=2))],
              [Paragraph(S["headline"], st("hl", s=11.5, l=14, textColor=BLUE)), ""]], colWidths=[110*mm, 64*mm])
head.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 1), (-1, 1), 2, NAVY), ("BOTTOMPADDING", (0, 1), (-1, 1), 7), ("SPAN", (1, 0), (1, 1)), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
f += [head] + sec("Profile") + [Paragraph(V["summary"], body)] + sec("Core competencies")
comp = V["competencies"]; half = (len(comp) + 1) // 2
t = Table([[bullets(comp[:half]), bullets(comp[half:])]], colWidths=[87*mm, 87*mm]); t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
f += [t] + sec("Experience")
for x in V["experience"]:
    top = Table([[Paragraph(x["role"], role), Paragraph(x["period"], st("p", s=9, l=12, textColor=MUTE, alignment=2))], [Paragraph(f'{x["org"]}, {x["place"]}', org), ""]], colWidths=[140*mm, 34*mm])
    top.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
    f += [KeepTogether([top, Spacer(1, 2), bullets(x["bullets"][:2])]), bullets(x["bullets"][2:]), Spacer(1, 6)]
def two(rows): 
    t = Table(rows, colWidths=[140*mm, 34*mm]); t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)])); return t
f += sec("Education") + [two([[Paragraph(f"<b>{a}</b>, {b}", body), Paragraph(c, st("d", s=9, l=12, textColor=MUTE, alignment=2))] for a, b, c in V["education"]])]
f += sec("Publications and presentations") + [bullets([f'<b>{p["title"]}</b>. {p["venue"]}{", " + p["year"] if p["year"] else ""}' for p in C["pubs"]])]
f += sec("Reports") + [bullets([f"<b>{a}</b>. {b}" for a, b in V["reports"]])]
f += sec("Awards") + [bullets(V["awards"])] + sec("Tools") + [Paragraph(" \u00b7 ".join(V["tools"]), body), Spacer(1, 6), Paragraph("Referees available on request.", small)]
doc.build(f); print("CV built")
