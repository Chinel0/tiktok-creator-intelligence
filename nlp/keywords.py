"""
keywords.py
Keyword extraction using TF-IDF (Term Frequency – Inverse Document Frequency).
TF-IDF gives higher scores to words that are common in a document but
rare across the full comment set — these are the most distinctive terms.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


# ── Cluster seed words ────────────────────────────────────────────────────────
# Each keyword gets assigned to the first cluster whose seeds match it.
# 'engagement' is the catch-all for anything that doesn't match.

CLUSTER_SEEDS = {
    'positive_reactions': [
        'love', 'amazing', 'great', 'beautiful', 'good', 'best', 'awesome',
        'perfect', 'wonderful', 'excellent', 'incredible', 'gorgeous', 'stunning',
        'obsessed', 'favorite', 'talented',
    ],
    'improvement_requests': [
        'need', 'want', 'should', 'more', 'better', 'improve', 'please',
        'wish', 'hope', 'try', 'could', 'would', 'fix', 'change', 'unclear',
    ],
    'content_requests': [
        'video', 'recipe', 'tutorial', 'show', 'make', 'how', 'next',
        'part', 'post', 'watch', 'content', 'collab', 'series',
    ],
    'engagement': [
        'follow', 'like', 'share', 'thank', 'people', 'day',
        'time', 'life', 'really', 'just', 'also',
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

    # Pick top N by mean TF-IDF score
    top_indices = np.argsort(mean_scores)[::-1][:top_n]
    keywords    = [(feature_names[i], float(mean_scores[i])) for i in top_indices]

    clusters = _assign_clusters(keywords)
    return keywords, clusters


def _assign_clusters(keywords: list) -> dict:
    """
    Assign each keyword to its best matching cluster using seed-word matching.
    A keyword that contains any seed word of a cluster is placed there.
    Unmatched keywords fall into 'engagement'.
    """
    clusters = {k: [] for k in CLUSTER_SEEDS}

    for word, _ in keywords:
        placed = False
        for cluster_name, seeds in CLUSTER_SEEDS.items():
            if any(seed in word for seed in seeds):
                clusters[cluster_name].append(word)
                placed = True
                break
        if not placed:
            clusters['engagement'].append(word)

    return clusters
