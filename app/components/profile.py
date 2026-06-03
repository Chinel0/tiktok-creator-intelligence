"""
profile.py  —  Page 5: User Profile
Shows the logged-in creator's profile, analysis summary, and history.
"""

import json
import os
import sys

import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from app.auth import save_analysis, get_user_analyses

C_PRIMARY  = '#4361EE'
C_POSITIVE = '#10b981'
C_NEGATIVE = '#ef4444'
C_NEUTRAL  = '#8b5cf6'
C_CARD_BG  = '#f8fafc'

NICHE_MAP = {
    'Food & Cooking':    ['food', 'recipe', 'cooking', 'baking', 'delicious', 'yummy',
                          'ingredient', 'meal', 'kitchen', 'cheesecake', 'pasta'],
    'Personal Finance':  ['debt', 'payoff', 'saving', 'budget', 'finance', 'afford', 'money'],
    'Student Life':      ['studying', 'university', 'student', 'lecture', 'exam', 'degree',
                          'studytok', 'revision'],
    'Hair & Beauty':     ['hair', 'braid', 'braiding', 'beauty', 'makeup', 'skincare', 'curl'],
    'Books & Reading':   ['book', 'reading', 'novel', 'booktok', 'author', 'chapter'],
    'Travel':            ['travel', 'travelling', 'berlin', 'europe', 'eurotok', 'abroad'],
}


def _detect_niche(keywords: list) -> str:
    """Detect niche from top keywords — requires at least 2 matches to avoid false positives."""
    if not keywords:
        return 'Lifestyle & General'
    scores = {niche: 0 for niche in NICHE_MAP}
    for word, _ in keywords:
        w = word.lower()
        for niche, seeds in NICHE_MAP.items():
            if any(w == seed or w.startswith(seed) for seed in seeds):
                scores[niche] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] >= 1 else 'Lifestyle & General'


def _health_score(positive_pct: float) -> tuple:
    if positive_pct > 60:
        return 'Great', '🟢'
    elif positive_pct >= 40:
        return 'Good', '🟡'
    else:
        return 'Needs Work', '🔴'


def _no_data_prompt():
    """Show a clear call to action when no analysis has been run yet."""
    st.title("Creator Profile")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """<div style="background:white; border-radius:14px; padding:40px;
            box-shadow:0 2px 10px rgba(0,0,0,0.08); text-align:center; max-width:500px; margin:0 auto;">
            <div style="font-size:3rem; margin-bottom:16px;">📊</div>
            <h3 style="color:#1f2937; margin-bottom:8px;">No analysis yet</h3>
            <p style="color:#6b7280; margin-bottom:0;">
                Go to <strong>Upload Data</strong> and click
                <strong>Load &amp; Analyse Existing Data</strong> to see your profile.
            </p>
        </div>""",
        unsafe_allow_html=True,
    )


