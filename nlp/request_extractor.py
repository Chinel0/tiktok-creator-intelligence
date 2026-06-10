"""
request_extractor.py
Finds explicit audience requests in comments ("teach me german",
"recipe please", "tutorial for this choreo") and counts how often each
one is asked, and on which content type.

Design principles (learned the hard way):
  - Pure pandas/regex. No streamlit, no sentiment-column dependencies.
  - Precision over recall: only count comments that are unmistakably
    asks. A missed request is fine; a fake one destroys trust.
  - Whole-comment grouping: TikTok requests repeat nearly verbatim, so
    we group by normalized comment text instead of chopping comments
    into keywords (chopping is what produced 'content' garbage before).
"""

import re
from collections import Counter

import pandas as pd

# A comment is a request if it matches ANY of these patterns.
REQUEST_PATTERNS = [
    r'\bteach me\b',
    r'\btutorial\b',
    r'\brecipe\b',
    r'\bhow (do|did) you\b',
    r'\bhow to\b',
    r'\bhow (much|many|expensive)\b',
    r'\bwhere\b',
    r'^what\b',                 # "what song is this", "what products..."
    r'\bmake (a|more)\b',       # "make a video about german food"
    r'\bdo (a|the|one)\b',      # "do a crossbar challenge"
    r'\bshow (us|me|more)\b',
    r'\bdrop the\b',
    r'\bwhen is\b',
    r'\bcan you\b',
    r'\bplease\b',
    r'\bpart (two|2)\b',
]
_COMPILED = [re.compile(p) for p in REQUEST_PATTERNS]

# Normalization: phrases that differ only by these fillers are the same ask
_FILLERS = re.compile(r'\b(please|pls|plz|can you|could you|next time|for us)\b')

# Normalized phrases with no real content - agreement noise, not asks
_JUNK = {'yes', 'no', 'omg', 'lol', 'wow', 'same', 'this', 'more', 'it', ''}


def _clean(text: str) -> str:
    """Lowercase, strip urls/mentions/punctuation - mirror of preprocessor."""
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|@\w+|#\w+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def _normalize_key(cleaned: str) -> str:
    """Collapse filler words so 'recipe please' == 'recipe pls'."""
    key = _FILLERS.sub('', cleaned)
    return re.sub(r'\s+', ' ', key).strip()


def extract_requests(df: pd.DataFrame, min_count: int = 2, top_n: int = 10,
                     fallback_to_questions: bool = True) -> list:
    """
    Extract repeated explicit requests from a comments dataframe.

    Args:
        df: needs a text column ('clean_comment' preferred, falls back to
            'Comment Text'). 'video_type' and original 'Comment Text' are
            used when present for context and display examples.

    Returns a list (sorted by count, max top_n) of dicts:
        {
          'request': str,          # representative phrasing
          'count': int,            # how many comments ask this
          'video_types': dict,     # {type: count} where it is asked
          'top_video_type': str | None,
          'examples': [str, ...],  # up to 3 original comments as proof
        }
    """
    if df is None or len(df) == 0:
        return []

    if 'clean_comment' in df.columns:
        texts = df['clean_comment'].fillna('').astype(str)
    elif 'Comment Text' in df.columns:
        texts = df['Comment Text'].fillna('').astype(str).map(_clean)
    else:
        return []

    originals = df['Comment Text'].fillna('').astype(str) \
        if 'Comment Text' in df.columns else texts
    vtypes = df['video_type'].fillna('').astype(str) \
        if 'video_type' in df.columns else pd.Series([''] * len(df), index=df.index)

    groups: dict = {}
    for idx in texts.index:
        cleaned = texts[idx]
        if len(cleaned) < 4 or not any(p.search(cleaned) for p in _COMPILED):
            continue

        key = _normalize_key(cleaned)
        if key in _JUNK or len(key.split()) < 2:
            continue

        g = groups.setdefault(key, {
            'phrasings': Counter(), 'count': 0, 'questions': 0,
            'video_types': Counter(), 'examples': [],
        })
        g['count'] += 1
        g['phrasings'][cleaned] += 1
        if '?' in originals[idx]:
            g['questions'] += 1
        vt = vtypes[idx].strip()
        if vt and vt.lower() not in ('unknown', 'nan'):
            g['video_types'][vt] += 1
        if len(g['examples']) < 3:
            g['examples'].append(originals[idx].strip())

    results = []
    for key, g in groups.items():
        if g['count'] < min_count:
            continue
        top_type = g['video_types'].most_common(1)[0][0] if g['video_types'] else None
        results.append({
            'request': g['phrasings'].most_common(1)[0][0],
            'count': g['count'],
            'video_types': dict(g['video_types']),
            'top_video_type': top_type,
            'examples': g['examples'],
            'is_question': g['questions'] > 0,  # original text had a '?'
        })

    results.sort(key=lambda r: r['count'], reverse=True)

    # No repeated asks at all (common for small/engagement-trade accounts):
    # fall back to individual questions, clearly identifiable by count == 1.
    if not results and min_count > 1 and fallback_to_questions:
        singles = extract_requests(df, min_count=1, top_n=top_n,
                                   fallback_to_questions=False)
        return [r for r in singles if r['is_question']][:5]

    return results[:top_n]


def requests_for_niche(requests: list, video_type: str) -> list:
    """Subset of requests that mostly come from one content type."""
    return [r for r in requests if r['top_video_type'] == video_type]
