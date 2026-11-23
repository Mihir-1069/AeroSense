"""Quantum University Roorkee formatted B.Tech Project Report builder (Exhaustive PDF + Markdown)."""
from __future__ import annotations

import html
import re
import shutil
from pathlib import Path
from typing import Dict, List

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.config import settings
from src.reporting.academic_references import get_alphabetical_bibliography
from src.reporting.report_chapters_part1 import append_chapters_1_to_4
from src.reporting.report_chapters_part2 import append_chapters_5_to_8_and_backmatter

# Printable width under A4 (21cm) with 4cm left and 2cm right margins = 15.0 cm
PRINT_W = 14.9 * cm


def _int_to_roman(num: int) -> str:
    vals = [
        (1000, "m"), (900, "cm"), (500, "d"), (400, "cd"),
        (100, "c"), (90, "xc"), (50, "l"), (40, "xl"),
        (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i"),
    ]
    res = []
    n = max(1, num)
    for v, sym in vals:
        while n >= v:
            res.append(sym)
            n -= v
    return "".join(res)


class _QUReportDocTemplate(SimpleDocTemplate):
    """Two-pass ReportLab template tracking Roman front matter and Arabic main pages."""

    def __init__(self, filename: str, tracker: Dict, **kwargs):
        super().__init__(filename, **kwargs)
        self.tracker = tracker

    def afterFlowable(self, flowable) -> None:
        if isinstance(flowable, Paragraph):
            tag = getattr(flowable, "_qu_toc", None)
            if tag is not None:
                kind, key, label = tag
                if kind == "main_start" and "main_start" not in self.tracker:
                    self.tracker["main_start"] = self.page
                start_main = self.tracker.get("main_start", 11)
                if kind == "front":
                    p_str = _int_to_roman(max(1, self.page - 1))
                    self.tracker["toc"].append(("front", label, p_str))
                elif kind in ("chapter", "section", "subsection", "back"):
                    arabic = str(max(1, self.page - start_main + 1))
                    self.tracker["toc"].append((kind, label, arabic))

            fig_tag = getattr(flowable, "_qu_fig", None)
            if fig_tag is not None:
                f_no, f_title = fig_tag
                start_main = self.tracker.get("main_start", 11)
                arabic = str(max(1, self.page - start_main + 1))
                self.tracker["figures"].append((f_no, f_title, arabic))

            tbl_tag = getattr(flowable, "_qu_tbl", None)
            if tbl_tag is not None:
                t_no, t_title = tbl_tag
                start_main = self.tracker.get("main_start", 11)
                arabic = str(max(1, self.page - start_main + 1))
                self.tracker["tables"].append((t_no, t_title, arabic))


def _qu_styles() -> dict[str, ParagraphStyle]:
    """Build exact Quantum University Times New Roman 12pt / 1.5-spaced hierarchy."""
    return {
        "TitleMain": ParagraphStyle(
            "QUTitleMain", fontName="Times-Bold", fontSize=18, leading=24,
            alignment=TA_CENTER, textColor=colors.black, spaceAfter=14,
        ),
        "CoverCenter": ParagraphStyle(
            "QUCoverCenter", fontName="Times-Roman", fontSize=12, leading=18,
            alignment=TA_CENTER, textColor=colors.black, spaceAfter=6,
        ),
        "CoverBold": ParagraphStyle(
            "QUCoverBold", fontName="Times-Bold", fontSize=13, leading=19,
            alignment=TA_CENTER, textColor=colors.black, spaceAfter=5,
        ),
        "FrontTitle": ParagraphStyle(
            "QUFrontTitle", fontName="Times-Bold", fontSize=16, leading=22,
            alignment=TA_CENTER, textColor=colors.black, spaceAfter=18,
        ),
        "ChapterLabel": ParagraphStyle(
            "QUChapterLabel", fontName="Times-Bold", fontSize=15, leading=20,
            alignment=TA_CENTER, textColor=colors.black, spaceAfter=2, keepWithNext=True,
        ),
        "ChapterTitle": ParagraphStyle(
            "QUChapterTitle", fontName="Times-Bold", fontSize=16, leading=22,
            alignment=TA_CENTER, textColor=colors.black, spaceAfter=14, keepWithNext=True,
        ),
        "H1": ParagraphStyle(
            "QUH1", fontName="Times-Bold", fontSize=14, leading=19,
            alignment=TA_LEFT, textColor=colors.black, spaceBefore=12, spaceAfter=6,
            keepWithNext=True,
        ),
        "H2": ParagraphStyle(
            "QUH2", fontName="Times-Bold", fontSize=12, leading=17,
            alignment=TA_LEFT, textColor=colors.black, spaceBefore=10, spaceAfter=5,
            keepWithNext=True,
        ),
        "Body": ParagraphStyle(
            "QUBody", fontName="Times-Roman", fontSize=12, leading=18,
            alignment=TA_JUSTIFY, textColor=colors.black, firstLineIndent=24, spaceAfter=7,
        ),
        "BodyNoIndent": ParagraphStyle(
            "QUBodyNoIndent", fontName="Times-Roman", fontSize=12, leading=18,
            alignment=TA_JUSTIFY, textColor=colors.black, spaceAfter=7,
        ),
        "Bullet": ParagraphStyle(
            "QUBullet", fontName="Times-Roman", fontSize=12, leading=18,
            alignment=TA_JUSTIFY, textColor=colors.black, leftIndent=18, spaceAfter=5,
        ),
        "Code": ParagraphStyle(
            "QUCode", fontName="Courier", fontSize=8.4, leading=12.0,
            alignment=TA_LEFT, textColor=colors.HexColor("#0F172A"),
            backColor=colors.HexColor("#F8FAFC"), leftIndent=8, rightIndent=8,
            spaceBefore=4, spaceAfter=8,
        ),
        "Formula": ParagraphStyle(
            "QUFormula", fontName="Times-Bold", fontSize=10.8, leading=15.5,
            alignment=TA_CENTER, textColor=colors.black, backColor=colors.HexColor("#F1F5F9"),
            spaceBefore=6, spaceAfter=8,
        ),
        "Caption": ParagraphStyle(
            "QUCaption", fontName="Times-Italic", fontSize=10.5, leading=14,
            alignment=TA_CENTER, textColor=colors.black, spaceBefore=4, spaceAfter=10,
        ),
        "TblTitle": ParagraphStyle(
            "QUTblTitle", fontName="Times-Bold", fontSize=10.8, leading=14.5,
            alignment=TA_CENTER, textColor=colors.black, spaceBefore=8, spaceAfter=4, keepWithNext=True,
        ),
        "Bib": ParagraphStyle(
            "QUBib", fontName="Times-Roman", fontSize=11, leading=16,
            alignment=TA_JUSTIFY, textColor=colors.black, leftIndent=24, firstLineIndent=-24, spaceAfter=6,
        ),
    }


def _qu_table(data: List[List[str]], col_widths: List[float], font_pt: float = 9.0) -> Table:
    """Create a bordered formal academic table safely constrained within 14.9 cm width."""
    h_st = ParagraphStyle("QUTH", fontName="Times-Bold", fontSize=font_pt, leading=font_pt + 2.8, alignment=TA_CENTER)
    c_st_l = ParagraphStyle("QUTCL", fontName="Times-Roman", fontSize=font_pt, leading=font_pt + 2.8, alignment=TA_LEFT)
    c_st_c = ParagraphStyle("QUTCC", fontName="Times-Roman", fontSize=font_pt, leading=font_pt + 2.8, alignment=TA_CENTER)
    headers = [str(h).strip().lower() for h in data[0]] if data else []
    center_cols = {
        idx for idx, h in enumerate(headers)
        if h in {"#", "rank", "page", "page no.", "table no.", "figure no.", "cases", "count", "active cols", "horizon", "valid hrs", "openaq id"}
        or col_widths[idx] <= 1.6 * cm
    }
    rows = []
    for r_i, row in enumerate(data):
        if r_i == 0:
            rows.append([Paragraph(html.escape(str(c)), h_st) for c in row])
        else:
            rows.append([
                Paragraph(html.escape(str(c)), c_st_c if c_i in center_cols else c_st_l)
                for c_i, c in enumerate(row)
            ])
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4.5),
    ]))
    return t


