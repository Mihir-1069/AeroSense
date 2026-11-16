"""Quantum University Roorkee formatted B.Tech Project Report builder (PDF + Markdown)."""
from __future__ import annotations

import html
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

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
                start_main = self.tracker.get("main_start", 10)
                if kind == "front":
                    # Title page is page 1 (unnumbered); front matter starts at Roman i = page 2
                    p_str = _int_to_roman(max(1, self.page - 1))
                    self.tracker["toc"].append(("front", label, p_str))
                elif kind in ("chapter", "section", "subsection", "back"):
                    arabic = str(max(1, self.page - start_main + 1))
                    self.tracker["toc"].append((kind, label, arabic))

            fig_tag = getattr(flowable, "_qu_fig", None)
            if fig_tag is not None:
                f_no, f_title = fig_tag
                start_main = self.tracker.get("main_start", 10)
                arabic = str(max(1, self.page - start_main + 1))
                self.tracker["figures"].append((f_no, f_title, arabic))

            tbl_tag = getattr(flowable, "_qu_tbl", None)
            if tbl_tag is not None:
                t_no, t_title = tbl_tag
                start_main = self.tracker.get("main_start", 10)
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
            alignment=TA_LEFT, textColor=colors.black, spaceBefore=12, spaceAfter=6,
            keepWithNext=True,
        ),
        "Body": ParagraphStyle(
            "QUBody", fontName="Times-Roman", fontSize=12, leading=18,
            alignment=TA_JUSTIFY, textColor=colors.black, firstLineIndent=24, spaceAfter=6,
        ),
        "BodyNoIndent": ParagraphStyle(
            "QUBodyNoIndent", fontName="Times-Roman", fontSize=12, leading=18,
            alignment=TA_JUSTIFY, textColor=colors.black, spaceAfter=6,
        ),
        "Bullet": ParagraphStyle(
            "QUBullet", fontName="Times-Roman", fontSize=12, leading=18,
            alignment=TA_JUSTIFY, textColor=colors.black, leftIndent=24, spaceAfter=4,
        ),
        "Code": ParagraphStyle(
            "QUCode", fontName="Courier", fontSize=8.8, leading=12.5,
            alignment=TA_LEFT, textColor=colors.HexColor("#0F172A"),
            backColor=colors.HexColor("#F8FAFC"), leftIndent=8, rightIndent=8,
            spaceBefore=4, spaceAfter=8,
        ),
        "Formula": ParagraphStyle(
            "QUFormula", fontName="Times-Bold", fontSize=11, leading=16,
            alignment=TA_CENTER, textColor=colors.black, backColor=colors.HexColor("#F1F5F9"),
            spaceBefore=6, spaceAfter=8,
        ),
        "Caption": ParagraphStyle(
            "QUCaption", fontName="Times-Italic", fontSize=10.5, leading=14,
            alignment=TA_CENTER, textColor=colors.black, spaceBefore=4, spaceAfter=10,
        ),
        "TblTitle": ParagraphStyle(
            "QUTblTitle", fontName="Times-Bold", fontSize=11, leading=15,
            alignment=TA_CENTER, textColor=colors.black, spaceBefore=8, spaceAfter=4, keepWithNext=True,
        ),
        "Bib": ParagraphStyle(
            "QUBib", fontName="Times-Roman", fontSize=11, leading=16,
            alignment=TA_JUSTIFY, textColor=colors.black, leftIndent=24, firstLineIndent=-24, spaceAfter=6,
        ),
    }


def _qu_table(data: List[List[str]], col_widths: List[float], font_pt: float = 9.5) -> Table:
    """Create a bordered formal academic table safely constrained within 15.0 cm width."""
    h_st = ParagraphStyle("QUTH", fontName="Times-Bold", fontSize=font_pt, leading=font_pt + 3, alignment=TA_CENTER)
    c_st = ParagraphStyle("QUTC", fontName="Times-Roman", fontSize=font_pt, leading=font_pt + 3, alignment=TA_LEFT)
    rows = []
    for r_i, row in enumerate(data):
        st = h_st if r_i == 0 else c_st
        rows.append([Paragraph(html.escape(str(c)), st) for c in row])
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
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
    h_pts = min(w_pts * aspect, 19.5 * cm)
    if h_pts < w_pts * aspect:
        w_pts = h_pts / aspect
    img = Image(str(p), width=w_pts, height=h_pts)
    img.hAlign = "CENTER"
    el.append(Spacer(1, 6))
    el.append(img)
    cap = Paragraph(f"<b>{html.escape(fig_no)}</b>  {html.escape(title)}", styles["Caption"])
    cap._qu_fig = (fig_no, title)
    el.append(cap)


def _add_qu_table_block(el: list, tbl_no: str, title: str, data: List[List[str]], col_widths: List[float], styles: dict, font_pt: float = 9.0) -> None:
    lbl = Paragraph(f"Table {html.escape(tbl_no)}  {html.escape(title)}", styles["TblTitle"])
    lbl._qu_tbl = (tbl_no, title)
    el.append(lbl)
    el.append(_qu_table(data, col_widths, font_pt=font_pt))
    el.append(Spacer(1, 8))


def _front_heading(title: str, styles: dict, toc_label: str) -> Paragraph:
    p = Paragraph(html.escape(title), styles["FrontTitle"])
    p._qu_toc = ("front", toc_label, title)
    return p


