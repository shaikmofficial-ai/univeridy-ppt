#!/usr/bin/env python3
"""
Generator for the "UniVerify V2.0" presentation.
Builds a styled, multi-slide .pptx deck using python-pptx.
Theme: dark Web3 / terminal aesthetic with cyan + electric-blue accents.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# ----------------------------------------------------------------------------
# Palette
# ----------------------------------------------------------------------------
BG_DARK     = RGBColor(0x0A, 0x0E, 0x1A)   # deep navy/charcoal background
BG_PANEL    = RGBColor(0x12, 0x18, 0x2B)   # slightly lighter panel
BG_CODE     = RGBColor(0x05, 0x09, 0x12)   # near-black code block
CYAN        = RGBColor(0x00, 0xE5, 0xC7)   # primary accent (teal/cyan)
BLUE        = RGBColor(0x4D, 0x8C, 0xFF)   # electric blue
PURPLE      = RGBColor(0x9B, 0x6D, 0xFF)   # accent purple
GREEN       = RGBColor(0x3D, 0xDC, 0x84)   # success green
RED         = RGBColor(0xFF, 0x5C, 0x5C)   # error red
AMBER       = RGBColor(0xFF, 0xB3, 0x4D)   # warning amber
WHITE       = RGBColor(0xF2, 0xF5, 0xFA)
GREY        = RGBColor(0x9A, 0xA6, 0xC0)   # muted text
DARKGREY    = RGBColor(0x5A, 0x66, 0x80)

# Code syntax colors
C_KEYWORD   = RGBColor(0xC5, 0x92, 0xFF)
C_TYPE      = RGBColor(0x66, 0xD9, 0xEF)
C_STRING    = RGBColor(0xE6, 0xDB, 0x74)
C_COMMENT   = RGBColor(0x6A, 0x73, 0x88)
C_FUNC      = RGBColor(0x3D, 0xDC, 0x84)
C_PLAIN     = RGBColor(0xE6, 0xEA, 0xF2)

MONO = "Consolas"
SANS = "Segoe UI"
SANS_LIGHT = "Segoe UI Light"

# Slide dimensions (16:9)
SW = Inches(13.333)
SH = Inches(7.5)

prs = Presentation()
prs.slide_width = SW
prs.slide_height = SH
BLANK = prs.slide_layouts[6]


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def add_slide():
    return prs.slides.add_slide(BLANK)


def bg(slide, color=BG_DARK):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def rect(slide, x, y, w, h, color, line=None, line_w=None, shape=MSO_SHAPE.RECTANGLE):
    sp = slide.shapes.add_shape(shape, x, y, w, h)
    sp.fill.solid()
    sp.fill.fore_color.rgb = color
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line
        sp.line.width = line_w or Pt(1)
    sp.shadow.inherit = False
    return sp


def no_fill_rect(slide, x, y, w, h, line, line_w=Pt(1.5), shape=MSO_SHAPE.RECTANGLE):
    sp = slide.shapes.add_shape(shape, x, y, w, h)
    sp.fill.background()
    sp.line.color.rgb = line
    sp.line.width = line_w
    sp.shadow.inherit = False
    return sp


def txt(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP, align=PP_ALIGN.LEFT, wrap=True):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    tf.paragraphs[0].alignment = align
    return tb, tf


def run(p, text, size, color, bold=False, font=SANS, italic=False, spacing=None):
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.name = font
    r.font.color.rgb = color
    if spacing is not None:
        _set_char_spacing(r, spacing)
    return r


def _set_char_spacing(r, pts):
    # pts in points; 100 = 1pt in spc units
    rPr = r._r.get_or_add_rPr()
    rPr.set('spc', str(int(pts * 100)))


def para(tf, first=False):
    if first and len(tf.paragraphs) == 1 and not tf.paragraphs[0].runs:
        return tf.paragraphs[0]
    return tf.add_paragraph()


def accent_bar(slide, x, y, w=Inches(0.09), h=Inches(0.55), color=CYAN):
    rect(slide, x, y, w, h, color)


def slide_header(slide, kicker, title, num):
    """Standard content-slide header with kicker label + title + side index."""
    accent_bar(slide, Inches(0.6), Inches(0.55), h=Inches(0.95))
    tb, tf = txt(slide, Inches(0.85), Inches(0.5), Inches(10.5), Inches(1.2))
    p = para(tf, first=True)
    run(p, kicker.upper(), 12, CYAN, bold=True, font=SANS, spacing=2.5)
    p2 = tf.add_paragraph()
    p2.space_before = Pt(2)
    run(p2, title, 30, WHITE, bold=True, font=SANS)
    # slide index top-right
    tbn, tfn = txt(slide, Inches(11.6), Inches(0.55), Inches(1.1), Inches(0.5),
                   align=PP_ALIGN.RIGHT)
    pn = para(tfn, first=True)
    run(pn, f"{num:02d}", 13, DARKGREY, bold=True, font=MONO)
    run(pn, " / 11", 13, DARKGREY, font=MONO)


def footer(slide):
    tb, tf = txt(slide, Inches(0.85), Inches(7.02), Inches(8), Inches(0.35))
    p = para(tf, first=True)
    run(p, "UniVerify V2.0", 9, CYAN, bold=True, font=MONO)
    run(p, "  ·  Decentralized Academic Certificate Verification", 9, DARKGREY, font=SANS)


def chip(slide, x, y, label, color, w=Inches(2.0)):
    sp = rect(slide, x, y, w, Inches(0.42), BG_PANEL, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    _round(sp, 0.5)
    sp.line.color.rgb = color
    sp.line.width = Pt(1)
    tf = sp.text_frame
    tf.word_wrap = True
    tf.margin_top = Pt(2); tf.margin_bottom = Pt(2)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run(p, label, 11, color, bold=True, font=SANS)
    return sp


def _round(shape, val):
    try:
        shape.adjustments[0] = val
    except Exception:
        pass


def card(slide, x, y, w, h, accent):
    """Panel card with a colored top edge."""
    panel = rect(slide, x, y, w, h, BG_PANEL, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    _round(panel, 0.04)
    rect(slide, x, y, w, Inches(0.06), accent)
    return panel


# ----------------------------------------------------------------------------
# SLIDE 1 — Title
# ----------------------------------------------------------------------------
s = add_slide()
bg(s)

# decorative faint grid blocks (hex-like nodes)
for (gx, gy, c) in [
    (Inches(11.1), Inches(0.7), BLUE),
    (Inches(12.0), Inches(1.5), CYAN),
    (Inches(10.6), Inches(1.9), PURPLE),
    (Inches(0.7), Inches(5.9), CYAN),
    (Inches(1.5), Inches(6.5), BLUE),
]:
    d = rect(s, gx, gy, Inches(0.16), Inches(0.16), c, shape=MSO_SHAPE.OVAL)

# big faint side accent
rect(s, Inches(0), Inches(0), Inches(0.18), SH, CYAN)

# kicker
tb, tf = txt(s, Inches(1.0), Inches(1.85), Inches(11), Inches(0.5))
p = para(tf, first=True)
run(p, "WEB3  ·  BLOCKCHAIN  ·  DECENTRALIZED IDENTITY", 14, CYAN, bold=True,
    font=SANS, spacing=3)

# title
tb, tf = txt(s, Inches(0.95), Inches(2.35), Inches(11.6), Inches(2.0))
p = para(tf, first=True)
run(p, "UniVerify ", 66, WHITE, bold=True, font=SANS)
run(p, "V2.0", 66, CYAN, bold=True, font=SANS)
p2 = tf.add_paragraph()
p2.space_before = Pt(4)
run(p2, "Decentralized Academic Certificate Verification Portal", 22, GREY, font=SANS_LIGHT)

# divider
rect(s, Inches(1.0), Inches(4.75), Inches(3.2), Inches(0.03), CYAN)

# subtitle tagline
tb, tf = txt(s, Inches(1.0), Inches(4.95), Inches(11), Inches(0.8))
p = para(tf, first=True)
run(p, "Immutable. Globally accessible. Verified in ", 16, GREY, font=SANS)
run(p, "zero-latency", 16, GREEN, bold=True, font=SANS)
run(p, ".", 16, GREY, font=SANS)

# bottom chips
chip(s, Inches(1.0), Inches(6.0), "Solidity ^0.8.0", CYAN, w=Inches(2.2))
chip(s, Inches(3.35), Inches(6.0), "Ethers.js", BLUE, w=Inches(1.8))
chip(s, Inches(5.3), Inches(6.0), "Sepolia Testnet", PURPLE, w=Inches(2.2))
chip(s, Inches(7.65), Inches(6.0), "MetaMask / EVM", GREEN, w=Inches(2.3))


# ----------------------------------------------------------------------------
# SLIDE 2 — The Problem
# ----------------------------------------------------------------------------
s = add_slide()
bg(s)
slide_header(s, "The Challenge", "The Problem with Traditional Verification", 2)

intro_tb, intro_tf = txt(s, Inches(0.85), Inches(1.75), Inches(11.6), Inches(0.7))
p = para(intro_tf, first=True)
run(p, "Conventional degree verification depends on centralized databases and manual, "
       "paper-based pipelines — slow, costly, and fragile.", 15, GREY, font=SANS)

cards = [
    ("\u23F1", "High Latency", "Manual verification takes 7\u201314 days, delaying admissions, hiring and onboarding.", AMBER),
    ("\u26A0", "Single Point of Failure", "Centralized servers are vulnerable to outages, data manipulation and tampering.", RED),
    ("\U0001F4B0", "Administrative Overhead", "Repeated manual checks create high recurring costs and operational burden.", BLUE),
    ("\U0001F6E1", "Credential Forgery", "Sophisticated fake certificates are hard to detect without a trusted source of truth.", PURPLE),
]
cw = Inches(2.78)
gap = Inches(0.18)
x0 = Inches(0.85)
y0 = Inches(2.75)
for i, (ic, title, body, acc) in enumerate(cards):
    cx = x0 + i * (cw + gap)
    card(s, cx, y0, cw, Inches(3.4), acc)
    # icon
    tbi, tfi = txt(s, cx + Inches(0.25), y0 + Inches(0.3), cw - Inches(0.5), Inches(0.7))
    pi = para(tfi, first=True)
    run(pi, ic, 30, acc, font=SANS)
    # title
    tbt, tft = txt(s, cx + Inches(0.25), y0 + Inches(1.1), cw - Inches(0.5), Inches(0.8))
    pt = para(tft, first=True)
    run(pt, title, 16, WHITE, bold=True, font=SANS)
    # body
    tbb, tfb = txt(s, cx + Inches(0.25), y0 + Inches(1.85), cw - Inches(0.5), Inches(1.4))
    pb = para(tfb, first=True)
    run(pb, body, 12, GREY, font=SANS)
footer(s)


# ----------------------------------------------------------------------------
# SLIDE 3 — The Solution
# ----------------------------------------------------------------------------
s = add_slide()
bg(s)
slide_header(s, "The Solution", "A Decentralized Source of Truth", 3)

# left: narrative
tb, tf = txt(s, Inches(0.85), Inches(1.95), Inches(6.0), Inches(4.5))
p = para(tf, first=True)
run(p, "UniVerify V2.0 anchors academic certificate cryptographic records permanently "
       "onto a public blockchain.", 16, WHITE, font=SANS)
for label, desc, col in [
    ("Immutable", "Once recorded, data can never be altered or deleted.", CYAN),
    ("Globally Accessible", "Anyone, anywhere can verify a credential 24/7.", BLUE),
    ("Zero-Latency", "Verification happens in seconds, not days.", GREEN),
    ("Tamper-Proof", "Cryptographic anchoring defeats forgery attempts.", PURPLE),
]:
    pp = tf.add_paragraph()
    pp.space_before = Pt(12)
    run(pp, "\u25B6 ", 13, col, bold=True, font=SANS)
    run(pp, label + " — ", 14, col, bold=True, font=SANS)
    run(pp, desc, 14, GREY, font=SANS)

# right: before vs after comparison
rx = Inches(7.2)
# before
b = card(s, rx, Inches(1.95), Inches(5.3), Inches(2.05), RED)
tbb, tfb = txt(s, rx + Inches(0.3), Inches(2.15), Inches(4.7), Inches(1.7))
p = para(tfb, first=True)
run(p, "TRADITIONAL", 11, RED, bold=True, font=MONO, spacing=2)
p = tfb.add_paragraph(); p.space_before = Pt(6)
run(p, "7\u201314 days", 24, WHITE, bold=True, font=SANS)
p = tfb.add_paragraph(); p.space_before = Pt(2)
run(p, "Centralized · Manual · SPOF · Forgeable", 12, GREY, font=SANS)

# after
a = card(s, rx, Inches(4.2), Inches(5.3), Inches(2.05), GREEN)
tba, tfa = txt(s, rx + Inches(0.3), Inches(4.4), Inches(4.7), Inches(1.7))
p = para(tfa, first=True)
run(p, "UNIVERIFY V2.0", 11, GREEN, bold=True, font=MONO, spacing=2)
p = tfa.add_paragraph(); p.space_before = Pt(6)
run(p, "~ Seconds", 24, WHITE, bold=True, font=SANS)
p = tfa.add_paragraph(); p.space_before = Pt(2)
run(p, "Decentralized · Immutable · O(1) lookup · Verified", 12, GREY, font=SANS)
footer(s)


# ----------------------------------------------------------------------------
# SLIDE 4 — Project Overview / Metadata
# ----------------------------------------------------------------------------
s = add_slide()
bg(s)
slide_header(s, "Overview", "Project at a Glance", 4)

meta = [
    ("\U0001F3F7", "Project", "UniVerify V2.0"),
    ("\U0001F310", "Domain", "Web3 · Blockchain · DID"),
    ("\U0001F4DC", "Contract", "Solidity ^0.8.0"),
    ("\u26D3", "Network", "Sepolia Testnet (EVM)"),
    ("\U0001F517", "Hash Field", "Manual mock string (P1)"),
    ("\U0001F510", "Access", "Role-Based (Admin only)"),
]
cw = Inches(3.78)
ch = Inches(1.55)
gx = Inches(0.2)
gy = Inches(0.25)
x0 = Inches(0.85)
y0 = Inches(2.0)
accents = [CYAN, BLUE, PURPLE, GREEN, AMBER, RED]
for i, (ic, k, v) in enumerate(meta):
    col = i % 3
    row = i // 3
    cx = x0 + col * (cw + gx)
    cy = y0 + row * (ch + gy)
    card(s, cx, cy, cw, ch, accents[i])
    tbi, tfi = txt(s, cx + Inches(0.28), cy + Inches(0.28), Inches(0.9), Inches(0.9))
    run(para(tfi, first=True), ic, 26, accents[i], font=SANS)
    tbm, tfm = txt(s, cx + Inches(1.15), cy + Inches(0.3), cw - Inches(1.3), Inches(1.1),
                   anchor=MSO_ANCHOR.MIDDLE)
    p = para(tfm, first=True)
    run(p, k.upper(), 10, GREY, bold=True, font=MONO, spacing=1.5)
    p2 = tfm.add_paragraph(); p2.space_before = Pt(3)
    run(p2, v, 16, WHITE, bold=True, font=SANS)

# objective banner
banner = rect(s, Inches(0.85), Inches(5.65), Inches(11.6), Inches(1.0), BG_PANEL,
              shape=MSO_SHAPE.ROUNDED_RECTANGLE)
_round(banner, 0.08)
banner.line.color.rgb = CYAN
banner.line.width = Pt(1)
tbo, tfo = txt(s, Inches(1.2), Inches(5.8), Inches(11.0), Inches(0.8),
               anchor=MSO_ANCHOR.MIDDLE)
p = para(tfo, first=True)
run(p, "CORE OBJECTIVE   ", 12, CYAN, bold=True, font=MONO)
run(p, "Replace slow, centralized, forgery-prone verification with an immutable, "
       "globally verifiable on-chain ledger.", 14, WHITE, font=SANS)
footer(s)


# ----------------------------------------------------------------------------
# SLIDE 5 — Architectural Inventions
# ----------------------------------------------------------------------------
s = add_slide()
bg(s)
slide_header(s, "Architecture", "Advanced Inventions in V2.0", 5)

items = [
    ("{ } ", "String-to-Struct Mapping",
     "Records are keyed directly by the unique alphanumeric Registration Number "
     "(e.g. \"2021CSE101\") instead of numeric array indices.", CYAN),
    ("O(1)", "Constant-Time Lookups",
     "Moving from array loops to key-value mappings delivers O(1) retrieval — "
     "instant, scalable verification at any data volume.", GREEN),
    ("\u270D", "Manual Curation Paradigm",
     "Designed for registry officials to curate and cryptographically authorize "
     "verified student records directly onto the ledger.", BLUE),
    ("\U0001F512", "Role-Based Access Control",
     "Only the deployer wallet (University Admin) can write. Unauthorized writes "
     "are blocked at the EVM level via require assertions.", PURPLE),
]
cw = Inches(5.7)
ch = Inches(2.05)
gx = Inches(0.2)
gy = Inches(0.2)
x0 = Inches(0.85)
y0 = Inches(2.0)
for i, (tag, title, body, acc) in enumerate(items):
    col = i % 2
    row = i // 2
    cx = x0 + col * (cw + gx)
    cy = y0 + row * (ch + gy)
    card(s, cx, cy, cw, ch, acc)
    # tag badge
    badge = rect(s, cx + Inches(0.3), cy + Inches(0.32), Inches(0.95), Inches(0.6),
                 BG_CODE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    _round(badge, 0.2)
    badge.line.color.rgb = acc; badge.line.width = Pt(1)
    btf = badge.text_frame; btf.paragraphs[0].alignment = PP_ALIGN.CENTER
    btf.vertical_anchor = MSO_ANCHOR.MIDDLE
    run(btf.paragraphs[0], tag, 16, acc, bold=True, font=MONO)
    # title
    tbt, tft = txt(s, cx + Inches(1.45), cy + Inches(0.3), cw - Inches(1.7), Inches(0.7),
                   anchor=MSO_ANCHOR.MIDDLE)
    run(para(tft, first=True), title, 17, WHITE, bold=True, font=SANS)
    # body
    tbb, tfb = txt(s, cx + Inches(0.32), cy + Inches(1.05), cw - Inches(0.6), Inches(0.9))
    run(para(tfb, first=True), body, 12.5, GREY, font=SANS)
footer(s)


# ----------------------------------------------------------------------------
# SLIDE 6 — Smart Contract Codebase
# ----------------------------------------------------------------------------
s = add_slide()
bg(s)
slide_header(s, "Codebase", "The Smart Contract (Solidity)", 6)

# code window
win_x, win_y = Inches(0.85), Inches(1.8)
win_w, win_h = Inches(7.55), Inches(4.95)
window = rect(s, win_x, win_y, win_w, win_h, BG_CODE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
_round(window, 0.02)
window.line.color.rgb = RGBColor(0x26, 0x2E, 0x44); window.line.width = Pt(1)
# title bar
bar = rect(s, win_x, win_y, win_w, Inches(0.42), BG_PANEL, shape=MSO_SHAPE.ROUND_2_SAME_RECTANGLE)
_round(bar, 0.08)
for j, c in enumerate([RED, AMBER, GREEN]):
    rect(s, win_x + Inches(0.25) + j * Inches(0.28), win_y + Inches(0.14),
         Inches(0.13), Inches(0.13), c, shape=MSO_SHAPE.OVAL)
tbf, tff = txt(s, win_x + Inches(1.2), win_y + Inches(0.06), Inches(5.5), Inches(0.3))
run(para(tff, first=True), "AcademicCertificates.sol", 11, GREY, font=MONO)

# code lines: list of list of (text, color)
code = [
    [("// SPDX-License-Identifier: MIT", C_COMMENT)],
    [("pragma solidity ", C_KEYWORD), ("^0.8.0;", C_TYPE)],
    [("", C_PLAIN)],
    [("contract ", C_KEYWORD), ("AcademicCertificates", C_FUNC), (" {", C_PLAIN)],
    [("  struct ", C_KEYWORD), ("Certificate", C_TYPE), (" {", C_PLAIN)],
    [("    string", C_TYPE), (" studentName;", C_PLAIN)],
    [("    string", C_TYPE), (" courseName;", C_PLAIN)],
    [("    string", C_TYPE), (" ipfsHash;", C_PLAIN)],
    [("  }", C_PLAIN)],
    [("  // RegNo string -> Certificate  (O(1))", C_COMMENT)],
    [("  mapping", C_KEYWORD), ("(string => Certificate) ", C_PLAIN),
     ("public", C_KEYWORD), (" certificates;", C_PLAIN)],
    [("  uint256 ", C_TYPE), ("public totalIssued;", C_PLAIN)],
    [("  address ", C_TYPE), ("public university;", C_PLAIN)],
    [("", C_PLAIN)],
    [("  constructor", C_FUNC), ("() {", C_PLAIN)],
    [("    university = ", C_PLAIN), ("msg.sender", C_TYPE), (";", C_PLAIN)],
    [("  }", C_PLAIN)],
    [("", C_PLAIN)],
    [("  function ", C_KEYWORD), ("issueDegree", C_FUNC),
     ("(...) ", C_PLAIN), ("public", C_KEYWORD), (" {", C_PLAIN)],
    [("    require", C_FUNC), ("(msg.sender == university,", C_PLAIN)],
    [("      ", C_PLAIN), ("\"Only the University...\"", C_STRING), (");", C_PLAIN)],
    [("    certificates[_regNo] = ", C_PLAIN), ("Certificate", C_TYPE), ("(...);", C_PLAIN)],
    [("    totalIssued++;", C_PLAIN)],
    [("  }", C_PLAIN)],
    [("}", C_PLAIN)],
]
code_tb = slide_code_tb = s.shapes.add_textbox(win_x + Inches(0.3), win_y + Inches(0.55),
                                               win_w - Inches(0.5), win_h - Inches(0.7))
ctf = code_tb.text_frame
ctf.word_wrap = True
for i, line in enumerate(code):
    p = ctf.paragraphs[0] if i == 0 else ctf.add_paragraph()
    p.line_spacing = 1.0
    p.space_after = Pt(0)
    if not line or (len(line) == 1 and line[0][0] == ""):
        run(p, "\u200b", 10.5, C_PLAIN, font=MONO)
        continue
    for seg, col in line:
        run(p, seg, 10.5, col, font=MONO)

# right column: explanation of key elements
ex_x = Inches(8.65)
labels = [
    ("struct Certificate", "Bundles studentName, courseName & a hash-string field.", CYAN),
    ("mapping(string => …)", "Keyed by Registration Number for O(1) reads.", GREEN),
    ("university = msg.sender", "Deployer is the permanent immutable admin.", PURPLE),
    ("require(... == university)", "Blocks all unauthorized writes at EVM level.", RED),
    ("totalIssued++", "On-chain counter of all anchored degrees.", BLUE),
]
yy = Inches(1.9)
for name, desc, col in labels:
    card(s, ex_x, yy, Inches(3.8), Inches(0.9), col)
    tb, tf = txt(s, ex_x + Inches(0.25), yy + Inches(0.12), Inches(3.4), Inches(0.7))
    p = para(tf, first=True)
    run(p, name, 11.5, col, bold=True, font=MONO)
    p2 = tf.add_paragraph(); p2.space_before = Pt(1)
    run(p2, desc, 10.5, GREY, font=SANS)
    yy = yy + Inches(0.97)
footer(s)


# ----------------------------------------------------------------------------
# SLIDE 7 — Frontend Architecture
# ----------------------------------------------------------------------------
s = add_slide()
bg(s)
slide_header(s, "Frontend", "Application Layout & Engine", 7)

# index.html card
hx = Inches(0.85)
card(s, hx, Inches(1.95), Inches(5.7), Inches(4.6), CYAN)
tb, tf = txt(s, hx + Inches(0.35), Inches(2.2), Inches(5.0), Inches(0.6))
p = para(tf, first=True)
run(p, "index.html ", 18, WHITE, bold=True, font=MONO)
run(p, "— Interface Engine", 13, GREY, font=SANS)
tb, tf = txt(s, hx + Inches(0.35), Inches(2.85), Inches(5.0), Inches(0.6))
run(para(tf, first=True),
    "Responsive Web3 dashboard with a sleek low-light terminal layout.", 12.5, GREY, font=SANS)
rows_html = [
    ("#regInput", "Alphanumeric entry gate — captures string keys", CYAN),
    ("verifyCertificate()", "onclick trigger event fires the lookup", GREEN),
    ("#result", "Contextual output display element", BLUE),
    (".loading / .success / .error", "Dynamic CSS state selectors", PURPLE),
]
yy = Inches(3.45)
for name, desc, col in rows_html:
    rect(s, hx + Inches(0.35), yy + Inches(0.07), Inches(0.09), Inches(0.55), col)
    tb, tf = txt(s, hx + Inches(0.6), yy, Inches(4.8), Inches(0.8))
    p = para(tf, first=True)
    run(p, name, 12.5, col, bold=True, font=MONO)
    p2 = tf.add_paragraph(); p2.space_before = Pt(1)
    run(p2, desc, 11.5, GREY, font=SANS)
    yy = yy + Inches(0.75)

# script.js card
sx = Inches(6.75)
card(s, sx, Inches(1.95), Inches(5.7), Inches(4.6), AMBER)
tb, tf = txt(s, sx + Inches(0.35), Inches(2.2), Inches(5.0), Inches(0.6))
p = para(tf, first=True)
run(p, "script.js ", 18, WHITE, bold=True, font=MONO)
run(p, "— Script Engine", 13, GREY, font=SANS)
tb, tf = txt(s, sx + Inches(0.35), Inches(2.85), Inches(5.0), Inches(0.6))
run(para(tf, first=True),
    "Connects to MetaMask via Ethers.js and queries on-chain state.", 12.5, GREY, font=SANS)
rows_js = [
    ("Web3Provider(window.ethereum)", "Client-side MetaMask provider bridge", AMBER),
    ("contract.certificates(regNo)", "Core gasless view call to the contract", GREEN),
    ("ABI array + struct destructuring", "Decodes returned EVM struct properties", BLUE),
    ("Safety filter on studentName", "Blank/undefined \u2192 \"Record Not Found\"", RED),
]
yy = Inches(3.45)
for name, desc, col in rows_js:
    rect(s, sx + Inches(0.35), yy + Inches(0.07), Inches(0.09), Inches(0.55), col)
    tb, tf = txt(s, sx + Inches(0.6), yy, Inches(4.8), Inches(0.8))
    p = para(tf, first=True)
    run(p, name, 12, col, bold=True, font=MONO)
    p2 = tf.add_paragraph(); p2.space_before = Pt(1)
    run(p2, desc, 11.5, GREY, font=SANS)
    yy = yy + Inches(0.75)
footer(s)


# ----------------------------------------------------------------------------
# SLIDE 8 — System Dataflow Lifecycle
# ----------------------------------------------------------------------------
s = add_slide()
bg(s)
slide_header(s, "Lifecycle", "System Dataflow: From Code to Verification", 8)

steps = [
    ("01", "Compilation", "Solidity \u2192 EVM bytecode + ABI JSON interface.", CYAN),
    ("02", "Deployment", "Admin signs a contract-creation tx (blank \"To\"), pays gas to Sepolia.", BLUE),
    ("03", "Record Issuance", "Admin writes a record; MetaMask signs, gas burned, data mined.", PURPLE),
    ("04", "Verification", "Verifier enters RegNo \u2192 gasless view call returns the record instantly.", GREEN),
]
n = len(steps)
cw = Inches(2.78)
gap = Inches(0.34)
x0 = Inches(0.85)
y0 = Inches(2.4)
ch = Inches(3.0)
for i, (num, title, body, acc) in enumerate(steps):
    cx = x0 + i * (cw + gap)
    card(s, cx, y0, cw, ch, acc)
    # big number
    tb, tf = txt(s, cx + Inches(0.28), y0 + Inches(0.3), cw - Inches(0.5), Inches(0.9))
    run(para(tf, first=True), num, 40, acc, bold=True, font=MONO)
    # title
    tb, tf = txt(s, cx + Inches(0.28), y0 + Inches(1.25), cw - Inches(0.5), Inches(0.6))
    run(para(tf, first=True), title, 16, WHITE, bold=True, font=SANS)
    # body
    tb, tf = txt(s, cx + Inches(0.28), y0 + Inches(1.85), cw - Inches(0.5), Inches(1.0))
    run(para(tf, first=True), body, 12, GREY, font=SANS)
    # arrow between cards
    if i < n - 1:
        ar = s.shapes.add_shape(MSO_SHAPE.CHEVRON,
                                cx + cw + Inches(0.04), y0 + Inches(1.25),
                                Inches(0.28), Inches(0.4))
        ar.fill.solid(); ar.fill.fore_color.rgb = DARKGREY
        ar.line.fill.background(); ar.shadow.inherit = False

# write vs read legend
tb, tf = txt(s, Inches(0.85), Inches(5.7), Inches(11.6), Inches(0.6))
p = para(tf, first=True)
run(p, "\u25CF WRITE  ", 13, AMBER, bold=True, font=SANS)
run(p, "(state mutation · costs gas)        ", 13, GREY, font=SANS)
run(p, "\u25CF READ  ", 13, GREEN, bold=True, font=SANS)
run(p, "(view call · gasless · instant)", 13, GREY, font=SANS)
footer(s)


# ----------------------------------------------------------------------------
# SLIDE 9 — Read Step deep dive (Client-side verification)
# ----------------------------------------------------------------------------
s = add_slide()
bg(s)
slide_header(s, "Read Path", "Client-Side Verification Flow", 9)

flow = [
    ("\U0001F464", "Verifier enters RegNo", "Alphanumeric string typed into #regInput.", CYAN),
    ("\u26A1", "Ethers.js view call", "contract.certificates(regNo) — free & gasless.", BLUE),
    ("\U0001F5C2", "EVM checks keyspace", "Mapping resolves the storage slot in O(1).", PURPLE),
    ("\u2705", "Render result", "Struct destructured & shown in #result panel.", GREEN),
]
yy = Inches(2.0)
for ic, title, body, acc in flow:
    bar = rect(s, Inches(0.85), yy, Inches(6.6), Inches(1.0), BG_PANEL,
               shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    _round(bar, 0.08)
    rect(s, Inches(0.85), yy, Inches(0.1), Inches(1.0), acc)
    tb, tf = txt(s, Inches(1.15), yy + Inches(0.18), Inches(0.8), Inches(0.7))
    run(para(tf, first=True), ic, 26, acc, font=SANS)
    tb, tf = txt(s, Inches(2.0), yy + Inches(0.16), Inches(5.2), Inches(0.8),
                 anchor=MSO_ANCHOR.MIDDLE)
    p = para(tf, first=True)
    run(p, title, 15, WHITE, bold=True, font=SANS)
    p2 = tf.add_paragraph(); p2.space_before = Pt(2)
    run(p2, body, 12, GREY, font=SANS)
    yy = yy + Inches(1.16)

# right: result panel mock (success + error states)
rx = Inches(7.9)
# success state
suc = card(s, rx, Inches(2.0), Inches(4.55), Inches(2.05), GREEN)
tb, tf = txt(s, rx + Inches(0.3), Inches(2.2), Inches(4.0), Inches(1.7))
p = para(tf, first=True)
run(p, "#result", 11, GREEN, bold=True, font=MONO)
run(p, "  .success", 11, DARKGREY, font=MONO)
p = tf.add_paragraph(); p.space_before = Pt(6)
run(p, "\u2713 Certificate Verified", 16, WHITE, bold=True, font=SANS)
p = tf.add_paragraph(); p.space_before = Pt(4)
run(p, "Name · Course · hash-string field", 12, GREY, font=SANS)

# error state
err = card(s, rx, Inches(4.25), Inches(4.55), Inches(2.05), RED)
tb, tf = txt(s, rx + Inches(0.3), Inches(4.45), Inches(4.0), Inches(1.7))
p = para(tf, first=True)
run(p, "#result", 11, RED, bold=True, font=MONO)
run(p, "  .error", 11, DARKGREY, font=MONO)
p = tf.add_paragraph(); p.space_before = Pt(6)
run(p, "\u2715 Record Not Found", 16, WHITE, bold=True, font=SANS)
p = tf.add_paragraph(); p.space_before = Pt(4)
run(p, "Triggered when studentName is blank / undefined.", 12, GREY, font=SANS)
footer(s)


# ----------------------------------------------------------------------------
# SLIDE 10 — Tech Stack & Benefits
# ----------------------------------------------------------------------------
s = add_slide()
bg(s)
slide_header(s, "Summary", "Technology Stack & Key Benefits", 10)

# left: stack
tb, tf = txt(s, Inches(0.85), Inches(1.95), Inches(5.6), Inches(0.5))
run(para(tf, first=True), "TECHNOLOGY STACK", 13, CYAN, bold=True, font=MONO, spacing=1.5)
stack = [
    ("Smart Contract", "Solidity ^0.8.0", CYAN),
    ("Blockchain", "Ethereum / Sepolia Testnet (EVM)", BLUE),
    ("Web3 Library", "Ethers.js", PURPLE),
    ("Wallet / Signer", "MetaMask", AMBER),
    ("Data Fingerprint", "Manual mock string (IPFS/SHA-256 in P2)", GREEN),
    ("Frontend", "HTML · CSS · JavaScript", RED),
]
yy = Inches(2.5)
for k, v, col in stack:
    rect(s, Inches(0.85), yy + Inches(0.05), Inches(0.09), Inches(0.5), col)
    tb, tf = txt(s, Inches(1.1), yy, Inches(5.3), Inches(0.6))
    p = para(tf, first=True)
    run(p, k + "  ", 13, WHITE, bold=True, font=SANS)
    p2 = tf.add_paragraph(); p2.space_before = Pt(0)
    run(p2, v, 12, GREY, font=MONO)
    yy = yy + Inches(0.66)

# right: benefits
tb, tf = txt(s, Inches(6.95), Inches(1.95), Inches(5.6), Inches(0.5))
run(para(tf, first=True), "KEY BENEFITS", 13, GREEN, bold=True, font=MONO, spacing=1.5)
benefits = [
    ("Immutable & tamper-proof records", CYAN),
    ("O(1) constant-time verification", GREEN),
    ("Zero-latency, 24/7 global access", BLUE),
    ("No single point of failure", PURPLE),
    ("Gasless reads for verifiers", AMBER),
    ("Admin-only writes via strict RBAC", RED),
]
yy = Inches(2.5)
for b, col in benefits:
    bar = rect(s, Inches(6.95), yy, Inches(5.5), Inches(0.55), BG_PANEL,
               shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    _round(bar, 0.25)
    tb, tf = txt(s, Inches(7.2), yy + Inches(0.02), Inches(5.1), Inches(0.5),
                 anchor=MSO_ANCHOR.MIDDLE)
    p = para(tf, first=True)
    run(p, "\u2713  ", 13, col, bold=True, font=SANS)
    run(p, b, 13, WHITE, font=SANS)
    yy = yy + Inches(0.66)
footer(s)


# ----------------------------------------------------------------------------
# SLIDE 11 — Closing
# ----------------------------------------------------------------------------
s = add_slide()
bg(s)
rect(s, Inches(0), Inches(0), Inches(0.18), SH, CYAN)
for (gx, gy, c) in [
    (Inches(11.6), Inches(1.0), CYAN),
    (Inches(12.2), Inches(1.8), BLUE),
    (Inches(1.0), Inches(6.2), PURPLE),
]:
    rect(s, gx, gy, Inches(0.16), Inches(0.16), c, shape=MSO_SHAPE.OVAL)

tb, tf = txt(s, Inches(1.0), Inches(2.55), Inches(11.3), Inches(1.6))
p = para(tf, first=True)
run(p, "Trust, ", 50, WHITE, bold=True, font=SANS)
run(p, "anchored on-chain.", 50, CYAN, bold=True, font=SANS)
tb, tf = txt(s, Inches(1.0), Inches(3.95), Inches(11.0), Inches(1.0))
p = para(tf, first=True)
run(p, "UniVerify V2.0 turns certificate verification from a multi-day, forgery-prone "
       "process into an instant, immutable, decentralized lookup.", 17, GREY, font=SANS_LIGHT)

rect(s, Inches(1.0), Inches(5.2), Inches(3.2), Inches(0.03), CYAN)
tb, tf = txt(s, Inches(1.0), Inches(5.45), Inches(11), Inches(0.6))
p = para(tf, first=True)
run(p, "Thank you", 22, WHITE, bold=True, font=SANS)
tb, tf = txt(s, Inches(1.0), Inches(6.05), Inches(11), Inches(0.5))
p = para(tf, first=True)
run(p, "UniVerify V2.0  ·  Web3 Academic Certificate Verification  ·  Sepolia Testnet",
    12, DARKGREY, font=MONO)


prs.save("UniVerify_V2.0.pptx")
print("Saved UniVerify_V2.0.pptx with", len(prs.slides._sldIdLst), "slides")
