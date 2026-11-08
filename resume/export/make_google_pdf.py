#!/usr/bin/env python3
"""One-page resume PDF tailored for a Google Software Engineering Intern example.

Same layout as make_pdf.py (Tinos, one Letter page, logo contact row).
Content is reordered toward Java, Python, data structures, and testing.
Facts come from the master resume and the Steelcase export. Nothing new is invented.
"""
import json
from pathlib import Path
from fpdf import FPDF
from fpdf.enums import XPos, YPos

FONT_DIR = "/usr/share/fonts/truetype/croscore/"
ICONS = Path(__file__).resolve().parent / "icons"
BUILD = Path(__file__).resolve().parent.parent / "build"
BUILD.mkdir(parents=True, exist_ok=True)

# ---- tunable sizing ----
NAME_SZ = 21
CONTACT_SZ = 10
SEC_SZ = 12.5
FS = 11            # body font size
LH = 4.6           # body line height
HEAD_H = 5.0       # entry header line height
SUB_H = 4.5        # subtitle line height
SEC_BEFORE = 1.8   # space before a section header
SEC_AFTER = 1.2    # space after the section rule
BULLET_AFTER = 0.4 # gap after each bullet block
ICON_H = 3.4
# ------------------------

pdf = FPDF(format="letter", unit="mm")
pdf.set_margins(13.0, 12.0, 13.0)
pdf.set_auto_page_break(True, margin=11.0)
pdf.add_font("Tinos", "", FONT_DIR + "Tinos-Regular.ttf")
pdf.add_font("Tinos", "B", FONT_DIR + "Tinos-Bold.ttf")
pdf.add_font("Tinos", "I", FONT_DIR + "Tinos-Italic.ttf")
pdf.add_font("Tinos", "BI", FONT_DIR + "Tinos-BoldItalic.ttf")
pdf.add_page()
EPW = pdf.epw

NEXT = dict(new_x=XPos.LMARGIN, new_y=YPos.NEXT)
RIGHT = dict(new_x=XPos.RIGHT, new_y=YPos.TOP)


def section(title):
    pdf.ln(SEC_BEFORE)
    pdf.set_font("Tinos", "B", SEC_SZ)
    pdf.cell(0, SEC_SZ * 0.42, title.upper(), **NEXT)
    y = pdf.get_y()
    pdf.line(pdf.l_margin, y, pdf.l_margin + EPW, y)
    pdf.ln(SEC_AFTER)


def header_row(left, right, bold=True):
    if right:
        pdf.set_font("Tinos", "", FS)
        rw = pdf.get_string_width(right) + 1
        pdf.set_font("Tinos", "B" if bold else "", FS)
        pdf.cell(EPW - rw, HEAD_H, left, **RIGHT)
        pdf.set_font("Tinos", "", FS)
        pdf.cell(rw, HEAD_H, right, align="R", **NEXT)
    else:
        pdf.set_font("Tinos", "B" if bold else "", FS)
        pdf.cell(0, HEAD_H, left, **NEXT)


def subtitle(text):
    pdf.set_font("Tinos", "I", FS - 0.5)
    pdf.cell(0, SUB_H, text, **NEXT)


def bullet(text):
    x0 = pdf.l_margin + 2
    pdf.set_font("Tinos", "", FS)
    pdf.set_x(x0)
    pdf.cell(4.0, LH, "\u2022", **RIGHT)
    save_lm = pdf.l_margin
    pdf.set_left_margin(x0 + 4.0)
    pdf.set_x(x0 + 4.0)
    pdf.multi_cell(EPW - 6.0, LH, text)
    pdf.set_left_margin(save_lm)
    pdf.ln(BULLET_AFTER)


def skill(label, items):
    x0 = pdf.l_margin + 2
    pdf.set_x(x0)
    pdf.set_font("Tinos", "", FS)
    pdf.cell(4.0, LH, "\u2022", **RIGHT)
    pdf.set_font("Tinos", "B", FS)
    lab = label + ": "
    pdf.cell(pdf.get_string_width(lab), LH, lab, **RIGHT)
    pdf.set_font("Tinos", "", FS)
    pdf.cell(0, LH, items, **NEXT)


def body(text):
    pdf.set_font("Tinos", "", FS)
    pdf.multi_cell(EPW, LH, text)


pdf.set_font("Tinos", "B", NAME_SZ)
pdf.cell(0, NAME_SZ * 0.42, "MARTIN SHIJO", align="C", **NEXT)
pdf.ln(1.0)


