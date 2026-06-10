"""
main.py  —  TikTok Creator Intelligence
Entry point for the Streamlit app.

Run with:
    streamlit run app/main.py

Navigation:
  Not logged in  →  Login / Register pages
  Logged in      →  Upload Data, User Profile, Dashboard, Insights, Recommendations
"""

import os
import sys

import streamlit as st

# ── Path setup ────────────────────────────────────────────────────────────────
# Add the project root (one level above app/) to sys.path so that all imports
# like `from nlp.preprocessor import ...` work correctly.
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
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Clean white background */
    .stApp { background-color: #f1f5f9; }

    /* Hide the default Streamlit header decoration */
    [data-testid="stDecoration"] { display: none; }

    /* TOP BLUE NAVIGATION BAR */
    .top-nav-bar {
        background-color: #4361EE;
        padding: 14px 20px;
        margin: -20px -20px 20px -20px;
        color: white;
        font-size: 16px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 10px;
        border-radius: 0;
    }

    .arrow-icon {
        font-size: 24px;
        animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid #e2e8f0;
    }

    /* Make radio buttons look like nav items */
    div[role="radiogroup"] label {
        padding: 8px 12px;
        border-radius: 8px;
        margin-bottom: 4px;
        cursor: pointer;
        font-weight: 500;
    }
    div[role="radiogroup"] label:hover {
        background: #ede9fe;
        color: #6366f1;
    }

    /* ── Brand blue to match Figma prototype ── */
    :root { --brand: #4361EE; --brand-dark: #3451D1; }

    /* ALL primary buttons — Streamlit 1.30+ uses data-testid */
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

    /* All buttons - including download */
    button {
        background-color: #4361EE !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
    }
    button:hover {
        background-color: #3451D1 !important;
    }

    /* Sidebar TikTok title colour */
    [data-testid="stSidebar"] h2 { color: #4361EE !important; }

    /* Remove default padding on metric labels */
    [data-testid="stMetricLabel"] p { font-weight: 600; }

    /* Clear visible borders on input fields */
    div[data-baseweb="input"],
    div[data-baseweb="textarea"] {
        border: 1.5px solid #d1d5db !important;
        border-radius: 8px !important;
        background-color: white !important;
    }
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="textarea"]:focus-within {
        border-color: #4361EE !important;
        box-shadow: 0 0 0 3px rgba(67,97,238,0.15) !important;
    }
    /* Remove the inner input's own border so only the wrapper shows */
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea {
        border: none !important;
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Top Navigation Bar ────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="top-nav-bar">
        <span class="arrow-icon">←</span>
        <span>Click the menu on the left to navigate</span>
    </div>
    """,
    unsafe_allow_html=True
)

# ── Database initialisation ───────────────────────────────────────────────────
init_db()

# ── Session state defaults ────────────────────────────────────────────────────
# These keys are used across all pages; set them once here so no page
# has to guard against KeyError.
_defaults = {
    'user':             None,    # dict of logged-in user, or None
    'auth_page':        'login', # which auth screen to show when logged out
    'current_page':     'Upload Data',
    'df_raw':           None,
    'df_analyzed':      None,
    'summary':          None,
    'keywords':         None,
    'clusters':         None,
    '_analysis_saved':  False,   # prevent duplicate DB writes per session
}
for key, default in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default



# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """<h2 style="color:#4361EE; margin-bottom:4px;">TikTok</h2>
           <h3 style="margin-top:0; color:#1f2937;">Intelligence</h3>""",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    if st.session_state.user:
        # ── Logged-in sidebar ──────────────────────────────────────────────
        uname = st.session_state.user['username']
        st.markdown(
            f"""<div style="background:#eef1fd; border-radius:8px; padding:10px 14px;
                margin-bottom:16px;">
                <span style="font-size:0.85rem; color:#6b7280;">Logged in as</span><br>
                <strong style="color:#4361EE;">@{uname}</strong>
            </div>""",
            unsafe_allow_html=True,
        )

        page = st.radio(
            "Navigate",
            ["Upload Data", "User Profile", "Dashboard", "Insights", "Recommendations"],
            key="nav_radio",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True):
            st.session_state.user            = None
            st.session_state.auth_page       = 'login'
            st.session_state._analysis_saved = False
            st.rerun()

    else:
        # Logged-out — no nav shown in sidebar; auth controlled by session state
        page = st.session_state.get('auth_page', 'login')


# ── Auth pages ────────────────────────────────────────────────────────────────
# Must be defined BEFORE the router calls them.

def _show_login():
    st.title("Welcome back")
    st.markdown("Log in to access your TikTok Creator Intelligence dashboard.")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit   = st.form_submit_button("Login", type="primary", use_container_width=True)

    if submit:
        if not username or not password:
            st.error("Please fill in both fields.")
        else:
            user = login_user(username, password)
            if user:
                st.session_state.user            = user
                st.session_state._analysis_saved = False
                st.rerun()
            else:
                st.error("Incorrect username or password.")

    col1, col2 = st.columns([2.5, 0.5])
    with col1:
        st.write("Don't have an account?")
    with col2:
        if st.button("Register", key="to_register", help="Sign up for an account"):
            st.session_state.auth_page = "register"
            st.rerun()


def _show_register():
    st.title("Create an account")
    st.markdown("Register to save your analyses and track progress over time.")

    with st.form("register_form"):
        username   = st.text_input("Username")
        tiktok_hdl = st.text_input("TikTok handle (e.g. @ichbinnelo)")
        password   = st.text_input("Password", type="password")
        confirm    = st.text_input("Confirm password", type="password")
        submit     = st.form_submit_button("Register", type="primary", use_container_width=True)

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

    col1, col2 = st.columns([2.5, 0.5])
    with col1:
        st.write("Already have an account?")
    with col2:
        if st.button("Login", key="to_login", help="Go back to login"):
            st.session_state.auth_page = "login"
            st.rerun()


# ── Page router ───────────────────────────────────────────────────────────────
if st.session_state.user:
    if page == "Upload Data":
        show_upload_page()
    elif page == "User Profile":
        show_profile_page()
    elif page == "Dashboard":
        show_dashboard_page()
    elif page == "Insights":
        show_insights_page()
    elif page == "Recommendations":
        show_recommendations_page()
else:
    if st.session_state.get('auth_page', 'login') == 'register':
        _show_register()
    else:
        _show_login()
