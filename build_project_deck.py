#!/usr/bin/env python3
"""
Builds the 20-slide UniVerify V2.0 academic project-review deck.
Run: python3 build_project_deck.py  ->  UniVerify_V2.0_ProjectReview.pptx + .pdf
"""
from deck_engine import PptxCanvas, PdfCanvas, _wrap

# --------------------------------------------------------------- palette
WHITE = "#FFFFFF"
INK = "#16213E"
MUTED = "#5B6678"
PRIMARY = "#1F3A8A"
T1 = "#0E7C86"   # teal
T2 = "#2563EB"   # blue
T3 = "#7C3AED"   # violet
T4 = "#16A34A"   # green
T5 = "#D97706"   # amber
T6 = "#DC2626"   # red
PANEL = "#F1F5F9"
PANEL2 = "#E8EEF6"
BORDER = "#CBD5E1"
# light fills (tints) keyed by accent
FILL = {
    T1: "#D6F1F2", T2: "#E3ECFD", T3: "#EDE7FC", T4: "#DCFCE7",
    T5: "#FEF1D6", T6: "#FCE3E0", PRIMARY: "#E4E9F7", MUTED: "#EEF1F5",
}
TOTAL = 20


# --------------------------------------------------------------- chrome
def header(c, kicker, title, num, sub=None):
    c.rect(40, 34, 7, 30, fill=PRIMARY)
    c.text(58, 32, 760, 14, kicker.upper(), size=11, color=T2, bold=True)
    c.text(57, 46, 800, 26, title, size=22, color=INK, bold=True)
    c.line(40, 80, 920, 80, color=BORDER, w=1.2)
    c.text(40, 32, 880, 16, f"{num:02d} / {TOTAL}", size=11, color=MUTED,
           bold=True, align="r")
    if sub:
        c.text(58, 70, 820, 14, sub, size=11.5, color=MUTED, italic=True)


def footer(c):
    c.line(40, 512, 920, 512, color=BORDER, w=0.8)
    c.text(40, 518, 600, 12, "UniVerify V2.0  |  B.Tech CSE \u2014 Project Review",
           size=8.5, color=MUTED)
    c.text(40, 518, 880, 12, "Decentralized Academic Certificate Verification",
           size=8.5, color=MUTED, align="r")


def bullets(c, x, y, w, items, size=13.5, lead=None, gap=8, marker="\u25B8",
            mcol=T2, tcol=INK):
    lead = lead or size * 1.28
    cy = y
    for it in items:
        if isinstance(it, tuple):
            head, body = it
        else:
            head, body = None, it
        c.text(x, cy + 1, 14, size, marker, size=size - 2, color=mcol, bold=True)
        if head:
            c.text(x + 18, cy, w - 18, size, head + "  ", size=size, color=tcol,
                   bold=True)
            hw = _wrap(head + "  ", w - 18, size)
            # body wrapped on following lines
            lines = _wrap(body, w - 18, size)
            c.text(x + 18 + _wpx(head + "  ", size), cy, w - 18 - _wpx(head + "  ", size),
                   size, lines[0], size=size, color=MUTED)
            cy += lead
            for ln in lines[1:]:
                c.text(x + 18, cy, w - 18, size, ln, size=size, color=MUTED)
                cy += lead
        else:
            lines = _wrap(body, w - 18, size)
            for ln in lines:
                c.text(x + 18, cy, w - 18, size, ln, size=size, color=tcol)
                cy += lead
        cy += gap
    return cy


def _wpx(s, size):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    return stringWidth(s, "Helvetica-Bold", size)


def para(c, x, y, w, s, size=13.5, color=MUTED, lead=None, bold=False):
    lead = lead or size * 1.32
    lines = _wrap(s, w, size)
    cy = y
    for ln in lines:
        c.text(x, cy, w, size, ln, size=size, color=color, bold=bold)
        cy += lead
    return cy


# --------------------------------------------------------------- diagram bits
def node(c, x, y, w, h, title, accent, body=None, radius=8, tsize=12.5,
         bsize=10.5):
    c.rect(x, y, w, h, fill=FILL.get(accent, PANEL), line=accent, line_w=1.4,
           radius=radius)
    c.rect(x, y, w, 5, fill=accent, radius=2)
    if body:
        pad_top = 9
        # measure the title's true wrapped height so multi-line titles never
        # spill into the body region below them
        tlines = []
        for part in str(title).split("\n"):
            tlines.extend(_wrap(part, w - 16, tsize))
        title_h = len(tlines) * tsize * 1.25
        c.text(x + 8, y + pad_top, w - 16, title_h, title, size=tsize, color=INK,
               bold=True, align="c")
        body_top = y + pad_top + title_h + 3
        body_h = max(12, (y + h) - body_top - 5)
        c.text(x + 8, body_top, w - 16, body_h, body, size=bsize, color=MUTED,
               align="c", valign="m")
    else:
        c.text(x + 6, y + 5, w - 12, h - 5, title, size=tsize, color=INK,
               bold=True, align="c", valign="m")


def actor(c, cx, top, label, color=PRIMARY, scale=1.7):
    r = 4 * scale
    c.ellipse(cx - r, top, 2 * r, 2 * r, fill=None, line=color, line_w=1.6)
    by = top + 2 * r
    c.line(cx, by, cx, by + 11 * scale, color=color, w=1.6)
    c.line(cx - 7 * scale, by + 4 * scale, cx + 7 * scale, by + 4 * scale,
           color=color, w=1.6)
    c.line(cx, by + 11 * scale, cx - 6 * scale, by + 19 * scale, color=color, w=1.6)
    c.line(cx, by + 11 * scale, cx + 6 * scale, by + 19 * scale, color=color, w=1.6)
    c.text(cx - 55, by + 19 * scale + 4, 110, 26, label, size=10.5, color=INK,
           bold=True, align="c")


def uml_class(c, x, y, w, name, attrs, methods, accent=T2):
    la, lm = len(attrs), len(methods)
    head_h = 20
    row = 13
    ah = max(row, la * row + 6)
    mh = max(row, lm * row + 6)
    h = head_h + ah + mh
    c.rect(x, y, w, h, fill=WHITE, line=accent, line_w=1.3)
    c.rect(x, y, w, head_h, fill=accent)
    c.text(x, y + 3, w, head_h, name, size=11, color=WHITE, bold=True,
           align="c")
    c.line(x, y + head_h, x + w, y + head_h, color=accent, w=1.0)
    ty = y + head_h + 4
    for a in attrs:
        c.text(x + 6, ty, w - 10, row, a, size=9, color=INK)
        ty += row
    c.line(x, y + head_h + ah, x + w, y + head_h + ah, color=accent, w=1.0)
    ty = y + head_h + ah + 4
    for m in methods:
        c.text(x + 6, ty, w - 10, row, m, size=9, color=INK)
        ty += row
    return h