def show_profile_page():
    df       = st.session_state.get('df_analyzed')
    summary  = st.session_state.get('summary')
    keywords = st.session_state.get('keywords', [])
    user     = st.session_state.get('user')

    if df is None or summary is None:
        _no_data_prompt()
        return

    niche          = _detect_niche(keywords)
    health_label, health_dot = _health_score(summary.get('positive', 0))

    # Save analysis once per session
    if user and not st.session_state.get('_analysis_saved'):
        save_analysis(
            user_id      = user['user_id'],
            summary      = summary,
            keywords     = keywords,
            health_score = f"{health_label} {health_dot}",
            niche        = niche,
        )
        st.session_state['_analysis_saved'] = True

    st.title("Creator Profile")

    # ── Profile card ───────────────────────────────────────────────────────────
    # Use the registered TikTok handle, fall back to username
    tiktok_handle = ''
    if user:
        raw = user.get('tiktok_handle', '') or user.get('username', '')
        tiktok_handle = raw.lstrip('@')

    top_lang   = df['Comment Language'].mode()[0] if 'Comment Language' in df.columns else 'en'
    date_range = '—'
    if 'comment_date' in df.columns:
        dates = df['comment_date'].dropna()
        if len(dates):
            try:
                date_range = f"{str(dates.min())[:10]}  to  {str(dates.max())[:10]}"
            except Exception:
                pass

    col1, col2 = st.columns([1, 2])

    with col1:
        initials = tiktok_handle[:2].upper() if tiktok_handle else '?'
        st.markdown(
            f"""<div style="background:white; border-radius:14px; padding:24px;
                box-shadow:0 2px 10px rgba(0,0,0,0.08); text-align:center;">
                <div style="width:72px; height:72px; border-radius:50%;
                     background:{C_PRIMARY}; color:white; font-size:1.4rem; font-weight:700;
                     display:flex; align-items:center; justify-content:center;
                     margin:0 auto 12px;">
                    {initials}
                </div>
                <h3 style="margin:0 0 8px; font-size:1.1rem; color:#1f2937;">
                    @{tiktok_handle if tiktok_handle else 'you'}
                </h3>
                <span style="background:#eef1fd; color:{C_PRIMARY}; font-size:0.78rem;
                      padding:3px 12px; border-radius:99px; font-weight:600;">
                    {niche}
                </span>
                <p style="margin:16px 0 4px; font-size:0.85rem; color:#6b7280;">
                    Content Health
                </p>
                <h2 style="margin:0; font-size:1.4rem; color:#1f2937;">
                    {health_label} {health_dot}
                </h2>
            </div>""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""<div style="background:white; border-radius:14px; padding:20px 24px;
                box-shadow:0 2px 10px rgba(0,0,0,0.08); height:100%;">
                <p style="margin:0 0 12px; font-size:0.95rem;">
                    <strong>Total comments analysed:</strong> {summary['total']}
                </p>
                <p style="margin:0 0 12px; font-size:0.95rem;">
                    <strong>Positive sentiment:</strong>
                    <span style="color:{C_POSITIVE}; font-weight:600;">
                        {summary['positive']}%
                    </span>
                </p>
                <p style="margin:0 0 12px; font-size:0.95rem;">
                    <strong>Most used language:</strong> {top_lang}
                </p>
                <p style="margin:0 0 12px; font-size:0.95rem;">
                    <strong>Date range:</strong> {date_range}
                </p>
                <p style="margin:0; font-size:0.95rem;">
                    <strong>Detected niche:</strong> {niche}
                </p>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top commenters ─────────────────────────────────────────────────────────
    if 'Author Nickname' in df.columns:
        top5 = (df['Author Nickname']
                .value_counts()
                .head(5)
                .reset_index()
                .rename(columns={'Author Nickname': 'Username', 'count': 'Comments'}))
        if len(top5):
            st.markdown("#### Top 5 Most Active Commenters")
            st.dataframe(top5, use_container_width=True, hide_index=True, height=210)

    # ── Engagement summary ─────────────────────────────────────────────────────
    st.markdown("### Engagement Summary")
    like_col    = 'Comment Like Count'
    total_likes = int(df[like_col].sum())      if like_col in df.columns else 0
    avg_likes   = round(df[like_col].mean(), 1) if like_col in df.columns else 0

    e1, e2 = st.columns(2)
    with e1:
        st.metric("Total Comment Likes", f"{total_likes:,}")
    with e2:
        st.metric("Avg Likes per Comment", avg_likes)

    # Most engaging comment
    if like_col in df.columns and total_likes > 0:
        best = df.loc[df[like_col].idxmax()]
        st.markdown("#### Most Engaging Comment")
        st.markdown(
            f"""<div style="background:#eef1fd; border:2px solid {C_PRIMARY};
                border-radius:12px; padding:16px 20px;">
                <p style="font-size:1rem; margin:0 0 8px; color:#1f2937;">
                    "{best['Comment Text']}"
                </p>
                <span style="color:{C_PRIMARY}; font-size:0.85rem; font-weight:600;">
                    @{best.get('Author Nickname', '—')} &nbsp;·&nbsp;
                    {int(best[like_col])} likes
                </span>
            </div>""",
            unsafe_allow_html=True,
        )

    # ── Analysis history ───────────────────────────────────────────────────────
    if user:
        st.markdown("---")
        st.markdown("### Analysis History")
        history = get_user_analyses(user['user_id'])
        if len(history) < 2:
            st.caption("Run more analyses over time to see your sentiment trend here.")
        else:
            _show_history(history)


def _show_history(history: list):
    dates    = [h['analysis_date'][:10] for h in history]
    pos_vals = [h['positive_pct']       for h in history]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=pos_vals,
        mode='lines+markers',
        name='Positive %',
        line=dict(color=C_POSITIVE, width=2.5),
        marker=dict(size=7),
    ))
    fig.update_layout(
        title='Positive Sentiment Over Time',
        xaxis_title='Date',
        yaxis_title='Positive %',
        yaxis=dict(range=[0, 100]),
        margin=dict(t=40, b=20, l=20, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    delta = round(pos_vals[-1] - pos_vals[-2], 1)
    if delta > 0:
        st.success(f"Positive sentiment improved by **{delta}%** since last analysis.")
    elif delta < 0:
        st.warning(f"Positive sentiment dropped by **{abs(delta)}%** since last analysis.")
    else:
        st.info("Sentiment is stable since last analysis.")
