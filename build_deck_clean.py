#!/usr/bin/env python3
"""
Clean, overflow-safe rebuild of the 20-slide UniVerify V2.0 academic deck.

Design rules that keep every slide aligned:
  * strict margins; a header band and footer band reserved on every slide
  * every box sizes itself to its (pre-wrapped) text -> no overflow
  * diagrams use a fixed grid; connectors are orthogonal only (no diagonals,
    no floating labels squeezed between shapes)
Run: python3 build_deck_clean.py
"""
from reportlab.pdfbase.pdfmetrics import stringWidth
from deck_engine import PptxCanvas, PdfCanvas, _wrap

# ------------------------------------------------------------------ palette
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
BORDER = "#CBD5E1"
GRID = "#EAEEF4"
FILL = {
    T1: "#D6F1F2", T2: "#E3ECFD", T3: "#EDE7FC", T4: "#DCFCE7",
    T5: "#FEF1D6", T6: "#FCE3E0", PRIMARY: "#E4E9F7", MUTED: "#EEF1F5",
}

PAGE_W, PAGE_H = 960.0, 540.0
MX = 54                 # left/right margin
CW = PAGE_W - 2 * MX    # content width = 852
TOTAL = 20


# ------------------------------------------------------------------ helpers
def _bw(s, size):
    return stringWidth(s, "Helvetica-Bold", size)


def header(c, kicker, title, num, sub=None):
    c.rect(MX, 36, 6, 30, fill=PRIMARY, radius=2)
    c.text(MX + 16, 34, 620, 14, kicker.upper(), size=11, color=T2, bold=True)
    c.text(MX + 15, 48, CW - 70, 30, title, size=22, color=INK, bold=True)
    c.text(MX, 34, CW, 14, f"{num:02d} / {TOTAL}", size=11, color=MUTED,
           bold=True, align="r")
    c.line(MX, 82, PAGE_W - MX, 82, color=BORDER, w=1.2)
    if sub:
        c.text(MX + 16, 88, CW - 32, 14, sub, size=11, color=MUTED, italic=True)
    return 112 if sub else 100


def footer(c):
    c.line(MX, 514, PAGE_W - MX, 514, color=BORDER, w=0.8)
    c.text(MX, 520, 560, 12, "UniVerify V2.0  |  B.Tech CSE \u2014 Project Review",
           size=8.5, color=MUTED)
    c.text(MX, 520, CW, 12, "Decentralized Academic Certificate Verification",
           size=8.5, color=MUTED, align="r")


def cpara(c, x, y, w, s, size=13, color=MUTED, lead=None, bold=False,
          italic=False, align="l"):
    """left/centre paragraph; one text() per wrapped line -> identical in both
    backends. returns the y after the last line."""
    lead = lead or size * 1.34
    cy = y
    for ln in _wrap(s, w, size):
        c.text(x, cy, w, size * 1.25 + 1, ln, size=size, color=color, bold=bold,
               italic=italic, align=align)
        cy += lead
    return cy


def bullets(c, x, y, w, items, size=13.5, gap=9, lead=None, accent=T2):
    """Each bullet: a bold lead-in on its own line (optional) + wrapped body."""
    lead = lead or size * 1.3
    cy = y
    for it in items:
        head, body = it if isinstance(it, tuple) else (None, it)
        c.text(x, cy + 1, 16, size, "\u25B8", size=size - 2, color=accent,
               bold=True)
        tx, tw = x + 20, w - 20
        if head:
            for ln in _wrap(head, tw, size):
                c.text(tx, cy, tw, size * 1.25 + 1, ln, size=size, color=INK,
                       bold=True)
                cy += lead
        body_color = MUTED if head else INK
        for ln in _wrap(body, tw, size):
            c.text(tx, cy, tw, size * 1.25 + 1, ln, size=size, color=body_color)
            cy += lead
        cy += gap
    return cy


def panel(c, x, y, w, h, accent=BORDER, fill=PANEL):
    c.rect(x, y, w, h, fill=fill, line=accent, line_w=1.2, radius=8)


def card(c, x, y, w, h, accent, title, body=None, tsize=12, bsize=10):
    """A rounded card with a top accent strip; title (centred) + optional body.
    Title and body are pre-wrapped and stacked so nothing ever overflows."""
    c.rect(x, y, w, h, fill=FILL.get(accent, PANEL), line=accent, line_w=1.4,
           radius=8)
    c.rect(x, y, w, 5, fill=accent, radius=2)
    tlines = []
    for part in str(title).split("\n"):
        tlines.extend(_wrap(part, w - 16, tsize))
    th = len(tlines) * tsize * 1.25
    if body:
        ty = y + 12
        c.text(x + 8, ty, w - 16, th, "\n".join(tlines), size=tsize, color=INK,
               bold=True, align="c")
        by = ty + th + 4
        blines = []
        for part in str(body).split("\n"):
            blines.extend(_wrap(part, w - 16, bsize))
        bh = len(blines) * bsize * 1.25
        avail = (y + h) - by - 8
        c.text(x + 8, by, w - 16, max(bh, avail), "\n".join(blines), size=bsize,
               color=MUTED, align="c", valign="m")
    else:
        c.text(x + 8, y + 7, w - 16, h - 12, "\n".join(tlines), size=tsize,
               color=INK, bold=True, align="c", valign="m")


def arrow(c, x1, y1, x2, y2, color=MUTED, w=1.6, dash=False):
    c.line(x1, y1, x2, y2, color=color, w=w, arrow_end=True, dash=dash)


def chiprow(c, x, y, items, size=10.5, h=30, gap=10):
    cx = x
    for label, col in items:
        wdt = _bw(label, size) + 26
        c.rect(cx, y, wdt, h, fill=FILL[col], line=col, line_w=1.1, radius=6)
        c.text(cx, y, wdt, h, label, size=size, color=INK, bold=True,
               align="c", valign="m")
        cx += wdt + gap


def table(c, x, y, widths, headers, rows, hsize=10.5, csize=10, pad=6,
          head_fill=PRIMARY):
    n = len(widths)
    xs, cx = [], x
    for wdt in widths:
        xs.append(cx)
        cx += wdt
    total = sum(widths)

    def cells_wrapped(cells, size):
        out = []
        mx = 1
        for i, cell in enumerate(cells):
            ls = _wrap(str(cell), widths[i] - 2 * pad, size)
            out.append(ls)
            mx = max(mx, len(ls))
        return out, mx * size * 1.25 + 2 * pad

    cy = y
    wrapped, hh = cells_wrapped(headers, hsize)
    c.rect(x, cy, total, hh, fill=head_fill, line=BORDER, line_w=1)
    for i, ls in enumerate(wrapped):
        c.text(xs[i] + pad, cy + pad, widths[i] - 2 * pad, hh - 2 * pad,
               "\n".join(ls), size=hsize, color=WHITE, bold=True, valign="m")
    cy += hh
    for r_idx, row in enumerate(rows):
        wrapped, rh = cells_wrapped(row, csize)
        c.rect(x, cy, total, rh, fill=(WHITE if r_idx % 2 == 0 else PANEL),
               line=BORDER, line_w=0.8)
        for i, ls in enumerate(wrapped):
            c.text(xs[i] + pad, cy + pad, widths[i] - 2 * pad, rh - 2 * pad,
                   "\n".join(ls), size=csize, color=INK, valign="m")
        cy += rh
    for cxp in xs[1:]:
        c.line(cxp, y, cxp, cy, color=BORDER, w=0.8)
    return cy


