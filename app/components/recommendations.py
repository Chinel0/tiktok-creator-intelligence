"""
recommendations.py  —  Page 4: Recommendations
Converts the NLP analysis into three actionable sections:
  1. What to Post More  — content your audience loves
  2. What to Improve    — areas with negative feedback
  3. Suggested Content Ideas — specific ideas with confidence scores
"""

import streamlit as st

C_PRIMARY  = '#4361EE'
C_POSITIVE = '#10b981'
C_NEGATIVE = '#ef4444'
C_CARD_BG  = '#f8fafc'


def _rec_card(title: str, reason: str, tip: str, border_color: str):
    """Render a single recommendation card."""
    st.markdown(
        f"""<div style="background:white; border-radius:12px; padding:18px 20px;
            margin-bottom:14px; box-shadow:0 2px 8px rgba(0,0,0,0.07);
            border-left:4px solid {border_color};">
            <strong style="font-size:0.95rem; color:#1f2937;">{title}</strong>
            <p style="color:#6b7280; font-size:0.86rem; margin:6px 0 4px 0;">
                <em>Why:</em> {reason}
            </p>
            <p style="color:#374151; font-size:0.88rem; margin:0;">
                <strong>Tip:</strong> {tip}
            </p>
        </div>""",
        unsafe_allow_html=True,
    )


def _idea_card(title: str, confidence: str, description: str):
    """Render a content idea card with a confidence badge."""
    conf_colors = {
        'High':   ('#dcfce7', '#16a34a'),
        'Medium': ('#fef9c3', '#ca8a04'),
        'Low':    ('#f3f4f6', '#6b7280'),
    }
    bg, fg = conf_colors.get(confidence, conf_colors['Low'])
    badge  = (f'<span style="background:{bg}; color:{fg}; font-size:0.72rem; '
              f'font-weight:600; padding:2px 9px; border-radius:99px;">'
              f'{confidence} confidence</span>')
    st.markdown(
        f"""<div style="background:white; border-radius:12px; padding:16px 20px;
            margin-bottom:12px; box-shadow:0 2px 8px rgba(0,0,0,0.07);">
            <div style="display:flex; justify-content:space-between;
                 align-items:center; margin-bottom:6px;">
                <strong style="font-size:0.93rem;">{title}</strong>
                {badge}
            </div>
            <p style="color:#6b7280; font-size:0.87rem; margin:0;">{description}</p>
        </div>""",
        unsafe_allow_html=True,
    )


def show_recommendations_page():
    df       = st.session_state.get('df_analyzed')
    summary  = st.session_state.get('summary')
    keywords = st.session_state.get('keywords')
    clusters = st.session_state.get('clusters')

    if df is None or summary is None:
        st.title("Recommendations")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """<div style="background:white; border-radius:14px; padding:40px;
                box-shadow:0 2px 10px rgba(0,0,0,0.08); text-align:center; max-width:500px; margin:0 auto;">
                <div style="font-size:3rem; margin-bottom:16px;">🎯</div>
                <h3 style="color:#1f2937; margin-bottom:8px;">No recommendations yet</h3>
                <p style="color:#6b7280; margin-bottom:0;">
                    Go to <strong>Upload Data</strong> and click
                    <strong>Load &amp; Analyse Existing Data</strong> to get your personalised recommendations.
                </p>
            </div>""",
            unsafe_allow_html=True,
        )
        return

    st.title("Recommendations")
    st.markdown("Actionable next steps based on what your audience is telling you.")

    keep, improve, ideas = _generate_recommendations(summary, keywords, clusters)

    # ── What to Post More ─────────────────────────────────────────────────────
    st.markdown("### What to Post More")
    if keep:
        for rec in keep:
            _rec_card(rec['title'], rec['reason'], rec['tip'], C_POSITIVE)
    else:
        st.info("No strong positive signals detected yet — upload more data for better results.")

    # ── What to Improve ───────────────────────────────────────────────────────
    st.markdown("### What to Improve")
    if improve:
        for rec in improve:
            _rec_card(rec['title'], rec['reason'], rec['tip'], C_NEGATIVE)
    else:
        st.success("No major improvement areas detected — your content looks solid!")

    # ── Suggested Content Ideas ───────────────────────────────────────────────
    st.markdown("### Suggested Content Ideas")
    for idea in ideas:
        _idea_card(idea['title'], idea['confidence'], idea['description'])