def browser(c, x, y, w, h, url):
    c.rect(x, y, w, h, fill=WHITE, line=BORDER, line_w=1.2, radius=8)
    c.rect(x, y, w, 22, fill="#E2E8F0", radius=6)
    c.rect(x, y + 14, w, 8, fill="#E2E8F0")
    for i, col in enumerate([T6, T5, T4]):
        c.ellipse(x + 10 + i * 12, y + 7, 8, 8, fill=col)
    c.rect(x + 48, y + 5, w - 60, 12, fill=WHITE, line=BORDER, line_w=0.8, radius=6)
    c.text(x + 54, y + 5, w - 70, 12, url, size=7.5, color=MUTED, valign="m")


def chart(c, x, y, w, h, cats, s1, s2, n1, n2, c1=T6, c2=T2, ymax=10):
    # axes
    c.line(x, y, x, y + h, color=MUTED, w=1.2)
    c.line(x, y + h, x + w, y + h, color=MUTED, w=1.2)
    for g in range(0, ymax + 1, 2):
        gy = y + h - (g / ymax) * h
        c.line(x, gy, x + w, gy, color=PANEL, w=0.8)
        c.text(x - 22, gy - 5, 18, 10, str(g), size=8, color=MUTED, align="r")
    n = len(cats)
    group = w / n
    bw = group * 0.28
    for i, cat in enumerate(cats):
        gx = x + i * group + group / 2.0
        b1 = (s1[i] / ymax) * h
        b2 = (s2[i] / ymax) * h
        c.rect(gx - bw - 3, y + h - b1, bw, b1, fill=c1)
        c.rect(gx + 3, y + h - b2, bw, b2, fill=c2)
        c.text(gx - bw - 3, y + h - b1 - 13, bw, 11, str(s1[i]), size=8,
               color=c1, bold=True, align="c")
        c.text(gx + 3, y + h - b2 - 13, bw, 11, str(s2[i]), size=8, color=c2,
               bold=True, align="c")
        c.text(gx - group / 2.0, y + h + 4, group, 22, cat, size=8.5, color=INK,
               align="c", bold=True)
    # legend
    lx = x + w - 230
    ly = y - 18
    c.rect(lx, ly, 12, 10, fill=c1)
    c.text(lx + 16, ly - 1, 90, 12, n1, size=9, color=INK)
    c.rect(lx + 110, ly, 12, 10, fill=c2)
    c.text(lx + 126, ly - 1, 100, 12, n2, size=9, color=INK)


# =====================================================================
#  SLIDES
# =====================================================================
def s01_title(c):
    c.new_page(WHITE)
    c.rect(0, 0, 960, 110, fill=PRIMARY)
    c.rect(0, 110, 960, 5, fill=T1)
    c.text(0, 26, 960, 16, "DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING",
           size=12, color="#C9D6F5", bold=True, align="c")
    c.text(0, 52, 960, 28, "<College / University Name>", size=20, color=WHITE,
           bold=True, align="c")
    c.text(0, 84, 960, 14, "A Final-Year B.Tech Major Project Report", size=11,
           color="#C9D6F5", align="c")

    c.text(60, 168, 840, 20, "PROJECT TITLE", size=12, color=T2, bold=True,
           align="c")
    c.text(60, 192, 840, 36, "UniVerify V2.0", size=40, color=INK, bold=True,
           align="c")
    para(c, 130, 244, 700,
         "A Decentralized Academic Certificate Verification Protocol "
         "Using Alphanumeric Keyspace Mapping", size=17, color=MUTED, lead=23)
    # mid divider
    c.line(380, 312, 580, 312, color=T1, w=2)

    # submitted by / guide cards
    c.rect(120, 332, 340, 92, fill=PANEL, line=BORDER, line_w=1, radius=8)
    c.rect(120, 332, 340, 5, fill=T2, radius=2)
    c.text(136, 346, 308, 14, "SUBMITTED BY", size=10.5, color=T2, bold=True)
    c.text(136, 366, 308, 16, "<Student Name>", size=14, color=INK, bold=True)
    c.text(136, 386, 308, 14, "Reg. No.: <2021CSE101>", size=11, color=MUTED)
    c.text(136, 404, 308, 14, "B.Tech \u2014 Computer Science & Engineering",
           size=10, color=MUTED)

    c.rect(500, 332, 340, 92, fill=PANEL, line=BORDER, line_w=1, radius=8)
    c.rect(500, 332, 340, 5, fill=T3, radius=2)
    c.text(516, 346, 308, 14, "UNDER THE GUIDANCE OF", size=10.5, color=T3,
           bold=True)
    c.text(516, 366, 308, 16, "<Guide Name>", size=14, color=INK, bold=True)
    c.text(516, 386, 308, 14, "Designation: <Assistant Professor>", size=11,
           color=MUTED)
    c.text(516, 404, 308, 14, "Department of CSE", size=10, color=MUTED)

    c.text(0, 452, 960, 14,
           "Solidity ^0.8.0   \u2022   Ethers.js v5.7.2   \u2022   MetaMask   "
           "\u2022   Ethereum Sepolia Testnet", size=11, color=T1, bold=True,
           align="c")
    c.text(0, 488, 960, 14, "Academic Year <2024\u201325>", size=11, color=MUTED,
           align="c")


def s02_abstract(c):
    c.new_page(WHITE)
    header(c, "Overview", "Abstract", 2)
    para(c, 58, 100, 844,
         "Traditional academic credential verification depends on centralized "
         "relational databases and manual, paper-based pipelines that suffer from "
         "high latency (7\u201314 days), recurring administrative cost, a single "
         "point of failure (SPOF), and easy forgery of unanchored documents.",
         size=13.5, lead=19)
    para(c, 58, 168, 844,
         "UniVerify V2.0 is a decentralized web application that anchors academic "
         "certificate records onto the public Ethereum Sepolia Testnet, making them "
         "immutable, globally accessible and verifiable in near real time. The "
         "smart contract binds each record to a student\u2019s unique alphanumeric "
         "Registration Number using a string-keyed state mapping, delivering O(1) "
         "constant-time lookups and Role-Based Access Control (RBAC) that restricts "
         "write operations to the deployer (University Admin) wallet. Verification "
         "is a gasless, read-only view call executed client-side via Ethers.js and "
         "MetaMask.", size=13.5, lead=19)
    c.rect(58, 322, 844, 92, fill=PANEL, line=T1, line_w=1.2, radius=8)
    c.text(74, 334, 812, 14, "SCOPE (PHASED)", size=10.5, color=T1, bold=True)
    para(c, 74, 354, 812,
         "Phase 1 (current, third year): a Production Ledger Prototype operated "
         "under a Manual Administrative Curation paradigm \u2014 the admin enters "
         "records in the Remix IDE and the hash field holds a manually-typed "
         "alphanumeric mock placeholder. Phase 2 (final year): an autonomous AI "
         "agent computes deterministic SHA-256 / IPFS hashes and broadcasts "
         "transactions programmatically.", size=12, lead=16.5, color=INK)
    footer(c)