def uml_class(c, x, y, w, name, attrs, methods, accent):
    pad, asize, msize, name_h = 6, 9.5, 9.5, 22
    a_h = len(attrs) * asize * 1.25 + 2 * pad
    m_h = len(methods) * msize * 1.25 + 2 * pad
    H = name_h + a_h + m_h
    c.rect(x, y, w, H, fill=WHITE, line=accent, line_w=1.4, radius=4)
    c.rect(x, y, w, name_h, fill=FILL[accent], line=accent, line_w=1.0)
    c.text(x, y, w, name_h, name, size=11, color=INK, bold=True, align="c",
           valign="m")
    ay = y + name_h + pad
    for a in attrs:
        c.text(x + pad, ay, w - 2 * pad, asize * 1.25, a, size=asize, color=INK,
               font="Courier")
        ay += asize * 1.25
    c.line(x, y + name_h + a_h, x + w, y + name_h + a_h, color=accent, w=1.0)
    my = y + name_h + a_h + pad
    for m in methods:
        c.text(x + pad, my, w - 2 * pad, msize * 1.25, m, size=msize, color=MUTED,
               font="Courier")
        my += msize * 1.25
    return H



# ================================================================== SLIDES
def s01_title(c):
    c.rect(0, 0, PAGE_W, 8, fill=PRIMARY)
    c.text(0, 54, PAGE_W, 16, "DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING",
           size=12, color=T2, bold=True, align="c")
    c.text(0, 76, PAGE_W, 24, "<College / University Name>", size=18, color=INK,
           bold=True, align="c")
    # title panel
    panel(c, 150, 138, 660, 150, accent=PRIMARY, fill=PANEL)
    c.text(150, 156, 660, 14, "PROJECT TITLE", size=11, color=T2, bold=True,
           align="c")
    c.text(150, 176, 660, 38, "UniVerify V2.0", size=32, color=PRIMARY,
           bold=True, align="c")
    cpara(c, 190, 222, 580,
          "A Decentralized Academic Certificate Verification Protocol Using "
          "Alphanumeric Keyspace Mapping", size=13, color=INK, lead=18,
          align="c")
    c.text(0, 300, PAGE_W, 14,
           "A Final-Year B.Tech Major Project  \u2014  Submitted in partial "
           "fulfilment for the degree of B.Tech (CSE)", size=10.5, color=MUTED,
           italic=True, align="c")
    # submitted-by / guide columns
    panel(c, 150, 336, 320, 132, accent=BORDER, fill=WHITE)
    c.text(150, 348, 320, 12, "SUBMITTED BY", size=10, color=T2, bold=True,
           align="c")
    c.text(150, 372, 320, 16, "<Student Name>", size=15, color=INK, bold=True,
           align="c")
    c.text(150, 398, 320, 12, "<Roll Number>", size=11, color=MUTED, align="c")
    c.text(150, 420, 320, 12, "<Branch / Semester>", size=11, color=MUTED,
           align="c")
    panel(c, 490, 336, 320, 132, accent=BORDER, fill=WHITE)
    c.text(490, 348, 320, 12, "PROJECT GUIDE", size=10, color=T3, bold=True,
           align="c")
    c.text(490, 372, 320, 16, "<Guide Name>", size=15, color=INK, bold=True,
           align="c")
    c.text(490, 398, 320, 12, "<Designation>", size=11, color=MUTED, align="c")
    c.text(490, 420, 320, 12, "Dept. of CSE", size=11, color=MUTED, align="c")
    footer(c)


def s02_abstract(c):
    top = header(c, "Overview", "Abstract", 2,
                 sub="A one-paragraph summary of the problem, approach and result.")
    panel(c, MX, top, CW, 322, accent=PRIMARY, fill=PANEL)
    y = cpara(c, MX + 22, top + 22, CW - 44,
              "Conventional academic record verification depends on centralized "
              "databases and physical documents, introducing a single point of "
              "failure (SPOF), forgery risk, and verification latency of 7\u201314 "
              "days. UniVerify V2.0 is a decentralized verification protocol that "
              "anchors certificate records on the Ethereum Sepolia testnet through "
              "a Solidity smart contract.", size=13.5, color=INK, lead=20)
    y = cpara(c, MX + 22, y + 8, CW - 44,
              "The design replaces array/loop lookups (O(N)) with an explicit "
              "string-keyed state mapping on the Registration Number, achieving "
              "O(1) constant-time retrieval. Role-Based Access Control freezes the "
              "deploying wallet as the sole issuer, and public verification is a "
              "gasless read-only view call via Ethers.js + MetaMask.", size=13.5,
              color=MUTED, lead=20)
    cpara(c, MX + 22, y + 8, CW - 44,
          "Phase 1 (current) validates the contract under a manual curation "
          "paradigm \u2014 data is entered by hand in Remix with a mock hash "
          "placeholder. Phase 2 will add an autonomous AI agent performing "
          "SHA-256 / IPFS hashing and programmatic transaction signing.",
          size=13.5, color=MUTED, lead=20)
    footer(c)


def s03_intro(c):
    top = header(c, "Context", "Introduction", 3,
                 sub="Why blockchain-anchored credentials, and what this project delivers.")
    bullets(c, MX, top + 4, CW, [
        ("Problem domain.", "Degree and certificate verification is slow, manual "
         "and trust-dependent, relying on institutions to confirm authenticity."),
        ("Blockchain premise.", "A public, append-only ledger provides tamper-"
         "evident, independently verifiable records without a central authority."),
        ("Core idea.", "Store each certificate as a struct in a Solidity mapping "
         "keyed by the alphanumeric Registration Number for instant lookups."),
        ("Access model.", "Only the university wallet can issue records; anyone "
         "can verify them for free through a read-only call."),
        ("Scope of this report.", "Phase-1 prototype on Sepolia with manual data "
         "entry; Phase-2 automation roadmap is described as future work."),
    ], size=13.5, gap=10)
    footer(c)


