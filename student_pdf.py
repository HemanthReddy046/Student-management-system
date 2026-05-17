"""
Per-student PDF report generation.

Flow:
  1. View Records list renders a Download PDF button per row (Streamlit download_button).
  2. On click, Streamlit calls generate_student_pdf(student) — no session_state writes.
  3. ReportLab builds an in-memory PDF (title, detail lines, optional QR).
  4. Bytes are returned to st.download_button as file_name student_<id>.pdf.
"""

import io
import platform
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from qr_utils import generate_student_qr

_DETAIL_FONT = "Helvetica"
_DETAIL_FONT_REGISTERED = False


def _register_detail_font() -> str:
    """Prefer a system font with broader Unicode/emoji coverage when available."""
    global _DETAIL_FONT, _DETAIL_FONT_REGISTERED
    if _DETAIL_FONT_REGISTERED:
        return _DETAIL_FONT

    candidates: list[tuple[str, Path]] = []
    if platform.system() == "Windows":
        win = Path(r"C:\Windows\Fonts")
        candidates.extend(
            [
                ("SegoeUI", win / "segoeui.ttf"),
                ("SegoeUISymbol", win / "seguisym.ttf"),
            ]
        )
    else:
        candidates.extend(
            [
                ("DejaVuSans", Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")),
                (
                    "NotoSans",
                    Path("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"),
                ),
            ]
        )

    for font_name, font_path in candidates:
        if font_path.is_file():
            try:
                pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
                _DETAIL_FONT = font_name
                break
            except Exception:
                continue

    _DETAIL_FONT_REGISTERED = True
    return _DETAIL_FONT


def student_pdf_filename(student_id: int | str) -> str:
    """Standard download name: student_101.pdf"""
    return f"student_{student_id}.pdf"


def _escape_xml(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _detail_line_html(emoji: str, label: str, value: str, *, link: str | None = None) -> str:
    safe_label = _escape_xml(label)
    safe_value = _escape_xml(value)
    if link:
        safe_value = (
            f'<a href="{_escape_xml(link)}" color="#1f4e79">{safe_value}</a>'
        )
    return f"{emoji} <b>{safe_label}:</b> {safe_value}"


def _build_detail_lines(student: dict[str, Any]) -> list[str]:
    full_name = f"{student['first_name']} {student['last_name']}".strip()
    email = str(student["mail"])
    return [
        _detail_line_html("🆔", "Student ID", str(student["student_id"])),
        _detail_line_html("👤", "Name", full_name),
        _detail_line_html("⚧", "Gender", str(student["gender"])),
        _detail_line_html("🎓", "Course", str(student["course"])),
        _detail_line_html("🏢", "Branch", str(student["branch"])),
        _detail_line_html("📧", "Email", email, link=f"mailto:{email}"),
        _detail_line_html("📱", "Contact", str(student["contact"])),
        _detail_line_html("🌍", "State", str(student["state"])),
        _detail_line_html("🏠", "Address", str(student["address"])),
        _detail_line_html("📮", "Pincode", str(student["areapincode"])),
    ]


def generate_student_pdf(student: dict[str, Any], *, include_qr: bool = True) -> bytes:
    """
    Build a single-student PDF report as bytes (never writes to disk).

    Layout: title → emoji detail lines → optional embedded QR.
    """
    detail_font = _register_detail_font()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=48,
        rightMargin=48,
        topMargin=48,
        bottomMargin=48,
        title=f"Student Report {student['student_id']}",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#1f4e79"),
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.HexColor("#5a6a7a"),
        spaceAfter=18,
        alignment=TA_CENTER,
    )
    section_style = ParagraphStyle(
        "SectionHead",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#1f4e79"),
        spaceBefore=4,
        spaceAfter=12,
    )
    detail_style = ParagraphStyle(
        "DetailLine",
        parent=styles["Normal"],
        fontName=detail_font,
        fontSize=11,
        leading=20,
        textColor=colors.HexColor("#1e293b"),
        alignment=TA_LEFT,
        spaceAfter=4,
        spaceBefore=2,
    )

    full_name = f"{student['first_name']} {student['last_name']}"
    story: list = [
        Paragraph("Student Report", title_style),
        Paragraph(f"Student: {_escape_xml(full_name)}", subtitle_style),
        Paragraph("Student Details", section_style),
    ]

    detail_rows = [
        [Paragraph(line, detail_style)] for line in _build_detail_lines(student)
    ]
    details_table = Table(detail_rows, colWidths=[5.4 * inch])
    details_table.hAlign = "CENTER"
    details_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, 0), 14),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 14),
                ("TOPPADDING", (0, 1), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 18),
                ("RIGHTPADDING", (0, 0), (-1, -1), 18),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(details_table)
    story.append(Spacer(1, 0.3 * inch))

    if include_qr:
        qr_png, _ = generate_student_qr(student)
        if qr_png:
            story.append(Paragraph("Student QR Code", section_style))
            qr_image = RLImage(io.BytesIO(qr_png), width=1.45 * inch, height=1.45 * inch)
            qr_image.hAlign = "CENTER"
            story.append(qr_image)

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()
