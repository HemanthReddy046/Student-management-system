"""Input validation for student records."""

import re
from typing import Any

from database import STUDENT_COLUMNS


def validate_student_data(data: dict[str, Any], *, is_update: bool = False) -> tuple[bool, str]:
    required = [
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
    for field in required:
        value = data.get(field)
        if value is None or str(value).strip() == "":
            return False, f"'{field.replace('_', ' ').title()}' cannot be empty."

    try:
        student_id = int(data["student_id"])
        if student_id <= 0:
            return False, "Student ID must be a positive number."
    except (TypeError, ValueError):
        return False, "Student ID must be numeric."

    name_pattern = re.compile(r"^[A-Za-z\s.'-]+$")
    for name_field in ("first_name", "last_name"):
        if not name_pattern.match(str(data[name_field]).strip()):
            return False, f"{name_field.replace('_', ' ').title()} must contain only letters."

    contact = str(data["contact"]).strip()
    if not contact.isdigit():
        return False, "Contact must contain digits only."
    if len(contact) < 10 or len(contact) > 15:
        return False, "Contact must be between 10 and 15 digits."

    pin = str(data["areapincode"]).strip()
    if not pin.isdigit() or len(pin) != 6:
        return False, "Area pincode must be a 6-digit number."

    mail = str(data["mail"]).strip()
    if "@" not in mail or "." not in mail.split("@")[-1]:
        return False, "Please enter a valid email address."

    gender = str(data["gender"]).strip().lower()
    if gender not in ("male", "female", "other"):
        return False, "Gender must be Male, Female, or Other."

    return True, ""


def row_to_dict(row) -> dict:
    return {col: row[col] for col in STUDENT_COLUMNS}
