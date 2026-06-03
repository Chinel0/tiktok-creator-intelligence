"""
upload.py  —  Page 1: Upload Data
Two modes:
  1. Connect TikTok  — scrapes the user's account live, then runs the pipeline
  2. Upload CSV      — original file upload flow (kept for demo / fallback)
"""

import os
import sys
import pandas as pd
import streamlit as st
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from nlp.preprocessor import preprocess
from nlp.sentiment    import analyze_sentiment
from nlp.keywords     import extract_keywords
from app.scraper_runner import run_scraper, session_saved, latest_comments_csv, MODES

ROOT        = Path(__file__).parent.parent.parent
SAMPLE_PATH = ROOT / "data" / "raw" / "sample_comments.csv"
REQUIRED_COLS = ['Comment Text', 'Comment Language', 'Comment Like Count', 'Author Nickname']


# ── Pipeline helper ────────────────────────────────────────────────────────────

def run_pipeline(df: pd.DataFrame):
    """Run the full NLP pipeline and store results in session state."""
    with st.spinner("Running NLP analysis..."):
        df_clean             = preprocess(df)
        df_analyzed, summary = analyze_sentiment(df_clean)
        keywords, clusters   = extract_keywords(df_analyzed)

    st.session_state['df_raw']      = df
    st.session_state['df_analyzed'] = df_analyzed
    st.session_state['summary']     = summary
    st.session_state['keywords']    = keywords
    st.session_state['clusters']    = clusters


def _load_scraped_csv(csv_path: str) -> pd.DataFrame:
    """
    Load a scraped comments CSV and rename columns to match what the
    preprocessor expects (Comment Text, Comment Language, etc.)
    """
    df = pd.read_csv(csv_path, encoding="utf-8-sig")

    # Merge video_type from videos_merged.csv if available
    videos_path = ROOT / "data" / "videos_merged.csv"
    if videos_path.exists():
        videos = pd.read_csv(videos_path, encoding="utf-8-sig")[["video_id", "video_type"]]
        df = df.merge(videos, on="video_id", how="left")

    # Filter out engagement spam before analysis
    if "video_type" in df.columns:
        df = df[df["video_type"] != "Engagement / Growth"]

    # Rename to match the preprocessor's expected column names
    df = df.rename(columns={
        "comment_text":     "Comment Text",
        "language":         "Comment Language",
        "like_count":       "Comment Like Count",
        "author_username":  "Author Nickname",
    })

    # Include translated comments — mark them as English so they aren't dropped
    if "original_text" in df.columns:
        df.loc[df["original_text"].notna(), "Comment Language"] = "en"

    return df


# ── Page ───────────────────────────────────────────────────────────────────────

def show_upload_page():
    st.title("Get Your TikTok Data")

    tab_scrape, tab_upload = st.tabs(["Connect TikTok", "Upload CSV"])

    # ── TAB 1: Connect TikTok ──────────────────────────────────────────────────
    with tab_scrape:
        _show_connect_tab()

    # ── TAB 2: Upload CSV ──────────────────────────────────────────────────────
    with tab_upload:
        _show_upload_tab()


# ── Connect TikTok tab ─────────────────────────────────────────────────────────

def _show_connect_tab():
    st.markdown("### Connect Your TikTok Account")
    st.markdown(
        "The app will open a browser, collect your videos and comments, "
        "and run the full analysis automatically. No manual steps needed."
    )

    # Login status indicator
    if session_saved():
        st.success("TikTok session found — no login needed. Ready to scrape.")
    else:
        st.warning(
            "No saved session found. When you click Start, a browser will open. "
            "Log in to TikTok, then the scraping will begin automatically."
        )

    # Mode selector
    mode_label = st.radio(
        "How much data to collect?",
        list(MODES.keys()),
        help="More videos = more accurate analysis, but takes longer.",
    )
    limit = MODES[mode_label]

    st.markdown("---")

    # Already have scraped data?
    existing_csv = latest_comments_csv()
    if existing_csv:
        st.info(f"Scraped data found: `{existing_csv.name}`")
        if st.button("Load & Analyse Existing Data", type="primary", use_container_width=True):
            df = _load_scraped_csv(str(existing_csv))
            run_pipeline(df)
            st.success("Analysis complete. Go to Dashboard.")
        st.markdown("Or scrape fresh data below.")

    # Start button
    if st.button("Start Scraping", type="primary", use_container_width=True):
        _run_scraper_with_progress(limit)