def s04_litsurvey(c):
    top = header(c, "Background", "Literature Survey", 4,
                 sub="Representative prior work and the gap UniVerify V2.0 addresses.")
    table(c, MX, top + 2, [150, 322, 326],
          ["Reference / Year", "Approach", "Limitation / Gap"],
          [["Nakamoto (2008)", "Peer-to-peer electronic cash; proof-of-work ledger",
            "General ledger; not tailored to credentialing"],
           ["Buterin (2014)", "Ethereum + programmable smart contracts",
            "Enables apps but no credential schema provided"],
           ["MIT Blockcerts (2016)", "Open standard for blockchain certificates",
            "Hash/issuer focus; lookup efficiency not emphasised"],
           ["Grech & Camilleri (2017)", "Survey of blockchain in education",
            "Policy-level; lacks a concrete O(1) data model"],
           ["IPFS \u2013 Benet (2014)", "Content-addressed distributed file store",
            "Storage layer only; deferred to Phase 2 here"]])
    cpara(c, MX, 470, CW,
          "Gap: prior work proves feasibility but rarely optimises on-chain "
          "retrieval. UniVerify V2.0 contributes an explicit string-keyed mapping "
          "for O(1) verification with hardcoded RBAC.", size=10, color=MUTED,
          italic=True)
    footer(c)


def s05_existing(c):
    top = header(c, "Baseline", "Existing System", 5,
                 sub="How academic verification works today.")
    bullets(c, MX, top + 4, 470, [
        ("Centralized databases (RDBMS).", "Records held in a single institutional "
         "server or department spreadsheet."),
        ("Manual verification.", "Employers email/call the university; staff look "
         "up and confirm \u2014 7\u201314 days typical."),
        ("Paper / PDF certificates.", "Static documents that can be edited or "
         "forged without easy detection."),
        ("Custodial trust.", "Authenticity depends entirely on trusting the "
         "issuing authority and its staff."),
    ], size=13, gap=10)
    panel(c, 548, top + 4, CW - 494, 300, accent=BORDER, fill=PANEL)
    c.text(566, top + 18, CW - 530, 14, "AT A GLANCE", size=10.5, color=PRIMARY,
           bold=True)
    rows = [("Latency", "7\u201314 days"), ("Trust", "Centralized"),
            ("Tamper-evidence", "Weak"), ("Availability", "Single server"),
            ("Audit", "Manual / periodic")]
    ry = top + 40
    for k, v in rows:
        c.text(566, ry, 150, 14, k, size=11, color=INK, bold=True)
        c.text(566, ry + 17, CW - 540, 14, v, size=11, color=MUTED)
        ry += 50
    footer(c)


def s06_existing_arch(c):
    top = header(c, "Baseline", "Architecture of Existing System", 6,
                 sub="A centralized request-response pipeline with a single point of failure.")
    boxes = [("Student /\nEmployer", T2), ("Verification\nRequest", T5),
             ("University Staff\n(manual lookup)", T3),
             ("Central RDBMS /\nPaper Files", T6)]
    bw, gap, y, h = 186, (CW - 4 * 186) / 3.0, top + 30, 86
    xs = [MX + i * (bw + gap) for i in range(4)]
    for i, (label, col) in enumerate(boxes):
        card(c, xs[i], y, bw, h, col, label, tsize=12.5)
        if i < 3:
            ax1 = xs[i] + bw + 4
            ax2 = xs[i + 1] - 4
            arrow(c, ax1, y + h / 2, ax2, y + h / 2)
    # SPOF callout under last box
    c.text(xs[3], y + h + 10, bw, 14, "\u26A0  Single Point of Failure",
           size=10.5, color=T6, bold=True, align="c")
    panel(c, MX, y + h + 40, CW, 120, accent=T6, fill=FILL[T6])
    c.text(MX + 18, y + h + 52, CW - 36, 14, "RISKS OF THE CENTRALIZED MODEL",
           size=11, color=T6, bold=True)
    bullets(c, MX + 18, y + h + 74, CW - 36, [
        (None, "Server breach or insider edits can silently alter records."),
        (None, "Downtime blocks all verification; no independent cross-check."),
        (None, "Forged PDFs are hard to detect without manual institutional audit."),
    ], size=11, gap=3, accent=T6)
    footer(c)


def s07_problem(c):
    top = header(c, "Motivation", "Drawbacks & Problem Statement", 7,
                 sub="The specific deficiencies this project sets out to solve.")
    bullets(c, MX, top + 4, CW, [
        ("Single Point of Failure (SPOF).", "A central server is vulnerable to "
         "breach, insider modification and outage."),
        ("High latency & overhead.", "Manual lookups take 7\u201314 days and incur "
         "recurring administrative cost."),
        ("Forgery & tampering.", "Unanchored PDFs and paper can be visually "
         "manipulated; detection needs redundant audits."),
        ("No independent verification.", "Third parties cannot confirm a record "
         "without trusting (and contacting) the issuer."),
    ], size=13.5, gap=10)
    panel(c, MX, 392, CW, 84, accent=PRIMARY, fill=PANEL)
    c.text(MX + 18, 404, CW - 36, 14, "PROBLEM STATEMENT", size=11, color=PRIMARY,
           bold=True)
    cpara(c, MX + 18, 426, CW - 36,
          "Design a decentralized, tamper-evident certificate verification system "
          "that offers instant, gasless, independently verifiable lookups while "
          "restricting issuance to an authorized authority.", size=12, color=INK,
          lead=17)
    footer(c)


def s08_proposed(c):
    top = header(c, "Solution", "Proposed System", 8,
                 sub="A decentralized, constant-time verification protocol on Ethereum.")
    bullets(c, MX, top + 4, 488, [
        ("On-chain anchoring.", "Records written to a Solidity contract on Sepolia "
         "\u2014 immutable once mined."),
        ("O(1) keyspace mapping.", "mapping(string => Certificate) keyed by "
         "Registration Number; no search loops."),
        ("Role-Based Access Control.", "Constructor freezes the deployer as sole "
         "admin; unauthorized writes revert."),
        ("Gasless verification.", "Read-only view call via Ethers.js \u2014 instant "
         "and free."),
        ("Safety filter.", "Blank zero-state results shown as \u201CRecord Not "
         "Found\u201D."),
    ], size=12.5, gap=9)
    panel(c, 560, top + 4, CW - 506, 250, accent=PRIMARY, fill=PANEL)
    c.text(578, top + 16, CW - 540, 14, "KEY BENEFITS", size=10.5, color=PRIMARY,
           bold=True)
    bx = 578
    by = top + 40
    for label, col in [("Immutable", T3), ("O(1) lookup", T4), ("No SPOF", T6),
                       ("Gasless reads", T1), ("RBAC-secured", T2),
                       ("Global access", T5)]:
        c.rect(bx, by, CW - 540, 28, fill=FILL[col], line=col, line_w=1.0,
               radius=6)
        c.text(bx, by, CW - 540, 28, label, size=11, color=INK, bold=True,
               align="c", valign="m")
        by += 34
    panel(c, MX, 392, CW, 84, accent=T5, fill=FILL[T5])
    c.text(MX + 18, 404, CW - 36, 14, "PHASE NOTE", size=11, color=T5, bold=True)
    cpara(c, MX + 18, 426, CW - 36,
          "Phase 1 uses manual entry in Remix with a mock hash placeholder; real "
          "SHA-256 / IPFS hashing and an autonomous AI agent arrive in Phase 2.",
          size=12, color=INK, lead=17)
    footer(c)


