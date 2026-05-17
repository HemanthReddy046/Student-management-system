"""QR code generation — mobile-friendly URLs, high-res images, and safe fallbacks."""

import io
import json
import os
from collections import Counter
from typing import Any
from urllib.parse import urlencode, urlparse

import qrcode
from qrcode.constants import ERROR_CORRECT_H

from crud import get_all_students

# URL payloads stay short; plain-text summaries may still be trimmed for previews.
MAX_QR_CHARS = 900
MAX_QR_VERSION = 40
DEFAULT_LOCAL_PORT = "8501"


def get_qr_base_url() -> str:
    """
    Absolute app base URL for QR links (no trailing slash).
    Set SMS_APP_BASE_URL on Streamlit Cloud if auto-detect fails.
    """
    explicit = os.environ.get("SMS_APP_BASE_URL", "").strip()
    if explicit:
        return explicit.rstrip("/")

    try:
        import streamlit as st

        ctx_url = getattr(getattr(st, "context", None), "url", None)
        if ctx_url:
            parsed = urlparse(str(ctx_url))
            if parsed.scheme and parsed.netloc:
                path = (parsed.path or "").rstrip("/")
                if path.endswith("/app.py"):
                    path = path[: -len("/app.py")]
                return f"{parsed.scheme}://{parsed.netloc}{path}".rstrip("/") or (
                    f"{parsed.scheme}://{parsed.netloc}"
                )
    except Exception:
        pass

    host = os.environ.get("STREAMLIT_SERVER_ADDRESS", "localhost")
    port = os.environ.get("STREAMLIT_SERVER_PORT", DEFAULT_LOCAL_PORT)
    return f"http://{host}:{port}".rstrip("/")


def student_qr_url(student_id: int | str) -> str:
    """Scannable link → mobile student detail page with PDF download."""
    params = urlencode({"view": "student", "id": str(student_id)})
    return f"{get_qr_base_url()}/?{params}"


def database_qr_url() -> str:
    """Scannable link → mobile full-database view with export download."""
    params = urlencode({"view": "database"})
    return f"{get_qr_base_url()}/?{params}"


def student_to_text(student: dict[str, Any]) -> str:
    """Human-readable preview text (not embedded in QR payloads)."""
    return (
        f"Student ID: {student['student_id']}\n"
        f"Name: {student['first_name']} {student['last_name']}\n"
        f"Gender: {student['gender']}\n"
        f"Course: {student['course']}\n"
        f"Branch: {student['branch']}\n"
        f"Email: {student['mail']}\n"
        f"Contact: {student['contact']}\n"
        f"State: {student['state']}\n"
        f"Address: {student['address']}\n"
        f"Pincode: {student['areapincode']}"
    )


def all_students_to_text() -> str:
    """Full text dump for previews/exports — not used inside QR payloads."""
    students = get_all_students()
    if not students:
        return "No student records in database."
    lines = [f"Total Students: {len(students)}", "=" * 40]
    for s in students:
        lines.append(student_to_text(s))
        lines.append("-" * 40)
    return "\n".join(lines)


def database_qr_summary() -> str:
    """
    Compact summary for UI previews (QR now encodes database_qr_url() instead).
    """
    students = get_all_students()
    if not students:
        return "Student Management System\nNo student records in database."

    branch_counts = Counter(s["branch"] for s in students)
    state_counts = Counter(s["state"] for s in students)

    lines = [
        "Student Management System",
        f"Total Students: {len(students)}",
        "Scan QR to open full mobile database view.",
        "",
        "Branch counts:",
    ]
    for branch, count in branch_counts.most_common(10):
        lines.append(f"  {branch}: {count}")

    lines.extend(["", "State counts:"])
    for state, count in state_counts.most_common(8):
        lines.append(f"  {state}: {count}")

    lines.extend(["", "Records (ID | Name | Branch):"])
    max_rows = 20
    for s in students[:max_rows]:
        lines.append(
            f"{s['student_id']} | {s['first_name']} {s['last_name']} | {s['branch']}"
        )
    if len(students) > max_rows:
        lines.append(f"... +{len(students) - max_rows} more (export files for full list)")

    return "\n".join(lines)


def all_students_to_json() -> str:
    return json.dumps(get_all_students(), indent=2, default=str)


def prepare_qr_payload(text: str) -> tuple[str, str | None]:
    """Ensure UTF-8-safe payload; trim only oversized plain-text (legacy previews)."""
    payload = (text or "").strip() or "No data"
    warning = None
    if payload.startswith("http://") or payload.startswith("https://"):
        return payload, None
    if len(payload) > MAX_QR_CHARS:
        payload = payload[: MAX_QR_CHARS - 3] + "..."
        warning = "Content shortened for QR size. Use CSV/Excel/PDF export for full data."
    return payload, warning


def generate_qr_png(
    text: str,
    *,
    box_size: int = 10,
    border: int = 4,
) -> tuple[bytes | None, str | None]:
    """
    Build a high-resolution PNG QR image (UTF-8, error correction H).

    Returns (image_bytes, warning_message). Never raises.
    """
    payload, warning = prepare_qr_payload(text)
    extra_warnings: list[str] = [warning] if warning else []

    for attempt in range(6):
        try:
            qr = qrcode.QRCode(
                version=None,
                error_correction=ERROR_CORRECT_H,
                box_size=box_size,
                border=border,
            )
            qr.add_data(payload.encode("utf-8"))
            qr.make(fit=True)

            if qr.version is not None and qr.version > MAX_QR_VERSION:
                raise ValueError(f"QR version {qr.version} exceeds limit {MAX_QR_VERSION}")

            img = qr.make_image(fill_color="#1f4e79", back_color="white")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            combined = " ".join(w for w in extra_warnings if w).strip() or None
            return buf.getvalue(), combined

        except (ValueError, Exception):
            if payload.startswith("http"):
                box_size = max(6, box_size - 2)
                extra_warnings.append("Retrying QR with adjusted size.")
                continue
            new_len = max(120, int(len(payload) * 0.7))
            payload = payload[:new_len].rstrip() + "\n[Truncated for QR]"
            extra_warnings.append("QR content was compressed to stay within scan limits.")

    return None, "Unable to generate QR. Please use CSV, Excel, or PDF export."


def generate_student_qr(student: dict[str, Any]) -> tuple[bytes | None, str | None]:
    """QR for a single student — encodes mobile-friendly URL (not raw text)."""
    return generate_qr_png(student_qr_url(student["student_id"]))


def generate_database_qr() -> tuple[bytes | None, str | None]:
    """QR for full database view — encodes mobile-friendly URL."""
    return generate_qr_png(database_qr_url())
