#!/usr/bin/env python3
"""Generate a tailored resume .docx for Martin Shijo (Steelcase IT Intern)."""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_TAB_ALIGNMENT, WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from pathlib import Path

ICONS = Path(__file__).resolve().parent / "icons"
BUILD = Path(__file__).resolve().parent.parent / "build"
BUILD.mkdir(parents=True, exist_ok=True)

RIGHT_TAB = Inches(7.5)  # usable width with 0.5in margins on 8.5in page

doc = Document()
for s in doc.sections:
    s.top_margin = Inches(0.5)
    s.bottom_margin = Inches(0.5)
    s.left_margin = Inches(0.5)
    s.right_margin = Inches(0.5)

normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(11)
normal.paragraph_format.space_after = Pt(0)
normal.paragraph_format.line_spacing = 1.0


def set_bottom_border(paragraph):
    p = paragraph._p
    pPr = p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "000000")
    pbdr.append(bottom)
    pPr.append(pbdr)


def name_line(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(21)


def _add_hyperlink(paragraph, url, text):
    r_id = paragraph.part.relate_to(url, RT.HYPERLINK, is_external=True)
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), r_id)
    run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0563C1")
    rPr.append(color)
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rPr.append(u)
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), "19")  # 9.5pt (half-points)
    rPr.append(sz)
    run.append(rPr)
    t = OxmlElement("w:t")
    t.text = text
    run.append(t)
    link.append(run)
    paragraph._p.append(link)


def _add_plain(paragraph, text):
    r = paragraph.add_run(text)
    r.font.size = Pt(9.5)


def contact_line(_unused=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    items = [
        ("email", "martinshijo9@gmail.com", "mailto:martinshijo9@gmail.com"),
        ("phone", "667-272-4968", None),
        ("github", "martinorsumn", "https://github.com/martinorsumn"),
        ("linkedin", "martinshijo", "https://www.linkedin.com/in/martin-shijo-9032aa337"),
    ]
    for i, (name, text, url) in enumerate(items):
        run = p.add_run()
        run.add_picture(str(ICONS / f"{name}.png"), height=Pt(9))
        _add_plain(p, " ")
        if url:
            _add_hyperlink(p, url, text)
        else:
            _add_plain(p, text)
        if i < len(items) - 1:
            _add_plain(p, "    ")


def section(title):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(title.upper())
    r.bold = True
    r.font.size = Pt(12.5)
    set_bottom_border(p)


def header_row(left, right, bold=True, italic=False, size=11, space_before=3):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.tab_stops.add_tab_stop(RIGHT_TAB, WD_TAB_ALIGNMENT.RIGHT)
    rl = p.add_run(left)
    rl.bold = bold
    rl.italic = italic
    rl.font.size = Pt(size)
    if right:
        p.add_run("\t")
        rr = p.add_run(right)
        rr.italic = italic
        rr.font.size = Pt(size)


def subtitle(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(text)
    r.italic = True
    r.font.size = Pt(10.5)


def bullet(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.27)
    p.paragraph_format.first_line_indent = Inches(-0.15)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run("\u2022  " + text)
    r.font.size = Pt(11)


def skill(label, items):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.27)
    p.paragraph_format.first_line_indent = Inches(-0.15)
    p.paragraph_format.space_after = Pt(1)
    b = p.add_run("\u2022  " + label + ": ")
    b.bold = True
    p.add_run(items)


def body(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    p.add_run(text)


# ---- Content ----
name_line("MARTIN SHIJO")
contact_line(
    "martinshijo9@gmail.com  |  667-272-4968  |  github.com/martinorsumn  |  linkedin.com/in/martinshijo"
)

section("Summary")
body(
    "Computer Science student at the University of Maryland (graduating 2029) seeking the "
    "Information Technology Summer Intern role at Steelcase. I enjoy using technology to solve "
    "real business problems, from building software in Java and Python to improving hands on "
    "processes during a manufacturing internship. Curious, adaptable, and motivated to learn new "
    "tools and contribute to a collaborative IT team."
)

section("Education")
header_row("University of Maryland, College Park (UMD)", "")
header_row("B.S. Computer Science", "Expected May 2029", bold=False, space_before=0)
header_row(
    "FIRE (UMD research program) \u2014 Climate Computing",
    "Spring 2027",
    bold=False,
    space_before=0,
)

section("Skills")
skill("Languages", "Java, Python")
skill("Tech", "Git, GitHub, Cursor, 3D Printing, Laser Cutting, VEX Robotics, Bambu Lab, xTool Studio")

section("Work Experience")
header_row("MAGIC  |  Robotics Intern  |  Bambu Lab, xTool Studio", "Feb 2026 \u2013 Jun 2026")
bullet(
    "Prototyped 4 Tinkercad cable holders. Three of the four, including the final one, started from "
    "a premade design. The first was a premade spool on a U. Final version installed (50+ units)"
)
bullet(
    "Assembled and took apart VEX robots from scratch, with and without tutorials, and prepared "
    "20 kits for 20+ students"
)

header_row("American Ice Co. Cafe  |  Barista", "Jun 2023 \u2013 Jun 2026")
bullet(
    "Managed solo shifts serving ~60 customers/shift while handling POS, inventory, and ~10 "
    "delivery orders/day in a caf\u00e9 generating up to $2,000/day"
)
bullet("Trained 3 new team members on workflows and operating procedures")

section("Projects")
header_row("Nightfall \u2014 Roblox Horror Tycoon", "Mar 2026 \u2013 Jul 2026")
subtitle("AI Assisted Development  |  Roblox Studio")
bullet(
    "Directed a Roblox horror tycoon in Studio by supplying assets and direction, then iterating "
    "with AI on changes such as player speed until the game felt right"
)
bullet(
    "Tested AI generated systems for resources, base building, villagers, pathfinding, day and "
    "night cycles, audio, and tree growth, and requested tweaks until they worked"
)

header_row("Passport Project", "Oct 2026")
subtitle("Java  |  Eclipse  |  JUnit")
bullet(
    "Built a Passport class in Java with multiple constructors, name validation, and StringBuffer "
    "stamp tracking"
)
bullet(
    "Implemented equals, compareTo, separator formatting, and static helpers, verified with JUnit tests"
)

header_row("Python Adventure Game", "May 2024 \u2013 Aug 2024")
subtitle("Python  |  GitHub")
bullet(
    "Developed a text based adventure game featuring randomized combat, enemy encounters, health, "
    "armor, weapons, and escape mechanics"
)
bullet(
    "Implemented a village system with shops, trading, inventory, and upgrades using functions, "
    "loops, lists, dictionaries, and randomized gameplay"
)

section("Leadership Experience")
header_row(
    "Bitcamp 2027 Logistics Organizer (Hardware)  |  University of Maryland", "Oct 2026 \u2013 Present"
)
bullet(
    "Logistics organizer for Bitcamp, one of the East Coast's largest hackathons (1,000+ hackers), "
    "helping coordinate event operations and logistics"
)

header_row("Class Vice President  |  Winters Mill High School", "Sep 2024 \u2013 May 2026")
bullet("Represented ~300 students on a 5-person board; organized 15 events and raised $8,000 for prom")

out = BUILD / "Martin_Shijo_Resume_Steelcase.docx"
doc.save(str(out))
print("Saved", out)
