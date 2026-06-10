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
    df             = st.session_state.get('df_analyzed')
    summary        = st.session_state.get('summary')
    keywords       = st.session_state.get('keywords')
    clusters       = st.session_state.get('clusters')
    niche_analysis = st.session_state.get('niche_analysis')
    requests       = st.session_state.get('requests')

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

    keep, improve, ideas = _generate_recommendations(
        summary, keywords, clusters, niche_analysis, requests
    )

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
        st.success("No urgent problems found in this dataset — we only flag issues "
                   "the data can prove.")

    # ── Suggested Content Ideas ───────────────────────────────────────────────
    st.markdown("### Suggested Content Ideas")
    for idea in ideas:
        _idea_card(idea['title'], idea['confidence'], idea['description'])


# ── Recommendation generator ──────────────────────────────────────────────────
# Every card is built from measured data (niche analyzer + request
# extractor). No card is shown unless the data behind it exists, and
# every reason cites the actual numbers so creators can verify it.

# Reaction/mood words make terrible "Deep Dive" topics ("Deep Dive: Wow").
_REACTION_WORDS = {
    'wow', 'lol', 'omg', 'lmao', 'lmaooo', 'lmaoooo', 'yes', 'no', 'same',
    'fire', 'goals', 'ate', 'tho', 'fr', 'real', 'facts', 'love', 'cute',
    'cool', 'vibe', 'vibes', 'energy', 'day', 'way', 'list', 'looks',
    'look', 'peaceful', 'blessed', 'grateful', 'yum', 'obsessed', 'relatable',
    'beautiful', 'amazing', 'talented', 'stunning', 'therapy', 'lets',
    'good', 'best', 'perfect', 'gorgeous', 'iconic', 'queen', 'man',
    'unreal', 'crazy', 'hard', 'clean', 'smooth', 'everything', 'tho',
}

# A deep-dive topic must also be a noun-ish content word, so bigrams of
# leftover praise ("highlight unreal") don't slip through. Single words
# are preferred; bigrams must contain no reaction word at all.
_DEEP_DIVE_BLOCK = {
    'glows', 'declines', 'assignment', 'understood',
}


def _first_topical_keyword(keywords: list) -> str | None:
    """First keyword where every token is a real topic word, or None.
    Single words are tried before bigrams - 'berlin' beats 'berlin looks'."""
    blocked = _REACTION_WORDS | _DEEP_DIVE_BLOCK
    candidates = (keywords or [])[:10]
    for grams in (
        [g for g, _ in candidates if ' ' not in g],   # single words first
        [g for g, _ in candidates if ' ' in g],       # then bigrams
    ):
        for gram in grams:
            if all(tok not in blocked for tok in gram.split()):
                return gram
    return None

