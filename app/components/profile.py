"""
profile.py  —  Page 5: User Profile
Shows a creator profile summary and, when the user is logged in,
a full analysis history with sentiment trend chart.
"""

import json
import os
import sys

import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from app.auth import save_analysis, get_user_analyses

C_PRIMARY  = '#6366f1'
C_POSITIVE = '#10b981'
C_NEGATIVE = '#ef4444'
C_NEUTRAL  = '#8b5cf6'
C_CARD_BG  = '#f8fafc'

# Niche detection keyword map
NICHE_MAP = {
    'Food & Lifestyle': ['food', 'recipe', 'cook', 'eat', 'meal', 'dish', 'kitchen',
                         'ingredient', 'bake', 'taste', 'delicious'],
    'Hair & Beauty':    ['hair', 'braid', 'style', 'beauty', 'makeup', 'skin',
                         'glow', 'nail', 'curl', 'shiny'],
    'Gardening':        ['garden', 'plant', 'grow', 'flower', 'soil', 'seed',
                         'water', 'herb', 'leaf'],
}


def _detect_niche(keywords: list) -> str:
    """Match top keywords against niche seed words and return the best match."""
    if not keywords:
        return 'Lifestyle & General'
    scores = {niche: 0 for niche in NICHE_MAP}
    for word, _ in keywords:
        for niche, seeds in NICHE_MAP.items():
            if any(seed in word for seed in seeds):
                scores[niche] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else 'Lifestyle & General'


def _health_score(positive_pct: float) -> str:
    if positive_pct > 60:
        return 'Great 🟢'
    elif positive_pct >= 40:
        return 'Good 🟡'
    else:
        return 'Needs Work 🔴'


