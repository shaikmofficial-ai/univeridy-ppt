#!/usr/bin/env python3
"""
Generator for the "UniVerify V2.0" publication-grade PDF dossier.

Built with reportlab as an 11-page, landscape 16:9, dark Web3 / terminal-themed
deck. Content is corrected to reflect the true Phase-1 (current, third-year)
scope: data is entered MANUALLY in the Remix IDE, and the `ipfsHash` struct
field currently stores a manually-typed alphanumeric MOCK placeholder string.
Deterministic SHA-256 / IPFS content-hashing is explicitly deferred to
Phase 2 (final-year automation roadmap).

Coordinate convention: every helper takes (x, y) as the TOP-LEFT origin and
measures y DOWNWARD from the top of the page, then converts to reportlab's
bottom-left native system internally.
"""

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase.pdfmetrics import stringWidth

# ---------------------------------------------------------------- page geometry
W, H = 960.0, 540.0            # 16:9 (points) == 13.33in x 7.5in
PAGE = (W, H)
TOTAL = 11

# ----------------------------------------------------------------------- palette
BG_DARK  = HexColor("#0A0E1A")
BG_PANEL = HexColor("#12182B")
BG_CODE  = HexColor("#05090F")
PANEL_LN = HexColor("#262E44")
CYAN     = HexColor("#00E5C7")
BLUE     = HexColor("#4D8CFF")
PURPLE   = HexColor("#9B6DFF")
GREEN    = HexColor("#3DDC84")
RED      = HexColor("#FF5C5C")
AMBER    = HexColor("#FFB34D")
WHITE    = HexColor("#F2F5FA")
GREY     = HexColor("#9AA6C0")
DARKGREY = HexColor("#5A6680")

C_KEYWORD = HexColor("#C592FF")
C_TYPE    = HexColor("#66D9EF")
C_STRING  = HexColor("#E6DB74")
C_COMMENT = HexColor("#6A7388")
C_FUNC    = HexColor("#3DDC84")
C_PLAIN   = HexColor("#E6EAF2")

# Fonts (built-in, no embedding required)
SANS   = "Helvetica"
SANSB  = "Helvetica-Bold"
SANSO  = "Helvetica-Oblique"
MONO   = "Courier"
MONOB  = "Courier-Bold"

c = canvas.Canvas("UniVerify_V2.0.pdf", pagesize=PAGE)
c.setTitle("UniVerify V2.0 - Decentralized Academic Certificate Verification Protocol")
c.setAuthor("UniVerify V2.0 - B.Tech CSE Capstone")
c.setSubject("Decentralized Ledger Technology / Smart Contract Engineering")


# --------------------------------------------------------------------- helpers
def fill_page(color=BG_DARK):
    c.setFillColor(color)
    c.rect(0, 0, W, H, stroke=0, fill=1)


def box(x, y, w, h, fill=None, stroke=None, sw=1.0, r=None):
    """Rectangle using top-left origin. y measured downward from page top."""
    ry = H - y - h
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke)
        c.setLineWidth(sw)
    do_fill = 1 if fill is not None else 0
    do_stroke = 1 if stroke is not None else 0
    if r:
        c.roundRect(x, ry, w, h, r, stroke=do_stroke, fill=do_fill)
    else:
        c.rect(x, ry, w, h, stroke=do_stroke, fill=do_fill)


def dot(x, y, d, color):
    c.setFillColor(color)
    c.circle(x + d / 2.0, H - y - d / 2.0, d / 2.0, stroke=0, fill=1)


def hline(x, y, w, color, sw=1.0):
    c.setStrokeColor(color)
    c.setLineWidth(sw)
    c.line(x, H - y, x + w, H - y)


def _tracked_width(s, font, size, tracking):
    return stringWidth(s, font, size) + tracking * max(0, len(s) - 1)


def text(x, y, s, font=SANS, size=12, color=WHITE, align="left", tracking=0.0):
    """Draw a single line. y is the TOP of the cap height."""
    baseline = H - y - size * 0.82
    if tracking:
        # letter-spacing requires a text object (canvas has no setCharSpace)
        sx = x
        w = _tracked_width(s, font, size, tracking)
        if align == "center":
            sx = x - w / 2.0
        elif align == "right":
            sx = x - w
        to = c.beginText()
        to.setTextOrigin(sx, baseline)
        to.setFont(font, size)
        to.setFillColor(color)
        to.setCharSpace(tracking)
        to.textOut(s)
        c.drawText(to)
        return
    c.setFillColor(color)
    c.setFont(font, size)
    if align == "center":
        c.drawCentredString(x, baseline, s)
    elif align == "right":
        c.drawRightString(x, baseline, s)
    else:
        c.drawString(x, baseline, s)