def s09_proposed_arch(c):
    top = header(c, "Solution", "Architecture of Proposed System", 9,
                 sub="Write path (admin, costs gas) and read path (verifier, gasless).")
    bw, h, gap = 150, 70, 36
    start_x = MX + 110
    xs = [start_x + i * (bw + gap) for i in range(3)]   # 164, 350, 536
    contract_x = 706
    contract_w = PAGE_W - MX - contract_x               # 200
    last_right = xs[2] + bw                             # 686
    # contract (shared, right) spanning both lanes
    contract_y = top + 18
    card(c, contract_x, contract_y, contract_w, 196, T3,
         "AcademicCertificates\n(Solidity \u2014 Sepolia EVM)",
         "mapping(string=>Certificate)\nImmutable ledger", tsize=11, bsize=9.5)
    # WRITE lane
    wy = top + 18
    panel(c, MX, wy, 98, h, accent=T2, fill=FILL[T2])
    c.text(MX, wy, 98, h, "WRITE PATH\n(admin)", size=11, color=T2, bold=True,
           align="c", valign="m")
    write_boxes = [("University\nAdmin", T2), ("MetaMask\n(sign + gas)", T5),
                   ("issueDegree()\nstate write", T2)]
    for i, (label, col) in enumerate(write_boxes):
        card(c, xs[i], wy, bw, h, col, label, tsize=11.5)
        if i < 2:
            arrow(c, xs[i] + bw + 3, wy + h / 2, xs[i + 1] - 3, wy + h / 2,
                  color=T2)
    arrow(c, last_right + 3, wy + h / 2, contract_x - 3, wy + h / 2, color=T2)
    # READ lane
    ry = top + 134
    panel(c, MX, ry, 98, h, accent=T4, fill=FILL[T4])
    c.text(MX, ry, 98, h, "READ PATH\n(verifier)", size=11, color=T4, bold=True,
           align="c", valign="m")
    read_boxes = [("Verifier /\nRecruiter", T4), ("Web UI +\nEthers.js", T4),
                  ("certificates()\nview \u2014 0 gas", T1)]
    for i, (label, col) in enumerate(read_boxes):
        card(c, xs[i], ry, bw, h, col, label, tsize=11.5)
        if i < 2:
            arrow(c, xs[i] + bw + 3, ry + h / 2, xs[i + 1] - 3, ry + h / 2,
                  color=T4)
    arrow(c, last_right + 3, ry + h / 2, contract_x - 3, ry + h / 2, color=T4)
    panel(c, MX, ry + h + 28, CW, 70, accent=BORDER, fill=PANEL)
    c.text(MX + 18, ry + h + 40, CW - 36, 14, "NETWORK", size=10.5,
           color=PRIMARY, bold=True)
    cpara(c, MX + 18, ry + h + 60, CW - 36,
          "Public Ethereum Sepolia testnet \u2014 EVM execution, no central host. "
          "Writes are signed transactions (gas); reads are free view calls.",
          size=11, color=MUTED, lead=15)
    footer(c)


def s10_module(c):
    top = header(c, "Design", "Module Diagram", 10,
                 sub="The system decomposed into six cooperating modules.")
    c.rect(MX, top + 6, CW, 30, fill=FILL[PRIMARY], line=PRIMARY, line_w=1.2,
           radius=6)
    c.text(MX, top + 6, CW, 30, "UniVerify V2.0  \u2014  System Modules", size=13,
           color=PRIMARY, bold=True, align="c", valign="m")
    mods = [
        ("Smart Contract", "struct, mapping,\nRBAC require()", T2),
        ("Admin & Issuance", "issueDegree(),\nMetaMask signing", T5),
        ("Web3 Provider", "Ethers.js +\nMetaMask bridge", T1),
        ("Verification", "view call +\nsafety filter", T4),
        ("UI / Result", "#regInput,\n#result states", T3),
        ("AI Agent (Phase 2)", "NLP + SHA-256 /\nIPFS, auto-sign", MUTED),
    ]
    cols, rows = 3, 2
    gx, gy = 22, 22
    cw_box = (CW - (cols - 1) * gx) / cols
    ch = 120
    y0 = top + 52
    for idx, (title, body, col) in enumerate(mods):
        r, cc = divmod(idx, cols)
        x = MX + cc * (cw_box + gx)
        y = y0 + r * (ch + gy)
        card(c, x, y, cw_box, ch, col, title, body, tsize=13, bsize=10.5)
    footer(c)



def _actor(c, x, y, w, label, accent):
    h = 54
    c.rect(x, y, w, h, fill=WHITE, line=accent, line_w=1.6, radius=8)
    c.rect(x, y, w, 5, fill=accent, radius=2)
    c.text(x + 6, y + 9, w - 12, 12, "ACTOR", size=8.5, color=accent, bold=True,
           align="c")
    c.text(x + 6, y + 24, w - 12, 24, label, size=11, color=INK, bold=True,
           align="c")
    return h


def _oval(c, x, y, w, h, label, accent):
    c.ellipse(x, y, w, h, fill=FILL[accent], line=accent, line_w=1.2)
    c.text(x, y, w, h, label, size=10, color=INK, bold=True, align="c",
           valign="m")


def s11_usecase(c):
    top = header(c, "UML \u2014 1 / 5", "Use Case Diagram", 11,
                 sub="Actors and the use cases they trigger inside the system.")
    bx, by, bw, bh = 300, top + 18, 360, 332
    c.rect(bx, by, bw, bh, fill=None, line=PRIMARY, line_w=1.4, radius=10)
    c.text(bx, by + 8, bw, 14, "UniVerify V2.0", size=12, color=PRIMARY,
           bold=True, align="c")
    # actors
    la_y, ra_y = by + 120, by + 120
    _actor(c, MX, la_y, 150, "University Admin", T2)
    _actor(c, PAGE_W - MX - 150, ra_y, 150, "Verifier / Recruiter", T4)
    # admin use cases (inner-left column)
    admin = [("Deploy Contract", by + 40), ("Connect Wallet", by + 110),
             ("Issue Degree", by + 180)]
    for label, oy in admin:
        _oval(c, bx + 20, oy, 150, 40, label, T2)
        c.line(MX + 150, la_y + 27, bx + 20, oy + 20, color=MUTED, w=1.1)
    # verifier use cases (inner-right column)
    ver = [("Enter Reg. No.", by + 70), ("Verify Certificate", by + 150),
           ("View Result", by + 230)]
    for label, oy in ver:
        _oval(c, bx + 190, oy, 150, 40, label, T4)
        c.line(PAGE_W - MX - 150, ra_y + 27, bx + 190 + 150, oy + 20,
               color=MUTED, w=1.1)
    footer(c)