def s03_intro(c):
    c.new_page(WHITE)
    header(c, "Background", "Introduction", 3)
    bullets(c, 58, 100, 540, [
        ("Problem context.", "Academic credential fraud and slow manual "
         "verification cause real losses in admissions, recruitment and "
         "immigration screening."),
        ("Blockchain / DLT.", "A decentralized, append-only ledger removes the "
         "central trusted authority and makes records tamper-evident."),
        ("Smart contracts.", "Self-executing code on the Ethereum Virtual Machine "
         "(EVM) enforces issuance rules deterministically at the protocol level."),
        ("Decentralized identity.", "Credentials are anchored on-chain and verified "
         "by anyone, anywhere, without contacting the issuing institution."),
        ("Our contribution.", "A string-keyed certificate registry with O(1) "
         "lookups, RBAC, and a gasless verification path."),
    ], size=12.8, gap=9)
    # right illustration: simple flow
    bx = 640
    node(c, bx, 110, 250, 46, "Issuing University", T2,
         "Admin wallet issues records", tsize=12, bsize=9.5)
    c.line(765, 156, 765, 196, color=MUTED, w=1.4, arrow_end=True)
    node(c, bx, 196, 250, 46, "Public Blockchain", T3,
         "Immutable certificate ledger", tsize=12, bsize=9.5)
    c.line(765, 242, 765, 282, color=MUTED, w=1.4, arrow_end=True)
    node(c, bx, 282, 250, 46, "Verifier / Recruiter", T4,
         "Instant gasless verification", tsize=12, bsize=9.5)
    c.text(bx, 338, 250, 14, "Trust shifts from an institution", size=9.5,
           color=MUTED, align="c", italic=True)
    c.text(bx, 352, 250, 14, "to a public, verifiable protocol", size=9.5,
           color=MUTED, align="c", italic=True)
    footer(c)


def s04_litsurvey(c):
    c.new_page(WHITE)
    header(c, "Related Work", "Literature Survey", 4,
           sub="Representative foundational works \u2014 replace/extend with your cited papers.")
    cols = [58, 150, 300, 600, 902]  # x boundaries: Ref | Author(Year) | Focus | Limitation
    heads = ["Ref.", "Author (Year)", "Focus / Contribution", "Limitation"]
    rows = [
        ("[1]", "Nakamoto (2008)", "Bitcoin: a peer-to-peer electronic cash system; "
         "first decentralized, tamper-evident ledger.",
         "Not programmable; no native support for arbitrary credential records."),
        ("[2]", "Buterin (2014)", "Ethereum: a Turing-complete smart-contract "
         "platform enabling programmable trust on the EVM.",
         "State-changing writes cost gas; throughput / scalability limits."),
        ("[3]", "Benet (2014)", "IPFS: content-addressed, distributed file storage "
         "referenced by cryptographic hash.",
         "Availability depends on pinning; not a verification protocol by itself."),
        ("[4]", "MIT Media Lab \u2014 Blockcerts (2016)", "Open standard for issuing "
         "and verifying blockchain-anchored academic certificates.",
         "Relies on issuer infrastructure; anchoring/verification overhead."),
        ("[5]", "Grech & Camilleri (2017)", "EU JRC study on blockchain in "
         "education; surveys credentialing use-cases.",
         "Highlights governance, scalability and adoption challenges."),
    ]
    # header row
    th = 26
    y = 96
    c.rect(58, y, 844, th, fill=PRIMARY)
    for i, hd in enumerate(heads):
        c.text(cols[i] + 6, y + 6, cols[i + 1] - cols[i] - 10, 14, hd, size=10.5,
               color=WHITE, bold=True)
    y += th
    rh = 64
    for ri, row in enumerate(rows):
        bg = WHITE if ri % 2 == 0 else PANEL
        c.rect(58, y, 844, rh, fill=bg, line=BORDER, line_w=0.6)
        c.text(cols[0] + 6, y + 6, 40, 14, row[0], size=10, color=T2, bold=True)
        para(c, cols[1] + 6, y + 6, cols[2] - cols[1] - 10, row[1], size=9.5,
             color=INK, bold=True, lead=12)
        para(c, cols[2] + 6, y + 6, cols[3] - cols[2] - 10, row[2], size=9.5,
             color=MUTED, lead=12)
        para(c, cols[3] + 6, y + 6, cols[4] - cols[3] - 10, row[3], size=9.5,
             color=MUTED, lead=12)
        y += rh
    footer(c)


def s05_existing(c):
    c.new_page(WHITE)
    header(c, "Current Practice", "Existing System", 5)
    bullets(c, 58, 100, 844, [
        ("Centralized RDBMS.", "Each institution stores degree records in a private "
         "relational database hosted on its own servers."),
        ("Manual / paper verification.", "Verifiers email or call the registrar; "
         "officials manually search records and issue confirmation letters."),
        ("Third-party agencies.", "Background-verification companies act as paid "
         "intermediaries, adding cost and further delay."),
        ("Standalone digital PDFs.", "Some institutions issue signed PDF "
         "certificates that are easy to copy and visually manipulate."),
        ("Trust model.", "Verification trust rests entirely on the availability and "
         "integrity of one central authority and its servers."),
    ], size=13, gap=10)
    footer(c)


def s06_existing_arch(c):
    c.new_page(WHITE)
    header(c, "Existing System", "Architecture of Existing System", 6,
           sub="Centralized request\u2013response model with a single point of failure.")
    actor(c, 120, 250, "Verifier /\nRecruiter", PRIMARY)
    node(c, 250, 230, 170, 60, "University\nWeb Server", T2,
         None, tsize=12)
    node(c, 250, 110, 170, 56, "Registrar / Admin\n(manual entry)", T5, None,
         tsize=11)
    node(c, 540, 230, 180, 60, "Centralized\nRDBMS", T3, None, tsize=12)
    node(c, 540, 110, 180, 56, "Backup Server\n(optional)", MUTED, None, tsize=11)

    c.line(175, 252, 250, 258, color=MUTED, w=1.5, arrow_end=True)
    c.text(150, 270, 130, 12, "1. request (regNo)", size=9, color=MUTED)
    c.line(335, 230, 335, 166, color=T5, w=1.5, arrow_start=True, arrow_end=True)
    c.text(228, 195, 120, 12, "manual curation", size=9, color=MUTED)
    c.line(420, 258, 540, 258, color=MUTED, w=1.5, arrow_start=True, arrow_end=True)
    c.text(430, 270, 120, 12, "2. SQL query / write", size=9, color=MUTED)
    c.line(630, 230, 630, 166, color=MUTED, w=1.3, dash=True, arrow_end=True)
    c.line(250, 285, 175, 270, color=MUTED, w=1.5, arrow_end=True)
    c.text(150, 290, 150, 12, "3. result (7\u201314 days)", size=9, color=MUTED)

    # SPOF callout
    c.rect(760, 200, 150, 110, fill=FILL[T6], line=T6, line_w=1.3, radius=8)
    c.text(770, 210, 130, 14, "\u26A0 SPOF", size=12, color=T6, bold=True)
    para(c, 770, 230, 130, "A single server/DB outage or breach halts or "
         "corrupts all verification.", size=9.5, color=INK, lead=13)
    footer(c)


