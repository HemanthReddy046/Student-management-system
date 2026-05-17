"""
Smart Student Management & Analytics System
Streamlit web application — legacy Tkinter app preserved in ../legacy_version/
"""

import html
import pandas as pd
import streamlit as st

from analytics import (
    branch_bar_chart,
    branch_summary_table,
    export_csv,
    export_excel,
    export_pdf,
    gender_pie_chart,
    get_dashboard_stats,
    state_bar_chart,
    students_display_dataframe,
)
from auth import is_logged_in, login, logout, require_login
from crud import (
    add_student,
    delete_student,
    get_all_students,
    get_student_by_id,
    search_students,
    student_id_exists,
    update_student,
)
from database import database_changed_since, get_db_mtime, init_database
from form_state import add_widget_key, request_add_form_reset, request_update_form_reset, update_widget_key
from qr_utils import (
    all_students_to_text,
    database_qr_summary,
    database_qr_url,
    generate_database_qr,
    generate_student_qr,
)
from student_filters import ALL_BRANCHES_LABEL, branch_filter_options, filter_students
from student_pdf import generate_student_pdf, student_pdf_filename
from ui_styles import APP_CSS, LOGIN_PAGE_CSS, MOBILE_QR_CSS
from validation import validate_student_data

# Management sub-pages (replaces fixed tabs so Edit from a card can switch views).
MGMT_TABS = {
    "add": "➕ Add",
    "update": "✏️ Update",
    "delete": "🗑️ Delete",
    "view": "📋 View All",
}

st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(APP_CSS, unsafe_allow_html=True)

def init_session() -> None:
    if "db_ready" not in st.session_state:
        init_database()
        st.session_state.db_ready = True
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "qr_student_id" not in st.session_state:
        st.session_state.qr_student_id = None
    if "mgmt_tab_key" not in st.session_state:
        st.session_state.mgmt_tab_key = "view"
    if "confirm_delete_id" not in st.session_state:
        st.session_state.confirm_delete_id = None
    if "update_load_id" not in st.session_state:
        st.session_state.update_load_id = None
    if "_db_mtime_seen" not in st.session_state:
        st.session_state._db_mtime_seen = get_db_mtime()


def queue_notification(kind: str, message: str) -> None:
    """Show on next rerun without duplicate flashes."""
    st.session_state["_pending_notification"] = (kind, message)


def show_pending_notification() -> None:
    pending = st.session_state.pop("_pending_notification", None)
    if not pending:
        return
    kind, message = pending
    if kind == "success":
        st.success(message)
    elif kind == "warning":
        st.warning(message)
    elif kind == "error":
        st.error(message)
    else:
        st.info(message)


def sync_database_state() -> None:
    """Detect external DB edits (e.g. DB Browser) and refresh the UI."""
    current = get_db_mtime()
    last = st.session_state.get("_db_mtime_seen")
    st.session_state._db_mtime_seen = current
    if last is not None and database_changed_since(last):
        st.toast("Database updated — refreshing data.", icon="🔄")
        st.rerun()


def _query_param(name: str) -> str:
    raw = st.query_params.get(name, "")
    if isinstance(raw, list):
        return str(raw[0]).strip() if raw else ""
    return str(raw or "").strip()


