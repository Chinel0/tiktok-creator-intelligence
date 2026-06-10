"""
upload.py  —  Page 1: Upload Data
CSV upload only - accepts both synthetic data format and scraped data format
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

# Also accept these alternate column names (from real scraper output)
ALTERNATE_COLS = {
    'comment_text': 'Comment Text',
    'language': 'Comment Language',
    'like_count': 'Comment Like Count',
    'author_username': 'Author Nickname',
}


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
    st.markdown(
        """<style>
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 1rem;
            color: #4361EE;
            font-weight: 600;
        }
        </style>""",
        unsafe_allow_html=True,
    )

    st.title("📊 Upload Your Comment Data")
    st.markdown("Upload a CSV file of TikTok comments to analyze your audience sentiment and keywords.")
    st.markdown("---")

    uploaded = st.file_uploader(
        "Drag and drop your CSV here, or click Browse",
        type=['csv', 'xlsx', 'xls'],
        help=f"Accepts both standard and scraped data formats",
    )

    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded, encoding='utf-8-sig') if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
        except Exception as e:
            st.error(f"Could not read the file: {e}")
            return

        # Try to rename columns if needed (accepts both formats)
        df = _normalize_columns(df)

        if df is None:
            return

        st.success(f"✅ File loaded — {len(df)} comments found")
        _show_preview_and_stats(df)

        if st.button("Run Analysis", type="primary", use_container_width=True):
            run_pipeline(df)
            st.success("✅ Analysis complete! Check the Dashboard for results.")

    else:
        st.markdown("---")
        with st.container():
            st.markdown(
                """
                <div style="background-color:#f0f4ff; padding:20px; border-radius:8px; border-left:4px solid #4361EE;">
                <h3 style="color:#4361EE; margin-top:0;">📌 How to get your data</h3>

                <p><strong>Option 1:</strong> Use your scraped TikTok data</p>
                <ul>
                <li>From the local scraper (comment_*.csv)</li>
                <li>The app automatically handles the format</li>
                </ul>

                <p><strong>Option 2:</strong> Use our test datasets</p>
                <ul>
                <li>Download a sample CSV (TERA, DENZEL, JUDITH, etc.)</li>
                <li>Test the analysis with realistic comments</li>
                </ul>

                <p style="margin-top:20px;"><strong>Data columns (accepts both formats):</strong></p>
                <ul>
                <li><code>Comment Text</code> or <code>comment_text</code> — the comment</li>
                <li><code>Comment Language</code> or <code>language</code> — language code (en, de, etc.)</li>
                <li><code>Comment Like Count</code> or <code>like_count</code> — engagement</li>
                <li><code>Author Nickname</code> or <code>author_username</code> — commenter handle</li>
                </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Accepts both column naming schemes:
    - Standard: Comment Text, Comment Language, Comment Like Count, Author Nickname
    - Scraped: comment_text, language, like_count, author_username

    Returns normalized dataframe or None if validation fails.
    """
    df = df.copy()

    # Check if already in standard format
    has_standard = all(c in df.columns for c in REQUIRED_COLS)

    # Check if in alternate format
    has_alternate = all(c in df.columns for c in ALTERNATE_COLS.keys())

    if has_standard:
        # Already correct
        return df
    elif has_alternate:
        # Rename alternate columns to standard
        df = df.rename(columns=ALTERNATE_COLS)
        return df
    else:
        # Missing required columns
        st.error(
            f"**Missing columns.** Your file must have one of these sets:\n\n"
            f"**Standard format:** {', '.join(REQUIRED_COLS)}\n\n"
            f"**OR Scraped format:** {', '.join(ALTERNATE_COLS.keys())}"
        )
        return None


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
