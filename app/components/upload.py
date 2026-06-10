"""
upload.py  —  Page 1: Upload Data
Two-file upload flow:
  - Comments CSV (required)  — what your audience says
  - Videos CSV   (optional)  — unlocks niche-level performance insights
Accepts both the synthetic format and the real scraper format.
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

ROOT          = Path(__file__).parent.parent.parent
REQUIRED_COLS = ['Comment Text', 'Comment Language', 'Comment Like Count', 'Author Nickname']

# Also accept these alternate column names (from real scraper output)
ALTERNATE_COLS = {
    'comment_text': 'Comment Text',
    'language': 'Comment Language',
    'like_count': 'Comment Like Count',
    'author_username': 'Author Nickname',
}

# Minimum columns a videos CSV must have to be useful
VIDEO_MIN_COLS = ['video_id']


# ── Pure helpers (no streamlit — importable by test_harness.py) ───────────────

def normalize_comment_columns(df: pd.DataFrame) -> pd.DataFrame | None:
    """
    Accepts both column naming schemes and returns a standardized dataframe,
    or None if neither format matches.
    """
    df = df.copy()
    if all(c in df.columns for c in REQUIRED_COLS):
        return df
    if all(c in df.columns for c in ALTERNATE_COLS):
        return df.rename(columns=ALTERNATE_COLS)
    return None


def _vid_str(series: pd.Series) -> pd.Series:
    """Video IDs as clean strings (strips float '.0' artifacts)."""
    return series.astype(str).str.replace(r'\.0$', '', regex=True)


def merge_video_metadata(comments_df: pd.DataFrame, videos_df: pd.DataFrame) -> tuple:
    """
    Join video metadata onto comments via video_id.
    - Brings video_type into the comments (videos file is authoritative).
    Returns (merged_comments_df, match_count).
    """
    c = comments_df.copy()
    v = videos_df.copy()

    if 'video_id' not in c.columns or 'video_id' not in v.columns:
        return c, 0

    c['video_id'] = _vid_str(c['video_id'])
    v['video_id'] = _vid_str(v['video_id'])

    match_count = c['video_id'].isin(set(v['video_id'])).sum()

    if 'video_type' in v.columns:
        type_map = v.drop_duplicates('video_id').set_index('video_id')['video_type']
        mapped = c['video_id'].map(type_map)
        if 'video_type' in c.columns:
            c['video_type'] = mapped.fillna(c['video_type'])
        else:
            c['video_type'] = mapped

    return c, int(match_count)


# ── Pipeline ───────────────────────────────────────────────────────────────────

def run_pipeline(df: pd.DataFrame, videos_df: pd.DataFrame | None = None):
    """Run the full NLP pipeline and store results in session state."""
    with st.spinner("Running NLP analysis..."):
        if videos_df is not None:
            df, _ = merge_video_metadata(df, videos_df)

        df_clean             = preprocess(df)
        df_analyzed, summary = analyze_sentiment(df_clean)
        keywords, clusters   = extract_keywords(df_analyzed)

    st.session_state['df_raw']      = df
    st.session_state['df_videos']   = videos_df
    st.session_state['df_analyzed'] = df_analyzed
    st.session_state['summary']     = summary
    st.session_state['keywords']    = keywords
    st.session_state['clusters']    = clusters


# ── File reading helper ────────────────────────────────────────────────────────

def _read_upload(uploaded):
    """Read an uploaded CSV/Excel file into a dataframe."""
    if uploaded.name.lower().endswith('.csv'):
        return pd.read_csv(uploaded, encoding='utf-8-sig')
    return pd.read_excel(uploaded)


# ── Page ───────────────────────────────────────────────────────────────────────

def show_upload_page():
    st.title("Analyze Your Comments")
    st.markdown("3 simple steps to get insights about your audience")
    st.markdown("---")

    # STEP 1: Comments CSV (required)
    st.markdown("### 1️⃣ Upload Your Comments CSV")
    uploaded = st.file_uploader(
        "Drag and drop your comments CSV here, or click Browse",
        type=['csv', 'xlsx', 'xls'],
        key="comments_upload",
    )

    df = None
    if uploaded is not None:
        try:
            df = _read_upload(uploaded)
        except Exception as e:
            st.error(f"Could not read the file: {e}")
            return

        df = normalize_comment_columns(df)
        if df is None:
            st.error(
                f"**Missing columns.** Your file must have one of these sets:\n\n"
                f"**Standard format:** {', '.join(REQUIRED_COLS)}\n\n"
                f"**OR Scraped format:** {', '.join(ALTERNATE_COLS.keys())}"
            )
            return

        st.success(f"✅ Comments loaded — {len(df)} comments found")
        _show_preview_and_stats(df)

    # STEP 2: Videos CSV (optional)
    videos_df = None
    if df is not None:
        st.markdown("---")
        st.markdown("### 2️⃣ Add Your Videos CSV *(optional — unlocks niche insights)*")
        st.caption("Tells the app which videos perform best so recommendations can "
                   "compare your niches (views, likes, comments per video type).")
        uploaded_videos = st.file_uploader(
            "Drag and drop your videos CSV here (skip if you don't have one)",
            type=['csv', 'xlsx', 'xls'],
            key="videos_upload",
        )

        if uploaded_videos is not None:
            try:
                videos_df = _read_upload(uploaded_videos)
            except Exception as e:
                st.error(f"Could not read the videos file: {e}")
                videos_df = None

            if videos_df is not None:
                missing = [c for c in VIDEO_MIN_COLS if c not in videos_df.columns]
                if missing:
                    st.error(f"Videos file is missing the **{missing[0]}** column — "
                             f"it can't be matched to your comments.")
                    videos_df = None
                else:
                    _, match_count = merge_video_metadata(df, videos_df)
                    st.success(f"✅ Videos loaded — {len(videos_df)} videos, "
                               f"{match_count} of your comments matched")
                    if match_count == 0:
                        st.warning("No comments matched these videos. "
                                   "Check that both files are from the same account.")

    # STEP 3: Run
    if df is not None:
        st.markdown("---")
        st.markdown("### 3️⃣ Analyze Your Data")
        if st.button("Run Analysis", type="primary", use_container_width=True):
            run_pipeline(df, videos_df)
            st.success("✅ Analysis complete! Check the Dashboard for results.")

    # No file yet → offer samples
    if df is None:
        st.markdown("---")
        st.markdown("### 2️⃣ Don't Have Data Yet?")
        st.markdown("Download sample files to try the app:")

        col1, col2 = st.columns(2)
        with col1:
            _sample_download(
                "data/comments_20260526_233400.csv",
                "Download Sample Comments",
                "sample_comments.csv",
            )
        with col2:
            _sample_download(
                "data/videos_merged.csv",
                "Download Sample Videos",
                "sample_videos.csv",
            )


def _sample_download(rel_path: str, label: str, download_name: str):
    """Render a download button for a bundled sample file."""
    sample_path = ROOT / rel_path
    if sample_path.exists():
        sample_df = pd.read_csv(sample_path, encoding='utf-8-sig')
        csv_data = sample_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label=label,
            data=csv_data,
            file_name=download_name,
            mime="text/csv",
            use_container_width=True,
        )
        st.caption(f"Real TikTok data • {len(sample_df)} rows")
    else:
        st.warning(f"Sample file not found: {rel_path}")


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