def _run_scraper_with_progress(limit):
    """Launch scraper subprocess and show live progress in the UI."""
    st.markdown("---")
    st.markdown("**Scraping in progress — do not close this tab.**")

    if not session_saved():
        st.info(
            "A browser window has opened. Log in to TikTok, then come back here. "
            "Progress will appear below once scraping starts."
        )

    progress_bar  = st.progress(0.0)
    status_box    = st.empty()
    log_container = st.container()
    log_lines     = []

    for value, message in run_scraper(limit):
        if value == "done":
            # Scraping finished
            progress_bar.progress(1.0)
            csv_path = message
            if csv_path:
                status_box.success("Scraping complete. Running analysis...")
                df = _load_scraped_csv(csv_path)
                run_pipeline(df)
                status_box.success(
                    "Analysis complete! Navigate to Dashboard to see your results."
                )
                st.balloons()
            else:
                status_box.error("Scraping finished but no CSV was found. Check the terminal for errors.")
            return

        # Update progress bar
        if isinstance(value, float):
            progress_bar.progress(min(value, 1.0))
            status_box.markdown(f"`{message}`")

        # Keep a rolling log of the last 8 lines
        log_lines.append(message)
        if len(log_lines) > 8:
            log_lines.pop(0)
        with log_container:
            st.code("\n".join(log_lines), language=None)


# ── Upload CSV tab ─────────────────────────────────────────────────────────────

def _show_upload_tab():
    st.markdown("### Upload a CSV or Excel File")
    st.markdown("Use this if you already have a comments export.")

    uploaded = st.file_uploader(
        "Drag and drop your file here, or click Browse",
        type=['csv', 'xlsx', 'xls'],
        help=f"Expected columns: {', '.join(REQUIRED_COLS)}",
    )

    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
        except Exception as e:
            st.error(f"Could not read the file: {e}")
            return

        missing = [c for c in REQUIRED_COLS if c not in df.columns]
        if missing:
            st.error(
                f"Missing required columns: **{', '.join(missing)}**\n\n"
                f"File must have: {', '.join(REQUIRED_COLS)}"
            )
            return

        st.success(f"File loaded — {len(df)} rows found.")
        _show_preview_and_stats(df)

        if st.button("Run Analysis", type="primary"):
            run_pipeline(df)
            st.success("Analysis complete! Navigate to Dashboard to see your results.")

    else:
        # Use real scraped data if available, otherwise fall back to demo
        real_csv = latest_comments_csv()
        if real_csv:
            st.info(f"Using your scraped data: `{real_csv.name}`")
            if st.session_state.get('df_analyzed') is None:
                df = _load_scraped_csv(str(real_csv))
                run_pipeline(df)
                st.caption("Your real TikTok data has been loaded automatically.")
            if st.button("Re-run Analysis"):
                df = _load_scraped_csv(str(real_csv))
                run_pipeline(df)
        else:
            st.info("No scraped data found. Showing **demo mode** with 50 sample comments.")
            df_demo = pd.read_csv(SAMPLE_PATH)
            _show_preview_and_stats(df_demo)
            if st.session_state.get('df_analyzed') is None:
                run_pipeline(df_demo)
                st.caption("Demo analysis loaded. Connect TikTok above to use real data.")


def _show_preview_and_stats(df: pd.DataFrame):
    st.markdown("#### Preview — first 5 rows")
    st.dataframe(df.head(), use_container_width=True)

    st.markdown("#### Basic Stats")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Comments", len(df))
    with col2:
        if 'Comment Language' in df.columns:
            st.metric("Languages Found", df['Comment Language'].dropna().nunique())
        else:
            st.metric("Languages Found", "—")
    with col3:
        if 'Comment Language' in df.columns:
            st.metric("English Comments", (df['Comment Language'].str.lower() == 'en').sum())
        else:
            st.metric("English Comments", "—")
