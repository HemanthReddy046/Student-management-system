"""Simple session-based authentication for Streamlit."""

import streamlit as st

DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin123"


def is_logged_in() -> bool:
    return st.session_state.get("authenticated", False)


def login(username: str, password: str) -> bool:
    if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
        st.session_state.authenticated = True
        st.session_state.username = username
        return True
    return False


def logout() -> None:
    st.session_state.authenticated = False
    st.session_state.pop("username", None)


def require_login() -> bool:
    if not is_logged_in():
        st.warning("Please log in to access this page.")
        return False
    return True