def _add_qu_figure(el: list, fig_dir: Path, fig_name: str, fig_no: str, title: str, styles: dict, width_cm: float = 14.5) -> None:
    p = fig_dir / fig_name
    if not p.exists():
        return
    with PILImage.open(p) as im:
        w, h = im.size
    aspect = h / float(w)
    w_pts = min(width_cm * cm, PRINT_W)
    h_pts = min(w_pts * aspect, 19.0 * cm)
    if h_pts < w_pts * aspect:
        w_pts = h_pts / aspect
    img = Image(str(p), width=w_pts, height=h_pts)
    img.hAlign = "CENTER"
    try:
        rel_fig = p.relative_to(settings.REPORTS_DIR).as_posix()
    except ValueError:
        rel_fig = f"figures/{fig_name}"
    img._qu_md_fig = (rel_fig, fig_no, title)
    el.append(Spacer(1, 6))
    el.append(img)
    cap = Paragraph(f"<b>{html.escape(fig_no)}</b>  {html.escape(title)}", styles["Caption"])
    cap._qu_fig = (fig_no, title)
    el.append(cap)


def _add_qu_table_block(el: list, tbl_no: str, title: str, data: List[List[str]], col_widths: List[float], styles: dict, font_pt: float = 8.6) -> None:
    lbl = Paragraph(f"Table {html.escape(tbl_no)}  {html.escape(title)}", styles["TblTitle"])
    lbl._qu_tbl = (tbl_no, title)
    el.append(lbl)
    tbl = _qu_table(data, col_widths, font_pt=font_pt)
    tbl._qu_raw_data = (tbl_no, title, data)
    el.append(tbl)
    el.append(Spacer(1, 8))


