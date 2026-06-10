"""
niche_analyzer.py
Per-niche (video_type) performance analysis. Pure pandas - no streamlit,
no external APIs - so it runs identically in the app and the test harness.

Combines two data sources:
  - video metadata (when uploaded): views, likes, official comment counts
  - analyzed comments: sentiment distribution, passion rate

Key metrics per niche:
  comments_per_video   - discussion volume (official counts when available)
  avg_views            - reach (needs video metadata)
  discussion_per_1k    - comments per 1000 views: conversation density.
                         Separates "the algorithm pushed it" from
                         "people actually had something to say".
  positive_pct         - share of positive comments
  passion_pct          - share of strongly positive comments (score >= 0.6),
                         i.e. hype, not just polite approval
"""

import pandas as pd

# A niche needs at least this many videos before we crown it a winner -
# one viral video is luck, not a strategy.
MIN_VIDEOS_FOR_RANKING = 3

# Sentiment score above which a comment counts as "passionate" (hype)
PASSION_THRESHOLD = 0.6

# video_type values that are placeholders, not real niches
IGNORED_TYPES = {'unknown', 'nan', ''}


def analyze_niches(df_analyzed: pd.DataFrame, videos_df: pd.DataFrame | None = None) -> dict | None:
    """
    Build per-niche performance metrics and a ranking.

    Args:
        df_analyzed: comments dataframe after sentiment analysis
                     (needs video_type; sentiment/sentiment_score columns)
        videos_df:   optional video metadata (video_id, view_count,
                     like_count, comment_count, video_type)

    Returns dict:
        {
          'niches': {type: {videos, scraped_comments, comments_per_video,
                            avg_views, avg_likes, discussion_per_1k,
                            positive_pct, negative_pct, passion_pct}},
          'ranked': [type, ...]            # by comments_per_video desc
          'best': str | None,              # winner (>= MIN_VIDEOS videos)
          'weakest': str | None,
          'engagement_ratio': float|None,  # best vs weakest comments/video
          'views_ratio': float | None,     # best vs weakest avg views
          'most_loved': str | None,        # highest positive_pct
          'has_video_metadata': bool,
        }
        or None when no niche data exists at all.
    """
    if df_analyzed is None or 'video_type' not in df_analyzed.columns:
        return None

    comments = df_analyzed[~df_analyzed['video_type'].astype(str).str.strip()
                           .str.lower().isin(IGNORED_TYPES)].copy()
    if comments.empty:
        return None

    has_meta = (videos_df is not None and 'video_type' in videos_df.columns
                and 'video_id' in videos_df.columns)

    niches: dict = {}

    # ---- comment-side metrics (sentiment lives here) ----
    for vtype, group in comments.groupby('video_type'):
        vtype = str(vtype).strip()
        n = len(group)
        pos = (group['sentiment'] == 'positive').sum() if 'sentiment' in group.columns else 0
        neg = (group['sentiment'] == 'negative').sum() if 'sentiment' in group.columns else 0
        passion = (group['sentiment_score'] >= PASSION_THRESHOLD).sum() \
            if 'sentiment_score' in group.columns else 0

        niches[vtype] = {
            'scraped_comments': int(n),
            'positive_pct': round(100 * pos / n, 1),
            'negative_pct': round(100 * neg / n, 1),
            'passion_pct': round(100 * passion / n, 1),
            'videos': int(group['video_id'].nunique()) if 'video_id' in group.columns else 0,
            'avg_views': None,
            'avg_likes': None,
            'discussion_per_1k': None,
        }

    # ---- video-side metrics (reach and official engagement) ----
    if has_meta:
        vids = videos_df[~videos_df['video_type'].astype(str).str.strip()
                         .str.lower().isin(IGNORED_TYPES)].copy()
        for vtype, group in vids.groupby('video_type'):
            vtype = str(vtype).strip()
            entry = niches.setdefault(vtype, {
                'scraped_comments': 0, 'positive_pct': 0.0, 'negative_pct': 0.0,
                'passion_pct': 0.0, 'videos': 0, 'avg_views': None,
                'avg_likes': None, 'discussion_per_1k': None,
            })
            entry['videos'] = int(len(group))
            if 'view_count' in group.columns:
                entry['avg_views'] = round(float(group['view_count'].mean()), 1)
            if 'like_count' in group.columns:
                entry['avg_likes'] = round(float(group['like_count'].mean()), 1)
            if 'comment_count' in group.columns:
                entry['comments_per_video'] = round(float(group['comment_count'].mean()), 1)
                if entry['avg_views'] and entry['avg_views'] > 0:
                    entry['discussion_per_1k'] = round(
                        1000 * entry['comments_per_video'] / entry['avg_views'], 1)

    # comments_per_video fallback from scraped rows when no metadata
    for vtype, entry in niches.items():
        if 'comments_per_video' not in entry:
            v = max(entry['videos'], 1)
            entry['comments_per_video'] = round(entry['scraped_comments'] / v, 1)

    # ---- ranking and headline comparisons ----
    ranked = sorted(niches, key=lambda t: niches[t]['comments_per_video'], reverse=True)

    eligible = [t for t in ranked if niches[t]['videos'] >= MIN_VIDEOS_FOR_RANKING]
    best = eligible[0] if eligible else None
    weakest = eligible[-1] if len(eligible) > 1 else None

    engagement_ratio = views_ratio = None
    if best and weakest:
        b, w = niches[best], niches[weakest]
        if w['comments_per_video'] > 0:
            engagement_ratio = round(b['comments_per_video'] / w['comments_per_video'], 1)
        if b['avg_views'] and w['avg_views'] and w['avg_views'] > 0:
            views_ratio = round(b['avg_views'] / w['avg_views'], 1)

    # "most loved": where the audience is happiest (needs a real sample)
    loved_pool = [t for t in eligible if niches[t]['scraped_comments'] >= 30]
    most_loved = max(loved_pool, key=lambda t: niches[t]['positive_pct']) if loved_pool else None

    return {
        'niches': niches,
        'ranked': ranked,
        'best': best,
        'weakest': weakest,
        'engagement_ratio': engagement_ratio,
        'views_ratio': views_ratio,
        'most_loved': most_loved,
        'has_video_metadata': has_meta,
    }