def para(x, y, w, s, font=SANS, size=12, color=GREY, leading=None, align="left",
         max_lines=None):
    """Word-wrapped paragraph. Returns y position just below the last line."""
    if leading is None:
        leading = size * 1.32
    lines = simpleSplit(s, font, size, w)
    if max_lines:
        lines = lines[:max_lines]
    cy = y
    for ln in lines:
        text(x, cy, ln, font=font, size=size, color=color, align=align)
        cy += leading
    return cy


def bullet(x, y, w, marker, marker_color, s, body_color=GREY, size=12,
           font=SANS, leading=None, gap=14):
    """A bullet/▶ marker followed by a wrapped paragraph indented past it."""
    text(x, y, marker, font=SANSB, size=size, color=marker_color)
    return para(x + gap, y, w - gap, s, font=font, size=size, color=body_color,
                leading=leading)


def header(kicker, title, num, sub=None):
    box(40, 34, 6, 66, fill=CYAN)
    text(58, 36, kicker.upper(), font=SANSB, size=11, color=CYAN, tracking=2.2)
    text(57, 54, title, font=SANSB, size=25, color=WHITE)
    if sub:
        text(58, 86, sub, font=SANS, size=12.5, color=GREY)
    text(W - 44, 40, f"{num:02d}", font=MONOB, size=12, color=DARKGREY, align="right")
    text(W - 44, 40, f"        / {TOTAL}", font=MONO, size=12, color=DARKGREY,
         align="right")


def footer():
    text(58, 512, "UniVerify V2.0", font=MONOB, size=8.5, color=CYAN)
    text(150, 512, "Decentralized Academic Certificate Verification Protocol  |  "
                   "B.Tech CSE Capstone", font=SANS, size=8.5, color=DARKGREY)
    text(W - 44, 512, "Phase 1 - Production Ledger Prototype", font=MONO, size=8.5,
         color=DARKGREY, align="right")


def card(x, y, w, h, accent, r=10):
    box(x, y, w, h, fill=BG_PANEL, r=r)
    box(x, y, w, 5, fill=accent)              # top accent edge
    box(x, y, w, 5, fill=accent, r=2)


def left_accent_card(x, y, w, h, accent, r=10):
    box(x, y, w, h, fill=BG_PANEL, r=r)
    box(x, y, 6, h, fill=accent)


def chip(x, y, label, color, w=150, h=26):
    box(x, y, w, h, fill=BG_PANEL, stroke=color, sw=1.0, r=h / 2.0)
    text(x + w / 2.0, y + 7, label, font=SANSB, size=10.5, color=color,
         align="center")


def badge(x, y, w, h, label, color):
    box(x, y, w, h, fill=BG_CODE, stroke=color, sw=1.0, r=6)
    c.setFont(MONOB, 14)
    c.setFillColor(color)
    c.drawCentredString(x + w / 2.0, H - y - h / 2.0 - 5, label)


# ============================================================================
# PAGE 1 — Title
# ============================================================================
fill_page()
box(0, 0, 9, H, fill=CYAN)
for (gx, gy, col, d) in [(820, 70, BLUE, 12), (876, 120, CYAN, 11),
                         (786, 150, PURPLE, 9), (60, 430, CYAN, 11),
                         (110, 470, BLUE, 9), (892, 360, GREEN, 9)]:
    dot(gx, gy, d, col)

text(72, 120, "WEB3   .   DLT   .   SMART-CONTRACT ENGINEERING   .   "
              "ROLE-BASED CRYPTOGRAPHY", font=SANSB, size=12, color=CYAN, tracking=2.4)

text(70, 160, "UniVerify", font=SANSB, size=70, color=WHITE)
text(395, 160, "V2.0", font=SANSB, size=70, color=CYAN)

para(72, 250, 760,
     "A Decentralized Academic Certificate Verification Protocol Using "
     "Alphanumeric Keyspace Mapping", font=SANS, size=21, color=GREY, leading=28)

hline(74, 340, 230, CYAN, 2)

text(72, 356, "B.Tech (Computer Science & Engineering)  |  Final-Year Capstone Project",
     font=SANSB, size=13, color=WHITE)
para(72, 380, 800,
     "An immutable, globally accessible, zero-latency ledger that supersedes "
     "centralized RDBMS verification pipelines.", font=SANS, size=12.5, color=GREY)