def _add_code_block(el: list, lines: List[str], styles: dict) -> None:
    escaped = [html.escape(line).replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;") for line in lines]
    p = Paragraph("<br/>".join(escaped), styles["Code"])
    p._qu_raw_code = lines
    el.append(p)


def _front_heading(title: str, styles: dict, toc_label: str) -> Paragraph:
    p = Paragraph(html.escape(title), styles["FrontTitle"])
    p._qu_toc = ("front", toc_label, title)
    return p


def _chapter_block(el: list, ch_num: int, ch_title: str, styles: dict, is_first: bool = False) -> None:
    p_num = Paragraph(f"CHAPTER {ch_num}", styles["ChapterLabel"])
    kind = "main_start" if is_first else "chapter"
    p_num._qu_toc = (kind, f"CHAPTER {ch_num}", f"CHAPTER {ch_num}  {ch_title}")
    p_num._qu_ch_heading = f"CHAPTER {ch_num}: {ch_title}"
    el.append(p_num)
    el.append(Paragraph(html.escape(ch_title), styles["ChapterTitle"]))


def _sec(title: str, styles: dict) -> Paragraph:
    p = Paragraph(html.escape(title), styles["H1"])
    p._qu_toc = ("section", title, title)
    return p


def _subsec(title: str, styles: dict) -> Paragraph:
    p = Paragraph(html.escape(title), styles["H2"])
    p._qu_toc = ("subsection", title, title)
    return p


def _strip_tags(text: str) -> str:
    text = text.replace("<br/>", "\n").replace("&nbsp;", " ")
    text = re.sub(r"</?b>", "**", text)
    text = re.sub(r"</?i>", "*", text)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text)