def s07_problem(c):
    c.new_page(WHITE)
    header(c, "Motivation", "Drawbacks & Problem Statement", 7)
    cards = [
        ("High latency", "Manual lookups take 7\u201314 days, delaying admissions and hiring.", T5),
        ("Single point of failure", "Central server/DB outage or breach stops everything.", T6),
        ("Administrative cost", "Repeated manual audits create recurring overhead.", T2),
        ("Credential forgery", "Unanchored PDFs are trivially copied or altered.", T3),
    ]
    cw, gap, x0, y0, ch = 205, 13, 58, 100, 96
    for i, (t, b, acc) in enumerate(cards):
        cx = x0 + i * (cw + gap)
        c.rect(cx, y0, cw, ch, fill=FILL[acc], line=acc, line_w=1.2, radius=8)
        c.rect(cx, y0, cw, 5, fill=acc, radius=2)
        c.text(cx + 12, y0 + 16, cw - 24, 16, t, size=13, color=INK, bold=True)
        para(c, cx + 12, y0 + 40, cw - 24, b, size=10.5, color=MUTED, lead=14)
    c.rect(58, 224, 844, 100, fill=PRIMARY, radius=10)
    c.text(76, 238, 812, 16, "PROBLEM STATEMENT", size=12, color="#C9D6F5",
           bold=True)
    para(c, 76, 262, 812,
         "Design a verification protocol that eliminates the centralized single "
         "point of failure and manual latency of conventional systems by anchoring "
         "tamper-evident certificate records on a public blockchain \u2014 enabling "
         "instant, constant-time, globally accessible verification while restricting "
         "issuance to an authorized institutional authority.",
         size=13, color=WHITE, lead=18)
    footer(c)


def s08_proposed(c):
    c.new_page(WHITE)
    header(c, "Our Approach", "Proposed System", 8)
    bullets(c, 58, 100, 540, [
        ("On-chain anchoring.", "Certificate records are written to a Solidity "
         "smart contract on the Ethereum Sepolia Testnet \u2014 immutable once mined."),
        ("Alphanumeric keyspace mapping.", "mapping(string => Certificate) keyed by "
         "Registration Number gives O(1) constant-time retrieval."),
        ("Role-Based Access Control.", "The constructor freezes the deployer as the "
         "sole admin; unauthorized writes revert at the EVM layer."),
        ("Gasless verification.", "Verifiers call a read-only view function via "
         "Ethers.js \u2014 instant and free of gas."),
        ("Safety filter.", "Zero-state (blank) results are intercepted and shown as "
         "\u201CRecord Not Found\u201D."),
    ], size=12.6, gap=8)
    # right: benefit chips
    chips = [("Immutable", T3), ("O(1) lookup", T4), ("No SPOF", T6),
             ("Gasless reads", T1), ("RBAC-secured", T2), ("Global access", T5)]
    bx, by = 636, 110
    for i, (t, col) in enumerate(chips):
        r, cc = divmod(i, 2)
        x = bx + cc * 135
        y = by + r * 56
        c.rect(x, y, 124, 44, fill=FILL[col], line=col, line_w=1.2, radius=8)
        c.text(x, y, 124, 44, t, size=12, color=INK, bold=True, align="c",
               valign="m")
    c.rect(636, 290, 259, 70, fill=PANEL, line=BORDER, line_w=1, radius=8)
    c.text(648, 300, 235, 12, "PHASE NOTE", size=9.5, color=T1, bold=True)
    para(c, 648, 316, 235, "Phase 1 uses manual entry in Remix with a mock hash; "
         "real SHA-256 / IPFS hashing arrives in Phase 2.", size=9.5, color=MUTED,
         lead=13)
    footer(c)


def s09_proposed_arch(c):
    c.new_page(WHITE)
    header(c, "Proposed System", "Architecture of Proposed System", 9,
           sub="Write path (admin, costs gas) and read path (verifier, gasless).")
    # admin write path (top)
    actor(c, 110, 120, "University\nAdmin", T2)
    node(c, 200, 110, 140, 48, "MetaMask\n(sign + gas)", T5, None, tsize=11)
    node(c, 372, 110, 150, 48, "issueDegree()\nstate mutation", T2, None, tsize=11)
    c.line(160, 138, 200, 134, color=MUTED, w=1.5, arrow_end=True)
    c.line(340, 134, 372, 134, color=MUTED, w=1.5, arrow_end=True)

    # contract / ledger (center-right)
    node(c, 560, 150, 200, 90, "AcademicCertificates\n(Solidity \u2014 Sepolia EVM)",
         T3, None, tsize=12)
    c.rect(580, 196, 160, 34, fill=WHITE, line=T3, line_w=1, radius=6)
    c.text(580, 196, 160, 34, "mapping(string=>Cert)\nImmutable ledger", size=8.5,
           color=MUTED, align="c", valign="m")
    c.line(522, 134, 660, 150, color=T2, w=1.6, arrow_end=True)
    c.text(536, 120, 130, 12, "signed tx + gas", size=9, color=MUTED)

    # verifier read path (bottom)
    actor(c, 110, 320, "Verifier /\nRecruiter", T4)
    node(c, 200, 312, 150, 48, "Web UI +\nEthers.js", T4, None, tsize=11)
    node(c, 382, 312, 150, 48, "certificates(regNo)\nview call (0 gas)", T1, None,
         tsize=10.5)
    c.line(160, 338, 200, 336, color=MUTED, w=1.5, arrow_end=True)
    c.line(350, 336, 382, 336, color=MUTED, w=1.5, arrow_end=True)
    c.line(532, 336, 660, 240, color=T1, w=1.6, arrow_end=True)
    c.text(540, 300, 130, 12, "gasless read", size=9, color=MUTED)
    c.line(660, 240, 360, 360, color=T4, w=1.3, dash=True, arrow_end=True)
    c.text(420, 372, 200, 12, "struct result \u2192 render success / not found",
           size=9, color=MUTED)

    c.rect(560, 270, 200, 70, fill=PANEL, line=BORDER, line_w=1, radius=8)
    c.text(572, 280, 176, 12, "NETWORK", size=9.5, color=T3, bold=True)
    para(c, 572, 296, 176, "Public Ethereum Sepolia Testnet \u2014 EVM execution, "
         "globally readable, no central host.", size=9, color=MUTED, lead=12.5)
    footer(c)