chip(72, 430, "Solidity v0.8.0", CYAN, w=150)
chip(232, 430, "Ethers.js v5.7.2", BLUE, w=160)
chip(402, 430, "MetaMask Web3 Provider", PURPLE, w=210)
chip(622, 430, "Ethereum Sepolia Testnet", GREEN, w=210)

text(72, 478, "PHASE 1 - PRODUCTION LEDGER PROTOTYPE  (Manual Administrative "
              "Curation via Remix IDE)", font=MONOB, size=10.5, color=AMBER,
     tracking=0.5)
c.showPage()


# ============================================================================
# PAGE 2 — Abstract & Problem Statement
# ============================================================================
fill_page()
header("Abstract", "Problem Statement & Motivation", 2)

para(58, 120, 844,
     "Conventional academic record tracking relies entirely on centralized "
     "relational database management systems (RDBMS) or legacy physical paper "
     "trails. Such architectures concentrate trust in a single authority, "
     "introducing systemic fragility across security, latency, and integrity "
     "dimensions.", font=SANS, size=13, color=GREY, leading=18)

cards = [
    ("SINGLE POINT OF FAILURE",
     "Centralized servers are exposed to malicious insider modification, "
     "external breaches, and downtime - a structural SPOF risk.", RED),
    ("HIGH VERIFICATION LATENCY",
     "Manual lookups incur a 7-14 day turnaround, throttling admissions, "
     "recruitment, and onboarding workflows.", AMBER),
    ("RECURRING ADMINISTRATIVE COST",
     "Redundant manual institutional audits impose substantial, continuous "
     "operational overhead.", BLUE),
    ("TRIVIAL CREDENTIAL FORGERY",
     "Unanchored PDFs and physical assets are visually falsifiable; forgery "
     "detection is near-impossible without cross-checks.", PURPLE),
]
cw, ch, gap, x0, y0 = 210, 190, 16, 58, 196
for i, (t, b, acc) in enumerate(cards):
    cx = x0 + i * (cw + gap)
    card(cx, y0, cw, ch, acc)
    box(cx + 18, y0 + 26, 34, 4, fill=acc)
    para(cx + 18, y0 + 44, cw - 36, t, font=SANSB, size=12.5, color=WHITE, leading=16)
    para(cx + 18, y0 + 92, cw - 36, b, font=SANS, size=11, color=GREY, leading=15)

box(58, 410, 844, 78, fill=BG_PANEL, stroke=CYAN, sw=1.0, r=10)
text(76, 426, "RESEARCH OBJECTIVE", font=MONOB, size=11, color=CYAN, tracking=1.2)
para(76, 446, 808,
     "Engineer a trust-minimized verification protocol that anchors certificate "
     "records to a public EVM ledger - rendering them immutable, globally "
     "queryable, and verifiable in constant time without a centralized "
     "intermediary.", font=SANS, size=12.5, color=WHITE, leading=17)
footer()
c.showPage()


# ============================================================================
# PAGE 3 — Solution & System Metadata
# ============================================================================
fill_page()
header("Overview", "Proposed Solution & System Specification", 3)

# left: narrative
text(58, 122, "ARCHITECTURAL THESIS", font=MONOB, size=11, color=CYAN, tracking=1.2)
yy = para(58, 144, 430,
          "UniVerify V2.0 anchors academic credentials directly onto the public "
          "Ethereum Sepolia Testnet. Once a record is mined, its state becomes "
          "cryptographically immutable and globally readable.", font=SANS,
          size=12.5, color=GREY, leading=17)
yy += 6
for label, desc, col in [
    ("Immutability", "Mined state cannot be retroactively altered or deleted.", CYAN),
    ("Global Availability", "Permissionless read access, 24x7, with no host server.", BLUE),
    ("Zero-Latency Reads", "Verification resolves in seconds via a gasless view call.", GREEN),
    ("Tamper-Evidence", "On-chain anchoring defeats document-level forgery.", PURPLE),
]:
    text(58, yy, "\u25B6", font=SANSB, size=10, color=col)
    text(76, yy, label + " - ", font=SANSB, size=12, color=col)
    wlab = stringWidth(label + " - ", SANSB, 12)
    para(76 + wlab, yy, 412 - wlab, desc, font=SANS, size=12, color=GREY,
         leading=15, max_lines=2)
    yy += 34

