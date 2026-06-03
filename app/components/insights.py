"""
insights.py  —  Page 3: Insights
Deeper analysis view showing:
  - Key findings with impact labels (High / Medium / Low)
  - Keyword clusters with percentage bars and keyword tags
"""

import streamlit as st
from nlp.keywords import CLUSTER_LABELS

C_PRIMARY  = '#4361EE'
C_POSITIVE = '#10b981'
C_NEGATIVE = '#ef4444'
C_NEUTRAL  = '#8b5cf6'
C_CARD_BG  = '#f8fafc'

# Impact badge colours
IMPACT_COLORS = {
    'High':   ('#fef2f2', '#ef4444'),
    'Medium': ('#fffbeb', '#f59e0b'),
    'Low':    ('#f0fdf4', '#10b981'),
}


def _badge(label: str) -> str:
    bg, fg = IMPACT_COLORS.get(label, ('#f3f4f6', '#6b7280'))
    return (f'<span style="background:{bg}; color:{fg}; font-size:0.75rem; '
            f'font-weight:600; padding:2px 10px; border-radius:99px;">{label}</span>')


def _keyword_tag(word: str) -> str:
    return (f'<span style="background:#ede9fe; color:{C_PRIMARY}; font-size:0.78rem; '
            f'padding:3px 10px; border-radius:99px; margin:2px; display:inline-block;">'
            f'{word}</span>')


def show_insights_page():
    df       = st.session_state.get('df_analyzed')
    summary  = st.session_state.get('summary')
    keywords = st.session_state.get('keywords')
    clusters = st.session_state.get('clusters')

    if df is None or summary is None:
        st.title("Insights")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """<div style="background:white; border-radius:14px; padding:40px;
                box-shadow:0 2px 10px rgba(0,0,0,0.08); text-align:center; max-width:500px; margin:0 auto;">
                <div style="font-size:3rem; margin-bottom:16px;">💡</div>
                <h3 style="color:#1f2937; margin-bottom:8px;">No insights yet</h3>
                <p style="color:#6b7280; margin-bottom:0;">
                    Go to <strong>Upload Data</strong> and click
                    <strong>Load &amp; Analyse Existing Data</strong> to unlock your insights.
                </p>
            </div>""",
            unsafe_allow_html=True,
        )
        return

    st.title("Insights")
    st.markdown("Key patterns found in your audience's comments.")

    # ── Key Findings ──────────────────────────────────────────────────────────
    st.markdown("### Key Findings")

    findings = _build_findings(summary, keywords, clusters)
    for finding in findings:
        bg, fg = IMPACT_COLORS.get(finding['impact'], ('#f3f4f6', '#6b7280'))
        st.markdown(
            f"""<div style="background:white; border-radius:12px; padding:16px 20px;
                margin-bottom:12px; box-shadow:0 2px 8px rgba(0,0,0,0.06);
                border-left:4px solid {fg};">
                <div style="display:flex; justify-content:space-between;
                     align-items:center; margin-bottom:6px;">
                    <strong style="font-size:0.95rem;">{finding['title']}</strong>
                    {_badge(finding['impact'])}
                </div>
                <p style="color:#6b7280; font-size:0.88rem; margin:0;">
                    {finding['description']}
                </p>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Keyword Clusters ──────────────────────────────────────────────────────
    st.markdown("### Keyword Clusters")
    st.markdown("Topics your audience is talking about, grouped by theme.")

    if not clusters:
        st.info("Not enough data for clustering.")
        return

    total_keywords = sum(len(v) for v in clusters.values())
    if total_keywords == 0:
        st.info("No keywords extracted from this dataset.")
        return

    for cluster_key, words in clusters.items():
        if not words:
            continue

        label   = CLUSTER_LABELS.get(cluster_key, cluster_key)
        pct     = round(len(words) / max(total_keywords, 1) * 100)
        top5    = words[:5]
        bar_clr = {
            'positive_reactions':   C_POSITIVE,
            'improvement_requests': C_NEGATIVE,
            'content_requests':     C_PRIMARY,
            'engagement':           C_NEUTRAL,
        }.get(cluster_key, C_PRIMARY)

        tags_html = ' '.join(_keyword_tag(w) for w in top5)

        st.markdown(
            f"""<div style="background:white; border-radius:12px; padding:16px 20px;
                margin-bottom:14px; box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                <div style="display:flex; justify-content:space-between;
                     margin-bottom:8px;">
                    <strong>{label}</strong>
                    <span style="color:#6b7280; font-size:0.85rem;">{pct}% of keywords</span>
                </div>
                <!-- progress bar -->
                <div style="background:#f3f4f6; border-radius:99px; height:8px; margin-bottom:12px;">
                    <div style="background:{bar_clr}; width:{pct}%; height:8px;
                         border-radius:99px;"></div>
                </div>
                <div>{tags_html}</div>
            </div>""",
            unsafe_allow_html=True,
        )


def _build_findings(summary: dict, keywords: list, clusters: dict) -> list:
    """Generate a list of finding dicts based on the analysis results."""
    findings = []
    pos = summary.get('positive', 0)
    neg = summary.get('negative', 0)

    # Sentiment-based findings
    if pos >= 60:
        findings.append({
            'title':       'Strong Positive Audience Sentiment',
            'description': f'{pos}% of comments express positive reactions — your content is resonating well.',
            'impact':      'High',
        })
    elif pos >= 40:
        findings.append({
            'title':       'Moderate Positive Sentiment',
            'description': f'{pos}% positive comments indicate a mixed but generally favourable reception.',
            'impact':      'Medium',
        })
    else:
        findings.append({
            'title':       'Low Positive Sentiment — Action Needed',
            'description': f'Only {pos}% positive comments. Review what your audience finds off-putting.',
            'impact':      'High',
        })

    if neg >= 20:
        findings.append({
            'title':       'Noticeable Negative Feedback',
            'description': f'{neg}% negative comments suggest areas your audience wants you to improve.',
            'impact':      'High',
        })
    elif neg >= 10:
        findings.append({
            'title':       'Some Negative Feedback Present',
            'description': f'{neg}% negative comments — worth reading to spot recurring complaints.',
            'impact':      'Medium',
        })

    # Keyword-based findings
    if clusters:
        requests = clusters.get('improvement_requests', [])
        if len(requests) >= 3:
            sample = ', '.join(requests[:3])
            findings.append({
                'title':       'Audience is Requesting Improvements',
                'description': f'Keywords like "{sample}" appear frequently — your audience wants specific changes.',
                'impact':      'Medium',
            })

        content_asks = clusters.get('content_requests', [])
        if content_asks:
            findings.append({
                'title':       'Content Requests Detected',
                'description': f'Terms like "{content_asks[0]}" suggest viewers want more specific content from you.',
                'impact':      'Low',
            })

    return findings
