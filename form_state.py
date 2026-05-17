"""
Safe Streamlit form reset helpers.

Why the StreamlitAPIException happens
-------------------------------------
Each widget with `key="add_sid"` stores its value in `st.session_state["add_sid"]`.
After that widget is drawn in a run, Streamlit owns that key for the rest of the run.
Calling `st.session_state["add_sid"] = ""` inside the submit handler (after the widget
already ran) triggers:

    StreamlitAPIException: st.session_state.add_sid cannot be modified after the widget
    with key add_sid is instantiated.

Why this solution works
-----------------------
We never overwrite widget keys after submit. On successful save we only bump a
version counter (`add_form_version`). Widget keys become `add_sid_0`, `add_sid_1`, …
The next run creates brand-new widgets with empty defaults — no conflict, no manual clears.
"""

import streamlit as st


def get_add_form_version() -> int:
    """Current add-form generation; increment via request_add_form_reset() after save."""
    return int(st.session_state.get("add_form_version", 0))


def add_widget_key(field: str) -> str:
    """Versioned key for an add-form widget (e.g. add_sid_2)."""
    return f"add_{field}_{get_add_form_version()}"


def request_add_form_reset() -> None:
    """
    Schedule add form to clear on the next run.
    Call only after a successful database insert — then st.rerun().
    """
    st.session_state.add_form_version = get_add_form_version() + 1


def get_update_form_version(load_id: int) -> int:
    """Per-record update form generation for the loaded student ID."""
    state_key = f"update_form_version_{load_id}"
    return int(st.session_state.get(state_key, 0))


def update_widget_key(field: str, load_id: int) -> str:
    """Versioned key for an update-form widget."""
    return f"upd_{field}_{load_id}_{get_update_form_version(load_id)}"


def request_update_form_reset(load_id: int) -> None:
    """
    Schedule update form widgets to rebuild from DB values on the next run.
    Call only after a successful database update — then st.rerun().
    """
    state_key = f"update_form_version_{load_id}"
    st.session_state[state_key] = get_update_form_version(load_id) + 1