# right: metadata grid
meta = [
    ("PROJECT", "UniVerify V2.0", CYAN),
    ("DOMAIN", "DLT . Web3 . RBAC", BLUE),
    ("CONTRACT", "Solidity v0.8.0", PURPLE),
    ("NETWORK", "Sepolia Testnet (EVM)", GREEN),
    ("WEB3 LIB", "Ethers.js v5.7.2", AMBER),
    ("SIGNER", "MetaMask Provider", RED),
]
gx0, gy0, gw, gh, ggx, ggy = 520, 132, 185, 92, 14, 14
for i, (k, v, acc) in enumerate(meta):
    col = i % 2
    row = i // 2
    cx = gx0 + col * (gw + ggx)
    cy = gy0 + row * (gh + ggy)
    left_accent_card(cx, cy, gw, gh, acc)
    text(cx + 20, cy + 20, k, font=MONOB, size=9.5, color=GREY, tracking=1.2)
    para(cx + 20, cy + 40, gw - 36, v, font=SANSB, size=14.5, color=WHITE, leading=18)

box(58, 452, 844, 56, fill=BG_PANEL, stroke=GREEN, sw=1.0, r=10)
text(76, 466, "NET EFFECT", font=MONOB, size=10.5, color=GREEN, tracking=1.2)
para(168, 463, 716,
     "A 7-14 day, forgery-prone, centralized pipeline collapses into an instant, "
     "tamper-evident, decentralized O(1) lookup.", font=SANS, size=12.5,
     color=WHITE, leading=16)
footer()
c.showPage()


# ============================================================================
# PAGE 4 — Phased Implementation Framework  (KEY CORRECTION)
# ============================================================================
fill_page()
header("Methodology", "Two-Tier Phased Implementation Framework", 4,
       sub="Core verification logic is decoupled from automated transactional ingestion.")

# Phase 1 card (current)
p1x, p1w = 58, 414
card(p1x, 128, p1w, 350, CYAN)
text(p1x + 22, 150, "PHASE 1", font=MONOB, size=12, color=CYAN, tracking=1.5)
chip(p1x + p1w - 150, 146, "CURRENT - 3RD YEAR", GREEN, w=132, h=22)
text(p1x + 22, 178, "Production Ledger Prototype", font=SANSB, size=16, color=WHITE)
para(p1x + 22, 204, p1w - 44,
     "Operates on a Manual Administrative Curation Paradigm to stress-test and "
     "validate state mutability, permission guardrails, and read-path latency.",
     font=SANS, size=11.5, color=GREY, leading=16)
p1items = [
    "Registry Admin manually inputs records via the Remix IDE transaction dashboard.",
    "Fields entered by hand: Alphanumeric Reg. No., Full Name, Course Name.",
    "The hash field is a MANUALLY-TYPED alphanumeric MOCK string - a data-"
    "fingerprint placeholder only. No file is uploaded or hashed.",
    "Objective: cryptographically validate contract logic, not production hashing.",
]
yy = 262
for it in p1items:
    text(p1x + 22, yy, "\u2713", font=SANSB, size=11, color=CYAN)
    yy = para(p1x + 40, yy, p1w - 62, it, font=SANS, size=11, color=GREY,
              leading=14.5) + 8

# Phase 2 card (future)
p2x, p2w = 488, 414
card(p2x, 128, p2w, 350, PURPLE)
text(p2x + 22, 150, "PHASE 2", font=MONOB, size=12, color=PURPLE, tracking=1.5)
chip(p2x + p2w - 168, 146, "ROADMAP - FINAL YEAR", AMBER, w=150, h=22)
text(p2x + 22, 178, "Autonomous AI Agent Orchestration", font=SANSB, size=16, color=WHITE)
para(p2x + 22, 204, p2w - 44,
     "A server-side Python / Node execution layer runs an autonomous agent that "
     "removes the human-in-the-loop bottleneck entirely.", font=SANS, size=11.5,
     color=GREY, leading=16)
p2items = [
    "Ingests unstructured raw student logs and runs NLP normalization pipelines.",
    "Natively computes a deterministic SHA-256 / IPFS file-blob content hash.",
    "Signs & broadcasts state-changing transactions via Web3.py / Ethers.js using "
    "its own secure wallet.",
    "Real cryptographic certificate hashing is introduced HERE - not in Phase 1.",
]
yy = 262
for it in p2items:
    text(p2x + 22, yy, "\u25B8", font=SANSB, size=11, color=PURPLE)
    yy = para(p2x + 40, yy, p2w - 62, it, font=SANS, size=11, color=GREY,
              leading=14.5) + 8

footer()
c.showPage()


# ============================================================================
# PAGE 5 — Algorithmic Inventions
# ============================================================================
fill_page()
header("Contributions", "Algorithmic Inventions & Complexity Metrics", 5)

