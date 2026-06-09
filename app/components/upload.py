"""
upload.py  —  Page 1: Upload Data
CSV upload only - for testing with synthetic data or user's own TikTok exports
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

ROOT        = Path(__file__).parent.parent.parent
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


# ── Page ───────────────────────────────────────────────────────────────────────

def show_upload_page():
    st.title("Upload Your Comment Data")
    st.markdown("Upload a CSV file of TikTok comments to analyze your audience sentiment and keywords.")

    uploaded = st.file_uploader(
        "Drag and drop your CSV here, or click Browse",
        type=['csv', 'xlsx', 'xls'],
        help=f"Required columns: {', '.join(REQUIRED_COLS)}",
    )

    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded, encoding='utf-8-sig') if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
        except Exception as e:
            st.error(f"Could not read the file: {e}")
            return

        missing = [c for c in REQUIRED_COLS if c not in df.columns]
        if missing:
            st.error(
                f"**Missing columns:** {', '.join(missing)}\n\n"
                f"Your file must have: **{', '.join(REQUIRED_COLS)}**"
            )
            return

        st.success(f"✅ File loaded — {len(df)} comments found")
        _show_preview_and_stats(df)

        if st.button("Run Analysis", type="primary", use_container_width=True):
            run_pipeline(df)
            st.success("✅ Analysis complete! Check the Dashboard for results.")

    else:
        st.markdown("---")
        st.info(
            "### How to get your data\n\n"
            "**Option 1:** Export from TikTok (if available in your region)\n\n"
            "**Option 2:** Use our test dataset\n"
            "- Download one of our sample CSVs with realistic comments\n"
            "- Test how the analysis works\n\n"
            "**Data file should have columns:**\n"
            "- `Comment Text` — the actual comment\n"
            "- `Comment Language` — language code (en, de, etc.)\n"
            "- `Comment Like Count` — how many people liked it\n"
            "- `Author Nickname` — commenter's handle"
        )


def _show_preview_and_stats(df: pd.DataFrame):
    st.markdown("#### Preview — first 5 rows")
    st.dataframe(df.head(), use_container_width=True)

    st.markdown("#### Basic Stats")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Comments", len(df))
    with col2:
        if 'Comment Language' in df.columns:
            st.metric("Languages", df['Comment Language'].dropna().nunique())
        else:
            st.metric("Languages", "—")
    with col3:
        if 'Comment Language' in df.columns:
            eng_count = (df['Comment Language'].astype(str).str.lower() == 'en').sum()
            st.metric("English Comments", eng_count)
        else:
            st.metric("English Comments", "—")