def s10_module(c):
    c.new_page(WHITE)
    header(c, "Design", "Module Diagram", 10,
           sub="Hub-and-spoke decomposition of the UniVerify V2.0 system.")
    # hub
    cxm, cym = 480, 285
    c.ellipse(cxm - 80, cym - 42, 160, 84, fill=FILL[PRIMARY], line=PRIMARY,
              line_w=1.6)
    c.text(cxm - 80, cym - 42, 160, 84, "UniVerify V2.0\nSystem Core", size=12,
           color=INK, bold=True, align="c", valign="m")
    mods = [
        ("Smart Contract\nModule", "struct, mapping,\nRBAC require()", T2, 90, 120),
        ("Admin & Issuance\nModule", "issueDegree(),\nMetaMask sign", T5, 380, 105),
        ("Web3 Provider\nModule", "Ethers.js +\nMetaMask bridge", T1, 700, 120),
        ("Verification\nModule", "view call +\nsafety filter", T4, 700, 380),
        ("UI / Result\nModule", "#regInput,\n#result states", T3, 380, 420),
        ("AI Agent Module\n(Phase 2)", "NLP + SHA-256/\nIPFS, auto-sign", MUTED, 90, 380),
    ]
    for title, body, col, x, y in mods:
        node(c, x, y, 170, 74, title, col, body, tsize=11, bsize=8.8)
        # connect to hub
        c.line(x + 85, y + 37, cxm, cym, color=col, w=1.3)
    footer(c)


def s11_usecase(c):
    c.new_page(WHITE)
    header(c, "UML \u2014 1/5", "Use Case Diagram", 11,
           sub="Actors and their interactions with the verification system.")
    # system boundary
    c.rect(280, 96, 400, 380, fill=None, line=PRIMARY, line_w=1.4, radius=10)
    c.text(280, 104, 400, 14, "UniVerify V2.0", size=12, color=PRIMARY, bold=True,
           align="c")
    actor(c, 130, 200, "University\nAdmin", T2)
    actor(c, 830, 250, "Verifier /\nRecruiter", T4)
    ucs_admin = [("Deploy Contract", 150), ("Connect Wallet", 215),
                 ("Issue Degree", 280)]
    for label, y in ucs_admin:
        c.ellipse(330, y, 150, 40, fill=FILL[T2], line=T2, line_w=1.2)
        c.text(330, y, 150, 40, label, size=10, color=INK, bold=True, align="c",
               valign="m")
        c.line(165, 215, 330, y + 20, color=MUTED, w=1.2)
    ucs_ver = [("Enter Reg. No.", 320), ("Verify Certificate", 385),
               ("View Result", 450)]
    for label, y in ucs_ver:
        c.ellipse(490, y, 150, 40, fill=FILL[T4], line=T4, line_w=1.2)
        c.text(490, y, 150, 40, label, size=10, color=INK, bold=True, align="c",
               valign="m")
        c.line(795, 265, 640, y + 20, color=MUTED, w=1.2)
    # include relationship example
    c.line(405, 405, 405, 360, color=MUTED, w=1.1, dash=True, arrow_end=True)
    c.text(360, 343, 120, 12, "\u00ABinclude\u00BB", size=8.5, color=MUTED,
           italic=True, align="c")
    footer(c)


def s12_class(c):
    c.new_page(WHITE)
    header(c, "UML \u2014 2/5", "Class Diagram (Model Classes)", 12,
           sub="Core domain model: contract, record struct, frontend and Phase-2 agent.")
    h1 = uml_class(c, 70, 120, 220, "AcademicCertificates",
                   ["+ certificates: mapping<string,Certificate>",
                    "+ totalIssued: uint256",
                    "+ university: address"],
                   ["+ constructor()",
                    "+ issueDegree(regNo,name,",
                    "      course,hash): void",
                    "# require(msg.sender==university)"], accent=T2)
    h2 = uml_class(c, 360, 150, 200, "Certificate",
                   ["+ studentName: string",
                    "+ courseName: string",
                    "+ ipfsHash: string  // mock (P1)"],
                   ["+ isEmpty(): bool"], accent=T3)
    h3 = uml_class(c, 640, 116, 250, "VerificationPortal",
                   ["- provider: Web3Provider",
                    "- contract: Contract",
                    "- result: DOMElement"],
                   ["+ connectWallet(): void",
                    "+ verifyCertificate(regNo): void",
                    "+ renderResult(data): void"], accent=T4)
    h4 = uml_class(c, 640, 300, 250, "AIAgent  (Phase 2)",
                   ["- wallet: SecureWallet",
                    "- web3: Web3"],
                   ["+ ingestLogs(): void",
                    "+ normalize(): void",
                    "+ computeHash(): bytes32",
                    "+ signAndBroadcast(): void"], accent=MUTED)
    # relationships
    # AcademicCertificates *-- Certificate (composition)
    c.line(290, 175, 360, 185, color=INK, w=1.3)
    c.diamond(282, 170, 14, 10, fill=INK, line=INK)
    c.text(300, 158, 60, 12, "1      *", size=8.5, color=MUTED)
    c.text(300, 188, 90, 12, "stores", size=8.5, color=MUTED, italic=True)
    # VerificationPortal ..> AcademicCertificates (dependency, view call)
    c.line(640, 175, 290, 160, color=MUTED, w=1.2, dash=True, arrow_end=True)
    c.text(430, 150, 150, 12, "\u00ABuses\u00BB view call", size=8.5, color=MUTED,
           italic=True, align="c")
    # AIAgent ..> AcademicCertificates (writes)
    c.line(640, 340, 290, 210, color=MUTED, w=1.2, dash=True, arrow_end=True)
    c.text(420, 300, 160, 12, "\u00ABwrites\u00BB issueDegree()", size=8.5,
           color=MUTED, italic=True, align="c")
    footer(c)


def s13_sequence(c):
    c.new_page(WHITE)
    header(c, "UML \u2014 3/5", "Sequence Diagram (Verification)", 13,
           sub="Gasless read-path message flow between client and contract.")
    objs = [("Verifier", 120, T4), ("VerificationPortal\n(Ethers.js)", 320, T2),
            ("MetaMask\nProvider", 540, T5), ("AcademicCertificates\n(Sepolia)", 760, T3)]
    top = 100
    bottom = 470
    lifelines = {}
    for name, x, col in objs:
        c.rect(x - 75, top, 150, 38, fill=FILL[col], line=col, line_w=1.2, radius=6)
        c.text(x - 75, top, 150, 38, name, size=10, color=INK, bold=True,
               align="c", valign="m")
        c.line(x, top + 38, x, bottom, color=BORDER, w=1.0, dash=True)
        lifelines[name] = x

    def msg(x1, x2, y, label, ret=False, col=INK):
        c.line(x1, y, x2, y, color=col, w=1.4, arrow_end=True, dash=ret)
        midx = min(x1, x2)
        c.text(midx + 6, y - 13, abs(x2 - x1) - 12, 12, label, size=9,
               color=MUTED, align="c")

    X = lifelines
    A, B, Cc, D = X["Verifier"], X["VerificationPortal\n(Ethers.js)"], \
        X["MetaMask\nProvider"], X["AcademicCertificates\n(Sepolia)"]
    msg(A, B, 170, "1: enter regNo + click verify", col=T4)
    msg(B, Cc, 205, "2: Web3Provider(window.ethereum)", col=T2)
    msg(Cc, B, 235, "provider ready", ret=True, col=MUTED)
    msg(B, D, 275, "3: certificates(regNo)  [view, 0 gas]", col=T2)
    msg(D, B, 310, "4: Certificate struct / zero-state", ret=True, col=MUTED)
    # self message validate
    c.line(B, 345, B + 70, 345, color=INK, w=1.3)
    c.line(B + 70, 345, B + 70, 365, color=INK, w=1.3)
    c.line(B + 70, 365, B, 365, color=INK, w=1.3, arrow_end=True)
    c.text(B + 8, 333, 200, 12, "5: validate studentName != \u201C\u201D", size=9,
           color=MUTED)
    msg(B, A, 400, "6: render success / Record Not Found", col=T4)
    footer(c)