items = [
    ("{ }", "Alphanumeric Keyspace Mapping",
     "State is bound via mapping(string => Certificate), keyed by the unique "
     "Registration Number string (e.g. \"2021CSE101\") rather than sequential "
     "uint256 array indices.", CYAN),
    ("O(1)", "Constant-Time Retrieval",
     "The keyspace structure bypasses iteration loops entirely, collapsing "
     "lookups from O(N) linear scans to flat O(1) constant time at any record "
     "volume.", GREEN),
    ("RBAC", "EVM-Layer Access Control",
     "The constructor freezes the deployer address as the immutable admin. "
     "Unauthorized writes are reverted by require() before gas is committed to "
     "an invalid block.", PURPLE),
    ("GAS", "Write/Read Cost Asymmetry",
     "State mutations (issueDegree) incur gas; verification view calls read an "
     "existing storage slot and therefore cost zero gas.", AMBER),
]
cw, ch, gx, gy, x0, y0 = 410, 158, 16, 16, 58, 124
for i, (tag, title, body, acc) in enumerate(items):
    col = i % 2
    row = i // 2
    cx = x0 + col * (cw + gx)
    cy = y0 + row * (ch + gy)
    card(cx, cy, cw, ch, acc)
    badge(cx + 22, cy + 26, 62, 44, tag, acc)
    text(cx + 100, cy + 36, title, font=SANSB, size=14.5, color=WHITE)
    para(cx + 100, cy + 62, cw - 120, body, font=SANS, size=11, color=GREY, leading=14.5)

# complexity comparison strip
box(58, 462, 844, 46, fill=BG_PANEL, stroke=PANEL_LN, sw=1.0, r=10)
text(76, 476, "COMPLEXITY", font=MONOB, size=10, color=GREY, tracking=1.0)
text(190, 474, "Array indexing:", font=SANS, size=12, color=GREY)
text(300, 474, "O(N)", font=MONOB, size=13, color=RED)
text(360, 474, "linear scan, gas grows with N", font=SANS, size=11, color=DARKGREY)
text(600, 474, "Keyspace mapping:", font=SANS, size=12, color=GREY)
text(728, 474, "O(1)", font=MONOB, size=13, color=GREEN)
text(788, 474, "constant, flat cost", font=SANS, size=11, color=DARKGREY)
footer()
c.showPage()


# ============================================================================
# PAGE 6 — Smart Contract Source Engine
# ============================================================================
fill_page()
header("Implementation", "Smart Contract Source Engine", 6)

# code window
wx, wy, ww, wh = 58, 120, 560, 388
box(wx, wy, ww, wh, fill=BG_CODE, stroke=PANEL_LN, sw=1.0, r=8)
box(wx, wy, ww, 30, fill=BG_PANEL, r=8)
box(wx, wy + 20, ww, 10, fill=BG_PANEL)
for j, col in enumerate([RED, AMBER, GREEN]):
    dot(wx + 16 + j * 18, wy + 11, 9, col)
text(wx + 78, wy + 9, "AcademicCertificates.sol", font=MONO, size=10, color=GREY)

code = [
    [("// SPDX-License-Identifier: MIT", C_COMMENT)],
    [("pragma solidity ", C_KEYWORD), ("^0.8.0;", C_TYPE)],
    [("", C_PLAIN)],
    [("contract ", C_KEYWORD), ("AcademicCertificates", C_FUNC), (" {", C_PLAIN)],
    [("    struct ", C_KEYWORD), ("Certificate", C_TYPE), (" {", C_PLAIN)],
    [("        string ", C_TYPE), ("studentName;", C_PLAIN)],
    [("        string ", C_TYPE), ("courseName;", C_PLAIN)],
    [("        string ", C_TYPE), ("ipfsHash;", C_PLAIN),
     ("   // mock placeholder (P1)", C_COMMENT)],
    [("    }", C_PLAIN)],
    [("", C_PLAIN)],
    [("    // RegNo string key -> O(1) lookup", C_COMMENT)],
    [("    mapping", C_KEYWORD), ("(string => Certificate) ", C_PLAIN)],
    [("        public", C_KEYWORD), (" certificates;", C_PLAIN)],
    [("    uint256 ", C_TYPE), ("public totalIssued;", C_PLAIN)],
    [("    address ", C_TYPE), ("public university;", C_PLAIN)],
    [("", C_PLAIN)],
    [("    constructor", C_FUNC), ("() {", C_PLAIN)],
    [("        university = ", C_PLAIN), ("msg.sender", C_TYPE), (";", C_PLAIN)],
    [("    }", C_PLAIN)],
    [("", C_PLAIN)],
    [("    function ", C_KEYWORD), ("issueDegree", C_FUNC), ("(", C_PLAIN)],
    [("        string memory ", C_TYPE), ("_regNo, _name,", C_PLAIN)],
    [("        string memory ", C_TYPE), ("_course, _hash", C_PLAIN)],
    [("    ) ", C_PLAIN), ("public", C_KEYWORD), (" {", C_PLAIN)],
    [("        require", C_FUNC), ("(msg.sender == university,", C_PLAIN)],
    [("            ", C_PLAIN), ("\"Only the University...\"", C_STRING), (");", C_PLAIN)],
    [("        certificates[_regNo] =", C_PLAIN)],
    [("            ", C_PLAIN), ("Certificate", C_TYPE), ("(_name,_course,_hash);", C_PLAIN)],
    [("        totalIssued++;", C_PLAIN)],
    [("    }", C_PLAIN)],
    [("}", C_PLAIN)],
]
cx0 = wx + 16
cy0 = wy + 42
lh = 11.0
c.setFont(MONO, 8.6)
for i, line in enumerate(code):
    yb = H - (cy0 + i * lh) - 8.6
    # line number gutter
    c.setFillColor(HexColor("#2C3550"))
    c.setFont(MONO, 8.0)
    c.drawRightString(cx0 + 14, yb, str(i + 1))
    cur = cx0 + 24
    c.setFont(MONO, 8.6)
    for seg, col in line:
        if seg == "":
            continue
        c.setFillColor(col)
        c.drawString(cur, yb, seg)
        cur += stringWidth(seg, MONO, 8.6)

