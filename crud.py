"""CRUD operations with parameterized SQL queries."""

from typing import Any

from database import STUDENT_COLUMNS, get_connection, touch_database


def get_all_students() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            f"SELECT {', '.join(STUDENT_COLUMNS)} FROM students ORDER BY student_id"
        ).fetchall()
    return [dict(row) for row in rows]


def get_student_by_id(student_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            f"SELECT {', '.join(STUDENT_COLUMNS)} FROM students WHERE student_id = ?",
            (student_id,),
        ).fetchone()
    return dict(row) if row else None


def student_id_exists(student_id: int, exclude_id: int | None = None) -> bool:
    with get_connection() as conn:
        if exclude_id is not None:
            row = conn.execute(
                "SELECT 1 FROM students WHERE student_id = ? AND student_id != ?",
                (student_id, exclude_id),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT 1 FROM students WHERE student_id = ?",
                (student_id,),
            ).fetchone()
    return row is not None


def add_student(data: dict[str, Any]) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO students (
                student_id, first_name, last_name, gender, course,
                branch, mail, contact, state, address, areapincode
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(data["student_id"]),
                str(data["first_name"]).strip(),
                str(data["last_name"]).strip(),
                str(data["gender"]).strip().title(),
                str(data["course"]).strip(),
                str(data["branch"]).strip(),
                str(data["mail"]).strip(),
                str(data["contact"]).strip(),
                str(data["state"]).strip(),
                str(data["address"]).strip(),
                str(data["areapincode"]).strip(),
            ),
        )
        conn.commit()
    touch_database()


def update_student(student_id: int, data: dict[str, Any]) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE students SET
                student_id = ?,
                first_name = ?,
                last_name = ?,
                gender = ?,
                course = ?,
                branch = ?,
                mail = ?,
                contact = ?,
                state = ?,
                address = ?,
                areapincode = ?
            WHERE student_id = ?
            """,
            (
                int(data["student_id"]),
                str(data["first_name"]).strip(),
                str(data["last_name"]).strip(),
                str(data["gender"]).strip().title(),
                str(data["course"]).strip(),
                str(data["branch"]).strip(),
                str(data["mail"]).strip(),
                str(data["contact"]).strip(),
                str(data["state"]).strip(),
                str(data["address"]).strip(),
                str(data["areapincode"]).strip(),
                student_id,
            ),
        )
        conn.commit()
    touch_database()
    return cursor.rowcount


def delete_student(student_id: int) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM students WHERE student_id = ?",
            (student_id,),
        )
        conn.commit()
    touch_database()
    return cursor.rowcount


def search_students(
    *,
    student_id: int | None = None,
    name: str | None = None,
    branch: str | None = None,
) -> list[dict]:
    query = f"SELECT {', '.join(STUDENT_COLUMNS)} FROM students WHERE 1=1"
    params: list[Any] = []

    if student_id is not None:
        query += " AND student_id = ?"
        params.append(student_id)
    if name:
        query += " AND (first_name LIKE ? OR last_name LIKE ?)"
        pattern = f"%{name.strip()}%"
        params.extend([pattern, pattern])
    if branch:
        query += " AND branch LIKE ?"
        params.append(f"%{branch.strip()}%")

    query += " ORDER BY student_id"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]