def s14_activity(c):
    c.new_page(WHITE)
    header(c, "UML \u2014 4/5", "Activity Diagram", 14,
           sub="Issuance (write) and verification (read) control flow with a decision.")
    # start
    c.ellipse(90, 110, 18, 18, fill=INK)
    c.line(99, 128, 99, 150, color=MUTED, w=1.4, arrow_end=True)
    node(c, 40, 150, 120, 40, "Admin enters\ndata (Remix)", T5, None, tsize=10)
    c.line(99, 190, 99, 212, color=MUTED, w=1.4, arrow_end=True)
    # decision: authorized?
    c.diamond(60, 212, 78, 56, fill=FILL[T2], line=T2, line_w=1.2)
    c.text(60, 212, 78, 56, "msg.sender\n== admin?", size=8.5, color=INK,
           align="c", valign="m")
    c.line(138, 240, 200, 240, color=MUTED, w=1.4, arrow_end=True)
    c.text(140, 226, 70, 12, "no", size=9, color=T6)
    node(c, 200, 218, 120, 44, "Revert tx\n(no gas wasted)", T6, None, tsize=10)
    c.line(99, 268, 99, 290, color=MUTED, w=1.4, arrow_end=True)
    c.text(104, 270, 50, 12, "yes", size=9, color=T4)
    node(c, 40, 290, 120, 44, "Write record\n& mine block", T4, None, tsize=10)

    # verification lane (right)
    c.line(560, 118, 560, 140, color=MUTED, w=1.4, arrow_end=True)
    c.ellipse(551, 110, 18, 18, fill=INK)
    node(c, 500, 140, 120, 40, "Verifier enters\nReg. No.", T4, None, tsize=10)
    c.line(560, 180, 560, 202, color=MUTED, w=1.4, arrow_end=True)
    node(c, 500, 202, 120, 40, "view call\ncertificates()", T1, None, tsize=10)
    c.line(560, 242, 560, 262, color=MUTED, w=1.4, arrow_end=True)
    c.diamond(516, 262, 88, 58, fill=FILL[T3], line=T3, line_w=1.2)
    c.text(516, 262, 88, 58, "studentName\nempty?", size=8.5, color=INK,
           align="c", valign="m")
    c.line(604, 291, 700, 291, color=MUTED, w=1.4, arrow_end=True)
    c.text(606, 277, 60, 12, "yes", size=9, color=T6)
    node(c, 700, 269, 130, 44, "Show\n\u201CRecord Not Found\u201D", T6, None, tsize=10)
    c.line(560, 320, 560, 342, color=MUTED, w=1.4, arrow_end=True)
    c.text(566, 322, 60, 12, "no", size=9, color=T4)
    node(c, 500, 342, 120, 44, "Show Verified\nCertificate", T4, None, tsize=10)
    # end nodes
    c.ellipse(92, 360, 18, 18, fill=None, line=INK, line_w=1.5)
    c.ellipse(96, 364, 10, 10, fill=INK)
    c.line(99, 334, 99, 360, color=MUTED, w=1.4, arrow_end=True)
    c.ellipse(551, 404, 18, 18, fill=None, line=INK, line_w=1.5)
    c.ellipse(555, 408, 10, 10, fill=INK)
    c.line(560, 386, 560, 404, color=MUTED, w=1.4, arrow_end=True)
    c.line(765, 313, 765, 413, color=MUTED, w=1.3)
    c.line(765, 413, 569, 413, color=MUTED, w=1.3, arrow_end=True)

    c.text(40, 96, 200, 12, "Issuance (write path)", size=10, color=T5, bold=True)
    c.text(500, 96, 220, 12, "Verification (read path)", size=10, color=T4,
           bold=True)
    footer(c)


def s15_component(c):
    c.new_page(WHITE)
    header(c, "UML \u2014 5/5", "Component / Deployment Diagram", 15,
           sub="Components grouped by deployment node; dashed arrows are dependencies.")

    def component(x, y, w, h, name, col):
        c.rect(x, y, w, h, fill=FILL[col], line=col, line_w=1.3, radius=4)
        c.rect(x - 6, y + 8, 14, 9, fill=WHITE, line=col, line_w=1)
        c.rect(x - 6, y + 24, 14, 9, fill=WHITE, line=col, line_w=1)
        c.text(x + 12, y, w - 16, h, name, size=10, color=INK, bold=True,
               align="c", valign="m")

    # Node 1: Client Browser
    c.rect(60, 110, 360, 200, fill=None, line=PRIMARY, line_w=1.4, radius=8)
    c.text(72, 116, 200, 12, "\u00ABnode\u00BB Client Browser", size=10,
           color=PRIMARY, bold=True)
    component(95, 150, 130, 44, "Web UI\n(HTML/CSS/JS)", T3)
    component(255, 150, 130, 44, "Ethers.js\nProvider", T2)
    component(175, 240, 130, 44, "MetaMask\nExtension", T5)
    c.line(225, 172, 255, 172, color=MUTED, w=1.2, dash=True, arrow_end=True)
    c.line(240, 240, 290, 194, color=MUTED, w=1.2, dash=True, arrow_end=True)

    # Node 2: Ethereum Sepolia
    c.rect(470, 110, 280, 200, fill=None, line=T3, line_w=1.4, radius=8)
    c.text(482, 116, 240, 12, "\u00ABnode\u00BB Ethereum Sepolia (EVM)", size=10,
           color=T3, bold=True)
    component(520, 160, 180, 50, "AcademicCertificates\n(Solidity ^0.8.0)", T3)
    component(520, 240, 180, 44, "Immutable Ledger\nmapping<string,Cert>", T4)
    c.line(610, 210, 610, 240, color=MUTED, w=1.2, dash=True, arrow_end=True)
    c.line(385, 172, 520, 185, color=MUTED, w=1.2, dash=True, arrow_end=True)
    c.text(410, 150, 110, 12, "view / tx", size=8.5, color=MUTED, italic=True)

    # Node 3: Phase-2 server (future)
    c.rect(470, 340, 280, 120, fill=None, line=MUTED, line_w=1.4, radius=8)
    c.text(482, 346, 240, 12, "\u00ABnode\u00BB Agent Server (Phase 2)", size=10,
           color=MUTED, bold=True)
    component(520, 378, 180, 44, "AI Agent\n(Web3.py / Node)", MUTED)
    component(520, 430, 180, 22, "IPFS (future)", T1)
    c.line(610, 378, 610, 284, color=MUTED, w=1.2, dash=True, arrow_end=True)
    c.text(615, 320, 110, 12, "writes (P2)", size=8.5, color=MUTED, italic=True)

    # legend
    c.rect(60, 340, 360, 120, fill=PANEL, line=BORDER, line_w=1, radius=8)
    c.text(74, 350, 330, 12, "LEGEND", size=10, color=PRIMARY, bold=True)
    c.line(80, 380, 130, 380, color=MUTED, w=1.2, dash=True, arrow_end=True)
    c.text(140, 374, 260, 12, "dependency / interface call", size=9.5, color=MUTED)
    c.rect(80, 398, 24, 16, fill=FILL[T2], line=T2, line_w=1, radius=3)
    c.text(140, 400, 260, 12, "deployable software component", size=9.5,
           color=MUTED)
    c.rect(80, 424, 24, 16, fill=None, line=PRIMARY, line_w=1.2, radius=3)
    c.text(140, 426, 260, 12, "execution / deployment node", size=9.5, color=MUTED)
    footer(c)


