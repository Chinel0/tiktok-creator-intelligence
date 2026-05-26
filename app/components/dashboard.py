"""
dashboard.py  —  Page 2: Dashboard
Shows the main analysis overview:
  - 4 metric cards (total comments, % positive, % negative, % neutral)
  - Sentiment distribution pie chart
  - Top keywords bar chart
  - 3 example comments per sentiment category
  - Quick insights panel
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Colour constants ──────────────────────────────────────────────────────────
C_PRIMARY  = '#6366f1'
C_POSITIVE = '#10b981'
C_NEGATIVE = '#ef4444'
C_NEUTRAL  = '#8b5cf6'
C_CARD_BG  = '#f8fafc'


def _metric_card(title: str, value: str, color: str) -> str:
    """Return an HTML string for a single coloured metric card."""
    return f"""
    <div style="
        background: white;
        padding: 20px 16px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
        border-top: 4px solid {color};
    ">
        <p style="color:#6b7280; font-size:0.82rem; margin:0; font-weight:500;">
            {title}
        </p>
        <h2 style="color:#1f2937; font-size:2rem; margin:8px 0 0 0; font-weight:700;">
            {value}
        </h2>
    </div>
    """


def show_dashboard_page():
    df       = st.session_state.get('df_analyzed')
    summary  = st.session_state.get('summary')
    keywords = st.session_state.get('keywords')

    if df is None or summary is None:
        st.warning("No data loaded yet. Please go to **Upload Data** first.")
        return

    st.title("Dashboard")
    st.markdown("Your audience at a glance.")

    # ── 4 Metric cards ────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "Total Comments",  str(summary['total']),           C_PRIMARY),
        (c2, "Positive",        f"{summary['positive']}%",       C_POSITIVE),
        (c3, "Negative",        f"{summary['negative']}%",       C_NEGATIVE),
        (c4, "Neutral",         f"{summary['neutral']}%",        C_NEUTRAL),
    ]
    for col, title, value, color in cards:
        with col:
            st.markdown(_metric_card(title, value, color), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts row ────────────────────────────────────────────────────────────
    left, right = st.columns([1, 1])

    with left:
        st.markdown("#### Sentiment Distribution")
        pie = px.pie(
            names  = ['Positive', 'Negative', 'Neutral'],
            values = [summary['positive'], summary['negative'], summary['neutral']],
            color  = ['Positive', 'Negative', 'Neutral'],
            color_discrete_map={
                'Positive': C_POSITIVE,
                'Negative': C_NEGATIVE,
                'Neutral':  C_NEUTRAL,
            },
            hole=0.45,
        )
        pie.update_traces(textposition='inside', textinfo='percent+label')
        pie.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(pie, use_container_width=True)

    with right:
        st.markdown("#### Top Keywords")
        if keywords:
            kw_df = __import__('pandas').DataFrame(keywords[:12], columns=['Keyword', 'Score'])
            bar   = px.bar(
                kw_df,
                x='Score', y='Keyword',
                orientation='h',
                color_discrete_sequence=[C_PRIMARY],
            )
            bar.update_layout(
                yaxis=dict(autorange='reversed'),
                margin=dict(t=10, b=10, l=10, r=10),
                xaxis_title='', yaxis_title='',
            )
            st.plotly_chart(bar, use_container_width=True)
        else:
            st.info("Not enough data to extract keywords.")

    st.markdown("---")

    # ── Example comments + Quick insights ─────────────────────────────────────
    comments_col, insights_col = st.columns([2, 1])

    with comments_col:
        st.markdown("#### Example Comments")
        for sentiment, color, emoji in [
            ('positive', C_POSITIVE, '😊'),
            ('negative', C_NEGATIVE, '😞'),
            ('neutral',  C_NEUTRAL,  '😐'),
        ]:
            subset = df[df['sentiment'] == sentiment]
            if len(subset) == 0:
                continue
            st.markdown(f"**{emoji} {sentiment.capitalize()} comments**")
            sample = subset.nlargest(3, 'sentiment_score') if sentiment == 'positive' \
                else subset.nsmallest(3, 'sentiment_score') if sentiment == 'negative' \
                else subset.head(3)
            for _, row in sample.iterrows():
                st.markdown(
                    f"""<div style="background:{C_CARD_BG}; border-left:4px solid {color};
                        padding:10px 14px; border-radius:6px; margin-bottom:8px;
                        font-size:0.9rem;">
                        {row['Comment Text']}
                        <span style="color:#9ca3af; font-size:0.78rem;
                        display:block; margin-top:4px;">
                        @{row.get('Author Nickname','—')}
                        </span>
                    </div>""",
                    unsafe_allow_html=True,
                )
            st.markdown("<br>", unsafe_allow_html=True)

    with insights_col:
        st.markdown("#### Quick Insights")
        dominant = max(['positive', 'negative', 'neutral'],
                       key=lambda s: summary[s])
        insights = [
            f"**{summary['positive']}%** of comments are positive",
            f"**{summary['negative']}%** express concerns or criticism",
            f"**{summary['neutral']}%** are questions or neutral observations",
            f"Dominant sentiment: **{dominant}**",
        ]
        if keywords:
            top3 = ', '.join([k[0] for k in keywords[:3]])
            insights.append(f"Top topics: **{top3}**")

        for insight in insights:
            st.markdown(
                f"""<div style="background:{C_CARD_BG}; padding:10px 14px;
                    border-radius:8px; margin-bottom:10px; font-size:0.88rem;">
                    {insight}
                </div>""",
                unsafe_allow_html=True,
            )
