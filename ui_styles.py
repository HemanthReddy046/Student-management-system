"""Shared CSS for login hero and dashboard UI."""

LOGIN_PAGE_CSS = """
<style>
    /* ---- Login page only (injected in render_login) ---- */
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse 80% 50% at 50% -10%, rgba(99, 102, 241, 0.18) 0%, transparent 55%),
            linear-gradient(160deg, #0a0f1a 0%, #111827 40%, #0f172a 100%);
        min-height: 100vh;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stSidebar"] { display: none; }
    footer, [data-testid="stToolbar"] { visibility: hidden; height: 0; }

    [data-testid="stMainBlockContainer"],
    section.main .block-container {
        max-width: 460px !important;
        width: 100% !important;
        margin: 0 auto !important;
        padding: 3rem 1.5rem 2.5rem !important;
    }

    section.main > div {
        min-height: calc(100vh - 4rem);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .login-hero-title {
        font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
        font-size: 1.95rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: #f8fafc;
        line-height: 1.3;
        margin: 0 0 0.5rem;
        text-align: center;
    }
    .login-hero-sub {
        font-size: 1rem;
        color: #94a3b8;
        text-align: center;
        margin: 0 0 2rem;
        line-height: 1.6;
        padding: 0 0.5rem;
    }

    .login-card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #f1f5f9;
        text-align: center;
        margin: 0 0 0.35rem;
    }
    .login-card-sub {
        font-size: 0.9rem;
        color: #94a3b8;
        text-align: center;
        margin: 0 0 1.5rem;
    }

    /* Login card */
    [data-testid="stMainBlockContainer"] [data-testid="stVerticalBlockBorderWrapper"] {
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 !important;
        background: rgba(30, 41, 59, 0.65) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 20px !important;
        box-shadow:
            0 0 0 1px rgba(255, 255, 255, 0.04) inset,
            0 8px 32px rgba(0, 0, 0, 0.35),
            0 24px 48px rgba(0, 0, 0, 0.2) !important;
        overflow: hidden;
    }

    [data-testid="stMainBlockContainer"] [data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: 2rem 2rem 1.75rem !important;
    }

    [data-testid="stMainBlockContainer"] div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
    }

    [data-testid="stMainBlockContainer"] .stTextInput {
        margin-bottom: 0.5rem;
    }

    [data-testid="stMainBlockContainer"] .stTextInput label,
    [data-testid="stMainBlockContainer"] .stTextInput p {
        color: #e2e8f0 !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        margin-bottom: 0.35rem !important;
    }

    [data-testid="stMainBlockContainer"] .stTextInput input {
        width: 100% !important;
        box-sizing: border-box !important;
        border-radius: 10px !important;
        border: 1px solid #475569 !important;
        background: #0f172a !important;
        color: #f8fafc !important;
        padding: 0.7rem 0.9rem !important;
        font-size: 0.95rem !important;
        min-height: 2.75rem !important;
        line-height: 1.4 !important;
    }

    [data-testid="stMainBlockContainer"] .stTextInput input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25) !important;
        outline: none !important;
    }

    [data-testid="stMainBlockContainer"] .stFormSubmitButton {
        margin-top: 1rem !important;
        width: 100% !important;
    }

    [data-testid="stMainBlockContainer"] .stFormSubmitButton > button {
        width: 100% !important;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        color: #fff !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        padding: 0.72rem 1.25rem !important;
        min-height: 2.85rem !important;
        letter-spacing: 0.01em;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }

    [data-testid="stMainBlockContainer"] .stFormSubmitButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 28px rgba(99, 102, 241, 0.4) !important;
    }

    @media (max-width: 520px) {
        [data-testid="stMainBlockContainer"],
        section.main .block-container {
            max-width: 100% !important;
            padding: 2rem 1rem 1.5rem !important;
        }
        [data-testid="stMainBlockContainer"] [data-testid="stVerticalBlockBorderWrapper"] > div {
            padding: 1.5rem 1.25rem 1.35rem !important;
        }
        .login-hero-title { font-size: 1.6rem; }
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
