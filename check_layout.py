#!/usr/bin/env python3
"""
Strict geometry/overflow verifier for the project deck.

Mimics the canvas API used by the builder, records the bounding box of every
primitive, and reports:
  * any shape/line/text drawn outside the 960x540 page (small tolerance)
  * any text whose longest wrapped line is wider than its box (h-overflow)
  * any text whose rendered height exceeds its box by > half a line
    (regardless of vertical anchor) -> would overlap neighbours
"""
from reportlab.pdfbase.pdfmetrics import stringWidth
from deck_engine import _wrap

PAGE_W, PAGE_H = 960.0, 540.0
TOL = 0.75

issues = []
page = {"n": 0}


def _font_for(font):
    return "Courier" if str(font).lower().startswith("courier") else "Helvetica"


def _f(kind, x, y, w, h, extra=""):
    if x < -TOL or y < -TOL or (x + w) > PAGE_W + TOL or (y + h) > PAGE_H + TOL:
        issues.append(
            f"[p{page['n']:02d}] OOB {kind}: x={x:.1f} y={y:.1f} "
            f"w={w:.1f} h={h:.1f} (x2={x+w:.1f} y2={y+h:.1f}) {extra}")


class CheckCanvas:
    def new_page(self, bg="#FFFFFF"):
        page["n"] += 1

    def rect(self, x, y, w, h, fill=None, line=None, line_w=1.0, radius=0):
        _f("rect", x, y, w, h)

    def ellipse(self, x, y, w, h, fill=None, line=None, line_w=1.0):
        _f("ellipse", x, y, w, h)

    def diamond(self, x, y, w, h, fill=None, line=None, line_w=1.0):
        _f("diamond", x, y, w, h)

    def line(self, x1, y1, x2, y2, color="#000000", w=1.0,
             arrow_end=False, arrow_start=False, dash=False):
        for (px, py) in ((x1, y1), (x2, y2)):
            if px < -TOL or py < -TOL or px > PAGE_W + TOL or py > PAGE_H + TOL:
                issues.append(
                    f"[p{page['n']:02d}] OOB line endpoint: ({px:.1f},{py:.1f})")

    def text(self, x, y, w, h, s, size=12, color="#16213E", align="l",
             valign="t", bold=False, italic=False, font="Helvetica", wrap=True):
        fnt = _font_for(font)
        if wrap:
            lines = []
            for part in str(s).split("\n"):
                lines.extend(_wrap(part, w, size, fnt))
        else:
            lines = str(s).split("\n")
        leading = size * 1.25
        rendered_h = len(lines) * leading

        # horizontal fit (always meaningful)
        longest = max((stringWidth(ln, fnt, size) for ln in lines), default=0)
        if longest > w + TOL:
            issues.append(
                f"[p{page['n']:02d}] TEXT too wide: w={w:.1f} need={longest:.1f} "
                f"text={s[:40]!r}")

        # vertical placement by anchor
        if valign == "m":
            top = y + (h - rendered_h) / 2.0
        elif valign == "b":
            top = y + (h - rendered_h)
        else:
            top = y
        bottom = top + rendered_h
        if top < -TOL or bottom > PAGE_H + TOL or x < -TOL or (x + w) > PAGE_W + TOL:
            issues.append(
                f"[p{page['n']:02d}] OOB text: x={x:.1f} top={top:.1f} "
                f"bottom={bottom:.1f} text={s[:40]!r}")

        # box overflow (any anchor): rendered taller than the box by > half a line
        if rendered_h > h + leading * 0.6 and h >= leading - 1:
            issues.append(
                f"[p{page['n']:02d}] TEXT overflows box: h={h:.1f} "
                f"rendered={rendered_h:.1f} lines={len(lines)} text={s[:40]!r}")


if __name__ == "__main__":
    import build_deck_clean as B
    c = CheckCanvas()
    B.build(c)
    print(f"Checked {page['n']} pages.")
    if not issues:
        print("OK: no out-of-bounds / overflow issues detected.")
    else:
        print(f"FOUND {len(issues)} issue(s):")
        for i in issues:
            print("  -", i)
