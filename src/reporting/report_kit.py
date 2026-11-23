"""Authoring helpers for the long-form Quantum University project report.

`ReportKit` wraps ReportLab flowable creation with automatic chapter / section / table /
figure numbering so chapter modules can focus on content.
"""
from __future__ import annotations

import html
import re
import textwrap
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Image, KeepTogether, PageBreak, Paragraph, Preformatted, Spacer, Table, TableStyle

PRINT_W = 14.9 * cm

# Characters outside Times-Roman / Courier WinAnsi coverage are mapped to safe ASCII.
_ASCII_MAP = {
    "\u2264": "<=", "\u2265": ">=", "\u2192": "->", "\u2190": "<-", "\u2248": "~", "\u2260": "!=",
    "\u2212": "-", "\u2013": "-", "\u2014": "-", "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2026": "...", "\u2022": "*", "\u00b5": "u", "\u00b3": "3", "\u00b2": "2", "\u03b1": "alpha",
    "\u03b2": "beta", "\u03c3": "sigma", "\u03bc": "mu", "\u03c6": "phi", "\u2211": "sum", "\u221a": "sqrt",
    "\u00d7": "x", "\u00b1": "+-", "\u2713": "ok", "\u2705": "[x]", "\u26a0": "(!)", "\u2022": "*",
    "\u00a0": " ", "\u2500": "-", "\u2502": "|", "\u251c": "+", "\u2514": "+", "\u00b0": " deg",
}


def to_ascii_safe(text: str) -> str:
    """Replace glyphs the built-in PDF fonts cannot draw."""
    for k, v in _ASCII_MAP.items():
        text = text.replace(k, v)
    return text.encode("ascii", "replace").decode("ascii").replace("?", "?")


def _inline(text: str) -> str:
    """Escape text and convert **bold**, __italic__ and `code` shorthand into ReportLab markup."""
    t = html.escape(text, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"__(.+?)__", r"<i>\1</i>", t)
    t = re.sub(r"`(.+?)`", r'<font face="Courier" size="10.5">\1</font>', t)
    return t