def _chapter_block(el: list, ch_num: int, ch_title: str, styles: dict, is_first: bool = False) -> None:
    p_num = Paragraph(f"CHAPTER {ch_num}", styles["ChapterLabel"])
    if is_first:
        p_num._qu_toc = ("main_start", f"CHAPTER {ch_num}", f"CHAPTER {ch_num}  {ch_title}")
    else:
        p_num._qu_toc = ("chapter", f"CHAPTER {ch_num}", f"CHAPTER {ch_num}  {ch_title}")
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

    qstyles = _qu_styles()
    alpha_refs = get_alphabetical_bibliography()

    def _compile(prev_tracker: Dict) -> Dict:
        tracker: Dict = {"toc": [], "tables": [], "figures": []}
        if "main_start" in prev_tracker:
            tracker["main_start"] = prev_tracker["main_start"]

        def _footer(canvas, doc) -> None:
            # Page 1 is unnumbered Title Page
            if doc.page == 1:
                return
            main_start = tracker.get("main_start", prev_tracker.get("main_start", 10))
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

        # ROMAN i — CERTIFICATE (Exact Quantum University Page 8 layout)
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
                Paragraph(f"Mr. Abhishek Kumar (QU0125261068)<br/><b>Project Guide</b>", sig_st_l),
                Paragraph("(Name &amp; Signature)<br/><b>Program Officer, CSE</b>", sig_st_r),
            ]],
            colWidths=[7.5 * cm, 7.4 * cm],
        )
        sig_top.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        el.append(sig_top)
        el.append(Spacer(1, 1.0 * inch))
        el.append(Paragraph("(Name &amp; Signature)<br/><b>HoD, CSE &amp; Dean Academics, QU</b>", sig_st_c))
        el.append(PageBreak())

        # ROMAN ii — DECLARATION (Exact Quantum University Page 9 layout)
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

        # ROMAN iv — TABLE OF CONTENTS (Page 10 template structure)
        el.append(_front_heading("TABLE OF CONTENTS", qstyles, "TABLE OF CONTENTS"))
        toc_rows = [["Section / Chapter Title", "Page"]]
        if prev_tracker.get("toc"):
            for kind, lbl, pno in prev_tracker["toc"]:
                if kind == "subsection":
                    continue
                prefix = "    " if kind == "section" else ""
                toc_rows.append([f"{prefix}{lbl}", pno])
        else:
            toc_rows.append(["Populating dynamically on pass 2...", "i"])
        el.append(_qu_table(toc_rows, [12.9 * cm, 2.0 * cm], font_pt=10.0))
        el.append(PageBreak())

        # ROMAN v — LIST OF TABLES (Page 11 format)
        el.append(_front_heading("LIST OF TABLES", qstyles, "LIST OF TABLES"))
        lot_rows = [["Table No.", "Title", "Page No."]]
        if prev_tracker.get("tables"):
            for t_no, t_title, pno in prev_tracker["tables"]:
                lot_rows.append([t_no, t_title, pno])
        else:
            lot_rows.append(["1.1", "Pending pass 2 page resolution", "1"])
        el.append(_qu_table(lot_rows, [2.2 * cm, 10.7 * cm, 2.0 * cm], font_pt=10.0))
        el.append(PageBreak())

        # ROMAN vi — LIST OF FIGURES (Page 12 format)
        el.append(_front_heading("LIST OF FIGURES", qstyles, "LIST OF FIGURES"))
        lof_rows = [["Figure No.", "Title", "Page No."]]
        if prev_tracker.get("figures"):
            for f_no, f_title, pno in prev_tracker["figures"]:
                lof_rows.append([f_no, f_title, pno])
        else:
            lof_rows.append(["Fig. 4.1", "Pending pass 2 page resolution", "1"])
        el.append(_qu_table(lof_rows, [2.4 * cm, 10.5 * cm, 2.0 * cm], font_pt=10.0))
        el.append(PageBreak())

        # ROMAN vii — LIST OF ABBREVIATIONS
        el.append(_front_heading("LIST OF ABBREVIATIONS", qstyles, "LIST OF ABBREVIATIONS"))
        abbr_rows = [
            ["Abbreviation", "Full Form / Technical Meaning"],
            ["AQI", "Air Quality Index (Indian CPCB 2014 and US EPA 2018)"],
            ["PM2.5 / PM10", "Particulate Matter <= 2.5 micrometers / <= 10 micrometers"],
            ["CPCB / NAAQS", "Central Pollution Control Board / National Ambient Air Quality Standards"],
            ["US EPA / WHO", "United States Environmental Protection Agency / World Health Organization"],
            ["PBL / IGP", "Planetary Boundary Layer / Indo-Gangetic Plain"],
            ["MAE / RMSE / R2", "Mean Absolute Error / Root Mean Squared Error / Coefficient of Determination"],
            ["ML / DL / XAI", "Machine Learning / Deep Learning / Explainable Artificial Intelligence"],
            ["LSTM / GRU", "Long Short-Term Memory / Gated Recurrent Unit"],
            ["TCN / SHAP", "Temporal Convolutional Network / SHapley Additive exPlanations"],
            ["DFD / UML / API", "Data Flow Diagram / Unified Modeling Language / Application Programming Interface"],
        ]
        el.append(_qu_table(abbr_rows, [4.2 * cm, 10.7 * cm], font_pt=10.0))
        el.append(PageBreak())

        # ROMAN viii — ONE-PAGE ABSTRACT
        el.append(_front_heading("ABSTRACT", qstyles, "ABSTRACT"))
        el.append(Paragraph(
            "Urban fine particulate matter (PM2.5) air pollution is a critical public health challenge across Indian urban basins "
            "and industrial megacities worldwide. Existing air quality portals often remain limited to static historical visualizers "
            "that fail to disclose incomplete sensor panels when calculating Air Quality Index (AQI) ratings, allow temporal data leakage "
            "via randomized cross-validation, or offer black-box predictions devoid of interpretable drivers. AeroSense AI addresses "
            "these methodological gaps through a complete, modular environmental analytics and forecasting system built in Python and Streamlit.",
            qstyles["Body"],
        ))
        el.append(Paragraph(
            "The platform implements an authenticated OpenAQ API v3 ingestion pipeline supporting global ISO country discovery, "
            "sensor-level hourly aggregation, schema checks, IQR x 3 anomaly rejection, and bounded <= 6-hour temporal interpolation "
            "with explicit imputation masks persisted in Apache Parquet. Dual CPCB (2014) and US EPA (2018) calculators compute sub-indices "
            "and surface explicit partial-panel disclaimers. Thirty-four leakage-free cyclical, autoregressive lag, shifted rolling, and "
            "momentum features feed chronological 70% training, 15% validation, and 15% held-out testing pipelines across three naive baselines, "
            "six tabular ML models (Linear Regression, Ridge, Random Forest, Extra Trees, Histogram Gradient Boosting, XGBoost), and four "
            "PyTorch deep sequence architectures (LSTM, GRU, Dilated Causal TCN, and Encoder-only Transformer).",
            qstyles["Body"],
        ))
        el.append(Paragraph(
            "Live 30-day Indian telemetry across Delhi R K Puram, Lucknow Talkatora, and Hyderabad Zoo Park (2,157 hourly records) "
            "reveals WHO 24-hour exceedance rates between 92.2% and 98.6%. Under controlled evaluation (n = 2,161), 1-step Linear Regression "
            "(9.449 ug/m3 MAE, R2 = 0.906) and PyTorch Transformer (9.580 ug/m3 MAE, R2 = 0.903) decisively beat Seasonal Naive baselines "
            "(30.966 ug/m3 MAE). On live Delhi R K Puram data (n = 639), Linear Regression achieves 23.803 ug/m3 MAE (R2 = 0.854), reducing error "
            "by 57.1% while illuminating why bounded tree ensembles struggle during extreme November smog peaks (up to 501.00 ug/m3). TreeSHAP "
            "confirms lag_1 and diurnal phase harmonics govern short-term variance, verified by 46 passing automated tests.",
            qstyles["Body"],
        ))
        el.append(PageBreak())

        # =====================================================================
        # CHAPTER 1  INTRODUCTION (Main matter Arabic page 1 begins here)
        # =====================================================================
        _chapter_block(el, 1, "INTRODUCTION", qstyles, is_first=True)
        el.append(Paragraph(
            "Ambient air pollution constitutes one of the most pressing public health and sustainable development challenges of the "
            "twenty-first century. This opening chapter motivates why an end-to-end, leakage-free air quality intelligence system "
            "combining real-world OpenAQ API v3 telemetry, dual regulatory indexing, traditional machine learning, deep sequence networks, "
            "and explainable diagnostics is essential for both academic research and public health readiness.",
            qstyles["BodyNoIndent"],
        ))

        el.append(_sec("1.1 Atmospheric Background and Health Significance", qstyles))
        el.append(Paragraph(
            "Fine particulate matter (PM2.5, particles with aerodynamic diameter at or below 2.5 micrometers) represents the single most "
            "hazardous regulated air pollutant because microscopic particles penetrate beyond upper respiratory defenses deep into lung alveoli "
            "and enter systemic vascular circulation. Epidemiological cohort evidence synthesized by the World Health Organization (WHO 2021) "
            "links elevated PM2.5 exposure directly to ischemic heart disease, stroke, chronic obstructive pulmonary disease (COPD), acute "
            "asthma exacerbation, lower respiratory infections, and impaired pediatric cognitive development. In response, the WHO tightened "
            "its 24-hour ambient PM2.5 guideline to 15 ug/m3 and annual guideline to 5 ug/m3, whereas India's National Ambient Air Quality "
            "Standards (NAAQS, CPCB) specify a 24-hour benchmark of 60 ug/m3.",
            qstyles["Body"],
        ))

        el.append(_sec("1.2 Indian Regional Urgency and Global Extensibility", qstyles))
        el.append(Paragraph(
            "Urban agglomerations across northern India and the Indo-Gangetic Plain (IGP) experience pronounced diurnal and seasonal "
            "concentration swings driven by vehicular emissions, biomass burning, industrial plumes, and winter radiative temperature "
            "inversions that trap surface aerosols beneath compressed planetary boundary layers. Live continuous telemetry retrieved via "
            "OpenAQ API v3 during October–November 2026 verifies these extremes across three geographically distinct Indian cities summarized "
            "in Table 1.1. Crucially, while Phase 1 prioritizes India (ISO code IN, primary pollutant PM2.5), AeroSense AI parameterizes all "
            "ingestion and analytics pipelines by ISO country code to support seamless global expansion.",
            qstyles["Body"],
        ))
        _add_qu_table_block(
            el, "1.1", "Live OpenAQ v3 Station Baseline Snapshot (India Phase 1)",
            [
                ["Station (OpenAQ ID)", "Valid Hrs", "Mean +- Std (ug/m3)", "WHO >15", "NAAQS >60"],
                ["R K Puram, Delhi - DPCC (17)", "639", "177.81 +- 95.74", "98.6%", "92.3%"],
                ["Talkatora, Lucknow - CPCB (407)", "641", "85.64 +- 50.82", "92.2%", "68.3%"],
                ["Zoo Park, Hyderabad - TSPCB (2456)", "627", "52.71 +- 19.43", "97.4%", "36.0%"],
            ],
            [5.3 * cm, 1.9 * cm, 3.5 * cm, 2.0 * cm, 2.2 * cm],
            qstyles, font_pt=9.0,
        )

        el.append(_sec("1.3 Problem Statement and Platform Objectives", qstyles))
        el.append(Paragraph(
            "Conventional air quality dashboards frequently fail scientific standards along four axes: (1) reliance on retired API endpoints "
            "or hardcoded dummy series; (2) unvalidated sensor outliers or long multi-day linear interpolations that fabricate pollution readings; "
            "(3) temporal data leakage via shuffled cross-validation and unshifted rolling statistics; and (4) reporting incomplete single-sensor "
            "AQI scores as official multi-pollutant indices. AeroSense AI eliminates each flaw through verified OpenAQ v3 ingestion, bounded "
            "6-hour cleaning, strict 70/15/15 chronological splits, 14-model ML/DL/baseline evaluation, SHAP interpretability, and automated reporting.",
            qstyles["Body"],
        ))
        el.append(PageBreak())

        # =====================================================================
        # CHAPTER 2  LITERATURE SURVEY
        # =====================================================================
        _chapter_block(el, 2, "LITERATURE SURVEY", qstyles)
        el.append(Paragraph(
            "A structured literature review spanning twenty-five peer-reviewed studies was conducted across epidemiological burden assessment, "
            "classical statistical time-series modeling, ensemble decision trees, deep sequence neural networks, chronological validation theory, "
            "and Shapley Explainable AI to anchor every architectural decision of AeroSense AI.",
            qstyles["BodyNoIndent"],
        ))

        el.append(_sec("2.1 Evolution of Air Pollution Modeling Paradigms", qstyles))
        el.append(_subsec("2.1.1 Classical Statistical and Ensemble Machine Learning Approaches", qstyles))
        el.append(Paragraph(
            "Early air quality prediction utilized chemical transport solvers and linear autoregressive ARIMA variants. With open "
            "telemetry availability, Breiman's Random Forests (2001), Friedman's Gradient Boosting (2001), Extra Trees by Geurts et al. (2006), "
            "XGBoost by Chen and Guestrin (2016), and LightGBM by Ke et al. (2017) achieved rapid adoption on tabular environmental lags. "
            "Applied studies by Masood and Ahmad (2021), Sengupta et al. (2021), and Nair et al. (2023) confirmed strong Delhi and multi-city "
            "accuracy, though Bergmeir and Benitez (2012) cautioned that standard k-fold cross-validation violates temporal causality.",
            qstyles["Body"],
        ))
        el.append(_subsec("2.1.2 Deep Sequence Networks and Attention Mechanisms", qstyles))
        el.append(Paragraph(
            "To capture long-range temporal abstractions directly from sequential histories, Hochreiter and Schmidhuber (1997) pioneered "
            "Long Short-Term Memory (LSTM) networks, later streamlined via Gated Recurrent Units (GRU) by Cho et al. (2014). Bai et al. (2018) "
            "demonstrated Dilated Causal Temporal Convolutional Networks (TCN), while Vaswani et al. (2017) introduced self-attention Transformers "
            "subsequently specialized for sequence forecasting by Zhou et al. (2021) and non-stationary PM2.5 haze by Zhang et al. (2023).",
            qstyles["Body"],
        ))

        el.append(_sec("2.2 Synthesis Matrix of Reviewed Research Literature", qstyles))
        _add_qu_table_block(
            el, "2.1", "Comparative Survey of Key Peer-Reviewed Air Pollution Forecasting Works",
            [
                ["Authors & Year", "Core Architecture", "Primary Strengths", "Identified Research Gap"],
                ["Breiman (2001); Geurts (2006)", "RandomForest / ExtraTrees", "Robust variance reduction on lags", "Cannot extrapolate above max(y_train)"],
                ["Chen & Guestrin (2016); Ke (2017)", "XGBoost / GBDT", "High accuracy & tabular speed", "Sensitive to temporal distribution shift"],
                ["Hochreiter (1997); Cho (2014)", "LSTM / GRU Networks", "Models sequential memory states", "Sequential steps; multi-day variance"],
                ["Bai et al. (2018); Liu (2022)", "Dilated Causal TCN", "Strict causality & GPU parallelism", "Requires careful dilation tuning"],
                ["Vaswani (2017); Zhang (2023)", "Transformer Attention", "Direct global attention across lags", "Needs meteorological covariates for h>1"],
                ["Bergmeir & Benitez (2012)", "Temporal Validation", "Exposes shuffled k-fold leakage", "Frequently ignored in student ML apps"],
                ["Lundberg & Lee (2017); Nair (2023)", "SHAP Attribution", "Game-theoretic local explanations", "Rarely unified with live OpenAQ v3 feeds"],
                ["AeroSense AI (This Project)", "ML + DL + XAI + v3 UI", "Chronological 70/15/15 & partial AQI", "Phase 2 will integrate ERA5 weather"],
            ],
            [3.6 * cm, 3.3 * cm, 4.0 * cm, 4.0 * cm],
            qstyles, font_pt=8.8,
        )

        el.append(_sec("2.3 Identified Engineering and Methodological Gaps", qstyles))
        el.append(Paragraph(
            "Three specific weaknesses motivate AeroSense AI: (1) widespread chronological leakage in applied notebooks; (2) omission of "
            "partial-pollutant disclosure rules during regulatory CPCB/EPA indexing; and (3) lack of unified empirical comparison showing "
            "where linear autoregressive slopes outperform bounded decision tree ensembles during non-stationary Indian smog peaks.",
            qstyles["Body"],
        ))
        el.append(PageBreak())

        # =====================================================================
        # CHAPTER 3  METHODOLOGY
        # =====================================================================
        _chapter_block(el, 3, "METHODOLOGY", qstyles)
        el.append(Paragraph(
            "AeroSense AI implements an end-to-end seven-stage engineering pipeline uniting authenticated external telemetry acquisition, "
            "deterministic data hygiene, dual regulatory indexing, leakage-free feature engineering, chronological model training, SHAP "
            "attribution, and automated multi-format academic reporting.",
            qstyles["BodyNoIndent"],
        ))

        el.append(_sec("3.1 Software and Hardware Requirements Specification", qstyles))
        _add_qu_table_block(
            el, "3.1", "Verified Software Stack, Environment Governance and Hardware Specifications",
            [
                ["Component Category", "Verified Specification & Versions"],
                ["Language & Runtime", "Python 3.12+ (Verified locally on Python 3.14.4 Windows & Streamlit Cloud)"],
                ["UI & Visualization", "Streamlit >= 1.35.0, Plotly >= 5.20 (MapLibre scatter_map), Matplotlib >= 3.8.0"],
                ["Data Engineering", "Pandas >= 2.1.0, NumPy >= 1.26.0, PyArrow >= 14.0 (Snappy Parquet), httpx >= 0.27.0"],
                ["ML, DL & Explainability", "Scikit-Learn >= 1.4, XGBoost >= 2.0, PyTorch >= 2.2 (CPU/CUDA), SHAP >= 0.45"],
                ["Reporting & QA", "ReportLab >= 4.0, python-pptx >= 0.6.23, Pytest >= 8.0, Streamlit AppTest"],
                ["Compute & Credentials", "Standard multi-core CPU / optional CUDA GPU; OPENAQ_API_KEY via .env / st.secrets"],
            ],
            [4.5 * cm, 10.4 * cm],
            qstyles, font_pt=9.2,
        )

        el.append(_sec("3.2 Problem Definition and Mathematical Formulation", qstyles))
        el.append(Paragraph(
            "Given an hourly univariate or multi-station time series {(t_i, y_i)} ordered monotonically in UTC, short-term horizon-1 "
            "and multi-step horizon-H air pollution forecasting predicts future concentration y_{t+h} using strictly causal past history "
            "{y_{t-k}, ... , y_{t-1}} and deterministic calendar features available prior to timestamp t. Model fidelity is quantified "
            "exclusively on unseen held-out test records using Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and Coefficient "
            "of Determination (R2).",
            qstyles["Body"],
        ))
        el.append(Paragraph("MAE = (1/N) * sum(|y_i - yhat_i|);    RMSE = sqrt((1/N) * sum((y_i - yhat_i)^2));    R2 = 1 - SSE / SST", qstyles["Formula"]))

        el.append(_sec("3.3 Core Platform Modules and Functionalities", qstyles))
        _add_qu_table_block(
            el, "3.2", "Modular Layer Decomposition and Responsibilities",
            [
                ["Package / Module", "Core Functionalities Delivered"],
                ["src/api/openaq_client.py", "Authenticated X-API-Key client, exponential backoff on 429/5xx, pagination"],
                ["src/data/bootstrap.py", "Cloud secrets sync, auto-seeding benchmark datasets & baseline ML models"],
                ["src/data/validation.py & cleaning.py", "Physical bounds check, deduplication, IQR x 3 filter, <= 6h interpolation"],
                ["src/aqi/cpcb.py & us_epa.py", "Exact piecewise-linear CPCB (2014) and US EPA sub-index & is_complete logic"],
                ["src/features/", "34 cyclical harmonics, shifted lags & rolling stats; (N, lookback, 1) tensors"],
                ["src/ml/ & src/dl/", "3 baselines, 6 tabular ML regressors, 4 PyTorch DL sequence architectures"],
                ["src/explainability/ & src/reporting/", "Native/permutation/SHAP drivers; MD, HTML, PDF, PPTX and ZIP report generators"],
            ],
            [5.2 * cm, 9.7 * cm],
            qstyles, font_pt=9.0,
        )

        el.append(_sec("3.4 Data Engineering Pipeline and Bounded Imputation", qstyles))
        el.append(Paragraph(
            "Live queries discover active stations via GET /v3/locations (filtered by ISO code and parameters_id) and extract hourly sensor "
            "streams from GET /v3/sensors/{id}/hours. Validation rejects physically impossible measurements (e.g., PM2.5 outside [0, 1000] ug/m3) "
            "and deduplicates (location_id, parameter, datetime_utc). Cleaning eliminates extreme sensor spikes exceeding Q3 + 3*IQR and "
            "interpolates only short telemetry outages <= 6 hours marked by is_imputed = True, preserving multi-day gaps transparently.",
            qstyles["Body"],
        ))

        el.append(_sec("3.5 Dual-Standard AQI Mathematical Formulation", qstyles))
        el.append(Paragraph(
            "Both CPCB (2014) and US EPA (2018) calculate pollutant sub-index I_p across breakpoint interval [BP_lo, BP_hi] and "
            "corresponding index bounds [I_lo, I_hi], reporting composite AQI as the dominant pollutant maximum alongside is_complete.",
            qstyles["Body"],
        ))
        el.append(Paragraph("I_p = round( ((I_hi - I_lo) / (BP_hi - BP_lo)) * (C_p - BP_lo) + I_lo );    AQI = max_p(I_p)", qstyles["Formula"]))

        el.append(_sec("3.6 Leakage-Free Feature Synthesis and Chronological Splitting", qstyles))
        el.append(Paragraph(
            "Periodic hour, day-of-week, and month indices are embedded cleanly onto sine/cosine unit circles to avoid midnight or year-end "
            "discontinuities. Lag variables (1, 3, 6, 12, 24h) and rolling statistics (mean, std, min, max over 3, 6, 12, 24h) operate strictly "
            "on target.shift(1), partitioned chronologically into 70% Train, 15% Validation, and 15% Held-Out Test splits.",
            qstyles["Body"],
        ))
        el.append(PageBreak())

        # =====================================================================
        # CHAPTER 4  SOFTWARE AND HARDWARE DESIGN
        # =====================================================================
        _chapter_block(el, 4, "SOFTWARE AND HARDWARE DESIGN", qstyles)
        el.append(Paragraph(
            "To uphold separation of concerns and enable seamless expansion from India (Phase 1) to global countries without altering core code, "
            "AeroSense AI enforces clean architectural boundaries modeled across Data Flow, UML Class, Sequence, Control Flow, and storage diagrams.",
            qstyles["BodyNoIndent"],
        ))

        el.append(_sec("4.1 Data Flow Diagrams and Control Governance", qstyles))
        el.append(Paragraph(
            "Level-1 Data Flow governance streams raw JSON payloads from OpenAQ API v3 through validation and IQR/interpolation processes "
            "into immutable raw/ and processed/ Apache Parquet repositories. Feature synthesis and chronological partitioning sit downstream "
            "prior to ML/DL training, ensuring interactive UI components consume strictly validated outputs.",
            qstyles["Body"],
        ))

        el.append(_sec("4.2 UML Class Sequence Object and Use Case Diagrams", qstyles))
        el.append(Paragraph(
            "Object interactions are encapsulated across OpenAQClient, DataIngestion, AQICalculator, MLTrainer, and PyTorch nn.Module subclasses "
            "(LSTMForecaster, GRUForecaster, TCNForecaster, TransformerForecaster). Figure 4.1 illustrates the unified Level-1 DFD, UML Class "
            "relationships, end-to-end Sequence invocation trace, and runtime Control Flow governance.",
            qstyles["Body"],
        ))
        _add_qu_figure(
            el, fig_dir, "fig6_uml_system_design.png", "Fig. 4.1",
            "AeroSense AI Level-1 DFD (A), UML Class Diagram (B), UML Sequence Diagram (C) and Control Flow / Use-Case Architecture (D)",
            qstyles, width_cm=14.6,
        )

        el.append(_sec("4.3 Persistent Storage and Apache Parquet Schema Design", qstyles))
        _add_qu_table_block(
            el, "4.1", "Processed Analytical Dataset Parquet Schema (data/processed/*.parquet)",
            [
                ["Column Name", "Arrow / Pandas Type", "Provenance & Analytical Role"],
                ["datetime_utc", "timestamp[ns, UTC]", "Chronological index enabling leakage-free 70/15/15 splits"],
                ["location_id / location_name", "int64 / string", "OpenAQ v3 station identifier and official monitor label"],
                ["city / country / latitude / longitude", "string / float64", "Geographic attributes for MapLibre spatial mapping"],
                ["sensor_id / parameter / unit", "int64 / string", "Traceable sensor key, normalized pollutant, ug/m3 unit"],
                ["value / is_imputed", "float64 / bool", "Observed or <= 6h interpolated reading with provenance mask"],
                ["source_provider / api_endpoint / retrieved_at", "string", "Audit trail guaranteeing zero fabricated telemetry"],
            ],
            [4.8 * cm, 3.6 * cm, 6.5 * cm],
            qstyles, font_pt=8.8,
        )
        el.append(PageBreak())

        # =====================================================================
        # CHAPTER 5  IMPLEMENTATION AND CODING TEMPLATES
        # =====================================================================
        _chapter_block(el, 5, "IMPLEMENTATION AND CODING TEMPLATES", qstyles)
        el.append(Paragraph(
            "This chapter details the production Python modules, class method contracts with input/output parameter types, algorithmic "
            "pseudo-code templates, and the ten-page interactive Streamlit interface powering AeroSense AI.",
            qstyles["BodyNoIndent"],
        ))

        el.append(_sec("5.1 Key Classes Methods Input and Output Parameters", qstyles))
        _add_qu_table_block(
            el, "5.1", "Core Software Classes, Methods, Inputs and Return Signatures",
            [
                ["Class / Function", "Input Parameters", "Return Output & Behavior"],
                ["OpenAQClient.get_sensor_hours", "sensor_id: int, datetime_from: str, datetime_to: str", "list[dict] of hourly sensor payloads with backoff retry"],
                ["validate_measurements", "df: pd.DataFrame", "Tuple[pd.DataFrame, ValidationReport] enforcing bounds"],
                ["clean_measurements", "df: pd.DataFrame, impute_strategy: str", "Hourly deduplicated DataFrame with is_imputed flag"],
                ["calculate_cpcb_aqi", "concentrations: dict | float, pollutant: str", "AQIResult(aqi, category, dominant_pollutant, is_complete)"],
                ["build_feature_matrix", "df: pd.DataFrame, target_col: str, drop_na: bool", "DataFrame with 34 leakage-free cyclical, lag & rolling cols"],
                ["train_models", "df: pd.DataFrame, model_names: list, save_dir: Path", "Metrics DataFrame + persisted .pkl model pipelines"],
                ["train_dl_model", "series: np.ndarray, model_name: str, horizon: int", "Dict(metrics, history, device) + saved PyTorch .pt state"],
            ],
            [4.5 * cm, 5.2 * cm, 5.2 * cm],
            qstyles, font_pt=8.6,
        )

        el.append(_sec("5.2 Algorithmic Coding Templates and Chronological Split Logic", qstyles))
        el.append(_subsec("5.2.1 Leakage-Free Chronological Feature & Split Template", qstyles))
        el.append(Paragraph(
            "def chronological_train_val_test(df, target_col='value'):<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;feat_df = build_feature_matrix(df.sort_values('datetime_utc'), drop_na=True)<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;n = len(feat_df); i1 = int(n * 0.70); i2 = int(n * 0.85)<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;X_tr, y_tr = feat_df.iloc[:i1][FEATURES], feat_df.iloc[:i1][target_col]<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;X_va, y_va = feat_df.iloc[i1:i2][FEATURES], feat_df.iloc[i1:i2][target_col]<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;X_te, y_te = feat_df.iloc[i2:][FEATURES], feat_df.iloc[i2:][target_col]<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;return X_tr, y_tr, X_va, y_va, X_te, y_te",
            qstyles["Code"],
        ))

        el.append(_subsec("5.2.2 MapLibre Spatial Rendering & Cloud Secrets Bootstrap Template", qstyles))
        el.append(Paragraph(
            "def ensure_ready():  # src/data/bootstrap.py<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;sync_streamlit_secrets()  # maps st.secrets['OPENAQ_API_KEY'] safely<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;if not list_processed_files(): seed_all_benchmarks()<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;if not list(ML_MODELS_DIR.glob('*.pkl')): train_baseline_models()<br/>"
            "def map_scatter(df):  # Plotly >=5.24 MapLibre compatible<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;return px.scatter_map(df, lat='latitude', lon='longitude', color='value', map_style='carto-darkmatter')",
            qstyles["Code"],
        ))

        el.append(_sec("5.3 Interactive Ten-Page Streamlit Application Suite", qstyles))
        el.append(Paragraph(
            "The multi-page UI (app.py + pages/01..10) provides zero-code access to OpenAQ v3 extraction (01_Global_Data_Explorer), "
            "exploratory temporal/statistical analytics (02_Pollution_Analytics), dual CPCB/EPA gauges (03_AQI_Intelligence), interactive "
            "ML/DL training (04_Forecasting_Studio), unified benchmarking (05_Model_Benchmarking), Tree/Linear SHAP explanations "
            "(06_Explainable_AI), spatial hotspots and Haversine matrices (07_Spatial_Hotspot_Analysis), WHO/NAAQS health risk advisories "
            "(08_Health_Risk_and_Advisory), academic export bundles (09_Research_Reports), and system diagnostics (10_System_Diagnostics).",
            qstyles["Body"],
        ))
        el.append(PageBreak())

        # =====================================================================
        # CHAPTER 6  RESULTS AND DISCUSSION
        # =====================================================================
        _chapter_block(el, 6, "RESULTS AND DISCUSSION", qstyles)
        el.append(Paragraph(
            "This chapter presents comprehensive black-box and white-box automated verification results alongside empirical findings from "
            "both live OpenAQ API v3 Indian telemetry and the 90-day controlled benchmark across fourteen forecasting models.",
            qstyles["BodyNoIndent"],
        ))

        el.append(_sec("6.1 Automated Black-Box and White-Box Testing Verification", qstyles))
        _add_qu_table_block(
            el, "6.1", "Automated Black-Box and White-Box Test Case Verification Suite (46/46 Passing)",
            [
                ["Test Suite / Type", "Cases", "Verified Assertion Coverage", "Outcome"],
                ["test_aqi.py (Black-Box)", "12", "CPCB Good->Severe, PM10, US EPA breakpoints, invalid negative guards", "12/12 PASS"],
                ["test_validation.py (White-Box)", "4", "Bounds enforcement, deduplication, IQR filter & <= 6h interpolation", "4/4 PASS"],
                ["test_features.py & test_ml_dl.py", "5", "34-col lag/rolling alignment, chronological splits, LSTM/GRU/TCN/Trans shapes", "5/5 PASS"],
                ["test_bootstrap.py & test_charts.py", "5", "Cloud st.secrets sync, auto-seeding & Plotly scatter_map MapLibre rendering", "5/5 PASS"],
                ["test_api, explainability & reporting", "9", "OpenAQ v3 pagination/401, Tree/Linear SHAP, MD/HTML/PDF/ZIP exports", "9/9 PASS"],
                ["test_streamlit_pages.py (E2E AppTest)", "11", "Headless end-to-end execution of app.py + all 10 UI pages without errors", "11/11 PASS"],
            ],
            [4.5 * cm, 1.3 * cm, 6.9 * cm, 2.2 * cm],
            qstyles, font_pt=8.5,
        )

        el.append(_sec("6.2 Live OpenAQ v3 Telemetry Analysis and Regulatory Exceedance", qstyles))
        el.append(Paragraph(
            "Figure 6.1 displays multi-city daily concentrations and IST diurnal boundary-layer oscillations across live Delhi R K Puram, "
            "Lucknow Talkatora, and Hyderabad Zoo Park sensors. Morning traffic and nocturnal inversions drive acute PM2.5 buildup, while "
            "Figure 6.2 demonstrates that 92.2% to 98.6% of valid hours breach the WHO 24-hour 15 ug/m3 guideline.",
            qstyles["Body"],
        ))
        _add_qu_figure(el, fig_dir, "fig1_live_station_profiles.png", "Fig. 6.1", "Live OpenAQ v3 Daily Mean PM2.5 Trends (A) and IST Diurnal Cycle (B)", qstyles, width_cm=14.6)
        _add_qu_figure(el, fig_dir, "fig5_aqi_exceedance.png", "Fig. 6.2", "Live CPCB AQI Category Share (A) and WHO / Indian NAAQS Breach Rates (B)", qstyles, width_cm=14.6)

        el.append(_sec("6.3 Controlled 90-Day Benchmark and Live Delhi Non-Stationarity", qstyles))
        _add_qu_table_block(
            el, "6.2", "Controlled 90-Day Chronological Test Leaderboard (Delhi Anand Vihar, n = 2,161)",
            [
                ["Model Architecture", "Family & Horizon", "Test MAE", "Test RMSE", "Test R2"],
                ["LinearRegression / Ridge", "ML Tabular (h=1)", "9.449 / 9.457", "11.947 / 11.948", "0.906 / 0.906"],
                ["TransformerForecaster", "DL Attention (h=1)", "9.580", "12.124", "0.903"],
                ["RandomForest / HistGradientBoosting", "ML Ensemble (h=1)", "9.930 / 10.149", "12.402 / 12.534", "0.898 / 0.896"],
                ["GRU / XGBoost / ExtraTrees", "DL & ML (h=1)", "10.161 / 10.319 / 10.575", "12.976 / 13.023 / 13.139", "0.889 / 0.888 / 0.886"],
                ["LSTM / TCN", "DL Sequence (h=1)", "10.838 / 11.851", "13.579 / 14.653", "0.878 / 0.858"],
                ["LSTM Multi-Step / Seasonal Naive", "DL (h=24) / Baseline", "30.288 / 30.966", "37.029 / 38.726", "0.094 / 0.008"],
            ],
            [4.8 * cm, 3.2 * cm, 2.4 * cm, 2.5 * cm, 2.0 * cm],
            qstyles, font_pt=8.6,
        )
        _add_qu_figure(el, fig_dir, "fig2_model_benchmark.png", "Fig. 6.3", "Controlled 1-Step Test MAE and R2 Comparison Across ML and DL Architectures", qstyles, width_cm=14.6)

        _add_qu_table_block(
            el, "6.3", "Live Delhi R K Puram Chronological Evaluation (n = 639, Oct–Nov 2026)",
            [
                ["Model on Live R K Puram", "Test MAE (ug/m3)", "Test RMSE (ug/m3)", "Test R2", "Gain vs Seasonal Naive"],
                ["LinearRegression / Ridge", "23.803 / 24.714", "30.540 / 32.074", "0.854 / 0.839", "57.1% / 55.5% MAE gain"],
                ["RandomForest / ExtraTrees", "26.534 / 31.829", "35.573 / 41.481", "0.802 / 0.731", "52.2% / 42.7% MAE gain"],
                ["HistGradientBoosting / XGBoost", "32.799 / 33.479", "40.471 / 42.794", "0.744 / 0.714", "40.9% / 39.7% MAE gain"],
                ["Seasonal Naive / Persistence", "55.515 / 61.876", "71.767 / 85.158", "0.165 / -0.176", "Reference Baselines"],
            ],
            [4.5 * cm, 2.7 * cm, 2.7 * cm, 2.0 * cm, 3.0 * cm],
            qstyles, font_pt=8.6,
        )
        el.append(Paragraph(
            "Crucially, Table 6.3 explains a foundational physical-ML insight: on live Delhi R K Puram measurements, linear regressors "
            "decisively outperform decision-tree ensembles during non-stationary November smog spikes reaching 501.00 ug/m3. Because decision "
            "tree leaves predict bounded averages inside [min(y_train), max(y_train)], tree ensembles underestimate unseen extremes, whereas "
            "linear autoregressive weights on lag_1 and trend_24 extrapolate smoothly.",
            qstyles["Body"],
        ))
        _add_qu_figure(el, fig_dir, "fig3_forecast_residuals.png", "Fig. 6.4", "Held-Out Test Forecast Trajectory (A) and Residual Error Distribution (B)", qstyles, width_cm=14.6)

        el.append(_sec("6.4 Explainable AI SHAP Drivers and Platform Screens", qstyles))
        el.append(Paragraph(
            "TreeSHAP attributions across 120 test instances (Figure 6.5) verify physically coherent drivers: lag_1 dominates at "
            "26.91 ug/m3 mean |SHAP|, followed by diurnal boundary-layer encoding (hour_sin = 2.58, hour = 2.09) and 24-hour momentum "
            "trend_24 = 1.39 ug/m3.",
            qstyles["Body"],
        ))
        _add_qu_figure(el, fig_dir, "fig4_shap_importance.png", "Fig. 6.5", "Top-10 Mean |SHAP| Feature Attributions on Held-Out Test Predictions", qstyles, width_cm=13.5)
        el.append(PageBreak())

        # =====================================================================
        # CHAPTER 7  CONCLUSIONS
        # =====================================================================
        _chapter_block(el, 7, "CONCLUSIONS", qstyles)
        el.append(Paragraph(
            "AeroSense AI delivers a modular, production-verified air pollution monitoring and forecasting platform spanning live OpenAQ v3 "
            "telemetry, rigorous cleaning, dual regulatory indexing, leakage-free forecasting, explainability, and academic reporting.",
            qstyles["BodyNoIndent"],
        ))
        el.append(_sec("7.1 Summary of Engineering Contributions", qstyles))
        el.append(Paragraph(
            "First, the platform replaces brittle ad-hoc notebooks with deterministic validation, <= 6-hour bounded interpolation provenance, "
            "and Cloud-bootstrapped benchmark storage. Second, transparent dual CPCB/US EPA AQI computation highlights incomplete sensor coverage "
            "honestly via is_complete. Third, strict 70/15/15 chronological benchmarking proves Linear Regression (9.449 ug/m3 controlled MAE; "
            "23.803 ug/m3 live MAE) and PyTorch Transformer (9.580 ug/m3 MAE) cut error by 57.1% to 69.5% relative to naive baselines while "
            "revealing boundary-extrapolation trade-offs under extreme pollution.",
            qstyles["Body"],
        ))
        el.append(_sec("7.2 Current System Limitations", qstyles))
        el.append(Paragraph(
            "Current Phase 1 forecasting models rely strictly on univariate ground monitor concentration history and calendar harmonics; without "
            "synoptic meteorological covariates (wind speed, mixing height, relative humidity), direct 24-hour multi-step deep learning accuracy "
            "(30.288 ug/m3 MAE) deteriorates over extended forecast horizons when sudden weather fronts alter dispersion.",
            qstyles["Body"],
        ))
        el.append(PageBreak())

        # =====================================================================
        # CHAPTER 8  FUTURE WORK AND RECOMMENDATIONS
        # =====================================================================
        _chapter_block(el, 8, "FUTURE WORK AND RECOMMENDATIONS", qstyles)
        el.append(Paragraph(
            "Planned Phase 2 research extensions build directly upon AeroSense AI's modular ingestion and feature interfaces to enhance "
            "multi-day generalization and municipal operational utility.",
            qstyles["BodyNoIndent"],
        ))
        el.append(_sec("8.1 Meteorological Fusion and Spatio-Temporal Graph Modeling", qstyles))
        el.append(Paragraph(
            "Integrating Copernicus ERA5 planetary boundary-layer height, temperature, relative humidity, and u/v wind components into the "
            "optional provider package alongside cross-station Spatio-Temporal Graph Neural Networks (ST-GNNs) will enable explicit modeling of "
            "upwind-to-downwind pollutant advection over 24- to 72-hour horizons.",
            qstyles["Body"],
        ))
        el.append(_sec("8.2 Global Expansion and Municipal Deployment Recommendations", qstyles))
        el.append(Paragraph(
            "Because OpenAQClient parameterizes station discovery strictly by ISO country codes, municipalities and environmental agencies can "
            "deploy automated scheduled retraining pipelines globally. Coupling live AQI alert webhooks with hospital, school, and municipal "
            "advisories transforms retrospective dashboards into proactive respiratory early-warning infrastructure.",
            qstyles["Body"],
        ))
        el.append(PageBreak())

        # =====================================================================
        # REFERENCES (25 Alphabetically Sorted Author Bibliography - Report p.5)
        # =====================================================================
        ref_h = Paragraph("REFERENCES", qstyles["ChapterTitle"])
        ref_h._qu_toc = ("back", "REFERENCES", "REFERENCES")
        el.append(ref_h)
        el.append(Spacer(1, 6))
        for ref_line in alpha_refs:
            el.append(Paragraph(html.escape(ref_line), qstyles["Bib"]))
        el.append(PageBreak())

        # APPENDICES
        app_h = Paragraph("APPENDICES", qstyles["ChapterTitle"])
        app_h._qu_toc = ("back", "APPENDICES", "APPENDICES")
        el.append(app_h)
        el.append(Paragraph(
            "Appendix A  Deployment Quickstart — Run pip install -r requirements.txt, configure OPENAQ_API_KEY in .env or Streamlit Cloud "
            "Secrets, launch streamlit run app.py, and verify with python -m pytest tests/ -v (46/46 passing).",
            qstyles["BodyNoIndent"],
        ))
        el.append(Paragraph(
            "Appendix B  Viva Defense Summary — Key defense talking points cover chronological 70/15/15 leakage prevention, why rolling "
            "windows shift onto y_{t-1}, OpenAQ v3 X-API-Key sensor scoping, tree leaf extrapolation limits under November Delhi smog, and "
            "PyTorch causal TCN chomp padding.",
            qstyles["BodyNoIndent"],
        ))

        doc.build(el, onFirstPage=_footer, onLaterPages=_footer)
        return tracker

    pass1 = _compile({})
    _compile(pass1)
    shutil.copy2(pdf_path, title_pdf_path)

    # Markdown Companion matching Quantum University sections & metadata
    team_md = "\n".join(f"| {m[0]} | {m[1]} | {m[2]} | {m[3]} |" for m in team_members)
    refs_md = "\n".join(f"- {r}" for r in alpha_refs)
    md_text = f"""# AIR POLLUTION PATTERN ANALYSIS AND AQI FORECASTING
**Platform:** {meta['app_name']} — *"{meta['tagline']}"*  
**Institution:** Department of Computer Science and Engineering, Quantum School of Technology, Quantum University, Roorkee - 247167  
**Degree / Batch / Semester:** B.Tech (CSE-DS) | Batch 2023 - 2027 | Semester 7 | Year: 2026  
**Project Guide:** {meta['guide']}  
**Soft-Copy Deliverables:** `AeroSense_Final_Project_Report.pdf` & `Air_Pollution_Pattern_Analysis_and_AQI_Forecasting.pdf`

### Project Group Members (4 Students)
| Student Name | Student ID & Roll No. | Batch / Sem / Branch | Primary Engineering Ownership |
| :--- | :--- | :--- | :--- |
{team_md}

---

## Chapters Summary (Quantum University Official Format)
- **Margins:** A4 (`21.0 x 29.7 cm`), Left `4 cm`, Top `3 cm`, Bottom `3 cm`, Right `2 cm`
- **Typography:** Times New Roman `12 pt`, `1.5` line spacing, 5-space first-line paragraph indent, bottom-center page numbering (`i–viii` front matter, `1+` main chapters)
- **Chapters:**
  1. `CHAPTER 1  INTRODUCTION`
  2. `CHAPTER 2  LITERATURE SURVEY` (25 papers synthesized)
  3. `CHAPTER 3  METHODOLOGY`
  4. `CHAPTER 4  SOFTWARE AND HARDWARE DESIGN` (DFD, UML Class/Sequence/Control Flow, Parquet Schema)
  5. `CHAPTER 5  IMPLEMENTATION AND CODING TEMPLATES`
  6. `CHAPTER 6  RESULTS AND DISCUSSION` (46/46 pytest QA, Live OpenAQ v3, 14-model ML/DL benchmarks, SHAP)
  7. `CHAPTER 7  CONCLUSIONS`
  8. `CHAPTER 8  FUTURE WORK AND RECOMMENDATIONS`

## References (Alphabetical by Author Surname — 25 Works)
{refs_md}
"""
    md_path.write_text(md_text, encoding="utf-8")
    return pdf_path, md_path