def s12_class(c):
    top = header(c, "UML \u2014 2 / 5", "Class Diagram (Model Classes)", 12,
                 sub="Domain model: contract, record struct, frontend, Phase-2 agent.")
    lx, rx = MX, 520
    lw, rw = 380, 365
    ty = top + 6
    by = 300
    h_tl = uml_class(c, lx, ty, lw, "AcademicCertificates",
                     ["+ certificates: map<string,Cert>",
                      "+ totalIssued: uint256",
                      "+ university: address"],
                     ["+ constructor()",
                      "+ issueDegree(regNo,name,course,hash)",
                      "# require(sender==university)",
                      "+ certificates(regNo): view"], accent=T2)
    h_tr = uml_class(c, rx, ty, rw, "Certificate  (struct)",
                     ["+ studentName: string",
                      "+ courseName: string",
                      "+ ipfsHash: string  // mock (P1)"],
                     ["+ isEmpty(): bool"], accent=T3)
    h_bl = uml_class(c, lx, by, lw, "VerificationPortal",
                     ["- provider: Web3Provider",
                      "- contract: Contract",
                      "- result: DOMElement"],
                     ["+ connectWallet()",
                      "+ verifyCertificate(regNo)",
                      "+ renderResult(data)"], accent=T4)
    h_br = uml_class(c, rx, by, rw, "AIAgent  (Phase 2)",
                     ["- wallet: SecureWallet",
                      "- web3: Web3"],
                     ["+ ingestLogs()",
                      "+ normalize()",
                      "+ computeHash(): bytes32",
                      "+ signAndBroadcast()"], accent=MUTED)
    # TL -- TR composition (horizontal, in the column gap)
    cy = ty + 110
    c.diamond(lx + lw, cy - 6, 14, 12, fill=INK, line=INK)
    c.line(lx + lw + 14, cy, rx, cy, color=INK, w=1.2)
    c.text(lx + lw + 8, cy - 22, rx - (lx + lw) - 16, 12, "1            *",
           size=9, color=MUTED, align="c")
    c.text(lx + lw + 8, cy + 6, rx - (lx + lw) - 16, 12, "stores", size=9,
           color=MUTED, italic=True, align="c")
    # BL ..> TL  uses (vertical)
    c.line(lx + 90, by, lx + 90, ty + h_tl, color=MUTED, w=1.2, dash=True,
           arrow_end=True)
    c.text(lx + 98, (ty + h_tl + by) / 2 - 6, 180, 12,
           "\u00ABuses\u00BB certificates()", size=9, color=MUTED, italic=True)
    # BR ..> TR populates (vertical)
    c.line(rx + 90, by, rx + 90, ty + h_tr, color=MUTED, w=1.2, dash=True,
           arrow_end=True)
    c.text(rx + 98, (ty + h_tr + by) / 2 - 6, 200, 12,
           "\u00ABpopulates\u00BB (Phase 2)", size=9, color=MUTED, italic=True)
    footer(c)


def s13_sequence(c):
    top = header(c, "UML \u2014 3 / 5", "Sequence Diagram (Verification)", 13,
                 sub="Gasless read-path message flow between client and contract.")
    objs = [("Verifier", 140, T4), ("VerificationPortal\n(Ethers.js)", 375, T2),
            ("MetaMask\nProvider", 605, T5),
            ("AcademicCertificates\n(Sepolia)", 830, T3)]
    head_y, h = top + 8, 42
    bottom = 470
    X = {}
    for name, cx, col in objs:
        c.rect(cx - 78, head_y, 156, h, fill=FILL[col], line=col, line_w=1.2,
               radius=6)
        c.text(cx - 78, head_y, 156, h, name, size=10, color=INK, bold=True,
               align="c", valign="m")
        c.line(cx, head_y + h, cx, bottom, color=BORDER, w=1.0, dash=True)
        X[name] = cx

    def msg(a, b, y, label, col=INK, ret=False):
        x1, x2 = X[a], X[b]
        c.line(x1, y, x2, y, color=col, w=1.4, arrow_end=True, dash=ret)
        left = min(x1, x2)
        c.text(left + 8, y - 14, abs(x2 - x1) - 16, 12, label, size=9,
               color=MUTED, align="c")

    A, B = "Verifier", "VerificationPortal\n(Ethers.js)"
    Cc, D = "MetaMask\nProvider", "AcademicCertificates\n(Sepolia)"
    msg(A, B, 180, "1: enter regNo, click Verify", col=T4)
    msg(B, Cc, 215, "2: Web3Provider(window.ethereum)", col=T2)
    msg(Cc, B, 248, "provider ready", col=MUTED, ret=True)
    msg(B, D, 288, "3: certificates(regNo)  [view, 0 gas]", col=T2)
    msg(D, B, 321, "4: struct / zero-state", col=MUTED, ret=True)
    # self message at Portal
    px = X[B]
    c.line(px, 356, px + 66, 356, color=INK, w=1.3)
    c.line(px + 66, 356, px + 66, 378, color=INK, w=1.3)
    c.line(px + 66, 378, px, 378, color=INK, w=1.3, arrow_end=True)
    c.text(px + 8, 344, 220, 12, "5: validate studentName != \u201C\u201D",
           size=9, color=MUTED)
    msg(B, A, 410, "6: render success / Record Not Found", col=T4)
    footer(c)