def render_student_qr_mobile(student_id: int) -> None:
    """Public mobile page for a single student (from QR scan)."""
    st.markdown(MOBILE_QR_CSS, unsafe_allow_html=True)
    student = get_student_by_id(student_id)
    st.markdown(
        '<div class="mobile-qr-header">'
        "<h1>🎓 Student Record</h1>"
        "<p>Scanned from QR code</p></div>",
        unsafe_allow_html=True,
    )
    if not student:
        st.error("❌ Student record not found.")
        return

    fields = [
        ("Student ID", student["student_id"]),
        ("Name", f"{student['first_name']} {student['last_name']}"),
        ("Gender", student["gender"]),
        ("Email", student["mail"]),
        ("Contact", student["contact"]),
        ("State", student["state"]),
        ("Address", student["address"]),
        ("Pincode", student["areapincode"]),
    ]
    for label, value in fields:
        safe_label = html.escape(str(label))
        safe_value = html.escape(str(value))
        st.markdown(
            f'<div class="mobile-detail-card">'
            f'<div class="label">{safe_label}</div>'
            f'<div class="value">{safe_value}</div></div>',
            unsafe_allow_html=True,
        )

    st.divider()
    try:
        pdf_bytes = generate_student_pdf(student)
        st.download_button(
            label="📥 Download PDF",
            data=pdf_bytes,
            file_name=student_pdf_filename(student_id),
            mime="application/pdf",
            use_container_width=True,
            type="primary",
            on_click=lambda: st.toast("✅ PDF downloaded successfully", icon="✅"),
        )
    except Exception as exc:
        st.error(f"❌ Could not generate PDF: {exc}")


