"""Dashboard statistics, charts, and data export."""

import io
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import cm

from crud import get_all_students

try:
    plt.style.use("seaborn-v0_8-whitegrid")
except OSError:
    plt.style.use("ggplot")


def get_dashboard_stats() -> dict:
    students = get_all_students()
    total = len(students)
    male = sum(1 for s in students if str(s["gender"]).lower() == "male")
    female = sum(1 for s in students if str(s["gender"]).lower() == "female")
    branches = len({s["branch"] for s in students})
    states = len({s["state"] for s in students})
    return {
        "total": total,
        "male": male,
        "female": female,
        "other": total - male - female,
        "branches": branches,
        "states": states,
    }


def students_to_dataframe() -> pd.DataFrame:
    students = get_all_students()
    columns = [
        "student_id",
        "first_name",
        "last_name",
        "gender",
        "course",
        "branch",
        "mail",
        "contact",
        "state",
        "address",
        "areapincode",
    ]
    if not students:
        return pd.DataFrame(columns=columns)
    df = pd.DataFrame(students)
    return df[columns]


def students_display_dataframe() -> pd.DataFrame:
    """DataFrame with visual-only serial numbers (not stored in DB)."""
    df = students_to_dataframe()
    if df.empty:
        return df
    df = df.copy()
    df.insert(0, "S.No", range(1, len(df) + 1))
    return df


def _students_df() -> pd.DataFrame:
    return students_to_dataframe()


def gender_pie_chart() -> bytes | None:
    df = _students_df()
    if df.empty:
        return None

    counts = df["gender"].str.title().value_counts()
    colors = ["#4C78A8", "#F58518", "#E45756", "#72B7B2"][: len(counts)]

    fig, ax = plt.subplots(figsize=(6, 4.5))
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors,
        explode=[0.03] * len(counts),
        shadow=True,
    )
    for t in autotexts:
        t.set_fontsize(9)
        t.set_fontweight("bold")
    ax.set_title("Gender Distribution", fontsize=13, fontweight="bold", pad=12)
    fig.tight_layout()
    return _fig_to_bytes(fig)


def branch_bar_chart() -> bytes | None:
    df = _students_df()
    if df.empty:
        return None

    branch_counts = df.groupby("branch", sort=False).size().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(branch_counts.index, branch_counts.values, color=cm.tab10(range(len(branch_counts))))
    ax.bar_label(bars, padding=3, fontsize=9)
    ax.set_xlabel("Branch", fontweight="bold")
    ax.set_ylabel("Number of Students", fontweight="bold")
    ax.set_title("Students per Branch", fontsize=13, fontweight="bold", pad=12)
    plt.xticks(rotation=40, ha="right")
    fig.tight_layout()
    return _fig_to_bytes(fig)


def state_bar_chart() -> bytes | None:
    df = _students_df()
    if df.empty:
        return None

    state_counts = df.groupby("state", sort=False).size().sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(9, max(4.5, len(state_counts) * 0.35)))
    colors = cm.viridis([i / max(len(state_counts) - 1, 1) for i in range(len(state_counts))])
    bars = ax.barh(state_counts.index, state_counts.values, color=colors)
    ax.bar_label(bars, padding=3, fontsize=8)
    ax.set_xlabel("Number of Students", fontweight="bold")
    ax.set_ylabel("State", fontweight="bold")
    ax.set_title("State-wise Student Distribution", fontsize=13, fontweight="bold", pad=12)
    fig.tight_layout()
    return _fig_to_bytes(fig)


def branch_summary_table() -> pd.DataFrame:
    df = _students_df()
    if df.empty:
        return pd.DataFrame()
    summary = (
        df.groupby(["branch", "gender"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    summary["Total"] = summary.select_dtypes(include="number").sum(axis=1)
    return summary


def _fig_to_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def export_csv() -> bytes:
    return students_display_dataframe().to_csv(index=False).encode("utf-8")


def export_excel() -> bytes:
    df = students_display_dataframe()
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Students")
        summary = branch_summary_table()
        if not summary.empty:
            summary.to_excel(writer, index=False, sheet_name="Branch Summary")
    buf.seek(0)
    return buf.getvalue()


def export_pdf() -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    df = students_display_dataframe()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("<b>Student Management System — Records Export</b>", styles["Title"]),
        Spacer(1, 12),
    ]

    if df.empty:
        elements.append(Paragraph("No student records found.", styles["Normal"]))
    else:
        headers = list(df.columns)
        data = [headers] + df.astype(str).values.tolist()
        table = Table(data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 7),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7fa")]),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ]
            )
        )
        elements.append(table)

    doc.build(elements)
    buf.seek(0)
    return buf.getvalue()