def s14_activity(c):
    top = header(c, "UML \u2014 4 / 5", "Activity Diagram", 14,
                 sub="Issuance (write) and verification (read) control flow.")
    lcx, rcx = 210, 700
    c.text(MX, top + 4, 300, 12, "ISSUANCE  (write path)", size=10.5, color=T2,
           bold=True)
    c.text(560, top + 4, 340, 12, "VERIFICATION  (read path)", size=10.5,
           color=T4, bold=True)

    def start(cx, y):
        c.ellipse(cx - 9, y, 18, 18, fill=INK)

    def end(cx, y):
        c.ellipse(cx - 9, y, 18, 18, fill=None, line=INK, line_w=1.5)
        c.ellipse(cx - 5, y + 4, 10, 10, fill=INK)

    def vbox(cx, y, label, col, w=156, h=42):
        card(c, cx - w / 2, y, w, h, col, label, tsize=10.5)

    def vdown(cx, y1, y2):
        c.line(cx, y1, cx, y2, color=MUTED, w=1.4, arrow_end=True)

    # LEFT
    start(lcx, top + 22)
    vdown(lcx, top + 40, top + 56)
    vbox(lcx, top + 56, "Admin enters\ndata (Remix)", T5)
    vdown(lcx, top + 98, top + 114)
    c.diamond(lcx - 58, top + 114, 116, 56, fill=FILL[T2], line=T2, line_w=1.2)
    c.text(lcx - 58, top + 114, 116, 56, "msg.sender\n== admin?", size=9,
           color=INK, align="c", valign="m")
    c.line(lcx + 58, top + 142, lcx + 96, top + 142, color=MUTED, w=1.4,
           arrow_end=True)
    c.text(lcx + 60, top + 128, 40, 12, "no", size=9, color=T6)
    card(c, lcx + 96, top + 120, 130, 44, T6, "Revert tx\n(no gas wasted)",
         tsize=10)
    vdown(lcx, top + 170, top + 188)
    c.text(lcx + 6, top + 172, 40, 12, "yes", size=9, color=T4)
    vbox(lcx, top + 188, "Write record\n& mine block", T4)
    vdown(lcx, top + 230, top + 248)
    end(lcx, top + 248)
    # RIGHT
    start(rcx, top + 22)
    vdown(rcx, top + 40, top + 56)
    vbox(rcx, top + 56, "Verifier enters\nReg. No.", T4)
    vdown(rcx, top + 98, top + 110)
    vbox(rcx, top + 110, "view call\ncertificates()", T1)
    vdown(rcx, top + 152, top + 168)
    c.diamond(rcx - 58, top + 168, 116, 56, fill=FILL[T3], line=T3, line_w=1.2)
    c.text(rcx - 58, top + 168, 116, 56, "studentName\nempty?", size=9,
           color=INK, align="c", valign="m")
    c.line(rcx + 58, top + 196, rcx + 96, top + 196, color=MUTED, w=1.4,
           arrow_end=True)
    c.text(rcx + 60, top + 182, 40, 12, "yes", size=9, color=T6)
    card(c, rcx + 96, top + 174, 130, 44, T6, "Show\n\u201CNot Found\u201D",
         tsize=10)
    vdown(rcx, top + 224, top + 242)
    c.text(rcx + 6, top + 226, 40, 12, "no", size=9, color=T4)
    vbox(rcx, top + 242, "Show Verified\nCertificate", T4)
    vdown(rcx, top + 284, top + 302)
    end(rcx, top + 302)
    footer(c)


def s15_component(c):
    top = header(c, "UML \u2014 5 / 5", "Component / Deployment Diagram", 15,
                 sub="Components grouped by deployment node; dashed = dependency.")

    def comp(x, y, w, h, name, col):
        c.rect(x, y, w, h, fill=FILL[col], line=col, line_w=1.3, radius=4)
        c.rect(x - 5, y + 8, 12, 8, fill=WHITE, line=col, line_w=1)
        c.rect(x - 5, y + 22, 12, 8, fill=WHITE, line=col, line_w=1)
        c.text(x + 10, y, w - 16, h, name, size=10, color=INK, bold=True,
               align="c", valign="m")

    # Node 1: Client Browser
    n1x, n1y, n1w, n1h = MX, top + 6, 400, 206
    c.rect(n1x, n1y, n1w, n1h, fill=None, line=PRIMARY, line_w=1.4, radius=8)
    c.text(n1x + 12, n1y + 8, 260, 12, "\u00ABnode\u00BB Client Browser",
           size=10, color=PRIMARY, bold=True)
    comp(n1x + 30, n1y + 36, 160, 46, "Web UI\n(HTML/CSS/JS)", T3)
    comp(n1x + 218, n1y + 36, 150, 46, "Ethers.js\nProvider", T2)
    comp(n1x + 124, n1y + 128, 160, 46, "MetaMask\nExtension", T5)
    c.line(n1x + 190, n1y + 59, n1x + 218, n1y + 59, color=MUTED, w=1.2,
           dash=True, arrow_end=True)
    c.line(n1x + 250, n1y + 82, n1x + 210, n1y + 128, color=MUTED, w=1.2,
           dash=True, arrow_end=True)
    # Node 2: Sepolia
    n2x, n2y, n2w, n2h = 478, top + 6, 428, 150
    c.rect(n2x, n2y, n2w, n2h, fill=None, line=T3, line_w=1.4, radius=8)
    c.text(n2x + 12, n2y + 8, 320, 12, "\u00ABnode\u00BB Ethereum Sepolia (EVM)",
           size=10, color=T3, bold=True)
    comp(n2x + 42, n2y + 34, 344, 44, "AcademicCertificates (Solidity ^0.8.0)", T3)
    comp(n2x + 42, n2y + 90, 344, 44, "Immutable Ledger  mapping<string,Cert>", T4)
    c.line(n2x + 214, n2y + 78, n2x + 214, n2y + 90, color=MUTED, w=1.2,
           dash=True, arrow_end=True)
    # Node 3: Agent server (P2)
    n3x, n3y, n3w, n3h = 478, top + 176, 428, 120
    c.rect(n3x, n3y, n3w, n3h, fill=None, line=MUTED, line_w=1.4, radius=8)
    c.text(n3x + 12, n3y + 8, 320, 12, "\u00ABnode\u00BB Agent Server (Phase 2)",
           size=10, color=MUTED, bold=True)
    comp(n3x + 42, n3y + 32, 344, 40, "AI Agent  (Web3.py / Node)", MUTED)
    comp(n3x + 42, n3y + 80, 344, 26, "IPFS (future)", T1)
    # cross-node deps
    c.line(n1x + n1w, n1y + 100, n2x, n1y + 100, color=MUTED, w=1.2, dash=True,
           arrow_end=True)
    c.text(n1x + n1w + 4, n1y + 84, 70, 12, "view / tx", size=8.5, color=MUTED,
           italic=True)
    c.line(n3x + 214, n3y, n3x + 214, n2y + n2h, color=MUTED, w=1.2, dash=True,
           arrow_end=True)
    c.text(n3x + 220, (n3y + n2y + n2h) / 2 - 6, 90, 12, "writes (P2)",
           size=8.5, color=MUTED, italic=True)
    # legend
    lx, ly, lw, lh = MX, top + 224, 400, 78
    panel(c, lx, ly, lw, lh, accent=BORDER, fill=PANEL)
    c.text(lx + 14, ly + 8, lw - 28, 12, "LEGEND", size=10, color=PRIMARY,
           bold=True)
    c.line(lx + 16, ly + 32, lx + 60, ly + 32, color=MUTED, w=1.2, dash=True,
           arrow_end=True)
    c.text(lx + 70, ly + 26, lw - 90, 12, "dependency / interface call",
           size=9.5, color=MUTED)
    c.rect(lx + 16, ly + 48, 22, 14, fill=FILL[T2], line=T2, line_w=1, radius=3)
    c.text(lx + 70, ly + 48, lw - 90, 12, "deployable component", size=9.5,
           color=MUTED, valign="m")
    c.rect(lx + 210, ly + 48, 22, 14, fill=None, line=PRIMARY, line_w=1.2,
           radius=3)
    c.text(lx + 240, ly + 48, lw - 250, 12, "deployment node", size=9.5,
           color=MUTED, valign="m")
    footer(c)



