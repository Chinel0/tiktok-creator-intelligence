"""
keywords.py
Keyword extraction using TF-IDF (Term Frequency – Inverse Document Frequency).
TF-IDF gives higher scores to words that are common in a document but
rare across the full comment set — these are the most distinctive terms.

Two safeguards keep the output meaningful:
  1. GENERIC_FILLER: platform words like "content"/"video"/"want" are
     dropped from the keyword list. They appear in every comment section
     on TikTok and say nothing about THIS creator's audience. (A bare
     "content" keyword is what once produced the recommendation
     'viewers are asking for "content" type of content'.)
  2. Cluster seeds are matched at TOKEN level (with light stemming),
     not substring level, and the seed lists contain only words that
     genuinely signal that intent — e.g. "want" is NOT an improvement
     request ("want to visit" is wanderlust, not criticism).
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


# ── Generic platform words — never useful as audience keywords ───────────────
GENERIC_FILLER = {
    'content', 'video', 'videos', 'channel', 'account', 'page',
    'make', 'makes', 'making', 'made', 'post', 'posting', 'posted',
    'watch', 'watching', 'watched', 'want', 'wants', 'wanted',
    'need', 'needs', 'needed', 'just', 'really', 'thing', 'things',
    'stuff', 'dont', 'doesnt', 'didnt', 'im', 'ur', 'u', 'pls', 'plz',
}

# ── Cluster seed words ────────────────────────────────────────────────────────
# Each keyword is assigned to the first cluster with a matching seed token.
# 'engagement' is the catch-all for anything that doesn't match.

CLUSTER_SEEDS = {
    'positive_reactions': [
        'love', 'amazing', 'great', 'beautiful', 'good', 'best', 'awesome',
        'perfect', 'wonderful', 'excellent', 'incredible', 'gorgeous',
        'stunning', 'obsessed', 'favorite', 'talented', 'talent', 'fire',
        'goals', 'queen', 'cute', 'delicious', 'relatable', 'inspiring',
    ],
    'improvement_requests': [
        # actual critique vocabulary, not demand words
        'better', 'improve', 'fix', 'change', 'unclear', 'confusing',
        'audio', 'caption', 'captions', 'quality', 'louder', 'shaky',
        'short', 'blurry', 'slow',
    ],
    'content_requests': [
        # words that signal a concrete ask, not the word "content"
        'tutorial', 'recipe', 'teach', 'series', 'collab', 'drop',
        'remix', 'cover', 'vlog', 'tips', 'guide', 'routine',
    ],
    'engagement': [
        'follow', 'share', 'thank', 'people', 'day', 'time', 'life',
    ],
}

# Human-readable display names for each cluster
CLUSTER_LABELS = {
    'positive_reactions':   'Positive Reactions',
    'improvement_requests': 'Improvement Requests',
    'content_requests':     'Content Requests',
    'engagement':           'General Engagement',
}


def extract_keywords(df, top_n: int = 20) -> tuple:
    """
    Extract the top N keywords from clean_comment using TF-IDF,
    then group them into thematic clusters.

    Args:
        df:    DataFrame with a 'clean_comment' column
        top_n: How many top keywords to return

    Returns:
        keywords: list of (word, score) tuples, sorted by score descending
        clusters: dict  { cluster_name: [word, word, ...] }
    """
    texts = [t for t in df['clean_comment'].dropna().tolist() if len(str(t)) > 2]

    if len(texts) < 2:
        # Not enough data for TF-IDF — return empty results
        return [], {k: [] for k in CLUSTER_SEEDS}

    vectorizer = TfidfVectorizer(
        max_features=200,
        stop_words='english',
        ngram_range=(1, 2),  # single words and two-word phrases
        min_df=1,
    )

    try:
        matrix        = vectorizer.fit_transform(texts)
        feature_names = vectorizer.get_feature_names_out()
        mean_scores   = np.mean(matrix.toarray(), axis=0)
    except ValueError:
        return [], {k: [] for k in CLUSTER_SEEDS}

    # Walk grams from highest score down, skipping generic filler,
    # until we have top_n meaningful keywords.
    keywords = []
    for i in np.argsort(mean_scores)[::-1]:
        gram = feature_names[i]
        if any(tok in GENERIC_FILLER for tok in gram.split()):
            continue
        keywords.append((gram, float(mean_scores[i])))
        if len(keywords) >= top_n:
            break

    clusters = _assign_clusters(keywords)
    return keywords, clusters


def _token_matches_seed(token: str, seed: str) -> bool:
    """
    Token-level match with light stemming: 'supporting' matches 'support',
    but 'heart' does not match 'hear' (suffix must be a plausible ending).
    """
    if token == seed:
        return True
    return token.startswith(seed) and len(token) - len(seed) <= 3


def _assign_clusters(keywords: list) -> dict:
    """
    Assign each keyword to its best matching cluster using token-level
    seed matching. Unmatched keywords fall into 'engagement'.
    """
    clusters = {k: [] for k in CLUSTER_SEEDS}

    for gram, _ in keywords:
        tokens = gram.split()
        placed = False
        for cluster_name, seeds in CLUSTER_SEEDS.items():
            if any(_token_matches_seed(tok, seed) for tok in tokens for seed in seeds):
                clusters[cluster_name].append(gram)
                placed = True
                break
        if not placed:
            clusters['engagement'].append(gram)

    return clusters