def render_database_qr_mobile() -> None:
    """Public mobile page for full database (from database QR scan)."""
    st.markdown(MOBILE_QR_CSS, unsafe_allow_html=True)
    students = get_all_students()
    st.markdown(
        '<div class="mobile-qr-header">'
        "<h1>📚 Student Database</h1>"
        f"<p>{len(students)} record(s)</p></div>",
        unsafe_allow_html=True,
    )

    if not students:
        st.info("No student records in the database.")
    else:
        for s in students:
            name = html.escape(f"{s['first_name']} {s['last_name']}")
            st.markdown(
                f'<div class="mobile-db-card">'
                f"<h3>👤 {name}</h3>"
                f"<p>🆔 ID: <b>{html.escape(str(s['student_id']))}</b></p>"
                f"<p>⚧ {html.escape(str(s['gender']))} · 💻 {html.escape(str(s['branch']))}</p>"
                f"<p>📧 {html.escape(str(s['mail']))}</p>"
                f"<p>📱 {html.escape(str(s['contact']))} · 🗺️ {html.escape(str(s['state']))}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.divider()
    st.markdown("##### 📥 Download Database")
    d1, d2, d3 = st.columns(3)
    with d1:
        st.download_button(
            "CSV",
            data=export_csv(),
            file_name="students.csv",
            mime="text/csv",
            use_container_width=True,
            on_click=lambda: st.toast("✅ Database exported successfully", icon="✅"),
        )
    with d2:
        st.download_button(
            "Excel",
            data=export_excel(),
            file_name="students.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            on_click=lambda: st.toast("✅ Database exported successfully", icon="✅"),
        )
    with d3:
        st.download_button(
            "PDF",
            data=export_pdf(),
            file_name="students.pdf",
            mime="application/pdf",
            use_container_width=True,
            on_click=lambda: st.toast("✅ Database exported successfully", icon="✅"),
        )


def try_render_qr_mobile_view() -> bool:
    """If URL has QR view params, render public mobile page (no login)."""
    view = _query_param("view").lower()
    if view == "student":
        sid_raw = _query_param("id")
        if not sid_raw.isdigit():
            st.markdown(MOBILE_QR_CSS, unsafe_allow_html=True)
            st.error("❌ Invalid student ID in QR link.")
            return True
        render_student_qr_mobile(int(sid_raw))
        return True
    if view == "database":
        render_database_qr_mobile()
        return True
    return False


def render_login() -> None:
    """Clean minimal login screen. Auth logic unchanged."""
    st.markdown(LOGIN_PAGE_CSS, unsafe_allow_html=True)

    left, right = st.columns([1.15, 1], gap="large")

    with left:
        st.markdown(
            '<p class="login-hero-title">🎓 Student Management System</p>'
            '<p class="login-hero-sub">Manage students, analytics, and exports in one place.</p>',
            unsafe_allow_html=True,
        )

    with right:
        with st.container(border=True):
            st.markdown(
                '<p class="login-card-title">🔐 Login Access</p>'
                '<p class="login-card-sub">Sign in to continue to your dashboard</p>',
                unsafe_allow_html=True,
            )
            with st.form("login_form", enter_to_submit=False):
                username = st.text_input("👤 Username", placeholder="Enter username")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter password")
                submitted = st.form_submit_button(
                    "🚀 Login to Dashboard",
                    use_container_width=True,
                    type="primary",
                )
                if submitted:
                    if login(username, password):
                        queue_notification("success", "✅ Login successful")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("### 🎓 Navigation")
        st.caption(f"👤 Logged in as **{st.session_state.get('username', 'admin')}**")
        page = st.radio(
            "Go to",
            ["Dashboard", "Student Management", "Search", "Analytics & Export"],
            format_func=lambda p: {
                "Dashboard": "📊 Dashboard",
                "Student Management": "👥 Student Management",
                "Search": "🔍 Search",
                "Analytics & Export": "📈 Analytics & Export",
            }[p],
            label_visibility="collapsed",
        )
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
    return page


def render_dashboard() -> None:
    st.markdown('<p class="main-header">📊 Dashboard</p>', unsafe_allow_html=True)
    st.caption("Overview of your student database")
    stats = get_dashboard_stats()

    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        (stats["total"], "👨‍🎓 Total Students"),
        (stats["male"], "👨 Male"),
        (stats["female"], "👩 Female"),
        (stats["branches"], "🏫 Branches"),
        (stats["states"], "🗺️ States"),
    ]
    for col, (value, label) in zip((c1, c2, c3, c4, c5), cards):
        with col:
            st.markdown(
                f'<div class="metric-card"><h2>{value}</h2><p>{label}</p></div>',
                unsafe_allow_html=True,
            )

    st.divider()
    st.subheader("📋 Student Records")
    df = students_display_dataframe()
    if df.empty:
        st.info("No student records yet. Add students from **👥 Student Management**.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)


def render_student_management() -> None:
    st.markdown('<p class="main-header">👥 Student Management</p>', unsafe_allow_html=True)
    st.caption("Add, update, delete, and view student records")

    tab_keys = list(MGMT_TABS.keys())
    tab_labels = list(MGMT_TABS.values())
    current = st.session_state.mgmt_tab_key
    if current not in tab_keys:
        current = "view"
    selected_label = st.radio(
        "Section",
        tab_labels,
        index=tab_keys.index(current),
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.mgmt_tab_key = tab_keys[tab_labels.index(selected_label)]

    section = st.session_state.mgmt_tab_key

    if section == "add":
        st.subheader("➕ Add New Student")
        with st.form("add_form", clear_on_submit=False, enter_to_submit=False):
            data = _render_add_form_fields()
            submitted = st.form_submit_button("💾 Save Student", use_container_width=True, type="primary")
            if submitted:
                _handle_add(data)

    elif section == "update":
        st.subheader("✏️ Update Student")
        with st.form("update_lookup_form", enter_to_submit=False):
            id_kwargs: dict = {"min_value": 1, "step": 1}
            if st.session_state.get("update_load_id"):
                id_kwargs["value"] = int(st.session_state.update_load_id)
            update_id = st.number_input("🔢 Enter Student ID to update", **id_kwargs)
            load_btn = st.form_submit_button("📂 Load Record", use_container_width=True)
        if load_btn:
            st.session_state.update_load_id = int(update_id)
        load_id = st.session_state.get("update_load_id")
        record = get_student_by_id(load_id) if load_id else None
        if record:
            with st.form("update_form", clear_on_submit=False, enter_to_submit=False):
                data = _render_update_form_fields(record, load_id)
                if st.form_submit_button("💾 Update Record", use_container_width=True, type="primary"):
                    _handle_update(load_id, data)
        elif load_id:
            st.warning("⚠️ No student found with that ID.")

    elif section == "delete":
        st.subheader("🗑️ Delete Student")
        with st.form("delete_form", enter_to_submit=False):
            del_id = st.number_input("🔢 Student ID to delete", min_value=1, step=1)
            if st.form_submit_button("🗑️ Delete Record", type="primary", use_container_width=True):
                if del_id:
                    rows = delete_student(int(del_id))
                    if rows:
                        queue_notification("warning", "⚠️ Student record deleted successfully")
                        st.rerun()
                    else:
                        st.warning("⚠️ Student not found.")
                else:
                    st.warning("⚠️ Enter a valid Student ID.")

    else:
        st.subheader("📋 View All Students")
        _render_student_cards()


def _render_add_form_fields() -> dict:
    """Add form fields using versioned keys so reset never touches live widget state."""
    genders = ["Male", "Female", "Other"]
    c1, c2 = st.columns(2)
    with c1:
        student_id = st.text_input("🔢 Student ID", key=add_widget_key("sid"))
        first_name = st.text_input("👤 First Name", key=add_widget_key("fn"))
        last_name = st.text_input("👤 Last Name", key=add_widget_key("ln"))
        gender = st.selectbox("⚧ Gender", genders, index=0, key=add_widget_key("gen"))
        course = st.text_input("📚 Course", key=add_widget_key("crs"))
        branch = st.text_input("🏫 Branch", key=add_widget_key("br"))
    with c2:
        mail = st.text_input("📧 Email", key=add_widget_key("mail"))
        contact = st.text_input("📱 Contact", key=add_widget_key("ct"))
        state = st.text_input("🗺️ State", key=add_widget_key("st"))
        address = st.text_area("🏠 Address", key=add_widget_key("addr"))
        areapincode = st.text_input("📮 Area Pincode", key=add_widget_key("pin"))
    return {
        "student_id": student_id,
        "first_name": first_name,
        "last_name": last_name,
        "gender": gender,
        "course": course,
        "branch": branch,
        "mail": mail,
        "contact": contact,
        "state": state,
        "address": address,
        "areapincode": areapincode,
    }


def _render_update_form_fields(record: dict, load_id: int) -> dict:
    """
    Update form with versioned keys. Initial values come from DB; on validation
    failure the same keys keep user edits. On success, version bumps → fresh load.
    """
    genders = ["Male", "Female", "Other"]
    g_default = str(record.get("gender", "Male")).title()
    g_index = genders.index(g_default) if g_default in genders else 0

    c1, c2 = st.columns(2)
    with c1:
        student_id = st.text_input(
            "🔢 Student ID",
            value=str(record.get("student_id", "")),
            key=update_widget_key("sid", load_id),
            disabled=True,
        )
        first_name = st.text_input(
            "👤 First Name",
            value=record.get("first_name", ""),
            key=update_widget_key("fn", load_id),
        )
        last_name = st.text_input(
            "👤 Last Name",
            value=record.get("last_name", ""),
            key=update_widget_key("ln", load_id),
        )
        gender = st.selectbox(
            "⚧ Gender",
            genders,
            index=g_index,
            key=update_widget_key("gen", load_id),
        )
        course = st.text_input(
            "📚 Course", value=record.get("course", ""), key=update_widget_key("crs", load_id)
        )
        branch = st.text_input(
            "🏫 Branch", value=record.get("branch", ""), key=update_widget_key("br", load_id)
        )
    with c2:
        mail = st.text_input(
            "📧 Email", value=record.get("mail", ""), key=update_widget_key("mail", load_id)
        )
        contact = st.text_input(
            "📱 Contact",
            value=str(record.get("contact", "")),
            key=update_widget_key("ct", load_id),
        )
        state = st.text_input(
            "🗺️ State", value=record.get("state", ""), key=update_widget_key("st", load_id)
        )
        address = st.text_area(
            "🏠 Address", value=record.get("address", ""), key=update_widget_key("addr", load_id)
        )
        areapincode = st.text_input(
            "📮 Area Pincode",
            value=str(record.get("areapincode", "")),
            key=update_widget_key("pin", load_id),
        )
    return {
        "student_id": student_id,
        "first_name": first_name,
        "last_name": last_name,
        "gender": gender,
        "course": course,
        "branch": branch,
        "mail": mail,
        "contact": contact,
        "state": state,
        "address": address,
        "areapincode": areapincode,
    }


def _handle_add(data: dict) -> None:
    ok, msg = validate_student_data(data)
    if not ok:
        st.warning(f"⚠️ {msg}")
        return
    sid = int(data["student_id"])
    if student_id_exists(sid):
        st.warning(f"⚠️ Student ID {sid} already exists.")
        return
    try:
        add_student(data)
        request_add_form_reset()
        queue_notification("success", "✅ Student data added successfully")
        st.rerun()
    except Exception as exc:
        st.error(f"❌ Could not add student: {exc}")


def _handle_update(original_id: int, data: dict) -> None:
    ok, msg = validate_student_data(data, is_update=True)
    if not ok:
        st.warning(f"⚠️ {msg}")
        return
    new_id = int(data["student_id"])
    if new_id != original_id and student_id_exists(new_id):
        st.warning(f"⚠️ Student ID {new_id} is already in use.")
        return
    try:
        rows = update_student(original_id, data)
        if rows:
            request_update_form_reset(original_id)
            if new_id != original_id:
                request_update_form_reset(new_id)
            st.session_state.update_load_id = new_id
            queue_notification("success", "✅ Student data updated successfully")
            st.rerun()
        else:
            st.warning("⚠️ Update failed — record not found.")
    except Exception as exc:
        st.error(f"❌ Could not update student: {exc}")


def _render_view_all_filters(all_students: list) -> tuple[str, str]:
    """
    Search bar + branch dropdown above the card grid.
    Widget values rerun the app on change — filtered list updates immediately.
    """
    with st.container(border=True):
        st.markdown("##### 🔎 Find Students")
        search_col, branch_col = st.columns([2.2, 1])
        with search_col:
            search_query = st.text_input(
                "🔍 Search Student...",
                placeholder="ID, name, email, or branch…",
                key="view_student_search",
                label_visibility="collapsed",
            )
        with branch_col:
            branch_options = branch_filter_options(all_students)
            branch_filter = st.selectbox(
                "🎯 Filter by Branch",
                branch_options,
                key="view_branch_filter",
            )
    return search_query or "", branch_filter or ALL_BRANCHES_LABEL


def _render_student_cards() -> None:
    """
    Compact unified student cards (View All).
    Flow: load all students → filter in memory → show counter → render only matches.
    Each card: summary → actions → inline QR → expandable details.
    """
    all_students = get_all_students()
    if not all_students:
        st.info("📭 No records in the database.")
        return

    search_query, branch_filter = _render_view_all_filters(all_students)

    # Filter BEFORE rendering cards (performance + no duplicate sections).
    filtered = filter_students(
        all_students,
        search_query=search_query,
        branch_filter=branch_filter,
    )
    total = len(all_students)
    shown = len(filtered)

    # Result counter: X of Y students.
    st.markdown(
        f'<p class="filter-counter">Showing <b>{shown}</b> of <b>{total}</b> students</p>',
        unsafe_allow_html=True,
    )

    if not filtered:
        st.markdown(
            '<div class="empty-results">'
            '<p class="empty-results-title">😕 No students found</p>'
            "<p>Try a different search term or branch filter.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        return

    # Two cards per row — only for filtered students.
    for i in range(0, len(filtered), 2):
        row_cols = st.columns(2, gap="medium")
        for col, student in zip(row_cols, filtered[i : i + 2]):
            with col:
                _render_single_student_card(student)


def _render_single_student_card(student: dict) -> None:
    """One student card — all actions and QR live inside this container."""
    sid = student["student_id"]
    active_qr_id = st.session_state.get("qr_student_id")
    confirm_id = st.session_state.get("confirm_delete_id")

    with st.container(border=True):
        # --- Card summary (always visible) ---
        st.markdown(
            f'<p class="student-card-title">👤 {student["first_name"]} {student["last_name"]}</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p class="student-card-meta">'
            f"🆔 ID: <b>{sid}</b> &nbsp;•&nbsp; "
            f"💻 Branch: <b>{student['branch']}</b> &nbsp;•&nbsp; "
            f"📘 Course: <b>{student['course']}</b>"
            f"</p>",
            unsafe_allow_html=True,
        )

        # --- Action buttons in one row ---
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            if st.button("🔳 View QR", key=f"qr_btn_{sid}", use_container_width=True):
                st.session_state.qr_student_id = None if active_qr_id == sid else sid
                if st.session_state.qr_student_id == sid:
                    queue_notification("success", "✅ QR code generated successfully")
                st.rerun()
        with b2:
            st.download_button(
                label="📄 PDF",
                data=generate_student_pdf(student),
                file_name=student_pdf_filename(sid),
                mime="application/pdf",
                key=f"pdf_btn_{sid}",
                use_container_width=True,
                help="Download PDF report",
                on_click=lambda: st.toast("✅ PDF downloaded successfully", icon="✅"),
            )
        with b3:
            if st.button("✏️ Edit", key=f"edit_btn_{sid}", use_container_width=True):
                st.session_state.update_load_id = sid
                st.session_state.mgmt_tab_key = "update"
                st.rerun()
        with b4:
            if st.button("🗑 Delete", key=f"del_btn_{sid}", use_container_width=True):
                st.session_state.confirm_delete_id = sid
                st.rerun()

        # --- Delete confirmation (inside same card) ---
        if confirm_id == sid:
            st.warning(f"Delete student **{student['first_name']} {student['last_name']}** (ID {sid})?")
            y, n = st.columns(2)
            if y.button("✅ Confirm", key=f"del_yes_{sid}", use_container_width=True):
                delete_student(int(sid))
                st.session_state.confirm_delete_id = None
                if st.session_state.get("qr_student_id") == sid:
                    st.session_state.qr_student_id = None
                queue_notification("warning", "⚠️ Student record deleted successfully")
                st.rerun()
            if n.button("Cancel", key=f"del_no_{sid}", use_container_width=True):
                st.session_state.confirm_delete_id = None
                st.rerun()

        # --- Inline QR: rendered inside this card, directly under buttons ---
        if active_qr_id == sid:
            png, qr_warn = generate_student_qr(student)
            if qr_warn:
                st.caption(f"⚠️ {qr_warn}")
            if png:
                st.image(png, width=200)
                st.caption("Scan with your phone camera to open the mobile student page.")
            else:
                st.caption("❌ Could not generate QR.")

        # --- Expandable extra fields (hidden by default) ---
        with st.expander("📂 View More Details"):
            st.markdown(
                f"**⚧ Gender:** {student['gender']}  \n"
                f"**📧 Email:** {student['mail']}  \n"
                f"**📱 Contact:** {student['contact']}  \n"
                f"**🌍 State:** {student['state']}  \n"
                f"**🏠 Address:** {student['address']}  \n"
                f"**📮 Pincode:** {student['areapincode']}"
            )


def render_search() -> None:
    st.markdown('<p class="main-header">🔍 Search Students</p>', unsafe_allow_html=True)

    with st.form("search_form", enter_to_submit=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            search_id = st.text_input("🔢 Search by ID (optional)")
        with c2:
            search_name = st.text_input("👤 Search by Name (optional)")
        with c3:
            search_branch = st.text_input("🏫 Search by Branch (optional)")
        if st.form_submit_button("🔍 Search", use_container_width=True, type="primary"):
            sid = int(search_id) if search_id.strip().isdigit() else None
            results = search_students(
                student_id=sid,
                name=search_name or None,
                branch=search_branch or None,
            )
            if results:
                df = pd.DataFrame(results)
                df.insert(0, "S.No", range(1, len(df) + 1))
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.caption(f"✅ Found {len(results)} record(s).")
            else:
                st.warning("⚠️ No matching records found.")


def render_analytics() -> None:
    st.markdown('<p class="main-header">📈 Analytics & Export</p>', unsafe_allow_html=True)
    st.caption("Charts, summaries, downloads, and QR export")

    st.subheader("📊 Visual Analytics")
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.markdown("##### ⚧ Gender Distribution")
        img = gender_pie_chart()
        if img:
            st.image(img, use_container_width=True)
        else:
            st.info("Add students to see this chart.")
    with r1c2:
        st.markdown("##### 🏫 Branch Distribution")
        img = branch_bar_chart()
        if img:
            st.image(img, use_container_width=True)
        else:
            st.info("Add students to see this chart.")

    st.markdown("##### 🗺️ State-wise Distribution")
    img = state_bar_chart()
    if img:
        st.image(img, use_container_width=True)
    else:
        st.info("Add students to see this chart.")

    summary = branch_summary_table()
    if not summary.empty:
        st.subheader("📋 Branch Summary")
        st.dataframe(summary, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("📥 Export Data")
    ec1, ec2, ec3 = st.columns(3)
    with ec1:
        st.download_button(
            label="📄 Download CSV",
            data=export_csv(),
            file_name="students.csv",
            mime="text/csv",
            use_container_width=True,
            on_click=lambda: st.toast("✅ Database exported successfully", icon="✅"),
        )
    with ec2:
        st.download_button(
            label="📊 Download Excel",
            data=export_excel(),
            file_name="students.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            on_click=lambda: st.toast("✅ Database exported successfully", icon="✅"),
        )
    with ec3:
        st.download_button(
            label="📕 Download PDF",
            data=export_pdf(),
            file_name="students.pdf",
            mime="application/pdf",
            use_container_width=True,
            on_click=lambda: st.toast("✅ Database exported successfully", icon="✅"),
        )

    st.divider()
    st.subheader("📱 View Via QR Code")
    st.markdown(
        '<p class="qr-caption">📱 Scan to open the full mobile database view</p>',
        unsafe_allow_html=True,
    )
    db_summary = database_qr_summary()
    png, qr_warn = generate_database_qr()
    c1, c2 = st.columns([1, 2])
    with c1:
        if qr_warn:
            st.warning(f"⚠️ {qr_warn}")
        if png:
            st.image(png, width=280)
        else:
            st.error("❌ Could not generate database QR. Use export buttons above.")
    with c2:
        st.caption(
            "Scanning opens a mobile-friendly page with all records and download options. "
            "Set `SMS_APP_BASE_URL` on Streamlit Cloud so QR links use your public URL."
        )
        st.code(database_qr_url(), language=None)
        with st.expander("Preview summary text"):
            st.text(db_summary)
        with st.expander("Full database text preview"):
            full_text = all_students_to_text()
            st.text(full_text[:3000] + ("..." if len(full_text) > 3000 else ""))


def main() -> None:
    init_session()
    sync_database_state()

    if try_render_qr_mobile_view():
        return

    show_pending_notification()

    if not is_logged_in():
        render_login()
        return

    raw_page = render_sidebar()
    if not require_login():
        return

    pages = {
        "Dashboard": render_dashboard,
        "Student Management": render_student_management,
        "Search": render_search,
        "Analytics & Export": render_analytics,
    }
    pages[raw_page]()


if __name__ == "__main__":
    main()
