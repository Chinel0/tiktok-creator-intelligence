"""
upload.py  —  Page 1: Upload Data
Handles CSV/Excel file upload, shows a data preview and basic stats,
then runs the full NLP pipeline and stores results in session state.
Falls back to built-in sample data if no file is uploaded.
"""

import os
import sys
import pandas as pd
import streamlit as st

# Make sure the project root is on the path so nlp/ imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from nlp.preprocessor import preprocess
from nlp.sentiment    import analyze_sentiment
from nlp.keywords     import extract_keywords

SAMPLE_PATH    = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw', 'sample_comments.csv')
REQUIRED_COLS  = ['Comment Text', 'Comment Language', 'Comment Like Count', 'Author Nickname']


# ── Shared helper ──────────────────────────────────────────────────────────────

def run_pipeline(df: pd.DataFrame):
    """
    Run the full NLP pipeline on a dataframe and store all results in
    st.session_state so every other page can access them.
    """
    with st.spinner("Running NLP analysis..."):
        df_clean             = preprocess(df)
        df_analyzed, summary = analyze_sentiment(df_clean)
        keywords, clusters   = extract_keywords(df_analyzed)

    st.session_state['df_raw']      = df
    st.session_state['df_analyzed'] = df_analyzed
    st.session_state['summary']     = summary
    st.session_state['keywords']    = keywords
    st.session_state['clusters']    = clusters


# ── Page ───────────────────────────────────────────────────────────────────────

def show_upload_page():
    st.title("Upload Your TikTok Data")
    st.markdown("Upload a CSV or Excel file exported from your TikTok comments.")

    # ── File uploader ──────────────────────────────────────────────────────────
    uploaded = st.file_uploader(
        "Drag and drop your file here, or click Browse",
        type=['csv', 'xlsx', 'xls'],
        help=f"Expected columns: {', '.join(REQUIRED_COLS)}",
    )

    if uploaded is not None:
        # Load file
        try:
            if uploaded.name.endswith('.csv'):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded)
        except Exception as e:
            st.error(f"Could not read the file: {e}")
            return

        # Validate columns
        missing = [c for c in REQUIRED_COLS if c not in df.columns]
        if missing:
            st.error(
                f"The file is missing these required columns: **{', '.join(missing)}**\n\n"
                f"Please make sure your file has: {', '.join(REQUIRED_COLS)}"
            )
            return

        st.success(f"File loaded successfully — {len(df)} rows found.")
        _show_preview_and_stats(df)

        if st.button("Run Analysis", type="primary"):
            run_pipeline(df)
            st.success("Analysis complete! Navigate to Dashboard to see your results.")

    else:
        # ── Demo mode ──────────────────────────────────────────────────────────
        st.info(
            "No file uploaded yet. Showing **demo mode** with 50 sample comments "
            "about food, hair, and lifestyle content."
        )

        df_demo = pd.read_csv(SAMPLE_PATH)
        _show_preview_and_stats(df_demo)

        # Auto-run pipeline for demo data if not already done
        if st.session_state.get('df_analyzed') is None:
            run_pipeline(df_demo)
            st.caption("Demo analysis loaded automatically. Upload your own file above to replace it.")
        else:
            if st.button("Re-run Demo Analysis"):
                run_pipeline(df_demo)
                st.success("Demo analysis refreshed.")


def _show_preview_and_stats(df: pd.DataFrame):
    """Show a 5-row preview table and basic statistics about the dataset."""
    st.markdown("#### Preview — first 5 rows")
    st.dataframe(df.head(), use_container_width=True)

    st.markdown("#### Basic Stats")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Comments", len(df))

    with col2:
        if 'Comment Language' in df.columns:
            langs = df['Comment Language'].dropna().unique()
            st.metric("Languages Found", len(langs))
        else:
            st.metric("Languages Found", "—")

    with col3:
        if 'Comment Language' in df.columns:
            en_count = (df['Comment Language'].str.lower() == 'en').sum()
            st.metric("English Comments", en_count)
        else:
            st.metric("English Comments", "—")

    if 'Comment Language' in df.columns:
        lang_counts = df['Comment Language'].value_counts()
        st.markdown("**Language breakdown:**")
        st.dataframe(lang_counts.rename("Count").reset_index().rename(columns={'index': 'Language'}),
                     use_container_width=True, height=150)
