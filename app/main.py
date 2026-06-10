"""
main.py  —  TikTok Creator Intelligence
Mobile-first design with bottom navigation bar.
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

    /* TOP HEADER - Minimal */
    .top-header {
        background-color: white;
        padding: 12px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 16px;
    }

    .brand-name {
        font-size: 18px;
        font-weight: 700;
        color: #4361EE;
    }

    .user-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background-color: #4361EE;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 14px;
    }

    /* BOTTOM NAVIGATION BAR */
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: white;
        border-top: 1px solid #e2e8f0;
        padding: 8px 0;
        display: flex;
        justify-content: space-around;
        align-items: center;
        z-index: 100;
    }

    .nav-button {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
        padding: 8px 12px;
        border: none;
        background: none;
        cursor: pointer;
        font-size: 12px;
        color: #6b7280;
        transition: all 0.2s;
        flex: 1;
        text-align: center;
    }

    .nav-button.active {
        background-color: #4361EE;
        color: white;
        border-radius: 8px;
        font-weight: 600;
    }

    .nav-button:hover:not(.active) {
        color: #4361EE;
    }

    .nav-icon {
        font-size: 20px;
    }

    /* Add padding to main content to avoid overlap with bottom nav */
    .main-content {
        padding-bottom: 80px;
        padding: 16px 20px 80px 20px;
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

    /* Hide overflow for bottom nav */
    .stApp > [data-testid="stVerticalBlock"] {
        overflow-y: auto;
        max-height: 100vh;
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


# ── AUTH PAGES ────────────────────────────────────────────────────────────────

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


# ── MAIN APP ──────────────────────────────────────────────────────────────────

if st.session_state.user:
    # TOP HEADER
    st.markdown(
        f"""
        <div class="top-header">
            <div class="brand-name">TikTok Intelligence</div>
            <div class="user-avatar">{st.session_state.user['username'][0].upper()}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # MAIN CONTENT
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

    # BOTTOM NAVIGATION BAR
    pages = [
        ("📤", "Upload Data"),
        ("📊", "Dashboard"),
        ("💡", "Insights"),
        ("⭐", "Recommendations"),
        ("👤", "User Profile"),
    ]

    st.markdown("---")

    # Create bottom nav buttons
    nav_cols = st.columns(len(pages))

    for idx, (icon, page_name) in enumerate(pages):
        with nav_cols[idx]:
            is_active = st.session_state.current_page == page_name
            btn_color = "#4361EE" if is_active else "white"
            text_color = "white" if is_active else "#4361EE"
            border_color = "#4361EE" if is_active else "#e2e8f0"

            if st.button(
                f"{icon}\n{page_name}",
                key=f"nav_{page_name}",
                use_container_width=True,
            ):
                st.session_state.current_page = page_name
                st.rerun()

    st.markdown("---")

    # Logout button
    if st.button("Logout", use_container_width=True, key="logout_btn"):
        st.session_state.user = None
        st.session_state.auth_page = 'login'
        st.session_state._analysis_saved = False
        st.rerun()

else:
    # Not logged in — show auth pages
    if st.session_state.get('auth_page', 'login') == 'register':
        _show_register()
    else:
        _show_login()