def s16_algorithm(c):
    top = header(c, "Methodology", "Algorithm Used in Proposed Solution", 16,
                 sub="Constant-time write and read, with RBAC enforced before gas.")
    DARK = "#0B1220"
    pw = 412
    # WRITE
    c.rect(MX, top + 4, pw, 224, fill=DARK, line=T2, line_w=1.2, radius=8)
    c.text(MX + 14, top + 14, pw - 28, 14, "Algorithm 1 \u2014 issueDegree (WRITE)",
           size=11, color="#7CC6FF", bold=True)
    code1 = ["Input : regNo, name, course, hash",
             "Pre   : caller == university  (RBAC)",
             "1. require(msg.sender==university)",
             "2.    else revert   // EVM blocks tx",
             "3. certificates[regNo] <-",
             "      Certificate(name,course,hash)",
             "4. totalIssued <- totalIssued + 1",
             "Cost  : O(1) write  (+ gas, Sepolia)"]
    yy = top + 36
    for ln in code1:
        col = "#9FB4D6" if ln[:1] == " " or ln.split(":")[0] in (
            "Input ", "Pre   ", "Cost  ") else "#E6EDF7"
        c.text(MX + 16, yy, pw - 30, 14, ln, size=10, color=col, font="Courier")
        yy += 22
    # READ
    c.rect(494, top + 4, pw, 224, fill=DARK, line=T4, line_w=1.2, radius=8)
    c.text(494 + 14, top + 14, pw - 28, 14,
           "Algorithm 2 \u2014 verifyCertificate (READ)", size=11,
           color="#86EFAC", bold=True)
    code2 = ["Input : regNo",
             "1. data <- contract.certificates(regNo)",
             "      // gasless view call (Ethers.js)",
             "2. if data.studentName == \"\" then",
             "3.    render(\"Record Not Found\")",
             "4. else",
             "5.    render(data)   // verified card",
             "Cost  : O(1) read   (0 gas, instant)"]
    yy = top + 36
    for ln in code2:
        col = "#9FB4D6" if ln[:1] == " " or ln.split(":")[0] in (
            "Input ", "Cost  ") else "#E6EDF7"
        c.text(494 + 16, yy, pw - 30, 14, ln, size=10, color=col, font="Courier")
        yy += 22
    panel(c, MX, top + 240, CW, 80, accent=T1, fill=FILL[T1])
    c.text(MX + 16, top + 250, CW - 32, 14, "WHY O(1)?", size=11, color=T1,
           bold=True)
    cpara(c, MX + 16, top + 270, CW - 32,
          "A hash-table state mapping resolves the storage slot for a Registration "
          "Number directly, with no iteration \u2014 unlike array/loop designs that "
          "are O(N) and whose gas grows with the record count. RBAC require() "
          "rejects unauthorized writes before any gas is spent.", size=11,
          color=INK, lead=16)
    footer(c)


def s17_output(c):
    top = header(c, "Results", "Output Screenshots", 17,
                 sub="Representative UI mock-ups \u2014 replace with your real screenshots.")

    def browser(x, y, w, h, url):
        c.rect(x, y, w, h, fill=WHITE, line=BORDER, line_w=1.2, radius=8)
        c.rect(x, y, w, 24, fill=PANEL, line=BORDER, line_w=1, radius=8)
        for i, cc in enumerate([T6, T5, T4]):
            c.ellipse(x + 12 + i * 16, y + 8, 9, 9, fill=cc)
        c.rect(x + 70, y + 5, w - 84, 14, fill=WHITE, line=BORDER, line_w=0.8,
               radius=4)
        c.text(x + 78, y + 5, w - 96, 14, url, size=8, color=MUTED, valign="m")

    # success
    browser(MX, top + 4, 410, 196, "univerify.app/verify")
    c.text(MX + 16, top + 36, 378, 14, "UniVerify \u2014 Verify Certificate",
           size=12, color=INK, bold=True)
    c.rect(MX + 16, top + 58, 270, 24, fill=WHITE, line=BORDER, line_w=1,
           radius=5)
    c.text(MX + 24, top + 58, 254, 24, "2021CSE101", size=10, color=INK,
           valign="m")
    c.rect(MX + 296, top + 58, 96, 24, fill=T2, radius=5)
    c.text(MX + 296, top + 58, 96, 24, "Verify", size=10, color=WHITE, bold=True,
           align="c", valign="m")
    c.rect(MX + 16, top + 94, 378, 92, fill=FILL[T4], line=T4, line_w=1.2,
           radius=6)
    c.text(MX + 28, top + 102, 354, 14, "\u2713 Certificate Verified", size=12,
           color=T4, bold=True)
    c.text(MX + 28, top + 124, 354, 12, "Name:   <Student Name>", size=10,
           color=INK)
    c.text(MX + 28, top + 142, 354, 12, "Course: B.Tech CSE", size=10, color=INK)
    c.text(MX + 28, top + 160, 354, 12, "Hash:   a1b2c3\u2026 (mock, Phase 1)",
           size=10, color=MUTED)
    # error
    browser(494, top + 4, 410, 196, "univerify.app/verify")
    c.text(494 + 16, top + 36, 378, 14, "UniVerify \u2014 Verify Certificate",
           size=12, color=INK, bold=True)
    c.rect(494 + 16, top + 58, 270, 24, fill=WHITE, line=BORDER, line_w=1,
           radius=5)
    c.text(494 + 24, top + 58, 254, 24, "9999XYZ000", size=10, color=INK,
           valign="m")
    c.rect(494 + 296, top + 58, 96, 24, fill=T2, radius=5)
    c.text(494 + 296, top + 58, 96, 24, "Verify", size=10, color=WHITE,
           bold=True, align="c", valign="m")
    c.rect(494 + 16, top + 94, 378, 92, fill=FILL[T6], line=T6, line_w=1.2,
           radius=6)
    c.text(494 + 28, top + 102, 354, 14, "\u2715 Record Not Found", size=12,
           color=T6, bold=True)
    cpara(c, 494 + 28, top + 126, 354,
          "No certificate exists for this Registration Number. Zero-state result "
          "intercepted by the safety filter.", size=10, color=INK, lead=14)
    # remix bar
    ry = top + 212
    c.rect(MX, ry, CW, 92, fill="#1E1E1E", line=BORDER, line_w=1, radius=8)
    c.text(MX + 16, ry + 10, CW - 32, 12,
           "Remix IDE \u2014 issueDegree (Admin write, Phase 1)", size=10.5,
           color="#D4D4D4", bold=True)
    fields = [("_regNo", "2021CSE101"), ("_name", "Student Name"),
              ("_course", "B.Tech CSE"), ("_hash", "a1b2c3 (manual mock)")]
    for i, (lab, val) in enumerate(fields):
        x = MX + 16 + i * 208
        c.rect(x, ry + 32, 192, 22, fill="#2D2D2D", line="#3C3C3C", line_w=0.8,
               radius=4)
        c.text(x + 6, ry + 32, 180, 22, lab + ": " + val, size=8.5,
               color="#9CDCFE", font="Courier", valign="m")
    c.rect(MX + 16, ry + 62, 122, 22, fill=T5, radius=4)
    c.text(MX + 16, ry + 62, 122, 22, "transact (sign)", size=9, color="#1E1E1E",
           bold=True, align="c", valign="m")
    c.text(MX + 150, ry + 62, 500, 22,
           "\u2713 status: 0x1 mined  \u2014  gas used (SepoliaETH)", size=9,
           color="#86EFAC", font="Courier", valign="m")
    footer(c)