def _story_to_markdown(el: list, team_members: list, meta: dict) -> str:
    """Convert the complete ReportLab flowable story into an exhaustive Markdown document."""
    team_md = "\n".join(f"| {m[0]} | {m[1]} | {m[2]} | {m[3]} |" for m in team_members)
    md_lines = [
        "# AIR POLLUTION PATTERN ANALYSIS AND AQI FORECASTING",
        f"**Application Platform:** {meta['app_name']} — *\"{meta['tagline']}\"*  ",
        "**Institution:** Department of Computer Science and Engineering, Quantum School of Technology, Quantum University, Roorkee - 247167  ",
        "**Degree / Batch / Semester:** Bachelor of Technology in CSE (Data Science) | Batch 2023 - 2027 | Semester 7 | Year: 2026  ",
        f"**Project Guide:** {meta['guide']}  ",
        "",
        "### Project Group Members (Batch 2023 - 2027 | Semester 7 | CSE-DS)",
        "| Student Name | Student ID & Roll No. | Batch / Sem / Branch | Primary Engineering Ownership |",
        "| :--- | :--- | :--- | :--- |",
        team_md,
        "",
        "---",
        "",
    ]

    skip_next_chapter_title = False
    for item in el:
        if isinstance(item, Paragraph):
            if skip_next_chapter_title:
                skip_next_chapter_title = False
                continue
            ch_head = getattr(item, "_qu_ch_heading", None)
            if ch_head:
                md_lines.extend(["", "---", "", f"## {ch_head}", ""])
                skip_next_chapter_title = True
                continue
            raw_code = getattr(item, "_qu_raw_code", None)
            if raw_code is not None:
                md_lines.append("```python")
                md_lines.extend(raw_code)
                md_lines.extend(["```", ""])
                continue
            if getattr(item, "_qu_tbl", None) is not None or getattr(item, "_qu_fig", None) is not None:
                continue
            toc_tag = getattr(item, "_qu_toc", None)
            txt = _strip_tags(item.text).strip()
            if not txt:
                continue
            if toc_tag is not None:
                kind, _, label = toc_tag
                if kind in ("front", "back"):
                    md_lines.extend(["", "---", "", f"## {label}", ""])
                elif kind == "section":
                    md_lines.extend(["", f"### {label}", ""])
                elif kind == "subsection":
                    md_lines.extend(["", f"#### {label}", ""])
                continue
            if item.style.name == "QUFormula":
                md_lines.extend([f"```text\n{txt}\n```", ""])
            elif item.style.name == "QUBib":
                md_lines.append(f"- {txt}")
            else:
                md_lines.extend([txt, ""])
        elif isinstance(item, Table):
            raw_tbl = getattr(item, "_qu_raw_data", None)
            if raw_tbl is not None:
                t_no, t_title, data = raw_tbl
                md_lines.append(f"**Table {t_no}: {t_title}**")
                md_lines.append("")
                header = data[0]
                md_lines.append("| " + " | ".join(str(c) for c in header) + " |")
                md_lines.append("| " + " | ".join(":---" for _ in header) + " |")
                for row in data[1:]:
                    md_lines.append("| " + " | ".join(str(c) for c in row) + " |")
                md_lines.append("")
        elif isinstance(item, Image):
            fig_info = getattr(item, "_qu_md_fig", None)
            if fig_info is not None:
                f_rel, f_no, f_title = fig_info
                md_lines.extend([f"![{f_no}: {f_title}]({f_rel})", f"*{f_no}: {f_title}*", ""])

    return "\n".join(md_lines)