# ── Recommendation generator ──────────────────────────────────────────────────

def _generate_recommendations(summary: dict, keywords: list, clusters: dict) -> tuple:
    """
    Build three lists of recommendations from the analysis results.
    Returns (keep_list, improve_list, ideas_list).
    All recommendations are rule-based — no external API needed.
    """
    keep    = []
    improve = []
    ideas   = []

    pos = summary.get('positive', 0)
    neg = summary.get('negative', 0)

    pos_words  = clusters.get('positive_reactions',   []) if clusters else []
    imp_words  = clusters.get('improvement_requests', []) if clusters else []
    cont_words = clusters.get('content_requests',     []) if clusters else []
    top_kws    = [k[0] for k in keywords[:5]] if keywords else []

    # ── What to post more ──────────────────────────────────────────────────
    if pos >= 50:
        keep.append({
            'title':  'Keep Posting This Type of Content',
            'reason': f'{pos}% of your audience reacted positively — this is working.',
            'tip':    'Double down on the format and topics that generated these reactions.',
        })

    if pos_words:
        sample = ', '.join(pos_words[:3])
        keep.append({
            'title':  f'Lean Into "{pos_words[0].title()}" Content',
            'reason': f'Your audience frequently uses words like {sample}, signalling strong appreciation.',
            'tip':    f'Create more videos that feature {pos_words[0]}-related themes.',
        })

    if cont_words:
        keep.append({
            'title':  'Respond to Content Requests',
            'reason': f'Your viewers are asking for "{cont_words[0]}" type of content.',
            'tip':    'Fulfilling explicit requests builds loyalty and boosts engagement.',
        })

    # ── What to improve ────────────────────────────────────────────────────
    if neg >= 20:
        improve.append({
            'title':  'Address the Negative Feedback',
            'reason': f'{neg}% of comments are negative — this is higher than average.',
            'tip':    'Read through the negative comments and look for recurring themes to fix.',
        })

    if imp_words:
        sample = ', '.join(imp_words[:3])
        improve.append({
            'title':  'Act on Improvement Requests',
            'reason': f'Keywords like "{sample}" appear in your comments, suggesting specific changes are wanted.',
            'tip':    'Acknowledge these requests in a video or try incorporating the feedback.',
        })

    if summary.get('neutral', 0) >= 40:
        improve.append({
            'title':  'Convert Neutral Viewers to Fans',
            'reason': f'{summary["neutral"]}% of comments are neutral — these are people on the fence.',
            'tip':    'Add stronger calls to action and more personality to pull neutral viewers in.',
        })

    # ── Content ideas ──────────────────────────────────────────────────────
    if top_kws:
        ideas.append({
            'title':       f'Deep Dive: {top_kws[0].title()} Content',
            'confidence':  'High',
            'description': f'Your top keyword is "{top_kws[0]}" — create a dedicated video series around this topic.',
        })

    if cont_words:
        ideas.append({
            'title':       f'Tutorial Series on {cont_words[0].title()}',
            'confidence':  'High',
            'description': 'Your audience is asking for tutorials. A step-by-step series tends to perform well.',
        })

    ideas.append({
        'title':       'Q&A Video Using Real Comments',
        'confidence':  'Medium',
        'description': 'Use the questions your audience is already asking as the script for a Q&A video.',
    })

    if neg >= 15:
        ideas.append({
            'title':       'Response Video Addressing Common Concerns',
            'confidence':  'Medium',
            'description': 'Directly addressing criticism in a transparent video builds trust and often goes viral.',
        })

    ideas.append({
        'title':       'Behind-the-Scenes or Process Video',
        'confidence':  'Low',
        'description': 'Audiences are curious about how things are made. A "how I create my content" video can boost engagement.',
    })

    return keep, improve, ideas