def _chart(c, x, y, w, h, cats, s1, s2, lab1, lab2, c1, c2, ymax=10):
    steps = 5
    for i in range(steps + 1):
        gy = y + h - h * i / steps
        c.line(x, gy, x + w, gy, color=GRID, w=0.8)
        c.text(x - 28, gy - 6, 24, 12, str(int(ymax * i / steps)), size=8.5,
               color=MUTED, align="r")
    c.line(x, y, x, y + h, color=BORDER, w=1.2)
    c.line(x, y + h, x + w, y + h, color=BORDER, w=1.2)
    n = len(cats)
    gw = w / n
    bw = gw * 0.26
    for i in range(n):
        gcx = x + gw * i + gw / 2
        h1 = h * s1[i] / ymax
        h2 = h * s2[i] / ymax
        c.rect(gcx - bw - 3, y + h - h1, bw, h1, fill=c1)
        c.rect(gcx + 3, y + h - h2, bw, h2, fill=c2)
        c.text(gcx - gw / 2, y + h + 6, gw, 26, cats[i], size=8.5, color=INK,
               align="c")


def s18_compare(c):
    top = header(c, "Evaluation", "Comparative Graph: Existing vs Proposed", 18,
                 sub="Indicative qualitative scores (out of 10; higher is better).")
    chiprow(c, 560, top + 2, [("Existing System", T6), ("Proposed System", T2)],
            size=10, h=26)
    cats = ["Speed", "Security", "Tamper-\nresistance", "Transparency",
            "Cost-\nefficiency", "Scalability"]
    _chart(c, 110, top + 44, 740, 244, cats, [3, 4, 2, 3, 4, 5],
           [9, 9, 10, 9, 8, 8], "Existing", "Proposed", T6, T2, ymax=10)
    cpara(c, 110, 466, 740,
          "Latency: ~7\u201314 days (existing) \u2192 ~seconds (proposed). Scores "
          "are indicative for comparison, not benchmarked units.", size=9.5,
          color=MUTED, italic=True)
    footer(c)


def s19_future(c):
    top = header(c, "Closing", "Future Enhancement & Conclusion", 19)
    c.text(MX, top, 470, 14, "FUTURE ENHANCEMENTS", size=11, color=T3, bold=True)
    bullets(c, MX, top + 20, 470, [
        ("Phase 2 AI agent.", "NLP-normalized ingestion, SHA-256 / IPFS hashing, "
         "programmatic transaction signing."),
        ("Mainnet / Layer-2.", "Deploy on a low-fee L2 (e.g., Polygon) for "
         "production scale."),
        ("Revocation & expiry.", "On-chain credential revocation and validity "
         "windows."),
        ("Multi-institution registry.", "Federated admin roles for many "
         "universities."),
        ("QR + mobile DID wallet.", "Scan-to-verify and self-sovereign holder "
         "wallets."),
    ], size=12, gap=8)
    panel(c, 548, top, CW - 494, 348, accent=T4, fill=PANEL)
    c.text(548 + 16, top + 12, CW - 526, 14, "CONCLUSION", size=11, color=T4,
           bold=True)
    y = cpara(c, 548 + 16, top + 34, CW - 526,
              "UniVerify V2.0 turns certificate verification from a slow, "
              "centralized, forgery-prone process into an immutable, decentralized, "
              "constant-time lookup on a public blockchain.", size=12, color=INK,
              lead=17)
    y = cpara(c, 548 + 16, y + 8, CW - 526,
              "The Phase-1 prototype validates state mutability, O(1) string-keyed "
              "retrieval, RBAC guardrails and the gasless read path under a manual "
              "curation paradigm \u2014 with the data-fingerprint held as a mock "
              "placeholder.", size=12, color=MUTED, lead=17)
    cpara(c, 548 + 16, y + 8, CW - 526,
          "Phase 2 closes the loop with autonomous, cryptographically-hashed "
          "issuance for an end-to-end trust-minimized system.", size=12,
          color=MUTED, lead=17)
    footer(c)


def s20_references(c):
    top = header(c, "Bibliography", "References", 20,
                 sub="IEEE style \u2014 add the specific sources cited in your report.")
    refs = [
        "[1]  S. Nakamoto, \u201CBitcoin: A Peer-to-Peer Electronic Cash System,\u201D 2008.",
        "[2]  V. Buterin, \u201CEthereum: A Next-Generation Smart Contract and "
        "Decentralized Application Platform,\u201D White Paper, 2014.",
        "[3]  J. Benet, \u201CIPFS \u2014 Content-Addressed, Versioned, P2P File "
        "System,\u201D arXiv:1407.3561, 2014.",
        "[4]  MIT Media Lab, \u201CBlockcerts: An Open Standard for Blockchain "
        "Certificates,\u201D 2016. Available: https://www.blockcerts.org",
        "[5]  A. Grech, A. F. Camilleri, \u201CBlockchain in Education,\u201D Joint "
        "Research Centre, European Commission, 2017.",
        "[6]  Ethereum Foundation, \u201CSolidity Documentation (v0.8.x).\u201D "
        "Available: https://docs.soliditylang.org",
        "[7]  Ethers.js, \u201CDocumentation (v5.7).\u201D Available: "
        "https://docs.ethers.org/v5/",
        "[8]  ConsenSys, \u201CMetaMask Developer Documentation.\u201D Available: "
        "https://docs.metamask.io",
    ]
    y = top + 2
    for r in refs:
        y = cpara(c, MX, y, CW, r, size=12, color=INK, lead=16) + 8
    cpara(c, MX, 474, CW,
          "Note: [1]\u2013[5] are foundational works; replace or augment with the "
          "specific papers cited in your report.", size=9.5, color=MUTED,
          italic=True)
    footer(c)


SLIDES = [s01_title, s02_abstract, s03_intro, s04_litsurvey, s05_existing,
          s06_existing_arch, s07_problem, s08_proposed, s09_proposed_arch,
          s10_module, s11_usecase, s12_class, s13_sequence, s14_activity,
          s15_component, s16_algorithm, s17_output, s18_compare, s19_future,
          s20_references]


def build(canvas):
    for fn in SLIDES:
        canvas.new_page(WHITE)
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