def build_detailed_project_report(
    styles: dict,
    team_members: list,
    meta: dict,
    styled_table,
    add_figure,
    footer_canvas,
) -> tuple[Path, Path]:
    """Generate official Quantum University formatted B.Tech Project Report (PDF + MD)."""
    reports_dir = settings.REPORTS_DIR
    fig_dir = reports_dir / "figures"
    qu_logo = fig_dir / "qu_logo.png"

    pdf_path = reports_dir / "AeroSense_Final_Project_Report.pdf"
    title_pdf_path = reports_dir / "Air_Pollution_Pattern_Analysis_and_AQI_Forecasting.pdf"
    md_path = reports_dir / "AeroSense_Final_Project_Report.md"
    docs_md_path = settings.PROJECT_ROOT / "docs" / "BTECH_PROJECT_REPORT.md"

    qstyles = _qu_styles()
    alpha_refs = get_alphabetical_bibliography()
    final_story: list = []

    def _compile(prev_tracker: Dict) -> Dict:
        nonlocal final_story
        tracker: Dict = {"toc": [], "tables": [], "figures": []}
        if "main_start" in prev_tracker:
            tracker["main_start"] = prev_tracker["main_start"]

        def _footer(canvas, doc) -> None:
            if doc.page == 1:
                return
            main_start = tracker.get("main_start", prev_tracker.get("main_start", 11))
            canvas.saveState()
            canvas.setFont("Times-Roman", 12)
            canvas.setFillColor(colors.black)
            if doc.page < main_start:
                txt = _int_to_roman(doc.page - 1)
            else:
                txt = str(doc.page - main_start + 1)
            canvas.drawCentredString(A4[0] / 2.0, 1.5 * cm, txt)
            canvas.restoreState()

        doc = _QUReportDocTemplate(
            str(pdf_path),
            tracker=tracker,
            pagesize=A4,
            leftMargin=4.0 * cm,
            rightMargin=2.0 * cm,
            topMargin=3.0 * cm,
            bottomMargin=3.0 * cm,
        )
        el: list = []

        # PAGE 1 — OFFICIAL QUANTUM UNIVERSITY TITLE PAGE (Unnumbered)
        el.append(Spacer(1, 0.25 * inch))
        el.append(Paragraph("AIR POLLUTION PATTERN ANALYSIS AND AQI FORECASTING", qstyles["TitleMain"]))
        el.append(Spacer(1, 0.12 * inch))
        el.append(Paragraph(
            "Project report submitted in partial fulfillment of the requirement for<br/>the award of the Degree of <b>B. Tech</b>",
            qstyles["CoverCenter"],
        ))
        el.append(Spacer(1, 0.14 * inch))
        el.append(Paragraph("By", qstyles["CoverCenter"]))
        el.append(Spacer(1, 0.08 * inch))
        for name, ids, _, _ in team_members:
            roll = ids.split("Roll:")[-1].strip()
            el.append(Paragraph(f"<b>{html.escape(name)}</b> (Roll No. {html.escape(roll)})", qstyles["CoverCenter"]))
        el.append(Spacer(1, 0.08 * inch))
        el.append(Paragraph(f"<i>Under the Guidance of {html.escape(meta['guide'])}</i>", qstyles["CoverCenter"]))
        el.append(Spacer(1, 0.22 * inch))
        if qu_logo.exists():
            logo = Image(str(qu_logo), width=2.2 * inch, height=1.25 * inch)
            logo.hAlign = "CENTER"
            el.append(logo)
        el.append(Spacer(1, 0.25 * inch))
        el.append(Paragraph("Department of Computer Science and Engineering", qstyles["CoverBold"]))
        el.append(Paragraph("Quantum School of Technology", qstyles["CoverBold"]))
        el.append(Paragraph("Quantum University, Roorkee", qstyles["CoverBold"]))
        el.append(Spacer(1, 0.12 * inch))
        el.append(Paragraph("2026", qstyles["CoverBold"]))
        el.append(PageBreak())

        # ROMAN i — CERTIFICATE
        el.append(_front_heading("CERTIFICATE", qstyles, "CERTIFICATE OF THE SUPERVISOR"))
        el.append(Spacer(1, 0.2 * inch))
        el.append(Paragraph(
            "This is to certify that the project report entitled <b>“Air Pollution Pattern Analysis and AQI Forecasting”</b> "
            "being submitted by <b>Aryan Saini (Roll No. 2301315012), Ayaan Ali (Roll No. 2301315013), Kawalpreet Kaur "
            "(Roll No. 2301315019), and Mihir Kumar (Roll No. 2301315022)</b> in partial fulfillment for the award of the Degree "
            "of Bachelor of Technology in Computer Science and Engineering with specialization in Data Science from Computer Science "
            "and Engineering department is a record of bonafide work carried out by them under my guidance and supervision.",
            qstyles["BodyNoIndent"],
        ))
        el.append(Spacer(1, 1.45 * inch))
        sig_st_l = ParagraphStyle("SigL", fontName="Times-Roman", fontSize=11.5, leading=16, alignment=TA_LEFT)
        sig_st_r = ParagraphStyle("SigR", fontName="Times-Roman", fontSize=11.5, leading=16, alignment=TA_RIGHT)
        sig_st_c = ParagraphStyle("SigC", fontName="Times-Roman", fontSize=11.5, leading=16, alignment=TA_CENTER)
        sig_top = Table(
            [[
                Paragraph("Mr. Abhishek Kumar (QU0125261068)<br/><b>Project Guide</b>", sig_st_l),
                Paragraph("(Name &amp; Signature)<br/><b>Program Officer, CSE</b>", sig_st_r),
            ]],
            colWidths=[7.5 * cm, 7.4 * cm],
        )
        sig_top.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        el.append(sig_top)
        el.append(Spacer(1, 1.0 * inch))
        el.append(Paragraph("(Name &amp; Signature)<br/><b>HoD, CSE &amp; Dean Academics, QU</b>", sig_st_c))
        el.append(PageBreak())

        # ROMAN ii — DECLARATION
        el.append(_front_heading("DECLARATION", qstyles, "DECLARATION"))
        el.append(Spacer(1, 0.15 * inch))
        el.append(Paragraph(
            "We hereby declare that the project entitled <b>“Air Pollution Pattern Analysis and AQI Forecasting”</b> "
            "submitted for the B. Tech Degree in Computer Science and Engineering with specialization in Data Science "
            "(Batch 2023 - 2027, Semester 7) is our original work and the project has not formed the basis or submitted for the "
            "award of any degree, diploma, or any other similar titles in any other college, institute, or university.",
            qstyles["BodyNoIndent"],
        ))
        el.append(Spacer(1, 0.35 * inch))
        decl_tbl = [
            ["Student Name", "Student ID", "Roll No.", "Signature"],
            ["Aryan Saini", "23030173", "2301315012", ""],
            ["Ayaan Ali", "23030175", "2301315013", ""],
            ["Kawalpreet Kaur", "23030255", "2301315019", ""],
            ["Mihir Kumar", "23030268", "2301315022", ""],
        ]
        el.append(_qu_table(decl_tbl, [4.2 * cm, 3.2 * cm, 3.5 * cm, 4.0 * cm], font_pt=10.5))
        el.append(Spacer(1, 0.4 * inch))
        el.append(Paragraph("Place  Roorkee", qstyles["BodyNoIndent"]))
        el.append(Paragraph("Date  November 2026", qstyles["BodyNoIndent"]))
        el.append(PageBreak())

        # ROMAN iii — ACKNOWLEDGEMENTS
        el.append(_front_heading("ACKNOWLEDGEMENTS", qstyles, "ACKNOWLEDGEMENTS"))
        el.append(Paragraph(
            "The successful completion of any major engineering undertaking depends upon sustained mentorship, constructive critical "
            "feedback, and institutional support. We express our deep gratitude to our Project Guide, Mr. Abhishek Kumar (QU0125261068), "
            "Department of Computer Science and Engineering, Quantum School of Technology, Quantum University, Roorkee, for his "
            "invaluable guidance, methodical advice, and unwavering encouragement throughout every stage of the AeroSense AI platform.",
            qstyles["Body"],
        ))
        el.append(Paragraph(
            "We sincerely thank the Program Officer (CSE), the Head of Department (CSE), and the Dean Academics at Quantum University, "
            "Roorkee, for fostering a strong research culture and providing computing facilities during Batch 2023-2027 (7th Semester). "
            "We also acknowledge the open environmental science and machine learning communities behind OpenAQ API v3, Central Pollution "
            "Control Board (CPCB India), World Health Organization (WHO), Scikit-Learn, XGBoost, PyTorch, SHAP, ReportLab, and Streamlit, "
            "whose open standards made authentic real-world validation possible.",
            qstyles["Body"],
        ))
        el.append(Paragraph(
            "Finally, we thank our parents, faculty members, and classmates for their constant encouragement, thoughtful suggestions, "
            "and support during testing, benchmarking, and documentation of this project.",
            qstyles["Body"],
        ))
        el.append(PageBreak())

        # ROMAN iv — TABLE OF CONTENTS
        el.append(_front_heading("TABLE OF CONTENTS", qstyles, "TABLE OF CONTENTS"))
        toc_rows = [["Section / Chapter Title", "Page"]]
        if prev_tracker.get("toc"):
            for kind, lbl, pno in prev_tracker["toc"]:
                if kind == "section":
                    prefix = "    "
                elif kind == "subsection":
                    prefix = "        "
                else:
                    prefix = ""
                toc_rows.append([f"{prefix}{lbl}", pno])
        else:
            toc_rows.append(["Populating dynamically on pass 2...", "i"])
        el.append(_qu_table(toc_rows, [12.9 * cm, 2.0 * cm], font_pt=9.2))
        el.append(PageBreak())

        # ROMAN v — LIST OF TABLES
        el.append(_front_heading("LIST OF TABLES", qstyles, "LIST OF TABLES"))
        lot_rows = [["Table No.", "Title", "Page No."]]
        if prev_tracker.get("tables"):
            for t_no, t_title, pno in prev_tracker["tables"]:
                lot_rows.append([t_no, t_title, pno])
        else:
            lot_rows.append(["1.1", "Pending pass 2 page resolution", "1"])
        el.append(_qu_table(lot_rows, [2.2 * cm, 10.7 * cm, 2.0 * cm], font_pt=9.2))
        el.append(PageBreak())

        # ROMAN vi — LIST OF FIGURES
        el.append(_front_heading("LIST OF FIGURES", qstyles, "LIST OF FIGURES"))
        lof_rows = [["Figure No.", "Title", "Page No."]]
        if prev_tracker.get("figures"):
            for f_no, f_title, pno in prev_tracker["figures"]:
                lof_rows.append([f_no, f_title, pno])
        else:
            lof_rows.append(["Fig. 4.1", "Pending pass 2 page resolution", "1"])
        el.append(_qu_table(lof_rows, [2.4 * cm, 10.5 * cm, 2.0 * cm], font_pt=9.2))
        el.append(PageBreak())

        # ROMAN vii — LIST OF ABBREVIATIONS AND SYMBOLS
        el.append(_front_heading("LIST OF ABBREVIATIONS AND SYMBOLS", qstyles, "LIST OF ABBREVIATIONS AND SYMBOLS"))
        abbr_rows = [
            ["Abbreviation / Symbol", "Full Form and Technical Definition"],
            ["AQI", "Air Quality Index (Indian CPCB 2014 and US EPA 2018 statutory indices)"],
            ["PM2.5 / PM10", "Particulate Matter with aerodynamic diameter <= 2.5 um / <= 10 um"],
            ["NO2 / SO2 / CO / O3", "Nitrogen Dioxide / Sulfur Dioxide / Carbon Monoxide / Ground-Level Ozone"],
            ["CPCB / NAAQS", "Central Pollution Control Board (India) / National Ambient Air Quality Standards"],
            ["DPCC / TSPCB", "Delhi Pollution Control Committee / Telangana State Pollution Control Board"],
            ["US EPA / WHO", "United States Environmental Protection Agency / World Health Organization"],
            ["PBL / BLH / IGP", "Planetary Boundary Layer / Boundary Layer Height / Indo-Gangetic Plain"],
            ["IQR / Q1, Q2, Q3", "Interquartile Range (Q3 - Q1) / 25th, 50th (Median), and 75th Percentiles"],
            ["MAE / RMSE / R2", "Mean Absolute Error / Root Mean Squared Error / Coefficient of Determination"],
            ["OLS / Ridge (L2)", "Ordinary Least Squares / Tikhonov L2-Penalized Linear Regression"],
            ["RF / ET / GBDT", "Random Forest / Extremely Randomized Trees / Gradient Boosted Decision Trees"],
            ["HistGB / XGBoost", "Histogram-Based Gradient Boosting / eXtreme Gradient Boosting"],
            ["LSTM / GRU", "Long Short-Term Memory / Gated Recurrent Unit Recurrent Neural Networks"],
            ["TCN / Chomp1d", "Dilated Causal Temporal Convolutional Network / Right-Padding Causal Slicer"],
            ["Transformer / MHA", "Self-Attention Encoder Architecture / Multi-Head Scaled Dot-Product Attention"],
            ["SHAP / phi_j", "SHapley Additive exPlanations / Cooperative Game-Theoretic Attribution of Feature j"],
            ["DFD / UML / REST", "Data Flow Diagram / Unified Modeling Language / Representational State Transfer"],
            ["UTC / IST", "Coordinated Universal Time / Indian Standard Time (UTC + 05:30)"],
        ]
        el.append(_qu_table(abbr_rows, [4.3 * cm, 10.6 * cm], font_pt=9.3))
        el.append(PageBreak())

        # ROMAN viii — EXECUTIVE ABSTRACT
        el.append(_front_heading("ABSTRACT", qstyles, "ABSTRACT"))
        el.append(Paragraph(
            "Urban fine particulate matter (PM2.5) air pollution is a critical public health emergency across the Indo-Gangetic Plain "
            "and rapidly urbanizing regions worldwide. Existing air quality monitoring portals remain largely constrained to retrospective "
            "visualizers that rely on retired APIs, interpolate blindly across multi-day sensor outages, suffer temporal look-ahead leakage "
            "from randomized cross-validation and unshifted rolling statistics, fail to disclose incomplete sensor panels when reporting "
            "statutory Air Quality Index (AQI) ratings, and deploy black-box predictors without feature attribution. AeroSense AI resolves "
            "these methodological and software engineering gaps through an end-to-end, modular environmental intelligence and forecasting "
            "platform built from scratch in Python, Scikit-Learn, XGBoost, PyTorch, SHAP, Plotly MapLibre, and Streamlit.",
            qstyles["Body"],
        ))
        el.append(Paragraph(
            "The platform implements an authenticated OpenAQ API v3 client (X-API-Key header, exponential backoff, two-phase station and "
            "sensor-hours discovery across 159 countries), deterministic validation, Tukey IQR x 3 anomaly rejection, and bounded <= 6-hour "
            "linear interpolation with explicit boolean provenance (is_imputed) persisted in Snappy-compressed Apache Parquet. Dual CPCB "
            "(2014) and US EPA (2018) piecewise-linear AQI calculators evaluate sub-indices across six criteria pollutants (PM2.5, PM10, "
            "NO2, SO2, CO, O3) and enforce statutory completeness disclosure via is_complete. Thirty-four strictly causal calendar, "
            "Fourier cyclical harmonic (sin/cos), autoregressive lag (1..48h), shifted rolling moment (target.shift(1) over 3..24h), and "
            "momentum features feed chronological 70% training, 15% validation, and 15% held-out testing splits across 14 models: three "
            "naive baselines, six tabular ML regressors, and four PyTorch deep sequence models (LSTM, GRU, Dilated Causal TCN, Transformer).",
            qstyles["Body"],
        ))
        el.append(Paragraph(
            "Live 30-day Indian telemetry extracted via OpenAQ v3 across Delhi R K Puram (n=639, mean 177.81 ug/m3), Lucknow Talkatora "
            "(n=641, mean 85.64 ug/m3), and Hyderabad Zoo Park (n=627, mean 52.71 ug/m3) reveals WHO 24-hour guideline (15 ug/m3) breach "
            "rates of 92.2% to 98.6%. On the 90-day controlled benchmark (n=2,161), 1-step Linear Regression (9.449 ug/m3 MAE, R2=0.906), "
            "Ridge (9.457 ug/m3), and PyTorch Transformer (9.580 ug/m3 MAE, R2=0.903) reduce test error by 69.5% over Seasonal Naive "
            "(30.966 ug/m3). On live Delhi R K Puram data featuring severe November smog surges up to 501.00 ug/m3, Linear Regression "
            "(23.803 ug/m3 MAE, R2=0.854) and Ridge (24.714 ug/m3) decisively outperform tree ensembles (26.534–33.479 ug/m3 MAE), "
            "demonstrating mathematically why unbounded linear slopes succeed where convex-hull-bounded tree leaves saturate. TreeSHAP "
            "confirms lag_1 (26.91 ug/m3, 74.4%) and diurnal harmonics govern short-term variance, verified by 46 passing pytest tests.",
            qstyles["Body"],
        ))
        el.append(PageBreak())

        # APPEND CHAPTERS 1 TO 4
        append_chapters_1_to_4(
            el=el,
            qstyles=qstyles,
            fig_dir=fig_dir,
            team_members=team_members,
            meta=meta,
            chapter_block=_chapter_block,
            sec=_sec,
            subsec=_subsec,
            add_table_block=_add_qu_table_block,
            add_figure=_add_qu_figure,
            code_block=_add_code_block,
        )

        # APPEND CHAPTERS 5 TO 8, REFERENCES, AND APPENDICES
        append_chapters_5_to_8_and_backmatter(
            el=el,
            qstyles=qstyles,
            fig_dir=fig_dir,
            team_members=team_members,
            meta=meta,
            alpha_refs=alpha_refs,
            chapter_block=_chapter_block,
            sec=_sec,
            subsec=_subsec,
            add_table_block=_add_qu_table_block,
            add_figure=_add_qu_figure,
            code_block=_add_code_block,
        )

        final_story = list(el)
        doc.build(el, onFirstPage=_footer, onLaterPages=_footer)
        return tracker

    pass1 = _compile({})
    _compile(pass1)
    shutil.copy2(pdf_path, title_pdf_path)

    full_md = _story_to_markdown(final_story, team_members, meta)
    md_path.write_text(full_md, encoding="utf-8")
    docs_md_path.parent.mkdir(parents=True, exist_ok=True)
    docs_md_path.write_text(full_md, encoding="utf-8")
    return pdf_path, md_path
