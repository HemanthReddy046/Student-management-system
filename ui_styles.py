"""Shared CSS for login hero and dashboard UI."""

LOGIN_PAGE_CSS = """
<style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(145deg, #0b1220 0%, #162032 42%, #1a2744 100%);
        min-height: 100vh;
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] { display: none; }

    section.main > div {
        padding: 1.5rem 1rem 2rem;
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .login-hero-title {
        font-size: clamp(2rem, 5vw, 3.25rem);
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #f8fafc;
        line-height: 1.15;
        margin: 0 0 0.75rem;
        text-align: center;
    }
    .login-hero-sub {
        font-size: 1.05rem;
        color: #94a3b8;
        text-align: center;
        margin: 0;
        line-height: 1.5;
        max-width: 28rem;
        margin-left: auto;
        margin-right: auto;
    }

    .login-card-title {
        font-size: 1.55rem;
        font-weight: 700;
        letter-spacing: -0.01em;
        color: #f8fafc;
        text-align: center;
        margin: 0 0 0.35rem;
    }
    .login-card-sub {
        font-size: 0.92rem;
        color: #94a3b8;
        text-align: center;
        margin: 0 0 1.35rem;
    }

    div[data-testid="stForm"] { border: none; padding: 0; }
    .stTextInput label, .stTextInput p {
        color: #cbd5e1 !important;
        font-weight: 500;
        font-size: 0.9rem;
    }
    .stTextInput input {
        border-radius: 10px !important;
        border: 1px solid #475569 !important;
        background: #0f172a !important;
        color: #f1f5f9 !important;
        padding: 0.65rem 0.85rem !important;
    }

    div[data-testid="column"] {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    div[data-testid="stVerticalBlock"] > div[data-testid="element-container"] > div[data-testid="stContainer"] {
        background: linear-gradient(160deg, rgba(30, 41, 59, 0.98) 0%, rgba(15, 23, 42, 0.98) 100%);
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 20px;
        padding: 2rem 1.75rem 1.85rem;
        box-shadow:
            0 4px 6px rgba(0, 0, 0, 0.12),
            0 24px 48px rgba(0, 0, 0, 0.35),
            inset 0 1px 0 rgba(255, 255, 255, 0.06);
        width: 100%;
        max-width: 400px;
        margin: 0 auto;
    }

    .stButton > button, .stFormSubmitButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.7rem 1.25rem !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 28px rgba(99, 102, 241, 0.35) !important;
    }

    @media (max-width: 768px) {
        section.main > div { padding-top: 2rem; }
        .login-hero-title { font-size: 1.85rem; }
    }
</style>
"""

MOBILE_QR_CSS = """
<style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #f0f4f8 0%, #e8eef5 100%);
    }
    section.main > div {
        max-width: 640px;
        margin: 0 auto;
        padding: 0.75rem 1rem 2rem;
    }
    .mobile-qr-header {
        text-align: center;
        padding: 1rem 0 0.5rem;
    }
    .mobile-qr-header h1 {
        font-size: 1.45rem;
        font-weight: 700;
        color: #1f4e79;
        margin: 0 0 0.25rem;
    }
    .mobile-qr-header p {
        color: #64748b;
        font-size: 0.9rem;
        margin: 0;
    }
    .mobile-detail-card {
        background: #fff;
        border-radius: 14px;
        padding: 1.1rem 1.15rem;
        margin: 0.75rem 0;
        box-shadow: 0 2px 12px rgba(31, 78, 121, 0.1);
        border: 1px solid #e2e8f0;
    }
    .mobile-detail-card .label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #64748b;
        margin-bottom: 0.15rem;
    }
    .mobile-detail-card .value {
        font-size: 1rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.65rem;
    }
    .mobile-db-card {
        background: #fff;
        border-radius: 12px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.65rem;
        box-shadow: 0 1px 8px rgba(31, 78, 121, 0.08);
        border-left: 4px solid #1f4e79;
    }
    .mobile-db-card h3 {
        margin: 0 0 0.35rem;
        font-size: 1rem;
        color: #1f4e79;
    }
    .mobile-db-card p {
        margin: 0.15rem 0;
        font-size: 0.88rem;
        color: #475569;
    }
</style>
"""

APP_CSS = """
<style>
    .main-header { font-size: 2rem; font-weight: 700; color: #1f4e79; margin-bottom: 0.25rem; }
    .sub-header { color: #5a6a7a; margin-bottom: 1rem; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem; border-radius: 12px; color: white; text-align: center;
        box-shadow: 0 4px 14px rgba(102, 126, 234, 0.35);
    }
    .metric-card h2 { margin: 0; font-size: 2rem; }
    .metric-card p { margin: 0.3rem 0 0; opacity: 0.92; }
    div[data-testid="stSidebar"] { background-color: #f0f4f8; }
    .qr-caption { text-align: center; font-weight: 600; color: #1f4e79; margin-top: 0.5rem; }
    .student-card-title { margin-bottom: 0.25rem; color: #1e293b; }
    .student-card-meta { color: #64748b; font-size: 0.92rem; margin-bottom: 0.75rem; }
    .filter-counter {
        color: #475569;
        font-size: 0.95rem;
        padding: 0.35rem 0 0.75rem;
        font-weight: 500;
    }
    .empty-results {
        text-align: center;
        padding: 2.5rem 1rem;
        color: #64748b;
        background: #f8fafc;
        border: 1px dashed #cbd5e1;
        border-radius: 12px;
        margin: 0.5rem 0 1rem;
    }
    .empty-results-title { font-size: 1.35rem; font-weight: 600; color: #334155; }
</style>
"""
