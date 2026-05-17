"""
Per-student PDF report generation.

Flow:
  1. View Records list renders a Download PDF button per row (Streamlit download_button).
  2. On click, Streamlit calls generate_student_pdf(student) — no session_state writes.
  3. ReportLab builds an in-memory PDF (title, detail table, optional QR, footer).
  4. Bytes are returned to st.download_button as file_name student_<id>.pdf.
"""

import io
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from qr_utils import generate_student_qr


def student_pdf_filename(student_id: int | str) -> str:
    """Standard download name: student_101.pdf"""
    return f"student_{student_id}.pdf"


def _detail_rows(student: dict[str, Any]) -> list[tuple[str, str]]:
    return [
        ("Student ID", str(student["student_id"])),
        ("First Name", str(student["first_name"])),
        ("Last Name", str(student["last_name"])),
        ("Gender", str(student["gender"])),
        ("Course", str(student["course"])),
        ("Branch", str(student["branch"])),
        ("Email", str(student["mail"])),
        ("Contact", str(student["contact"])),
        ("State", str(student["state"])),
        ("Address", str(student["address"])),
        ("Pincode", str(student["areapincode"])),
    ]


def generate_student_pdf(student: dict[str, Any], *, include_qr: bool = True) -> bytes:
    """
    Build a single-student PDF report as bytes (never writes to disk).

    Layout: title → details table → optional embedded QR → footer branding.
    """
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
        spaceAfter=16,
        alignment=TA_CENTER,
    )
    section_style = ParagraphStyle(
        "SectionHead",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#1f4e79"),
        spaceBefore=8,
        spaceAfter=10,
    )
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#5a6a7a"),
        alignment=TA_CENTER,
        spaceBefore=20,
    )

    full_name = f"{student['first_name']} {student['last_name']}"
    story: list = [
        Paragraph("Student Report", title_style),
        Paragraph(f"Student: {full_name}", subtitle_style),
        Paragraph("Student Details", section_style),
    ]

    # Detail table with emoji labels (glyph rendering depends on PDF viewer/font).
    emoji_prefix = {
        "Student ID": "🆔",
        "First Name": "👤",
        "Last Name": "👤",
        "Gender": "🚻",
        "Course": "📘",
        "Branch": "💻",
        "Email": "📧",
        "Contact": "📱",
        "State": "🌍",
        "Address": "🏠",
        "Pincode": "📮",
    }

    table_data = [["Field", "Value"]]
    for label, value in _detail_rows(student):
        display_label = f"{emoji_prefix.get(label, '')} {label}".strip()
        table_data.append([display_label, value])

    detail_table = Table(table_data, colWidths=[2.2 * inch, 4.0 * inch])
    detail_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("TOPPADDING", (0, 0), (-1, 0), 10),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d0d7de")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(detail_table)
    story.append(Spacer(1, 0.25 * inch))

    # Bonus: embed scannable QR for this student (same payload as View QR).
    if include_qr:
        qr_png, _ = generate_student_qr(student)
        if qr_png:
            story.append(Paragraph("Student QR Code", section_style))
            qr_image = RLImage(io.BytesIO(qr_png), width=1.45 * inch, height=1.45 * inch)
            qr_image.hAlign = "CENTER"
            story.append(qr_image)
            story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("Generated by Smart Student Management System", footer_style))
    story.append(
        Paragraph(
            '<font color="#1f4e79"><b>Smart Student Management System</b></font>',
            footer_style,
        )
    )

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()