def s16_algorithm(c):
    c.new_page(WHITE)
    header(c, "Methodology", "Algorithm Used in Proposed Solution", 16)
    # Issuance pseudocode
    c.rect(58, 100, 412, 232, fill="#0B1220", line=PRIMARY, line_w=1.2, radius=8)
    c.text(72, 110, 384, 14, "Algorithm 1 \u2014 issueDegree (WRITE)", size=11,
           color="#7CC6FF", bold=True)
    code1 = [
        "Input : regNo, name, course, hash",
        "Pre   : caller wallet = university (RBAC)",
        "1. require(msg.sender == university)",
        "2.    else revert  // blocked at EVM",
        "3. certificates[regNo] \u2190",
        "       Certificate(name, course, hash)",
        "4. totalIssued \u2190 totalIssued + 1",
        "Cost  : O(1) write  (+ gas in SepoliaETH)",
    ]
    yy = 134
    for ln in code1:
        col = "#9FB4D6" if ln.startswith((" ", "Input", "Pre", "Cost")) else "#E6EDF7"
        c.text(80, yy, 380, 13, ln, size=10, color=col, font="Courier")
        yy += 22

    # Verification pseudocode
    c.rect(490, 100, 412, 232, fill="#0B1220", line=T4, line_w=1.2, radius=8)
    c.text(504, 110, 384, 14, "Algorithm 2 \u2014 verifyCertificate (READ)",
           size=11, color="#86EFAC", bold=True)
    code2 = [
        "Input : regNo",
        "1. data \u2190 contract.certificates(regNo)",
        "      // gasless view call via Ethers.js",
        "2. if data.studentName == \"\"  then",
        "3.    render(\"Record Not Found\")  // .error",
        "4. else",
        "5.    render(data)                // .success",
        "Cost  : O(1) read   (0 gas, instant)",
    ]
    yy = 134
    for ln in code2:
        col = "#9FB4D6" if ln.startswith((" ", "Input", "Cost")) else "#E6EDF7"
        c.text(512, yy, 380, 13, ln, size=10, color=col, font="Courier")
        yy += 22

    c.rect(58, 346, 844, 66, fill=FILL[T1], line=T1, line_w=1.2, radius=8)
    c.text(74, 356, 812, 14, "WHY O(1)?", size=11, color=T1, bold=True)
    para(c, 74, 376, 812,
         "A hash-table state mapping resolves the storage slot for a Registration "
         "Number directly, with no iteration over records \u2014 unlike array/loop "
         "designs that are O(N) and whose gas cost grows with the number of "
         "students. RBAC require() rejects unauthorized writes before gas is spent.",
         size=11.5, color=INK, lead=16)
    footer(c)


def s17_output(c):
    c.new_page(WHITE)
    header(c, "Results", "Output Screenshots", 17,
           sub="Representative UI mock-ups \u2014 replace with your actual screenshots.")
    # success portal
    browser(c, 58, 100, 410, 200, "univerify.app/verify")
    c.text(74, 132, 378, 14, "UniVerify \u2014 Certificate Verification", size=12,
           color=INK, bold=True)
    c.rect(74, 154, 280, 24, fill=WHITE, line=BORDER, line_w=1, radius=5)
    c.text(82, 154, 270, 24, "2021CSE101", size=10, color=INK, valign="m")
    c.rect(360, 154, 92, 24, fill=T2, radius=5)
    c.text(360, 154, 92, 24, "Verify", size=10, color=WHITE, bold=True, align="c",
           valign="m")
    c.rect(74, 190, 378, 92, fill=FILL[T4], line=T4, line_w=1.2, radius=6)
    c.text(86, 198, 360, 14, "\u2713 Certificate Verified", size=12, color=T4,
           bold=True)
    c.text(86, 220, 360, 12, "Name: <Student Name>", size=10, color=INK)
    c.text(86, 238, 360, 12, "Course: B.Tech CSE", size=10, color=INK)
    c.text(86, 256, 360, 12, "Hash: a1b2c3...(mock, P1)", size=10, color=MUTED)

    # error portal
    browser(c, 492, 100, 410, 200, "univerify.app/verify")
    c.text(508, 132, 378, 14, "UniVerify \u2014 Certificate Verification", size=12,
           color=INK, bold=True)
    c.rect(508, 154, 280, 24, fill=WHITE, line=BORDER, line_w=1, radius=5)
    c.text(516, 154, 270, 24, "9999XYZ000", size=10, color=INK, valign="m")
    c.rect(794, 154, 92, 24, fill=T2, radius=5)
    c.text(794, 154, 92, 24, "Verify", size=10, color=WHITE, bold=True, align="c",
           valign="m")
    c.rect(508, 190, 378, 92, fill=FILL[T6], line=T6, line_w=1.2, radius=6)
    c.text(520, 198, 360, 14, "\u2715 Record Not Found", size=12, color=T6,
           bold=True)
    para(c, 520, 222, 360, "No certificate exists for this Registration Number. "
         "Zero-state result intercepted by the safety filter.", size=10,
         color=INK, lead=14)

    # remix mock
    c.rect(58, 320, 844, 92, fill="#1E1E1E", line=BORDER, line_w=1, radius=8)
    c.text(74, 330, 812, 12, "Remix IDE \u2014 issueDegree (Admin write, Phase 1)",
           size=10.5, color="#D4D4D4", bold=True)
    for i, (lab, val) in enumerate([("_regNo", "2021CSE101"),
                                    ("_name", "Student Name"),
                                    ("_course", "B.Tech CSE"),
                                    ("_hash", "a1b2c3 (manual mock)")]):
        x = 74 + (i % 4) * 205
        c.rect(x, 352, 190, 22, fill="#2D2D2D", line="#3C3C3C", line_w=0.8, radius=4)
        c.text(x + 6, 352, 184, 22, lab + ": " + val, size=8.5, color="#9CDCFE",
               font="Courier", valign="m")
    c.rect(74, 382, 120, 22, fill=T5, radius=4)
    c.text(74, 382, 120, 22, "transact (sign)", size=9, color="#1E1E1E",
           bold=True, align="c", valign="m")
    c.text(210, 382, 500, 22, "\u2713 status: 0x1 mined  \u2014  gas used in "
           "SepoliaETH", size=9, color="#86EFAC", font="Courier", valign="m")
    footer(c)