def show_profile_page():
    df       = st.session_state.get('df_analyzed')
    summary  = st.session_state.get('summary')
    keywords = st.session_state.get('keywords', [])
    user     = st.session_state.get('user')

    if df is None or summary is None:
        st.warning("No data loaded yet. Please go to **Upload Data** first.")
        return

    niche        = _detect_niche(keywords)
    health       = _health_score(summary.get('positive', 0))

    # ── Save analysis automatically when logged in ─────────────────────────
    # Use a flag so we only save once per session load, not on every rerender
    if user and not st.session_state.get('_analysis_saved'):
        save_analysis(
            user_id      = user['user_id'],
            summary      = summary,
            keywords     = keywords,
            health_score = health,
            niche        = niche,
        )
        st.session_state['_analysis_saved'] = True

    st.title("Creator Profile")

    # ── Login banner for guests ────────────────────────────────────────────
    if not user:
        st.info(
            "Register to track your progress over time and compare analyses.",
            icon="📈",
        )

    # ── Profile card ──────────────────────────────────────────────────────
    creator_name = df['Author Nickname'].mode()[0] if 'Author Nickname' in df.columns else 'Unknown'
    top5_users   = (df['Author Nickname'].value_counts().head(5).reset_index()
                    .rename(columns={'index': 'User', 'Author Nickname': 'Comments'})
                    if 'Author Nickname' in df.columns else None)
    top_lang     = df['Comment Language'].mode()[0] if 'Comment Language' in df.columns else 'en'

    date_range = '—'
    if 'comment_date' in df.columns:
        dates = df['comment_date'].dropna()
        if len(dates):
            date_range = f"{dates.min()[:10]} → {dates.max()[:10]}"

    st.markdown("### Creator Summary")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(
            f"""<div style="background:white; border-radius:14px; padding:24px;
                box-shadow:0 2px 10px rgba(0,0,0,0.08); text-align:center;">
                <div style="width:72px; height:72px; border-radius:50%;
                     background:{C_PRIMARY}; color:white; font-size:1.8rem;
                     display:flex; align-items:center; justify-content:center;
                     margin:0 auto 12px;">
                    🎵
                </div>
                <h3 style="margin:0 0 4px; font-size:1.1rem;">@{creator_name}</h3>
                <span style="background:#ede9fe; color:{C_PRIMARY}; font-size:0.78rem;
                      padding:3px 12px; border-radius:99px; font-weight:600;">
                    {niche}
                </span>
                <p style="margin:16px 0 4px; font-size:0.9rem; color:#374151;">
                    Content Health
                </p>
                <h2 style="margin:0; font-size:1.5rem;">{health}</h2>
            </div>""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""<div style="background:white; border-radius:14px; padding:20px 24px;
                box-shadow:0 2px 10px rgba(0,0,0,0.08);">
                <p style="margin:0 0 10px;"><strong>Total comments analysed:</strong> {summary['total']}</p>
                <p style="margin:0 0 10px;"><strong>Most used language:</strong> {top_lang}</p>
                <p style="margin:0 0 10px;"><strong>Date range:</strong> {date_range}</p>
                <p style="margin:0 0 10px;"><strong>Account niche:</strong> {niche}</p>
            </div>""",
            unsafe_allow_html=True,
        )

    # ── Most active commenters ─────────────────────────────────────────────
    if top5_users is not None and len(top5_users):
        st.markdown("#### Top 5 Most Active Commenters")
        st.dataframe(top5_users, use_container_width=True, height=210)

    # ── Engagement summary ─────────────────────────────────────────────────
    st.markdown("### Engagement Summary")
    e1, e2, e3 = st.columns(3)

    like_col = 'Comment Like Count'
    total_likes   = int(df[like_col].sum())    if like_col in df.columns else 0
    avg_likes     = round(df[like_col].mean(), 1) if like_col in df.columns else 0
    reply_count   = int((df.get('reply_count', df.get('Comment Reply Count', 0)) > 0).sum()) \
                    if 'reply_count' in df.columns else 0
    reply_pct     = round(reply_count / max(len(df), 1) * 100, 1)

    with e1:
        st.metric("Total Comment Likes",    total_likes)
    with e2:
        st.metric("Avg Likes per Comment",  avg_likes)
    with e3:
        st.metric("% Comments with Replies", f"{reply_pct}%")

    # Most engaging comment
    if like_col in df.columns and len(df):
        best_row = df.loc[df[like_col].idxmax()]
        st.markdown("#### Most Engaging Comment")
        st.markdown(
            f"""<div style="background:#faf5ff; border:2px solid {C_PRIMARY};
                border-radius:12px; padding:16px 20px;">
                <p style="font-size:1rem; margin:0 0 8px;">
                    "{best_row['Comment Text']}"
                </p>
                <span style="color:{C_PRIMARY}; font-size:0.85rem;">
                    @{best_row.get('Author Nickname','—')} •
                    {int(best_row[like_col])} likes
                </span>
            </div>""",
            unsafe_allow_html=True,
        )

    # ── Analysis history (logged-in users only) ────────────────────────────
    if user:
        st.markdown("---")
        st.markdown("### Analysis History")
        history = get_user_analyses(user['user_id'])

        if len(history) < 2:
            st.caption("Run more analyses over time to see your progress trend here.")
        else:
            _show_history(history)


def _show_history(history: list):
    """Render a sentiment trend line chart and comparison text."""
    dates     = [h['analysis_date'][:10] for h in history]
    pos_vals  = [h['positive_pct']       for h in history]
    health_h  = [h['content_health_score'] for h in history]

    # Line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=pos_vals,
        mode='lines+markers',
        name='Positive %',
        line=dict(color='#10b981', width=2.5),
        marker=dict(size=7),
    ))
    fig.update_layout(
        title='Positive Sentiment Over Time',
        xaxis_title='Analysis Date',
        yaxis_title='Positive %',
        yaxis=dict(range=[0, 100]),
        margin=dict(t=40, b=20, l=20, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Content health history
    st.markdown("**Content health score history:**")
    health_str = '  →  '.join(health_h)
    st.markdown(f"`{health_str}`")

    # Improvement / drop message
    delta = round(pos_vals[-1] - pos_vals[-2], 1)
    if delta > 0:
        st.success(f"Your positive sentiment improved by **{delta}%** since the last analysis!")
    elif delta < 0:
        st.warning(f"Your positive sentiment dropped by **{abs(delta)}%** since the last analysis.")
    else:
        st.info("Your sentiment is stable since the last analysis.")

    # Keyword comparison
    last  = history[-1]
    prev  = history[-2]
    new_kws  = set(json.loads(last.get('top_keywords', '[]')))
    prev_kws = set(json.loads(prev.get('top_keywords', '[]')))
    appeared = new_kws - prev_kws

    if appeared:
        st.markdown(f"**New keywords this analysis:** {', '.join(appeared)}")