def _generate_recommendations(summary: dict, keywords: list, clusters: dict,
                              niche_analysis: dict | None = None,
                              requests: list | None = None) -> tuple:
    """
    Build three lists of recommendations from the analysis results.
    Returns (keep_list, improve_list, ideas_list).
    All recommendations are rule-based and evidence-cited — no external API.
    """
    keep    = []
    improve = []
    ideas   = []

    requests = requests or []
    neg      = summary.get('negative', 0)
    neutral  = summary.get('neutral', 0)

    na      = niche_analysis or {}
    niches  = na.get('niches', {})
    best    = na.get('best')
    weakest = na.get('weakest')
    ratio   = na.get('engagement_ratio')

    # ── What to post more ──────────────────────────────────────────────────

    # 1. The winner niche, with numbers a creator can check.
    if best and weakest and ratio and ratio >= 1.5:
        b, w = niches[best], niches[weakest]
        reason = (f'Your {best} videos average {b["comments_per_video"]} comments each — '
                  f'{ratio}x more than {weakest} ({w["comments_per_video"]}).')
        vr = na.get('views_ratio')
        if vr and b.get('avg_views') and w.get('avg_views'):
            views_str = f'{b["avg_views"]:,.0f} vs {w["avg_views"]:,.0f}'
            if vr >= 1.2:
                reason += f' They also pull {vr}x the views ({views_str} on average).'
            elif vr >= 0.85:
                reason += (f' Reach is similar ({views_str} views) — the gap is pure '
                           f'engagement.')
            else:
                reason += (f' And that is despite fewer views ({views_str}) — this '
                           f'audience earns its engagement.')

        best_reqs = [r for r in requests if r.get('top_video_type') == best and r['count'] > 1]
        if best_reqs:
            tip = (f'Make {best} your main lane. Next upload: answer '
                   f'"{best_reqs[0]["request"]}" — {best_reqs[0]["count"]} viewers '
                   f'already asked for it.')
        else:
            tip = f'Make {best} your main lane — aim for at least half of your next 10 uploads.'

        keep.append({'title': f'Double Down on {best}', 'reason': reason, 'tip': tip})

    # 2. Honest card when there is no clear winner.
    elif best and ratio and ratio < 1.5:
        b = niches[best]
        keep.append({
            'title':  'No Breakout Niche Yet — Your Audience Likes It All',
            'reason': (f'Your top niche ({best}, {b["comments_per_video"]} comments/video) '
                       f'performs about the same as the rest ({ratio}x difference).'),
            'tip':    ('Run a 4-week experiment: two weeks focused on one niche, two on '
                       'another, then compare comments per video.'),
        })

    # 3. Where the audience mood is best.
    most_loved = na.get('most_loved')
    loved_quiet_fired = False
    if most_loved and most_loved != best:
        m = niches[most_loved]
        if m['positive_pct'] >= 40 and most_loved == weakest and ratio and ratio >= 1.5:
            # Loved but quiet: happiest audience AND lowest volume. One
            # nuanced card instead of two contradictory ones.
            keep.append({
                'title':  f'{most_loved}: Loved but Quiet',
                'reason': (f'{m["positive_pct"]}% of comments on {most_loved} are positive '
                           f'— your happiest audience — but it only gets '
                           f'{m["comments_per_video"]} comments per video, your lowest.'),
                'tip':    (f'The niche makes fans, not conversation. Keep it, but add a '
                           f'question or hook from your {best} videos to wake up the '
                           f'comment section.'),
            })
            loved_quiet_fired = True
        elif m['positive_pct'] >= 40:
            keep.append({
                'title':  f'Your {most_loved} Audience Is the Happiest',
                'reason': (f'{m["positive_pct"]}% of comments on {most_loved} videos are '
                           f'positive ({m["passion_pct"]}% outright passionate) — the best '
                           f'mood anywhere on your account.'),
                'tip':    (f'Blend {most_loved} elements into your bigger formats, or post '
                           f'it when you need a guaranteed win with your core fans.'),
            })

    # ── What to improve ────────────────────────────────────────────────────

    # 1. A niche where negativity concentrates.
    negativity_covered = False
    if niches:
        sour = [(t, m) for t, m in niches.items()
                if m['scraped_comments'] >= 30 and m['negative_pct'] >= max(10, neg * 1.5)]
        if sour:
            t, m = max(sour, key=lambda x: x[1]['negative_pct'])
            improve.append({
                'title':  f'Check the Comments on {t}',
                'reason': (f'{m["negative_pct"]}% of comments there are negative, vs '
                           f'{neg}% across your whole account.'),
                'tip':    ('Read the recent negative comments on those videos — recurring '
                           'complaints usually point at one fixable thing.'),
            })
            negativity_covered = True

    # 1b. High overall negativity with no single niche to blame.
    if neg >= 12 and not negativity_covered:
        improve.append({
            'title':  'High Negative Score — Check What It Really Is',
            'reason': f'{neg}% of all your comments score negative, spread across niches.',
            'tip':    ('Read a sample before changing anything: sentiment tools often '
                       'misread hype slang ("hard", "crazy", "sick") as negative. If it '
                       'is real criticism, look for the recurring complaint.'),
        })

    # 2. Concrete production complaints (audio, captions, length...).
    imp_words = clusters.get('improvement_requests', []) if clusters else []
    if imp_words:
        improve.append({
            'title':  'Viewers Mention Fixable Issues',
            'reason': (f'Words like {", ".join(imp_words[:3])} keep coming up in your '
                       f'comments.'),
            'tip':    ('These are production issues, not content issues — audio, captions '
                       'and length are quick wins you can fix on the very next upload.'),
        })

    # 3. Passive comment section.
    if neutral >= 55:
        improve.append({
            'title':  'Mostly Passive Comments',
            'reason': (f'{neutral}% of your comments are neutral — lots of quick reactions '
                       f'and follow-trades, not much real conversation.'),
            'tip':    ('End each video with one specific question. Viewers comment when '
                       'they are asked something concrete.'),
        })

    # 4. The weakest niche, when the gap is big enough to act on.
    #    (Skipped only when the 'Loved but Quiet' card actually fired -
    #    that card already covers the nuance.)
    if best and weakest and ratio and ratio >= 2 and not loved_quiet_fired:
        w = niches[weakest]
        improve.append({
            'title':  f'Rethink {weakest}',
            'reason': (f'{weakest} averages {w["comments_per_video"]} comments per video '
                       f'across {w["videos"]} videos — your weakest performer.'),
            'tip':    (f'Either cut its share of your schedule or borrow what works in '
                       f'{best}: same hook style, same topics, same energy.'),
        })

    # ── Content ideas: built from what viewers literally asked for ─────────
    for r in requests[:4]:
        if r['count'] >= 10:
            conf = 'High'
        elif r['count'] >= 4:
            conf = 'Medium'
        else:
            conf = 'Low'

        where = f' on your {r["top_video_type"]} videos' if r.get('top_video_type') else ''
        example = (r['examples'][0][:70] + '…') if len(r['examples'][0]) > 70 else r['examples'][0]

        if r['count'] == 1:
            desc = (f'A viewer asked: "{example}"{where}. Small accounts grow by '
                    f'answering every question on camera.')
        else:
            desc = f'Asked {r["count"]} times{where}. Example: "{example}"'

        ideas.append({
            'title':       f'Answer: "{r["request"][:55]}"',
            'confidence':  conf,
            'description': desc,
        })

    # One topical deep-dive — only when the keyword is a real topic
    # (berlin, kenya, track), never a reaction word (wow, goals, looks).
    topical = _first_topical_keyword(keywords)
    if topical:
        ideas.append({
            'title':       f'Deep Dive: {topical.title()}',
            'confidence':  'Medium',
            'description': (f'"{topical}" is the most distinctive topic in your comment '
                            f'section — your audience already associates you with it. '
                            f'A dedicated series builds on proven interest.'),
        })

    # Last resort so the section is never empty.
    if not ideas:
        ideas.append({
            'title':       'Q&A Video Using Real Comments',
            'confidence':  'Low',
            'description': ('Not enough repeated requests in this dataset yet. Collect '
                            'questions from your next few uploads and answer them on camera.'),
        })

    return keep, improve, ideas