# right annotations
ax, aw = 636, 266
notes = [
    ("struct Certificate", "Packs studentName, courseName & a hash-string field "
     "into one EVM storage record.", CYAN),
    ("mapping(string=>...)", "Reg. No. string is the lookup key -> O(1) reads, no "
     "iteration.", GREEN),
    ("university=msg.sender", "Deployer frozen as the permanent, immutable admin "
     "owner.", PURPLE),
    ("require(...==university)", "Reverts every unauthorized write at the EVM layer "
     "before gas commit.", RED),
    ("ipfsHash (Phase 1)", "Currently stores a MANUAL mock string; real SHA-256 / "
     "IPFS hashing is Phase 2.", AMBER),
]
yy = 124
for name, desc, col in notes:
    h = 70
    left_accent_card(ax, yy, aw, h, col)
    text(ax + 18, yy + 14, name, font=MONOB, size=10.5, color=col)
    para(ax + 18, yy + 32, aw - 34, desc, font=SANS, size=10, color=GREY, leading=13)
    yy += h + 7
footer()
c.showPage()


# ============================================================================
# PAGE 7 — Frontend & Read-Path Discrimination
# ============================================================================
fill_page()
header("Client Layer", "Decentralized Frontend & Read-Path Discrimination", 7)

# left: mechanics
left_accent_card(58, 124, 470, 372, BLUE)
text(78, 142, "SERVERLESS STATE BRIDGE", font=MONOB, size=11, color=BLUE, tracking=1.0)
yy = para(78, 166, 430,
          "The interface integrates an injected Web3 engine, binding to MetaMask "
          "through ethers.providers.Web3Provider(window.ethereum). No backend "
          "server mediates the verification request.", font=SANS, size=12,
          color=GREY, leading=16)
yy += 10
rows = [
    ("Web3Provider(window.ethereum)", "Injected MetaMask provider bridge.", CYAN),
    ("contract.certificates(regNo)", "Isolated view call - reads an active "
     "storage slot, costs ZERO gas.", GREEN),
    ("ABI + struct destructuring", "Decodes returned EVM struct fields into the "
     "UI model.", PURPLE),
    ("Uninitialized-Key Safety Filter", "if (!data.studentName || "
     "data.studentName.trim() === \"\")", RED),
]
for name, desc, col in rows:
    box(78, yy, 16, 16, fill=None, stroke=col, sw=1.5, r=3)
    text(86, yy + 1, "\u2022", font=SANSB, size=12, color=col, align="center")
    text(104, yy, name, font=MONOB, size=11, color=col)
    yy = para(104, yy + 18, 410, desc, font=SANS, size=11, color=GREY, leading=14) + 12

# right: result states
text(556, 122, "DYNAMIC #result STATES", font=MONOB, size=11, color=CYAN, tracking=1.0)

# success
card(556, 148, 346, 150, GREEN)
text(576, 168, "#result", font=MONOB, size=11, color=GREEN)
text(640, 168, ".success", font=MONO, size=11, color=DARKGREY)
text(576, 192, "\u2713  Certificate Verified", font=SANSB, size=16, color=WHITE)
para(576, 222, 310, "Resolved struct fields (studentName, courseName, hash) render "
                    "into the verified panel.", font=SANS, size=11, color=GREY,
     leading=14)