def contact_row():
    asp = json.load(open(ICONS / "aspects.json"))
    items = [
        ("email", "martinshijo9@gmail.com", "mailto:martinshijo9@gmail.com"),
        ("phone", "667-272-4968", None),
        ("github", "martinorsumn", "https://github.com/martinorsumn"),
        ("linkedin", "martinshijo", "https://www.linkedin.com/in/martin-shijo-9032aa337"),
    ]
    line_h = 5.0
    gap = 1.5
    sep = 5.0
    pdf.set_font("Tinos", "", CONTACT_SZ)
    widths = [(ICON_H * asp[n], pdf.get_string_width(t)) for n, t, _ in items]
    total = sum(iw + gap + tw for iw, tw in widths) + sep * (len(items) - 1)
    x = pdf.l_margin + (EPW - total) / 2.0
    y = pdf.get_y()
    icon_y = y + (line_h - ICON_H) / 2.0
    for i, (name, text, url) in enumerate(items):
        iw, tw = widths[i]
        pdf.image(str(ICONS / f"{name}.png"), x=x, y=icon_y, h=ICON_H)
        if url:
            pdf.link(x, icon_y, iw, ICON_H, url)
        x += iw + gap
        pdf.set_xy(x, y)
        if url:
            pdf.set_font("Tinos", "U", CONTACT_SZ)
            pdf.set_text_color(5, 99, 193)
            pdf.cell(tw, line_h, text, link=url, **RIGHT)
            pdf.set_text_color(0, 0, 0)
        else:
            pdf.set_font("Tinos", "", CONTACT_SZ)
            pdf.cell(tw, line_h, text, **RIGHT)
        x += tw + (sep if i < len(items) - 1 else 0)
    pdf.set_xy(pdf.l_margin, y + line_h)
    pdf.ln(1.4)


contact_row()

section("Summary")
body(
    "Computer Science student at the University of Maryland (graduating May 2029) seeking a "
    "Software Engineering Intern role at Google. I build software in Java and Python, from data "
    "structures and game systems to small tools. I like taking a problem apart and iterating until "
    "the result works."
)

section("Education")
header_row("University of Maryland, College Park (UMD)", "")
header_row("B.S. Computer Science", "Expected May 2029", bold=False)
header_row("FIRE (UMD research program) \u2014 Climate Computing", "Spring 2027", bold=False)

section("Skills")
skill("Languages", "Java, Python")
skill("Development", "Git, GitHub, Cursor")

section("Projects")
header_row("Python Adventure Game", "May 2024 \u2013 Aug 2024")
subtitle("Python  |  GitHub")
bullet("Developed a text based adventure game featuring randomized combat, enemy encounters, health, armor, weapons, and escape mechanics")
bullet("Implemented a village system with shops, trading, inventory, and upgrades using functions, loops, lists, dictionaries, and randomized gameplay")
header_row("Passport Project", "Oct 2026")
subtitle("Java  |  Eclipse  |  JUnit")
bullet("Built a Passport class in Java with multiple constructors, name validation, and StringBuffer stamp tracking")
bullet("Implemented equals, compareTo, separator formatting, and static helpers, verified with JUnit tests")
header_row("Nightfall \u2014 Roblox Horror Tycoon", "Mar 2026 \u2013 Jul 2026")
subtitle("AI Assisted Development  |  Roblox Studio  |  Lua")
bullet("Developed an iterative Roblox prototype to evaluate AI assisted development workflows and document their capabilities and limitations")
bullet("Designed resource collection, base building, NPC villagers, enemy pathfinding, day/night cycles, audio, and procedural tree growth; tested AI generated systems and refined behavior")

section("Work Experience")
header_row("MAGIC  |  Robotics Intern  |  Bambu Lab, xTool Studio", "Feb 2026 \u2013 Jun 2026")
bullet("Designed and prototyped 4 iterations of a 3D printed cable management system in Tinkercad; final design deployed across the workspace (50+ units installed)")
bullet("Assembled and inventoried 20 VEX Robotics kits supporting 20+ students in STEM programs")
header_row("American Ice Co. Cafe  |  Barista", "Jun 2023 \u2013 Jun 2026")
bullet("Managed solo shifts serving ~60 customers/shift while handling POS, inventory, and ~10 delivery orders/day in a caf\u00e9 generating up to $2,000/day")
bullet("Trained 3 new team members on workflows and operating procedures")

section("Leadership Experience")
header_row("Class Vice President  |  Winters Mill High School", "Sep 2024 \u2013 May 2026")
bullet("Represented ~300 students on a 5-person board; organized 15 events and raised $8,000 for prom")
header_row("Bitcamp 2027 Logistics Organizer (Hardware)  |  University of Maryland", "Oct 2026 \u2013 Present")
bullet("Logistics organizer for Bitcamp, one of the East Coast's largest hackathons (1,000+ hackers), helping coordinate event operations and logistics")

out = BUILD / "Martin_Shijo_Resume_Google.pdf"
pdf.output(str(out))
print("wrote", out, "| pages:", pdf.page_no())
