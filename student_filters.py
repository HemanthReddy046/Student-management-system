"""
In-memory search and branch filters for the View All Students dashboard.

Filtering runs on the full student list AFTER one database fetch and BEFORE
any cards are rendered — so only matching cards are drawn (fast, no duplicate UI).
"""

from typing import Any

# Standard branch options shown in the dropdown (DB-only branches are appended).
STANDARD_BRANCHES = ("CSE", "ECE", "EEE", "IT", "ME", "Civil")
ALL_BRANCHES_LABEL = "All Branches"


def branch_filter_options(students: list[dict[str, Any]]) -> list[str]:
    """Build dropdown: All Branches + standard list + any extra branches from data."""
    options = [ALL_BRANCHES_LABEL, *STANDARD_BRANCHES]
    seen = {b.lower() for b in options}
    for student in students:
        branch = str(student.get("branch", "")).strip()
        if branch and branch.lower() not in seen:
            options.append(branch)
            seen.add(branch.lower())
    return options


def _matches_search(student: dict[str, Any], query: str) -> bool:
    """Case-insensitive match across ID, names, email, and branch."""
    q = query.lower()
    fields = (
        str(student.get("student_id", "")),
        str(student.get("first_name", "")),
        str(student.get("last_name", "")),
        str(student.get("mail", "")),
        str(student.get("branch", "")),
    )
    full_name = f"{student.get('first_name', '')} {student.get('last_name', '')}".lower()
    if q in full_name:
        return True
    return any(q in str(field).lower() for field in fields)


def _matches_branch(student: dict[str, Any], branch_filter: str) -> bool:
    """Branch filter — exact match (case-insensitive)."""
    if not branch_filter or branch_filter == ALL_BRANCHES_LABEL:
        return True
    student_branch = str(student.get("branch", "")).strip().lower()
    return student_branch == branch_filter.strip().lower()


def filter_students(
    students: list[dict[str, Any]],
    *,
    search_query: str = "",
    branch_filter: str = ALL_BRANCHES_LABEL,
) -> list[dict[str, Any]]:
    """
    Apply branch filter then global search (both are case-insensitive).

    Order: branch → search, so the result count reflects combined filters.
    """
    result = list(students)

    if branch_filter and branch_filter != ALL_BRANCHES_LABEL:
        result = [s for s in result if _matches_branch(s, branch_filter)]

    query = (search_query or "").strip()
    if query:
        result = [s for s in result if _matches_search(s, query)]

    return result