# error
card(556, 314, 346, 150, RED)
text(576, 334, "#result", font=MONOB, size=11, color=RED)
text(640, 334, ".error", font=MONO, size=11, color=DARKGREY)
text(576, 358, "\u2715  Record Not Found", font=SANSB, size=16, color=WHITE)
para(576, 388, 310, "An unknown / mistyped key returns zero-state blanks; the "
                    "filter intercepts the empty shape and renders this card.",
     font=SANS, size=11, color=GREY, leading=14)

box(556, 474, 346, 30, fill=BG_CODE, stroke=PANEL_LN, sw=1.0, r=6)
text(572, 482, "EVM returns default \"\" for uninitialized mapping keys (no revert).",
     font=MONO, size=8.6, color=AMBER)
footer()
c.showPage()


# ============================================================================
# PAGE 8 — System Dataflow Lifecycle
# ============================================================================
fill_page()
header("Lifecycle", "End-to-End System Dataflow", 8)

steps = [
    ("01", "Compilation",
     "Solidity is compiled to EVM bytecode and an ABI JSON interface.", CYAN),
    ("02", "Deployment",
     "Admin signs a contract-creation tx (blank \"to\" field) and pays gas to "
     "Sepolia.", BLUE),
    ("03", "Issuance (Write)",
     "Admin enters fields in Remix; MetaMask signs; record is mined. Costs gas.",
     PURPLE),
    ("04", "Verification (Read)",
     "Verifier submits a Reg. No.; a gasless view call returns the record "
     "instantly.", GREEN),
]
cw, gap, x0, y0, ch = 200, 24, 58, 150, 230
for i, (num, title, body, acc) in enumerate(steps):
    cx = x0 + i * (cw + gap)
    card(cx, y0, cw, ch, acc)
    text(cx + 20, y0 + 26, num, font=MONOB, size=34, color=acc)
    text(cx + 20, y0 + 86, title, font=SANSB, size=15, color=WHITE)
    para(cx + 20, y0 + 116, cw - 40, body, font=SANS, size=11.5, color=GREY,
         leading=15)
    if i < len(steps) - 1:
        text(cx + cw + gap / 2.0, y0 + ch / 2.0 - 14, "\u203A", font=SANSB,
             size=30, color=DARKGREY, align="center")

# legend
box(58, 416, 844, 64, fill=BG_PANEL, stroke=PANEL_LN, sw=1.0, r=10)
dot(80, 436, 12, AMBER)
text(100, 432, "WRITE PATH", font=SANSB, size=12, color=AMBER)
text(195, 432, "state mutation, requires admin signature & gas (SepoliaETH).",
     font=SANS, size=11.5, color=GREY)
dot(80, 458, 12, GREEN)
text(100, 454, "READ PATH", font=SANSB, size=12, color=GREEN)
text(195, 454, "gasless view call, permissionless, resolves in O(1) constant time.",
     font=SANS, size=11.5, color=GREY)
footer()
c.showPage()


# ============================================================================
# PAGE 9 — Data Fingerprint Clarification  (KEY CORRECTION)
# ============================================================================
fill_page()
header("Scope Clarification", "The Hash Field: Current Reality vs. Final-Year Goal", 9,
       sub="Disambiguating the ipfsHash struct field across the project timeline.")

# NOW
card(58, 138, 414, 320, AMBER)
chip(78, 160, "PHASE 1 - NOW (3RD YEAR)", AMBER, w=200, h=24)
text(78, 196, "Manual Mock Placeholder", font=SANSB, size=17, color=WHITE)
now = [
    "The ipfsHash field is populated by HAND in Remix with an arbitrary "
    "alphanumeric string.",
    "No certificate file is uploaded; no IPFS pinning occurs.",
    "No SHA-256 / cryptographic digest is computed anywhere in the pipeline.",
    "Purpose: a data-fingerprint PLACEHOLDER to exercise the struct storage "
    "layout and read path.",
]
yy = 232
for it in now:
    text(78, yy, "\u2022", font=SANSB, size=13, color=AMBER)
    yy = para(96, yy, 360, it, font=SANS, size=11.5, color=GREY, leading=15) + 10

