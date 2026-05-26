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

    /* Primary button colour */
    .stButton > button[kind="primary"] {
        background-color: #6366f1;
        border: none;
        color: white;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #4f46e5;
    }

    /* Remove default padding on metric labels */
    [data-testid="stMetricLabel"] p { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

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
        """<h2 style="color:#6366f1; margin-bottom:4px;">🎵 TikTok</h2>
           <h3 style="margin-top:0; color:#1f2937;">Creator Intelligence</h3>""",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    if st.session_state.user:
        # ── Logged-in sidebar ──────────────────────────────────────────────
        uname = st.session_state.user['username']
        st.markdown(
            f"""<div style="background:#ede9fe; border-radius:8px; padding:10px 14px;
                margin-bottom:16px;">
                <span style="font-size:0.85rem; color:#6b7280;">Logged in as</span><br>
                <strong style="color:#6366f1;">@{uname}</strong>
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
        # ── Logged-out sidebar ─────────────────────────────────────────────
        page = st.radio(
            "Account",
            ["Login", "Register"],
            key="nav_radio",
        )

    st.markdown("---")
    st.caption("NLP Course Project · Spring 2026")


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

    st.markdown("Don't have an account? Switch to **Register** in the sidebar.")


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
                st.success(msg + " Switch to Login in the sidebar.")
            else:
                st.error(msg)


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
    if page == "Login":
        _show_login()
    else:
        _show_register()
