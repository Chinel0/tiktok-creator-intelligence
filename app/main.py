"""
main.py  —  TikTok Creator Intelligence
Entry point for the Streamlit app with top navigation bar.
"""

import os
import sys
import streamlit as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.auth                       import init_db, register_user, login_user
from app.components.upload          import show_upload_page
from app.components.dashboard       import show_dashboard_page
from app.components.insights        import show_insights_page
from app.components.recommendations import show_recommendations_page
from app.components.profile         import show_profile_page

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TikTok Creator Intelligence",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Brand colors */
    :root { --brand: #4361EE; --brand-dark: #3451D1; }

    /* Clean background */
    .stApp { background-color: #f8fafb; }
    [data-testid="stDecoration"] { display: none; }

    /* Hide default sidebar */
    [data-testid="stSidebar"] { display: none; }

    /* TOP NAVIGATION BAR */
    .nav-bar {
        background-color: #4361EE;
        padding: 16px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
        border-radius: 0;
    }

    .nav-brand {
        font-size: 20px;
        font-weight: 700;
        color: white;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .nav-brand-text {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }

    .nav-brand-main { font-size: 18px; }
    .nav-brand-sub { font-size: 12px; opacity: 0.9; }

    /* Navigation tabs (top) */
    .nav-tabs {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        align-items: center;
    }

    .nav-tab {
        padding: 8px 14px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        color: white;
        background-color: rgba(255, 255, 255, 0.2);
        border: none;
        transition: all 0.2s;
    }

    .nav-tab:hover {
        background-color: rgba(255, 255, 255, 0.3);
    }

    .nav-tab.active {
        background-color: white;
        color: #4361EE;
    }

    .nav-logout {
        padding: 8px 16px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        color: white;
        background-color: rgba(255, 255, 255, 0.2);
        border: none;
        cursor: pointer;
        transition: all 0.2s;
    }

    .nav-logout:hover {
        background-color: rgba(255, 255, 255, 0.3);
    }

    /* Primary buttons */
    [data-testid="baseButton-primary"],
    [data-testid="baseButton-primary"]:focus {
        background-color: #4361EE !important;
        border: none !important;
        color: white !important;
        border-radius: 8px !important;
    }
    [data-testid="baseButton-primary"]:hover {
        background-color: #3451D1 !important;
    }

    /* Metrics styling */
    [data-testid="stMetricLabel"] p { font-weight: 600; }

    /* Input fields */
    div[data-baseweb="input"],
    div[data-baseweb="textarea"] {
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 8px !important;
        background-color: white !important;
    }
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="textarea"]:focus-within {
        border-color: #4361EE !important;
        box-shadow: 0 0 0 3px rgba(67,97,238,0.15) !important;
    }
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea {
        border: none !important;
        background-color: transparent !important;
    }

    /* Content padding */
    .main-content {
        padding: 0 24px;
        max-width: 1400px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

# ── Database initialisation ───────────────────────────────────────────────────
init_db()

# ── Session state defaults ────────────────────────────────────────────────────
_defaults = {
    'user': None,
    'auth_page': 'login',
    'current_page': 'Upload Data',
    'df_raw': None,
    'df_analyzed': None,
    'summary': None,
    'keywords': None,
    'clusters': None,
    '_analysis_saved': False,
}
for key, default in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Handle query params for auth
_go = st.query_params.get("go", "")
if _go == "register":
    st.session_state.auth_page = "register"
    st.query_params.clear()
elif _go == "login":
    st.session_state.auth_page = "login"
    st.query_params.clear()


# ── AUTH PAGES (when not logged in) ───────────────────────────────────────────

def _show_login():
    st.title("Welcome Back")
    st.markdown("Log in to access your TikTok Creator Intelligence dashboard.")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", type="primary", use_container_width=True)

    if submit:
        if not username or not password:
            st.error("Please fill in both fields.")
        else:
            user = login_user(username, password)
            if user:
                st.session_state.user = user
                st.session_state._analysis_saved = False
                st.rerun()
            else:
                st.error("Incorrect username or password.")

    st.markdown(
        "Don't have an account? "
        '<a href="?go=register" target="_top" style="color:#4361EE; font-weight:600; text-decoration:none;">'
        "Register here</a>",
        unsafe_allow_html=True,
    )


def _show_register():
    st.title("Create an Account")
    st.markdown("Register to save your analyses and track progress over time.")

    with st.form("register_form"):
        username = st.text_input("Username")
        tiktok_hdl = st.text_input("TikTok handle (e.g. @ichbinnelo)")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm password", type="password")
        submit = st.form_submit_button("Register", type="primary", use_container_width=True)

    if submit:
        if not username or not password or not confirm:
            st.error("Please fill in all fields.")
        elif password != confirm:
            st.error("Passwords do not match.")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters.")
        else:
            ok, msg = register_user(username, password, tiktok_hdl)
            if ok:
                st.success(msg)
                st.session_state.auth_page = 'login'
                st.rerun()
            else:
                st.error(msg)

    st.markdown(
        "Already have an account? "
        '<a href="?go=login" target="_top" style="color:#4361EE; font-weight:600; text-decoration:none;">'
        "Login here</a>",
        unsafe_allow_html=True,
    )


# ── MAIN APP (when logged in) ─────────────────────────────────────────────────

if st.session_state.user:
    # Top navigation bar
    col_brand, col_nav, col_user = st.columns([2, 3, 1])

    with col_brand:
        st.markdown(
            '<div class="nav-brand"><div class="nav-brand-text"><div class="nav-brand-main">TikTok</div><div class="nav-brand-sub">Intelligence</div></div></div>',
            unsafe_allow_html=True
        )

    with col_nav:
        pages = ["Upload Data", "Dashboard", "Insights", "Recommendations", "User Profile"]

        # Create buttons for each page
        cols = st.columns(len(pages))
        for i, page_name in enumerate(pages):
            with cols[i]:
                if st.button(
                    page_name,
                    key=f"nav_{page_name}",
                    use_container_width=True,
                ):
                    st.session_state.current_page = page_name
                    st.rerun()

    with col_user:
        if st.button("Logout", use_container_width=True, key="logout_btn"):
            st.session_state.user = None
            st.session_state.auth_page = 'login'
            st.session_state._analysis_saved = False
            st.rerun()

    st.markdown("---")

    # Main content area
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # Route to appropriate page
    if st.session_state.current_page == "Upload Data":
        show_upload_page()
    elif st.session_state.current_page == "Dashboard":
        show_dashboard_page()
    elif st.session_state.current_page == "Insights":
        show_insights_page()
    elif st.session_state.current_page == "Recommendations":
        show_recommendations_page()
    elif st.session_state.current_page == "User Profile":
        show_profile_page()

    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Not logged in — show auth pages
    if st.session_state.get('auth_page', 'login') == 'register':
        _show_register()
    else:
        _show_login()