# FUTURE
card(488, 138, 414, 320, GREEN)
chip(508, 160, "PHASE 2 - FINAL YEAR", GREEN, w=180, h=24)
text(508, 196, "Real Cryptographic Hashing", font=SANSB, size=17, color=WHITE)
fut = [
    "An autonomous agent computes a deterministic SHA-256 / IPFS file-blob hash "
    "from the actual certificate.",
    "The content hash is generated off-chain, then anchored on-chain "
    "programmatically.",
    "Web3.py / Ethers.js sign & broadcast the write from the agent's own wallet.",
    "This upgrades the placeholder into a true tamper-evident document "
    "fingerprint.",
]
yy = 232
for it in fut:
    text(508, yy, "\u2192", font=SANSB, size=12, color=GREEN)
    yy = para(528, yy, 356, it, font=SANS, size=11.5, color=GREY, leading=15) + 10

box(58, 470, 844, 36, fill=BG_CODE, stroke=AMBER, sw=1.0, r=8)
text(76, 480, "VIVA NOTE:", font=MONOB, size=10.5, color=AMBER)
text(166, 480, "The field is named ipfsHash for forward-compatibility, but in the "
               "current prototype it carries a manually-entered mock value only.",
     font=SANS, size=11, color=WHITE)
footer()
c.showPage()


# ============================================================================
# PAGE 10 — Tech Stack & Outcomes
# ============================================================================
fill_page()
header("Summary", "Technology Stack & Engineering Outcomes", 10)

# left: stack
text(58, 122, "TECHNOLOGY STACK", font=MONOB, size=11, color=CYAN, tracking=1.2)
stack = [
    ("Smart Contract", "Solidity v0.8.0", CYAN),
    ("Execution Network", "Ethereum Sepolia Testnet (EVM)", BLUE),
    ("Web3 Library", "Ethers.js v5.7.2", PURPLE),
    ("Wallet / Signer", "MetaMask Injected Provider", AMBER),
    ("Data Fingerprint (P1)", "Manual mock string in Remix IDE", RED),
    ("Hashing Roadmap (P2)", "SHA-256 / IPFS via autonomous agent", GREEN),
]
yy = 150
for k, v, col in stack:
    box(58, yy + 3, 6, 40, fill=col)
    text(78, yy, k, font=SANSB, size=12.5, color=WHITE)
    text(78, yy + 18, v, font=MONO, size=11, color=GREY)
    yy += 56

# right: outcomes
text(508, 122, "ENGINEERING OUTCOMES", font=MONOB, size=11, color=GREEN, tracking=1.2)
outs = [
    ("Immutable, tamper-evident on-chain records", CYAN),
    ("O(1) constant-time verification at scale", GREEN),
    ("Zero-latency, 24x7 permissionless global reads", BLUE),
    ("No single point of failure (no central server)", PURPLE),
    ("Gasless verification path for public verifiers", AMBER),
    ("EVM-enforced admin-only write authorization", RED),
]
yy = 150
for label, col in outs:
    box(508, yy, 394, 42, fill=BG_PANEL, r=8)
    text(528, yy + 13, "\u2713", font=SANSB, size=13, color=col)
    text(552, yy + 13, label, font=SANS, size=12.5, color=WHITE)
    yy += 50
footer()
c.showPage()


# ============================================================================
# PAGE 11 — Conclusion
# ============================================================================
fill_page()
box(0, 0, 9, H, fill=CYAN)
for (gx, gy, col, d) in [(836, 80, CYAN, 12), (884, 130, BLUE, 9),
                         (74, 446, PURPLE, 10)]:
    dot(gx, gy, d, col)

text(72, 150, "CONCLUSION", font=SANSB, size=12, color=CYAN, tracking=2.4)
text(70, 188, "Trust, anchored on-chain.", font=SANSB, size=46, color=WHITE)
para(72, 268, 820,
     "UniVerify V2.0 reframes certificate verification from a multi-day, "
     "centralized, forgery-prone process into an immutable, decentralized, "
     "constant-time lookup. The Phase-1 prototype proves the contract's state "
     "mutability, RBAC guardrails, and gasless read path under a manual "
     "curation paradigm.", font=SANS, size=15, color=GREY, leading=22)

hline(74, 372, 230, CYAN, 2)
text(72, 388, "Next Milestone (Final Year)", font=SANSB, size=15, color=WHITE)
para(72, 414, 820,
     "Phase 2 introduces the Autonomous AI Agent: NLP-normalized ingestion, "
     "deterministic SHA-256 / IPFS content hashing, and programmatic transaction "
     "signing - eliminating the human-in-the-loop entirely.", font=SANS, size=13,
     color=GREY, leading=19)

text(72, 484, "UniVerify V2.0  .  B.Tech CSE Capstone  .  Ethereum Sepolia Testnet",
     font=MONO, size=10.5, color=DARKGREY)
c.showPage()

c.save()
print("Saved UniVerify_V2.0.pdf")