class ReportKit:
    """Stateful builder shared by all chapter modules."""

    def __init__(
        self,
        el: list,
        styles: Dict[str, ParagraphStyle],
        fig_dir: Path,
        screen_dir: Path,
        qu_table: Callable,
        chapter_block: Callable,
        sec_fn: Callable,
        subsec_fn: Callable,
    ) -> None:
        self.el = el
        self.st = styles
        self.fig_dir = fig_dir
        self.screen_dir = screen_dir
        self._qu_table = qu_table
        self._chapter_block = chapter_block
        self._sec_fn = sec_fn
        self._subsec_fn = subsec_fn
        self.ch: str = "0"
        self._sec_no = 0
        self._sub_no = 0
        self._tbl_no = 0
        self._fig_no = 0
        self.bullet_style = ParagraphStyle(
            "KitBullet", parent=styles["Body"], firstLineIndent=0, leftIndent=30, bulletIndent=12, spaceAfter=3,
        )
        self.small_style = ParagraphStyle(
            "KitSmall", parent=styles["BodyNoIndent"], fontSize=10.5, leading=14.5,
        )
        self.note_style = ParagraphStyle(
            "KitNote", parent=styles["BodyNoIndent"], fontSize=11, leading=15.5, leftIndent=10, rightIndent=10,
            backColor=colors.HexColor("#EFF6FF"), borderColor=colors.HexColor("#93C5FD"), borderWidth=0.6,
            borderPadding=6, spaceBefore=6, spaceAfter=10,
        )
        self.code_style = ParagraphStyle(
            "KitCodeBlock", fontName="Courier", fontSize=7.4, leading=9.2, textColor=colors.HexColor("#0F172A"),
            backColor=colors.HexColor("#F8FAFC"), leftIndent=4, rightIndent=4,
        )

    # ------------------------------------------------------------------ structure
    def chapter(self, number: int | str, title: str, first: bool = False, intro: Optional[str] = None) -> None:
        self.ch = str(number)
        self._sec_no = self._sub_no = self._tbl_no = self._fig_no = 0
        if isinstance(number, int):
            self._chapter_block(self.el, number, title, self.st, is_first=first)
        else:
            self._chapter_block(self.el, 0, title, self.st, is_first=first)
        if intro:
            self.pn(intro)

    def appendix(self, letter: str, title: str) -> None:
        """Appendix heading (registered in the table of contents as a back-matter section)."""
        self.ch = letter
        self._sec_no = self._sub_no = self._tbl_no = self._fig_no = 0
        label = Paragraph(f"APPENDIX {html.escape(letter)}", self.st["ChapterLabel"])
        label._qu_toc = ("chapter", f"APPENDIX {letter}", f"APPENDIX {letter}  {title}")
        self.el.append(label)
        self.el.append(Paragraph(html.escape(title), self.st["ChapterTitle"]))

    def sec(self, title: str) -> str:
        self._sec_no += 1
        self._sub_no = 0
        label = f"{self.ch}.{self._sec_no} {title}"
        self.el.append(self._sec_fn(label, self.st))
        return label

    def sub(self, title: str) -> str:
        self._sub_no += 1
        label = f"{self.ch}.{self._sec_no}.{self._sub_no} {title}"
        self.el.append(self._subsec_fn(label, self.st))
        return label

    def pagebreak(self) -> None:
        self.el.append(PageBreak())

    def space(self, pts: float = 6) -> None:
        self.el.append(Spacer(1, pts))

    # ------------------------------------------------------------------ text
    def p(self, text: str) -> None:
        self.el.append(Paragraph(_inline(to_ascii_safe(text)), self.st["Body"]))

    def pn(self, text: str) -> None:
        self.el.append(Paragraph(_inline(to_ascii_safe(text)), self.st["BodyNoIndent"]))

    def bullets(self, items: Sequence[str]) -> None:
        for it in items:
            self.el.append(Paragraph(_inline(to_ascii_safe(it)), self.bullet_style, bulletText="\u2022"))
        self.el.append(Spacer(1, 4))

    def numbered(self, items: Sequence[str]) -> None:
        for i, it in enumerate(items, start=1):
            self.el.append(Paragraph(_inline(to_ascii_safe(it)), self.bullet_style, bulletText=f"{i}."))
        self.el.append(Spacer(1, 4))

    def note(self, text: str) -> None:
        self.el.append(Paragraph(_inline(to_ascii_safe(text)), self.note_style))

    def formula(self, text: str) -> None:
        self.el.append(Paragraph(html.escape(to_ascii_safe(text)), self.st["Formula"]))

    # ------------------------------------------------------------------ tables
    def next_table_label(self) -> str:
        return f"{self.ch}.{self._tbl_no + 1}"

    def next_fig_label(self) -> str:
        return f"Fig. {self.ch}.{self._fig_no + 1}"

    def table(
        self,
        title: str,
        data: List[List[object]],
        widths: Sequence[float],
        font: float = 9.0,
    ) -> str:
        self._tbl_no += 1
        label = f"{self.ch}.{self._tbl_no}"
        clean = [[to_ascii_safe(str(c)) for c in row] for row in data]
        lbl = Paragraph(f"Table {html.escape(label)}  {html.escape(to_ascii_safe(title))}", self.st["TblTitle"])
        lbl._qu_tbl = (label, to_ascii_safe(title))
        self.el.append(lbl)
        self.el.append(self._qu_table(clean, [w * cm if w < 100 else w for w in widths], font_pt=font))
        self.el.append(Spacer(1, 8))
        return label

    def autotable(self, title: str, header: Sequence[str], rows: Sequence[Sequence[object]], font: float = 9.0,
                  weights: Optional[Sequence[float]] = None) -> str:
        """Table whose column widths are derived proportionally from `weights` (default: content length)."""
        data = [list(header)] + [list(r) for r in rows]
        if weights is None:
            n = len(header)
            lens = [max(len(str(r[i])) for r in data) for i in range(n)]
            weights = [min(max(l, 6), 38) for l in lens]
        total = float(sum(weights))
        widths = [PRINT_W / cm * (w / total) for w in weights]
        return self.table(title, data, widths, font=font)

    # ------------------------------------------------------------------ figures
    def figure(self, filename: str, title: str, width_cm: float = 14.4, max_h_cm: float = 19.0,
               screen: bool = False) -> str:
        path = (self.screen_dir if screen else self.fig_dir) / filename
        if not path.exists():
            return ""
        self._fig_no += 1
        label = f"Fig. {self.ch}.{self._fig_no}"
        with PILImage.open(path) as im:
            w, h = im.size
        aspect = h / float(w)
        w_pts = min(width_cm * cm, PRINT_W)
        h_pts = w_pts * aspect
        if h_pts > max_h_cm * cm:
            h_pts = max_h_cm * cm
            w_pts = h_pts / aspect
        img = Image(str(path), width=w_pts, height=h_pts)
        img.hAlign = "CENTER"
        cap = Paragraph(f"<b>{html.escape(label)}</b>  {html.escape(to_ascii_safe(title))}", self.st["Caption"])
        cap._qu_fig = (label, to_ascii_safe(title))
        self.el.append(KeepTogether([Spacer(1, 6), img, cap]))
        return label

    # ------------------------------------------------------------------ code
    def code(self, text: str, wrap: int = 96) -> None:
        text = to_ascii_safe(text.rstrip("\n"))
        lines: List[str] = []
        for ln in text.splitlines():
            ln = ln.replace("\t", "    ")
            if len(ln) <= wrap:
                lines.append(ln)
            else:
                indent = len(ln) - len(ln.lstrip(" "))
                lines.extend(textwrap.wrap(ln, width=wrap, subsequent_indent=" " * (indent + 4),
                                           break_long_words=True, replace_whitespace=False) or [ln])
        self.el.append(Preformatted("\n".join(lines), self.code_style))
        self.el.append(Spacer(1, 8))

    def code_file(self, rel_path: str, root: Path, title: Optional[str] = None,
                  start: Optional[int] = None, end: Optional[int] = None) -> int:
        """Embed a real project source file (optionally a 1-based inclusive line range). Returns lines embedded."""
        fp = root / rel_path
        if not fp.exists():
            return 0
        lines = fp.read_text(encoding="utf-8", errors="ignore").splitlines()
        lo = (start or 1) - 1
        hi = end or len(lines)
        chunk = lines[lo:hi]
        label = title or rel_path.replace("\\", "/")
        head = Paragraph(f"<b>Listing {html.escape(self.ch)}</b>  {html.escape(to_ascii_safe(label))}  "
                         f"(lines {lo + 1}-{lo + len(chunk)} of {rel_path.replace(chr(92), '/')})",
                         self.small_style)
        self.el.append(head)
        numbered = [f"{lo + i + 1:4d}  {ln}" for i, ln in enumerate(chunk)]
        self.code("\n".join(numbered), wrap=98)
        return len(chunk)