def s18_compare(c):
    c.new_page(WHITE)
    header(c, "Evaluation", "Comparative Graph: Existing vs Proposed", 18,
           sub="Indicative qualitative scores (out of 10; higher is better).")
    cats = ["Speed", "Security", "Tamper-\nresistance", "Transparency",
            "Cost-\nefficiency", "Scalability"]
    existing = [3, 4, 2, 3, 4, 5]
    proposed = [9, 9, 10, 9, 8, 8]
    chart(c, 90, 130, 700, 300, cats, existing, proposed,
          "Existing System", "Proposed System", c1=T6, c2=T2, ymax=10)
    c.text(810, 150, 110, 12, "Lower latency,", size=9.5, color=MUTED)
    c.text(810, 166, 110, 12, "no SPOF, and", size=9.5, color=MUTED)
    c.text(810, 182, 110, 12, "immutable on-", size=9.5, color=MUTED)
    c.text(810, 198, 110, 12, "chain records", size=9.5, color=MUTED)
    c.text(810, 214, 110, 12, "drive the gains.", size=9.5, color=MUTED)
    c.text(90, 470, 700, 12,
           "Latency: ~7\u201314 days (existing)  \u2192  ~seconds (proposed). "
           "Scores are indicative for comparison, not benchmarked units.",
           size=9.5, color=MUTED, italic=True)
    footer(c)


def s19_future(c):
    c.new_page(WHITE)
    header(c, "Closing", "Future Enhancement & Conclusion", 19)
    c.text(58, 96, 420, 14, "FUTURE ENHANCEMENTS", size=11, color=T3, bold=True)
    bullets(c, 58, 116, 420, [
        ("Phase 2 AI agent.", "NLP-normalized ingestion, deterministic SHA-256 / "
         "IPFS hashing, and programmatic transaction signing."),
        ("Mainnet / Layer-2.", "Deploy on a low-fee L2 (e.g., Polygon) for "
         "production-scale, low-cost issuance."),
        ("Revocation & expiry.", "Support credential revocation and validity "
         "windows on-chain."),
        ("Multi-institution registry.", "Federated admin roles for many "
         "universities."),
        ("QR + mobile DID wallet.", "Scan-to-verify and self-sovereign holder "
         "wallets."),
    ], size=11.5, gap=8)
    c.rect(500, 100, 402, 326, fill=PANEL, line=T4, line_w=1.2, radius=8)
    c.text(516, 112, 372, 14, "CONCLUSION", size=11, color=T4, bold=True)
    para(c, 516, 134, 372,
         "UniVerify V2.0 demonstrates that academic certificate verification can be "
         "transformed from a slow, centralized, forgery-prone process into an "
         "immutable, decentralized, constant-time lookup on a public blockchain.",
         size=12, color=INK, lead=17)
    para(c, 516, 214, 372,
         "The Phase-1 prototype validates the contract\u2019s state mutability, "
         "O(1) string-keyed retrieval, RBAC guardrails, and gasless read path under "
         "a manual curation paradigm \u2014 with the data-fingerprint field held as "
         "a mock placeholder.",
         size=12, color=MUTED, lead=17)
    para(c, 516, 312, 372,
         "Phase 2 will close the loop with autonomous, cryptographically-hashed "
         "issuance, delivering an end-to-end trust-minimized credentialing system.",
         size=12, color=MUTED, lead=17)
    footer(c)


def s20_references(c):
    c.new_page(WHITE)
    header(c, "Bibliography", "References", 20,
           sub="IEEE style \u2014 add your additional cited sources as needed.")
    refs = [
        "[1]  S. Nakamoto, \u201CBitcoin: A Peer-to-Peer Electronic Cash System,\u201D 2008.",
        "[2]  V. Buterin, \u201CEthereum: A Next-Generation Smart Contract and "
        "Decentralized Application Platform,\u201D White Paper, 2014.",
        "[3]  J. Benet, \u201CIPFS \u2014 Content Addressed, Versioned, P2P File "
        "System,\u201D arXiv:1407.3561, 2014.",
        "[4]  MIT Media Lab, \u201CBlockcerts: An Open Standard for Blockchain "
        "Certificates,\u201D 2016. [Online]. Available: https://www.blockcerts.org",
        "[5]  A. Grech and A. F. Camilleri, \u201CBlockchain in Education,\u201D "
        "Joint Research Centre (JRC), European Commission, 2017.",
        "[6]  Ethereum Foundation, \u201CSolidity Documentation (v0.8.x),\u201D "
        "[Online]. Available: https://docs.soliditylang.org",
        "[7]  Ethers.js, \u201CDocumentation (v5.7),\u201D [Online]. Available: "
        "https://docs.ethers.org/v5/",
        "[8]  ConsenSys, \u201CMetaMask Developer Documentation,\u201D [Online]. "
        "Available: https://docs.metamask.io",
    ]
    y = 100
    for r in refs:
        ny = para(c, 58, y, 844, r, size=12, color=INK, lead=16)
        y = ny + 8
    c.text(58, 470, 844, 12,
           "Note: references [1]\u2013[5] are foundational works; replace or "
           "augment with the specific papers cited in your report.", size=9.5,
           color=MUTED, italic=True)
    footer(c)


SLIDES = [s01_title, s02_abstract, s03_intro, s04_litsurvey, s05_existing,
          s06_existing_arch, s07_problem, s08_proposed, s09_proposed_arch,
          s10_module, s11_usecase, s12_class, s13_sequence, s14_activity,
          s15_component, s16_algorithm, s17_output, s18_compare, s19_future,
          s20_references]


def build(canvas):
    for fn in SLIDES:
        fn(canvas)


if __name__ == "__main__":
    p = PptxCanvas()
    build(p)
    p.save("UniVerify_V2.0_ProjectReview.pptx")
    print("Saved PPTX with", len(p.prs.slides._sldIdLst), "slides")

    d = PdfCanvas("UniVerify_V2.0_ProjectReview.pdf")
    build(d)
    d.save()
    print("Saved PDF")
